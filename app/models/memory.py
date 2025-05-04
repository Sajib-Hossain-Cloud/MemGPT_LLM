"""
Memory models for agent system.
Provides structured memory management for agents with different types of memory.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pydantic import BaseModel, Field

class MemoryItem(BaseModel):
    """Base class for a memory item"""
    id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    importance: float = 1.0  # 0.0 to 1.0, with 1.0 being most important
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "importance": self.importance,
            "metadata": self.metadata
        }

class FactMemory(MemoryItem):
    """Factual information to be remembered"""
    pass

class ConversationMemory(MemoryItem):
    """Memory of conversation exchanges"""
    sender: str
    receiver: str
    
    def to_dict(self) -> Dict:
        base_dict = super().to_dict()
        base_dict.update({
            "sender": self.sender,
            "receiver": self.receiver
        })
        return base_dict

class ReflectionMemory(MemoryItem):
    """Agent's reflections and insights based on past information"""
    related_memories: List[str] = Field(default_factory=list)
    
    def to_dict(self) -> Dict:
        base_dict = super().to_dict()
        base_dict.update({
            "related_memories": self.related_memories
        })
        return base_dict

class AgentMemory:
    """Main memory manager for an agent"""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.facts: Dict[str, FactMemory] = {}
        self.conversations: Dict[str, ConversationMemory] = {}
        self.reflections: Dict[str, ReflectionMemory] = {}
        
    def add_fact(self, fact_id: str, content: str, importance: float = 1.0, metadata: Dict = None) -> FactMemory:
        """Add a fact to memory"""
        fact = FactMemory(
            id=fact_id,
            content=content,
            importance=importance,
            metadata=metadata or {}
        )
        self.facts[fact_id] = fact
        return fact
        
    def add_conversation(self, conv_id: str, content: str, sender: str, 
                         receiver: str, importance: float = 1.0, metadata: Dict = None) -> ConversationMemory:
        """Add a conversation exchange to memory"""
        conversation = ConversationMemory(
            id=conv_id,
            content=content,
            sender=sender,
            receiver=receiver,
            importance=importance,
            metadata=metadata or {}
        )
        self.conversations[conv_id] = conversation
        return conversation
        
    def add_reflection(self, refl_id: str, content: str, 
                       related_memories: List[str] = None, 
                       importance: float = 1.0, metadata: Dict = None) -> ReflectionMemory:
        """Add a reflection to memory"""
        reflection = ReflectionMemory(
            id=refl_id,
            content=content,
            related_memories=related_memories or [],
            importance=importance,
            metadata=metadata or {}
        )
        self.reflections[refl_id] = reflection
        return reflection
        
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """
        Get memories relevant to the given query.
        This is a simple implementation - a production system would use 
        embeddings and semantic search.
        """
        # Combine all memories and sort by importance
        all_memories = list(self.facts.values()) + list(self.conversations.values()) + list(self.reflections.values())
        all_memories.sort(key=lambda x: x.importance, reverse=True)
        
        # Simple keyword matching (would be replaced with embeddings in production)
        query_terms = query.lower().split()
        scored_memories = []
        
        for memory in all_memories:
            score = 0
            for term in query_terms:
                if term in memory.content.lower():
                    score += 1
            if score > 0:
                scored_memories.append((memory, score))
        
        # Sort by relevance score then importance
        scored_memories.sort(key=lambda x: (x[1], x[0].importance), reverse=True)
        return [memory for memory, _ in scored_memories[:limit]]
    
    def save_to_file(self, file_path: str) -> None:
        """Save memory to a file"""
        memory_data = {
            "agent_id": self.agent_id,
            "facts": {k: v.to_dict() for k, v in self.facts.items()},
            "conversations": {k: v.to_dict() for k, v in self.conversations.items()},
            "reflections": {k: v.to_dict() for k, v in self.reflections.items()}
        }
        
        with open(file_path, 'w') as f:
            json.dump(memory_data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'AgentMemory':
        """Load memory from a file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        memory = cls(agent_id=data["agent_id"])
        
        # Load facts
        for fact_id, fact_data in data["facts"].items():
            memory.facts[fact_id] = FactMemory(**fact_data)
            
        # Load conversations
        for conv_id, conv_data in data["conversations"].items():
            # Make sure the conversation data has sender and receiver fields
            if "sender" not in conv_data or "receiver" not in conv_data:
                print(f"Warning: Conversation {conv_id} missing sender or receiver fields. Skipping.")
                continue
            memory.conversations[conv_id] = ConversationMemory(**conv_data)
            
        # Load reflections
        for refl_id, refl_data in data["reflections"].items():
            # Make sure reflection data has related_memories
            if "related_memories" not in refl_data:
                refl_data["related_memories"] = []
            memory.reflections[refl_id] = ReflectionMemory(**refl_data)
            
        return memory 