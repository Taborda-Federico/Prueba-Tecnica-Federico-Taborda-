from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel, EmailStr, Field

from ingesta import main as ejecutar_ingesta
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from contextlib import asynccontextmanager
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
import os

embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db=None
@asynccontextmanager
async def lifespan(app:FastAPI):
    global db
    ruta_db ="./chroma_db"
    if not os.path.exists(ruta_db)or not os.listdir(ruta_db):
        print("No se encontro base de datos. creendo una ...")
        ejecutar_ingesta()
    else:
        print("Exite una base de datos")
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db= Chroma(
        persist_directory =ruta_db,
        embedding_function= embeddings_model
    )
    print("Base de datos conectada")
    yield
    print("Apagando Api ")

app = FastAPI(lifespan=lifespan)
class BasePregunta(BaseModel):
    pregunta:str = Field(
        min_length=1,
        max_length= 500,
        description= "Consulta tecnica del usuario sobre el siestema "
    )

def promtFuction(context:str, pregutna:str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "Eres el Ingeniero de Soporte de MineCatalog. Tu misión es ayudar al usuario "
            "resolviendo sus dudas técnicas basándote en la documentación proporcionada.\n\n"
            "INSTRUCCIONES:\n"
            "1. Analiza el CONTEXTO y responde a la intención del usuario de forma útil.\n"
            "2. Puedes parafrasear y explicar los pasos con tus propias palabras siempre que "
            "la base de la solución esté en el contexto.\n"
            "3. Si el contexto NO contiene información relacionada con la pregunta, "
            "amablemente indica que no tienes esa información específica y sugiere contactar a soporte.\n"
            "4. Sé profesional y directo."
        )),
        ("user", "DOCUMENTACIÓN DE REFERENCIA:\n{contexto}\n\n---\nPREGUNTA DEL USUARIO: {pregunta}")
    ])
    
    try:
        llm= ChatOpenAI(model="gpt-4o", temperature=0)
        chain = prompt | llm
        entradas = {'contexto':context, "pregunta": pregutna}
        response = chain.invoke(entradas) 
        return response.content
    except Exception as e:
        print(e)
    
   
    try:
            llm_local=ChatOllama(model="llama3", temperature=0)
            chain_local= prompt | llm_local
    
            response = chain_local.invoke({'contexto':context, "pregunta": pregutna}) 
            return response
    
    except Exception as e:
        print(e)
        return response
        
@app.post("/preguntar")
def nuevaPregunta(playload: BasePregunta):
            
    try:    
      


        
        docs =db.similarity_search(playload.pregunta, k=3)
  
        if not docs:
            return {
                'Mensaje Error': "No exiten respuestas hacia tu pregunta por favor "
            }
        contexto_unido = "\n\n".join([doc.page_content for doc in docs])
        fuentes = list(set([doc.metadata.get('source') for doc in docs]))
        respuesta = promtFuction(contexto_unido,playload.pregunta )
   
        return {
            'chunks similares' : respuesta,
            'fuentes':fuentes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))