"""Datenmodell für die Formelbibliothek."""

from __future__ import annotations

from dataclasses import dataclass, field
import enum
import re
from typing import Any, Union
import pandas as pd
import sympy as sp

from pydag.nodes.documents.ReadExcelTableAction import ReadExcelTableAction
from pydag.utils.FileUtils import FileUtils

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
    lookups : dict[str, Lookup] = field(default_factory=dict, metadata={"description": "lookup datamodel"})

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

class LookupSource(str, enum.Enum):
    XLSX = "xlsx"

class LookupReturnType(str, enum.Enum):
    SINGLE = "single"
    LIST = "list"
    DICT = "dict"
    
@dataclass
class Lookup:
    description_de: str = field(default=None, kw_only=True)
    description_en: str = field(default=None, kw_only=True)
    source : str = field(default=None, metadata={"description": ""})
    endpoint : str = field(default=None, metadata={"description": ""})
    target : str = field(default=None, metadata={"description": ""})
    query : str = field(default=None, metadata={"description": ""})
    return_type : str = field(default=LookupReturnType.SINGLE.value, metadata={"description": ""})
    
    def lookup(self, query_inputs : dict[str, Union[str,float]]) -> list | dict | str | int | float:
        df : pd.DataFrame = self._make_dataframe()
        q : str = self.query
        for k, v in query_inputs.items():
            if isinstance(v, str):
                q = q.replace(f"@{k}", f"'{v}")
            elif isinstance(v, float):
                q = q.replace(f"@{k}", f"{v}")
            else:
                raise ValueError("query inputs must be either str or float")
        result : pd.DataFrame = df.query(q)[self.target]
        match self.return_type:
            case LookupReturnType.SINGLE.value:                
                return result.iloc[0]
            case LookupReturnType.LIST.value:                
                return result.tolist()
            case LookupReturnType.DICT.value:
                return result.to_dict()
            
    def get_query_params(self) -> set[str]:
        params = set(re.findall(r"@(\w+)", self.query))
        return params
    
    def _make_dataframe(self) -> pd.DataFrame:
        match self.source:
            case LookupSource.XLSX.value:
                return self._dataframe_from_xlsx()
            case _:
                return None
            
    
    def _dataframe_from_xlsx(self):
        ep : str = self.endpoint        
        fp, sheet, table = re.fullmatch(r"\[(.*?)\](?:(.*?)!)?(.*)", ep).groups()
        if FileUtils.exists_file(fp):
            reta : ReadExcelTableAction
            if sheet:
                reta = ReadExcelTableAction(excel_file=fp, sheet_name=sheet, table_name=table)
            else:
                reta = ReadExcelTableAction(excel_file=fp, table_name=table)
            reta.install()
            reta.execute()
            d = reta.get_data()
            df : pd.DataFrame = pd.DataFrame(d)
            return df
        else:
            return None