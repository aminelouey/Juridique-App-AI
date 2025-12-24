"""
LLM Service - Génération de réponses avec Groq (LLaMA cloud)
"""

import os
from typing import Optional
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: str) -> str:
        pass


class GroqLLM(BaseLLM):
    """Groq Cloud LLM - Fast LLaMA inference"""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key
        self.model = model
        
    async def initialize(self):
        print(f"✅ Groq initialized with model: {self.model}")
    
    async def generate(self, prompt: str, context: str) -> str:
        import aiohttp
        
        system_prompt = """Tu es un assistant juridique algérien expert du Code pénal.
Tu dois:
- Répondre en français de manière claire et professionnelle
- Utiliser UNIQUEMENT les informations du contexte fourni
- Citer les articles de loi quand disponibles
- Mentionner les sanctions (prison et amende)
- NE JAMAIS inventer d'informations non présentes dans le contexte
- Ajouter un avertissement que c'est une information générale, pas un conseil juridique

Si le contexte ne contient pas l'information demandée, dis-le clairement."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Contexte juridique:\n{context}\n\nQuestion: {prompt}"}
        ]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 800
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error = await response.text()
                    return f"Erreur Groq ({response.status}): {error}"


class MockLLM(BaseLLM):
    """Mock LLM for testing without API keys"""
    
    async def initialize(self):
        print("✅ Mock LLM initialized (no API needed)")
    
    async def generate(self, prompt: str, context: str) -> str:
        return f"""📋 **Réponse à votre question:** "{prompt}"

{context}

---
⚠️ **Avertissement juridique:** Cette réponse est une information juridique générale basée sur le Code pénal algérien et ne constitue pas un avis juridique personnalisé. Pour toute situation spécifique, consultez un avocat."""


class LLMService:
    """Service principal pour la génération LLM - Utilise Groq Cloud"""
    
    def __init__(self):
        self.llm: Optional[BaseLLM] = None
        self.provider: str = "mock"
        
    async def initialize(self):
        """Initialize LLM - priorité à Groq"""
        groq_key = os.getenv("GROQ_API_KEY")
        
        if groq_key:
            self.llm = GroqLLM(api_key=groq_key)
            self.provider = "groq"
        else:
            self.llm = MockLLM()
            self.provider = "mock"
        
        await self.llm.initialize()
        print(f"🤖 LLM Provider: {self.provider}")
        
    async def generate_response(self, question: str, context: str) -> str:
        if not self.llm:
            await self.initialize()
        return await self.llm.generate(question, context)
