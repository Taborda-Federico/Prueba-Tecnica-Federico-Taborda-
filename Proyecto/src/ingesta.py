
from parser import documentFactory
from langchain_core.prompts import  ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
##from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
load_dotenv()
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
   
	print("Texto parseado, pasamos a la fase de limpieza")
	## System : quien sera nuestra ia y human es lo que le pediremos en lenguaje natural
	prompt = ChatPromptTemplate.from_messages(
		 
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
		chain = prompt | llM
		entradaBatch = [{'textoCrudo': doc.page_content} for doc in listdoc] #batch() espera recibir una lista de diccionarios
		responses = chain.batch(entradaBatch)
		for i, response in enumerate(responses):
			listdoc[i].page_content = response.content 
		return listdoc
	
	except Exception as e:
		print(f"OpenAI fallo, Error: {e}. Lanzamiento locar ..")
		
		
	try:
		llm_local=ChatOllama(model="llama3", temperature=0)
		chain_local= prompt | llm_local
	
		for doc in listdoc:
			res_local= chain_local.invoke({"textoCrudo": doc.page_content})
			doc.page_content = res_local.content
		print("LLM local funcionando, eliminando ruido localmente ")
	
		return listdoc
	except Exception as e_local:
		print(f"Todo falló. Usando texto original sin limpieza. Error local: {e_local}")
		return listdoc
def split_text(listText):
	"""
		Aca se diviran los archivos grandes, en chunks mas paqueños 
	"""
	text_splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=125)
	listChunks = []
	
	listChunks = text_splitter.split_documents(listText)
	

	return listChunks
class StoreVector:
	def __init__(self, db_directory:str = './chroma_db'):
		self.db_directory = db_directory
		self.embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
	def creastoreVec(self,listChunk:list):
			"""
					guardado de vectores
			""" 
			

			try:
			

					vectorstore = Chroma.from_documents(
						documents=listChunk,
						embedding=self.embeddings_model,
						persist_directory=self.db_directory
					)
			except Exception as e:
				print(f"Se produjo un error:{e}")


def main():
	  
	litsParse = extractionDir('../docs')

	listClean = cleanText(litsParse)

	listChunk = split_text(listClean)

	manager = StoreVector()
	
	manager.creastoreVec(listChunk)

	print('Creado correctamente chromaDB')

if __name__ == "__main__":
	main()