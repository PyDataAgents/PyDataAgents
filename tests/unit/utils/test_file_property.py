import ctypes
from ctypes import wintypes
from datetime import datetime, timezone

datei = r"C:\Users\jhillenb\OneDrive - Steinmeyer Holding GmbH\Produktentwicklung (STA) - Dokumente\5_Versuche (STA)\_archiv\V20151202_Klebeversuche\20170213_Versuchsbericht_Freigabe_Klebstoff.pdf"

# Gewünschte Zeitpunkte
erstellt = datetime(2017, 2, 10, 10, 30, 1, tzinfo=timezone.utc)
geaendert = datetime(2017, 2, 20, 14, 15, 0, tzinfo=timezone.utc)


def datetime_to_filetime(dt):
    value = int(dt.timestamp() * 10_000_000) + 116444736000000000
    return wintypes.FILETIME(
        value & 0xFFFFFFFF,
        value >> 32
    )


creation_time = datetime_to_filetime(erstellt)
last_write_time = datetime_to_filetime(geaendert)


handle = ctypes.windll.kernel32.CreateFileW(
    datei,
    0x0100,  # FILE_WRITE_ATTRIBUTES
    0x00000003,  # FILE_SHARE_READ | FILE_SHARE_WRITE
    None,
    3,  # OPEN_EXISTING
    0,
    None
)

if handle == wintypes.HANDLE(-1).value:
    raise ctypes.WinError()

try:

    result = ctypes.windll.kernel32.SetFileTime(
        handle,
        ctypes.byref(creation_time),    # Erstellungsdatum
        None,                            # Letzter Zugriff unverändert
        ctypes.byref(last_write_time)   # Änderungsdatum
    )

    if not result:
        raise ctypes.WinError()

finally:
    ctypes.windll.kernel32.CloseHandle(handle)

print("Erstellungsdatum und Änderungsdatum wurden gesetzt.")