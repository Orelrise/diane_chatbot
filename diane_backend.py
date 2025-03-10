import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://luslan.fr"}})  # Autorise uniquement luslan.fr

# Charger la clé API Mistral depuis les variables d'environnement
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def truncate_response(text, max_words=80):
    """ Tronque la réponse à max_words mots. """
    words = text.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

@app.route("/diane", methods=["POST"])
def diane_chatbot():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"response": "Aucun message reçu."}), 400

        # Requête à l'API Mistral
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistral-medium",
            "messages": [
                {"role": "system", "content": "Tu es Diane, une herboriste experte en plantes médicinales."},
                {"role": "user", "content": user_message}
            ]
        }

        mistral_response = requests.post(url, headers=headers, json=payload)

        if mistral_response.status_code == 200:
            response_data = mistral_response.json()
            bot_reply = response_data.get("choices", [{}])[0].get("message", {}).get("content", "Réponse introuvable")
            bot_reply = truncate_response(bot_reply)  # Limitation à 80 mots
            return jsonify({"response": bot_reply})
        else:
            return jsonify({"error": f"Erreur avec l'API Mistral: {mistral_response.status_code}"}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500

# Configuration pour Render : récupérer le port depuis les variables d'environnement
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Utilise le port assigné par Render
    app.run(host="0.0.0.0", port=port)
