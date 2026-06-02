from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel, EmailStr, Field
from ingesta import main
from ingesta import main as ejecutar_ingesta
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from contextlib import asynccontextmanager
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

@app.post("/preguntar")
def nuevaPregunta(playload: BasePregunta):
    		
    try:    
      


        
        docs =db.similarity_search(playload.pregunta, k=3)

        if not docs:
            return {
                'Mensaje Error': "No exiten respuestas hacia tu pregunta por favor "
            }
        return {
            'chunks similares' : [doc.page_content for doc in docs],
            'fuentes':[doc.metadata.get('source') for doc in docs]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))