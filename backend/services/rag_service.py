"""
RAG Service LITE - Version légère pour Render (512MB RAM)
Recherche par mots-clés + Groq LLM (sans Sentence Transformers)
"""

import json
import os
import re
from typing import List, Dict, Any

from .llm_service import LLMService


class RAGService:
    def __init__(self):
        self.crimes: List[Dict[str, Any]] = []
        self.llm_service: LLMService = None
        self.is_ready: bool = False
        
    async def initialize(self):
        """Initialize the RAG service: load data and init LLM"""
        # Load crime data
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "code_penal.json")
        with open(data_path, "r", encoding="utf-8") as f:
            self.crimes = json.load(f)
        
        print(f"📚 Loaded {len(self.crimes)} crimes from database")
        
        # Initialize LLM service (Groq)
        self.llm_service = LLMService()
        await self.llm_service.initialize()
        
        self.is_ready = True
        print("✅ RAG Service LITE initialized")
        
    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant crimes using keyword matching"""
        if not self.is_ready:
            return []
        
        query_lower = self._normalize_text(query)
        query_words = query_lower.split()
        
        # Score each crime based on keyword matches
        scored_crimes = []
        
        for crime in self.crimes:
            score = 0
            
            # Check crime name
            if self._normalize_text(crime['crime']) in query_lower:
                score += 10
            
            # Check keywords
            for keyword in crime['keywords']:
                keyword_norm = self._normalize_text(keyword)
                for word in query_words:
                    if len(word) > 2 and (keyword_norm in word or word in keyword_norm):
                        score += 5
            
            # Check description
            desc_norm = self._normalize_text(crime['description'])
            for word in query_words:
                if len(word) > 3 and word in desc_norm:
                    score += 2
            
            # Check article number
            numbers = re.findall(r'\d+', query)
            for num in numbers:
                if num in crime['article']:
                    score += 8
            
            if score > 0:
                crime_copy = crime.copy()
                crime_copy['score'] = min(score / 20, 1.0)  # Normalize to 0-1
                scored_crimes.append(crime_copy)
        
        # Sort by score descending
        scored_crimes.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_crimes[:top_k]
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        return (text.lower()
                .replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('ë', 'e')
                .replace('à', 'a').replace('â', 'a').replace('ä', 'a')
                .replace('î', 'i').replace('ï', 'i')
                .replace('ô', 'o').replace('ö', 'o')
                .replace('ù', 'u').replace('û', 'u').replace('ü', 'u')
                .replace('ç', 'c'))
    
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
        """Generate a natural language response using LLM"""
        context = self._build_context(results)
        response = await self.llm_service.generate_response(query, context)
        return response
    
    def format_response(self, results: List[Dict[str, Any]], original_query: str) -> str:
        """Fallback: Format without LLM"""
        if not results:
            return """Je n'ai pas trouvé d'information correspondant à votre recherche."""

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
            response_parts.append(part)
        
        return "".join(response_parts)
