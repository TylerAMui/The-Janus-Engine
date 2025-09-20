# pages/3_Symposium.py
import streamlit as st
import utils
from lenses import get_filtered_lenses
from utils import WorkInput, SELECT_MANUAL, SELECT_SMART, SELECTION_MODES

# --- PAGE SETUP ---
PAGE_TITLE = "Janus v8.0 | Symposium"
utils.initialize_page_config(PAGE_TITLE)
st.title("3 | Symposium (3+ Lenses)")
st.write("Analyze ONE work through THREE or more lenses, synthesized into a discussion.")

# Constants for this mode
MIN_SELECTIONS = 3

# --- SIDEBAR ---
utils.render_sidebar_settings()

# Initialize Session State for this page
if 'symposium_selection' not in st.session_state:
    st.session_state.symposium_selection = []
if 'symposium_selection_mode' not in st.session_state:
    st.session_state.symposium_selection_mode = SELECT_MANUAL
if 'symposium_smart_count' not in st.session_state:
    # Default count for Smart Selection
    st.session_state.symposium_smart_count = 3 

# Initialize WorkInput object in session state
if 'work_input_symposium' not in st.session_state:
    st.session_state.work_input_symposium = WorkInput()

# --- LENS SELECTION (Sidebar) ---
with st.sidebar:
    st.markdown("---")
    st.subheader("🔬 Lens Selection")

    # v8.0 Feature: Smart Selection Toggle
    selection_mode = st.radio(
        "Selection Method:",
        SELECTION_MODES,
        index=SELECTION_MODES.index(st.session_state.symposium_selection_mode), # Reflect current state
        key="symposium_selection_mode_radio"
    )
    
    # Update session state if the radio changes
    if selection_mode != st.session_state.symposium_selection_mode:
        st.session_state.symposium_selection_mode = selection_mode
        # Clear selections when switching modes
        st.session_state.symposium_selection = []
        # Rerun to ensure UI updates correctly
        st.rerun()

    if st.session_state.symposium_selection_mode == SELECT_MANUAL:
        # Render the standard Library/Workshop interface
        current_hierarchy, labels = utils.render_lens_selection_interface("symposium")
        st.caption(f"Select {MIN_SELECTIONS} or more lenses for the symposium.")
        
        lens_label = f"2. Select Lenses (Minimum {MIN_SELECTIONS}):"

        # Stage 1: Category/Tier Selection
        selected_categories = st.multiselect(
            labels["category_label_multi"],
            options=sorted(list(current_hierarchy.keys())),
            placeholder=labels["placeholder_text_multi"],
            key="symposium_category_select"
        )

        # Stage 2: Filtered Lens Selection
        if selected_categories:
            # Dynamically populate the lens options
            available_lenses = get_filtered_lenses(current_hierarchy, selected_categories)
            
            # Use a container for visual nesting
            with st.container(border=True):
                selected_lenses = st.multiselect(
                    lens_label,
                    options=available_lenses,
                    placeholder="Choose lenses from selected categories...",
                    key="symposium_lens_select"
                )
            
            # Validation for minimum selection
            if len(selected_lenses) > 0 and len(selected_lenses) < MIN_SELECTIONS:
                st.warning(f"Please select at least {MIN_SELECTIONS} lenses.")
                st.session_state.symposium_selection = [] # Reset selection if invalid
            elif len(selected_lenses) >= MIN_SELECTIONS:
                 # Valid selection
                 st.session_state.symposium_selection = selected_lenses
            else:
                st.session_state.symposium_selection = []
        else:
            st.info("Select categories/tiers above to view available lenses.")
            st.session_state.symposium_selection = []
    
    elif st.session_state.symposium_selection_mode == SELECT_SMART:
        st.info("🤖 **Smart Selection Activated.** The Janus 'Analyst-in-Chief' will choose the most potent lenses.")
        
        # Add control for how many lenses to select
        smart_count = st.number_input(
            "Number of lenses for Janus to select:",
            min_value=MIN_SELECTIONS,
            max_value=6, # Set a reasonable maximum for complexity
            value=st.session_state.symposium_smart_count,
            key="symposium_smart_count_input"
        )
        st.session_state.symposium_smart_count = smart_count

        # Ensure selection is empty in smart mode until execution
        st.session_state.symposium_selection = []

