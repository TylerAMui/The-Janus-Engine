import streamlit as st
import utils
from utils import WorkInput

# Define Callbacks for state management
def reset_analysis_state():
    """Callback to reset the analysis state when configuration or input changes."""
    st.session_state.single_lens_state = 'config'
    st.session_state.single_lens_result = None
    # Clear refinement input UI element if it exists
    if 'refinement_instruction' in st.session_state:
        st.session_state.refinement_instruction = ""
    
    # CRITICAL: Clean up cached files when the session is reset
    if 'work_input_single' in st.session_state:
        st.session_state.work_input_single.cleanup_gemini_file()

# v9.4b: Callback specifically for Zeitgeist toggle activation
def handle_zeitgeist_toggle():
    # If Zeitgeist is turned ON, we must clear any previous lens/persona selections from the UI widgets
    # to prevent inconsistent state
    if st.session_state.get('single_zeitgeist_active', False):
        # Clear the UI selection widgets if they exist in the state
        if 'single_cat_select' in st.session_state:
            st.session_state.single_cat_select = None
        if 'single_lens_select' in st.session_state:
            st.session_state.single_lens_select = None
            
    # Always reset the analysis results when the mode changes
    reset_analysis_state()

# --- PAGE SETUP ---
# v9.5a: Update version number
PAGE_TITLE = "Janus v9.5a | Single Lens"
utils.initialize_page_config(PAGE_TITLE)
st.title("1 | Single Lens Analysis")
# v9.4b: Update description
st.write("Analyze ONE work through ONE specific lens or the Zeitgeist Simulation. Ideal for focused inquiry and iterative refinement.")

# --- SIDEBAR (Global Settings Only) ---
utils.render_sidebar_settings()

# Initialize Session State for this page
if 'single_lens_selection' not in st.session_state:
    # v9.4b: Updated structure to include is_zeitgeist flag
    # This dictionary acts as the lens_config object passed to the engine.
    st.session_state.single_lens_selection = {'lens': None, 'persona': None, 'is_zeitgeist': False, 'zeitgeist_context': "", 'zeitgeist_persona': ""}

# Initialize WorkInput object in session state
if 'work_input_single' not in st.session_state:
    st.session_state.work_input_single = WorkInput()

# Initialize state for Refinement Loop
if 'single_lens_state' not in st.session_state:
    # Possible states: 'config', 'executed'
    st.session_state.single_lens_state = 'config'
if 'single_lens_result' not in st.session_state:
    st.session_state.single_lens_result = None


# --- MAIN PAGE LAYOUT ---

# Reference session state variables
selection = st.session_state.single_lens_selection
work_a = st.session_state.work_input_single
api_key = st.session_state.get("api_key", "")

