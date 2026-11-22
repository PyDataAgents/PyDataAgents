from __future__ import annotations

import re
import threading
import sympy as sp
from sympy.physics import units as u
from loguru import logger

from .formula_models import Formula, FormulaSet, SymbolInput

"""
Einheiten-Handling für die Formula Engine.

Nutzt sympy.physics.units als Basis (keine externe Abhängigkeit wie `pint`
nötig). Präfixe (k, M, m, ...) werden bewusst als reine Zahlenfaktoren
statt als sympy `Prefix`-Objekte hinterlegt, weil letztere sich in
Kombination mit `convert_to` inkonsistent verhalten (Faktor wird teils
doppelt angewendet). Mit reinen Zahlenfaktoren ist die Umrechnung robust
und leicht nachvollziehbar.
"""


# ---------------------------------------------------------------------------
# Bekannte Einheiten: Name -> sympy-Ausdruck (Zahlenfaktor * Basiseinheit)
# ---------------------------------------------------------------------------
UNIT_TABLE: dict[str, sp.Expr] = {
    # dimensionsless
    "1": sp.Integer(1),
    "-": sp.Integer(1),
    "": sp.Integer(1),
    "dimensionless": sp.Integer(1),
    "rad": sp.Integer(1),  # rad ist dimensionslos (m/m)
    "deg": sp.pi / 180,
    "°": sp.pi / 180,
    "%": sp.Rational(1, 100),
    # length
    "meter": u.meter,
    "m": u.meter,
    "mm": sp.Rational(1, 1000) * u.meter,
    "millimeter": sp.Rational(1, 1000) * u.meter,
    "cm": sp.Rational(1, 100) * u.meter,
    "km": 1000 * u.meter,
    "µm": sp.Rational(1, 1000000) * u.meter,
    # area
    "m**2": u.meter**2,
    "mm**2": sp.Rational(1, 1000) ** 2 * u.meter**2,
    "cm**2": sp.Rational(1, 100) ** 2 * u.meter**2,
    # volume / area moment of inertia
    "m**3": u.meter**3,
    "mm**3": sp.Rational(1, 1000) ** 3 * u.meter**3,
    "cm**3": sp.Rational(1, 100) ** 3 * u.meter**3,
    "m**4": u.meter**4,
    "mm**4": sp.Rational(1, 1000) ** 4 * u.meter**4,
    "cm**4": sp.Rational(1, 100) ** 4 * u.meter**4,
    # Mass
    "kg": u.kilogram,
    "g": sp.Rational(1, 1000) * u.kilogram,
    "t": 1000 * u.kilogram,
    "kg/m**3": u.kilogram / u.meter**3,
    "m**3/s": u.meter**3 / u.second,
    "Pa*s": u.pascal * u.second,
    # Time
    "s": u.second,
    "min": 60 * u.second,
    "h": 3600 * u.second,
    # Force
    "N": u.newton,
    "kN": 1000 * u.newton,
    "MN": 1_000_000 * u.newton,
    # Tension / Pressure
    "Pa": u.pascal,
    "kPa": 1000 * u.pascal,
    "MPa": 1_000_000 * u.pascal,
    "GPa": 1_000_000_000 * u.pascal,
    "N/mm**2": 1_000_000 * u.pascal,  # == MPa
    "kilogram/(meter*second**2)": u.pascal,
    "bar": 100_000 * u.pascal,
    "N/m": u.newton / u.meter,
    "N/mm": 1000 * u.newton / u.meter,
    "N*s/m": u.newton * u.second / u.meter,
    "N*s": u.newton * u.second,
    "kg*m/s": u.kilogram * u.meter / u.second,
    # Moment / Energy / Power
    "N*m": u.newton * u.meter,
    "kN*m": 1000 * u.newton * u.meter,
    "N*mm": sp.Rational(1, 1000) * u.newton * u.meter,
    "J": u.joule,
    "kJ": 1000 * u.joule,
    "W": u.watt,
    "kW": 1000 * u.watt,
    # Speed / Acceleration
    "m/s": u.meter / u.second,
    "km/h": sp.Rational(1, 3.6) * u.meter / u.second,
    "m/s**2": u.meter / u.second**2,
    # Frequency / Rotational Speed
    "Hz": 1 / u.second,
    "1/s": 1 / u.second,
    "1/min": 1 / (60 * u.second),
    "rpm": 1 / (60 * u.second),
    "rad/s": 1 / u.second,
    "rad/s**2": 1 / u.second**2,
    # Temperature (only as Kelvin-Difference)
    "K": u.kelvin,
    "1/K": 1 / u.kelvin,
    "mol": u.mole,
    "J/(mol*K)": u.joule / (u.mole * u.kelvin),
    "J/(kg*K)": u.joule / (u.kilogram * u.kelvin),
    "W/(m*K)": u.watt / (u.meter * u.kelvin),
}

