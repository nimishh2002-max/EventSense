from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """
    The shared state of the Event Intelligence Graph.
    Data flows from top to bottom, being enriched by each agent.
    """
    # 1. Input
    event_name: str
    
    # 2. Inference Agent Output
    event_details: Dict[str, Any]  # {type, scale, venue_requirements, duration}
    
    # 3. Classification Agent Output
    search_queries: List[str]      # Normalized tags for vector DB lookup
    
    # 4. Memory Retrieval Output (Tool)
    knowledge_docs: List[str]      # SOPs, Rules (RAG)
    past_memories: List[Dict]      # Past failure/success logs
    
    # 5. Risk Agent Output
    risk_assessment: Dict[str, Any] # {score: int, level: str, reasoning: str}
    
    # 6. Marketing Agent Output
    marketing_code: str            # HTML content