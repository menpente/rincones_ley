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
        color: #1f2937;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
    }
    .source-box {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .answer-box {
        background-color: #ffffff;
        color: #1f2937;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
    }
    .answer-preview {
        background-color: #ffffff;
        color: #1f2937;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
        line-height: 1.6;
    }
    .read-more-btn {
        background-color: #3b82f6;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .read-more-btn:hover {
        background-color: #2563eb;
    }
    /* Ensure all text elements have proper contrast */
    .stMarkdown, .stText {
        color: #1f2937 !important;
    }
    /* Fix any potential dark mode conflicts */
    div[data-testid="stMarkdownContainer"] p {
        color: #1f2937 !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Inicializa las variables de sesión"""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def create_answer_preview(answer_text: str, max_length: int = 180) -> tuple[str, bool]:
    """
    Crea un preview del texto de respuesta.
    Retorna (preview_text, is_truncated)
    """
    if len(answer_text) <= max_length:
        return answer_text, False

    # Buscar el último espacio antes del límite para no cortar palabras
    truncate_pos = answer_text.rfind(' ', 0, max_length)
    if truncate_pos == -1:  # No se encontró espacio, cortar en el límite
        truncate_pos = max_length

    preview = answer_text[:truncate_pos].rstrip()
    return f"{preview}...", True

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
    """Muestra el historial de consultas y respuestas con progressive disclosure"""
    if not st.session_state.chat_history:
        return

    st.subheader("💬 Historial de Consultas")

    # Mostrar las consultas más recientes primero
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        chat_index = len(st.session_state.chat_history) - i

        # Contenedor principal para cada consulta
        st.markdown("---")

        # Mostrar la pregunta
        st.markdown(f'<div class="query-box"><strong>Consulta {chat_index}:</strong> {chat["query"]}</div>',
                   unsafe_allow_html=True)

        result = chat["result"]
        answer_text = result["answer"]

        # Crear preview de la respuesta
        preview_text, is_truncated = create_answer_preview(answer_text)

        # Mostrar fuentes si están disponibles
        if result.get("sources"):
            st.markdown("**📚 Fuentes consultadas:**")
            for source in result["sources"]:
                st.markdown(f'<div class="source-box">• {source}</div>',
                           unsafe_allow_html=True)

        # Mostrar preview de la respuesta
        st.markdown(f'<div class="answer-preview">{preview_text}</div>',
                   unsafe_allow_html=True)

        # Si la respuesta está truncada, mostrar botón "Leer más"
        if is_truncated:
            if st.button(f"📖 Leer respuesta completa", key=f"expand_{chat_index}"):
                # Mostrar respuesta completa
                st.markdown(f'<div class="answer-box">{answer_text}</div>',
                           unsafe_allow_html=True)

        # Mostrar contexto usado (opcional, para debug)
        if st.checkbox(f"🔍 Mostrar contexto utilizado", key=f"context_{i}"):
            if result.get("context_docs"):
                st.subheader("📄 Fragmentos de texto utilizados:")
                for j, doc in enumerate(result["context_docs"]):
                    with st.expander(f"Fragmento {j+1} - {doc['source']}"):
                        st.text(doc["text"][:500] + "..." if len(doc["text"]) > 500 else doc["text"])

if __name__ == "__main__":
    main()