# Bevorzugte Anzeige-Einheit je SI-kohärenter Einheit (aus der Formel-
# Definition selbst, z.B. "Pa" -> zeig lieber "MPa" an).
PREFERRED_DISPLAY: dict[str, str] = {
    "Pa": "MPa",
    "m**4": "mm**4",
    "m**3": "cm**3",
    "m**2": "mm**2",
    "m": "mm",
    "N*m": "N*m",
    "1/s": "1/min",
}

_BASE = [u.meter, u.kilogram, u.second, u.ampere, u.kelvin, u.mole, u.candela]


class UnitError(ValueError):
    pass


def _unit_expr(unit_str: str) -> sp.Expr:
    unit_str = unit_str.strip()
    if unit_str in UNIT_TABLE:
        return UNIT_TABLE[unit_str]
    normalized = unit_str.replace("^", "**").replace(" ", "")
    normalized = re.sub(r"(?<=[a-zA-Z])2\b", "**2", normalized)
    normalized = re.sub(r"(?<=[a-zA-Z])3\b", "**3", normalized)
    normalized = re.sub(r"(?<=[a-zA-Z])4\b", "**4", normalized)
    if normalized in UNIT_TABLE:
        return UNIT_TABLE[normalized]
    raise UnitError(
        f"Unbekannte Einheit '{unit_str}'. Bekannte Einheiten u.a.: "
        f"{', '.join(sorted(k for k in UNIT_TABLE if k and len(k) <= 6))} ..."
    )


def value_to_si(value: float, unit_str: str) -> tuple[float, str]:
    """Wandelt (Zahl, Einheit) in eine reine Zahl in SI-Basiseinheiten um."""
    qty = sp.Float(value) * _unit_expr(unit_str)
    si_expr = u.convert_to(qty, _BASE)
    if si_expr.is_number:
        return float(si_expr), "1"
    coeff, _rest = si_expr.as_coeff_Mul()
    return float(coeff), str(_rest)


def si_to_unit(si_value: float, si_unit_str: str, target_unit: str | None = None) -> tuple[float, str]:
    """
    Wandelt einen Zahlenwert, der in der SI-kohärenten Einheit
    `si_unit_str` (z.B. "Pa", "N*m", "m**4") vorliegt, in eine
    menschenfreundliche Zieleinheit um. Ohne explizite Zieleinheit wird
    PREFERRED_DISPLAY verwendet, sonst die SI-Einheit selbst.
    """
    if target_unit is None:
        target_unit = PREFERRED_DISPLAY.get(si_unit_str, si_unit_str)
    si_base_expr = _unit_expr(si_unit_str)
    target_expr = _unit_expr(target_unit)
    if si_base_expr.is_number and target_expr.is_number:
        return float(sp.Float(si_value) * si_base_expr / target_expr), target_unit

    # target_expr = prefix_factor * base_unit (z.B. 1e6 * pascal für "MPa").
    # convert_to ignoriert numerische Koeffizienten im Zielausdruck, daher
    # spalten wir den Präfix-Faktor ab und dividieren ihn manuell heraus.
    prefix_factor, base_unit_expr = target_expr.as_coeff_Mul()

    qty = sp.Float(si_value) * si_base_expr
    converted = u.convert_to(qty, base_unit_expr)
    coeff, _rest = converted.as_coeff_Mul()
    try:
        num = float(coeff) / float(prefix_factor)
    except TypeError:
        num = float(coeff.evalf()) / float(prefix_factor)
    return num, target_unit


