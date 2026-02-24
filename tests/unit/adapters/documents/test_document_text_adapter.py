from pydag.adapters.documents.DocumentTextAdapter import DocumentTextAdapter


def test_000():
    a = DocumentTextAdapter()
    
    print(a.config_options())