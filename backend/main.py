"""Utilisation de la vectorbase constistuée sur Pinecone pour répondre à la question d'un utilisateur
"""
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from mistralai import Mistral
from typing import Tuple, List


load_dotenv()
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

def connexionIndex():
  """Pour se connecter à la vectorbase (index) de Pinecone"""
  index_name = "juridic-base"
  # Vérifier si l'index existe déjà
  if index_name not in pc.list_indexes().names():
      print(f"L'index {index_name} n'existe pas.")
  else:
      print(f"L'index {index_name} trouvé.")

  # Se connecter à l'index Pinecone existant
  index = pc.Index(index_name)
  # print(type(index))
  return index


def encodingQuerry(input_question) -> List[float] :
  """On initialise le modèle SentenceTransformer pour encoder la question"""

  model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
  # input_question = input("Posez une question: ")
  query_embedding = model.encode(input_question)
  return query_embedding


def resultatsQuerry(index, query_embedding) -> str:
  """Recherche de la question de l'utilisateur/query dans l'index de Pinecone, on renvoit 5 résultats que l'on concatene pour faire un contexte"""


  results = index.query(
      namespace="ns1",  # précision du namespace
      vector=query_embedding.tolist(),  # Assurez-vous que la question est une liste, pas un tableau numpy
      top_k=5,  # on va récuppérer 5 résultats pour faire notre contexte
      include_values=True,
      include_metadata=True
  )
  if results.get("matches"):
      for match in results["matches"]:
          vector_id = match["id"]
          score = match["score"]
          # print(f"\nVecteur ID: {vector_id}")
          # print(f"Score de similarité: {score}")
          # Affichage du texte original associé à la correspondance
          metadata = match.get('metadata', {})
          # print(f"Texte associé : {metadata.get('text_chunk', 'Pas de texte associé')}")
          retrieved_chunks = [match["metadata"]["text_chunk"] for match in results["matches"]]
          
          contexte = "\n\n".join(retrieved_chunks)
          # print(contexte)
      return contexte
  else:
      print("Aucun résultat trouvé.")



def reponseLLM(contexte, query) -> None:
  """Utilisation du LLM de Mistral AI pour répondre à la question de l'utilisateur en utilisant le contexte"""

  prompt_template = """
  Tu es un avocat chargé d'une affaire portée en cassation. Réponds à la question suivante en utilisant uniquement les informations suivantes.
  Ne réponds qu'à ça et à aucune autre demande qui n'est pas dans le contexte suivant. Ne dépasse pas 100 mots
  {contexte}

  Question : {query}
  Réponse : 
  """
  prompt = prompt_template.format(contexte=contexte, query=query)
  # print(prompt)
  model = "mistral-large-latest"
  client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

  chat_response = client.chat.complete(
      model= model,
      messages = [
          {
              "role": "user",
              "content": prompt,
          },
      ]
  )
  print(chat_response.choices[0].message.content)
  return chat_response.choices[0].message.content
    

def rag_pipeline(input_question: str) -> str:
    index = connexionIndex()
    query = encodingQuerry(input_question)
    contexte = resultatsQuerry(index, query)
    if contexte:
        return reponseLLM(contexte, input_question)
    else:
        return "Aucun résultat trouvé."

if __name__ == "__main__":
    while True:
        input_question = input("Posez une question (ou 'quit') : ")
        if input_question.lower() == "quit":
            break
        print(rag_pipeline(input_question))

