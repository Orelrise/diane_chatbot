import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://luslan.fr"}})  # Autorise uniquement Luslan.fr

# Charger la clé API Mistral depuis les variables d'environnement
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def clean_response(text, word_limit=80):
    """
    Limite la réponse à un nombre maximal de mots sans couper une phrase.
    """
    words = text.split()
    if len(words) <= word_limit:
        return text  # Pas besoin de tronquer

    # Cherche un point de coupure intelligent (évite de couper une phrase)
    truncated_text = " ".join(words[:word_limit])
    match = re.search(r"([.!?])\s", truncated_text[::-1])
    if match:
        cut_index = len(truncated_text) - match.start()
        return truncated_text[:cut_index].strip()

    return truncated_text.strip() + "..."  # Ajoute "..." si coupure forcée

@app.route("/diane", methods=["POST"])
def diane_chatbot():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"response": "Je n'ai pas compris votre question. Pouvez-vous préciser ?"}), 400

        # Requête à l'API Mistral
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistral-medium",
            "messages": [
                {"role": "system", "content": (
                    "Tu es Diane, une herboriste experte en plantes médicinales. "
                    "Tes réponses doivent être **courtes (≤ 80 mots)**, bien structurées et faciles à comprendre. "
                    "Utilise un ton chaleureux, pédagogique et bienveillant. "
                    "Si la question est trop large, donne une réponse concise et invite à poser des précisions."
                )},
                {"role": "user", "content": user_message}
            ]
        }

        mistral_response = requests.post(url, headers=headers, json=payload)

        if mistral_response.status_code == 200:
            response_data = mistral_response.json()
            bot_reply = response_data.get("choices", [{}])[0].get("message", {}).get("content", "Réponse introuvable")

            return jsonify({"response": clean_response(bot_reply)})
        else:
            return jsonify({"error": "Erreur avec l'API Mistral."}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500

# Configuration pour Render : récupérer le port depuis les variables d'environnement
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Utilise le port assigné par Render
    app.run(host="0.0.0.0", port=port)
