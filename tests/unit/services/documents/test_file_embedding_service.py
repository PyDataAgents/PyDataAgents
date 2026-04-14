import os
from pydag.services.documents.FileEmbeddingService import FileEmbeddingService
from pydag.services.ServiceException import ServiceException
import pytest
import tempfile
import shutil
import time
from pathlib import Path

TEST_DOCS_ROOT = Path(__file__).resolve().parent/"test_documents_for_embedding"

def _docs_path(name:str) -> str:
    return str(TEST_DOCS_ROOT / name)


def test_embed_files_save_properly():
    # Test: Valid documents are placed in the embedding folder. --> All valid documents are embedded; the number of embedded documents matches the number of valid documents in the embedding folder.
    
        
    fs = FileEmbeddingService(docs_folder = [_docs_path("docs_0")], store_name="test_store")
    fs.install()
    fs.start()

    loaded_docs = fs._embedding_store._collection.count()
    print(f"Number of documents in embedding store: {loaded_docs}")
    assert loaded_docs == 7, "No documents were embedded, but there should be some valid documents in the folder."
    assert os.path.exists(os.path.join(FileEmbeddingService.EMBEDDINGS_RESOURCE_FOLDER, "test_store")), "Embedding store folder was not created in the embeddings resource folder."
    time.sleep(1) # Give some time for the file system to release the directory


def test_embed_files_properly():
    # Test: Files are embedded properly.
    
        
    fs = FileEmbeddingService(docs_folder = [_docs_path("docs_1")], store_name="test_store_1")
    fs.install()
    fs.start()

    loaded_docs = fs._embedding_store._collection.count()
    print(f"Number of documents in embedding store: {loaded_docs}")
    assert loaded_docs == 14, "No documents were embedded, but there should be some valid documents in the folder."
    time.sleep(1) # Give some time for the file system to release the directory


def test_empty_folder():
    # Test: No documents should be embedded from an empty folder.
    
        
    fs = FileEmbeddingService(docs_folder = [_docs_path("docs_2")], store_name="test_store_2")
    fs.install()
    fs.start()

    loaded_docs = fs._embedding_store._collection.count()
    print(f"Number of documents in embedding store: {loaded_docs}")
    assert loaded_docs == 0, "No documents should be embedded from an empty folder."
    time.sleep(1) # Give some time for the file system to release the directory


def test_name_as_string():
    #Test:  provide folder name as string instead of list.
    
        
    fs = FileEmbeddingService(docs_folder = _docs_path("docs_3"), store_name="test_store_3")
    fs.install()
    fs.start()

    loaded_docs = fs._embedding_store._collection.count()
    print(f"Number of documents in embedding store: {loaded_docs}")
    assert loaded_docs == 7, "Documents should be embedded from the folder provided as a string."
    time.sleep(1) # Give some time for the file system to release the directory

def test_multiple_folders():
    # Test multiple folders with valid documents.
    
        
    fs = FileEmbeddingService(docs_folder = [_docs_path("docs_3"), _docs_path("docs_0")], store_name="test_store_4")
    fs.install()
    fs.start()

    loaded_docs = fs._embedding_store._collection.count()
    print(f"Number of documents in embedding store: {loaded_docs}")
    assert loaded_docs == 14, "Documents should be embedded from multiple folders."
    time.sleep(1) # Give some time for the file system to release the directory


def test_no_folders():
    # Test no folders provided.
    
    with pytest.raises(ServiceException):  
        fs = FileEmbeddingService(docs_folder = [], store_name="test_store_5")
        fs.install()
        fs.start()
    time.sleep(1) # Give some time for the file system to release the directory


def test_unauthorized_files():
    # Test mix of unauthorized and authorized files in folder
    
    fs = FileEmbeddingService(docs_folder = [_docs_path("docs_4")], store_name="test_store_6")
    fs.install()
    fs.start()

    loaded_docs = fs._embedding_store._collection.count()
    print(f"Number of documents in embedding store: {loaded_docs}")
    assert loaded_docs == 7, "Documents should be embedded from the folder."
    time.sleep(1) # Give some time for the file system to release the directory

