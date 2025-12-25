# Backend - Chatbot Juridique DZ (LITE)

Version légère optimisée pour Render Free Tier (512MB RAM).

## 🚀 Quick Start

### Local
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Variables d'environnement
```
GROQ_API_KEY=gsk_your_key_here
```

## 📡 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Info API |
| GET | `/health` | Health check |
| POST | `/chat` | Chatbot IA |
| GET | `/crimes` | Liste infractions |

## 🔧 Architecture

```
Question utilisateur
      ↓
Recherche par mots-clés
      ↓
Contexte juridique trouvé
      ↓
Groq LLaMA génère réponse
      ↓
Réponse naturelle
```

## 🐳 Déploiement Render

Le service est déployé sur :
https://chatbot-juridique-api.onrender.com
