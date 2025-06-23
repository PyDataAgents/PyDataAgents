import ast
from pathlib import Path
from typing import List, Dict, Set

from pydatagrabber.grabbers.GrabberElement import GrabberElement
from pydatagrabber.utils.ClassUtils import ClassUtils
from pydatagrabber.utils.TimeUtils import TimeUtils


# Stores class inheritance and definitions across the codebase
class_hierarchy: Dict[str, List[str]] = {}
class_defs: Dict[str, ast.ClassDef] = {}
class_modules: Dict[str, Path] = {}

def get_full_name(node):
    """Extract the name from ast.Name or ast.Attribute nodes."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{get_full_name(node.value)}.{node.attr}"
    return ""

def extract_class_info(file_path: Path, base_dir : Path):
    with open(file_path, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filename=str(file_path))

    for item in node.body:
        if isinstance(item, ast.ClassDef):
            class_name = item.name
            bases = [get_full_name(base) for base in item.bases]
            class_hierarchy[class_name] = bases
            class_defs[class_name] = item
            class_modules[class_name] = file_path.relative_to(base_dir)

def inherits_from_type(cls_name: str, type : str, seen: Set[str] = None) -> bool:
    """Recursively check if a class inherits from GrabberElement."""
    if seen is None:
        seen = set()
    if cls_name in seen:
        return False
    seen.add(cls_name)

    bases = class_hierarchy.get(cls_name, [])
    for base in bases:
        if base == type or base.endswith("." + type):
            return True
        if base in class_hierarchy:
            if inherits_from_type(base, type, seen):
                return True
    return False

def inherits_from_types(class_name: str, types: List[str], seen: Set[str] = None) -> bool:
    """Check if `class_name` inherits from any class in `types`, recursively."""
    if seen is None:
        seen = set()
    if class_name in seen:
        return False
    seen.add(class_name)

    bases = class_hierarchy.get(class_name, [])

    for base in bases:
        # Check direct match or qualified match
        if base in types or any(base.endswith("." + t) for t in types):
            return True
        if base in class_hierarchy and inherits_from_types(base, types, seen):
            return True
    return False

def get_all_fields(cls_name: str, seen: Set[str] = None) -> List[Dict]:
    """Get fields from the entire class hierarchy, starting from base classes."""
    if seen is None:
        seen = set()
    if cls_name in seen:
        return []
    seen.add(cls_name)

    fields = []

    # First, get fields from base classes
    for base in class_hierarchy.get(cls_name, []):
        if base in class_defs:
            fields.extend(get_all_fields(base, seen))

    # Then add fields from this class (overrides will replace duplicates by name)
    class_def = class_defs[cls_name]
    own_fields = extract_fields(class_def)

    # Replace duplicates by field name (child overrides parent)
    seen_names = {f['name'] for f in own_fields}
    fields = [f for f in fields if f['name'] not in seen_names]
    fields.extend(own_fields)

    return fields

def extract_fields(class_def: ast.ClassDef) -> List[Dict]:
    fields = []
    
    # always retrieve GrabberElement fields
    ge_fields = ClassUtils.get_dataclass_fields(GrabberElement)
    for ge_field in ge_fields:
        fields.append({
            "name": ge_field.name,
            "type": ge_field.type if ge_field.type else None,
            "description": ge_field.metadata.get("description", ""),
            "default": repr(ge_field.default) if ge_field.default is not None else ""
        })
    
    # remove type field
    fields = [f for f in fields if f['name'] != 'type']
    
    for stmt in class_def.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            field_name = stmt.target.id
            field_type = ast.unparse(stmt.annotation) if stmt.annotation else "Unknown"
            description = ""
            default = None
            if stmt.value and isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "field":
                    for keyword in stmt.value.keywords:
                        if keyword.arg == "default":
                            try:
                                default = ast.literal_eval(keyword.value)
                            except Exception:
                                default = ast.unparse(keyword.value)
                        elif keyword.arg == "default_factory":
                            default = f"{ast.unparse(keyword.value)}()"
                        if keyword.arg == "metadata":
                            if isinstance(keyword.value, ast.Dict):
                                for key_node, value_node in zip(keyword.value.keys, keyword.value.values):
                                    if isinstance(key_node, ast.Constant) and key_node.value == "description":
                                        description = value_node.value if isinstance(value_node, ast.Constant) else ""
                else:
                    try:
                        default = ast.literal_eval(stmt.value)
                    except Exception:
                        default = ast.unparse(stmt.value)
                        
            fields.append({
                "name": field_name,
                "type": field_type,
                "description": description,
                "default": repr(default) if default is not None else ""
            })
        
    return fields

def scan_repository(base_dir: Path, type : str):
    # First pass: collect class definitions and hierarchy
    for py_file in base_dir.rglob("*.py"):
        extract_class_info(py_file, base_dir)

    # Second pass: identify grabber classes
    summary = []
    for class_name, class_def in class_defs.items():
        if inherits_from_type(class_name, type):
            fields = get_all_fields(class_name)
            docstring = ast.get_docstring(class_def) or ""
            summary.append({
                "name": class_name,
                "docstring": docstring,
                "fields": fields,
                "file": class_modules[class_name]
            })
    return summary

def generate_readme(class_data: List[Dict], output_file: Path, name : str):
    lines = ["# " + name + " Documentation\n"]
    
    # class summary
    lines.append("## Summary\n")
    lines.append("| Class | Description |")
    lines.append("|-------|-------------|")

    for cls in sorted(class_data, key=lambda x: str(x["file"])):
        anchor = f"{cls['name'].lower()}-from-{str(cls['file']).replace('/', '').replace('.py', '')}"
        docstring = cls["docstring"] if cls["docstring"] else ""
        lines.append(f"| [`{cls['name']}`](#{anchor}) | {docstring} |")
    lines.append("\n\n")
    
    # class details    
    for cls in sorted(class_data, key=lambda x: str(x["file"])):
        lines.append(f"## `{cls['name']}` (from `{cls['file']}`)\n")
        if cls["docstring"]:
            lines.append(cls["docstring"])
        if not cls["fields"]:
            lines.append("_No fields defined._\n")
            continue
        # Table headers
        lines.append("| Field | Type | Default | Description |")
        lines.append("|-------|------|---------|-------------|")

        # Table rows
        for field in cls["fields"]:
            lines.append(f"| `{field['name']}` | `{field['type']}` | `{field['default']}` | {field['description']} |")
        
        lines.append("")  # newline between classes
        
        # code section
        lines.append("")  # Newline after table
        # Code Example
        lines.append("```python")
        lines.append(f"# Example usage of `{cls['name']}`")
        lines.append(f"from pydatagrabber import {cls['name']}  # Adjust import if needed\n")
        # Instantiate the class with placeholder values
        init_args = []
        for field in cls["fields"]:
            if field["default"]:
                # If a default value is provided, use it
                value = field["default"]
            else:
                # Otherwise, guess a placeholder value based on the type
                value = guess_placeholder_value(field["type"], field["name"])
            init_args.append(f"{field['name']}={value}")
        constructor = f"{cls['name']}(\n    " + ",\n    ".join(init_args) + "\n)"
        lines.append(f"obj = {constructor}")

        # Optional method call
        #lines.append("obj.run()  # or obj.grab(), etc.\n")
        
        # end code section
        lines.append("```")
        lines.append("")  # Extra newline between classes
        
    output_file.write_text("\n".join(lines), encoding="utf-8")

def guess_placeholder_value(type_str: str, field : str) -> str:
    """Returns a placeholder value as a string based on type or field string."""
    type_str = type_str.lower()
    if "str" in type_str:
        if "file" in field.lower():
            return '"path/to/file.txt"'
        elif "url" in field.lower():
            return '"https://example.com"'
        elif "email" in field.lower():
            return '"john.doe@example.com"'
        elif "name" in field.lower():
            return '"John Doe"'
        elif "folder" in field.lower():
            return '"path/to/folder"'
        else:
            return '"<string>"'
    elif "int" in type_str:
        return '1'
    elif "float" in type_str:
        return '3.14'
    elif "bool" in type_str:
        return 'True'
    elif "list" in type_str or "sequence" in type_str:
        return '[]'
    elif "dict" in type_str:
        return '{}'
    elif "datetime" in type_str:
        return '"' + TimeUtils.now_iso8601() + '"  # datetime as ISO string'
    else:
        return '"<value>"'

def generate_docs_for_type(name : str, type : str, src_folder : Path, docu_folder : Path):
    """Generate documentation for a specific type of class."""
    class_info = scan_repository(src_folder, type)
    generate_readme(class_info, docu_folder / (name + ".md"), name)
    class_hierarchy.clear()
    class_defs.clear()
    class_modules.clear()   

# Run the whole process
if __name__ == "__main__":
    
    # find all grabbers
    generate_docs_for_type("Grabbers", GrabberElement.cname(), Path("pydatagrabber\\grabbers"), Path("docs\\"))
    
    # find all adapters
    generate_docs_for_type("Adapters", GrabberElement.cname(), Path("pydatagrabber\\adapters"), Path("docs\\"))

    # find all buffers
    generate_docs_for_type("Buffers", GrabberElement.cname(), Path("pydatagrabber\\buffers"), Path("docs\\"))

    # find all mappings
    generate_docs_for_type("Mappings", GrabberElement.cname(), Path("pydatagrabber\\mappings"), Path("docs\\"))

    # find all services
    generate_docs_for_type("Services", GrabberElement.cname(), Path("pydatagrabber\\services"), Path("docs\\"))
    
    # find Statemachine Nodes
    generate_docs_for_type("Actions and Transitions", GrabberElement.cname(), Path("pydatagrabber\\statemachine"), Path("docs\\"))


