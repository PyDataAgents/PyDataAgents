import enum


class DatasetNames(str, enum.Enum):
    ArrowHead = "ArrowHead"
    AbnormalHeartbeat = "AbnormalHeartbeat"
    Car = "Car"
    ChlorineConcentration = "ChlorineConcentration"
    Crop = "Crop"
    ECG5000 = "ECG5000"
    ElectricDevices = "ElectricDevices"
    FordA = "FordA"
    InsectSound = "InsectSound"
    KeplerLightCurves = "KeplerLightCurves"
    Plane = "Plane"
    ShapesAll = "ShapesAll"
    UWaveGestureLibrary = "UWaveGestureLibrary"
    Wafer = "Wafer"
    Wine = "Wine"
    Blobs = "Blobs"  # This is a sklearn dataset which creates Clusters. https://scikit-learn.org/stable/modules/generated/sklearn.datasets.make_blobs.html