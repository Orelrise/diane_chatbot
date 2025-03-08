from flask import Flask, request, jsonify
import requests

# Configuration
app = Flask(__name__)

MISTRAL_API_KEY = "BkO0BEjhCaVrMJt3ohVVQkALeVl3qxv4"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

@app.route("/", methods=["GET"])
def home():
    return "Diane Chatbot API is running!"

@app.route("/diane", methods=["POST"])
def chat_with_diane():
    try:
        # Vérifie si la requête contient du JSON
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Message manquant"}), 400

        user_message = data["message"]
        print(f"📩 Message reçu : {user_message}")  # Affiche le message reçu par Flask

        # Création de la requête pour Mistral
        payload = {
            "model": "mistral-medium",
            "messages": [
                {"role": "system", "content": "Tu es Diane, une herboriste experte en plantes médicinales."},
                {"role": "user", "content": user_message}
            ]
        }

        print(f"🚀 Envoi à Mistral : {payload}")  # Affiche la requête envoyée à Mistral

        # Envoie la requête à Mistral
        response = requests.post(MISTRAL_API_URL, headers=HEADERS, json=payload)

        if response.status_code != 200:
            print(f"⚠️ Erreur API Mistral : {response.status_code} - {response.text}")
            return jsonify({"error": "Problème avec l'API Mistral"}), 500

        response_data = response.json()
        bot_reply = response_data["choices"][0]["message"]["content"]

        print(f"💬 Réponse de Mistral : {bot_reply}")  # Affiche la réponse de Mistral

        return jsonify({"response": bot_reply})

    except Exception as e:
        print(f"🔥 Erreur serveur : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
