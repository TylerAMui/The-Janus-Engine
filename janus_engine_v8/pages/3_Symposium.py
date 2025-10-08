import streamlit as st
import utils
import re
# Import PERSONA_POOL for the UI logic
# v9.4b: LENS_ZEITGEIST is removed.
from lenses import get_filtered_lenses, PERSONA_POOL
from utils import WorkInput, SELECT_MANUAL, SELECT_SMART, SELECTION_MODES, VIEW_ERA, VIEW_LIBRARY

# Constants for this mode
MIN_SELECTIONS = 3

# --- CALLBACKS ---

def handle_symposium_config_change():
    """
    Callback for changes in configuration:
    - Selection Mode (Manual/Smart)
    - Zeitgeist Toggle
    - Lens Multiselect
    """
    # If configuration changes, the previous execution data needs to be cleared to force reconfiguration.
    st.session_state.symposium_execution_data = []
    
    # Specific logic for mode switching (Manual/Smart)
    # We track the previous mode to detect actual changes in the radio button state.
    current_mode = st.session_state.get('symposium_selection_mode')
    if current_mode != st.session_state.get('previous_selection_mode'):
        # If switching modes, clear the lens selection UI state
        if 'symposium_lens_select_ui' in st.session_state:
            st.session_state.symposium_lens_select_ui = []
        st.session_state.previous_selection_mode = current_mode


# --- PAGE SETUP ---
# v9.5a: Update version number
PAGE_TITLE = "Janus v9.5a | Symposium"
utils.initialize_page_config(PAGE_TITLE)
st.title("3 | Symposium (3+ Perspectives)")
st.write("Analyze ONE work through THREE or more perspectives, synthesized into a discussion.")

# --- SIDEBAR (Global Settings Only) ---
utils.render_sidebar_settings()

# Initialize Session State for this page
if 'symposium_lens_select_ui' not in st.session_state:
    # Stores the state of the multiselect widget (list of lens names)
    st.session_state.symposium_lens_select_ui = []

if 'symposium_execution_data' not in st.session_state:
    # Stores the final data for execution: [{'lens': L1, 'persona': P1, 'is_zeitgeist': F, ...}, ...]
    st.session_state.symposium_execution_data = []

# Initialize the selection mode.
if 'symposium_selection_mode' not in st.session_state:
    st.session_state.symposium_selection_mode = SELECT_MANUAL

# Initialize 'previous_selection_mode' for the callback logic
if 'previous_selection_mode' not in st.session_state:
    st.session_state.previous_selection_mode = SELECT_MANUAL

if 'symposium_smart_count' not in st.session_state:
    # Default count for Smart Selection
    st.session_state.symposium_smart_count = 3 

# v9.4b: Initialize Zeitgeist toggle state
if 'symposium_include_zeitgeist' not in st.session_state:
    st.session_state.symposium_include_zeitgeist = False

# Initialize WorkInput object in session state
if 'work_input_symposium' not in st.session_state:
    st.session_state.work_input_symposium = WorkInput()

# --- MAIN PAGE LAYOUT ---

selection_mode = st.session_state.symposium_selection_mode
# Read the toggle state after potential updates from callbacks
include_zeitgeist = st.session_state.symposium_include_zeitgeist

# Reference the WorkInput object stored in session state
work_a = st.session_state.work_input_symposium
api_key = st.session_state.get("api_key", "")


