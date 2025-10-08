import streamlit as st
import utils
import re
# v9.4b: LENS_ZEITGEIST constant is removed from utils.
from utils import WorkInput, SELECT_MANUAL, SELECT_SMART, SELECTION_MODES, VIEW_ERA, VIEW_LIBRARY

# --- CONSTANTS ---
# v9.4b: Define specific modes for this page including Zeitgeist
MODE_STANDARD = "Standard (Lens vs. Lens)"
MODE_ZEITGEIST = "Zeitgeist Simulation (Era vs. Era)"

# --- CALLBACKS ---
def handle_dialectical_mode_change():
    """Callback to clear selections when the mode changes (Standard vs Zeitgeist, or Manual vs Smart)."""
    st.session_state.dialectical_selection_data = []
    # Also clear specific UI widget states if necessary to ensure a clean slate when switching modes
    if 'dialectic_cat_a' in st.session_state: del st.session_state.dialectic_cat_a
    if 'dialectic_lens_a' in st.session_state: del st.session_state.dialectic_lens_a
    if 'dialectic_cat_b' in st.session_state: del st.session_state.dialectic_cat_b
    if 'dialectic_lens_b' in st.session_state: del st.session_state.dialectic_lens_b

# --- PAGE SETUP ---
# v9.5a: Update version number
PAGE_TITLE = "Janus v9.5a | Dialectical Dialogue"
utils.initialize_page_config(PAGE_TITLE)
st.title("2 | Dialectical Dialogue (2 Perspectives)")
st.write("Analyze ONE work through TWO perspectives (Thesis vs. Antithesis), synthesized into a dialogue.")

# --- SIDEBAR (Global Settings Only) ---
utils.render_sidebar_settings()

# Initialize Session State for this page
if 'dialectical_selection_data' not in st.session_state:
    # Stores the final configuration data: [config_a, config_b]
    st.session_state.dialectical_selection_data = []
if 'dialectical_selection_method' not in st.session_state:
    # Stores the method within Standard mode (Manual or Smart)
    st.session_state.dialectical_selection_method = SELECT_MANUAL
if 'dialectical_analysis_mode' not in st.session_state:
    # Stores the overall mode (Standard or Zeitgeist)
    st.session_state.dialectical_analysis_mode = MODE_STANDARD
if 'work_input_dialectical' not in st.session_state:
    st.session_state.work_input_dialectical = WorkInput()

# --- MAIN PAGE LAYOUT ---
# v9.4b: Renamed variables for clarity
selection_method = st.session_state.dialectical_selection_method
analysis_mode = st.session_state.dialectical_analysis_mode

work_a = st.session_state.work_input_dialectical
api_key = st.session_state.get("api_key", "")

