from typing import List
from src.rag import query_knowledge_base

def retrieve_sop_guidelines(query_tags: list) -> List[str]:
    """
    Retrieves ONLY documents tagged as 'category': 'rule'.
    Used by the Risk Agent to find relevant Standard Operating Procedures.
    """
    # specific query formulation for rules
    query_string = f"Standard operating procedures, safety rules, and compliance policies for {', '.join(query_tags)}"
    
    # METADATA FILTERING: Only look for Rules
    # This ensures we don't accidentally retrieve a past event when we need a law.
    results = query_knowledge_base(
        query=query_string,
        filters={"category": "rule"}, 
        k=4
    )
    
    # Format for the LLM to easily distinguish sources
    formatted_docs = []
    for r in results:
        formatted_docs.append(f"[RULE SOURCE: {r['source']}]\n{r['content']}")
        
    return formatted_docs

def retrieve_past_events(query_tags: list) -> List[str]:
    """
    Retrieves ONLY documents tagged as 'category': 'memory'.
    Used by the Memory Agent to find historical precedents (Successes/Failures).
    """
    # specific query formulation for memories
    query_string = f"Past failures, incidents, lessons learned, and success stories regarding {', '.join(query_tags)}"
    
    # METADATA FILTERING: Only look for Memories
    results = query_knowledge_base(
        query=query_string,
        filters={"category": "memory"},
        k=3
    )
    
    # Format for the LLM
    formatted_memories = []
    for r in results:
        formatted_memories.append(f"[HISTORY LOG: {r['source']}]\n{r['content']}")
        
    return formatted_memories