# --- CONFIGURATION & LENS SELECTION (Hybrid Layout) ---
with st.expander("🔬 Configuration & Lens Selection", expanded=True):
    
    # v9.4b: ZEITGEIST TOGGLE (Part 2: The Relocation)
    st.toggle(
        "Activate Zeitgeist Simulation", 
        key="single_zeitgeist_active",
        on_change=handle_zeitgeist_toggle, # v9.4b: Use the specific toggle callback
        help="Activate this mode to define a custom historical context and witness persona instead of using a standard library lens."
    )
    
    # Update the configuration dictionary based on the toggle state
    selection['is_zeitgeist'] = st.session_state.single_zeitgeist_active
    
    st.markdown("---")

    # --- CONDITIONAL UI LOGIC ---
    
    if selection['is_zeitgeist']:
        # ZEITGEIST MODE UI
        # Ensure standard lens selections are cleared in the config object
        selection['lens'] = None
        selection['persona'] = None
        
        st.subheader("🕰️ Define the Zeitgeist")
        z_col1, z_col2 = st.columns(2)
        with z_col1:
            # We update the selection dictionary by reading the widget state after interaction
            st.text_area(
                "Historical Context:", height=150, key="single_z_context",
                placeholder="e.g., 'Vienna, 1905. The height of modernism...'",
                on_change=reset_analysis_state # Reset results if inputs change
            )
            selection['zeitgeist_context'] = st.session_state.single_z_context
        with z_col2:
            st.text_area(
                "Witness Persona:", height=150, key="single_z_persona",
                placeholder="e.g., 'A middle-aged, conservative art critic...'",
                on_change=reset_analysis_state # Reset results if inputs change
            )
            selection['zeitgeist_persona'] = st.session_state.single_z_persona

    else:
        # STANDARD LENS SELECTION UI
        # Ensure Zeitgeist data is cleared in the config object
        selection['zeitgeist_context'] = ""
        selection['zeitgeist_persona'] = ""

        # Render the standard Library/Workshop/Timeline interface
        # v9.4b: Updated signature (LENS_ZEITGEIST removed)
        current_hierarchy, labels = utils.render_view_toggle_and_help("single")
        
        # Initialize variables for the UI selection process
        selected_persona = None

        # Use columns for cleaner, horizontal selection layout
        col_cat, col_lens, col_persona = st.columns(3)

        # Determine sorting order
        category_options = list(current_hierarchy.keys())
        current_view_mode = st.session_state.get("single_view_mode", utils.VIEW_LIBRARY)
        
        # Sort alphabetically UNLESS it is the Era view (which is chronological)
        if current_view_mode != utils.VIEW_ERA:
            category_options.sort()

        # Stage 1: Category/Tier/Era Selection
        with col_cat:
            category = st.selectbox(
                labels["category_label_single"],
                options=category_options,
                index=None,
                placeholder=labels["placeholder_text_single"],
                key="single_cat_select",
                on_change=reset_analysis_state
            )

        # Stage 2 & 3: Specific Lens Selection and Conditional Logic
        if category:
            with col_lens:
                lens_options = current_hierarchy[category]
                
                # BUG FIX: THE INDEX METHOD (Ensures persistence when switching views)
                # 1. Get the current value from the widget's state key
                current_lens_selection = st.session_state.get("single_lens_select")
                
                # 2. Calculate the index of the current selection in the options list
                try:
                    index = lens_options.index(current_lens_selection)
                except (ValueError, TypeError):
                    index = None

                # 3. Render the widget, passing the calculated index.
                st.selectbox(
                    "2. Specific Lens:",
                    options=lens_options,
                    index=index,
                    placeholder="Select a specific lens...",
                    key="single_lens_select",
                    on_change=reset_analysis_state, 
                    help=utils.get_lens_tooltip(current_lens_selection)
                )

            # Update the main selection dictionary with the value from the widget's state
            selection['lens'] = st.session_state.get("single_lens_select")
            selected_lens = selection['lens']

            # Stage 3: Persona Selection
            if selected_lens:
                with col_persona:
                    selected_persona = utils.render_persona_selector(selected_lens, "single")
        else:
            # Ensure lens is None if no category is selected
            selection['lens'] = None

        # Update Session State for Persona
        selection['persona'] = selected_persona


# --- INPUT & EXECUTION ---

# v9.4b: Determine if configuration is complete (either Lens or Zeitgeist)
is_configured = False
if selection['is_zeitgeist']:
    # Check if Zeitgeist inputs are complete
    if selection['zeitgeist_context'] and selection['zeitgeist_persona']:
        is_configured = True
elif selection['lens']:
    # Check if a lens is selected
    is_configured = True

