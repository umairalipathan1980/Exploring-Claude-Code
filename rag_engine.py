from typing import List, Optional
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document


class RAGEngine:
    def __init__(self, model_name: str = "gpt-4-1106-preview"):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0,
            max_tokens=1000
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant that answers questions based on the provided context. 
Use only the information from the context to answer the question. If the answer cannot be found in the context, 
say "I cannot find the answer in the provided documents."

Context:
{context}

Question: {question}

Answer: """
        )
    
    def create_qa_chain(self, vector_store: FAISS, k: int = 4) -> RetrievalQA:
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={
                "prompt": self.prompt_template
            },
            return_source_documents=True
        )
        
        return qa_chain
    
    def query(self, qa_chain: RetrievalQA, question: str) -> dict:
        try:
            result = qa_chain({"query": question})
            return {
                "answer": result["result"],
                "source_documents": result["source_documents"],
                "success": True
            }
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "source_documents": [],
                "success": False
            }
    
    def get_relevant_documents(self, vector_store: FAISS, question: str, k: int = 4) -> List[Document]:
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        return retriever.get_relevant_documents(question)