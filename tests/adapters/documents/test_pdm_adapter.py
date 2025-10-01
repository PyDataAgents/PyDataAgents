import win32com.client

def test_000():
    # Create vault object
    vault = win32com.client.Dispatch("ConisioLib.EdmVault5")

    # Login to the vault
    vault.Login("YourUsername", "YourPassword", "YourVaultName")
    