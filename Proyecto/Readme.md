# Prueba Técnica - Federico Julián Taborda (Implementac+on 2)
**Este repositorio contiene la resolución de la prueba técnica para el rol de Machine Learning. El proyecto implementa un asistente automatizado capaz de responder preguntas de soporte utilizando documentación técnica interna, backend en Python(FastAPI + LangChain).**
#### Aclaraciòn
**Acalaro que esta es una segunda implementacion donde la respuesta del backend es la repuesta definiva para el chatbot, diferente a la implemntaciòn (main) donde la respuesta de la api definida es simplemente los chunks similares a la pregunta, luego simplemte se agrega un nodo mas en n8n donde se agrega un nodo de OpenAI para que devuelva una respuesta segun la documentaciòn similar**

## Backend
En el bakcend tenemos tres Archvio:
### Ingesta.py
**Creacìon de Chromadb, con Api OpenAI (si exite api key) y llm ollama (en caso de no existir)**
### main.py
**Definiciòn de la appi conectada a n8n**
### parser.py 
**Parseo de documentacion, de diferente Extenciòn**

## Requisitos Previos

Asegúrese de tener instalados los siguientes componentes antes de ejecutar el proyecto:

-Python 3.10+

-n8n (Ejecutándose de manera local).

#### En caso de no tener OpenIA KEY
-Ollama (Para el modelo local de contingencia).

    Una vez instalado Ollama, abra una terminal y ejecute: ollama run llama3 para descargar el modelo necesario.


## Insatalaciòn y Configuraciòn 
```bash
        git clone https://github.com/Taborda-Federico/Prueba-Tecnica-Federico-Taborda-.git
        cd proyecto 
```
```bash
        python -m venv venv
        source venv/bin/activate 
         # En Windows use: venv\Scripts\activate
```
```bash
    pip install -r requirements.txt
```

``` bash
    cp .env.example .env
    #### copiar su OpenIa Key 
```
### importar Json de workFlow en n8n
**Con openAI Key usar Federico_Taborda_workFlow_IM2.json**
**Sin openAI Key usar Federico_llm_local.json**
## Levantamiento y ejecucion 

**Correr en bash el siguiente Codigo**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
## Desde src 
```
Esperar que se cree la Chromadb y dirigirse a n8n:
    -Abrir chat y preguntar por ejemplo:
        ¿Cómo resuelvo el error ERR-001?"

esperar respuesta..

## 🔄 Flujo del Sistema

```
Documentos (.md, .txt, .json, .pdf)
    ↓
Parser (clean_text)
    ↓
LLM (limpieza con OpenAI/Ollama)
    ↓
Text Splitter (chunks de 900 tokens)
    ↓
Embeddings (HuggingFace all-MiniLM-L6-v2)
    ↓
ChromaDB (almacenamiento vectorial)
    ↓
Consulta → Similarity Search → LLM → Respuesta
```

## Stack Tecnológico

- **FastAPI** - Framework web
- **LangChain** - Orquestación LLM
- **ChromaDB** - Base de datos vectorial
- **HuggingFace** - Embeddings locales
- **OpenAI / Ollama** - Modelos LLM
- **PyPDF2 / python-docx** - Parseo de documentos

## Notas

- Si no tienes OpenAI KEY, el sistema usa automáticamente Ollama
- Los embeddings se calculan localmente con HuggingFace
- La limpieza de texto es crítica para la calidad de respuestas