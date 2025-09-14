from groq import Groq
from typing import List, Dict
from vector_store import VectorStore
from document_processor import DocumentProcessor

class RAGSystem:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.vector_store = VectorStore()
        self.doc_processor = DocumentProcessor()
        
    def initialize(self):
        """Inicializa el sistema RAG cargando o creando el índice"""
        # Intentar cargar índice existente
        if not self.vector_store.load_index():
            print("Creando nuevo índice...")
            documents = self.doc_processor.process_documents()
            if documents:
                self.vector_store.build_index(documents)
                self.vector_store.save_index()
            else:
                print("No se encontraron documentos para procesar")
    
    def retrieve_context(self, query: str, k: int = 3) -> List[Dict]:
        """Recupera contexto relevante para la consulta"""
        return self.vector_store.search(query, k=k)
    
    def generate_prompt(self, query: str, context_docs: List[Dict]) -> str:
        """Genera el prompt para el modelo con contexto recuperado"""
        context_text = "\n\n".join([
            f"[Fuente: {doc['source']}]\n{doc['text']}"
            for doc in context_docs
        ])
        
        prompt = f"""Eres un asistente jurídico especializado en derecho español. Responde de manera precisa y profesional basándote únicamente en la información proporcionada.

CONTEXTO LEGAL:
{context_text}

PREGUNTA: {query}

INSTRUCCIONES:
- Responde basándote únicamente en el contexto proporcionado
- Si la información no está en el contexto, indícalo claramente
- Cita las fuentes relevantes en tu respuesta
- Usa terminología jurídica española apropiada
- Estructura tu respuesta de manera clara y profesional

RESPUESTA:"""
        
        return prompt
    
    def query(self, question: str, model: str = "llama-3.1-70b-versatile") -> Dict:
        """Procesa una consulta usando RAG"""
        try:
            # Recuperar contexto relevante
            context_docs = self.retrieve_context(question)
            
            if not context_docs:
                return {
                    "answer": "No se encontró información relevante en los documentos disponibles.",
                    "sources": [],
                    "context_used": False
                }
            
            # Generar prompt con contexto
            prompt = self.generate_prompt(question, context_docs)
            
            # Consultar al modelo
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente jurídico especializado en derecho español."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "sources": [doc['source'] for doc in context_docs],
                "context_used": True,
                "context_docs": context_docs
            }
            
        except Exception as e:
            return {
                "answer": f"Error procesando la consulta: {str(e)}",
                "sources": [],
                "context_used": False
            }
    
    def get_available_models(self):
        """Obtiene lista de modelos disponibles en Groq"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if 'llama' in model.id.lower()]
        except:
            return ["llama-3.1-70b-versatile", "llama-3.1-8b-instant"]