def known_units() -> list[str]:
    return sorted(k for k in UNIT_TABLE if k)


class FormulaEngine:
    """
    Core engine: solves a registered formula for one or more
    unknown quantities based on given known values
    (including units).
    """
    
    @staticmethod
    def solve(formula_set : FormulaSet, input_values : dict[str, SymbolInput], targets_units : dict[str, str]) -> dict:
        """
        input_values: {"M_b": SymbolInput(value=150, unit="N*m"), "W_b": SymbolInput(value=20, unit="cm**3")}
        targets_units: keys of the target symbols and their required units, z.B. {"sigma": "MPa"}

        returns the target results
        """
        equations_available : dict[int, Formula] = formula_set.formulas.copy()
        equations_solvable : dict[int, sp.Eq] = {}
        inputs_available : set[str] = set(input_values.keys())
        inputs_used : set[str] = set()
        symbols_computable : set[str] = set()
        targets : set[str] = set(targets_units.keys())
        
        n_c : int = len(symbols_computable)
        n_c_last : int = -1
        
        while n_c > n_c_last:            
            indices_used : set[int] = set()
            for i, formula in equations_available.items():
                formula_symbols : set[str] = formula.get_symbols()
                remaining_symbols : set[str] = formula_symbols - inputs_available - symbols_computable
                if len(remaining_symbols) == 1:
                    symbols_computable = symbols_computable | remaining_symbols
                    equations_solvable[i] = formula.equation
                    indices_used.add(i)
                    inputs_used = (formula_symbols & inputs_available) | inputs_used
            for i in indices_used:
                equations_available.pop(i, None)
            n_c_last = n_c
            n_c = len(symbols_computable)
            if len(targets - symbols_computable - inputs_used) == 0:
                n_c = 0
                break
        
        if len(targets - symbols_computable - inputs_used) > 0:
            logger.error("Not all targets are included in computable symbols")
            return {}
        
        if len(equations_solvable) == len(symbols_computable):
            # assemble correct input values
            symbol_inputs : dict[sp.Symbol, float] = {}            
            used_inputs : dict[str, SymbolInput] = {k: v for k, v in input_values.items() if k in inputs_used}
            for symbol_name, symbol_input in used_inputs.items():
                input_unit = symbol_input.unit
                input_value = symbol_input.value
                formula_unit = formula_set.symbols[symbol_name].unit
                if formula_unit != input_unit:
                    si_value, si_unit = value_to_si(input_value, input_unit)
                    formula_value, tu = si_to_unit(si_value, si_unit, formula_unit)
                else:
                    formula_value = input_value
                symbol = sp.symbols(symbol_name)
                symbol_inputs[symbol] = formula_value
            substituted_equations : list[sp.Eq] = [eq.subs(symbol_inputs) for eq in equations_solvable.values()]
            target_symbols : list[sp.Symbol] = [sp.symbols(target) for target in symbols_computable]
            solution : dict = sp.solve(substituted_equations, target_symbols, dict=True)
            if len(solution) > 0:
                if len(solution[0]) > 0:
                    target_values : dict = {}                        
                    for symbol_name, target_unit in targets_units.items():
                        symbol = sp.symbols(symbol_name)
                        if symbol in solution[0]:
                            formula_value = solution[0][symbol]
                            formula_unit = formula_set.symbols[symbol_name].unit
                            if formula_unit != target_unit:
                                si_value, si_unit = value_to_si(float(formula_value), formula_unit)
                                target_value, tu = si_to_unit(si_value, si_unit, target_unit)
                            else:
                                target_value = float(formula_value)
                            target_values[symbol_name] = {"value": target_value, "unit": target_unit}
                    return target_values
                else:
                    logger.error("System of equations could not be solved")
                    return {}
            else:
                logger.error("System of equations could not be solved")
                return {}
        else: 
            logger.error("Number of equations to solve does not equal number of unknwon symbols to solve for")     
            return {}
