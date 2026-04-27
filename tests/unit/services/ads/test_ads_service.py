import pytest

try:
    from pydag.services.ads.AdsService import AdsService
except (ImportError, OSError, FileNotFoundError) as exc:
    pytest.skip(f"ADS tests require pyads/TcAdsDll: {exc}", allow_module_level=True)


def test_000():
    a = AdsService()   
    print(a.config_options) 
