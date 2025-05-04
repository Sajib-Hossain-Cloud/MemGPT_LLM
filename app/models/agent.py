"""
Agent model for intelligent, memory-enabled LLM agents.
"""

import uuid
from typing import Dict, List, Optional, Any, Callable
import json
import os
from datetime import datetime

from app.models.memory import AgentMemory
from app.core.llm_service import LLMService

class AgentTool:
    """Tool that an agent can use to interact with the external world"""
    def __init__(self, name: str, description: str, function: Callable):
        self.name = name
        self.description = description
        self.function = function
        
    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool function"""
        return self.function(*args, **kwargs)

class Agent:
    """
    An intelligent agent with memory and reasoning capabilities.
    Inspired by the Letta/MemGPT approach.
    """
    def __init__(self, 
                agent_id: Optional[str] = None, 
                name: str = "Assistant",
                persona: str = "I am a helpful AI assistant.",
                llm_service: Optional[LLMService] = None):
        """
        Initialize a new agent or load an existing one.
        
        Args:
            agent_id: Unique identifier for the agent (generates new if None)
            name: Human-readable name for the agent
            persona: Description of the agent's personality and behavior
            llm_service: LLM service to use for generating responses
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.persona = persona
        self.memory = AgentMemory(agent_id=self.agent_id)
        self.llm_service = llm_service or LLMService()
        self.tools: Dict[str, AgentTool] = {}
        self.context_window_limit = 4000  # tokens, approximated
        self.conversation_history: List[Dict] = []
        
    def register_tool(self, name: str, description: str, function: Callable) -> None:
        """Register a tool that the agent can use"""
        self.tools[name] = AgentTool(name=name, description=description, function=function)
        
    def generate_response(self, user_input: str) -> str:
        """
        Generate a response to user input, using memory and persona.
        
        Args:
            user_input: The user's message
            
        Returns:
            str: The agent's response
        """
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Record in memory
        conv_id = f"conv_{len(self.conversation_history)}"
        self.memory.add_conversation(
            conv_id=conv_id,
            content=user_input,
            sender="user",
            receiver=self.agent_id,
            importance=0.8  # Default importance for user messages
        )
        
        # Retrieve relevant memories based on the input
        relevant_memories = self.memory.get_relevant_memories(user_input, limit=5)
        
        # Build context from memories and conversation history
        context = self._build_context(user_input, relevant_memories)
        
        # Generate system prompt with agent persona and context
        system_prompt = f"""
        {self.persona}
        
        You have access to your past memories and knowledge:
        {context}
        
        Available tools: {", ".join(self.tools.keys()) if self.tools else "None"}
        
        Base your response on your memories and persona. If you don't know something, 
        say so rather than making up information.
        """
        
        # Get response from LLM
        response = self.llm_service.generate_response(
            prompt=user_input,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        # Add response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Record in memory
        response_id = f"resp_{len(self.conversation_history)}"
        self.memory.add_conversation(
            conv_id=response_id,
            content=response,
            sender=self.agent_id,
            receiver="user",
            importance=0.7  # Default importance for agent responses
        )
        
        # Add a reflection about this exchange (simulate "thinking")
        self._add_reflection(user_input, response)
        
        return response
    
    def _build_context(self, query: str, memories: List) -> str:
        """
        Build a context string from memories, keeping within token limit.
        
        Args:
            query: The user's input query
            memories: List of relevant memories
            
        Returns:
            str: Formatted context string
        """
        context_parts = []
        
        # Add memories with their categories
        if memories:
            context_parts.append("Relevant memories:")
            for memory in memories:
                if hasattr(memory, 'related_memories'):
                    memory_type = "Reflection"
                    context_parts.append(f"- {memory_type}: {memory.content} (Related to: {', '.join(memory.related_memories)})")
                elif hasattr(memory, 'sender'):
                    memory_type = "Conversation"
                    context_parts.append(f"- {memory_type}: {memory.sender} → {memory.receiver}: {memory.content}")
                else:
                    memory_type = "Fact"
                    context_parts.append(f"- {memory_type}: {memory.content}")
        
        # Add recent conversation context (last 5 messages)
        if self.conversation_history:
            context_parts.append("\nRecent conversation:")
            recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
            for msg in recent_history:
                context_parts.append(f"- {msg['role'].capitalize()}: {msg['content']}")
        
        # Combine all parts, being mindful of approximate token count
        # This is a simple approximation - production systems would use a proper tokenizer
        context = "\n".join(context_parts)
        
        # Very simple token count approximation (4 chars ≈ 1 token)
        # In a real system, you'd use a proper tokenizer
        approx_token_count = len(context) // 4
        if approx_token_count > self.context_window_limit:
            # If over limit, truncate memories
            return "Context is too large to include all memories. Only the most relevant are included: \n" + \
                   "\n".join(context_parts[:5]) + "\n(additional context omitted due to token limits)"
        
        return context
    
    def _add_reflection(self, user_input: str, response: str) -> None:
        """
        Add a reflection based on the current exchange.
        This simulates the agent "thinking" about what happened.
        
        Args:
            user_input: User's message
            response: Agent's response
        """
        # In a full implementation, we'd use the LLM to generate a reflection
        # For this simplified version, we'll create a basic reflection
        reflection_prompt = f"""
        Consider the following exchange:
        User: {user_input}
        Agent: {response}
        
        Write a brief internal reflection about what the user might be trying to accomplish,
        what they might ask next, and what information would be helpful to remember for future interactions.
        """
        
        reflection_content = self.llm_service.generate_response(
            prompt=reflection_prompt,
            system_prompt="You are creating internal reflections for an AI assistant to help its memory. Be concise but insightful."
        )
        
        # Add to memory
        reflection_id = f"refl_{len(self.conversation_history)}"
        self.memory.add_reflection(
            refl_id=reflection_id,
            content=reflection_content,
            related_memories=[f"conv_{len(self.conversation_history)-1}", f"resp_{len(self.conversation_history)}"],
            importance=0.9  # Reflections have high importance
        )
    
    def save(self, directory: str = "./data/agents") -> str:
        """
        Save the agent state to disk.
        
        Args:
            directory: Directory to save agent data in
            
        Returns:
            str: Path to saved agent file
        """
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Save agent metadata
        agent_path = os.path.join(directory, f"{self.agent_id}")
        os.makedirs(agent_path, exist_ok=True)
        
        metadata = {
            "agent_id": self.agent_id,
            "name": self.name,
            "persona": self.persona,
            "created_at": datetime.now().isoformat(),
            "conversation_history": self.conversation_history
        }
        
        with open(os.path.join(agent_path, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save memory
        memory_path = os.path.join(agent_path, "memory.json")
        self.memory.save_to_file(memory_path)
        
        return agent_path
    
    @classmethod
    def load(cls, agent_id: str, directory: str = "./data/agents") -> 'Agent':
        """
        Load an agent from disk.
        
        Args:
            agent_id: ID of the agent to load
            directory: Directory containing agent data
            
        Returns:
            Agent: The loaded agent
        """
        agent_path = os.path.join(directory, agent_id)
        
        # Load metadata
        with open(os.path.join(agent_path, "metadata.json"), 'r') as f:
            metadata = json.load(f)
        
        # Create agent
        agent = cls(
            agent_id=metadata["agent_id"],
            name=metadata["name"],
            persona=metadata["persona"]
        )
        
        # Load conversation history
        agent.conversation_history = metadata["conversation_history"]
        
        # Load memory
        memory_path = os.path.join(agent_path, "memory.json")
        agent.memory = AgentMemory.load_from_file(memory_path)
        
        return agent 