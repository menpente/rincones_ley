import anthropic
from typing import List, Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import re


class ContextualRetrieval:
    def __init__(self, anthropic_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.contextual_vectorizer = None
        self.contextual_tfidf_matrix = None
        self.contextual_documents = []
        self.contextualization_prompt = """
        <documento>
        {whole_document}
        </documento>

        <fragmento>
        {chunk_content}
        </fragmento>

        Proporciona un contexto breve y conciso para situar este fragmento dentro del documento completo.
        El contexto debe ayudar a entender de qué trata el fragmento y su relevancia en el documento.
        Mantén el contexto entre 50-100 tokens y enfócate en información que mejore la recuperación semántica.
        """

    def generate_contextual_description(self, chunk: Dict, whole_document: str) -> str:
        """
        Genera una descripción contextual para un fragmento usando Claude
        """
        try:
            prompt = self.contextualization_prompt.format(
                whole_document=whole_document[:3000],  # Limitar el documento completo para evitar tokens excesivos
                chunk_content=chunk['text']
            )

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            context = response.content[0].text.strip()
            return context

        except Exception as e:
            print(f"❌ Error generando contexto para fragmento: {e}")
            return ""

    def create_contextual_chunks(self, documents: List[Dict], whole_documents: Dict[str, str]) -> List[Dict]:
        """
        Crea fragmentos contextuales agregando descripciones contextuales generadas por Claude
        """
        contextual_chunks = []
        total_chunks = len(documents)

        print(f"🔄 Generando contextos para {total_chunks} fragmentos...")

        for i, doc in enumerate(documents):
            print(f"📝 Procesando fragmento {i+1}/{total_chunks}: {doc['source']}")

            filename = doc['filename']
            whole_doc = whole_documents.get(filename, "")

            # Generar descripción contextual
            context_description = self.generate_contextual_description(doc, whole_doc)

            if context_description:
                # Crear texto contextual combinando contexto + contenido original
                contextual_text = f"{context_description}\n\n{doc['text']}"

                # Crear nuevo documento con texto contextual
                contextual_doc = doc.copy()
                contextual_doc['contextual_text'] = contextual_text
                contextual_doc['context_description'] = context_description
                contextual_chunks.append(contextual_doc)

                print(f"✅ Contexto generado para {doc['source']}")
            else:
                # Si no se pudo generar contexto, usar el documento original
                contextual_doc = doc.copy()
                contextual_doc['contextual_text'] = doc['text']
                contextual_doc['context_description'] = ""
                contextual_chunks.append(contextual_doc)

                print(f"⚠️ No se pudo generar contexto para {doc['source']}, usando texto original")

        print(f"✅ Fragmentos contextuales creados: {len(contextual_chunks)}")
        return contextual_chunks

    def build_contextual_index(self, contextual_documents: List[Dict]):
        """
        Construye el índice TF-IDF usando los textos contextuales
        """
        if not contextual_documents:
            return

        print("🔨 Construyendo índice contextual...")

        # Configurar TF-IDF para textos contextuales
        self.contextual_vectorizer = TfidfVectorizer(
            max_features=8000,  # Más features para capturar contexto adicional
            stop_words=None,
            ngram_range=(1, 3),  # Incluir trigramas para mejor contexto
            lowercase=True,
            token_pattern=r'\b[a-záéíóúüñ]+\b'
        )

        # Usar textos contextuales para el índice
        contextual_texts = [self._preprocess_text(doc['contextual_text']) for doc in contextual_documents]

        # Crear matriz TF-IDF contextual
        self.contextual_tfidf_matrix = self.contextual_vectorizer.fit_transform(contextual_texts)
        self.contextual_documents = contextual_documents

        print(f"✅ Índice contextual construido con {len(contextual_documents)} documentos")

    def _preprocess_text(self, text: str) -> str:
        """Preprocesa el texto para mejorar la búsqueda"""
        text = text.lower()
        text = re.sub(r'[^\w\s\náéíóúüñ]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def contextual_search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Realiza búsqueda usando embeddings contextuales
        """
        print(f"🔍 Búsqueda contextual: '{query}'")

        if self.contextual_tfidf_matrix is None or not self.contextual_documents:
            print("❌ Índice contextual no inicializado")
            return []

        # Preprocesar consulta
        query_processed = self._preprocess_text(query)
        query_vector = self.contextual_vectorizer.transform([query_processed])

        # Calcular similitudes con textos contextuales
        similarities = cosine_similarity(query_vector, self.contextual_tfidf_matrix)[0]

        # Obtener top k resultados
        top_indices = np.argsort(similarities)[::-1][:k]

        results = []
        for i, idx in enumerate(top_indices):
            score = similarities[idx]
            if score > 0:
                result = self.contextual_documents[idx].copy()
                result['contextual_similarity_score'] = score
                result['contextual_rank'] = i + 1
                results.append(result)

        print(f"📝 Resultados contextuales encontrados: {len(results)}")
        return results

    def hybrid_search(self, query: str, traditional_results: List[Dict], k: int = 5,
                     alpha: float = 0.7) -> List[Dict]:
        """
        Combina resultados contextuales con tradicionales usando ponderación
        """
        contextual_results = self.contextual_search(query, k=k*2)  # Obtener más para mezclar

        # Crear diccionario para combinar resultados por chunk_id y filename
        combined_scores = {}

        # Agregar puntuaciones tradicionales
        for result in traditional_results:
            key = (result['filename'], result['chunk_id'])
            combined_scores[key] = {
                'doc': result,
                'traditional_score': result.get('similarity_score', 0),
                'contextual_score': 0
            }

        # Agregar puntuaciones contextuales
        for result in contextual_results:
            key = (result['filename'], result['chunk_id'])
            if key in combined_scores:
                combined_scores[key]['contextual_score'] = result['contextual_similarity_score']
            else:
                combined_scores[key] = {
                    'doc': result,
                    'traditional_score': 0,
                    'contextual_score': result['contextual_similarity_score']
                }

        # Calcular puntuación híbrida
        hybrid_results = []
        for key, scores in combined_scores.items():
            hybrid_score = (alpha * scores['contextual_score'] +
                          (1 - alpha) * scores['traditional_score'])

            doc = scores['doc']
            doc['hybrid_score'] = hybrid_score
            doc['traditional_score'] = scores['traditional_score']
            doc['contextual_score'] = scores['contextual_score']
            hybrid_results.append(doc)

        # Ordenar por puntuación híbrida
        hybrid_results.sort(key=lambda x: x['hybrid_score'], reverse=True)

        return hybrid_results[:k]

    def save_contextual_index(self, filepath: str = "contextual_index"):
        """Guarda el índice contextual"""
        if self.contextual_tfidf_matrix is not None:
            with open(f"{filepath}_tfidf.pkl", 'wb') as f:
                pickle.dump(self.contextual_tfidf_matrix, f)
            with open(f"{filepath}_vectorizer.pkl", 'wb') as f:
                pickle.dump(self.contextual_vectorizer, f)
            with open(f"{filepath}_docs.pkl", 'wb') as f:
                pickle.dump(self.contextual_documents, f)
            print(f"📁 Índice contextual guardado en {filepath}")

    def load_contextual_index(self, filepath: str = "contextual_index") -> bool:
        """Carga el índice contextual"""
        try:
            files_needed = [f"{filepath}_tfidf.pkl", f"{filepath}_vectorizer.pkl", f"{filepath}_docs.pkl"]
            if all(os.path.exists(f) for f in files_needed):
                with open(f"{filepath}_tfidf.pkl", 'rb') as f:
                    self.contextual_tfidf_matrix = pickle.load(f)
                with open(f"{filepath}_vectorizer.pkl", 'rb') as f:
                    self.contextual_vectorizer = pickle.load(f)
                with open(f"{filepath}_docs.pkl", 'rb') as f:
                    self.contextual_documents = pickle.load(f)
                print(f"✅ Índice contextual cargado desde {filepath}")
                return True
        except Exception as e:
            print(f"❌ Error cargando índice contextual: {e}")
        return False