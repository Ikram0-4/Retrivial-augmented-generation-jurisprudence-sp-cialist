import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from mistralai import Mistral
from typing import List, Optional

# Chargement des variables d'environnement
load_dotenv()

print("Chargement du modèle d'embedding...")

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Connexion Pinecone...")

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

print("Initialisation client Mistral...")

mistral_client = Mistral(
    api_key=os.getenv("MISTRAL_API_KEY")
)

print("Initialisation terminée.\n")

def connexionIndex():
    """Connexion à l'index Pinecone"""

    index_name = "juridic-base"

    if index_name not in pc.list_indexes().names():
        raise Exception(f"L'index {index_name} n'existe pas.")

    print(f"Index '{index_name}' trouvé.")

    return pc.Index(index_name)


# Embedding question

def encodingQuerry(input_question: str) -> List[float]:
    """Encode la question utilisateur"""

    print("⏳ Encoding...")

    query_embedding = embedding_model.encode(input_question)

    print("Encoding terminé.")

    return query_embedding




def resultatsQuerry(index, query_embedding) -> Optional[str]:
    """Recherche des chunks pertinents"""

    print("🔎 Recherche vectorielle...")

    results = index.query(
        namespace="ns1",
        vector=query_embedding.tolist(),
        top_k=5,
        include_metadata=True
    )

    matches = results.get("matches")

    if not matches:
        print("Aucun résultat trouvé.")
        return None

    retrieved_chunks = [
        match["metadata"]["text_chunk"]
        for match in matches
        if "text_chunk" in match.get("metadata", {})
    ]

    contexte = "\n\n".join(retrieved_chunks)

    print(f"{len(retrieved_chunks)} chunks récupérés.")

    return contexte


# Réponse Mistral


def reponseLLM(contexte: str, query: str) -> str:
    """Génération de réponse avec Mistral"""

    print("Appel Mistral...")

    prompt_template = """
Tu es un avocat chargé d'une affaire portée en cassation.

Réponds uniquement avec les informations présentes dans le contexte suivant.
Ne dépasse pas 100 mots.

CONTEXTE :
{contexte}

QUESTION :
{query}

RÉPONSE :
"""

    prompt = prompt_template.format(
        contexte=contexte,
        query=query
    )

    chat_response = mistral_client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response = chat_response.choices[0].message.content

    print("Réponse générée.\n")

    return response


def rag_pipeline(input_question: str) -> str:

    try:
        index = connexionIndex()

        query_embedding = encodingQuerry(input_question)

        contexte = resultatsQuerry(
            index,
            query_embedding
        )

        if not contexte:
            return "Aucun résultat trouvé."

        response = reponseLLM(
            contexte,
            input_question
        )

        return response

    except Exception as e:
        print(f"Erreur : {e}")
        return "Une erreur est survenue."

if __name__ == "__main__":

    print("=== RAG Juridique ===\n")

    while True:

        input_question = input(
            "Posez une question (ou 'quit') : "
        )

        if input_question.lower() == "quit":
            print("Arrêt du programme.")
            break

        response = rag_pipeline(input_question)

        print("\n Réponse :")
        print(response)
        print("\n" + "=" * 50 + "\n")
