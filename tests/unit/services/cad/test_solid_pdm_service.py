import pytest
import win32com.client

@pytest.mark.skip(reason="not working with: due to 32/64bit issues")
def test_000():
    # Create vault object
    vault = win32com.client.Dispatch("ConisioLib.EdmVault5")

    # Login to the vault
    vault.Login("YourUsername", "YourPassword", "YourVaultName")
    