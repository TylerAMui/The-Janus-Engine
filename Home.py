import streamlit as st
import utils

# --- PAGE CONFIGURATION ---
# v10.2: Update page title
utils.initialize_page_config("Janus | Home")

# v10.2: Update version number and title
st.title("🏛️ The Janus Engine")
st.write("An AI-powered pedagogical platform utilizing a dynamic, multi-stage adaptive architecture for intuitive, multi-perspective analysis.")

# Beta disclaimer
st.info("🧪 **Beta Software** - This is an experimental AI analysis platform. Expect occasional bugs. [Report issues here](https://github.com/TylerAMui/The-Janus-Engine/issues)")

# --- SIDEBAR CONFIGURATION ---
# v10.2: Render workflow settings (API configuration moved to main page)
utils.render_sidebar_settings()

st.sidebar.info("Use the links above to navigate between analysis modes. Workflow settings are below.")

# --- MAIN PAGE CONTENT ---

# v10.2: API Configuration at top (prerequisite for all functionality)
utils.render_api_configuration()

st.header("Welcome to the Next Generation of Holistic Inquiry")

# v10.1: Update architecture description
st.markdown("""
The Janus Engine (v10.2) leverages advanced AI (Gemini 2.5 Pro and Flash-Lite) to help you analyze creative works—text, images, audio, or video—from multiple perspectives simultaneously.

It utilizes a **"Generative & Adaptive"** four-stage architecture:
""")

# Architecture stages with tooltips
st.markdown("**1. Triage (Optional)** :grey_question:", help=utils.get_tooltip("triage"))
st.markdown("**2. Theoretician** :grey_question:", help=utils.get_tooltip("theoretician"))
st.markdown("**3. Specialist Swarm** :grey_question:", help=utils.get_tooltip("specialist_swarm"))
st.markdown("**4. Master Synthesizer** :grey_question:", help=utils.get_tooltip("synthesizer"))

st.markdown("""
This architecture intelligently generates and executes bespoke analytical strategies tailored to the artwork, moving beyond static frameworks.
""")

st.header("Analysis Modes")
st.markdown("Select an analysis mode from the navigation menu to begin:")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔬 Single Lens")
    st.write("Analyze ONE work through ONE specific lens or the Zeitgeist Simulation. Ideal for focused inquiry and iterative refinement.")

    st.subheader("🎭 Dialectical Dialogue")
    st.write("Analyze ONE work through TWO lenses or two distinct Zeitgeist simulations. The results are synthesized into a dialogue (Thesis vs. Antithesis).")

with col2:
    st.subheader("🏛️ Symposium")
    st.write("Analyze ONE work through THREE or more perspectives (including Zeitgeist). The results are woven into a multi-participant discussion.")

    st.subheader("🔄 Comparative Synthesis")
    st.write("Analyze TWO different works through the SAME lens or the same Zeitgeist context. Ideal for comparison.")

