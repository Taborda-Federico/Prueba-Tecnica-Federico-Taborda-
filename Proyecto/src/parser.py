##Voy a hacer un loader por cada extension 
from abc import ABC, abstractmethod
import fitz
import re
import json


class BaseParser(ABC):
    @abstractmethod
    def parse(self, filepath:str)->str:
        """
         Este metodo ser obligatorio para todas las clases derivadas 
        """
    pass

    def clean_text(self, text:str)->str:
        """
        Limpieza de textos 
        """
        text= re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'[\r\n\t]+', ' ', text)
        
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\*]', '', text)
        text = re.sub(r' +', ' ', text)
        text = text.lower()
        return text.strip()
    pass

class mdParser(BaseParser):
    def parse(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as archivo:
          contenido_md = archivo.read()
        return self.clean_text(contenido_md)
    
class txtParser(BaseParser):
    def parse(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as archivo:
          contenido_txt = archivo.read()
        return self.clean_text(contenido_txt)

class jsParser(BaseParser):
    def parse(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as archivo:
          contenido_js = json.load(archivo)

          software = contenido_js.get("software","Desconocido")
          modulo = contenido_js.get("modulo", "desconocido ")

          texto = f"Documentacion de {software}. Modulo : {modulo}.\n\n"
          for item in contenido_js.get("contenido", []):
              ##Voy a iterar sobre todo el json y reconstruirlo
              texto += f"---Error ID {item.get('id', '')}:{item.get('titulo', '')}---\n"
              texto += f"Categoria : {item.get('categoria', '')}.\n"
              texto += f"Mensaje de usuario : {item.get('mensaje_usuario', '')}.\n"
              causas = ", ".join(item.get('causas_posibles', []))
              texto += f"Causas posibles : {causas}\n\n"
              soluciones = ", ".join(item.get('solucion', []))
              texto += f"Soluciones recomendadas : {soluciones}\n\n"
              texto += f"Nivel de soporte requerido:{item.get('nivel_soporte', '')}"
    

        return self.clean_text(texto)
    
class pdfParser(BaseParser):
    def parse(self, filepath):

        doc = fitz.open(filepath)
        texto_completo = ""
        for numero_pagina, pagina in enumerate(doc):
            texto_pag = pagina.get_text("text")
            texto_completo += f"\n\n Inicio de pagina {numero_pagina +1}"
            texto_completo += texto_pag
            texto_completo += f"\n\n Fin de pagina {numero_pagina +1}"
        doc.close()
        texto = re.sub(r'\n(\d+\.\d+\s+.*?)(?=\n)', r'\n\n--- SECCIÓN: \1 ---\n', texto_completo)
        palabras_clave = r'(Posibles causas|Acciones recomendadas|Verificaciones básicas|Acción recomendada)'
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        texto = re.sub(r'(\w+)-\n(\w+)', r'\1\2', texto)
        texto = re.sub(r'\n{3,}', '\n\n', texto)

        return self.clean_text(texto)

class documentFactory:


    def __init__(self):
        self._parsers={
            '.md':mdParser(),
            '.txt':txtParser(),
            '.json':jsParser(),
            '.pdf' : pdfParser()
        }
    def get_Parser(self, fileExtension:str) ->BaseParser:
        parser = self._parsers.get(fileExtension.lower())
        if not parser:
            raise ValueError(f"No hay parser configurado para la extension: {fileExtension}")
        return parser