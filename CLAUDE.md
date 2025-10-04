# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Environment
```bash
# Activate virtual environment (required)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional dependencies for contextual retrieval
pip install anthropic
```

### Running the Application
```bash
# Basic mode (hybrid search only)
export GROQ_API_KEY="your_groq_key"
streamlit run app.py

# Premium mode (with contextual retrieval)
export GROQ_API_KEY="your_groq_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
streamlit run app.py
```

### Testing Components
```bash
# Test basic imports and initialization
python3 -c "from rag_system import RAGSystem; print('✅ RAG system imports correctly')"

# Test document processing
python3 -c "from document_processor import DocumentProcessor; dp = DocumentProcessor(); print('✅ Document processor ready')"

# Test contextual retrieval
python3 -c "from contextual_retrieval import ContextualRetrieval; print('✅ Contextual retrieval available')"

# Test hybrid reranking
python3 -c "from hybrid_reranking import HybridReranker; print('✅ Hybrid reranking available')"
```

## Architecture Overview

### Multi-Layer RAG System
This is a sophisticated RAG (Retrieval-Augmented Generation) system with three search methods that automatically prioritize based on available API keys:

1. **Traditional Search** (baseline): Basic TF-IDF vectorization
2. **Hybrid Reranking** (free upgrade): Multi-vectorizer search with legal-specific reranking
3. **Contextual Retrieval** (premium): Claude-generated context descriptions for chunks

### Core Components

#### RAGSystem (`rag_system.py`)
- **Central orchestrator** that coordinates all search methods
- **Automatic method selection**: Contextual > Hybrid > Traditional based on available API keys
- **Search priority logic**: `retrieve_context()` method implements the selection hierarchy
- **Index management**: Handles loading/saving of all index types simultaneously

#### Search Method Hierarchy
```
Priority 1: ContextualRetrieval (if ANTHROPIC_API_KEY available)
├── Uses Claude to generate 50-100 token context descriptions
├── Combines contextual + traditional search with 70/30 weighting
└── Cost: $25.75 one-time for current document set

Priority 2: HybridReranker (always available, default)
├── Triple search: Semantic + Keyword + Phrase vectorizers
├── Legal-specific reranking with term coverage, legal bonuses
└── Cost: Free

Priority 3: VectorStore (fallback)
└── Traditional TF-IDF search (baseline)
```

#### Document Processing Pipeline
- **DocumentProcessor**: Extracts text from PDFs, creates chunks with overlap
- **Returns tuple**: `(chunks, whole_documents)` where whole_documents enables contextual processing
- **Legal text optimization**: Preserves article references ("artículo 123") and legal citations

### Index Storage Strategy
The system maintains separate persistent indexes:
- `vector_index_*.pkl`: Traditional TF-IDF indexes
- `hybrid_index_*.pkl`: Multiple vectorizer indexes for hybrid search
- `contextual_index_*.pkl`: Contextual descriptions + enhanced indexes (if premium)

### Key Integration Points

#### RAGSystem.initialize()
Critical method that:
1. Checks for existing indexes of all types
2. Rebuilds only missing indexes (no unnecessary reprocessing)
3. Handles incremental upgrades (traditional → hybrid → contextual)

#### RAGSystem.retrieve_context()
The search method selector that implements the priority hierarchy. Modify this to change search behavior or add new methods.

#### Document Location
- Legal PDFs must be in `ref/` directory
- System auto-detects and processes all `.pdf` files
- Current set: Spanish Penal Code, Criminal Procedure Law, Immigration Law

### Configuration Patterns

#### Environment Variables (Recommended)
```bash
GROQ_API_KEY="required_for_llm"
ANTHROPIC_API_KEY="optional_for_contextual_retrieval"
```

#### Programmatic Configuration
```python
# Free hybrid search (default)
rag = RAGSystem(groq_api_key="key")

# Disable hybrid for traditional only
rag = RAGSystem(groq_api_key="key", use_hybrid_reranking=False)

# Enable premium contextual
rag = RAGSystem(groq_api_key="key", anthropic_api_key="key")
```

### Legal Domain Optimizations

#### Text Preprocessing
- Preserves legal article numbers: "artículo 123" → "articulo_123"
- Handles legal citations: "ley 15/2023" → "ley_15_2023"
- Spanish character support in tokenization patterns

#### Reranking Factors (in HybridReranker)
- **Legal keyword bonus**: Recognizes "artículo", "ley", "código", "reglamento"
- **Document position bonus**: Earlier chunks often contain key definitions
- **Term coverage scoring**: Rewards results matching more query terms
- **Length optimization**: Penalizes very short/long chunks

### Extension Points

#### Adding New Search Methods
1. Create new search class following `HybridReranker` pattern
2. Add to `RAGSystem.__init__()` initialization
3. Extend `retrieve_context()` priority logic
4. Add index loading/saving in `initialize()`

#### Legal Domain Customization
- **Legal keywords**: Modify `legal_keywords` list in `HybridReranker.rerank_results()`
- **Reference patterns**: Update regex patterns in `_preprocess_text()` methods
- **Chunk boundaries**: Adjust `chunk_size` and `overlap` in `DocumentProcessor`

### System Prompt
Loaded from `system_prompt.md` - contains legal domain instructions for the LLM. The system gracefully falls back to a default prompt if file is missing.

### Cost Considerations
- **Hybrid reranking**: No additional costs (local processing)
- **Contextual retrieval**: One-time $25.75 for current document set
- **Usage costs**: Only Groq API calls for LLM responses (typically $0.001-0.002 per query)