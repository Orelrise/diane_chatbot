# 🌿 Diane Herborist API

API REST backend pour Diane, une conseillère herboriste virtuelle spécialisée en plantes médicinales. Cette API utilise Groq (Llama 3.3 70B) pour fournir des conseils éducatifs sur l'herboristerie et la phytothérapie.

## 📋 Table des Matières

- [Caractéristiques](#caractéristiques)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API Endpoints](#api-endpoints)
- [Déploiement sur Render](#déploiement-sur-render)
- [Tests](#tests)
- [Sécurité](#sécurité)

## ✨ Caractéristiques

- **API REST asynchrone** avec FastAPI
- **IA conversationnelle** via Groq API (Llama 3.3 70B Versatile)
- **Validation pré-API** des questions hors-sujet (économie de tokens)
- **Rate Limiting** : 10 requêtes/minute par IP
- **CORS** configuré pour intégration WordPress
- **Réponses HTML formatées** prêtes pour affichage direct
- **Logging complet** avec masquage des clés API
- **Tests unitaires** avec pytest
- **Documentation auto-générée** avec FastAPI

## 🏗️ Architecture

```
diane_chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application FastAPI + endpoints
│   ├── config.py            # Configuration et variables d'environnement
│   ├── models.py            # Modèles Pydantic (request/response)
│   ├── prompts.py           # System prompt de Diane
│   ├── services/
│   │   ├── __init__.py
│   │   ├── groq_service.py  # Service d'appels API Groq
│   │   └── validator.py     # Validation des questions hors-sujet
│   └── utils/
│       ├── __init__.py
│       └── logger.py        # Configuration du logging
├── tests/
│   ├── __init__.py
│   └── test_api.py          # Tests unitaires
├── .env                     # Variables d'environnement (NON commité)
├── .env.example             # Template des variables d'environnement
├── .gitignore               # Fichiers à ignorer
├── requirements.txt         # Dépendances Python
└── README.md                # Documentation
```

## 🚀 Installation

### Prérequis

- Python 3.11+
- pip
- Git

### Installation Locale

1. **Cloner le repository**

```bash
git clone https://github.com/votre-username/diane_chatbot.git
cd diane_chatbot
```

2. **Créer un environnement virtuel**

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**

```bash
cp .env.example .env
# Éditer .env et ajouter votre clé API Groq
```

5. **Lancer le serveur de développement**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur `http://localhost:8000`

Documentation interactive : `http://localhost:8000/docs`

## ⚙️ Configuration

### Variables d'Environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```bash
# Groq API Configuration
GROQ_API_KEY=votre_clé_api_groq
MAX_TOKENS=800
TEMPERATURE=0.7
MODEL=llama-3.3-70b-versatile

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
```

### Obtenir une Clé API Groq

1. Créer un compte sur [Groq Console](https://console.groq.com/)
2. Générer une clé API dans les paramètres
3. Copier la clé dans votre fichier `.env`

## 📖 Utilisation

### Exemple de Requête

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quelles plantes pour le sommeil ?"
  }'
```

### Exemple de Réponse

```json
{
  "response": "<p>Pour améliorer le sommeil, plusieurs plantes sont efficaces :</p><ul><li><strong>Valériane</strong> (Valeriana officinalis) : Réduit le temps d'endormissement...</li></ul>",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-11-13T14:30:00Z",
  "is_valid_topic": true,
  "tokens_used": 380
}
```

## 🔌 API Endpoints

### `GET /`

Health check basique

**Réponse :**
```json
{
  "status": "healthy",
  "service": "Diane Herborist API",
  "version": "1.0.0"
}
```

### `GET /health`

Vérification détaillée incluant la connexion Groq

**Réponse :**
```json
{
  "api_status": "ok",
  "groq_connection": true,
  "timestamp": "2025-11-13T14:30:00Z"
}
```

### `POST /chat` ⭐

Endpoint principal pour les questions

**Request Body :**
```json
{
  "message": "Quelles plantes pour le sommeil ?",
  "conversation_id": "optional-uuid-v4",
  "user_id": "optional-wordpress-user-id"
}
```

**Réponse (question valide) :**
```json
{
  "response": "<p>HTML formaté...</p>",
  "conversation_id": "uuid-v4",
  "timestamp": "2025-11-13T14:30:00Z",
  "is_valid_topic": true,
  "tokens_used": 380
}
```

**Réponse (hors-sujet) :**
```json
{
  "response": "<p>Je suis désolée, mais je suis spécialisée exclusivement en herboristerie...</p>",
  "conversation_id": "uuid-v4",
  "timestamp": "2025-11-13T14:30:00Z",
  "is_valid_topic": false,
  "tokens_used": 0
}
```

**Rate Limiting :** 10 requêtes/minute par IP

**Status Codes :**
- `200` : Succès
- `422` : Validation error (message invalide)
- `429` : Rate limit dépassé
- `500` : Erreur serveur

## 🌐 Déploiement sur Render

### Étape 1 : Préparer le Repository GitHub

1. **Commiter tous les fichiers**

```bash
git add .
git commit -m "Initial commit - Diane Herborist API"
```

2. **Pousser sur GitHub**

```bash
git remote add origin https://github.com/votre-username/diane_chatbot.git
git branch -M main
git push -u origin main
```

### Étape 2 : Configurer Render

1. **Créer un compte** sur [Render](https://render.com/)

2. **Créer un nouveau Web Service**
   - Cliquer sur "New +" → "Web Service"
   - Connecter votre repository GitHub
   - Sélectionner le repository `diane_chatbot`

3. **Configuration du Service**

   - **Name** : `diane-api` (ou votre choix)
   - **Region** : Choisir la région la plus proche
   - **Branch** : `main`
   - **Root Directory** : (laisser vide)
   - **Runtime** : `Python 3`
   - **Build Command** :
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command** :
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type** : Free (ou selon vos besoins)

4. **Configurer les Variables d'Environnement** ⚠️ **IMPORTANT**

   Dans la section "Environment", ajoutez ces variables :

   ```
   GROQ_API_KEY=your_groq_api_key_here
   MAX_TOKENS=800
   TEMPERATURE=0.7
   MODEL=llama-3.3-70b-versatile
   RATE_LIMIT_PER_MINUTE=10
   ```

   **⚠️ Note Importante** :
   - L'API **démarrera même sans `GROQ_API_KEY`** (pour permettre le déploiement)
   - Les endpoints `/` et `/health` fonctionneront
   - L'endpoint `/chat` retournera une erreur claire jusqu'à ce que la clé soit ajoutée
   - Obtenez votre clé sur [Groq Console](https://console.groq.com/keys)
   - Une fois la clé ajoutée, Render redéploiera automatiquement

5. **Déployer**

   Cliquer sur "Create Web Service"

   Render va automatiquement :
   - Cloner votre repository
   - Installer les dépendances
   - Démarrer l'application

### Étape 3 : Vérifier le Déploiement

Une fois déployé, votre API sera accessible sur :

```
https://diane-api.onrender.com
```

Tester avec :

```bash
curl https://diane-api.onrender.com/health
```

### Mises à Jour Automatiques

Render redéploie automatiquement à chaque push sur la branche `main`.

## 🧪 Tests

### Lancer les Tests

```bash
pytest tests/test_api.py -v
```

### Couverture des Tests

```bash
pytest tests/test_api.py --cov=app --cov-report=html
```

### Tests Inclus

- ✅ Health check endpoints
- ✅ Chat endpoint avec questions valides
- ✅ Chat endpoint avec questions hors-sujet
- ✅ Validation des messages
- ✅ Gestion des erreurs
- ✅ Modèles Pydantic
- ✅ Générateur de conversation ID

## 🔒 Sécurité

### Bonnes Pratiques Implémentées

1. **Protection des Secrets**
   - Clé API stockée uniquement en variable d'environnement
   - `.env` dans `.gitignore`
   - Masquage de la clé dans les logs

2. **Rate Limiting**
   - 10 requêtes/minute par IP
   - Protection contre les abus

3. **CORS**
   - Configuré pour autoriser uniquement les origines approuvées
   - Par défaut : toutes origines (modifiable dans `config.py`)

4. **Validation des Entrées**
   - Validation Pydantic sur tous les endpoints
   - Longueur maximale des messages : 1000 caractères
   - Filtrage des questions hors-sujet

5. **Gestion d'Erreurs**
   - Messages d'erreur user-friendly
   - Pas de stack traces exposées
   - Logging détaillé côté serveur

### Masquage de la Clé API

La clé API est automatiquement masquée dans les logs :

```
API Key configured: gsk_WXP...***vLPy
```

## 📚 Documentation

### Documentation Interactive

FastAPI génère automatiquement une documentation interactive :

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

### Exemples d'Intégration

#### JavaScript / WordPress

```javascript
async function askDiane(question) {
  const response = await fetch('https://diane-api.onrender.com/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: question
    })
  });

  const data = await response.json();

  // Injecter le HTML dans votre widget
  document.getElementById('diane-response').innerHTML = data.response;
}
```

#### Python

```python
import requests

response = requests.post(
    'https://diane-api.onrender.com/chat',
    json={'message': 'Propriétés de la camomille ?'}
)

data = response.json()
print(data['response'])
```

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push sur la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📝 License

Ce projet est sous licence MIT.

## 👤 Auteur

Diane Chatbot API - Conseillère Herboriste Virtuelle

## 🙏 Remerciements

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderne et rapide
- [Groq](https://groq.com/) - API d'inférence LLM ultra-rapide
- [Render](https://render.com/) - Plateforme de déploiement cloud

---

**⚠️ Avertissement** : Les conseils fournis par Diane sont éducatifs et ne remplacent pas un avis médical professionnel.
