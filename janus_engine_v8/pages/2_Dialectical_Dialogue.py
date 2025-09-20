# pages/2_Dialectical_Dialogue.py
import streamlit as st
import utils
from utils import WorkInput, SELECT_MANUAL, SELECT_SMART, SELECTION_MODES

# --- CALLBACKS ---
# Diagnosis: The original code used st.rerun() in the sidebar to synchronize state changes.
# This is an anti-pattern that causes the script execution to halt prematurely, resulting in a blank page.
# Fix: We use the idiomatic Streamlit pattern: an on_change callback to handle side effects (clearing selections).

def handle_dialectical_mode_change():
    """Callback to clear selections when the mode changes."""
    # This runs after the state key is updated but before the script reruns.
    st.session_state.dialectical_selection = []

# --- PAGE SETUP ---
PAGE_TITLE = "Janus v8.0 | Dialectical Dialogue"
utils.initialize_page_config(PAGE_TITLE)
st.title("2 | Dialectical Dialogue (2 Lenses)")
st.write("Analyze ONE work through TWO lenses, synthesized into a dialogue (Thesis vs. Antithesis).")

# --- SIDEBAR ---
utils.render_sidebar_settings()

# Initialize Session State for this page
if 'dialectical_selection' not in st.session_state:
    st.session_state.dialectical_selection = []

# Initialize the selection mode. This key is the single source of truth, managed by the widget.
if 'dialectical_selection_mode' not in st.session_state:
    st.session_state.dialectical_selection_mode = SELECT_MANUAL

# Initialize WorkInput object in session state
if 'work_input_dialectical' not in st.session_state:
    st.session_state.work_input_dialectical = WorkInput()

# --- LENS SELECTION (Sidebar) ---
with st.sidebar:
    st.markdown("---")
    st.subheader("🔬 Lens Selection")

    # v8.0 Feature: Smart Selection Toggle
    # Replaced manual comparison and st.rerun() with the idiomatic pattern.
    st.radio(
        "Selection Method:",
        SELECTION_MODES,
        # Index is handled automatically based on the key's initialized state.
        key="dialectical_selection_mode", 
        on_change=handle_dialectical_mode_change
    )
    
    # The previous block containing the manual check and st.rerun() has been removed.

    if st.session_state.dialectical_selection_mode == SELECT_MANUAL:
        # Render the standard Library/Workshop interface
        current_hierarchy, labels = utils.render_lens_selection_interface("dialectical")
        st.caption("Select two independent lenses (Thesis and Antithesis).")

        # Initialize variables
        lens_a = None
        lens_b = None

        # --- Lens A (Thesis) Pathway ---
        with st.container(border=True):
            st.markdown("🏛️ **Lens A (Thesis)**")
            
            # Stage 1: Category/Tier Selection
            category_a = st.selectbox(
                labels["category_label_single"],
                options=sorted(list(current_hierarchy.keys())),
                index=None,
                placeholder=labels["placeholder_text_single"],
                key="dialectic_cat_a",
            )

            # Stage 2: Specific Lens Selection
            if category_a:
                lens_options_a = current_hierarchy[category_a]
                lens_a = st.selectbox(
                    "2. Specific Lens A:",
                    options=lens_options_a,
                    index=None,
                    placeholder="Select a specific lens...",
                    key="dialectic_lens_a",
                )

        # --- Lens B (Antithesis) Pathway ---
        with st.container(border=True):
            st.markdown("🏛️ **Lens B (Antithesis)**")
            
            # Stage 1: Category/Tier Selection
            category_b = st.selectbox(
                labels["category_label_single"],
                options=sorted(list(current_hierarchy.keys())),
                index=None,
                placeholder=labels["placeholder_text_single"],
                key="dialectic_cat_b",
            )

            # Stage 2: Specific Lens Selection
            if category_b:
                lens_options_b = current_hierarchy[category_b]
                lens_b = st.selectbox(
                    "2. Specific Lens B:",
                    options=lens_options_b,
                    index=None,
                    placeholder="Select a specific lens...",
                    key="dialectic_lens_b",
                )

        # Validation and Session State Update
        if lens_a and lens_b:
            if lens_a == lens_b:
                st.warning("Please select two different lenses for the dialogue.")
                st.session_state.dialectical_selection = []
            else:
                # Valid selection, store as a list
                st.session_state.dialectical_selection = [lens_a, lens_b]
        else:
            st.session_state.dialectical_selection = []
    
    elif st.session_state.dialectical_selection_mode == SELECT_SMART:
        st.info("🤖 **Smart Selection Activated.** The Janus 'Analyst-in-Chief' will choose the two most potent lenses after analyzing your input.")
        # Ensure selection is empty in smart mode until execution (also handled by callback)
        st.session_state.dialectical_selection = []

