# Plan de Desarrollo - Aplicación RAG para Abogados Españoles

## Arquitectura del Sistema

### Componentes Principales
1. **Procesamiento de Documentos**: Extracción de texto de PDFs en carpeta `ref/`
2. **Almacenamiento Vectorial**: FAISS para almacenamiento local de vectores (simple, sin dependencias externas)
3. **Pipeline RAG**: Recuperación de fragmentos relevantes + generación con LLM Groq
4. **Interfaz en Español**: Interfaz Streamlit en español para abogados

### Estructura de la Aplicación
```
├── app.py                 # Aplicación principal Streamlit
├── document_processor.py  # Procesamiento de PDF y segmentación
├── vector_store.py       # Operaciones vectoriales FAISS
├── rag_system.py         # Pipeline RAG con Groq
├── requirements.txt      # Dependencias
└── ref/                  # Documentos legales
```

### Funcionalidades Clave
- Carga/procesamiento de documentos desde carpeta `ref/`
- Interfaz en español con terminología legal
- Tipos de consulta: "Redactar contrato", "Consulta legal", "Buscar jurisprudencia"
- Citación de documentos en respuestas
- Barra lateral simple para gestión de documentos

### Stack Tecnológico
- **Streamlit** (Interfaz de usuario)
- **Groq** (Modelo de lenguaje)
- **FAISS** (Base de datos vectorial)
- **PyMuPDF** (Procesamiento de PDF)
- **sentence-transformers** (Embeddings)

## Documentos Disponibles
- BOE-038_Codigo_Penal_y_legislacion_complementaria.pdf
- Ley de Enjuiciamiento Criminal.pdf
- extranjería.pdf

## Estimación de Complejidad
- Aplicación total: 200-300 líneas de código
- Diseño simple y funcional para abogados españoles
- Sin dependencias externas complejas
- Enfoque en simplicidad y usabilidad

## Próximos Pasos
1. Crear archivo principal de Streamlit
2. Implementar procesamiento de documentos y almacenamiento vectorial
3. Crear sistema RAG con integración Groq
4. Añadir interfaz en español y características específicas para abogados
5. Crear requirements.txt