import sys
import os
import streamlit as st

# Ensure we can import from the src directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- STREAMLIT CONFIG ---
st.set_page_config(
    page_title="Agentic Event Intel",
    page_icon="🧠",
    layout="wide"
)

# --- IMPORT HANDLER ---
# This block handles the connection to your backend and catches dependency errors
try:
    from src.graph import build_graph
except ImportError as e:
    # Check specifically for the common Pydantic/LangChain version mismatch
    if "pydantic_v1" in str(e) or "langchain_core" in str(e):
        st.error("❌ **Dependency Mismatch Detected**")
        st.markdown("""
        Your `langgraph` and `langchain-core` versions are out of sync.
        
        **Please run this command in your terminal to fix it:**
        ```bash
        pip install -U langgraph langchain-core langchain-ollama langchain-chroma pydantic
        ```
        Then restart this app.
        """)
        st.stop()
    else:
        # Re-raise other import errors (like missing src files)
        raise e

# --- CACHED RESOURCES ---
@st.cache_resource
def load_agent_system():
    """
    Load the graph once and cache it. 
    This prevents re-initializing the LLM/VectorDB on every button click.
    """
    return build_graph()

# --- CSS STYLING ---
st.markdown("""
    <style>
    .risk-high { color: #ff4b4b; font-weight: bold; }
    .risk-medium { color: #ffa700; font-weight: bold; }
    .risk-low { color: #21c354; font-weight: bold; }
    .main-header { font-size: 2.5rem; font-weight: 700; color: #4B4B4B; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- MAIN APP LOGIC ---
def main():
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Status")
        
        # Initialize System
        if 'app_initialized' not in st.session_state:
            with st.spinner("Booting Agents & Memory..."):
                try:
                    app = load_agent_system()
                    st.session_state['agent_app'] = app
                    st.session_state['app_initialized'] = True
                    st.success("Agents Online")
                    st.success("Memory (RAG) Connected")
                except Exception as e:
                    st.error(f"System Offline: {e}")
                    st.stop()
        else:
            st.success("System Ready")

        st.markdown("---")
        st.info("💡 **Architecture:**\n\n- **Orchestrator:** LangGraph\n- **Reasoning:** Llama 3.2\n- **Memory:** ChromaDB + mxbai-large\n- **Interface:** Streamlit")
        
        if st.button("🧹 Clear Cache / Reset"):
            st.cache_resource.clear()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Main Content
    st.markdown('<div class="main-header">🧠 AgenticAI Event Intelligence</div>', unsafe_allow_html=True)
    st.markdown("An autonomous multi-agent system for risk-aware event planning.")

    # Input Section
    col1, col2 = st.columns([3, 1])
    with col1:
        event_name = st.text_input("Describe your event:", placeholder="e.g., Midnight Rooftop Jazz Charity Fundraiser")
    with col2:
        st.write("") # Spacer
        st.write("") # Spacer
        run_btn = st.button("🚀 Analyze Event", type="primary", use_container_width=True)

    # Execution Logic
    if run_btn and event_name:
        # Retrieve the app from session state
        app = st.session_state.get('agent_app')
        
        if not app:
            st.error("Agents are not initialized. Please reset the app.")
            st.stop()

        with st.status("🤖 Orchestrating Agents...", expanded=True) as status:
            try:
                # 1. Run the Graph
                inputs = {"event_name": event_name}
                
                st.write("🕵️ Inference Agent: Expanding context & normalizing data...")
                # Invoke the graph
                result = app.invoke(inputs)
                
                st.write("🧠 Memory Agent: Retrieving SOPs & Historical Failures...")
                st.write("⚠️ Risk Agent: Calculating safety score...")
                st.write("🎨 Marketing Agent: Coding landing page...")
                
                # Extract Data
                details = result.get('event_details', {})
                risk = result.get('risk_assessment', {})
                memories = result.get('past_memories', [])
                marketing = result.get('marketing_code', '')
                
                status.update(label="Analysis Complete", state="complete", expanded=False)
                
            except Exception as e:
                status.update(label="Workflow Failed", state="error")
                st.error(f"Error executing graph: {e}")
                st.stop()

        # --- RESULTS DASHBOARD ---
        st.divider()
        
        # Create Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Decision Intelligence", "🧠 Institutional Memory", "🎨 Marketing Preview"])
        
        # TAB 1: OVERVIEW & RISK
        with tab1:
            row1_col1, row1_col2 = st.columns([1, 1])
            
            with row1_col1:
                st.subheader("Event Profile")
                st.json(details)
            
            with row1_col2:
                st.subheader("Risk Assessment")
                score = risk.get('score', 0)
                level = risk.get('level', 'Unknown')
                
                # Dynamic Color for Risk Display
                color = "green"
                if isinstance(score, int):
                    if score > 60: color = "red"
                    elif score > 20: color = "orange"
                
                st.markdown(f"### Score: :{color}[{score}/100] ({level})")
                st.markdown(f"**Reasoning:** {risk.get('reasoning')}")
                st.info(f"🛡️ **Mitigation:** {risk.get('mitigation_plan')}")

        # TAB 2: MEMORY (RAG)
        with tab2:
            st.subheader("📚 Retrieved Knowledge & History")
            st.markdown("These documents were retrieved from the vector database to ground the AI's decision.")
            
            if memories:
                for idx, mem in enumerate(memories):
                    with st.expander(f"Evidence #{idx+1} (Source: RAG)"):
                        st.markdown(mem)
            else:
                st.warning("No specific historical data found for this event type.")

        # TAB 3: MARKETING
        with tab3:
            st.subheader("Generated Landing Page")
            
            col_d1, col_d2 = st.columns([1, 4])
            with col_d1:
                # Download Button
                st.download_button(
                    label="📥 Download HTML",
                    data=marketing,
                    file_name=f"{event_name.replace(' ', '_').lower()}.html",
                    mime="text/html"
                )
            
            # Preview (Sandboxed iframe)
            st.caption("Live Preview:")
            import streamlit.components.v1 as components
            components.html(marketing, height=600, scrolling=True)

if __name__ == "__main__":
    main()