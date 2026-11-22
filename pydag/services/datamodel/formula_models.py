"""Datenmodell für die Formelbibliothek."""

from __future__ import annotations

from dataclasses import dataclass, field
import sympy as sp

@dataclass(frozen=True)
class Option:
    name : str = field(default=None)
    value : float = field(default=None)

@dataclass(frozen=True)
class SymbolMeta:
    """Metadaten zu einer Formelgröße."""
    unit : str  # SI-kohärente Einheit, z.B. "Pa", "N*m", "m**4", "dimensionless"
    options : list[Option] = field(default=None)
    label_de: str = field(default=None, kw_only=True)
    description_de: str = field(default=None, kw_only=True)
    label_en: str = field(default=None, kw_only=True)
    description_en: str = field(default=None, kw_only=True)

@dataclass(frozen=True)
class SymbolInput:
    value : int | float
    unit : str  # SI-kohärente Einheit, z.B. "Pa", "N*m", "m**4", "dimensionless"

@dataclass
class FormulaSet:
    id : str = field(default=None)
    categories : list[str] = field(default_factory=list)
    name : str = field(default=None)
    formulas : dict[int, Formula] = field(default_factory=dict)
    symbols : dict[str, SymbolMeta] = field(default_factory=dict, metadata={"description": ""})
    sources : list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    label_de: str = field(default=None, kw_only=True)
    description_de: str = field(default=None, kw_only=True)
    label_en: str = field(default=None, kw_only=True)
    description_en: str = field(default=None, kw_only=True)

@dataclass
class Formula:
    equation : sp.Eq = None
    label_de: str = field(default=None, kw_only=True)
    description_de: str = field(default=None, kw_only=True)
    label_en: str = field(default=None, kw_only=True)
    description_en: str = field(default=None, kw_only=True)

    def get_symbols(self) -> set[str]:
        return {str(s) for s in self.equation.free_symbols}

    def has_symbol(self, symbol_name : str) -> bool:
        return self.equation.has(sp.symbols(symbol_name))

@dataclass(frozen=True)
class MaterialProperty(SymbolMeta):
    value : float = field(default = None, metadata={"description": "default value of the material property"})

@dataclass
class MechanicalProperties():
    E : MaterialProperty = MaterialProperty(unit="Pa", description_de="Elastizitätsmodul (E-Modul)"),
    G : MaterialProperty = MaterialProperty(unit="Pa", description_de="Schubmodul (G-Modul)"),
    nu : MaterialProperty = MaterialProperty(unit="dimensionless", description_de="Querkontraktionszahl (Poissonzahl)"),
    R_p_02 : MaterialProperty = MaterialProperty(unit="Pa", description_de="Streckgrenze / 0,2%-Dehngrenze"),
    Rm : MaterialProperty = MaterialProperty(unit="Pa", description_de="Zugfestigkeit"),
    rho : MaterialProperty = MaterialProperty(unit="kg/m**3", description_de="Dichte"),
    alpha : MaterialProperty = MaterialProperty(unit="1/K", description_de="linearer Wärmeausdehnungskoeffizient"),
    c_p : MaterialProperty = MaterialProperty(unit="J/(kg*K)", description_de="spezifische Wärmekapazität"),
    lambda_th : MaterialProperty = MaterialProperty(unit="W/(m*K)", description_de="Wärmeleitfähigkeit"),
    A : MaterialProperty = MaterialProperty(unit="dimensionless", description_de="Bruchdehnung (bei Zugversuch)")

@dataclass
class Material:
    id : str = None
    name : str = None
    material_number : str = None
    chemical_name : str = None
    common_names : list[str] = None
    category : str = None
    mechanical_properties : MechanicalProperties = field(default_factory=MechanicalProperties())
    source : str = None
    note : str = None
    tags : list[str] = field(default_factory=list)
