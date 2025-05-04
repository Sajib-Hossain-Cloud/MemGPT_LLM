"""
Core LLM service implementation.
Handles interactions with the LLM provider (OpenAI).
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

class LLMService:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API"))
        self.model = "gpt-3.5-turbo"  # Default model

    def generate_response(self, 
                         prompt: str, 
                         system_prompt: Optional[str] = None,
                         temperature: float = 0.7) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user's input prompt
            system_prompt: Optional system prompt to set context
            temperature: Controls randomness in the response (0.0 to 1.0)
            
        Returns:
            str: The generated response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # For testing without an API key, return a mock response
        if not self.client.api_key or self.client.api_key.startswith("sk-your"):
            return self._generate_mock_response(prompt, system_prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._generate_mock_response(prompt, system_prompt)
    
    def _generate_mock_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a mock response for testing without an API key"""
        if "planet" in prompt.lower():
            return "The Earth is the third planet from the Sun and is the only astronomical object known to harbor life. About 71% of Earth's surface is water-covered."
        elif "water" in prompt.lower() or "freeze" in prompt.lower():
            return "Water freezes at 0 degrees Celsius (32 degrees Fahrenheit) at standard atmospheric pressure."
        elif "remember" in prompt.lower() or "first question" in prompt.lower():
            return "Yes, your first question was about our planet. You asked if I could tell you something interesting about it."
        elif "know about me" in prompt.lower():
            return "Based on our conversation, I know that you're interested in science topics, particularly about Earth and properties of water."
        elif "thank" in prompt.lower():
            return "You're welcome! I'm happy I could provide you with useful information. Feel free to ask if you have any other questions."
        else:
            return "I'm a simulated agent response for testing. This is a placeholder since no valid OpenAI API key was provided." 