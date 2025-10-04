from groq import Groq
from typing import List, Dict, Optional
from vector_store import VectorStore
from document_processor import DocumentProcessor
from contextual_retrieval import ContextualRetrieval
from hybrid_reranking import HybridReranker
import os

class RAGSystem:
    def __init__(self, groq_api_key: str, anthropic_api_key: Optional[str] = None, use_hybrid_reranking: bool = True):
        self.client = Groq(api_key=groq_api_key)
        self.vector_store = VectorStore()
        self.doc_processor = DocumentProcessor()
        self.contextual_retrieval = ContextualRetrieval(anthropic_api_key) if anthropic_api_key else None
        self.hybrid_reranker = HybridReranker() if use_hybrid_reranking else None
        self.system_prompt = self._load_system_prompt()
        self.use_contextual_retrieval = anthropic_api_key is not None
        self.use_hybrid_reranking = use_hybrid_reranking
        
    def initialize(self):
        """Inicializa el sistema RAG cargando o creando el índice"""
        try:
            print("🔄 Iniciando sistema RAG...")

            # Verificar que existe la carpeta de documentos
            ref_folder = "ref"
            if not os.path.exists(ref_folder):
                print(f"❌ Carpeta {ref_folder} no existe")
                raise Exception(f"Carpeta {ref_folder} no encontrada")

            pdf_files = [f for f in os.listdir(ref_folder) if f.lower().endswith('.pdf')]
            print(f"📄 PDFs encontrados: {pdf_files}")

            # Intentar cargar índices existentes
            traditional_loaded = self.vector_store.load_index()
            contextual_loaded = False
            hybrid_loaded = False

            if self.use_contextual_retrieval:
                contextual_loaded = self.contextual_retrieval.load_contextual_index()

            if self.use_hybrid_reranking:
                hybrid_loaded = self.hybrid_reranker.load_hybrid_index()

            # Check if we need to rebuild any indexes
            need_rebuild = (not traditional_loaded or
                          (self.use_contextual_retrieval and not contextual_loaded) or
                          (self.use_hybrid_reranking and not hybrid_loaded))

            if need_rebuild:
                print("🔨 Creando nuevos índices...")
                documents, whole_documents = self.doc_processor.process_documents()
                print(f"📚 Documentos procesados: {len(documents)}")

                if documents:
                    # Mostrar una muestra del primer documento
                    if len(documents) > 0:
                        print(f"📝 Muestra del primer documento: {documents[0]['text'][:100]}...")

                    # Construir índice tradicional
                    if not traditional_loaded:
                        self.vector_store.build_index(documents)
                        self.vector_store.save_index()
                        print("✅ Índice tradicional creado y guardado")

                    # Construir índice híbrido (gratuito)
                    if self.use_hybrid_reranking and not hybrid_loaded:
                        print("🔄 Generando índice híbrido con reranking...")
                        self.hybrid_reranker.build_hybrid_index(documents)
                        self.hybrid_reranker.save_hybrid_index()
                        print("✅ Índice híbrido creado y guardado")

                    # Construir índice contextual si está habilitado (costo adicional)
                    if self.use_contextual_retrieval and not contextual_loaded:
                        print("🤖 Generando índice contextual...")
                        contextual_chunks = self.contextual_retrieval.create_contextual_chunks(
                            documents, whole_documents
                        )
                        self.contextual_retrieval.build_contextual_index(contextual_chunks)
                        self.contextual_retrieval.save_contextual_index()
                        print("✅ Índice contextual creado y guardado")

                else:
                    print("❌ No se encontraron documentos para procesar")
                    raise Exception("No se pudieron procesar los documentos PDF. Verifique que PyMuPDF esté instalado.")
            else:
                print("✅ Índice tradicional cargado correctamente")
                print(f"📊 Documentos en índice: {len(self.vector_store.documents)}")

                if self.use_hybrid_reranking and hybrid_loaded:
                    print("✅ Índice híbrido cargado correctamente")
                    print(f"🔄 Documentos híbridos: {len(self.hybrid_reranker.documents)}")

                if self.use_contextual_retrieval and contextual_loaded:
                    print("✅ Índice contextual cargado correctamente")
                    print(f"🤖 Documentos contextuales: {len(self.contextual_retrieval.contextual_documents)}")

        except Exception as e:
            print(f"❌ Error en inicialización RAG: {e}")
            import traceback
            traceback.print_exc()
            raise e

    def _load_system_prompt(self) -> str:
        """Carga el prompt del sistema desde archivo markdown"""
        try:
            prompt_file = "system_prompt.md"
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract only the main content, removing markdown headers
                    lines = content.split('\n')
                    # Skip title and take content after first paragraph
                    content_lines = []
                    skip_headers = True
                    for line in lines:
                        if line.strip() and not line.startswith('#') and skip_headers:
                            skip_headers = False
                        if not skip_headers and not line.startswith('#'):
                            content_lines.append(line)
                    return '\n'.join(content_lines).strip()
            else:
                print(f"⚠️ Archivo {prompt_file} no encontrado, usando prompt por defecto")
                return "Eres un asistente jurídico especializado en derecho español. Responde de manera precisa y profesional basándote únicamente en la información proporcionada."
        except Exception as e:
            print(f"❌ Error cargando prompt del sistema: {e}")
            return "Eres un asistente jurídico especializado en derecho español. Responde de manera precisa y profesional basándote únicamente en la información proporcionada."

    def retrieve_context(self, query: str, k: int = 3) -> List[Dict]:
        """Recupera contexto relevante usando el mejor método disponible"""

        # Priority: Contextual > Hybrid Reranking > Traditional
        if self.use_contextual_retrieval and self.contextual_retrieval.contextual_documents:
            # Contextual retrieval (paid, highest accuracy)
            traditional_results = self.vector_store.search(query, k=k*2)
            hybrid_results = self.contextual_retrieval.hybrid_search(
                query, traditional_results, k=k, alpha=0.7
            )
            print(f"🤖 Usando búsqueda contextual (premium)")
            return hybrid_results

        elif self.use_hybrid_reranking and self.hybrid_reranker.documents:
            # Hybrid reranking (free, good improvement)
            hybrid_results = self.hybrid_reranker.enhanced_search(query, k=k)
            print(f"🔄 Usando búsqueda híbrida con reranking (gratuito)")
            return hybrid_results

        else:
            # Traditional search (baseline)
            traditional_results = self.vector_store.search(query, k=k)
            print(f"🔍 Usando búsqueda tradicional (baseline)")
            return traditional_results
    
    def generate_prompt(self, query: str, context_docs: List[Dict]) -> str:
        """Genera el prompt para el modelo con contexto recuperado"""
        context_text = "\n\n".join([
            f"[Fuente: {doc['source']}]\n{doc['text']}"
            for doc in context_docs
        ])

        prompt = f"""CONTEXTO LEGAL:
{context_text}

PREGUNTA: {query}

RESPUESTA:"""

        return prompt
    
    def query(self, question: str, model: str = "llama-3.3-70b-versatile") -> Dict:
        """Procesa una consulta usando RAG"""
        try:
            print(f"🔍 Procesando consulta: {question}")

            # Verificar que el sistema esté inicializado
            if not self.vector_store.documents:
                print("❌ No hay documentos cargados en el vector store")
                return {
                    "answer": "Sistema no inicializado correctamente. No hay documentos disponibles para consulta.",
                    "sources": [],
                    "context_used": False
                }

            print(f"📊 Documentos disponibles en vector store: {len(self.vector_store.documents)}")

            # Recuperar contexto relevante
            context_docs = self.retrieve_context(question)
            print(f"🎯 Documentos relevantes encontrados: {len(context_docs)}")

            if not context_docs:
                print("❌ No se encontraron documentos relevantes")
                return {
                    "answer": "No se encontró información relevante en los documentos disponibles.",
                    "sources": [],
                    "context_used": False
                }

            # Mostrar información de los documentos encontrados
            for i, doc in enumerate(context_docs):
                score = doc.get('similarity_score', 0)
                print(f"📄 Doc {i+1}: {doc['source']} (score: {score:.3f})")
            
            # Generar prompt con contexto
            print("🤖 Generando prompt con contexto...")
            prompt = self.generate_prompt(question, context_docs)
            print(f"📝 Longitud del prompt: {len(prompt)} caracteres")

            # Consultar al modelo
            print(f"🌐 Realizando llamada a Groq API con modelo: {model}")
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": self.system_prompt
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1500
                )
                print("✅ Respuesta recibida de Groq API")

                answer = response.choices[0].message.content
                print(f"📄 Longitud de la respuesta: {len(answer)} caracteres")

            except Exception as api_error:
                print(f"❌ Error en llamada a Groq API: {api_error}")
                print(f"❌ Tipo de error: {type(api_error).__name__}")
                import traceback
                traceback.print_exc()
                raise api_error
            
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
            return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