# --- CONFIGURATION & LENS SELECTION (Hybrid Layout) ---
with st.expander("🔬 Configuration & Perspective Selection", expanded=True):

    # v9.4b: ZEITGEIST TOGGLE (Relocation Implementation Part A)
    # This toggle adds a Zeitgeist simulation as one participant, compatible with both Manual and Smart modes.
    st.markdown("#### 🕰️ Zeitgeist Participant (Optional)")
    st.toggle(
        "Include a Zeitgeist Simulation Participant",
        key="symposium_include_zeitgeist",
        on_change=handle_symposium_config_change,
        help="Add a custom historical context and witness persona as one of the participants in the symposium. This counts towards the minimum of 3."
    )

    zeitgeist_config = None
    if include_zeitgeist:
        st.markdown("Define the simulation parameters for the Zeitgeist participant:")
        z_col1, z_col2 = st.columns(2)
        with z_col1:
            z_context = st.text_area("Historical Context:", key="symposium_z_context", placeholder="Describe the era, location, and cultural climate...", height=150)
        with z_col2:
            z_persona = st.text_area("Witness Persona:", key="symposium_z_persona", placeholder="Describe the witness analyzing the work...", height=150)

        # v9.4b: Create the Zeitgeist configuration dictionary
        if z_context and z_persona:
            zeitgeist_config = {'lens': None, 'persona': None, 'is_zeitgeist': True, 'zeitgeist_context': z_context, 'zeitgeist_persona': z_persona}
        else:
            st.warning("Please complete the Historical Context and Witness Persona fields for the Zeitgeist simulation.")

    st.markdown("---")
    st.markdown("#### 🏛️ Lens Selection")

    # Selection Method Toggle
    st.radio(
        "Selection Method:",
        SELECTION_MODES,
        horizontal=True,
        key="symposium_selection_mode",
        on_change=handle_symposium_config_change
    )
    
    if selection_mode == SELECT_MANUAL:
        st.markdown("---")
        
        # Render the view toggle
        # v9.4b: Updated call (LENS_ZEITGEIST is removed)
        current_hierarchy, labels = utils.render_view_toggle_and_help("symposium")
        
        # Calculate required selections based on Zeitgeist inclusion
        required_lenses = MIN_SELECTIONS - 1 if include_zeitgeist else MIN_SELECTIONS
        
        lens_label = f"2. Select Lenses (Minimum {required_lenses}):"
        caption_text = f"Select {required_lenses} or more lenses. "
        if include_zeitgeist:
            caption_text += f"Combined with the Zeitgeist participant, this will meet the minimum of {MIN_SELECTIONS}."
        st.caption(caption_text)

        # Determine sorting order
        category_options = list(current_hierarchy.keys())
        current_view_mode = st.session_state.get("symposium_view_mode", VIEW_LIBRARY)
        
        # Sort alphabetically UNLESS it is the Era view
        if current_view_mode != VIEW_ERA:
            category_options.sort()

        # Layout for selection using columns
        col_filter, col_select = st.columns([1, 2])

        # Stage 1: Category/Tier/Era Selection
        with col_filter:
            selected_categories = st.multiselect(
                labels["category_label_multi"],
                options=category_options,
                placeholder=labels["placeholder_text_multi"],
                key="symposium_category_select"
            )

        # Stage 2: Filtered Lens Selection
        with col_select:
            if selected_categories:
                # Dynamically populate the lens options
                available_lenses = get_filtered_lenses(current_hierarchy, selected_categories)
                
                # The multiselect widget itself.
                selected_lenses_ui = st.multiselect(
                    lens_label,
                    options=available_lenses,
                    placeholder="Choose lenses...",
                    key="symposium_lens_select_ui",
                    on_change=handle_symposium_config_change # Use the general config change handler
                )
            else:
                st.info("Select categories/tiers/eras to view available lenses.")
                selected_lenses_ui = []

        # Stage 3: Persona Configuration
        
        final_data = []
        
        # v9.4b: Add Zeitgeist config first if active and valid
        is_zeitgeist_valid = False
        if include_zeitgeist:
            if zeitgeist_config:
                 final_data.append(zeitgeist_config)
                 is_zeitgeist_valid = True
            else:
                # Configuration is invalid if toggle is active but config is incomplete
                pass
        else:
            is_zeitgeist_valid = True # Valid because it's not required

        # v9.4b: Calculate total participants
        total_participants = len(selected_lenses_ui) + (1 if include_zeitgeist else 0)
        is_valid_count = total_participants >= MIN_SELECTIONS
        

        if selected_lenses_ui:
            st.markdown("---")
            st.markdown(f"**3. Configure Personas (Optional)**")

            # --- PERSONA CONFIGURATION (For selected lenses) ---
            
            cols = st.columns(3) 
            col_index = 0
            
            # Track lenses that have pools but weren't displayed in the grid yet
            lenses_without_pools = []

            for i, lens_name in enumerate(selected_lenses_ui):
                # Initialize the config dictionary for this lens (v9.4b structure)
                # Initialize with empty strings for optional keys for consistency
                config = {'lens': lens_name, 'persona': None, 'is_zeitgeist': False, 'zeitgeist_context': "", 'zeitgeist_persona': ""}

                # Check if a pool exists
                if lens_name in PERSONA_POOL:
                    with cols[col_index % 3]:
                        # Render the selector dynamically. The key ensures unique state per selector.
                        persona = utils.render_persona_selector(lens_name, f"symposium_persona_{i}_{lens_name}")
                        config['persona'] = persona
                        final_data.append(config)
                        col_index += 1
                else:
                    # No pool, just add the lens data
                    final_data.append(config)
                    lenses_without_pools.append(lens_name)

            if lenses_without_pools:
                st.caption(f"Lenses without specific pools (AI will generate persona): {', '.join(lenses_without_pools)}")

        # Validation Summary for Manual Mode
        if not is_valid_count:
             st.warning(f"Total participants: {total_participants}. Please select more lenses or include Zeitgeist to reach the minimum of {MIN_SELECTIONS}.")

        if is_valid_count and is_zeitgeist_valid:
            st.session_state.symposium_execution_data = final_data
        else:
            st.session_state.symposium_execution_data = []

    
    elif selection_mode == SELECT_SMART:
        # v9.4b: Updated info text to reflect compatibility with Zeitgeist.
        st.info("🤖 **Smart Selection Activated.** The Janus 'Analyst-in-Chief' will choose the potent lenses. Personas will be selected automatically.")
        
        # Add control for how many lenses to select
        smart_count_input = st.number_input(
            "Number of lenses for Janus to select:",
            min_value=1, # Minimum is 1, because Zeitgeist might provide the others.
            max_value=6, # Set a reasonable maximum for complexity
            value=st.session_state.symposium_smart_count,
            key="symposium_smart_count_input"
        )
        # Update the session state variable used in the execution block
        st.session_state.symposium_smart_count = smart_count_input

        # v9.4b: Validate the total count in Smart Mode
        total_participants_smart = smart_count_input + (1 if include_zeitgeist else 0)
        
        # Check if Zeitgeist configuration is valid if the toggle is active
        is_zeitgeist_valid_smart = (not include_zeitgeist) or (include_zeitgeist and zeitgeist_config)

        if total_participants_smart < MIN_SELECTIONS:
             st.warning(f"Total participants: {total_participants_smart}. Please increase the Smart Selection count or activate Zeitgeist to reach the minimum of {MIN_SELECTIONS}.")
             st.session_state.symposium_execution_data = [] # Treat as invalid for input readiness
        elif not is_zeitgeist_valid_smart:
             # Zeitgeist warning already displayed above, but we must invalidate the state
             st.session_state.symposium_execution_data = []
        else:
            # In Smart mode, the execution data is built during the execution phase,
            # but we use this state variable to signal readiness for input.
            # We use a placeholder list to signify readiness.
            st.session_state.symposium_execution_data = ["READY_SMART"]


