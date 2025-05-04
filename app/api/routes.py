"""
API routes for the agent system.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()

# Request/Response Models
class CreateAgentRequest(BaseModel):
    name: str
    persona: str

class AgentResponse(BaseModel):
    agent_id: str
    name: str
    persona: str
    created_at: Optional[str] = None

class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    message: str
    agent_id: str

@router.post("/agents", response_model=AgentResponse)
async def create_agent(request: CreateAgentRequest):
    """Create a new agent"""
    agent = agent_service.create_agent(request.name, request.persona)
    agent_service.create_default_tools(agent.agent_id)
    
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "persona": agent.persona
    }

@router.get("/agents", response_model=List[AgentResponse])
async def list_agents():
    """List all available agents"""
    agents = agent_service.list_agents()
    return agents

@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    agent = agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found")
    
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "persona": agent.persona
    }

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    success = agent_service.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found")
    
    return {"message": f"Agent {agent_id} deleted successfully"}

@router.post("/agents/{agent_id}/message", response_model=MessageResponse)
async def send_message(agent_id: str, request: MessageRequest):
    """Send a message to an agent and get a response"""
    agent = agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found")
    
    response = agent_service.generate_response(agent_id, request.message)
    
    return {
        "message": response,
        "agent_id": agent_id
    } 