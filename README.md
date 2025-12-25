# 🏛️ Chatbot Juridique Algérien

Application mobile Flutter + Backend FastAPI pour consulter le Code pénal algérien avec une IA conversationnelle.

## 🎯 Fonctionnalités

- 💬 **Interface chat** style WhatsApp
- 🔍 **Recherche intelligente** par mots-clés
- 🤖 **Réponses IA** générées par Groq LLaMA
- 📜 **10 infractions** du Code pénal algérien
- ⚠️ **Disclaimers juridiques** automatiques

## 📱 Screenshots

L'application répond à des questions comme :
- "Quelle est la peine pour vol ?"
- "Article 350"
- "Sanction corruption ?"

## 🛠️ Stack Technique

| Composant | Technologie |
|-----------|-------------|
| Frontend | Flutter |
| Backend | FastAPI (Python) |
| LLM | Groq (LLaMA 3.1) |
| Recherche | Mots-clés |
| Hébergement | Render |

## 🚀 Installation

### Backend (Local)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Créer .env avec ta clé Groq
echo GROQ_API_KEY=gsk_... > .env

# Lancer
uvicorn main:app --reload --port 8000
```

### Flutter

```bash
flutter pub get
flutter run
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Info API |
| GET | `/health` | Health check |
| POST | `/chat` | Chatbot IA |
| GET | `/crimes` | Liste infractions |
| GET | `/config` | Configuration |

### Exemple de requête

```bash
curl -X POST https://chatbot-juridique-api.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelle est la peine pour vol ?"}'
```

## 📊 Données

10 infractions du Code pénal algérien :
- Vol simple (Art. 350)
- Vol avec violence (Art. 353)
- Meurtre (Art. 254)
- Faux témoignage (Art. 232)
- Escroquerie (Art. 372)
- Coups et blessures (Art. 264)
- Diffamation (Art. 296)
- Corruption (Art. 126)
- Trafic de stupéfiants (Loi 04-18)
- Abus de confiance (Art. 376)

## ⚠️ Avertissement

> Cette application fournit des **informations juridiques générales** et ne constitue pas un avis juridique personnalisé. Pour toute situation spécifique, consultez un avocat.

## 📝 Licence

MIT License

## 👤 Auteur

**Amine Louey** - [@aminelouey](https://github.com/aminelouey)
