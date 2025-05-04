"""
Visualization service for the Agent Development Environment (ADE).
Provides functionality to visualize agent memory and reasoning.
"""

import json
from typing import Dict, List, Any, Optional
import os
from datetime import datetime
import uuid

class ADEVisualization:
    """
    Visualization service for the Agent Development Environment.
    In a production system, this would generate interactive visualizations.
    For this demo, we'll generate JSON that could be consumed by a frontend.
    """
    
    def __init__(self, output_dir: str = "./data/visualizations"):
        """Initialize the visualization service"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def visualize_agent_memory(self, agent_memory: Any) -> Dict:
        """
        Generate a visualization of an agent's memory.
        
        Args:
            agent_memory: The agent's memory object
            
        Returns:
            Dict: Visualization data that could be rendered by a frontend
        """
        # Extract memory items and organize by type
        memory_viz = {
            "agent_id": agent_memory.agent_id,
            "facts": [],
            "conversations": [],
            "reflections": [],
            "memory_stats": {
                "total_items": 0,
                "facts_count": len(agent_memory.facts),
                "conversations_count": len(agent_memory.conversations),
                "reflections_count": len(agent_memory.reflections)
            },
            "visualization_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat()
        }
        
        # Process facts
        for fact_id, fact in agent_memory.facts.items():
            memory_viz["facts"].append({
                "id": fact_id,
                "content": fact.content,
                "importance": fact.importance,
                "created_at": fact.created_at.isoformat() if hasattr(fact.created_at, 'isoformat') else fact.created_at,
                "metadata": fact.metadata
            })
        
        # Process conversations
        for conv_id, conv in agent_memory.conversations.items():
            memory_viz["conversations"].append({
                "id": conv_id,
                "content": conv.content,
                "sender": conv.sender,
                "receiver": conv.receiver,
                "importance": conv.importance,
                "created_at": conv.created_at.isoformat() if hasattr(conv.created_at, 'isoformat') else conv.created_at,
                "metadata": conv.metadata
            })
        
        # Process reflections
        for refl_id, refl in agent_memory.reflections.items():
            memory_viz["reflections"].append({
                "id": refl_id,
                "content": refl.content,
                "related_memories": refl.related_memories,
                "importance": refl.importance,
                "created_at": refl.created_at.isoformat() if hasattr(refl.created_at, 'isoformat') else refl.created_at,
                "metadata": refl.metadata
            })
        
        # Update total count
        memory_viz["memory_stats"]["total_items"] = (
            memory_viz["memory_stats"]["facts_count"] +
            memory_viz["memory_stats"]["conversations_count"] +
            memory_viz["memory_stats"]["reflections_count"]
        )
        
        # Save visualization data
        self._save_visualization(memory_viz, "memory")
        
        return memory_viz
    
    def visualize_agent_reasoning(self, 
                                 agent_id: str, 
                                 user_input: str, 
                                 response: str, 
                                 context: str,
                                 memory_items: List) -> Dict:
        """
        Generate a visualization of an agent's reasoning process.
        
        Args:
            agent_id: The agent's ID
            user_input: The user's input message
            response: The agent's response
            context: The context used for generation
            memory_items: The memory items used in the response
            
        Returns:
            Dict: Visualization data that could be rendered by a frontend
        """
        # Create reasoning visualization
        reasoning_viz = {
            "agent_id": agent_id,
            "user_input": user_input,
            "agent_response": response,
            "context_used": context,
            "memory_items_used": [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in memory_items],
            "visualization_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat()
        }
        
        # Save visualization data
        self._save_visualization(reasoning_viz, "reasoning")
        
        return reasoning_viz
    
    def _save_visualization(self, data: Dict, viz_type: str) -> None:
        """
        Save visualization data to a file.
        
        Args:
            data: Visualization data
            viz_type: Type of visualization (memory, reasoning, etc.)
        """
        filename = f"{viz_type}_{data['visualization_id']}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_visualizations(self, agent_id: Optional[str] = None, viz_type: Optional[str] = None) -> List[Dict]:
        """
        Get saved visualizations.
        
        Args:
            agent_id: Optional filter by agent ID
            viz_type: Optional filter by visualization type
            
        Returns:
            List[Dict]: List of visualization data
        """
        visualizations = []
        
        for filename in os.listdir(self.output_dir):
            if not filename.endswith('.json'):
                continue
                
            # Check if the filename matches the requested type
            if viz_type and not filename.startswith(f"{viz_type}_"):
                continue
                
            filepath = os.path.join(self.output_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Filter by agent ID if specified
                if agent_id and data.get("agent_id") != agent_id:
                    continue
                    
                visualizations.append(data)
            except Exception as e:
                print(f"Error loading visualization from {filepath}: {e}")
        
        # Sort by creation time, most recent first
        visualizations.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return visualizations 