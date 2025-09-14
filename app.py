import streamlit as st
import os
from rag_system import RAGSystem

# Configuración de la página
st.set_page_config(
    page_title="Asistente Jurídico - Rincones de la Ley",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
    }
    .source-box {
        background-color: #fef3c7;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .answer-box {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Inicializa las variables de sesión"""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def setup_sidebar():
    """Configura la barra lateral"""
    with st.sidebar:
        st.header("⚖️ Configuración")

        # Check for environment variable first
        env_api_key = os.environ.get("GROQ_API_KEY")

        if env_api_key:
            # Use environment variable and hide input
            groq_api_key = env_api_key
            st.success("✅ API Key configurada desde variables de entorno")
        else:
            # API Key input for local development
            groq_api_key = st.text_input(
                "Clave API de Groq:",
                type="password",
                help="Ingresa tu clave API de Groq para usar el servicio"
            )
        
        if groq_api_key and (not st.session_state.rag_system or 
                           st.session_state.get('current_api_key') != groq_api_key):
            with st.spinner("Inicializando sistema RAG..."):
                try:
                    st.session_state.rag_system = RAGSystem(groq_api_key)
                    st.session_state.rag_system.initialize()
                    st.session_state.current_api_key = groq_api_key
                    st.success("Sistema inicializado correctamente")
                except Exception as e:
                    st.error(f"Error inicializando: {str(e)}")
                    st.session_state.rag_system = None
        
        # Información de documentos
        st.subheader("📚 Documentos Cargados")
        ref_folder = "ref"
        if os.path.exists(ref_folder):
            pdf_files = [f for f in os.listdir(ref_folder) if f.lower().endswith('.pdf')]
            for pdf_file in pdf_files:
                st.text(f"• {pdf_file}")
        else:
            st.warning("Carpeta 'ref' no encontrada")
        
        # Limpiar historial
        if st.button("🗑️ Limpiar Historial"):
            st.session_state.chat_history = []
            st.rerun()

def main():
    """Función principal de la aplicación"""
    initialize_session_state()
    setup_sidebar()
    
    # Título principal
    st.markdown('<h1 class="main-header">⚖️ Asistente Jurídico</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #64748b; font-size: 1.2rem;">Consulta inteligente de documentos legales españoles</p>', unsafe_allow_html=True)
    
    # Verificar si el sistema está listo
    if not st.session_state.rag_system:
        st.warning("⚠️ Ingresa tu clave API de Groq en la barra lateral para comenzar.")
        return
    
    # Tipos de consulta predefinidos
    st.subheader("🎯 Consultas Rápidas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Redactar Contrato", use_container_width=True):
            st.session_state.quick_query = "¿Qué elementos debe contener un contrato válido según la legislación española?"
    
    with col2:
        if st.button("🔍 Consulta Legal", use_container_width=True):
            st.session_state.quick_query = "Explícame los procedimientos legales relacionados con"
    
    with col3:
        if st.button("📖 Buscar Jurisprudencia", use_container_width=True):
            st.session_state.quick_query = "¿Qué dice la ley sobre"
    
    # Campo de consulta
    query_text = st.text_area(
        "💬 Tu consulta legal:",
        value=st.session_state.get('quick_query', ''),
        height=100,
        placeholder="Ejemplo: ¿Cuáles son los plazos de prescripción en derecho penal español?"
    )
    
    # Limpiar quick_query después de usarla
    if 'quick_query' in st.session_state:
        del st.session_state.quick_query
    
    # Botón de consulta
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Consultar", type="primary", use_container_width=True):
            if query_text.strip():
                process_query(query_text)
            else:
                st.warning("Por favor, ingresa una consulta.")
    
    # Mostrar historial de chat
    display_chat_history()

def process_query(query: str):
    """Procesa una consulta y muestra los resultados"""
    with st.spinner("🔍 Buscando información relevante..."):
        try:
            result = st.session_state.rag_system.query(query)
            
            # Agregar al historial
            st.session_state.chat_history.append({
                "query": query,
                "result": result
            })
            
        except Exception as e:
            st.error(f"Error procesando la consulta: {str(e)}")

def display_chat_history():
    """Muestra el historial de consultas y respuestas"""
    if not st.session_state.chat_history:
        return
    
    st.subheader("💬 Historial de Consultas")
    
    # Mostrar las consultas más recientes primero
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.expander(f"Consulta {len(st.session_state.chat_history) - i}: {chat['query'][:60]}..."):
            
            # Mostrar la pregunta
            st.markdown(f'<div class="query-box"><strong>Pregunta:</strong> {chat["query"]}</div>', 
                       unsafe_allow_html=True)
            
            result = chat["result"]
            
            # Mostrar fuentes si están disponibles
            if result.get("sources"):
                st.markdown("**📚 Fuentes consultadas:**")
                for source in result["sources"]:
                    st.markdown(f'<div class="source-box">• {source}</div>', 
                               unsafe_allow_html=True)
            
            # Mostrar la respuesta
            st.markdown(f'<div class="answer-box">{result["answer"]}</div>', 
                       unsafe_allow_html=True)
            
            # Mostrar contexto usado (opcional, para debug)
            if st.checkbox(f"Mostrar contexto usado - Consulta {len(st.session_state.chat_history) - i}", key=f"context_{i}"):
                if result.get("context_docs"):
                    st.subheader("🔍 Fragmentos de texto utilizados:")
                    for j, doc in enumerate(result["context_docs"]):
                        with st.expander(f"Fragmento {j+1} - {doc['source']}"):
                            st.text(doc["text"][:500] + "..." if len(doc["text"]) > 500 else doc["text"])

if __name__ == "__main__":
    main()