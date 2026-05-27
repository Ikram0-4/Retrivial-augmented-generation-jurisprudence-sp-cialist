from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from mistralai import Mistral
from main import *
import os

load_dotenv(dotenv_path=".env")

api_key = os.getenv('PINECONE_API_KEY')
if api_key is None:
    raise ValueError("PINECONE_API_KEY not found in environment variables")

pc = Pinecone(api_key=api_key)
index = connexionIndex()
if isinstance(index, dict) and "error" in index:
    print(index)

class Question(BaseModel):
    question: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API !"}


@app.post("/ask")
def ask_question(question: Question):
    print("Requête reçue:", question.question)
    input_question = question.question
    print("Encoding...")
    query_embedding = encodingQuerry(input_question)
    print("Recherche Pinecone...")
    contexte = resultatsQuerry(index, query_embedding)
    print("LLM...")
    if contexte == "Aucun contexte trouvé":
        return {"response": "Désolé, je n'ai trouvé aucune information pertinente."}
    response = reponseLLM(contexte, input_question)
    print("Réponse:", response)
    return {"response": response}
