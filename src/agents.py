import json
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
from .tools import retrieve_sop_guidelines, retrieve_past_events
from .prompts import INFERENCE_PROMPT, CLASSIFICATION_PROMPT, RISK_ANALYSIS_PROMPT, MARKETING_PROMPT

# --- IMPORT THE NEW RENDERER ---
from .marketing_renderer import render_full_page

# --- CONFIGURATION ---
# Ensure you have run `ollama pull llama3.2`
llm = ChatOllama(model="llama3.2", temperature=0, format="json")
creative_llm = ChatOllama(model="llama3.2", temperature=0.7) # Higher temp for creativity

# --- HELPER ---
def clean_json_response(response_content: str) -> dict:
    """
    Llama 3.2 is good, but sometimes includes chatty preambles.
    This strips them ensuring we get just the JSON.
    """
    try:
        return json.loads(response_content)
    except json.JSONDecodeError:
        try:
            # Fallback: try to find the first { and last }
            start = response_content.find('{')
            end = response_content.rfind('}') + 1
            return json.loads(response_content[start:end])
        except:
            return {"error": "Failed to parse JSON", "raw": response_content}

# --- AGENT NODES ---

def inference_agent(state: AgentState) -> AgentState:
    """
    Agent 1: Event Context Inference
    Expands a simple name into a detailed structured profile.
    """
    print(f"--- AGENT: INFERENCE (Processing '{state['event_name']}') ---")
    
    # Format the prompt with the input event name
    prompt = INFERENCE_PROMPT.format(event_name=state['event_name'])
    
    response = llm.invoke([HumanMessage(content=prompt)])
    data = clean_json_response(response.content)
    
    return {"event_details": data}

def classification_agent(state: AgentState) -> AgentState:
    """
    Agent 2: Classification & Search Query Gen
    Converts details into normalized tags for the Vector DB.
    """
    print("--- AGENT: CLASSIFICATION ---")
    
    details = state['event_details']
    prompt = CLASSIFICATION_PROMPT.format(event_details_json=json.dumps(details))
    
    response = llm.invoke([HumanMessage(content=prompt)])
    data = clean_json_response(response.content)
    
    return {"search_queries": data.get("queries", [])}

def memory_retrieval_node(state: AgentState) -> AgentState:
    """
    Agent 3: Memory Retrieval (Functional Node)
    Not an LLM, but a deterministic tool caller.
    """
    print("--- AGENT: MEMORY RETRIEVAL ---")
    
    queries = state['search_queries']
    
    # 1. Get SOPs (Knowledge)
    sops = retrieve_sop_guidelines(queries)
    
    # 2. Get Past Events (Memory)
    memories = retrieve_past_events(queries)
    
    return {"knowledge_docs": sops, "past_memories": memories}

def risk_analysis_agent(state: AgentState) -> AgentState:
    """
    Agent 4: Risk Analysis
    Compares the Plan vs. SOPs vs. Memories to calculate risk.
    """
    print("--- AGENT: RISK ANALYSIS ---")
    
    details = state['event_details']
    sops = state['knowledge_docs']
    memories = state['past_memories']
    
    prompt = RISK_ANALYSIS_PROMPT.format(
        event_details_json=json.dumps(details),
        sops_json=json.dumps(sops),
        memories_json=json.dumps(memories)
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    data = clean_json_response(response.content)
    
    return {"risk_assessment": data}

def marketing_agent(state: AgentState) -> AgentState:
    """
    Agent 5: Marketing Generator
    Generates content blocks and wraps them in the beautiful renderer.
    """
    print("--- AGENT: MARKETING (Design Phase) ---")
    
    details = state['event_details']
    name = state['event_name']
    
    # Inject variables into the prompt
    final_prompt = MARKETING_PROMPT.format(
        event_name=name,
        event_details_json=json.dumps(details)
    )
    
    # Get the "Content Blocks" from Llama 3.2
    # We use creative_llm (higher temp) for better copy
    response = creative_llm.invoke([HumanMessage(content=final_prompt)])
    content_html = response.content
    
    # CLEANUP: Remove markdown backticks if the LLM accidentally added them
    content_html = content_html.replace("```html", "").replace("```", "")
    
    # RENDER: Merge content with the beautiful Glassmorphism template
    full_website_code = render_full_page(title=name, body_content=content_html)
    
    return {"marketing_code": full_website_code}