# --- INPUT & EXECUTION ---

# Determine if we are ready to proceed
is_ready_for_input = False
header_text = "Analysis | "

# Read the session state AFTER the configuration block has run
current_execution_data = st.session_state.symposium_execution_data

# v9.4b: Check readiness based on the validity determined in the config block.
if current_execution_data:
    is_ready_for_input = True
    
    if selection_mode == SELECT_MANUAL:
        header_text += f"{len(current_execution_data)} Participants (Manual)"
        
        # Display configured lenses/personas in the main area for confirmation
        with st.expander("View Configured Symposium Participants"):
            st.info("The following perspectives will participate:")
            for item in current_execution_data:
                # v9.4b: Handle display for new structure
                if item.get('is_zeitgeist'):
                    display_text = "**Zeitgeist Simulation** (User Defined)"
                else:
                    display_text = f"**{item.get('lens', 'Unknown')}**"
                    if item.get('persona'):
                        display_text += f" (as {item['persona']})"
                st.markdown(f"- {display_text}")

    elif selection_mode == SELECT_SMART:
        # Calculate total participants for the header
        smart_count_val = st.session_state.symposium_smart_count
        total_smart_p = smart_count_val + (1 if include_zeitgeist else 0)
        header_text += f"{total_smart_p} Participants (Smart Selection)"

