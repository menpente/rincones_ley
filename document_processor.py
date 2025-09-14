try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ PyMuPDF no está instalado. Instálelo con: pip install PyMuPDF")
    fitz = None

import os
from typing import List, Dict
import re

class DocumentProcessor:
    def __init__(self, ref_folder: str = "ref"):
        self.ref_folder = ref_folder
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrae texto de un archivo PDF"""
        if fitz is None:
            raise ImportError("PyMuPDF no está disponible. Instálelo para procesar PDFs.")

        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"Error procesando {pdf_path}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Limpia y normaliza el texto extraído"""
        # Eliminar saltos de línea múltiples
        text = re.sub(r'\n+', '\n', text)
        # Eliminar espacios múltiples
        text = re.sub(r' +', ' ', text)
        # Eliminar caracteres especiales problemáticos
        text = text.replace('\x00', '')
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Divide el texto en fragmentos con solapamiento"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Buscar un punto de corte natural (punto, salto de línea)
            if end < len(text):
                # Buscar hacia atrás por un punto seguido de espacio o salto de línea
                for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                    if text[i] in '.!?\n' and i + 1 < len(text) and text[i + 1] in ' \n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
        return chunks
    
    def process_documents(self) -> List[Dict[str, str]]:
        """Procesa todos los documentos PDF en la carpeta ref"""
        documents = []
        
        if not os.path.exists(self.ref_folder):
            return documents
        
        for filename in os.listdir(self.ref_folder):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(self.ref_folder, filename)
                print(f"Procesando: {filename}")
                
                text = self.extract_text_from_pdf(pdf_path)
                if text:
                    cleaned_text = self.clean_text(text)
                    chunks = self.chunk_text(cleaned_text)
                    
                    for i, chunk in enumerate(chunks):
                        documents.append({
                            'filename': filename,
                            'chunk_id': i,
                            'text': chunk,
                            'source': f"{filename} (fragmento {i+1})"
                        })
        
        print(f"Total de fragmentos procesados: {len(documents)}")
        return documents