# Contextual Retrieval Logic

## Core Problem
Traditional RAG chunks documents without context, losing important semantic information about where each chunk fits in the overall document.

## Contextual Retrieval Solution

### 1. **Context Generation Phase**
- For each document chunk, use Claude to generate a 50-100 token contextual description
- The description explains what the chunk is about and how it relates to the whole document
- Example prompt: "Give a short succinct context to situate this chunk within the overall document"

### 2. **Enhanced Embeddings**
- Instead of embedding just the raw chunk text
- Embed the contextual description + original chunk text
- This creates "contextual embeddings" with richer semantic information

### 3. **Contextual BM25**
- Similarly enhance the lexical search (BM25/TF-IDF)
- Index the contextual text instead of just raw chunks
- Improves keyword matching with added context

### 4. **Hybrid Retrieval**
- Combine contextual embeddings + contextual BM25 scores
- Use weighted combination (e.g., 70% contextual embeddings, 30% BM25)
- Optionally add reranking for further improvement

## Implementation Flow for Your System

1. **Document Processing**: When processing PDFs, generate contextual descriptions for each chunk
2. **Index Building**: Create TF-IDF vectors from contextual text (description + original)
3. **Search**: Query against contextual index, combine with traditional search
4. **Results**: Return documents with improved relevance scores

## Expected Benefits
- 35% reduction in retrieval failure rate with contextual embeddings
- 49% reduction when combining contextual embeddings + BM25
- 67% reduction with added reranking

## Cost Considerations
- One-time cost: $1.02 per million document tokens for contextualization
- Upfront investment for long-term retrieval accuracy improvements