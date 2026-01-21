import sys
import os

# Ensure the parent directory is in the path so we can run this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents import (
    inference_agent,
    classification_agent,
    memory_retrieval_node,
    risk_analysis_agent,
    marketing_agent
)

def build_graph():
    """
    Constructs the Event Intelligence Agent Graph.
    Flow: Inference -> Classify -> Memory -> Risk -> Marketing -> END
    """
    # 1. Initialize the Graph with our typed State
    workflow = StateGraph(AgentState)

    # 2. Add Nodes (Register the agent functions)
    workflow.add_node("inference", inference_agent)
    workflow.add_node("classify", classification_agent)
    workflow.add_node("memory", memory_retrieval_node)
    workflow.add_node("risk", risk_analysis_agent)
    workflow.add_node("marketing", marketing_agent)

    # 3. Define the Edges (The Logic Flow)
    
    # Start at Inference (Input: Event Name -> Output: Event Details)
    workflow.set_entry_point("inference")
    
    # Inference -> Classification (Output: Search Queries)
    workflow.add_edge("inference", "classify")
    
    # Classification -> Memory Retrieval (Output: SOPs & Past Events)
    workflow.add_edge("classify", "memory")
    
    # Memory -> Risk Analysis (Output: Risk Score & Mitigation)
    workflow.add_edge("memory", "risk")
    
    # Risk -> Marketing (Output: HTML Landing Page)
    workflow.add_edge("risk", "marketing")
    
    # Marketing -> End
    workflow.add_edge("marketing", END)

    # 4. Compile the Graph
    app = workflow.compile()
    return app

# --- EXECUTABLE BLOCK FOR TESTING ---
if __name__ == "__main__":
    print("🚀 Booting Agentic Event Intelligence System...")
    
    # Initialize the graph
    app = build_graph()
    
    # Test Input
    user_input = "Midnight Rooftop Jazz Charity"
    print(f"📝 Input Event: '{user_input}'\n")
    
    # Run the graph
    inputs = {"event_name": user_input}
    result = app.invoke(inputs)
    
    # Display Results
    print("\n✅ WORKFLOW COMPLETE. RESULTS:\n")
    
    print(f"🔹 INFERRED TYPE: {result['event_details'].get('type', 'Unknown')}")
    print(f"🔹 ESTIMATED CROWD: {result['event_details'].get('estimated_attendees', 0)}")
    
    print("\n⚠️ RISK ASSESSMENT:")
    risk = result.get('risk_assessment', {})
    print(f"   Score: {risk.get('score')}/100")
    print(f"   Level: {risk.get('level')}")
    print(f"   Reasoning: {risk.get('reasoning')}")
    
    print("\n🧠 MEMORY RETRIEVAL:")
    print(f"   Fetched {len(result['past_memories'])} historical records.")
    
    print("\n🎨 MARKETING WEBSITE GENERATED:")
    # Print first 200 chars of HTML just to prove it worked
    html_preview = result.get('marketing_code', '')[:200].replace('\n', ' ')
    print(f"   {html_preview}...")
    
    # Optional: Save the HTML to file to view it
    with open("event_landing_page.html", "w") as f:
        f.write(result.get('marketing_code', ''))
    print("\n📂 Saved website to 'event_landing_page.html'")