from dataclasses import dataclass, field
from typing import Any

from pydag.agents.Agent import Agent
from pydag.services.Service import Service
from pydag.services.datamodel.formula_engine import FormulaEngine, known_units
from pydag.services.datamodel.formula_models import FormulaSet
from pydag.services.datamodel.formula_registries import FormulaRegistry, MaterialRegistry


@dataclass
class FormulaService(Service):
    
    formula_sources : list[str] = field()
    material_sources : list[str] = field()
    
    def __post_init__(self):
        super().__post_init__()
        self._formula_registry : FormulaRegistry = None
        self._material_registry : MaterialRegistry = None
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._formula_registry = FormulaRegistry()
        self._material_registry = MaterialRegistry()    

    def list_categories(self) -> list[str]:
        """
        Listet alle verfügbaren Formel-Kategorien (z.B. 'Festigkeitslehre.Biegung').
        Nützlich, um sich einen Überblick über die Struktur der Bibliothek zu
        verschaffen, bevor man gezielt sucht.
        """
        return self._formula_registry.categories()

    def search_formulas(self, query: str = "", category: str | None = None) -> list[dict]:
        """
        Durchsucht die Formelbibliothek per Volltextsuche über Name, Beschreibung,
        Tags und Größen. Gibt eine Kurzübersicht (id, name, category, equation,
        variables) zurück — für Details danach get_formula(id) aufrufen.

        Args:
            query: Suchbegriff, z.B. "biegung", "knicken", "federrate". Leerer
                String gibt alle Formeln (ggf. gefiltert nach category) zurück.
            category: Optionaler Kategorie-Filter (Präfix-Match), z.B.
                "Festigkeitslehre" oder "Festigkeitslehre.Biegung".
        """
        results : list[FormulaSet] = self._formula_registry.search(query, category)
        return [f.summary() for f in results]

    def get_formula(self, formula_id: str) -> dict:
        """
        Liefert die vollständigen Details einer Formel: Gleichung, alle Symbole
        mit Einheit und Beschreibung, verwandte Formeln, Gültigkeitsbereich und
        Quelle. Immer vor solve_formula aufrufen, um die exakten Symbolnamen
        und erwarteten Einheiten zu kennen.

        Args:
            formula_id: Die ID der Formel, z.B. "biegespannung".
        """
        try:
            f = self._formula_registry.formula(formula_id)
        except KeyError as e:
            return {"error": str(e)}
        return f.detail()

    def solve_formula(self, formula_id: str, known_values: dict[str, Any], target_units: dict[str, str] | None = None) -> dict:
        """
        Löst eine Formel symbolisch nach der/den fehlenden Größe(n) auf und
        berechnet das numerische Ergebnis inkl. Einheitenumrechnung.

        Gib alle bekannten Größen an (Name -> {"value": Zahl, "unit": Einheit}),
        lass genau die gesuchte(n) Größe(n) weg. Rufe vorher get_formula auf,
        um die exakten Symbolnamen und plausible Einheiten zu sehen.

        Args:
            formula_id: Die ID der Formel, z.B. "biegespannung".
            known_values: z.B. {"M_b": {"value": 150, "unit": "N*m"},
                                "W_b": {"value": 20, "unit": "cm**3"}}
            target_units: Optionale Wunsch-Einheiten für die Ausgabe, z.B.
                {"sigma_b": "MPa"}. Ohne Angabe wird eine sinnvolle
                Standardeinheit gewählt.

        Returns:
            dict mit den aufgelösten Werten, dem symbolischen Rechenweg,
            Gültigkeitsbedingungen und Quellenangabe. Bei Fehlern (unbekannte
            Größe, falsche Einheit, etc.) enthält die Antwort ein "error"-Feld
            statt "results".
        """
        try:
            f = self._formula_registry.formula(formula_id)
        except KeyError as e:
            return {"error": str(e)}

        return FormulaEngine.solve(f, known_values, target_units)

    def list_supported_units(self) -> list[str]:
        """
        Listet alle Einheiten-Strings, die solve_formula für 'unit'-Felder
        akzeptiert (z.B. "MPa", "kN", "mm**4", "rpm").
        """
        return known_units()