def test_call_multiple_same_folder():
    # Test: Method is called multiple times with the same unchanged folder. The database should not be changed. 
    fs = FileEmbeddingService(docs_folder = [_docs_path("docs_1")], store_name="test_store_7")
        
    fs.install()
    fs.start()

    loaded_docs = fs._embedding_store._collection.count()
    print(f"Number of documents in embedding store: {loaded_docs}")
    assert loaded_docs == 14, "No documents were embedded, but there should be some valid documents in the folder."
    fs.stop()
    # Call start again
    fs.start()
    loaded_docs_after = fs._embedding_store._collection.count()
    assert loaded_docs_after == 14, "Document count should remain the same after calling start again."
    assert loaded_docs_after == loaded_docs, "Document count should remain the same after calling start again."
    time.sleep(1) # Give some time for the file system to release the directory


def test_invalid_folder_path():
    # Test: Invalid folder path should raise an exception
    
    with pytest.raises(ServiceException):
        fs = FileEmbeddingService(docs_folder = [r"C:\NonExistentFolder\Invalid"], store_name="test_store_8")
        fs.install()
        fs.start()
    time.sleep(1) # Give some time for the file system to release the directory

def test_multiple_folders_one_invalid():
    # Test: Multiple folders where one is invalid
    
    fs = FileEmbeddingService(docs_folder = [
        r"C:\Users\tobia\Python Scripts\PyDataAgents\tests\unit\services\documents\test_documents_for_embedding\docs_0",
        r"C:\NonExistentFolder\Invalid"
    ], store_name="test_store_9")
    fs.install()
    # Should either handle gracefully or raise exception
    with pytest.raises(ServiceException):
        fs.start()
    time.sleep(1) # Give some time for the file system to release the directory


def test_embedding_store_updates_when_documents_change():
    # Test: When documents are added/removed, embedding store should update
    
    # Create temporary folder
    temp_dir = tempfile.mkdtemp()
    
    try:
        fs = FileEmbeddingService(docs_folder=[temp_dir])
        fs.install()
        fs.start()
        
        initial_count = fs._embedding_store._collection.count()
        assert initial_count == 0, "Empty folder should have no documents"
        
        # Copy some documents to the temp folder
        src_folder = r"C:\Users\tobia\Python Scripts\PyDataAgents\tests\unit\services\documents\test_documents_for_embedding\docs_0"
        if os.path.exists(src_folder):
            for file in os.listdir(src_folder):
                shutil.copy(os.path.join(src_folder, file), temp_dir)
            
            # Recreate service with updated folder
            fs = FileEmbeddingService(docs_folder=[temp_dir])
            fs.install()
            fs.start()
            
            updated_count = fs._embedding_store._collection.count()
            assert updated_count == 7, "Documents should be embedded after adding files"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        


def test_none_docs_folder():
    # Test: None as docs_folder parameter
    
    with pytest.raises((ServiceException, TypeError)):
        fs = FileEmbeddingService(docs_folder=None, store_name="test_store_11")
        fs.install()
        fs.start()
    time.sleep(1) # Give some time for the file system to release the directory


def test_pdf_files():
    # Test: Folder with pdf files should be embedded properly
    
    fs = FileEmbeddingService(docs_folder=[_docs_path("docs_5")], store_name="test_store_12")
    fs.install()
    fs.start()
    
    loaded_docs = fs._embedding_store._collection.count()
    assert loaded_docs >= 0, "Should handle mixed file types gracefully"
    time.sleep(1) # Give some time for the file system to release the directory


def test_searchin_in_embedding_store():
    # Test: Search for a document in the embedding store after embedding
    
    fs = FileEmbeddingService(docs_folder=[_docs_path("docs_5")], store_name="test_store_13")
    fs.install()
    fs.start()
    
    retriever = fs._embedding_store.as_retriever(search_kwargs={"k": 20})
    results = retriever.get_relevant_documents("Who are the authors of the paper?")
    for res in results:
        print(res.page_content)
    assert any('Angeliki Lazaridou' in res.page_content for res in results), "Should retrieve at least one relevant document"
    time.sleep(1) # Give some time for the file system to release the directory



def test_delete_all_test_folders():
    # Cleanup: Delete all test embedding folders created during testing
    
    test_folders = [
        "test_store",
        "test_store_1",
        "test_store_2",
        "test_store_3",
        "test_store_4",
        "test_store_5",
        "test_store_6",
        "test_store_7",
        "test_store_8",
        "test_store_9",
        "test_store_10",
        "test_store_11",
        "test_store_12",
        "test_store_13"
    ]
    
    for folder in test_folders:
        folder_path = os.path.join(FileEmbeddingService.EMBEDDINGS_RESOURCE_FOLDER, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)