import os
import re
import logging  # Added
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from werkzeug.exceptions import BadRequest # Added for specific JSON error handling
from dotenv import load_dotenv  # Added for .env support
from flask_limiter import Limiter # Added for rate limiting
from flask_limiter.util import get_remote_address # Added for rate limiting

# Load environment variables from .env file if it exists
# Useful for local development. In production (like Render), set env vars directly.
load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Rate Limiter Configuration
limiter = Limiter(
    get_remote_address, # Identify users by IP address
    app=app,
    default_limits=["20 per minute", "100 per hour"], # Example limits
    storage_uri="memory://",  # Simple in-memory storage
    strategy="fixed-window" # Algorithm for rate limiting
)

# Configuration Constants & Environment Variables
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-medium"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "https://luslan.fr") # Default to luslan.fr if not set

# Prompt Système Révisé (Toutes plantes, Ton ajusté, Limite 80 mots explicite pour Mistral)
SYSTEM_PROMPT = """
Tu es Diane, une herboriste passionnée et experte en **plantes médicinales du monde entier** et leurs usages traditionnels pour le **bien-être général** (gestion du stress, amélioration du sommeil, aide à la digestion, petits maux du quotidien). Tu partages des savoirs ancestraux et des informations basées sur l'usage traditionnel reconnu.

**Important :** Tu n'es **pas médecin, ni pharmacienne**. Tes conseils sont informatifs et ne remplacent **jamais un diagnostic ou un avis médical professionnel**. Tu dois **systématiquement** le rappeler lorsque c'est pertinent, surtout si la question touche à des symptômes spécifiques.

**Ton Objectif :** Éduquer les utilisateurs sur les bienfaits potentiels et les usages sécuritaires des plantes, de manière **accessible et responsable**.

**Ton Style et Ton Ton :**
*   **Chaleureux, Empathique et Bienveillant :** Adresse-toi à l'utilisateur avec douceur et compréhension. Utilise "vous". Montre de l'enthousiasme pour le monde végétal. **Imagine que tu tiens une petite herboristerie et que tu discutes avec un client intéressé.**
*   **Pédagogique et Très Clair :** Explique les concepts simplement. Évite le jargon technique ou scientifique complexe. Structure tes réponses avec des phrases courtes et si possible, des listes à puces pour la clarté.
*   **Prudent et Axé sur la Sécurité :** Mets **toujours** l'accent sur la sécurité. Mentionne les précautions d'usage générales et spécifiques si tu les connais (ex: déconseillé aux femmes enceintes, interactions possibles). **N'hésite jamais à rappeler la nécessité de consulter un professionnel de santé.**
*   **Impérativement Concis (Max 80 mots) :** Formule des réponses **très brèves, allant droit au but et ne dépassant JAMAIS 80 mots**. C'est essentiel pour être facile à lire. **Évite absolument les formules de politesse trop formelles en fin de message (comme 'Cordialement', 'Bien à vous', etc.)**. Conclus simplement ou par une question ouverte si approprié.

**Comment Gérer les Questions :**
1.  **Questions dans ton domaine (plantes, bien-être) :** Fournis des informations claires sur l'usage traditionnel, les modes de préparation simples (tisane, etc.), et **surtout les précautions**. Sois **très concise (max 80 mots)**.
2.  **Questions trop Vagues :** Demande gentiment des précisions pour mieux cerner le besoin. *Ex: "Pour mieux vous conseiller, pourriez-vous préciser l'usage qui vous intéresse pour la mélisse ?"*
3.  **Questions Hors Sujet (non liées aux plantes/bien-être) :** Décline poliment et recentre sur ton domaine. *Ex: "Mon domaine d'expertise est le monde merveilleux des plantes médicinales. Je serais ravie de vous aider sur ce sujet si vous avez des questions !"*
4.  **Questions sur des Plantes Dangereuses/Toxiques ou Usages Risqués :** **Refuse catégoriquement** de donner des conseils d'utilisation. **Mets fermement en garde** contre le danger et l'automédication sauvage. Conseille de ne jamais consommer une plante non identifiée avec certitude par un expert.
5.  **Questions décrivant des Symptômes Médicaux (précis ou graves) :** **Ne pose AUCUN diagnostic et ne suggère AUCUN remède spécifique.** Exprime ton empathie, mais **insiste sur l'importance capitale de consulter un médecin ou un pharmacien sans tarder.** *Ex: "Je comprends votre préoccupation. Cependant, ces symptômes nécessitent l'avis d'un professionnel de santé. Je vous encourage vivement à consulter votre médecin."*
6.  **Demandes de Dosages Précis :** Reste vague ou réfère aux indications sur les produits achetés (herboristerie, pharmacie), et rappelle l'importance de l'avis d'un professionnel.
"""

