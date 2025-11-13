# 🔧 Guide Rapide : Corriger le Déploiement Render

## 🚨 Problème

Render essaie d'exécuter `gunicorn diane_backend:app` (ancien backend Flask) au lieu de `uvicorn app.main:app` (nouveau backend FastAPI).

## ✅ Solution en 3 Étapes

### Étape 1 : Aller dans Settings

1. Connectez-vous à **Render** : https://dashboard.render.com/
2. Cliquez sur votre service (diane-api)
3. Allez dans l'onglet **"Settings"**

### Étape 2 : Modifier le Start Command

Descendez jusqu'à **"Build & Deploy"** et trouvez **"Start Command"**.

**Remplacez** :
```bash
gunicorn diane_backend:app
```

**Par** :
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Étape 3 : Sauvegarder et Redéployer

1. Cliquez sur **"Save Changes"** (en bas de la page)
2. Render va automatiquement redéployer avec la bonne commande
3. Attendez 2-3 minutes que le déploiement se termine

## 🎯 Configuration Complète Render

Voici TOUTES les valeurs à vérifier dans Settings :

### Build & Deploy

**Build Command** :
```bash
pip install -r requirements.txt
```

**Start Command** :
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment

**Variables d'environnement requises** :

| Clé | Valeur |
|-----|--------|
| `GROQ_API_KEY` | `votre_nouvelle_cle_groq` (à obtenir sur console.groq.com) |
| `MAX_TOKENS` | `800` |
| `TEMPERATURE` | `0.7` |
| `MODEL` | `llama-3.3-70b-versatile` |
| `RATE_LIMIT_PER_MINUTE` | `10` |

**⚠️ Important** : Si vous n'avez pas encore de clé Groq valide, obtenez-en une sur https://console.groq.com/keys

## 🔄 Alternative : Utiliser render.yaml (Automatique)

Si vous créez un **nouveau** service Render :

1. Supprimez l'ancien service sur Render
2. Créez un nouveau service "Web Service"
3. Connectez votre GitHub repo
4. Render détectera automatiquement `render.yaml` et utilisera la bonne configuration
5. Ajoutez seulement `GROQ_API_KEY` manuellement dans Environment

## ✅ Vérification

Une fois redéployé, testez :

```bash
# Health check basique
curl https://votre-app.onrender.com/

# Health check détaillé
curl https://votre-app.onrender.com/health

# Test question hors-sujet (devrait marcher sans Groq)
curl -X POST https://votre-app.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Qui a gagné le match de football ?"}'
```

**Réponse attendue** :
```json
{
  "response": "<p>Je suis désolée, mais je suis spécialisée exclusivement en herboristerie...</p>",
  "conversation_id": "...",
  "timestamp": "...",
  "is_valid_topic": false,
  "tokens_used": 0
}
```

## 📝 Logs à Vérifier

Dans les logs Render, vous devriez voir :

```
✅ Installing collected packages: ... fastapi ... uvicorn ...
✅ Build successful 🎉
✅ Deploying...
✅ INFO:     Started server process [1]
✅ INFO:     Waiting for application startup.
✅ INFO:     Diane Herborist API v1.0.0 started successfully
✅ INFO:     Application startup complete.
✅ INFO:     Uvicorn running on http://0.0.0.0:10000
```

**❌ Si vous voyez encore** :
```
bash: line 1: gunicorn: command not found
```

👉 Retournez à l'Étape 2 et vérifiez que vous avez bien sauvegardé le Start Command.

## 🆘 Besoin d'Aide ?

- **Documentation Render** : https://render.com/docs/web-services
- **Logs de déploiement** : Cliquez sur "Logs" dans votre service Render
- **Variables d'environnement** : Vérifiez qu'elles sont toutes présentes dans "Environment"

---

**Résumé** : Changez le Start Command dans Settings Render de `gunicorn diane_backend:app` vers `uvicorn app.main:app --host 0.0.0.0 --port $PORT` et sauvegardez ! 🚀
