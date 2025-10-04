import numpy as np
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


class HybridReranker:
    """
    Cost-free hybrid search with reranking implementation
    Combines multiple retrieval methods without requiring external APIs
    """

    def __init__(self):
        # Multiple TF-IDF vectorizers for different approaches
        self.semantic_vectorizer = None  # Focus on semantic content
        self.keyword_vectorizer = None   # Focus on exact keywords
        self.phrase_vectorizer = None    # Focus on phrases

        # Matrices for different approaches
        self.semantic_matrix = None
        self.keyword_matrix = None
        self.phrase_matrix = None

        self.documents = []

    def build_hybrid_index(self, documents: List[Dict]):
        """Build multiple indexes for hybrid retrieval"""
        if not documents:
            return

        print("🔨 Building hybrid retrieval indexes...")
        self.documents = documents

        # Extract and preprocess texts
        texts = [self._preprocess_text(doc['text']) for doc in documents]

        # 1. Semantic-focused vectorizer (broader context)
        self.semantic_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8,
            stop_words=None,
            lowercase=True,
            token_pattern=r'\b[a-záéíóúüñ]+\b'
        )
        self.semantic_matrix = self.semantic_vectorizer.fit_transform(texts)

        # 2. Keyword-focused vectorizer (exact matches)
        self.keyword_vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 1),  # Single words only
            min_df=1,
            lowercase=True,
            token_pattern=r'\b[a-záéíóúüñ]+\b'
        )
        self.keyword_matrix = self.keyword_vectorizer.fit_transform(texts)

        # 3. Phrase-focused vectorizer (legal phrases)
        self.phrase_vectorizer = TfidfVectorizer(
            max_features=8000,
            ngram_range=(2, 4),  # 2-4 word phrases
            min_df=1,
            lowercase=True,
            token_pattern=r'\b[a-záéíóúüñ]+\b'
        )
        self.phrase_matrix = self.phrase_vectorizer.fit_transform(texts)

        print(f"✅ Hybrid indexes built: {len(documents)} documents")
        print(f"   Semantic features: {self.semantic_matrix.shape[1]}")
        print(f"   Keyword features: {self.keyword_matrix.shape[1]}")
        print(f"   Phrase features: {self.phrase_matrix.shape[1]}")

    def _preprocess_text(self, text: str) -> str:
        """Enhanced preprocessing for legal text"""
        text = text.lower()
        # Preserve legal article numbers (e.g., "artículo 123")
        text = re.sub(r'\bartículo\s+(\d+)', r'articulo_\1', text)
        text = re.sub(r'\bart\.\s*(\d+)', r'articulo_\1', text)
        # Preserve legal references
        text = re.sub(r'\bley\s+(\d+/\d+)', r'ley_\1', text)
        # Clean other characters
        text = re.sub(r'[^\w\s\náéíóúüñ_]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def hybrid_search(self, query: str, k: int = 10) -> List[Dict]:
        """
        Perform hybrid search using multiple retrieval methods
        """
        if not all([self.semantic_matrix is not None,
                   self.keyword_matrix is not None,
                   self.phrase_matrix is not None]):
            print("❌ Hybrid indexes not built")
            return []

        query_processed = self._preprocess_text(query)
        results_dict = {}

        # 1. Semantic search
        semantic_vector = self.semantic_vectorizer.transform([query_processed])
        semantic_similarities = cosine_similarity(semantic_vector, self.semantic_matrix)[0]

        # 2. Keyword search
        keyword_vector = self.keyword_vectorizer.transform([query_processed])
        keyword_similarities = cosine_similarity(keyword_vector, self.keyword_matrix)[0]

        # 3. Phrase search
        phrase_vector = self.phrase_vectorizer.transform([query_processed])
        phrase_similarities = cosine_similarity(phrase_vector, self.phrase_matrix)[0]

        # Combine scores with weights
        for i in range(len(self.documents)):
            doc_key = (self.documents[i]['filename'], self.documents[i]['chunk_id'])

            # Weighted combination
            combined_score = (
                0.4 * semantic_similarities[i] +    # Semantic understanding
                0.4 * keyword_similarities[i] +     # Exact keyword matches
                0.2 * phrase_similarities[i]        # Legal phrase matches
            )

            if combined_score > 0:
                doc = self.documents[i].copy()
                doc['hybrid_score'] = combined_score
                doc['semantic_score'] = semantic_similarities[i]
                doc['keyword_score'] = keyword_similarities[i]
                doc['phrase_score'] = phrase_similarities[i]
                results_dict[doc_key] = doc

        # Sort by hybrid score
        results = list(results_dict.values())
        results.sort(key=lambda x: x['hybrid_score'], reverse=True)

        return results[:k*2]  # Return more for reranking

    def rerank_results(self, query: str, results: List[Dict], final_k: int = 5) -> List[Dict]:
        """
        Rerank results using multiple criteria without external APIs
        """
        if not results:
            return []

        query_lower = query.lower()
        query_words = set(query_lower.split())

        for result in results:
            text_lower = result['text'].lower()

            # 1. Query term coverage
            text_words = set(text_lower.split())
            term_coverage = len(query_words.intersection(text_words)) / len(query_words) if query_words else 0

            # 2. Legal keyword bonus
            legal_keywords = ['artículo', 'ley', 'código', 'reglamento', 'decreto', 'jurisprudencia', 'sentencia']
            legal_bonus = sum(1 for keyword in legal_keywords if keyword in text_lower) * 0.1

            # 3. Document position bonus (earlier chunks often more important)
            position_bonus = max(0, 0.1 - (result['chunk_id'] * 0.01))

            # 4. Length penalty for very short or very long chunks
            text_len = len(result['text'])
            if text_len < 100:
                length_penalty = -0.2
            elif text_len > 2000:
                length_penalty = -0.1
            else:
                length_penalty = 0

            # 5. Exact phrase bonus
            phrase_bonus = 0.2 if query_lower in text_lower else 0

            # Calculate rerank score
            rerank_score = (
                result['hybrid_score'] * 0.6 +  # Base hybrid score
                term_coverage * 0.2 +           # Query coverage
                legal_bonus * 0.1 +             # Legal relevance
                position_bonus +                # Document position
                length_penalty +                # Length appropriateness
                phrase_bonus                    # Exact phrase match
            )

            result['rerank_score'] = rerank_score
            result['term_coverage'] = term_coverage
            result['legal_bonus'] = legal_bonus

        # Sort by rerank score
        results.sort(key=lambda x: x['rerank_score'], reverse=True)

        return results[:final_k]

    def enhanced_search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Complete enhanced search pipeline: hybrid search + reranking
        """
        print(f"🔍 Enhanced hybrid search: '{query}'")

        # Step 1: Hybrid search
        hybrid_results = self.hybrid_search(query, k=k)
        print(f"📊 Hybrid search found: {len(hybrid_results)} candidates")

        # Step 2: Reranking
        final_results = self.rerank_results(query, hybrid_results, final_k=k)
        print(f"🎯 Reranked to final: {len(final_results)} results")

        # Add ranking information
        for i, result in enumerate(final_results):
            result['final_rank'] = i + 1

        return final_results

    def save_hybrid_index(self, filepath: str = "hybrid_index"):
        """Save hybrid indexes"""
        import pickle

        if all([self.semantic_matrix is not None,
               self.keyword_matrix is not None,
               self.phrase_matrix is not None]):

            # Save matrices
            with open(f"{filepath}_semantic.pkl", 'wb') as f:
                pickle.dump((self.semantic_matrix, self.semantic_vectorizer), f)
            with open(f"{filepath}_keyword.pkl", 'wb') as f:
                pickle.dump((self.keyword_matrix, self.keyword_vectorizer), f)
            with open(f"{filepath}_phrase.pkl", 'wb') as f:
                pickle.dump((self.phrase_matrix, self.phrase_vectorizer), f)
            with open(f"{filepath}_docs.pkl", 'wb') as f:
                pickle.dump(self.documents, f)

            print(f"📁 Hybrid index saved to {filepath}")

    def load_hybrid_index(self, filepath: str = "hybrid_index") -> bool:
        """Load hybrid indexes"""
        import pickle
        import os

        try:
            files_needed = [
                f"{filepath}_semantic.pkl",
                f"{filepath}_keyword.pkl",
                f"{filepath}_phrase.pkl",
                f"{filepath}_docs.pkl"
            ]

            if all(os.path.exists(f) for f in files_needed):
                with open(f"{filepath}_semantic.pkl", 'rb') as f:
                    self.semantic_matrix, self.semantic_vectorizer = pickle.load(f)
                with open(f"{filepath}_keyword.pkl", 'rb') as f:
                    self.keyword_matrix, self.keyword_vectorizer = pickle.load(f)
                with open(f"{filepath}_phrase.pkl", 'rb') as f:
                    self.phrase_matrix, self.phrase_vectorizer = pickle.load(f)
                with open(f"{filepath}_docs.pkl", 'rb') as f:
                    self.documents = pickle.load(f)

                print(f"✅ Hybrid index loaded from {filepath}")
                return True
        except Exception as e:
            print(f"❌ Error loading hybrid index: {e}")
        return False