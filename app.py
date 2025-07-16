import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
import time

from document_processor import DocumentProcessor
from vector_store_manager import VectorStoreManager
from rag_engine import RAGEngine

load_dotenv()

st.set_page_config(
    page_title="RAG Document Q&A System",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for ChatGPT-like interface
st.markdown("""
<style>
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background-color: #fafafa;
        margin: 1rem 0;
    }
    
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin: 1rem 0;
    }
    
    .user-bubble {
        background-color: #007bff;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 18px 18px 4px 18px;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    .assistant-message {
        display: flex;
        justify-content: flex-start;
        margin: 1rem 0;
    }
    
    .assistant-bubble {
        background-color: #f1f3f4;
        color: #333;
        padding: 0.75rem 1rem;
        border-radius: 18px 18px 18px 4px;
        max-width: 70%;
        word-wrap: break-word;
        border: 1px solid #e0e0e0;
    }
    
    .timestamp {
        font-size: 0.7rem;
        color: #666;
        margin-top: 0.25rem;
    }
    
    .chat-input {
        position: sticky;
        bottom: 0;
        background-color: white;
        padding: 1rem 0;
        border-top: 1px solid #e0e0e0;
    }
    
    .sources-section {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 8px;
        margin-top: 0.5rem;
        border-left: 4px solid #007bff;
    }
    
    .source-doc {
        background-color: white;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 4px;
        font-size: 0.8rem;
        border: 1px solid #e0e0e0;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 20px;
    }
    
    .upload-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'vector_store_manager' not in st.session_state:
        st.session_state.vector_store_manager = VectorStoreManager()
    
    if 'document_processor' not in st.session_state:
        st.session_state.document_processor = DocumentProcessor()
    
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = RAGEngine()
    
    if 'current_vector_store' not in st.session_state:
        st.session_state.current_vector_store = None
    
    if 'current_store_name' not in st.session_state:
        st.session_state.current_store_name = None
    
    if 'qa_chain' not in st.session_state:
        st.session_state.qa_chain = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""

def sidebar_knowledge_base_management():
    st.sidebar.header("📚 Knowledge Base Management")
    
    available_stores = st.session_state.vector_store_manager.list_available_stores()
    
    if available_stores:
        st.sidebar.subheader("Select Existing Knowledge Base")
        selected_store = st.sidebar.selectbox(
            "Choose a knowledge base:",
            ["None"] + available_stores,
            index=0 if st.session_state.current_store_name is None else 
                  (available_stores.index(st.session_state.current_store_name) + 1 
                   if st.session_state.current_store_name in available_stores else 0)
        )
        
        if selected_store != "None" and selected_store != st.session_state.current_store_name:
            with st.spinner(f"Loading knowledge base: {selected_store}"):
                vector_store = st.session_state.vector_store_manager.load_vector_store(selected_store)
                if vector_store:
                    st.session_state.current_vector_store = vector_store
                    st.session_state.current_store_name = selected_store
                    st.session_state.qa_chain = st.session_state.rag_engine.create_qa_chain(vector_store)
                    st.sidebar.success(f"Loaded: {selected_store}")
                else:
                    st.sidebar.error(f"Failed to load: {selected_store}")
    else:
        st.sidebar.info("No existing knowledge bases found.")
    
    st.sidebar.subheader("Create New Knowledge Base")
    new_store_name = st.sidebar.text_input("Enter name for new knowledge base:")
    
    if st.sidebar.button("Create New Knowledge Base"):
        if new_store_name and new_store_name not in available_stores:
            st.session_state.current_store_name = new_store_name
            st.session_state.current_vector_store = None
            st.session_state.qa_chain = None
            st.sidebar.success(f"Ready to create: {new_store_name}")
        elif new_store_name in available_stores:
            st.sidebar.error("Knowledge base name already exists!")
        else:
            st.sidebar.error("Please enter a valid name!")

def document_upload_section():
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("### 📄 Document Upload")
        
        if st.session_state.current_store_name is None:
            st.warning("⚠️ Please select or create a knowledge base first.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        st.info(f"📚 Current Knowledge Base: **{st.session_state.current_store_name}**")
        
        uploaded_files = st.file_uploader(
            "Choose PDF or Word documents",
            type=['pdf', 'docx', 'doc'],
            accept_multiple_files=True,
            help="Upload one or more PDF or Word documents to add to your knowledge base."
        )
        
        col1, col2 = st.columns([3, 1])
        with col2:
            process_btn = st.button("🚀 Process Documents", type="primary", disabled=not uploaded_files)
        
        if uploaded_files and process_btn:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("📖 Reading documents...")
                progress_bar.progress(25)
                documents = st.session_state.document_processor.process_documents(uploaded_files)
                
                status_text.text("🔍 Creating embeddings...")
                progress_bar.progress(50)
                
                if st.session_state.current_vector_store is None:
                    status_text.text("🏗️ Creating knowledge base...")
                    progress_bar.progress(75)
                    st.session_state.current_vector_store = st.session_state.vector_store_manager.create_vector_store(
                        documents, st.session_state.current_store_name
                    )
                    status_text.text("✅ Knowledge base created!")
                    st.success(f"🎉 Created new knowledge base '{st.session_state.current_store_name}' with {len(documents)} document chunks.")
                else:
                    status_text.text("📚 Adding to existing knowledge base...")
                    progress_bar.progress(75)
                    st.session_state.current_vector_store = st.session_state.vector_store_manager.add_documents_to_store(
                        st.session_state.current_vector_store, documents, st.session_state.current_store_name
                    )
                    status_text.text("✅ Documents added!")
                    st.success(f"🎉 Added {len(documents)} document chunks to '{st.session_state.current_store_name}'.")
                
                progress_bar.progress(100)
                st.session_state.qa_chain = st.session_state.rag_engine.create_qa_chain(st.session_state.current_vector_store)
                
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                with st.expander("👀 View processed documents"):
                    for i, doc in enumerate(documents[:5]):
                        st.text(f"📄 Chunk {i+1}: {doc.page_content[:200]}...")
                        if i >= 4 and len(documents) > 5:
                            st.text(f"... and {len(documents) - 5} more chunks")
                            break
                            
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error processing documents: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_chat_message(message, is_user=True):
    timestamp = datetime.now().strftime("%I:%M %p")
    
    if is_user:
        st.markdown(f"""
        <div class="user-message">
            <div class="user-bubble">
                {message['content']}
                <div class="timestamp">{timestamp}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        sources_html = ""
        if message.get('sources'):
            sources_html = '<div class="sources-section"><strong>📚 Sources:</strong>'
            for i, source in enumerate(message['sources'][:3]):
                filename = source.metadata.get('filename', 'Unknown')
                content_preview = source.page_content[:100] + "..." if len(source.page_content) > 100 else source.page_content
                sources_html += f'<div class="source-doc"><strong>📄 {filename}:</strong><br>{content_preview}</div>'
            sources_html += '</div>'
        
        st.markdown(f"""
        <div class="assistant-message">
            <div class="assistant-bubble">
                🤖 {message['content']}
                {sources_html}
                <div class="timestamp">{timestamp}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def chat_interface():
    st.markdown("### 💬 Chat with your Documents")
    
    if st.session_state.current_vector_store is None:
        st.warning("⚠️ Please upload documents to a knowledge base first.")
        return
    
    # Chat history container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="assistant-message">
                <div class="assistant-bubble">
                    👋 Hello! I'm ready to help you explore your documents. Ask me anything about the content you've uploaded!
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.chat_history:
            display_chat_message(message, message['role'] == 'user')
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input section
    st.markdown('<div class="chat-input">', unsafe_allow_html=True)
    
    # Create input form for Enter key functionality
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Ask me anything about your documents...",
                label_visibility="collapsed",
                key="chat_input"
            )
        
        with col2:
            send_button = st.form_submit_button("Send 📤", type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process user input
    if send_button and user_input.strip():
        # Add user message to chat history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        # Show typing indicator
        with st.spinner("🤔 Thinking..."):
            result = st.session_state.rag_engine.query(st.session_state.qa_chain, user_input)
            
            if result["success"]:
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': result["answer"],
                    'sources': result["source_documents"],
                    'timestamp': datetime.now()
                })
            else:
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': f"❌ Sorry, I encountered an error: {result['answer']}",
                    'timestamp': datetime.now()
                })
        
        # Rerun to update the chat display
        st.rerun()
    
    # Clear chat button
    if st.session_state.chat_history and st.button("🗑️ Clear Chat", help="Clear conversation history"):
        st.session_state.chat_history = []
        st.rerun()

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 2rem;">
        <h1>📚 RAG Document Q&A System</h1>
        <p>Upload documents and chat with AI-powered search and retrieval</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not os.getenv("OPENAI_API_KEY"):
        st.error("🔑 Please set your OPENAI_API_KEY in the .env file.")
        st.stop()
    
    # Sidebar for knowledge base management
    sidebar_knowledge_base_management()
    
    # Main content layout
    document_upload_section()
    
    # Chat interface
    st.markdown("<br>", unsafe_allow_html=True)
    chat_interface()
    
    # Sidebar stats
    if st.session_state.current_vector_store:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Knowledge Base Stats")
        try:
            doc_count = len(st.session_state.current_vector_store.docstore._dict)
            st.sidebar.metric("Document Chunks", doc_count)
            st.sidebar.metric("Current KB", st.session_state.current_store_name)
        except:
            st.sidebar.text("Stats unavailable")
        
        # Add some helpful tips
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💡 Tips")
        st.sidebar.markdown("""
        - Use specific questions for better answers
        - Check source documents for context
        - Clear chat to start fresh conversations
        - Upload more documents to expand knowledge
        """)

if __name__ == "__main__":
    main()