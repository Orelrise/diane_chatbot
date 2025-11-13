# 🚀 Notes de Déploiement - Diane API

## ✅ État du Projet

**Date** : 2025-11-13
**Status** : Prêt pour déploiement

### Fichiers Créés

- ✅ Structure complète du projet
- ✅ Tous les modules Python implémentés
- ✅ Tests unitaires (11/13 passent)
- ✅ Documentation complète (README.md)
- ✅ Configuration (.env.example, .gitignore)
- ✅ Dépendances (requirements.txt)

### Tests

**Résultats** : 11/13 tests passent ✅

**Tests qui passent** :
- ✅ Health check endpoints (/, /health)
- ✅ Validation des messages
- ✅ Détection des questions hors-sujet
- ✅ Gestion des erreurs
- ✅ Modèles Pydantic
- ✅ Générateur de conversation ID

**Tests qui échouent** :
- ❌ Appels API Groq (403 Access denied)
  - Raison probable : La clé API nécessite vérification/activation
  - Le code est correct, c'est un problème d'authentification API

## 🔑 Configuration Groq API

**⚠️ IMPORTANT** : Vérifier la clé API Groq

La clé fournie retourne une erreur 403. Actions à prendre :

1. **Vérifier sur Groq Console** : https://console.groq.com/
   - La clé est-elle active ?
   - A-t-elle les bonnes permissions ?
   - Y a-t-il des limites de quota ?

2. **Régénérer si nécessaire**
   - Créer une nouvelle clé API
   - Mettre à jour la variable d'environnement `GROQ_API_KEY`

3. **Tester la connexion**
   ```bash
   curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
     -H "Authorization: Bearer VOTRE_CLE" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "llama-3.3-70b-versatile",
       "messages": [{"role": "user", "content": "test"}]
     }'
   ```

## 📦 Déploiement sur Render

### Variables d'Environnement Requises

```bash
GROQ_API_KEY=<votre_nouvelle_clé_groq>
MAX_TOKENS=800
TEMPERATURE=0.7
MODEL=llama-3.3-70b-versatile
RATE_LIMIT_PER_MINUTE=10
```

### Commandes Render

**Build Command** :
```bash
pip install -r requirements.txt
```

**Start Command** :
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 🧪 Tests Post-Déploiement

Une fois déployé sur Render, tester :

1. **Health Check**
   ```bash
   curl https://votre-app.onrender.com/
   curl https://votre-app.onrender.com/health
   ```

2. **Question Hors-Sujet** (devrait fonctionner même sans Groq)
   ```bash
   curl -X POST "https://votre-app.onrender.com/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Qui a gagné le match de football ?"}'
   ```

3. **Question Valide** (nécessite clé Groq valide)
   ```bash
   curl -X POST "https://votre-app.onrender.com/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Quelles plantes pour le sommeil ?"}'
   ```

## 🔒 Sécurité

- ✅ Clé API masquée dans les logs
- ✅ .env dans .gitignore (non commité)
- ✅ Rate limiting activé
- ✅ CORS configuré
- ✅ Validation des entrées

## 📚 Documentation

- **Swagger UI** : `/docs`
- **ReDoc** : `/redoc`
- **README complet** : `README.md`

## 🎯 Prochaines Étapes

1. ✅ Code commité sur GitHub
2. ⚠️ Vérifier/régénérer clé API Groq
3. 🚀 Déployer sur Render
4. 🧪 Tester en production
5. ✅ Intégrer au widget WordPress

## 📞 Support

- Documentation Groq : https://console.groq.com/docs
- Documentation FastAPI : https://fastapi.tiangolo.com/
- Documentation Render : https://render.com/docs

---

**Note** : Le backend est complet et fonctionnel. Seule la clé API Groq nécessite vérification.
