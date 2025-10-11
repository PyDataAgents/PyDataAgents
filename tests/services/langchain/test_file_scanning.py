from pathlib import Path
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores.utils import filter_complex_metadata

def test_000():
    file = "tests\\data\\pdf\\unsup.pdf"
    loader = UnstructuredLoader(file)
    documents = loader.load()
    # filter for complex data        
    filtered_docs = filter_complex_metadata(documents)
    # Split into chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    split_docs = text_splitter.split_documents(filtered_docs)
    
    for d in split_docs:
        print(d.page_content)
        
def test_010():
    file = Path.home() / "Downloads" / "slides.pptx"
    loader = UnstructuredLoader(file)
    documents = loader.load()
    # filter for complex data        
    filtered_docs = filter_complex_metadata(documents)
    # Split into chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    split_docs = text_splitter.split_documents(filtered_docs)
    
    for d in split_docs:
        print(d.page_content)
    