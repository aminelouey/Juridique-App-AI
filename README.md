# ⚖️ Chatbot Juridique DZ

Application mobile Flutter + Backend FastAPI pour consulter le **Code Pénal Algérien** avec une IA conversationnelle.

![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-FF6B6B?style=for-the-badge&logo=ai&logoColor=white)

## 🎯 Fonctionnalités

### 📱 Application Mobile
- 💬 **Interface ChatGPT-like** moderne et fluide
- 🌙 **Dark mode** style Gemini
- ✨ **Streaming text** - réponses caractère par caractère
- � **Sidebar** avec historique des conversations
- ⚙️ **Page paramètres** complète
- 🔄 **Pull-to-refresh** pour reconnecter

### 🤖 Intelligence Artificielle
- 🔍 **RAG** (Retrieval Augmented Generation)
- 🚀 **Groq LLaMA 3.1** pour les réponses
- 🧠 **Jina AI** pour les embeddings sémantiques
- 📚 **147 articles** du Code Pénal Algérien

## � Screenshots

L'application répond à des questions comme :
- "Quelle est la peine pour vol ?"
- "Explique-moi l'article 350"
- "Quelles sont les sanctions pour corruption ?"

## 🛠️ Stack Technique

| Composant | Technologie |
|-----------|-------------|
| Frontend | Flutter (Dart) |
| Backend | FastAPI (Python) |
| LLM | Groq (LLaMA 3.1 70B) |
| Embeddings | Jina AI |
| Database | SQLite |
| Hébergement | Render |

## 🚀 Installation

### Backend (Local)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Créer .env avec tes clés API
echo GROQ_API_KEY=gsk_... > .env
echo JINA_API_KEY=jina_... >> .env

# Initialiser la base de données
python scripts/init_db.py
python scripts/add_articles.py

# Lancer le serveur
uvicorn main:app --reload --port 8000
```

### Flutter (Mobile)

```bash
flutter pub get
flutter run
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Info API |
| GET | `/health` | Health check + status RAG |
| POST | `/chat` | Chatbot IA avec RAG |
| GET | `/articles` | Liste des articles |
| GET | `/config` | Configuration LLM |

### Exemple de requête

```bash
curl -X POST https://chatbot-juridique-api.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelle est la peine pour vol ?"}'
```

## 📊 Base de Données

**147 articles** du Code Pénal Algérien organisés par catégories :

| Catégorie | Nombre |
|-----------|--------|
| Atteintes aux personnes | ~40 |
| Atteintes aux biens | ~35 |
| Corruption & Abus | ~20 |
| Stupéfiants | ~15 |
| Crimes contre la famille | ~20 |
| Autres | ~17 |

## 🔧 Configuration

### Variables d'environnement (Backend)

```env
GROQ_API_KEY=gsk_xxxxx    # API Groq pour LLM
JINA_API_KEY=jina_xxxxx   # API Jina pour embeddings
```

### URL Backend (Flutter)

Modifier dans `lib/services/api_service.dart` :
```dart
static const String baseUrl = 'https://chatbot-juridique-api.onrender.com';
// Pour local: 'http://10.0.2.2:8000' (émulateur Android)
```

## ⚠️ Avertissement Juridique

> **IMPORTANT** : Cette application fournit des **informations juridiques générales** basées sur le Code Pénal Algérien.
> 
> ❌ Ne constitue pas un avis juridique professionnel  
> ❌ Ne remplace pas la consultation d'un avocat  
> ✅ À titre informatif uniquement

## 📝 Licence

MIT License - Voir [LICENSE](LICENSE)

## 👤 Auteur

**Amine Louey** - [@aminelouey](https://github.com/aminelouey)

---

<p align="center">
  Made with ❤️ in Algeria 🇩🇿
</p>
