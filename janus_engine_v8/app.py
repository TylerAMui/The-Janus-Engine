# app.py
import streamlit as st
import utils

# --- PAGE CONFIGURATION ---
utils.initialize_page_config("The Janus Engine v8.0 | Home")

st.title("🏛️ The Janus Engine v8.0")
st.write("An AI-powered pedagogical platform utilizing a meta-prompt architecture and a holistic lens library for intuitive, multi-perspective analysis.")

# --- SIDEBAR CONFIGURATION ---
# Render global settings (API Key)
utils.render_sidebar_settings()

# Add navigation reminder in the sidebar
st.sidebar.info("Navigate between analysis modes using the links above the settings.")

# --- MAIN PAGE CONTENT ---

st.header("Welcome to the Next Generation of Holistic Inquiry")

st.markdown("""
The Janus Engine (v8.0) leverages advanced AI (Gemini 1.5 Pro) to help you analyze creative works—text, images, or audio—from multiple perspectives simultaneously. 

It utilizes a unique **"General and Soldier"** architecture:
1. **The General (Meta-Prompt):** You provide a lens (e.g., "Marxist", "Jungian"). The AI first analyzes your input work and designs the optimal strategy (prompt) for applying that lens to that specific work.
2. **The Soldier (Execution):** The AI executes the custom-designed prompt, generating a deep, nuanced analysis.
""")

st.header("Analysis Modes")
st.markdown("Select an analysis mode from the sidebar to begin:")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔬 Single Lens")
    st.write("Analyze ONE work through ONE specific lens. Ideal for focused inquiry.")

    st.subheader("🎭 Dialectical Dialogue")
    st.write("Analyze ONE work through TWO lenses. The results are synthesized into a dialogue (Thesis vs. Antithesis), concluding with a Synthesis (Aufheben).")

with col2:
    st.subheader("🏛️ Symposium")
    st.write("Analyze ONE work through THREE or more lenses. The results are woven into a multi-participant discussion, offering a holistic view.")

    st.subheader("🔄 Comparative Synthesis")
    st.write("Analyze TWO different works through the SAME lens. Ideal for comparing how different works react to the same analytical framework.")

st.header("New in v8.0: Smart Selection")
st.markdown("""
In Dialectical and Symposium modes, you can now use **Smart Selection (Let Janus Choose)**. 

The "Analyst-in-Chief" (a specialized AI agent) will first analyze your input work and determine the most potent combination of lenses for the analysis, providing a justification for its choices before proceeding.
""")