# --- CONFIGURATION & LENS SELECTION (Hybrid Layout) ---
with st.expander("🔬 Configuration & Perspective Selection", expanded=True):
    # v9.4b: Implement Zeitgeist Toggle as a Mode Switch
    st.markdown("#### Select Analysis Mode")
    activate_zeitgeist = st.toggle(
        "Activate Zeitgeist Simulation (Era vs. Era)",
        value=(analysis_mode == MODE_ZEITGEIST),
        on_change=handle_dialectical_mode_change,
        help="Switch from standard lens analysis to a simulation comparing two distinct historical contexts."
    )

    # Update the analysis mode based on the toggle
    if activate_zeitgeist:
        st.session_state.dialectical_analysis_mode = MODE_ZEITGEIST
        analysis_mode = MODE_ZEITGEIST
    else:
        st.session_state.dialectical_analysis_mode = MODE_STANDARD
        analysis_mode = MODE_STANDARD

    st.markdown("---")

    # Initialize empty configurations (v9.4b structure)
    # Include optional keys for structural consistency even if empty
    config_a = {'lens': None, 'persona': None, 'is_zeitgeist': False, 'zeitgeist_context': "", 'zeitgeist_persona': ""}
    config_b = {'lens': None, 'persona': None, 'is_zeitgeist': False, 'zeitgeist_context': "", 'zeitgeist_persona': ""}
    is_valid = True # Track validity within the configuration block

    # === ZEITGEIST MODE UI ===
    if analysis_mode == MODE_ZEITGEIST:
        st.info("🕰️ **Zeitgeist Simulation Activated.** Define the two historical contexts and witness personas.")
        
        config_a['is_zeitgeist'] = True
        config_b['is_zeitgeist'] = True

        col_a, col_b = st.columns(2)

        with col_a:
            with st.container(border=True):
                st.markdown("🏛️ **Perspective A (Thesis)**")
                config_a['zeitgeist_context'] = st.text_area("Historical Context A:", height=150, key="dialectic_z_context_a", placeholder="Describe the era, location, and cultural climate...")
                config_a['zeitgeist_persona'] = st.text_area("Witness Persona A:", height=150, key="dialectic_z_persona_a", placeholder="Describe the witness analyzing the work...")

        with col_b:
            with st.container(border=True):
                st.markdown("🏛️ **Perspective B (Antithesis)**")
                config_b['zeitgeist_context'] = st.text_area("Historical Context B:", height=150, key="dialectic_z_context_b", placeholder="Describe the era, location, and cultural climate...")
                config_b['zeitgeist_persona'] = st.text_area("Witness Persona B:", height=150, key="dialectic_z_persona_b", placeholder="Describe the witness analyzing the work...")

        # Validation for Zeitgeist
        # 1. Check for identical configurations
        if (config_a['zeitgeist_context'] and config_a['zeitgeist_persona'] and 
            config_a['zeitgeist_context'] == config_b['zeitgeist_context'] and 
            config_a['zeitgeist_persona'] == config_b['zeitgeist_persona']):
            st.warning("Cannot run identical Zeitgeist simulations. Please ensure the Context or Persona differs between A and B.")
            is_valid = False

        # 2. Check for completeness (don't show warning here, just invalidate)
        if (not config_a['zeitgeist_context'] or not config_a['zeitgeist_persona'] or
            not config_b['zeitgeist_context'] or not config_b['zeitgeist_persona']):
            is_valid = False

    # === STANDARD MODE UI ===
    elif analysis_mode == MODE_STANDARD:
        st.radio(
            "Selection Method:",
            SELECTION_MODES,
            horizontal=True,
            key="dialectical_selection_method", 
            on_change=handle_dialectical_mode_change
        )
        
        # Update selection_method based on the radio button state (it might have changed via callback)
        selection_method = st.session_state.dialectical_selection_method

        if selection_method == SELECT_MANUAL:
            st.markdown("---")
            # v9.4b: Updated call (LENS_ZEITGEIST is removed)
            current_hierarchy, labels = utils.render_view_toggle_and_help("dialectical")
            st.caption("Select two independent lenses (Thesis and Antithesis).")

            category_options = list(current_hierarchy.keys())
            current_view_mode = st.session_state.get("dialectical_view_mode", VIEW_LIBRARY)
            if current_view_mode != VIEW_ERA:
                category_options.sort()

            col_a, col_b = st.columns(2)

            # --- Lens A (Thesis) Pathway ---
            with col_a:
                with st.container(border=True):
                    st.markdown("🏛️ **Lens A (Thesis)**")
                    category_a = st.selectbox(
                        labels["category_label_single"], options=category_options, index=None,
                        placeholder=labels["placeholder_text_single"], key="dialectic_cat_a"
                    )
                    if category_a:
                        lens_options_a = current_hierarchy[category_a]
                        
                        # BUG FIX: THE INDEX METHOD (Handles state stability when switching categories)
                        current_lens_a_selection = st.session_state.get("dialectic_lens_a")
                        try:
                            index_a = lens_options_a.index(current_lens_a_selection)
                        except (ValueError, TypeError):
                            index_a = None
                        
                        st.selectbox(
                            "2. Specific Lens A:", options=lens_options_a, index=index_a,
                            placeholder="Select lens...", key="dialectic_lens_a",
                            # v9.4b: Terminology Refactor Integration (Implicitly handled as tooltips use the UI names)
                            help=utils.get_lens_tooltip(st.session_state.get("dialectic_lens_a"))
                        )
                    
                    config_a['lens'] = st.session_state.get("dialectic_lens_a")
                    
                    if config_a['lens']:
                        config_a['persona'] = utils.render_persona_selector(config_a['lens'], "dialectic_a")

            # --- Lens B (Antithesis) Pathway ---
            with col_b:
                with st.container(border=True):
                    st.markdown("🏛️ **Lens B (Antithesis)**")
                    category_b = st.selectbox(
                        labels["category_label_single"], options=category_options, index=None,
                        placeholder=labels["placeholder_text_single"], key="dialectic_cat_b"
                    )
                    if category_b:
                        lens_options_b = current_hierarchy[category_b]

                        # BUG FIX: THE INDEX METHOD
                        current_lens_b_selection = st.session_state.get("dialectic_lens_b")
                        try:
                            index_b = lens_options_b.index(current_lens_b_selection)
                        except (ValueError, TypeError):
                            index_b = None

                        st.selectbox(
                            "2. Specific Lens B:", options=lens_options_b, index=index_b,
                            placeholder="Select lens...", key="dialectic_lens_b",
                            help=utils.get_lens_tooltip(st.session_state.get("dialectic_lens_b"))
                        )
                    
                    config_b['lens'] = st.session_state.get("dialectic_lens_b")

                    if config_b['lens']:
                        config_b['persona'] = utils.render_persona_selector(config_b['lens'], "dialectic_b")

            # Validation for Manual Selection
            if config_a['lens'] and config_b['lens']:
                if (config_a['lens'] == config_b['lens']) and (config_a['persona'] == config_b['persona']):
                    st.warning("Cannot use the same Lens and Persona for both A and B. Please specify different personas or lenses.")
                    is_valid = False
            else:
                is_valid = False # Lenses not yet selected
        
        elif selection_method == SELECT_SMART:
            st.info("🤖 **Smart Selection Activated.** The Janus 'Analyst-in-Chief' will choose the two most potent lenses after analyzing your input.")
            # In Smart mode, the configuration data is determined during execution, not here.
            is_valid = False # Set to False because config_a/b are empty, but execution logic handles this.

    # Final Session State Update (centralized)
    # We only update the session state if the configuration is valid AND we are NOT in Smart Selection mode.
    if is_valid and (analysis_mode == MODE_ZEITGEIST or (analysis_mode == MODE_STANDARD and selection_method == SELECT_MANUAL)):
        st.session_state.dialectical_selection_data = [config_a, config_b]
    else:
        # Clear the data if invalid or if using Smart Selection
        st.session_state.dialectical_selection_data = []


