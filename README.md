# Asistente Jurídico RAG - Rincones de la Ley

Una aplicación web en español para abogados que utiliza Retrieval Augmented Generation (RAG) con documentos legales españoles.

## 🚀 Instalación y Configuración

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar API Key de Groq
- Obtén tu API key gratuita en [Groq Console](https://console.groq.com/)
- La introducirás en la aplicación web cuando la ejecutes

### 3. Ejecutar la aplicación
```bash
streamlit run app.py
```

## 📁 Estructura del Proyecto

```
├── app.py                 # Aplicación principal Streamlit
├── document_processor.py  # Procesamiento de PDF y segmentación
├── vector_store.py       # Almacenamiento vectorial con FAISS
├── rag_system.py         # Sistema RAG con Groq
├── requirements.txt      # Dependencias
├── ref/                  # Documentos legales (PDFs)
└── README.md            # Este archivo
```

## 📚 Documentos Incluidos

- **BOE-038_Codigo_Penal_y_legislacion_complementaria.pdf**: Código Penal Español
- **Ley de Enjuiciamiento Criminal.pdf**: Procedimiento penal
- **extranjería.pdf**: Legislación de extranjería

## ⚡ Características

- **Interfaz en Español**: Diseñada específicamente para abogados españoles
- **RAG Inteligente**: Busca información relevante en los documentos legales
- **Consultas Rápidas**: Botones para tipos comunes de consultas legales
- **Citación de Fuentes**: Muestra qué documentos se utilizaron en cada respuesta
- **Historial de Chat**: Mantiene un registro de consultas anteriores
- **Almacenamiento Local**: Utiliza FAISS para búsqueda vectorial rápida

## 🎯 Tipos de Consulta

1. **Redactar Contrato**: Ayuda con elementos contractuales
2. **Consulta Legal**: Procedimientos y normativas
3. **Buscar Jurisprudencia**: Referencias legales específicas

## 🔧 Tecnologías Utilizadas

- **Streamlit**: Interfaz web
- **Groq**: Modelo de lenguaje (LLama)
- **scikit-learn**: TF-IDF para búsqueda vectorial
- **PyMuPDF**: Extracción de texto de PDFs

## 📋 Uso

1. Ejecuta `streamlit run app.py`
2. Introduce tu API key de Groq en la barra lateral
3. Espera a que se indexen los documentos (primera vez)
4. Haz consultas legales en español
5. Revisa las fuentes citadas en cada respuesta

## 🛠️ Desarrollo

El sistema procesa automáticamente todos los PDFs en la carpeta `ref/` y crea un índice TF-IDF optimizado para búsqueda rápida en español. No requiere modelos pesados de embeddings neuronales.

## ⚖️ Aviso Legal

Esta herramienta es un asistente informativo. Siempre consulta con profesionales del derecho para asesoramiento legal oficial.