# Chatbot Juridique DZ - Backend API

## 🚀 Quick Start

### 1. Créer un environnement virtuel
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer le serveur
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Tester l'API
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## 📡 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Info API |
| GET | `/health` | Health check |
| POST | `/chat` | Chatbot RAG |
| GET | `/crimes` | Liste infractions |
| GET | `/crimes/{id}` | Détail infraction |

## 🔧 Stack Technique

- **Framework**: FastAPI
- **Embeddings**: Sentence Transformers (multilingual)
- **Vector DB**: FAISS
- **Model**: `paraphrase-multilingual-MiniLM-L12-v2`

## 🐳 Docker

```bash
docker build -t chatbot-juridique-backend .
docker run -p 8000:8000 chatbot-juridique-backend
```
