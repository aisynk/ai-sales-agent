# backend/agents/base_agent.py
from groq import Groq
import os
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Base class for all AI agents
    Provides common functionality that all agents need
    """
    
    def __init__(self, agent_name: str):
        """
        Initialize base agent
        
        Args:
            agent_name: Name of the agent (for logging and tracking)
        """
        self.agent_name = agent_name
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"  # Fast, capable model
        
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main function
        Each agent must implement this
        
        Args:
            context: Current conversation/customer context
            
        Returns:
            Result of agent's execution
        """
        pass
    
    async def _call_ai(
        self, 
        system_prompt: str, 
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Common method to call AI with prompts
        
        Args:
            system_prompt: Instructions for the AI
            user_message: User's input
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            
        Returns:
            AI's response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error calling AI: {str(e)}"
    
    def _log(self, message: str, level: str = "INFO"):
        """
        Log agent activity
        
        Args:
            message: What to log
            level: Log level (INFO, WARNING, ERROR)
        """
        print(f"[{level}] {self.agent_name}: {message}")
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract JSON from AI response that might have extra text
        
        Args:
            text: AI response that contains JSON
            
        Returns:
            Parsed JSON dict or None
        """
        import json
        import re
        
        # Try to find JSON in the text
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
        
        # If no JSON found, return None
        return None