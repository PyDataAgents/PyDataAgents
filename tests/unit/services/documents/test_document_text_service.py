from pydag.services.documents.DocumentTextService import DocumentTextService


def test_000():
    a = DocumentTextService()
    
    print(a.config_options())