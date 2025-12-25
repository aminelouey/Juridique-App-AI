"""
Database Service - SQLite pour le Code Pénal Algérien
"""

import aiosqlite
import os
import json
from typing import List, Dict, Any, Optional

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "code_penal.db")


class DatabaseService:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def initialize(self):
        """Initialize database and create tables if needed"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.connection = await aiosqlite.connect(self.db_path)
        
        # Create articles table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                texte TEXT NOT NULL,
                texte_arabe TEXT,
                categorie TEXT,
                section TEXT,
                chapitre TEXT,
                titre TEXT,
                livre TEXT,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster search
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_numero ON articles(numero)
        """)
        
        await self.connection.commit()
        print(f"📦 Database initialized: {self.db_path}")
    
    async def get_article_count(self) -> int:
        """Get total number of articles"""
        cursor = await self.connection.execute("SELECT COUNT(*) FROM articles")
        row = await cursor.fetchone()
        return row[0] if row else 0
    
    async def insert_article(self, article: Dict[str, Any]) -> int:
        """Insert a single article"""
        cursor = await self.connection.execute("""
            INSERT INTO articles (numero, texte, texte_arabe, categorie, section, chapitre, titre, livre)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.get('numero', ''),
            article.get('texte', ''),
            article.get('texte_arabe', ''),
            article.get('categorie', ''),
            article.get('section', ''),
            article.get('chapitre', ''),
            article.get('titre', ''),
            article.get('livre', '')
        ))
        await self.connection.commit()
        return cursor.lastrowid
    
    async def insert_articles_batch(self, articles: List[Dict[str, Any]]) -> int:
        """Insert multiple articles at once"""
        count = 0
        for article in articles:
            await self.insert_article(article)
            count += 1
        return count
    
    async def update_embedding(self, article_id: int, embedding: bytes):
        """Update embedding for an article"""
        await self.connection.execute("""
            UPDATE articles SET embedding = ? WHERE id = ?
        """, (embedding, article_id))
        await self.connection.commit()
    
    async def search_by_numero(self, numero: str) -> Optional[Dict[str, Any]]:
        """Search article by number"""
        cursor = await self.connection.execute("""
            SELECT id, numero, texte, texte_arabe, categorie, section, chapitre, titre, livre
            FROM articles WHERE numero LIKE ?
        """, (f"%{numero}%",))
        row = await cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'numero': row[1],
                'texte': row[2],
                'texte_arabe': row[3],
                'categorie': row[4],
                'section': row[5],
                'chapitre': row[6],
                'titre': row[7],
                'livre': row[8]
            }
        return None
    
    async def search_by_text(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search articles by text (simple LIKE search)"""
        cursor = await self.connection.execute("""
            SELECT id, numero, texte, texte_arabe, categorie, section, chapitre, titre, livre
            FROM articles 
            WHERE texte LIKE ? OR numero LIKE ?
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        rows = await cursor.fetchall()
        return [
            {
                'id': row[0],
                'numero': row[1],
                'texte': row[2],
                'texte_arabe': row[3],
                'categorie': row[4],
                'section': row[5],
                'chapitre': row[6],
                'titre': row[7],
                'livre': row[8]
            }
            for row in rows
        ]
    
    async def get_all_articles(self) -> List[Dict[str, Any]]:
        """Get all articles"""
        cursor = await self.connection.execute("""
            SELECT id, numero, texte, texte_arabe, categorie, section, chapitre, titre, livre
            FROM articles ORDER BY id
        """)
        rows = await cursor.fetchall()
        return [
            {
                'id': row[0],
                'numero': row[1],
                'texte': row[2],
                'texte_arabe': row[3],
                'categorie': row[4],
                'section': row[5],
                'chapitre': row[6],
                'titre': row[7],
                'livre': row[8]
            }
            for row in rows
        ]
    
    async def get_articles_without_embeddings(self) -> List[Dict[str, Any]]:
        """Get articles that don't have embeddings yet"""
        cursor = await self.connection.execute("""
            SELECT id, numero, texte FROM articles WHERE embedding IS NULL
        """)
        rows = await cursor.fetchall()
        return [{'id': row[0], 'numero': row[1], 'texte': row[2]} for row in rows]
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
