from dataclasses import dataclass
from typing import Any
import win32com.client
import pythoncom
from loguru import logger

from ..Service import Service
from ...agents.Agent import Agent


@dataclass
class SolidWorksService(Service):
    
    def __post_init__(self):
        super().__post_init__()
        self._sw_app : Any = None
        self._active_doc : Any = None
        self._errors : Any = None
        self._warnings : Any = None
    
    def _on_install(self, agent :Agent = None):
        super()._on_install(agent)
        # Required for some COM calls
        pythoncom.CoInitialize()

        # Start SolidWorks or get active application
        try:
            self._sw_app = win32com.client.GetActiveObject("SldWorks.Application")
            logger.debug("Connected to existing SolidWorks session")
        except Exception:
            self._sw_app = win32com.client.Dispatch("SldWorks.Application")
            logger.debug("opened new SolidWorks session")
        
        self._sw_app.Visible = True
        
        # init error and warning object
        self._errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        self._warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        
        return
    
    def _on_uninstall(self, agent=None):
        super()._on_uninstall(agent)
        self._sw_app = None
        self._active_doc = None
        return
           
    def _on_start(self):
        return
    
    def _on_stop(self):
        self._sw_app : Any = None
        self._active_doc : Any = None
        self._errors : Any = None
        self._warnings : Any = None
        return
    
    def open_model(self, model_path : str):
        model = self._sw_app.OpenDoc6(
            model_path,
            1,      # swDocPART
            0,      # swOpenDocOptions_Silent
            "",
            self._errors,
            self._warnings
        )
        
        self._active_doc = model
        return model
       
    def get_application(self) -> Any:
        return self._sw_app
    
    def get_active_model(self) -> Any:
        return self._active_doc
    
    # VBA-like helper wrappers
    def open_assembly(self, assemblyPath: str) -> Any:
        if self._sw_app is None:
            logger.error("No Solidworks Application was specified")
            return None
        errors = pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        warnings = pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        swAssembly = self._sw_app.OpenDoc6(assemblyPath, 2, 0, "", errors, warnings)
        return swAssembly

    def set_active_model(self) -> Any:
        swModel = None
        if self._sw_app is not None:
            swModel = self._sw_app.ActiveDoc
        if swModel is None:
            logger.error("No active model was found!")
            return None
        return swModel

    def new_assembly(self) -> Any:
        return self._sw_app.NewDocument("", 2, 0, 0)

    def add_component(self, assembly: Any, componentPath: str) -> Any:
        return assembly.AddComponent(componentPath, 0, 0, 0)

    def activate_config(self, swModel: Any, configName: str) -> bool:
        try:
            configNames = list(swModel.GetConfigurationNames())
        except Exception:
            configNames = swModel.GetConfigurationNames()
        for name in configNames:
            if name == configName:
                swModel.ShowConfiguration(name)
                return True
        return False

    def get_config_names(self, swModel: Any):
        try:
            return list(swModel.GetConfigurationNames())
        except Exception:
            return swModel.GetConfigurationNames()

    def regenerate(self, swModel: Any, allConfigs: bool = False):
        if allConfigs:
            swCfgMgr = swModel.ConfigurationManager
            try:
                currentConfigName = swCfgMgr.ActiveConfiguration.Name
            except Exception:
                currentConfigName = None
            try:
                configNames = list(swModel.GetConfigurationNames())
            except Exception:
                configNames = swModel.GetConfigurationNames()
            for name in configNames:
                try:
                    swModel.ShowConfiguration(name)
                except Exception:
                    pass
                try:
                    swModel.ForceRebuild3(False)
                except Exception:
                    try:
                        swModel.EditRebuild3()
                    except Exception:
                        pass
            if currentConfigName:
                try:
                    swModel.ShowConfiguration(currentConfigName)
                except Exception:
                    pass
        else:
            try:
                swModel.ForceRebuild3(False)
            except Exception:
                try:
                    swModel.EditRebuild3()
                except Exception:
                    pass

    def save_model(self, swModel: Any):
        errors = pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        warnings = pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        try:
            swModel.Save3(1, errors, warnings)
            if errors.value != 0:
                logger.error(f"ERROR@Save failed. Error code: {errors.value}")
        except Exception as e:
            logger.error(f"ERROR@swSaveModel: {e}")

    def set_fileproperties(self, modelDoc: Any, fileProperties: dict, ignoreMissing: bool = False) -> bool:
        if modelDoc is None:
            return False
        for key, value in fileProperties.items():
            try:
                existing = modelDoc.Extension.CustomPropertyManager("").Get(key)
            except Exception:
                existing = None
            if existing is not None and existing != "":
                try:
                    modelDoc.Extension.CustomPropertyManager("").Set2(key, value)
                except Exception as e:
                    logger.error(f"ERROR@swSetFileProperties: Failed to set {key} -> {value}: {e}")
                    if not ignoreMissing:
                        return False
            else:
                logger.error(f"ERROR@swSetFileProperties: file property does not exist: {key}")
                if not ignoreMissing:
                    return False
        return True

    def set_fileproperties2(self, modelPath: str, fileProperties: dict) -> bool:
        modelDoc = self.open_model(modelPath)
        ok = self.swSetFileProperties(modelDoc, fileProperties, True)
        try:
            self.swRegenerate(modelDoc)
            self.swRegenerate(modelDoc)
        except Exception:
            pass
        return ok

    def get_feature(self, swModel: Any, featureName: str) -> Any:
        swFeature = swModel.FeatureByName(featureName)
        if swFeature is None:
            logger.error(f"ERROR@swGetFeature: {featureName} was not found")
            return None
        return swFeature

    def set_model_parameter(self, swModel: Any, parameterName: str, value, inAllConfigs: bool = False) -> bool:
        try:
            swParam = swModel.Parameter(parameterName)
        except Exception:
            try:
                swParam = swModel.parameter(parameterName)
            except Exception:
                swParam = None
        if swParam is None:
            logger.error(f"ERROR@swSetModelParameter: Parameter {parameterName} was not found!")
            return False
        try:
            if inAllConfigs:
                swParam.SetSystemValue3(value, 2, None)
            else:
                swParam.SystemValue = value
            return True
        except Exception as e:
            logger.error(f"ERROR@swSetModelParameter: {e}")
            return False

    def set_model_parameter_tolerance(self, model: Any, parameterName: str, toleranceType: int, upperTol: float, lowerTol: float, fit: str = "") -> bool:
        swFeature = model.FirstFeature
        while swFeature is not None:
            swDispDim = swFeature.GetFirstDisplayDimension()
            while swDispDim is not None:
                swDim = swDispDim.GetDimension()
                try:
                    swDim.SetToleranceType(toleranceType)
                    swDim.SetToleranceValues(lowerTol, upperTol)
                    if fit:
                        try:
                            swDim.Tolerance.SetFitValues("", fit)
                        except Exception:
                            try:
                                swDim.Tolerance.SetFitValues(fit, "")
                            except Exception:
                                pass
                except Exception:
                    pass
                pn = getattr(swDim, 'Name', '')
                fn = getattr(swFeature, 'Name', '')
                if parameterName == f"{pn}@{fn}":
                    return True
                swDispDim = swFeature.GetNextDisplayDimension(swDispDim)
            swFeature = swFeature.GetNextFeature()
        return False

    def set_model_parameter_2(self, swModel: Any, parameterName: str, parameterValue: float, toleranceType: int, upperTol: float, lowerTol: float, fit: str = "") -> bool:
        swFeature = swModel.FirstFeature
        while swFeature is not None:
            swDispDim = swFeature.GetFirstDisplayDimension()
            while swDispDim is not None:
                try:
                    swParam = swModel.Parameter(parameterName)
                    swParam.SystemValue = parameterValue
                except Exception:
                    pass
                swDim = swDispDim.GetDimension()
                try:
                    swDim.SetToleranceType(toleranceType)
                    swDim.SetToleranceValues(lowerTol, upperTol)
                    if fit:
                        try:
                            swDim.Tolerance.SetFitValues("", fit)
                        except Exception:
                            try:
                                swDim.Tolerance.SetFitValues(fit, "")
                            except Exception:
                                pass
                except Exception:
                    pass
                pn = getattr(swDim, 'Name', '')
                fn = getattr(swFeature, 'Name', '')
                if parameterName == f"{pn}@{fn}":
                    return True
                swDispDim = swFeature.GetNextDisplayDimension(swDispDim)
            swFeature = swFeature.GetNextFeature()
        return False

    def set_feature_tolerance(self, swFeature: Any, parameterName: str, toleranceType: int, upperTol: float, lowerTol: float, fit: str = "") -> bool:
        swDispDim = swFeature.GetFirstDisplayDimension()
        while swDispDim is not None:
            swDim = swDispDim.GetDimension()
            pn = getattr(swDim, 'Name', '')
            fn = getattr(swFeature, 'Name', '')
            if parameterName == f"{pn}@{fn}":
                try:
                    swDim.SetToleranceType(toleranceType)
                    swDim.SetToleranceValues(lowerTol, upperTol)
                    if fit and toleranceType == 7:
                        try:
                            swDim.Tolerance.SetFitValues("", fit)
                        except Exception:
                            try:
                                swDim.Tolerance.SetFitValues(fit, "")
                            except Exception:
                                pass
                    else:
                        try:
                            swDim.Tolerance.SetFitValues("", "")
                        except Exception:
                            pass
                except Exception:
                    pass
                return True
            swDispDim = swFeature.GetNextDisplayDimension(swDispDim)
        return False

    def get_model_parameter(self, swModel: Any, parameterName: str) -> float:
        try:
            swParam = swModel.Parameter(parameterName)
        except Exception:
            try:
                swParam = swModel.parameter(parameterName)
            except Exception:
                swParam = None
        if swParam is None:
            logger.error(f"ERROR@swGetModelParameter: Parameter {parameterName} was not found!")
            return 0.0
        return float(swParam.SystemValue)

    def get_model_parameter_2(self, swModel: Any, parameterName: str):
        val = self.swGetModelParameter(swModel, parameterName)
        dimType = toleranceType = 0
        upperTol = lowerTol = 0.0
        fit = ""
        try:
            dt, tt, ut, lt, f = self.swGetModelParameterTolerance(swModel, parameterName)
            dimType = dt; toleranceType = tt; upperTol = ut; lowerTol = lt; fit = f
        except Exception:
            pass
        return val, dimType, toleranceType, upperTol, lowerTol, fit

    def get_model_parameter_3(self, swFeature: Any, dimName: str):
        swDispDim = swFeature.GetFirstDisplayDimension()
        while swDispDim is not None:
            swDim = swDispDim.GetDimension()
            dn = getattr(swDim, 'Name', '')
            if dimName == dn:
                try:
                    v = swDim.GetSystemValue3(1, None)
                    parameterValue = float(v[0]) if v else 0.0
                except Exception:
                    parameterValue = 0.0
                dimType = swDim.getType()
                toleranceType = getattr(swDim.Tolerance, 'Type', -1)
                tolValues = None
                try:
                    tolValues = swDim.GetToleranceValues()
                except Exception:
                    tolValues = None
                lowerTol = upperTol = 0.0
                if tolValues:
                    try:
                        lowerTol = tolValues[0]
                        upperTol = tolValues[1]
                    except Exception:
                        pass
                fit = ""
                if toleranceType == 7:
                    try:
                        fit = swDim.Tolerance.GetHoleFitValue() or swDim.Tolerance.GetShaftFitValue() or ""
                    except Exception:
                        fit = ""
                return parameterValue, dimType, toleranceType, upperTol, lowerTol, fit
            swDispDim = swFeature.GetNextDisplayDimension(swDispDim)
        return None

    def get_model_parameter_tolerance(self, model: Any, parameterName: str):
        dimType = -1
        fit = ""
        toleranceType = -1
        lowerTol = 0.0
        upperTol = 0.0
        swFeature = model.FirstFeature
        while swFeature is not None:
            swDispDim = swFeature.GetFirstDisplayDimension()
            while swDispDim is not None:
                swDim = swDispDim.GetDimension()
                pn = getattr(swDim, 'Name', '')
                fn = getattr(swFeature, 'Name', '')
                if parameterName == f"{pn}@{fn}":
                    try:
                        dimType = swDim.getType()
                    except Exception:
                        dimType = -1
                    try:
                        toleranceType = swDim.Tolerance.Type
                    except Exception:
                        toleranceType = -1
                    try:
                        tolValues = swDim.GetToleranceValues()
                        if tolValues:
                            lowerTol = tolValues[0]
                            upperTol = tolValues[1]
                    except Exception:
                        pass
                    if toleranceType == 7:
                        try:
                            fit = swDim.Tolerance.GetHoleFitValue() or swDim.Tolerance.GetShaftFitValue() or ""
                        except Exception:
                            fit = ""
                    return dimType, toleranceType, upperTol, lowerTol, fit
                swDispDim = swFeature.GetNextDisplayDimension(swDispDim)
            swFeature = swFeature.GetNextFeature()
        return dimType, toleranceType, upperTol, lowerTol, fit

    def get_all_model_parameters(self, swModel: Any, ignoreModelId: bool = True):
        swFeature = swModel.FirstFeature
        col = []
        seen = set()
        while swFeature is not None:
            swDispDim = swFeature.GetFirstDisplayDimension()
            while swDispDim is not None:
                swDim = swDispDim.GetDimension()
                parameterName = getattr(swDim, 'fullName', None) or getattr(swDim, 'FullName', '')
                if ignoreModelId and parameterName:
                    splits = parameterName.split("@")
                    if len(splits) >= 2:
                        parameterName = f"{splits[0]}@{splits[1]}"
                if parameterName and parameterName not in seen:
                    seen.add(parameterName)
                    col.append(parameterName)
                swDispDim = swFeature.GetNextDisplayDimension(swDispDim)
            swFeature = swFeature.GetNextFeature()
        return col

    def sw_tolerance_type(self, tolType: str) -> int:
        mapping = {
            "Basic": 1,
            "Bilateral": 2,
            "Limit": 3,
            "Symmetric": 4,
            "Min": 5,
            "Max": 6,
            "Fit": 7,
            "None": 0,
        }
        return mapping.get(tolType, 0)

    def sw_tolerance_type_name(self, tolId: int) -> str:
        mapping = {
            1: "Basic",
            2: "Bilateral",
            3: "Limit",
            4: "Symmetric",
            5: "Min",
            6: "Max",
            7: "Fit",
            0: "None",
        }
        return mapping.get(tolId, "None")

    def sw_2_dim_str(self, dimType: int) -> str:
        if dimType == 0:
            return "mm"
        if dimType == 1:
            return "°"
        return ""

    def sw_rad(self, degree: float) -> float:
        return degree * (3.14159265358979 / 180.0)

    def sw_deg(self, rad: float) -> float:
        return rad * (180.0 / 3.14159265358979)

    def sw_meter(self, millimeter: float) -> float:
        return millimeter / 1000.0

    def sw_millimeter(self, meter: float) -> float:
        return meter * 1000.0