# --- INPUT & EXECUTION ---

# Determine if we are ready to proceed
is_ready_for_input = False
header_text = "Analysis | "

# Read the session state AFTER the configuration block has run
current_manual_data = st.session_state.dialectical_selection_data

# v9.4b: Updated readiness logic to handle the new modes
if analysis_mode == MODE_ZEITGEIST:
    if current_manual_data and len(current_manual_data) == 2:
        is_ready_for_input = True
        header_text += "Zeitgeist Simulation (A vs. B)"
    else:
        st.info("Please complete the configuration for both Zeitgeist Perspective A and B above.")

elif analysis_mode == MODE_STANDARD:
    if selection_method == SELECT_MANUAL:
        if current_manual_data and len(current_manual_data) == 2:
            is_ready_for_input = True
            # Construct header text including personas if present
            data_a = current_manual_data[0]
            data_b = current_manual_data[1]
            
            # v9.4b: Helper to format display text (simplified as Zeitgeist is handled separately now)
            def format_display(data):
                text = f"{data['lens']}"
                if data['persona']:
                    text += f" (as {data['persona']})"
                return text

            header_text += f"{format_display(data_a)} vs. {format_display(data_b)}"

        else:
            st.info("Please select and configure Lens A (Thesis) and Lens B (Antithesis) using the options above.")

    elif selection_method == SELECT_SMART:
        is_ready_for_input = True
        header_text += "Smart Selection"


