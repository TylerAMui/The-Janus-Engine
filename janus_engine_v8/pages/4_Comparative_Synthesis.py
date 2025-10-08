import streamlit as st
import utils
# v9.4b: LENS_ZEITGEIST constant is removed from utils.
from utils import WorkInput, VIEW_ERA, VIEW_LIBRARY

# --- CONSTANTS ---
# v9.4b: Define specific modes for this page including Zeitgeist
MODE_STANDARD = "Standard (Common Lens)"
MODE_ZEITGEIST = "Zeitgeist Simulation (Common Context)"

# --- CALLBACKS ---
def handle_comparative_mode_change():
    """Callback to clear selections when the mode changes (Standard vs Zeitgeist)."""
    # Reset the selection data structure
    st.session_state.comparative_selection = {'lens': None, 'persona': None, 'is_zeitgeist': False, 'zeitgeist_context': "", 'zeitgeist_persona': ""}
    # Clear specific UI widget states to prevent state conflicts
    if 'comparative_category_select' in st.session_state: del st.session_state.comparative_category_select
    if 'comparative_lens_select' in st.session_state: del st.session_state.comparative_lens_select


# --- PAGE SETUP ---
# v9.5a: Update version number
PAGE_TITLE = "Janus v9.5a | Comparative Synthesis"
utils.initialize_page_config(PAGE_TITLE)
st.title("4 | Comparative Synthesis (2 Works)")
st.write("Analyze TWO different works through the SAME analytical framework.")

# --- SIDEBAR (Global Settings Only) ---
utils.render_sidebar_settings()

# Initialize Session State
if 'comparative_selection' not in st.session_state:
    # v9.4b: Updated structure
    st.session_state.comparative_selection = {'lens': None, 'persona': None, 'is_zeitgeist': False, 'zeitgeist_context': "", 'zeitgeist_persona': ""}

if 'comparative_analysis_mode' not in st.session_state:
    # Stores the overall mode (Standard or Zeitgeist)
    st.session_state.comparative_analysis_mode = MODE_STANDARD

if 'work_input_comparative_a' not in st.session_state:
    st.session_state.work_input_comparative_a = WorkInput()
if 'work_input_comparative_b' not in st.session_state:
    st.session_state.work_input_comparative_b = WorkInput()

# --- MAIN PAGE LAYOUT ---
selection = st.session_state.comparative_selection
analysis_mode = st.session_state.comparative_analysis_mode

work_a = st.session_state.work_input_comparative_a
work_b = st.session_state.work_input_comparative_b
api_key = st.session_state.get("api_key", "")

# --- CONFIGURATION & LENS SELECTION (Hybrid Layout) ---
with st.expander("🔬 Configuration & Framework Selection", expanded=True):
    
    # v9.4b: Implement Zeitgeist Toggle as a Mode Switch
    st.markdown("#### Select Analysis Mode")
    activate_zeitgeist = st.toggle(
        "Activate Zeitgeist Simulation (Common Context)",
        value=(analysis_mode == MODE_ZEITGEIST),
        on_change=handle_comparative_mode_change,
        help="Switch from standard lens analysis to a simulation using a specific historical context applied to both works."
    )

    # Update the analysis mode and selection data based on the toggle
    if activate_zeitgeist:
        st.session_state.comparative_analysis_mode = MODE_ZEITGEIST
        analysis_mode = MODE_ZEITGEIST
        selection['is_zeitgeist'] = True
        # Ensure lens/persona are cleared when switching to Zeitgeist (handled by callback, but defensively set here too)
        selection['lens'] = None
        selection['persona'] = None
    else:
        st.session_state.comparative_analysis_mode = MODE_STANDARD
        analysis_mode = MODE_STANDARD
        selection['is_zeitgeist'] = False
        # Ensure Zeitgeist data is cleared when switching to Standard
        selection['zeitgeist_context'] = ""
        selection['zeitgeist_persona'] = ""

    st.markdown("---")

    # === ZEITGEIST MODE UI ===
    if analysis_mode == MODE_ZEITGEIST:
        st.info("🕰️ **Zeitgeist Simulation Activated.** Define the common historical context and witness persona.")
        st.subheader("Define the Common Zeitgeist")
        z_col1, z_col2 = st.columns(2)
        with z_col1:
            zeitgeist_context = st.text_area("Historical Context:", height=150, key="comparative_z_context", placeholder="Describe the era, location, and cultural climate...")
        with z_col2:
            zeitgeist_persona = st.text_area("Witness Persona:", height=150, key="comparative_z_persona", placeholder="Describe the witness analyzing the work...")
        
        # Update the selection object
        selection['zeitgeist_context'] = zeitgeist_context
        selection['zeitgeist_persona'] = zeitgeist_persona

    # === STANDARD MODE UI ===
    elif analysis_mode == MODE_STANDARD:
        st.caption("Select the common lens for comparison.")

        # v9.4b: Updated call (LENS_ZEITGEIST is removed)
        current_hierarchy, labels = utils.render_view_toggle_and_help("comparative")
        
        selected_persona = None

        col_cat, col_lens, col_persona = st.columns(3)

        category_options = list(current_hierarchy.keys())
        current_view_mode = st.session_state.get("comparative_view_mode", VIEW_LIBRARY)
        if current_view_mode != VIEW_ERA:
            category_options.sort()

        with col_cat:
            main_lens_category = st.selectbox(
                labels["category_label_single"], options=category_options, index=None,
                placeholder=labels["placeholder_text_single"], key="comparative_category_select"
            )

        if main_lens_category:
            with col_lens:
                lens_options = current_hierarchy[main_lens_category]
                
                # BUG FIX: THE INDEX METHOD
                current_lens_selection = st.session_state.get("comparative_lens_select")
                try:
                    index = lens_options.index(current_lens_selection)
                except (ValueError, TypeError):
                    index = None

                st.selectbox(
                    "2. Specific Lens:", options=lens_options, index=index,
                    placeholder="Select a specific lens...", key="comparative_lens_select",
                    # v9.4b: Terminology Refactor Integration
                    help=utils.get_lens_tooltip(st.session_state.get("comparative_lens_select"))
                )

        # Update the main selection dictionary with the value from the widget's state
        selection['lens'] = st.session_state.get("comparative_lens_select")
        current_selected_lens = selection['lens']

        if current_selected_lens:
            with col_persona:
                selected_persona = utils.render_persona_selector(current_selected_lens, "comparative")
        
        # Update Session State for Persona
        selection['persona'] = selected_persona


