from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import sympy as sp
from dataclasses import fields, is_dataclass
from typing import get_type_hints, get_origin, get_args

import yaml

from pydag.services.datamodel.formula_models import FormulaSet


@dataclass
class FormulaRegistry():
    
    model_sources : list[str] = field(default_factory=lambda: [os.path.dirname(__file__) + os.sep + "models"], metadata={"description": "folders to load the formula models from"})
    
    def __post_init__(self):
        self._formula_sets : dict[str, FormulaSet] = {}
        fo : str
        for fo in self.model_sources:
            p : Path = Path(fo)
            for file in p.iterdir():
                if file.is_file():
                    if file.suffix == ".yaml" or file.suffix == ".yml":
                        fs : FormulaSet = FormulaRegistry._load_yaml(file.absolute())
                        self._formula_sets[fs.id] = fs
    
    @staticmethod
    def _load_yaml(file_path : str) -> FormulaSet:
        fs : FormulaSet = None
        with open(file_path, encoding="utf-8", mode="r") as f:
            data : dict = yaml.safe_load(f)
            fs = FormulaRegistry._dataclass_from_dict(FormulaSet, data)
        return fs
        
    @staticmethod
    def _dataclass_from_dict(clazz, data : dict):
        type_hints = get_type_hints(clazz)
        kwargs = {}
        for f in fields(clazz):
            if f.name not in data:
                continue
            value = data[f.name]
            field_type = type_hints.get(f.name, f.type)
            kwargs[f.name] = FormulaRegistry._convert_value(field_type, value)
        return clazz(**kwargs)
    
    @staticmethod
    def _convert_value(field_type, value):
        origin = get_origin(field_type)
        args = get_args(field_type)

        if origin is list:
            element_type = args[0]

            if element_type is sp.Eq:
                return [FormulaRegistry._parse_equation(x) for x in value]

            return [
                FormulaRegistry._convert_value(element_type, item)
                for item in value
            ]

        if origin is dict:
            key_type, value_type = args

            if sp.Eq in get_args(value_type):
                d : dict = {}
                for k, v in value.items():
                    if "=" in v:
                        d.update({FormulaRegistry._convert_value(key_type, k): FormulaRegistry._parse_equation(v)})
                    else:
                        d.update({FormulaRegistry._convert_value(key_type, k): FormulaRegistry._convert_value(value_type, v)})
                return d
            else:
                return {
                    FormulaRegistry._convert_value(key_type, k):
                    FormulaRegistry._convert_value(value_type, v)
                    for k, v in value.items()
                }

        if isinstance(value, dict) and is_dataclass(field_type):
            return FormulaRegistry._dataclass_from_dict(field_type, value)

        if args is sp.Eq:
            return FormulaRegistry._parse_equation(value)

        if field_type is sp.Eq:
            return FormulaRegistry._parse_equation(value)
                
        return value    
    
    @staticmethod
    def _parse_equation(expression: str) -> sp.Eq:
        # replace common operators into sympy compatible syntax
        # 1) Absolute value brackets [ ]
        expression = re.sub(r"\|([^|]+)\|", r"Abs(\1)", expression)
        
        lhs, rhs = expression.split("=", 1)

        lhs = sp.sympify(lhs.strip())
        rhs = sp.sympify(rhs.strip())

        return sp.Eq(lhs, rhs)
                        
    def formula_sets(self) -> dict[str, FormulaSet]:
        return self._formula_sets
    
    def formula(self, formula_id: str) -> FormulaSet:
        if formula_id not in self._formula_sets:
            raise KeyError(
                f"Formel '{formula_id}' nicht gefunden. "
                f"Nutze search_formulas oder list_categories, um gültige IDs zu finden."
            )
        return self._formula_sets[formula_id]


    def categories(self) -> list[str]:
        cs : set = set()
        for fs in self._formula_sets.values():
            for c in fs.categories:
                cs.add(c)
        return sorted(cs)


    def search(self, query: str, category: str | None = None) -> list[FormulaSet]:
        q = query.lower().strip()
        results = []
        for f in self._formula_sets.values():
            for c in f.categories:
                if category and not c.lower().startswith(category.lower()):
                    continue
            haystack = " ".join(
                [
                    f.id,
                    f.name,
                    " ".join(f.categories),
                    " ".join(f.tags),
                    " ".join(m.description_de or "" for m in f.symbols.values()),
                ]
            ).lower()
            if not q or q in haystack:
                results.append(f)
        return results

class MaterialRegistry():
    pass