# --- MAIN PAGE ---

selection_mode = st.session_state.symposium_selection_mode
manual_selection = st.session_state.symposium_selection
smart_count = st.session_state.symposium_smart_count
# Reference the WorkInput object stored in session state
work_a = st.session_state.work_input_symposium
api_key = st.session_state.get("api_key", "")

# Determine if we are ready to proceed
is_ready_for_input = False
header_text = "Analysis | "

if selection_mode == SELECT_MANUAL:
    if manual_selection and len(manual_selection) >= MIN_SELECTIONS:
        is_ready_for_input = True
        header_text += f"{len(manual_selection)} Lenses (Manual)"
        st.info(f"**Manual Selection:** Ready to host a symposium between: {', '.join(manual_selection)}")
    else:
        st.info(f"⬅️ Please select {MIN_SELECTIONS} or more lenses using the multi-stage selector in the sidebar, or switch to Smart Selection.")

elif selection_mode == SELECT_SMART:
    is_ready_for_input = True
    header_text += f"{smart_count} Lenses (Smart Selection)"
    st.info(f"🤖 **Smart Selection:** Provide the input work below. The 'Analyst-in-Chief' will select {smart_count} lenses upon execution.")
else:
    st.info(f"⬅️ Please select {MIN_SELECTIONS} or more lenses using the sidebar, or switch to Smart Selection.")
if is_ready_for_input:
    st.header(header_text)
    
    # Input UI
    st.subheader("Input Work")
    utils.handle_input_ui(work_a, st.container(border=True), "work_symposium")

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
                final_selection = []

                with results_area:
                    try:
                        # --- Step 0: Smart Selection (if applicable) ---
                        if selection_mode == SELECT_SMART:
                            # Initialize JSON model specifically for Smart Selection
                            model_json = utils.get_model(api_key, json_mode=True)
                            if model_json:
                                smart_selection_status = st.status("Executing Smart Selection...", expanded=True)
                                # The analyst_in_chief handles the upload/caching
                                final_selection = utils.analyst_in_chief(
                                    model_json, 
                                    work_a, 
                                    required_count=smart_count, 
                                    status_container=smart_selection_status
                                )
                                smart_selection_status.update(label="Smart Selection Complete.", state="complete")
                            else:
                                st.error("Failed to initialize JSON model for Smart Selection.")
                        else:
                            final_selection = manual_selection

                        # Check if we have a valid selection
                        if not final_selection or len(final_selection) < MIN_SELECTIONS:
                             # Error message already displayed by analyst_in_chief if it failed
                             st.stop()

                        # --- Steps 1-N+1: Analysis and Synthesis ---
                        analyses_results = {}
                        N = len(final_selection)
                        total_steps = N + 1
                        
                        # Flag to track if execution should continue
                        continue_execution = True

                        # Step 1-N: Generate individual analyses
                        for i, lens_name in enumerate(final_selection):
                            if not continue_execution:
                                break
                                
                            st.subheader(f"Step {i+1}/{total_steps}: Analyzing ({lens_name})")
                            # generate_analysis uses the cached file upload if available
                            analysis_text = utils.generate_analysis(
                                model_standard,
                                lens_name,
                                work_a
                            )
                            if analysis_text:
                                analyses_results[lens_name] = analysis_text
                            else:
                                st.error(f"Failed to generate analysis for {lens_name}. Halting execution.")
                                continue_execution = False

                        # Step N+1: Synthesis
                        if continue_execution:
                            st.subheader(f"Step {total_steps}/{total_steps}: Symposium Synthesis")
                            with st.spinner("Synthesizing the symposium dialogue..."):
                                symposium_text = utils.generate_symposium_synthesis(
                                    model_standard,
                                    analyses_results,
                                    work_a.get_display_title()
                                )

                            if symposium_text:
                                st.header("Symposium Dialogue Result")
                                st.markdown(symposium_text)

                                # Display the raw analyses for reference
                                st.markdown("---")
                                st.subheader("Source Analyses (Reference)")
                                for lens_name, analysis_text in analyses_results.items():
                                    with st.expander(f"View Raw Analysis: {lens_name}"):
                                        st.markdown(analysis_text)
                    
                    finally:
                        # CRITICAL: Cleanup uploaded files after ALL analysis is complete
                        work_a.cleanup_gemini_file()