if is_ready_for_input:
    st.header(header_text)
    
    # Input UI
    st.subheader("Input Work")
    utils.handle_input_ui(work_a, st.container(border=True), "work_dialectical")

    # Execution Button
    st.markdown("---")
    if st.button("Execute Analysis Engine", type="primary", use_container_width=True):
        # Validation
        is_valid = True
        if not api_key:
            st.warning("Please enter your Gemini API Key in the sidebar (under 🔑 API Configuration).")
            is_valid = False

        if not work_a.is_ready():
            st.warning("Please provide the creative work to be analyzed.")
            is_valid = False

        if is_valid:
            # --- Execution Block ---
            # Initialize standard model for analysis/synthesis
            model_standard = utils.get_model(api_key, json_mode=False)
            
            if model_standard:
                st.markdown("---")
                results_area = st.container()
                # This list will hold the final execution data (lens config)
                final_execution_data = []

                with results_area:
                    try:
                        # --- Step 0: Determine Execution Data (Smart Selection or Manual/Zeitgeist) ---
                        # v9.4b: Check if Smart Selection is active (only possible in Standard mode)
                        if analysis_mode == MODE_STANDARD and selection_method == SELECT_SMART:
                            # Initialize JSON model specifically for Smart Selection
                            model_json = utils.get_model(api_key, json_mode=True)
                            if model_json:
                                smart_selection_status = st.status("Executing Smart Selection...", expanded=True)
                                # Returns a list of lens names
                                smart_lenses = utils.analyst_in_chief(
                                    model_json, 
                                    work_a, 
                                    required_count=2, 
                                    status_container=smart_selection_status
                                )
                                smart_selection_status.update(label="Smart Selection Complete.", state="complete")
                                
                                if smart_lenses:
                                    # Transform smart selection (lenses only) into execution data format (v9.4b structure)
                                    final_execution_data = [{'lens': lens, 'persona': None, 'is_zeitgeist': False} for lens in smart_lenses]
                                    
                            else:
                                st.error("Failed to initialize JSON model for Smart Selection.")
                        else:
                            # Use the data directly from session state (Manual Mode or Zeitgeist Mode)
                            final_execution_data = st.session_state.dialectical_selection_data

                        # Check if we have a valid selection (manual or smart)
                        if not final_execution_data or len(final_execution_data) != 2:
                            # Error message already displayed by analyst_in_chief if it failed, or configuration was incomplete.
                            st.stop()
                        
                        # --- Steps 1-3: Analysis and Synthesis ---
                        data_a = final_execution_data[0]
                        data_b = final_execution_data[1]

                        # v9.4b: Determine display name for steps
                        display_name_a = data_a.get('lens') or "Zeitgeist A"
                        display_name_b = data_b.get('lens') or "Zeitgeist B"

                        # Call 1 (Concurrent): Generate Thesis and Antithesis
                        st.subheader(f"Step 1/2: Generating Thesis ({display_name_a}) and Antithesis ({display_name_b}) concurrently...")
                        
                        # Create a list of async tasks
                        tasks = [
                            utils.async_generate_analysis(model_standard, data_a, work_a),
                            utils.async_generate_analysis(model_standard, data_b, work_a)
                        ]
                        
                        # Run the tasks concurrently
                        results = utils.run_async_tasks(tasks)
                        analysis_a, analysis_b = results

                        # Call 2: Synthesis
                        if analysis_a and analysis_b:
                            st.subheader("Step 2/2: Synthesis (Aufheben)")

                            def get_synthesis_clarification(analysis_text, config_data):
                                """Creates a clear string with both the persona and the lens they represent."""
                                persona_name = "Unknown Persona"
                                # Extract the definitive persona name from the analysis header
                                match = re.search(r"^### Analysis by (.*)", analysis_text.strip())
                                if match:
                                    persona_name = match.group(1).strip()

                                # For Zeitgeist, the persona is the entire description
                                if config_data.get('is_zeitgeist'):
                                    return persona_name
                                
                                lens_name = config_data.get('lens', 'Unknown Lens')

                                # Avoid redundant labels like "The Structuralist (Structuralism)"
                                if lens_name.lower() in persona_name.lower():
                                    return persona_name
                                
                                return f"{persona_name} ({lens_name})"

                            # Generate the full clarification strings
                            persona_a_display = get_synthesis_clarification(analysis_a, data_a)
                            persona_b_display = get_synthesis_clarification(analysis_b, data_b)
                            
                            st.info(f"**Synthesizing:** {persona_a_display} **vs.** {persona_b_display}")

                            with st.spinner("Synthesizing the dialogue..."):
                                # Pass the full data dictionaries
                                dialogue_text = utils.generate_dialectical_synthesis(
                                    model_standard,
                                    data_a,
                                    analysis_a,
                                    data_b,
                                    analysis_b,
                                    work_a.get_display_title()
                                )

                            if dialogue_text:
                                st.header("Dialectical Dialogue Result")
                                st.markdown(dialogue_text)

                                # Display the raw analyses for reference
                                st.markdown("---")
                                st.subheader("Source Analyses (Reference)")
                                with st.expander(f"View Raw Analysis A: {display_name_a}"):
                                    st.markdown(analysis_a)
                                with st.expander(f"View Raw Analysis B: {display_name_b}"):
                                    st.markdown(analysis_b)
                        else:
                            st.error("Could not generate the initial analyses. Cannot proceed to synthesis.")
                    
                    finally:
                        # CRITICAL: Cleanup uploaded files after ALL analysis is complete
                        work_a.cleanup_gemini_file()
