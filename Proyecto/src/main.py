from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
from ingesta import main
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

app=FastAPI()
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db = Chroma(
    persist_directory="./chroma_db",
    embedding_function = embeddings_model
)
class BasePregunta(BaseModel):
    pregunta:str = Field(
        min_length=1,
        max_length= 500,
        description= "Consulta tecnica del usuario sobre el siestema "
    )

@app.post("api/buscar")
def nuevaPregunta(pregunta: BasePregunta):
    		
    try:    
      


        
        docs =db.similarity_search(pregunta.pergunta, k=3)

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