from __future__ import annotations

import importlib.util
from fnmatch import fnmatch
from pathlib import Path


def _module_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


OPTIONAL_TEST_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "cadquery": (
        "tests/unit/services/cad/test_ballscrew.py",
        "tests/unit/services/cad/test_cadquery.py",
        "tests/unit/services/cad/test_flange_nut_axial_deflector.py",
    ),
    "docxtpl": (
        "tests/unit/adapters/documents/test_docx_adapter.py",
        "tests/unit/nodes/documents/test_docxtemplate_action.py",
    ),
    "langgraph.graph": (
        "tests/regression/agents/test_llmsqlservice_agent.py",
        "tests/unit/services/llm/test_llmsqlservice.py",
    ),
    "msal": (
        "tests/regression/services/office/test_MSGraphService.py",
    ),
    "mistralai": (
        "tests/unit/nodes/llm/test_llm_ocr_action.py",
    ),
    "ross": (
        "tests/unit/services/datamodel/mbs/test_rotordynamics.py",
    ),
    "sktime": (
        "tests/unit/nodes/dataset/test_sampleddataset.py",
    ),
    "serial": (
        "tests/unit/adapters/socket/test_bytestream_adapter.py",
        "tests/unit/adapters/socket/test_serial_adapter.py",
    ),
    "sktime.forecasting.chronos": (
        "tests/unit/nodes/regression/test_RegressionTransform.py",
    ),
    "pytesseract": (
        "tests/unit/nodes/ocr/test_ocr_action.py",
    ),
    "librosa": (
        "tests/unit/utils/test_signal_utils.py",
    ),
    "vobject": (
        "tests/unit/nodes/documents/test_ical_action.py",
    ),
}

MISSING_OPTIONAL_MODULES = {
    module_name
    for module_name in OPTIONAL_TEST_DEPENDENCIES
    if not _module_available(module_name)
}


def pytest_ignore_collect(collection_path, config) -> bool:
    # Keep test discovery working when optional extras are not installed.
    collection_file = Path(str(collection_path))
    if collection_file.suffix != ".py":
        return False

    root_path = Path(str(config.rootpath))
    try:
        relative_path = collection_file.relative_to(root_path).as_posix()
    except ValueError:
        relative_path = collection_file.as_posix()

    for module_name in MISSING_OPTIONAL_MODULES:
        for pattern in OPTIONAL_TEST_DEPENDENCIES[module_name]:
            if fnmatch(relative_path, pattern):
                return True
    return False
