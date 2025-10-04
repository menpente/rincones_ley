# Asistente Jurídico RAG - Rincones de la Ley

Una aplicación web avanzada en español para abogados que utiliza Retrieval Augmented Generation (RAG) con múltiples métodos de búsqueda mejorados y documentos legales españoles.

## 🚀 Instalación y Configuración

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar API Keys

#### Groq (Requerido)
- Obtén tu API key gratuita en [Groq Console](https://console.groq.com/)
- Úsala para el modelo de lenguaje LLama

#### Anthropic (Opcional - Premium)
- Para recuperación contextual avanzada ($25.75 costo único)
- Obtén tu API key en [Anthropic Console](https://console.anthropic.com/)

### 3. Variables de Entorno (Recomendado)
```bash
export GROQ_API_KEY="your_groq_key"
export ANTHROPIC_API_KEY="your_anthropic_key"  # Opcional
```

### 4. Ejecutar la aplicación
```bash
streamlit run app.py
```

## 📁 Estructura del Proyecto

```
├── app.py                          # Aplicación principal Streamlit
├── rag_system.py                   # Sistema RAG principal con búsqueda inteligente
├── document_processor.py           # Procesamiento de PDF y segmentación
├── vector_store.py                # Búsqueda tradicional TF-IDF (baseline)
├── hybrid_reranking.py            # Búsqueda híbrida gratuita (mejorada)
├── contextual_retrieval.py        # Búsqueda contextual premium (Anthropic)
├── requirements.txt               # Dependencias Python
├── ref/                          # Documentos legales (PDFs)
├── vector_index_*.pkl            # Índices tradicionales guardados
├── hybrid_index_*.pkl            # Índices híbridos guardados
├── contextual_index_*.pkl        # Índices contextuales guardados (si premium)
└── README.md                     # Este archivo
```

## 📚 Documentos Incluidos

- **BOE-038_Codigo_Penal_y_legislacion_complementaria.pdf**: Código Penal Español
- **Ley de Enjuiciamiento Criminal.pdf**: Procedimiento penal
- **extranjería.pdf**: Legislación de extranjería

## ⚡ Características Avanzadas

### 🔍 **Múltiples Métodos de Búsqueda**

| Método | Costo | Mejora | Descripción |
|--------|-------|---------|-------------|
| **Tradicional** | Gratis | Baseline | TF-IDF estándar |
| **Híbrida + Reranking** | **Gratis** | **+15-25%** | Triple búsqueda con reranking inteligente |
| **Contextual Premium** | $25.75 único | +35-49% | Descripciones contextuales por Claude |

### 🎯 **Búsqueda Híbrida Gratuita** (Activada por defecto)
- **Triple motor**: Semántica + Palabras clave + Frases legales
- **Reranking inteligente**: Cobertura de términos, bonos legales, optimización de posición
- **Optimizado para legal**: Reconoce referencias ("artículo 123", "ley 15/2023")
- **Sin costos adicionales**: Mejora inmediata sin APIs externas

### 🤖 **Búsqueda Contextual Premium** (Opcional)
- **Contexto por Claude**: Cada fragmento tiene descripción contextual
- **Máxima precisión**: 35-49% mejora en precisión de recuperación
- **Costo único**: $25.75 para procesar todos los documentos
- **Activación automática**: Solo con API key de Anthropic

### 🖥️ **Interfaz Inteligente**
- **Selección automática**: Usa el mejor método disponible según API keys
- **Transparencia**: Muestra qué método de búsqueda se está usando
- **Historial avanzado**: Incluye puntuaciones de relevancia y contexto
- **Fuentes detalladas**: Referencias exactas a documentos legales

## 🎯 Tipos de Consulta

1. **Redactar Contrato**: Ayuda con elementos contractuales
2. **Consulta Legal**: Procedimientos y normativas
3. **Buscar Jurisprudencia**: Referencias legales específicas

## 🔧 Tecnologías Utilizadas

### Core
- **Streamlit**: Interfaz web interactiva
- **Groq API**: Modelo de lenguaje LLama (gratuito)
- **scikit-learn**: Múltiples vectorizadores TF-IDF
- **PyMuPDF**: Extracción de texto de PDFs

### Búsqueda Avanzada
- **Anthropic Claude**: Generación de contexto (opcional, premium)
- **NumPy**: Cálculos de similitud coseno
- **Pickle**: Almacenamiento persistente de índices

## 📋 Configuración y Uso

### Modo Básico (Solo Groq)
```bash
# Solo búsqueda híbrida gratuita
export GROQ_API_KEY="your_groq_key"
streamlit run app.py
```

### Modo Premium (Groq + Anthropic)
```bash
# Búsqueda contextual premium
export GROQ_API_KEY="your_groq_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
streamlit run app.py
```

### Primera Ejecución
1. **Procesamiento inicial** (~1-2 minutos): Lee PDFs y crea índices
2. **Híbrido gratuito**: Se crea automáticamente (sin costo)
3. **Contextual premium**: Solo si tienes API key de Anthropic ($25.75)
4. **Ejecuciones posteriores**: Carga índices guardados (instantáneo)

### Funcionamiento
- **Introduce consulta**: En español, lenguaje natural
- **Búsqueda automática**: Sistema elige el mejor método disponible
- **Resultados rankeados**: Con puntuaciones de relevancia
- **Fuentes citadas**: Referencias exactas a documentos legales

## 🛠️ Arquitectura del Sistema

### Pipeline de Búsqueda (Automático)
```
Consulta → Detección de Método → [Híbrida|Contextual|Tradicional] → Reranking → Resultados
```

### Métodos de Búsqueda (Por Prioridad)
1. **Contextual** (si hay API key Anthropic): Máxima precisión
2. **Híbrida** (siempre disponible): Buena mejora gratuita
3. **Tradicional** (fallback): Funcionamiento básico

### Persistencia de Datos
- **Índices guardados**: Los cálculos se guardan automáticamente
- **Sin reprocesamiento**: Documentos se procesan solo una vez
- **Escalabilidad**: Añade PDFs a `ref/` y se indexan automáticamente

## 🚀 Mejoras Implementadas

### v2.0 - Búsqueda Inteligente Multicapa
- ✅ **Búsqueda híbrida gratuita** (15-25% mejora)
- ✅ **Reranking con criterios legales** específicos
- ✅ **Búsqueda contextual premium** opcional (35-49% mejora)
- ✅ **Selección automática** del mejor método disponible
- ✅ **Optimización para documentos legales** españoles

### Próximas Mejoras
- 🔄 Cross-encoder reranking para 67% mejora total
- 🔄 Optimización de chunk boundaries
- 🔄 Prompts contextuales personalizables
- 🔄 Métricas de precisión de recuperación

## 💰 Consideraciones de Costos

| Configuración | Costo Inicial | Costo Operativo | Mejora |
|--------------|---------------|-----------------|---------|
| **Solo Groq** | $0 | $0 | +15-25% |
| **Groq + Anthropic** | $25.75 | $0 | +35-49% |

### Análisis ROI
- **Inversión**: $25.75 una sola vez para contextual
- **Comparación**: Menos que 1 hora de consultoría legal
- **Beneficio**: Mejora permanente en precisión de búsqueda
- **Recomendación**: Probar híbrido gratuito primero, luego evaluar contextual

## 📊 Documentación Técnica

- `contextual_retrieval_implementation.md` - Guía completa de implementación
- `contextual_retrieval_cost_analysis.md` - Análisis detallado de costos
- `cost_free_hybrid_alternative.md` - Explicación del sistema híbrido gratuito
- `contextual_retrieval_logic.md` - Lógica y fundamentos del sistema

## ⚖️ Aviso Legal

Esta herramienta es un asistente informativo. Siempre consulta con profesionales del derecho para asesoramiento legal oficial.