# --- INPUT & EXECUTION ---

# v9.4b: Determine readiness based on the mode
is_ready = False
if analysis_mode == MODE_ZEITGEIST:
    if selection['zeitgeist_context'] and selection['zeitgeist_persona']:
        is_ready = True
elif analysis_mode == MODE_STANDARD:
    if selection['lens']:
        is_ready = True

if is_ready:
    # Construct header text
    # v9.4b: Customize header for Zeitgeist or Standard Persona
    if analysis_mode == MODE_ZEITGEIST:
        header_text = "Analysis | Zeitgeist Simulation (Common Context)"
    else:
        header_text = f"Analysis | Lens: {selection['lens']}"
        if selection['persona']:
            header_text += f" | Persona: {selection['persona']}"
        
    st.header(header_text)
    
    # Input UI (Dual Input)
    st.subheader("Input Works for Comparison")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 🏛️ Work A")
        utils.handle_input_ui(work_a, st.container(border=True), "work_a")

    with col_b:
        st.markdown("### 🏛️ Work B")
        utils.handle_input_ui(work_b, st.container(border=True), "work_b")


    # Execution Button
    st.markdown("---")
    if st.button("Execute Analysis Engine", type="primary", use_container_width=True):
        # Validation (Basic checks)
        is_valid = True
        if not api_key:
            st.warning("Please enter your Gemini API Key in the sidebar (under 🔑 API Configuration).")
            is_valid = False

        if not work_a.is_ready():
            st.warning("Please provide the first creative work (Work A).")
            is_valid = False

        if not work_b.is_ready():
            st.warning("Please provide the second creative work (Work B).")
            is_valid = False

        # v9.4b: Zeitgeist Validation (Redundant check just before execution)
        if analysis_mode == MODE_ZEITGEIST:
            if not selection['zeitgeist_context'] or not selection['zeitgeist_persona']:
                st.warning("Please complete the Zeitgeist configuration (Context and Persona).")
                is_valid = False

        if is_valid:
            # --- Execution Block ---
            model = utils.get_model(api_key)
            if model:
                st.markdown("---")
                results_area = st.container()

                with results_area:
                    try:
                        # Call 1 (Concurrent): Analyze Work A and Work B
                        st.subheader(f"Step 1/2: Analyzing Work A and Work B concurrently...")
                        
                        # Create a list of async tasks
                        tasks = [
                            utils.async_generate_analysis(model, selection, work_a),
                            utils.async_generate_analysis(model, selection, work_b)
                        ]

                        # Run the tasks concurrently
                        results = utils.run_async_tasks(tasks)
                        analysis_a, analysis_b = results

                        # Call 2: Comparative Synthesis
                        if analysis_a and analysis_b:
                            st.subheader("Step 2/2: Comparative Synthesis")

                            st.info(f"**Synthesizing Comparison Between:** '{work_a.get_display_title()}' **and** '{work_b.get_display_title()}'")

                            with st.spinner("Generating comparative synthesis..."):
                                # v9.4b: Updated signature. Pass the full lens_config (selection).
                                synthesis_text = utils.generate_comparative_synthesis(
                                    model,
                                    selection, # v9.4b Updated
                                    analysis_a,
                                    work_a.get_display_title(),
                                    analysis_b,
                                    work_b.get_display_title()
                                )

                            if synthesis_text:
                                st.header("Comparative Synthesis Result")
                                st.markdown(synthesis_text)

                                # Display the raw analyses for reference
                                st.markdown("---")
                                st.subheader("Source Analyses (Reference)")
                                with st.expander(f"View Raw Analysis A: {work_a.get_display_title()}"):
                                    st.markdown(analysis_a)
                                with st.expander(f"View Raw Analysis B: {work_b.get_display_title()}"):
                                    st.markdown(analysis_b)
                        else:
                            st.error("Could not generate the initial analyses. Cannot proceed to comparison.")

                    finally:
                        # CRITICAL: Cleanup uploaded files after analysis is complete
                        work_a.cleanup_gemini_file()
                        work_b.cleanup_gemini_file()

else:
    if analysis_mode == MODE_ZEITGEIST:
        st.info("Please define the Historical Context and Witness Persona using the configuration options above.")
    else:
        st.info("Please select the common lens using the configuration options above.")
