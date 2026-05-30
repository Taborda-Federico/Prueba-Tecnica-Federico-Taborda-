##Voy a hacer un loader por cada extension 
from abc import ABC, abstractmethod
import strip_markdown 
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
        text =re.sub(r'\n+', '\n',text)
        
        text =re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\n]', '',text)
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
        return super().parser(filepath)


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