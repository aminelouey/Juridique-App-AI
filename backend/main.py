"""
Chatbot Juridique DZ - Backend FastAPI
RAG complet avec FAISS + Embeddings + LLM (GPT/LLaMA)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from services.rag_service import RAGService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Chatbot Juridique DZ API",
    description="API de recherche juridique avec Groq LLM (version LITE)",
    version="2.1.0-lite"
)

# CORS configuration for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
rag_service = RAGService()


# Request/Response models
class ChatRequest(BaseModel):
    question: str
    use_llm: bool = True  # Use LLM for natural response
    
class CrimeResult(BaseModel):
    id: int
    crime: str
    article: str
    categorie: str
    prison: str
    amende: str
    description: str
    score: float

class ChatResponse(BaseModel):
    response: str
    crimes: List[CrimeResult]
    llm_provider: str
    disclaimer: str = "⚠️ Cette réponse est une information juridique générale et ne constitue pas un avis juridique personnalisé."


@app.on_event("startup")
async def startup_event():
    """Load data and initialize LLM on startup"""
    await rag_service.initialize()
    print("✅ RAG Service LITE initialized")


@app.get("/")
async def root():
    return {
        "message": "🏛️ Chatbot Juridique DZ API (LITE)",
        "status": "online",
        "version": "2.1.0-lite",
        "features": ["Keywords", "Groq LLM"]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "rag_ready": rag_service.is_ready,
        "llm_provider": rag_service.llm_service.provider if rag_service.llm_service else "none"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - RAG with LLM for natural responses
    
    Flow:
    1. User question → Embedding
    2. FAISS search → Find relevant crimes
    3. Context + Question → LLM
    4. Natural response like ChatGPT
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if not rag_service.is_ready:
        raise HTTPException(status_code=503, detail="RAG service not ready")
    
    # Step 1 & 2: Search using FAISS
    results = await rag_service.search(request.question)
    
    # Step 3 & 4: Generate response with LLM
    if request.use_llm:
        response_text = await rag_service.generate_response(request.question, results)
    else:
        response_text = rag_service.format_response(results, request.question)
    
    # Format crime results
    crimes = [
        CrimeResult(
            id=r["id"],
            crime=r["crime"],
            article=r["article"],
            categorie=r["categorie"],
            prison=r["penalty"]["prison"],
            amende=r["penalty"]["amende"],
            description=r["description"],
            score=r["score"]
        )
        for r in results
    ]
    
    return ChatResponse(
        response=response_text, 
        crimes=crimes,
        llm_provider=rag_service.llm_service.provider if rag_service.llm_service else "none"
    )


@app.get("/crimes")
async def list_crimes():
    """Get all crimes in the database"""
    return {"crimes": rag_service.crimes, "total": len(rag_service.crimes)}


@app.get("/crimes/{crime_id}")
async def get_crime(crime_id: int):
    """Get a specific crime by ID"""
    for crime in rag_service.crimes:
        if crime["id"] == crime_id:
            return crime
    raise HTTPException(status_code=404, detail="Crime not found")


@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "llm_provider": rag_service.llm_service.provider if rag_service.llm_service else "none",
        "search_method": "keyword-matching",
        "version": "LITE (512MB RAM)",
        "crimes_count": len(rag_service.crimes)
    }
