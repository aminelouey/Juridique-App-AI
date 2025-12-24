"""
RAG Service - Recherche Augmentée par Génération
Utilise FAISS + Sentence Transformers + LLM pour des réponses naturelles
"""

import json
import os
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss

from .llm_service import LLMService


class RAGService:
    def __init__(self):
        self.crimes: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = None
        self.index: faiss.IndexFlatL2 = None
        self.model: SentenceTransformer = None
        self.llm_service: LLMService = None
        self.is_ready: bool = False
        
    async def initialize(self):
        """Initialize the RAG service: load data, create embeddings, build FAISS index, init LLM"""
        # Load crime data
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "code_penal.json")
        with open(data_path, "r", encoding="utf-8") as f:
            self.crimes = json.load(f)
        
        print(f"📚 Loaded {len(self.crimes)} crimes from database")
        
        # Load sentence transformer model (multilingual for French)
        print("🔄 Loading Sentence Transformer model...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ Embedding model loaded")
        
        # Create embeddings for each crime
        texts_to_embed = []
        for crime in self.crimes:
            # Combine relevant text fields for better matching
            text = f"{crime['crime']} {crime['article']} {crime['description']} {' '.join(crime['keywords'])}"
            texts_to_embed.append(text)
        
        print("🔄 Creating embeddings...")
        self.embeddings = self.model.encode(texts_to_embed, convert_to_numpy=True)
        print(f"✅ Created {len(self.embeddings)} embeddings")
        
        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
        print(f"✅ FAISS index built with {self.index.ntotal} vectors")
        
        # Initialize LLM service
        self.llm_service = LLMService()
        await self.llm_service.initialize()
        
        self.is_ready = True
        
    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant crimes using FAISS vector similarity
        """
        if not self.is_ready:
            return []
        
        # Encode the query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Prepare results with scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.crimes):
                crime = self.crimes[idx].copy()
                # Convert distance to similarity score (lower distance = higher similarity)
                max_distance = 100
                score = max(0, 1 - (distances[0][i] / max_distance))
                crime["score"] = round(score, 3)
                results.append(crime)
        
        return results
    
    def _build_context(self, results: List[Dict[str, Any]]) -> str:
        """Build context string from search results for LLM"""
        if not results:
            return "Aucune information trouvée dans la base de données juridique."
        
        context_parts = []
        for crime in results:
            part = f"""
📜 **{crime['crime']}** ({crime['article']})
- Catégorie: {crime['categorie']}
- Peine de prison: {crime['penalty']['prison']}
- Amende: {crime['penalty']['amende']}
- Description: {crime['description']}
"""
            context_parts.append(part)
        
        return "\n---\n".join(context_parts)
    
    async def generate_response(self, query: str, results: List[Dict[str, Any]]) -> str:
        """
        Generate a natural language response using LLM
        """
        context = self._build_context(results)
        response = await self.llm_service.generate_response(query, context)
        return response
    
    def format_response(self, results: List[Dict[str, Any]], original_query: str) -> str:
        """
        Fallback: Format the search results into a human-readable response (no LLM)
        """
        if not results:
            return """Je n'ai pas trouvé d'information correspondant à votre recherche dans le Code pénal algérien.

💡 Essayez avec des termes comme :
• Vol, meurtre, escroquerie
• Coups et blessures
• Faux témoignage
• Corruption, drogue"""

        response_parts = []
        
        for i, crime in enumerate(results):
            if i > 0:
                response_parts.append("\n━━━━━━━━━━━━━━━━━━━━━\n")
            
            part = f"""⚖️ **{crime['crime']}**

📜 {crime['article']}
📂 Catégorie: {crime['categorie']}

🔒 **Sanctions:**
• Prison: {crime['penalty']['prison']}"""
            
            if crime['penalty']['amende'] != 'N/A':
                part += f"\n• Amende: {crime['penalty']['amende']}"
            
            part += f"\n\n📝 {crime['description']}"
            
            if 'score' in crime:
                relevance = "🟢 Très pertinent" if crime['score'] > 0.7 else "🟡 Pertinent" if crime['score'] > 0.4 else "🟠 Partiellement pertinent"
                part += f"\n\n{relevance}"
            
            response_parts.append(part)
        
        return "".join(response_parts)