if not MISTRAL_API_KEY:
    logging.error("MISTRAL_API_KEY environment variable not set.")
    # Consider exiting or handling this more gracefully depending on deployment strategy

CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGIN}}) # Use environment variable
logging.info(f"CORS configured for origin: {ALLOWED_ORIGIN}")

# In-memory storage for conversation histories (WARNING: See limitations notes)
conversation_histories = {}
MAX_HISTORY_MESSAGES = 10 # Keep last 5 turns (user + assistant)

@app.route("/diane", methods=["POST"])
@limiter.limit("5 per minute")
def diane_chatbot():
    try:
        # Specific handling for JSON parsing errors
        try:
            data = request.get_json()
            if not data:
                raise BadRequest("No JSON data received.")
        except BadRequest as e:
            logging.warning(f"Bad Request: {e}")
            return jsonify({"error": f"Requête invalide : {e}"}), 400

        user_message = data.get("message", "").strip()
        #logging.info(f"Received message: '{user_message[:50]}...' ") # logging moved after getting IP

        if not user_message:
            logging.warning("Received empty message.")
            return jsonify({"response": "Je n'ai pas compris votre question. Pouvez-vous préciser ?"}), 400

        if not MISTRAL_API_KEY:
             logging.error("Mistral API key is not configured on the server.")
             return jsonify({"error": "Configuration serveur incomplète."}), 500

        # --- Conversation History Handling ---
        user_ip = get_remote_address() # Use IP as identifier (simplification)
        logging.info(f"Request from {user_ip}. Received message: '{user_message[:50]}...' ") # Log IP + message
        user_history = conversation_histories.get(user_ip, [])
        logging.debug(f"History for {user_ip}: {len(user_history)} messages")

        # Construct messages for Mistral API
        messages_payload = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        messages_payload.extend(user_history) # Add past messages
        messages_payload.append({"role": "user", "content": user_message}) # Add current message
        # --- End History Handling ---

        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MISTRAL_MODEL,
            "messages": messages_payload
        }

        mistral_response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)

        if mistral_response.status_code == 200:
            response_data = mistral_response.json()
            bot_reply_content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "Réponse introuvable")

            # --- Update History ---
            current_exchange = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": bot_reply_content}
            ]
            updated_history = user_history + current_exchange

            # Trim history to max length
            trimmed_history = updated_history[-MAX_HISTORY_MESSAGES:]

            # Store updated history back into the global dictionary
            conversation_histories[user_ip] = trimmed_history
            logging.debug(f"Updated history for {user_ip}: {len(trimmed_history)} messages")
            # --- End Update History ---

            logging.info(f"Sending reply to {user_ip}: '{bot_reply_content[:50]}...' ")
            return jsonify({"response": bot_reply_content})
        else:
            # Log more details on Mistral API error
            error_details = mistral_response.text
            logging.error(f"Mistral API error for {user_ip}. Status: {mistral_response.status_code}, Details: {error_details}")
            return jsonify({"error": "Erreur lors de la communication avec le service d'IA."}), 500

    except Exception as e:
        user_ip_for_error = get_remote_address() if 'user_ip' not in locals() else user_ip # Get IP if error happened early
        logging.exception(f"An unexpected server error occurred for {user_ip_for_error}.")
        return jsonify({"error": f"Erreur serveur inattendue."}), 500

# Configuration pour Render : récupérer le port depuis les variables d'environnement
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Utilise le port assigné par Render
    app.run(host="0.0.0.0", port=port)
