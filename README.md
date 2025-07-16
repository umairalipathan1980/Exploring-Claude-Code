# 📚 RAG Document Q&A System

A naive RAG (Retrieval-Augmented Generation) built with Claude Code. 


![RAG System](https://img.shields.io/badge/RAG-System-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white) ![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-2D3748?logo=langchain&logoColor=white)

## ✨ Features

### 📄 Document Processing
- **Multi-format Support**: Upload PDF and Word (.docx, .doc) documents
- **Intelligent Chunking**: Automatic text splitting optimized for retrieval
- **Batch Processing**: Handle multiple documents simultaneously
- **Progress Tracking**: Real-time processing status with progress bars

### 🧠 AI-Powered Chat
- **ChatGPT-like Interface**: Modern conversation bubbles with timestamps
- **Enter Key Support**: Send messages by pressing Enter
- **Conversation History**: Persistent chat history with scrollable interface
- **Source Attribution**: View source documents for each response
- **Smart Retrieval**: Context-aware answers from your documents only

### 🗃️ Knowledge Base Management
- **Multiple Knowledge Bases**: Create and switch between different document collections
- **Persistent Storage**: Knowledge bases saved automatically using FAISS
- **Easy Management**: Load existing or create new knowledge bases
- **Statistics Dashboard**: View document counts and knowledge base info


## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- LangChain
- Streamlit
- FAISS

### Installation

1. **Clone or download the project**:
   ```bash
   cd experimental
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API**:
   - Add your OpenAI API key to the `.env` file:
     ```env
     OPENAI_API_KEY=your_actual_openai_api_key_here
     ```

4. **Launch the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** and navigate to the displayed URL (typically `http://localhost:8501`)

## 📖 How to Use

### Step 1: Knowledge Base Setup
1. **Create New**: Enter a name for your knowledge base in the sidebar
2. **Or Select Existing**: Choose from previously created knowledge bases
3. The app automatically detects and loads existing knowledge bases on startup

### Step 2: Document Upload
1. **Select Files**: Use the drag-and-drop uploader for PDF or Word documents
2. **Process Documents**: Click "🚀 Process Documents" to add them to your knowledge base
3. **Monitor Progress**: Watch the real-time processing status
4. **View Results**: Expand to see processed document chunks

### Step 3: Interactive Chat
1. **Start Chatting**: Type your question in the chat input
2. **Send Message**: Press Enter or click "Send 📤"
3. **View Responses**: See AI responses with source document references
4. **Continue Conversation**: Build on previous questions and answers
5. **Clear History**: Use "🗑️ Clear Chat" to start fresh

### Pro Tips 💡
- **Be Specific**: More detailed questions yield better answers
- **Check Sources**: Review source documents for additional context
- **Multiple Documents**: Upload related documents for comprehensive knowledge
- **Conversation Flow**: Build complex queries by referencing previous answers

## 🏗️ Architecture

### File Structure
```
experimental/
├── app.py                    # Main Streamlit application with UI
├── document_processor.py     # Document loading and text chunking
├── vector_store_manager.py   # FAISS vector store operations
├── rag_engine.py            # RAG query engine with OpenAI
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (API keys)
├── README.md               # This documentation
└── vector_stores/          # Persistent knowledge bases (auto-created)
    ├── knowledge_base_1/
    ├── knowledge_base_2/
    └── ...
```

## ⚙️ Configuration

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Customization Options
- **Chunk Size**: Modify `chunk_size` in `DocumentProcessor` (default: 1000)
- **Chunk Overlap**: Adjust `chunk_overlap` for better context (default: 200)
- **Retrieval Count**: Change `k` parameter in RAG engine (default: 4)
- **Model Selection**: Update model names in `rag_engine.py`

## 🔧 Advanced Features

### Knowledge Base Management
- **Automatic Detection**: Finds existing knowledge bases on startup
- **Incremental Updates**: Add new documents to existing knowledge bases
- **Statistics Tracking**: Monitor document counts and storage usage
- **Error Handling**: Robust error recovery and user feedback

### Chat Features
- **Context Awareness**: Maintains conversation context
- **Source Transparency**: Shows exact document sources for each answer
- **Message Persistence**: Conversation history survives page refreshes
- **Real-time Updates**: Instant message display and status updates

## 🐛 Troubleshooting

### Common Issues

**"Please set your OPENAI_API_KEY"**
- Ensure your `.env` file contains a valid OpenAI API key
- Check that the key has sufficient credits and permissions

**"Error processing documents"**
- Verify document format (PDF, DOCX, DOC only)
- Check file size and ensure documents aren't corrupted
- Try processing documents individually

**"Stats unavailable"**
- This is normal for newly created knowledge bases
- Stats will appear after successful document processing

**Slow Performance**
- Large documents may take time to process
- Consider splitting very large files before upload
- Check your internet connection for OpenAI API calls

### Getting Help
- Check the sidebar tips for usage guidance
- Review source documents if answers seem incomplete
- Try rephrasing questions for better results

## 📝 License

This project is open source and available under the MIT License.