else:
    # General info message if configuration is incomplete (specific warnings shown in config block)
    st.info(f"Please ensure {MIN_SELECTIONS} or more participants are selected and configured using the options above.")


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
                # This list holds the final execution data configuration
                final_execution_data = []

                with results_area:
                    try:
                        # --- Step 0: Determine Final Execution Data (Handle Smart Selection and Zeitgeist) ---
                        
                        # v9.4b: Retrieve Zeitgeist configuration if active (needed for both modes during execution phase)
                        zeitgeist_config_exec = None
                        if include_zeitgeist:
                            # We rely on the validation done previously ensuring these inputs exist in session state.
                             z_context_exec = st.session_state.get("symposium_z_context")
                             z_persona_exec = st.session_state.get("symposium_z_persona")
                             if z_context_exec and z_persona_exec:
                                 zeitgeist_config_exec = {'lens': None, 'persona': None, 'is_zeitgeist': True, 'zeitgeist_context': z_context_exec, 'zeitgeist_persona': z_persona_exec}
                             else:
                                 # Safety fallback
                                 st.error("Internal Error: Zeitgeist configuration missing during execution.")
                                 st.stop()

                        if selection_mode == SELECT_SMART:
                            # Initialize JSON model specifically for Smart Selection
                            model_json = utils.get_model(api_key, json_mode=True)
                            if model_json:
                                smart_selection_status = st.status("Executing Smart Selection...", expanded=True)
                                # The analyst_in_chief handles the upload/caching
                                smart_lenses = utils.analyst_in_chief(
                                    model_json, 
                                    work_a, 
                                    required_count=st.session_state.symposium_smart_count, 
                                    status_container=smart_selection_status
                                )
                                smart_selection_status.update(label="Smart Selection Complete.", state="complete")

                                if smart_lenses:
                                    # Transform smart selection into execution data format (v9.4b structure)
                                    final_execution_data = [{'lens': lens, 'persona': None, 'is_zeitgeist': False} for lens in smart_lenses]
                                    # Add Zeitgeist config if present
                                    if zeitgeist_config_exec:
                                        final_execution_data.append(zeitgeist_config_exec)

                            else:
                                st.error("Failed to initialize JSON model for Smart Selection.")
                        else:
                            # Use the data directly from session state (Manual Mode)
                            # This already includes the Zeitgeist config if active.
                            final_execution_data = st.session_state.symposium_execution_data

                        # Final Check if we have a valid selection
                        if not final_execution_data or len(final_execution_data) < MIN_SELECTIONS:
                            # Error message already displayed by analyst_in_chief if it failed, or config incomplete.
                            st.stop()

                        # Backend Persona-Aware Validation (Defensive check for duplicates)
                        config_identifiers = set()
                        has_duplicates = False
                        for item in final_execution_data:
                            # v9.4b: Create a unique tuple identifier based on new structure.
                            if item.get('is_zeitgeist'):
                                 identifier = ('ZEITGEIST_SIM', item.get('zeitgeist_context'), item.get('zeitgeist_persona'))
                            else:
                                # If persona is None, the AI defaults, which we treat as identical for the same lens.
                                identifier = (item.get('lens'), item.get('persona'))

                            if identifier in config_identifiers:
                                has_duplicates = True
                                break
                            config_identifiers.add(identifier)
                        
                        if has_duplicates:
                            # This might happen if Smart Selection returns duplicates.
                            st.error("Duplicate configuration detected (likely an issue with Smart Selection). Please try again.")
                            st.stop()


                        # --- Steps 1-N+1: Analysis and Synthesis ---
                        analyses_results_list = [] 
                        N = len(final_execution_data)
                        total_steps = N + 1
                        
                        # Step 1-N (Concurrent): Generate individual analyses
                        st.subheader(f"Step 1/{total_steps}: Generating all {N} analyses concurrently...")

                        # Create a list of async tasks
                        tasks = [
                            utils.async_generate_analysis(model_standard, data_item, work_a)
                            for data_item in final_execution_data
                        ]

                        # Run the tasks concurrently
                        analysis_texts = utils.run_async_tasks(tasks)

                        # Associate results with their original config and check for failures
                        continue_execution = True
                        for i, analysis_text in enumerate(analysis_texts):
                            if analysis_text:
                                analyses_results_list.append((final_execution_data[i], analysis_text))
                            else:
                                display_name = final_execution_data[i].get('lens') or "Zeitgeist Simulation"
                                st.error(f"Failed to generate analysis for {display_name}. Halting execution.")
                                continue_execution = False
                        
                        # Step N+1: Synthesis
                        if continue_execution:
                            st.subheader(f"Step {total_steps-1}/{total_steps}: Symposium Synthesis") # Adjusted step number
                            
                            # Clarification for the user by extracting personas and lenses
                            participant_list = []
                            for config, analysis_text in analyses_results_list:
                                persona_name = "Unknown Persona"
                                match = re.search(r"^### Analysis by (.*)", analysis_text.strip())
                                if match:
                                    persona_name = match.group(1).strip()

                                if config.get('is_zeitgeist'):
                                    participant_list.append(persona_name)
                                else:
                                    lens_name = config.get('lens', 'Unknown Lens')
                                    # Avoid redundant labels
                                    if lens_name.lower() in persona_name.lower():
                                        participant_list.append(persona_name)
                                    else:
                                        participant_list.append(f"{persona_name} ({lens_name})")

                            st.info(f"**Synthesizing Dialogue Between:** {', '.join(participant_list)}")

                            with st.spinner("Synthesizing the symposium dialogue..."):
                                # v9.4b: Call the synthesis function with the correctly formatted results list.
                                symposium_text = utils.generate_symposium_synthesis(
                                    model_standard,
                                    analyses_results_list, # Updated argument
                                    work_a.get_display_title()
                                )

                            if symposium_text:
                                st.header("Symposium Dialogue Result")
                                st.markdown(symposium_text)

                                # Display the raw analyses for reference
                                st.markdown("---")
                                st.subheader("Source Analyses (Reference)")
                                # v9.4b: Iterate over the list of tuples
                                for config, analysis_text in analyses_results_list:
                                    display_name = config.get('lens') or "Zeitgeist Simulation"
                                    with st.expander(f"View Raw Analysis: {display_name}"):
                                        st.markdown(analysis_text)
                        
                    finally:
                        # CRITICAL: Cleanup uploaded files after ALL analysis is complete
                        work_a.cleanup_gemini_file()
