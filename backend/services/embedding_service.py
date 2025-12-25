"""
Jina AI Embedding Service - API cloud pour embeddings
"""

import aiohttp
import os
import struct
from typing import List, Optional


class JinaEmbeddingService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        self.api_url = "https://api.jina.ai/v1/embeddings"
        self.model = "jina-embeddings-v3"  # Multilingual, supports French & Arabic
        self.dimensions = 1024  # Default dimensions
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for a single text"""
        if not self.api_key:
            print("⚠️ JINA_API_KEY not set")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": [text],
            "task": "retrieval.passage"  # Optimized for search
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["data"][0]["embedding"]
                    else:
                        error = await response.text()
                        print(f"❌ Jina API error ({response.status}): {error}")
                        return None
        except Exception as e:
            print(f"❌ Jina API exception: {e}")
            return None
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Get embeddings for multiple texts (batch)"""
        if not self.api_key:
            print("⚠️ JINA_API_KEY not set")
            return [None] * len(texts)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": texts,
            "task": "retrieval.passage"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [item["embedding"] for item in data["data"]]
                    else:
                        error = await response.text()
                        print(f"❌ Jina API batch error ({response.status}): {error}")
                        return [None] * len(texts)
        except Exception as e:
            print(f"❌ Jina API exception: {e}")
            return [None] * len(texts)
    
    async def get_query_embedding(self, query: str) -> Optional[List[float]]:
        """Get embedding for a search query (different task type)"""
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": [query],
            "task": "retrieval.query"  # Optimized for queries
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["data"][0]["embedding"]
                    else:
                        return None
        except Exception as e:
            print(f"❌ Jina query error: {e}")
            return None
    
    @staticmethod
    def embedding_to_bytes(embedding: List[float]) -> bytes:
        """Convert embedding list to bytes for SQLite storage"""
        return struct.pack(f'{len(embedding)}f', *embedding)
    
    @staticmethod
    def bytes_to_embedding(data: bytes) -> List[float]:
        """Convert bytes back to embedding list"""
        count = len(data) // 4  # float is 4 bytes
        return list(struct.unpack(f'{count}f', data))
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)