# v10.2: Update Header and description of new features
st.header("New in v10.2: Export System & Centralized Configuration")
st.markdown("""
Version 10.2 adds comprehensive export functionality and reorganizes API configuration for future scalability.

**Key Features:**

1. **📥 Export Functionality (Critical Feature):**
   - Download analysis results as **Markdown** (.md) or **Plain Text** (.txt)
   - Available on all 4 analysis pages immediately after results display
   - Comprehensive metadata included: timestamp, analysis type/mode, lens/persona config, work details, API usage metrics
   - Dual metadata tracking for Comparative analysis (Work A + Work B)
   - Timestamp-based file naming prevents overwrites

2. **📖 In-App Documentation Page:**
   - Complete user guide accessible as 6th navigation page
   - Covers architecture, analysis modes, lens library, configuration, best practices, troubleshooting
   - Version history and changelog
   - No need to leave the app or read repository documentation

3. **🔑 Centralized API Configuration (Scalability Upgrade):**
   - API configuration moved from sidebar to Home page
   - Infrastructure setup separated from workflow preferences
   - **Multi-provider framework ready:** Designed to support OpenAI, Anthropic, Cohere, and other providers in future releases
   - Sidebar now dedicated to workflow settings only (Analysis Mode)
   - Visual status indicators (✅ Configured / ❌ Not Configured)

---

### Previous Features (v10.1)

**Multi-Dimensional Filtering & Lens Consolidation:**

1. **Unified Multi-Dimensional Filter System (UX Enhancement):**
   - All analysis pages now feature the Library's advanced filtering: **Discipline × Function × Era**
   - Filter by academic discipline (Art History, Philosophy, Theology, etc.)
   - Filter by functional tier (What it is / How it works / Why it matters)
   - Filter by historical era (Ancient → Contemporary)
   - All filters are optional and work in combination for precise lens discovery
   - Makes navigating 157+ lenses intuitive and manageable

2. **Three-Tier Persona Selection (Analytical Control):**
   - **(All Personas - AI Decides):** Default mode - AI selects the most appropriate historical figure from the persona pool based on content analysis
   - **(No Persona - Generic Title):** Uses an archetypal title specific to the framework (e.g., "The Republican Theorist" for Republicanism)
   - **Specific Persona:** Lock analysis to a particular historical figure from the pool

3. **Era-Spanning Political Ideology Lenses (Historical Depth):**
   - Added **Republicanism**, **Democracy**, **Conservatism**, and **Socialism** with persona pools spanning multiple eras
   - Example: Republicanism includes Cicero (Ancient), Jefferson & Madison (Early Modern Period), Lincoln (19th Century), and Arendt (20th Century)
   - AI can select personas from different historical periods to match the work's context

4. **Multi-Discipline Lens Membership (Contextual Analysis):**
   - Lenses can now appear in multiple discipline categories
   - Example: **Stoicism** appears in both "Ethics" and "Individual Philosophy" for context-specific analysis
   - **Post-Structuralism** spans Metaphysics, Literary Theory, Individual Philosophy, and Sociology
   - Provides nuanced analysis based on the user's selected discipline filter

5. **Lens Consolidation (Library Refinement):**
   - Consolidated overly specific "person-isms" into broader frameworks with persona pools:
     - **Deontology** (from Kantianism) - now includes Kant, W.D. Ross, Christine Korsgaard, Thomas Nagel
     - **Egoism** (from Objectivism) - now includes Ayn Rand, Max Stirner, Friedrich Nietzsche
     - **Idealism** (from Platonism + Hegelian Idealism) - now includes Plato, Berkeley, Hegel, Royce, Bradley
     - **Psychoanalytic Theory** (from Freudianism, Jungian Analysis, Lacanianism) - toolkit with 11 sub-primers covering all three schools
     - **Buddhism** (from Chan/Zen, Theravāda, Tibetan variants) - toolkit with 3 sub-primers for each tradition
     - **Christian Theology** (from Catholic, Protestant, Liberation Theology) - toolkit with 3 sub-primers for each tradition
   - Reduces granularity bloat while preserving analytical depth through persona pools and sub-primers toolkits
   - Total lens count optimized from ~163 to 157 lenses

6. **Film Movement Lenses (Visual Culture):**
   - Added 10 cinema movement lenses: Cinema Novo, Dogme 95, Film Noir, French New Wave, German Expressionism, Italian Neorealism, New Hollywood, Soviet Montage, Third Cinema

7. **Mythology Lens Reorganization:**
   - Renamed all mythology lenses for better readability (e.g., "Norse Myth", "Greco-Roman Myth", "Egyptian Myth")

*(This builds upon the Adaptive Architecture (v10.0), General's Toolkit (v9.5a), UX Overhaul/Zeitgeist Mode (v9.4b), Foundation Patch (v9.4a), Great Library (v9.3), Refinement Loop (v9.2), Primers/Video Analysis (v9.1), and the Hybrid UI/Persona Pools (v9.0)).*
""")