# --- MAIN PAGE ---
# The script now reliably reaches this point because st.rerun() is no longer used.

selection_mode = st.session_state.dialectical_selection_mode
manual_selection = st.session_state.dialectical_selection
# Reference the WorkInput object stored in session state
work_a = st.session_state.work_input_dialectical
api_key = st.session_state.get("api_key", "")

# Determine if we are ready to proceed
is_ready_for_input = False
header_text = "Analysis | "

if selection_mode == SELECT_MANUAL:
    if manual_selection and len(manual_selection) == 2:
        is_ready_for_input = True
        header_text += f"{manual_selection[0]} vs. {manual_selection[1]}"
        st.info(f"**Manual Selection:** Ready to synthesize **{manual_selection[0]}** (Thesis) and **{manual_selection[1]}** (Antithesis).")
    else:
        # This message is displayed on initial load.
        st.info("⬅️ Please select Lens A (Thesis) and Lens B (Antithesis) using the selectors in the sidebar, or switch to Smart Selection.")

elif selection_mode == SELECT_SMART:
    is_ready_for_input = True
    header_text += "Smart Selection"
    st.info("🤖 **Smart Selection:** Provide the input work below. The 'Analyst-in-Chief' will select the lenses upon execution.")

# Removed redundant final 'else' block as conditions above cover all required states.

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
                final_selection = []

                with results_area:
                    try:
                        # --- Step 0: Smart Selection (if applicable) ---
                        if selection_mode == SELECT_SMART:
                            # Initialize JSON model specifically for Smart Selection
                            model_json = utils.get_model(api_key, json_mode=True)
                            if model_json:
                                smart_selection_status = st.status("Executing Smart Selection...", expanded=True)
                                # The analyst_in_chief handles the upload if necessary and utilizes caching
                                final_selection = utils.analyst_in_chief(
                                    model_json, 
                                    work_a, 
                                    required_count=2, 
                                    status_container=smart_selection_status
                                )
                                smart_selection_status.update(label="Smart Selection Complete.", state="complete")
                            else:
                                st.error("Failed to initialize JSON model for Smart Selection.")
                        else:
                            final_selection = manual_selection

                        # Check if we have a valid selection (manual or smart)
                        if not final_selection or len(final_selection) != 2:
                             # Error message already displayed by analyst_in_chief if it failed
                             st.stop()
                        
                        # --- Steps 1-3: Analysis and Synthesis ---
                        lens_a_name = final_selection[0]
                        lens_b_name = final_selection[1]

                        # Call 1 (Part A): Generate Thesis
                        st.subheader(f"Step 1/3: Thesis ({lens_a_name})")
                        # generate_analysis uses the cached file upload if available
                        analysis_a = utils.generate_analysis(
                            model_standard,
                            lens_a_name,
                            work_a
                        )

                        # Call 1 (Part B): Generate Antithesis
                        analysis_b = None
                        if analysis_a:
                            st.subheader(f"Step 2/3: Antithesis ({lens_b_name})")
                            analysis_b = utils.generate_analysis(
                                model_standard,
                                lens_b_name,
                                work_a
                            )

                        # Call 2: Synthesis
                        if analysis_a and analysis_b:
                            st.subheader("Step 3/3: Synthesis (Aufheben)")
                            with st.spinner("Synthesizing the dialogue..."):
                                dialogue_text = utils.generate_dialectical_synthesis(
                                    model_standard,
                                    lens_a_name,
                                    analysis_a,
                                    lens_b_name,
                                    analysis_b,
                                    work_a.get_display_title()
                                )

                            if dialogue_text:
                                st.header("Dialectical Dialogue Result")
                                st.markdown(dialogue_text)

                                # Display the raw analyses for reference
                                st.markdown("---")
                                st.subheader("Source Analyses (Reference)")
                                with st.expander(f"View Raw Analysis A: {lens_a_name}"):
                                    st.markdown(analysis_a)
                                with st.expander(f"View Raw Analysis B: {lens_b_name}"):
                                    st.markdown(analysis_b)
                        else:
                            st.error("Could not generate the initial analyses. Cannot proceed to synthesis.")
                    
                    finally:
                        # CRITICAL: Cleanup uploaded files after ALL analysis is complete
                        # This ensures the file uploaded during Smart Selection or Analysis is deleted.
                        work_a.cleanup_gemini_file()
