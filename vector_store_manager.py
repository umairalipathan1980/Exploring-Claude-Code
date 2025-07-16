import os
import pickle
from typing import List, Optional
from pathlib import Path

import faiss
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document


class VectorStoreManager:
    def __init__(self, embeddings_model: str = "text-embedding-3-large"):
        self.embeddings = OpenAIEmbeddings(model=embeddings_model)
        self.vector_stores_dir = Path("vector_stores")
        self.vector_stores_dir.mkdir(exist_ok=True)
    
    def create_vector_store(self, documents: List[Document], store_name: str) -> FAISS:
        if not documents:
            raise ValueError("Cannot create vector store with empty documents")
        
        vector_store = FAISS.from_documents(documents, self.embeddings)
        self.save_vector_store(vector_store, store_name)
        return vector_store
    
    def load_vector_store(self, store_name: str) -> Optional[FAISS]:
        store_path = self.vector_stores_dir / store_name
        if not store_path.exists():
            return None
        
        try:
            return FAISS.load_local(str(store_path), self.embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            print(f"Error loading vector store {store_name}: {e}")
            return None
    
    def save_vector_store(self, vector_store: FAISS, store_name: str):
        store_path = self.vector_stores_dir / store_name
        store_path.mkdir(exist_ok=True)
        vector_store.save_local(str(store_path))
    
    def add_documents_to_store(self, vector_store: FAISS, documents: List[Document], store_name: str) -> FAISS:
        if not documents:
            return vector_store
        
        vector_store.add_documents(documents)
        self.save_vector_store(vector_store, store_name)
        return vector_store
    
    def list_available_stores(self) -> List[str]:
        if not self.vector_stores_dir.exists():
            return []
        
        stores = []
        for item in self.vector_stores_dir.iterdir():
            if item.is_dir() and (item / "index.faiss").exists():
                stores.append(item.name)
        
        return sorted(stores)
    
    def delete_vector_store(self, store_name: str) -> bool:
        store_path = self.vector_stores_dir / store_name
        if not store_path.exists():
            return False
        
        try:
            import shutil
            shutil.rmtree(store_path)
            return True
        except Exception as e:
            print(f"Error deleting vector store {store_name}: {e}")
            return False
    
    def get_store_info(self, store_name: str) -> dict:
        vector_store = self.load_vector_store(store_name)
        if not vector_store:
            return {}
        
        return {
            "name": store_name,
            "document_count": len(vector_store.docstore._dict),
            "created": os.path.getctime(self.vector_stores_dir / store_name)
        }