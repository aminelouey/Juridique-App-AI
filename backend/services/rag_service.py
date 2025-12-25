"""
RAG Service avec Jina AI Embeddings + SQLite + Groq LLM
Version production pour Render (< 200MB RAM)
"""

import os
from typing import List, Dict, Any, Optional

from .database import DatabaseService
from .embedding_service import JinaEmbeddingService
from .llm_service import LLMService


class RAGService:
    def __init__(self):
        self.db: DatabaseService = None
        self.embedding_service: JinaEmbeddingService = None
        self.llm_service: LLMService = None
        self.is_ready: bool = False
        self.use_embeddings: bool = False  # Fallback to keyword search if no embeddings
        
    async def initialize(self):
        """Initialize all services"""
        # Initialize database
        self.db = DatabaseService()
        await self.db.initialize()
        
        article_count = await self.db.get_article_count()
        print(f"📚 {article_count} articles dans la base de données")
        
        # Initialize embedding service (if key is available)
        jina_key = os.getenv("JINA_API_KEY")
        if jina_key:
            self.embedding_service = JinaEmbeddingService(jina_key)
            self.use_embeddings = True
            print("🔍 Jina AI Embeddings activé")
        else:
            print("⚠️ JINA_API_KEY non défini - recherche par mots-clés")
        
        # Initialize LLM service (Groq)
        self.llm_service = LLMService()
        await self.llm_service.initialize()
        
        self.is_ready = True
        print("✅ RAG Service initialisé")
    
    @property
    def articles(self) -> List[Dict[str, Any]]:
        """Compatibility property for old code"""
        return []
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant articles using embeddings or keywords"""
        if not self.is_ready:
            return []
        
        # Try embedding search first
        if self.use_embeddings and self.embedding_service:
            results = await self._search_by_embedding(query, top_k)
            if results:
                return results
        
        # Fallback to keyword search
        return await self._search_by_keywords(query, top_k)
    
    async def _search_by_embedding(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search using Jina AI embeddings and cosine similarity"""
        try:
            # Get query embedding
            query_embedding = await self.embedding_service.get_query_embedding(query)
            if not query_embedding:
                return []
            
            # Get all articles with embeddings
            cursor = await self.db.connection.execute("""
                SELECT id, numero, texte, texte_arabe, categorie, section, embedding
                FROM articles WHERE embedding IS NOT NULL
            """)
            rows = await cursor.fetchall()
            
            if not rows:
                return []
            
            # Calculate similarities
            results = []
            for row in rows:
                article_embedding = JinaEmbeddingService.bytes_to_embedding(row[6])
                similarity = JinaEmbeddingService.cosine_similarity(query_embedding, article_embedding)
                
                results.append({
                    'id': row[0],
                    'numero': row[1],
                    'texte': row[2],
                    'texte_arabe': row[3],
                    'categorie': row[4],
                    'section': row[5],
                    'score': similarity,
                    'crime': row[1],  # Compatibility
                    'article': row[1],
                    'description': row[2],
                    'penalty': {
                        'prison': self._extract_penalty(row[2]),
                        'amende': self._extract_amende(row[2])
                    }
                })
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Embedding search error: {e}")
            return []
    
    async def _search_by_keywords(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search using keyword matching"""
        query_lower = self._normalize_text(query)
        query_words = [w for w in query_lower.split() if len(w) > 2]
        
        # Get all articles
        all_articles = await self.db.get_all_articles()
        
        scored_results = []
        for article in all_articles:
            score = 0
            texte_lower = self._normalize_text(article['texte'])
            numero_lower = article['numero'].lower()
            categorie_lower = self._normalize_text(article.get('categorie', ''))
            
            # Check article number
            for word in query_words:
                if word.isdigit() and word in numero_lower:
                    score += 15
            
            # Check category
            for word in query_words:
                if word in categorie_lower:
                    score += 8
            
            # Check text content
            for word in query_words:
                if word in texte_lower:
                    score += 3
            
            if score > 0:
                scored_results.append({
                    'id': article['id'],
                    'numero': article['numero'],
                    'texte': article['texte'],
                    'texte_arabe': article.get('texte_arabe', ''),
                    'categorie': article.get('categorie', ''),
                    'section': article.get('section', ''),
                    'score': min(score / 30, 1.0),
                    'crime': article['numero'],
                    'article': article['numero'],
                    'description': article['texte'],
                    'penalty': {
                        'prison': self._extract_penalty(article['texte']),
                        'amende': self._extract_amende(article['texte'])
                    }
                })
        
        # Sort by score
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results[:top_k]
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        return (text.lower()
                .replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('ë', 'e')
                .replace('à', 'a').replace('â', 'a').replace('ä', 'a')
                .replace('î', 'i').replace('ï', 'i')
                .replace('ô', 'o').replace('ö', 'o')
                .replace('ù', 'u').replace('û', 'u').replace('ü', 'u')
                .replace('ç', 'c'))
    
    def _extract_penalty(self, text: str) -> str:
        """Extract prison penalty from article text"""
        import re
        # Patterns for prison/réclusion
        patterns = [
            r'réclusion perpétuelle',
            r'réclusion à temps de (\d+) à (\d+) ans?',
            r'emprisonnement de (\d+) (?:mois|jours?) à (\d+) (?:ans?|mois)',
            r'emprisonnement d\'un an à (\d+) ans?',
            r'puni de mort',
            r'puni de la mort',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Voir article"
    
    def _extract_amende(self, text: str) -> str:
        """Extract fine from article text"""
        import re
        pattern = r'amende de ([\d\.\s]+) (?:DA|dinars?)? à ([\d\.\s]+) (?:DA|dinars?)?'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)} à {match.group(2)} DA"
        return "N/A"
    
    def _build_context(self, results: List[Dict[str, Any]]) -> str:
        """Build context string for LLM"""
        if not results:
            return "Aucune information trouvée dans le Code Pénal."
        
        context_parts = []
        for article in results:
            part = f"""
📜 **{article['numero']}** ({article.get('categorie', 'Code Pénal')})
{article['texte'][:500]}{'...' if len(article['texte']) > 500 else ''}
"""
            context_parts.append(part)
        
        return "\n---\n".join(context_parts)
    
    async def generate_response(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Generate natural language response using LLM"""
        context = self._build_context(results)
        response = await self.llm_service.generate_response(query, context)
        return response
    
    def format_response(self, results: List[Dict[str, Any]], original_query: str) -> str:
        """Fallback format without LLM"""
        if not results:
            return "Je n'ai pas trouvé d'information correspondant à votre recherche dans le Code Pénal."
        
        response_parts = []
        for i, article in enumerate(results):
            if i > 0:
                response_parts.append("\n━━━━━━━━━━━━━━━━━━━━━\n")
            
            part = f"""⚖️ **{article['numero']}**
📂 {article.get('categorie', 'Code Pénal')}

📝 {article['texte'][:400]}{'...' if len(article['texte']) > 400 else ''}
"""
            response_parts.append(part)
        
        return "".join(response_parts)
