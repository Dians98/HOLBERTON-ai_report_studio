import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Charge les variables du fichier .env
load_dotenv()

# 2. Récupère la configuration choisie
provider = os.getenv("AI_PROVIDER", "gemini")
api_key = os.getenv("AI_API_KEY")
base_url = os.getenv("AI_BASE_URL")
model_name = os.getenv("AI_MODEL")

print(
    f"🔌 Connexion au fournisseur : {provider.upper()} (Modèle: {model_name})")

# 3. Initialise le client OpenAI générique avec les bonnes adresses
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)


def ask(prompt: str) -> str:
    """Envoie un prompt à l'IA actuellement sélectionnée dans le .env."""
    response = client.chat.completions.create(
        model=model_name,  # Le modèle est sélectionné ici dynamiquement !
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


# Zone de test automatique
if __name__ == "__main__":
    try:
        reponse = ask("Dis 'Le switch de modèle fonctionne !' en français.")
        print(f"✅ Réponse : {reponse}")
    except Exception as e:
        print(f"❌ Erreur avec {provider} : {e}")
