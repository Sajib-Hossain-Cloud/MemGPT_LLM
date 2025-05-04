"""
Simple demonstration of the agent system.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from app.models.agent import Agent
from app.models.memory import AgentMemory

def main():
    """Run the demo"""
    print("=== Agent OS Demo ===")
    
    # Create a new agent
    agent = Agent(
        name="Demo Assistant",
        persona="I am a helpful AI assistant with a focus on being friendly and informative."
    )
    print(f"Created agent: {agent.name} (ID: {agent.agent_id})")
    
    # Add some initial facts to the agent's memory
    agent.memory.add_fact(
        fact_id="f1",
        content="The Earth is the third planet from the Sun.",
        importance=0.8
    )
    
    agent.memory.add_fact(
        fact_id="f2",
        content="Water freezes at 0 degrees Celsius at standard pressure.",
        importance=0.7
    )
    
    agent.memory.add_fact(
        fact_id="f3",
        content="The user is interested in science topics.",
        importance=0.9
    )
    
    print(f"Added initial facts to agent memory")
    
    # Simulate a conversation
    messages = [
        "Hello! Can you tell me something interesting about our planet?",
        "What temperature does water freeze at?",
        "Can you remember the first question I asked you?",
        "What do you know about me?",
        "Thank you for the information!"
    ]
    
    for i, message in enumerate(messages):
        print(f"\n[User]: {message}")
        
        # Generate response
        response = agent.generate_response(message)
        
        print(f"[Agent]: {response}")
        
        # Show some memory stats after each exchange
        print(f"\nMemory stats after exchange {i+1}:")
        print(f"- Facts: {len(agent.memory.facts)}")
        print(f"- Conversations: {len(agent.memory.conversations)}")
        print(f"- Reflections: {len(agent.memory.reflections)}")
    
    # Save the agent's state
    agent_path = agent.save()
    print(f"\nAgent state saved to: {agent_path}")
    
    # Show how we could later load the agent
    print("\nReloading agent to demonstrate persistence...")
    loaded_agent = Agent.load(agent.agent_id)
    print(f"Loaded agent: {loaded_agent.name} (ID: {loaded_agent.agent_id})")
    print(f"Memory stats for loaded agent:")
    print(f"- Facts: {len(loaded_agent.memory.facts)}")
    print(f"- Conversations: {len(loaded_agent.memory.conversations)}")
    print(f"- Reflections: {len(loaded_agent.memory.reflections)}")

if __name__ == "__main__":
    main() 