if is_configured:
    # Construct header text
    # v9.4b: Updated header logic
    if selection['is_zeitgeist']:
        header_text = "Analysis | Zeitgeist Simulation Mode"
    else:
        header_text = f"Analysis | Lens: {selection['lens']}"
        if selection['persona']:
            header_text += f" | Persona: {selection['persona']}"
        
    st.header(header_text)
    
    # Input UI
    st.subheader("Input Work")
    # Pass the callback to handle_input_ui so changes to the work reset the results and clean files
    utils.handle_input_ui(work_a, st.container(border=True), "work_single", on_change_callback=reset_analysis_state)

    # Execution Button
    st.markdown("---")

    # Change button label if already executed
    button_label = "Execute Analysis Engine"
    if st.session_state.single_lens_state == 'executed':
        button_label = "Re-Execute Analysis (Start Over)"

    if st.button(button_label, type="primary", use_container_width=True):
        # Validation (Basic validation already handled by is_configured, checking API/Work here)
        is_valid = True
        if not api_key:
            st.warning("Please enter your Gemini API Key in the sidebar (under 🔑 API Configuration).")
            is_valid = False

        if not work_a.is_ready():
            st.warning("Please provide the creative work to be analyzed.")
            is_valid = False
        
        if is_valid:
            # If re-executing, reset state first (this also cleans up old files)
            if st.session_state.single_lens_state == 'executed':
                reset_analysis_state()

            # --- Execution Block ---
            model = utils.get_model(api_key)
            if model:
                # We use a temporary container to show the status indicators during execution
                st.markdown("---")
                execution_area = st.container()

                with execution_area:
                    try:
                        # Call the analysis function
                        # Pass the entire selection dictionary (lens_config)
                        analysis_result = utils.generate_analysis(
                            model,
                            selection,
                            work_a
                        )

                        if analysis_result:
                            # Update session state on success
                            st.session_state.single_lens_result = analysis_result
                            st.session_state.single_lens_state = 'executed'
                            # Rerun to display results outside the execution block and show refinement UI
                            st.rerun()
                        else:
                            # Error messages are typically displayed within generate_analysis status
                            pass 
                    
                    finally:
                        # Do NOT clean up files here if successful. We need the cache for the refinement loop.
                        # If analysis failed, we should clean up.
                        if st.session_state.single_lens_state != 'executed':
                            work_a.cleanup_gemini_file()

else:
    # Message displayed on initial load or incomplete configuration.
    st.info("Please select a Lens or activate and define the Zeitgeist Simulation using the configuration options above.")


# --- RESULTS & REFINEMENT LOOP ---
# This section is displayed regardless of the configuration above, based on the execution state.

if st.session_state.single_lens_state == 'executed' and st.session_state.single_lens_result:
    st.markdown("---")
    st.header("Analysis Result")
    # Display the current result stored in session state
    st.markdown(st.session_state.single_lens_result)

    # Refinement Loop UI
    st.markdown("---")
    st.subheader("🔄 Refinement Loop")
    with st.container(border=True):
        st.write("Provide instructions to iteratively refine the analysis above.")
        refinement_instruction = st.text_area("Refinement Instruction:", height=100, key="refinement_instruction", placeholder="e.g., 'Focus more deeply on the symbolism of the color blue', or 'Make the tone more academic and less conversational.'")

        if st.button("Refine Analysis", type="secondary"):
            if not refinement_instruction:
                st.warning("Please enter a refinement instruction.")
            elif not api_key:
                st.warning("API Key is missing. Please check configuration.")
            else:
                # --- Refinement Execution Block ---
                model_refine = utils.get_model(api_key)
                if model_refine:
                    refinement_area = st.container()
                    with refinement_area:
                        # Call the refinement function
                        refined_result = utils.generate_refined_analysis(
                            model_refine,
                            work_a, # Pass the original work input (which holds the cached file reference)
                            st.session_state.single_lens_result, # Pass the previous analysis
                            refinement_instruction
                        )

                        if refined_result:
                            # Update the result in session state
                            st.session_state.single_lens_result = refined_result
                            # Clear the instruction input box
                            st.session_state.refinement_instruction = ""
                            # Rerun to display the new result
                            st.rerun()
                # No cleanup needed here; relies on reset_analysis_state for final cleanup.
