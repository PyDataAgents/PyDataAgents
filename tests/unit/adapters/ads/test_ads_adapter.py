import pytest

try:
    from pydag.adapters.ads.AdsAdapter import AdsAdapter
except (ImportError, OSError, FileNotFoundError) as exc:
    pytest.skip(f"ADS tests require pyads/TcAdsDll: {exc}", allow_module_level=True)


def test_000():
    a = AdsAdapter()   
    print(a.config_options) 
