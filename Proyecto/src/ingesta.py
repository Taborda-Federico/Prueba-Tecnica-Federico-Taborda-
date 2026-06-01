from huggingface_hub import list_jobs
from parser import documentFactory
from langchain_core.prompts import  ChatPromptTemplate, LLMChain 
from langchain_openai import ChatOpenAI
import os
from getpass import getpass
from langchain_core.documents import Document
api_key = os.getenv('OPENAI_API_KEY')
def extractionDir(doc):

    factory = documentFactory()
    
    listDocs = []
    for currentExten in  os.listdir(doc) : ## Itero sobre el directorio ./docs 
            complPath = os.path.join(doc,currentExten) 
            _, extension =  os.path.splitext(currentExten)
            try:
                parserTool= factory.get_Parser(extension)
                texto = parserTool.parse(complPath)

                nuevo_doc = Document(
                    page_content=texto, 
                    metadata={"source": currentExten}
                )
                listDocs.append(nuevo_doc)
            except ValueError as e: 
                print(f"Saltando archivo: {e}")
    return listDocs

def cleanText(listdoc):
   
## System : quien sera nuestra ia y human es lo que le pediremos en lenguaje natural
    promt = ChatPromptTemplate.from_messages(
         
        [ (
            "system", "Eres un experto en limpieza de datos técnicos. Tu tarea es normalizar el texto: quita números de página, "
            "corrige palabras cortadas por guiones y elimina ruido visual."
            "Mantén exactos todos los códigos de error (ej: ERR-001) y nombres de servicios."
            " Elimina pies de página, números de página y ruidos de conversión."
            " Si el texto menciona una solución paso a paso, asegúrate de que se mantenga el orden."
            " No resumas, solo limpia y mejora la claridad."

            
         ),
         (
              "human", "Por favor, limpia y optimiza el siguiente fragmento de documentación: {textoCrudo}"
         )]
    )
    try:
        llM = ChatOpenAI(model="gpt-4o-mini", temperature= 0)
        chain = promt | llM
        entradaBatch = [{'textoCrudo': doc.page_content} for doc in listdoc] #batch() espera recibir una lista de diccionarios
        responses = chain.batch(entradaBatch)
        for i, response in enumerate(responses):
            listdoc[i].page_content = response.content 
        return listdoc
    except Exception as e:
         print(f"Se produjo un error:{e}")
def split_text():
    """
        Aca se diviran los archivos grandes 
    """



def storeVec():
        """
            guardado de vectores
        """


def main():
      
    litsParse = extractionDir('./Docs')

    listClean
