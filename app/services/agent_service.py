"""
Agent service for managing agent instances.
"""

import os
import json
from typing import Dict, List, Optional
import uuid

from app.models.agent import Agent
from app.core.llm_service import LLMService

class AgentService:
    """
    Service for managing multiple agents and their lifecycle.
    Similar to Letta's agent management system.
    """
    def __init__(self, storage_dir: str = "./data/agents"):
        self.storage_dir = storage_dir
        self.active_agents: Dict[str, Agent] = {}
        self.llm_service = LLMService()
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def create_agent(self, name: str, persona: str) -> Agent:
        """
        Create a new agent.
        
        Args:
            name: Name for the agent
            persona: Description of the agent's personality
            
        Returns:
            Agent: The newly created agent
        """
        agent = Agent(
            name=name,
            persona=persona,
            llm_service=self.llm_service
        )
        
        # Add to active agents
        self.active_agents[agent.agent_id] = agent
        
        # Save agent
        agent.save(self.storage_dir)
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID, loading it if needed.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Agent: The requested agent, or None if not found
        """
        # Check if agent is already active
        if agent_id in self.active_agents:
            return self.active_agents[agent_id]
        
        # Try to load from storage
        agent_path = os.path.join(self.storage_dir, agent_id)
        if not os.path.exists(agent_path):
            return None
        
        # Load agent
        agent = Agent.load(agent_id, self.storage_dir)
        self.active_agents[agent_id] = agent
        
        return agent
    
    def list_agents(self) -> List[Dict]:
        """
        List all available agents.
        
        Returns:
            List[Dict]: List of agent metadata
        """
        agents = []
        
        # Check for agent directories
        for item in os.listdir(self.storage_dir):
            item_path = os.path.join(self.storage_dir, item)
            metadata_path = os.path.join(item_path, "metadata.json")
            
            if os.path.isdir(item_path) and os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    agents.append(metadata)
                except Exception as e:
                    print(f"Error loading agent metadata from {metadata_path}: {e}")
        
        return agents
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: ID of the agent to delete
            
        Returns:
            bool: True if agent was deleted, False otherwise
        """
        # Remove from active agents
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
        
        # Delete from storage
        agent_path = os.path.join(self.storage_dir, agent_id)
        if not os.path.exists(agent_path):
            return False
        
        try:
            # Delete all files in the agent directory
            for filename in os.listdir(agent_path):
                file_path = os.path.join(agent_path, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            # Delete the directory
            os.rmdir(agent_path)
            return True
        except Exception as e:
            print(f"Error deleting agent {agent_id}: {e}")
            return False
    
    def save_all_agents(self) -> None:
        """Save all active agents to storage"""
        for agent in self.active_agents.values():
            agent.save(self.storage_dir)
            
    def generate_response(self, agent_id: str, user_input: str) -> str:
        """
        Generate a response from an agent.
        
        Args:
            agent_id: ID of the agent to use
            user_input: User's message
            
        Returns:
            str: Agent's response, or error message if agent not found
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return f"Error: Agent with ID {agent_id} not found"
        
        response = agent.generate_response(user_input)
        
        # Save agent after interaction
        agent.save(self.storage_dir)
        
        return response

    def create_default_tools(self, agent_id: str) -> None:
        """
        Add default tools to an agent.
        
        Args:
            agent_id: ID of the agent to add tools to
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return
        
        # Web search tool (simulated)
        def web_search(query: str) -> str:
            return f"Simulated web search results for: {query}"
        
        agent.register_tool(
            name="web_search",
            description="Search the web for information",
            function=web_search
        )
        
        # Calculator tool
        def calculator(expression: str) -> str:
            try:
                return str(eval(expression))
            except Exception as e:
                return f"Error calculating {expression}: {str(e)}"
        
        agent.register_tool(
            name="calculator",
            description="Evaluate a mathematical expression",
            function=calculator
        )
        
        # Save agent with new tools
        agent.save(self.storage_dir) 