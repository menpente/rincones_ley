import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import pickle
import os
import re

class VectorStore:
    def __init__(self):
        # Configurar TF-IDF con parámetros optimizados para español
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=None,  # Sin stop words por defecto
            ngram_range=(1, 2),
            lowercase=True,
            token_pattern=r'\b[a-záéíóúüñ]+\b'  # Incluir caracteres españoles
        )
        self.tfidf_matrix = None
        self.documents = []
        
    def build_index(self, documents: List[Dict[str, str]]):
        """Construye el índice TF-IDF con los documentos"""
        if not documents:
            return
        
        print("Generando vectores TF-IDF...")
        texts = [self._preprocess_text(doc['text']) for doc in documents]
        
        # Crear matriz TF-IDF
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        self.documents = documents
        print(f"Índice construido con {len(documents)} documentos")
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocesa el texto para mejorar la búsqueda"""
        # Convertir a minúsculas y limpiar
        text = text.lower()
        # Eliminar caracteres especiales excepto letras españolas
        text = re.sub(r'[^\w\s\náéíóúüñ]', ' ', text)
        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Busca documentos similares usando TF-IDF y cosine similarity"""
        if self.tfidf_matrix is None or not self.documents:
            return []
        
        # Preprocesar y vectorizar la consulta
        query_processed = self._preprocess_text(query)
        query_vector = self.vectorizer.transform([query_processed])
        
        # Calcular similitudes coseno
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # Obtener los k más similares
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for i, idx in enumerate(top_indices):
            if similarities[idx] > 0:  # Solo incluir resultados con similitud > 0
                result = self.documents[idx].copy()
                result['similarity_score'] = similarities[idx]
                result['rank'] = i + 1
                results.append(result)
        
        return results
    
    def save_index(self, filepath: str = "vector_index"):
        """Guarda el índice y documentos en archivos"""
        if self.tfidf_matrix is not None:
            # Guardar matriz TF-IDF
            with open(f"{filepath}_tfidf.pkl", 'wb') as f:
                pickle.dump(self.tfidf_matrix, f)
            # Guardar vectorizador
            with open(f"{filepath}_vectorizer.pkl", 'wb') as f:
                pickle.dump(self.vectorizer, f)
            # Guardar documentos
            with open(f"{filepath}_docs.pkl", 'wb') as f:
                pickle.dump(self.documents, f)
            print(f"Índice guardado en {filepath}")
    
    def load_index(self, filepath: str = "vector_index") -> bool:
        """Carga el índice y documentos desde archivos"""
        try:
            files_needed = [f"{filepath}_tfidf.pkl", f"{filepath}_vectorizer.pkl", f"{filepath}_docs.pkl"]
            if all(os.path.exists(f) for f in files_needed):
                # Cargar matriz TF-IDF
                with open(f"{filepath}_tfidf.pkl", 'rb') as f:
                    self.tfidf_matrix = pickle.load(f)
                # Cargar vectorizador
                with open(f"{filepath}_vectorizer.pkl", 'rb') as f:
                    self.vectorizer = pickle.load(f)
                # Cargar documentos
                with open(f"{filepath}_docs.pkl", 'rb') as f:
                    self.documents = pickle.load(f)
                print(f"Índice cargado desde {filepath}")
                return True
        except Exception as e:
            print(f"Error cargando índice: {e}")
        return False