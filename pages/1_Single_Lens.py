import streamlit as st
import utils
from utils import WorkInput

# Define Callbacks for state management
# v10.0.15: Centralize reset logic
def reset_analysis_state():
    utils.reset_page_state('single_lens')

# v9.4b: Callback specifically for Zeitgeist toggle activation
# v10.1: Updated to clear new filter widgets
def handle_zeitgeist_toggle():
    # If Zeitgeist is turned ON, we must clear any previous lens/persona selections from the UI widgets
    # to prevent inconsistent state
    if st.session_state.get('single_zeitgeist_active', False):
        # Clear the UI selection widgets if they exist in the state
        if 'single_lens_select' in st.session_state:
            st.session_state.single_lens_select = None
        # Clear filter widgets
        if 'single_discipline_filter' in st.session_state:
            st.session_state.single_discipline_filter = "All Disciplines"
        if 'single_function_filter' in st.session_state:
            st.session_state.single_function_filter = "All Functions"
        if 'single_era_filter' in st.session_state:
            st.session_state.single_era_filter = "All Eras"
        if 'single_geographic_filter' in st.session_state:
            st.session_state.single_geographic_filter = "All Regions"

# --- PAGE SETUP ---
# v10.2: Update page title
PAGE_TITLE = "Janus | Single Lens"
utils.initialize_page_config(PAGE_TITLE)
st.title("1 | Single Lens Analysis")
# v9.4b: Update description
st.write("Analyze ONE work through ONE specific lens or the Zeitgeist Simulation. Ideal for focused inquiry and iterative refinement.")

# --- SIDEBAR (Global Settings Only) ---
utils.render_sidebar_settings()

# --- PAGE MEMORY MANAGEMENT ---
# Clean up uploaded files from other pages to prevent memory accumulation
if 'current_page' not in st.session_state:
    st.session_state.current_page = None

if st.session_state.current_page != "single_lens":
    st.session_state.current_page = "single_lens"
    utils.cleanup_other_pages_files("single_lens")

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
if 'single_lens_strategy' not in st.session_state:
    st.session_state.single_lens_strategy = None
if 'single_lens_selection_method' not in st.session_state:
    st.session_state.single_lens_selection_method = utils.SELECT_MANUAL

# v10.1: Handle Library Pre-selection (MUST happen before any widgets are created)
if 'library_selected_lens' in st.session_state:
    preselected_lens = st.session_state.library_selected_lens
    # Turn off Zeitgeist if it was active
    if 'single_zeitgeist_active' not in st.session_state:
        st.session_state.single_zeitgeist_active = False
    else:
        st.session_state.single_zeitgeist_active = False
    # Reset filters to ensure pre-selected lens is visible
    st.session_state.single_discipline_filter = "All Disciplines"
    st.session_state.single_function_filter = "All Functions"
    st.session_state.single_era_filter = "All Eras"
    st.session_state.single_geographic_filter = "All Regions"
    # Set the lens selection
    st.session_state.single_lens_select = preselected_lens
    # Clear the flag (one-time use)
    del st.session_state.library_selected_lens
    st.rerun()

# --- REFINEMENT EXECUTION LOGIC (Moved to top of script) ---
if st.session_state.get("run_refinement_on_next_load"):
    st.session_state.run_refinement_on_next_load = False
    instruction = st.session_state.get("instruction_to_run", "")
    if instruction:
        # --- Refinement Execution Block ---
        refinement_area = st.container()
        with refinement_area:
            refined_result = utils.generate_refined_analysis(
                st.session_state.work_input_single,
                st.session_state.single_lens_result,
                instruction
            )

            if refined_result:
                # Update the main result
                st.session_state.single_lens_result = refined_result
                # Now it's safe to clear the input state for the widget
                st.session_state.refinement_instruction = ""
                # Rerun to display the new result and return to the top of the page
                st.rerun()


# --- MAIN PAGE LAYOUT ---

# Reference session state variables
selection = st.session_state.single_lens_selection
work_a = st.session_state.work_input_single
selection_method = st.session_state.single_lens_selection_method

# --- STEP 1: INPUT WORK (Always visible first) ---

# v10.2: API Key Warning Banner
if not st.session_state.get("api_key"):
    st.warning("⚠️ API Key Required — Please configure on Home page to use the engine")

st.header("📄 Input Work")
st.caption("Upload your creative work or enter text to begin")
utils.handle_input_ui(work_a, st.container(border=True), "work_single", on_change_callback=reset_analysis_state)

# Check if work is ready
work_is_ready = work_a.is_ready()

if not work_is_ready:
    st.info("👆 Please upload a file or enter text above to proceed with configuration.")
    st.stop()  # Stop rendering here until work is provided

# --- STEP 2: CONFIGURATION & LENS SELECTION (Only appears after work is ready) ---
st.markdown("---")
with st.expander("🔬 Configuration & Lens Selection", expanded=True):

    # v10.2: Selection Method and Zeitgeist toggle on same line (always visible)
    method_col, zeitgeist_col = st.columns([3, 1])
    with method_col:
        if not st.session_state.get('single_zeitgeist_active', False):
            st.radio(
                "**Selection Method:**",
                utils.SELECTION_MODES,
                horizontal=True,
                key="single_lens_selection_method"
            )
        else:
            st.markdown("**Mode:** Zeitgeist Simulation")
    with zeitgeist_col:
        st.toggle(
            "Zeitgeist",
            key="single_zeitgeist_active",
            on_change=handle_zeitgeist_toggle,
            help="Activate Zeitgeist Simulation mode"
        )

    # Update the configuration dictionary based on the toggle state
    selection['is_zeitgeist'] = st.session_state.get('single_zeitgeist_active', False)

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
                placeholder="e.g., 'Vienna, 1905. The height of modernism...'"
            )
            selection['zeitgeist_context'] = st.session_state.single_z_context
        with z_col2:
            st.text_area(
                "Witness Persona:", height=150, key="single_z_persona",
                placeholder="e.g., 'A middle-aged, conservative art critic...'"
            )
            selection['zeitgeist_persona'] = st.session_state.single_z_persona

    else:
        # STANDARD LENS SELECTION UI
        # Ensure Zeitgeist data is cleared in the config object
        selection['zeitgeist_context'] = ""
        selection['zeitgeist_persona'] = ""

        selection_method = st.session_state.single_lens_selection_method

        if selection_method == utils.SELECT_MANUAL:
            # v10.2: Cascading Filter System with Persona Integration
            from lenses import LENSES_HIERARCHY, LENSES_FUNCTIONAL, LENSES_BY_ERA, ERA_ORDER, SORTED_LENS_NAMES, SORTED_PERSONA_NAMES, PERSONA_METADATA, get_lens_data

            # v10.2: Scope toggle
            st.radio(
                "**Scope:**",
                ["Narrow", "Broad"],
                horizontal=True,
                index=0,
                help="Narrow: Select specific lens/persona. Broad: AI analyzes from general category perspective.",
                key="single_scope"
            )

            scope = st.session_state.get("single_scope", "Narrow")

            st.markdown("---")

            # Reset button in line with Filter Selection
            col_clear1, col_clear2 = st.columns([4, 1])
            with col_clear1:
                st.markdown("**Filter Selection:**")
            with col_clear2:
                if st.button("✕", key="reset_single", help="Clear all filters, lens, and persona"):
                    st.session_state.single_lens_select = None
                    st.session_state.single_persona_select = None
                    st.session_state.single_discipline_filter = "All Disciplines"
                    st.session_state.single_function_filter = "All Functions"
                    st.session_state.single_era_filter = "All Eras"
                    st.session_state.single_geographic_filter = "All Regions"
                    st.rerun()

            if scope == "Narrow":
                st.caption("Select any combination - filters cascade to show compatible options.")
            else:
                st.caption("Select category-level perspective - AI will analyze broadly without specific lens selection.")
                # v10.2: Clear lens and persona selections in session state when in Broad mode
                if st.session_state.get("single_lens_select"):
                    st.session_state.single_lens_select = None
                if st.session_state.get("single_persona_select") and st.session_state.get("single_persona_select") not in ["(AI Decides)", "(No Persona)"]:
                    st.session_state.single_persona_select = "(AI Decides)"

            # Get current filter states (including persona)
            current_discipline = st.session_state.get("single_discipline_filter", "All Disciplines")
            current_function = st.session_state.get("single_function_filter", "All Functions")
            current_era = st.session_state.get("single_era_filter", "All Eras")
            current_lens = st.session_state.get("single_lens_select")
            current_persona = st.session_state.get("single_persona_select")

            # v10.2: Calculate available options for ALL FIVE dropdowns
            # Rule: A dropdown should not restrict itself - each shows options based on OTHER selections

            available_disciplines = set(["All Disciplines"])
            available_functions = set(["All Functions"])
            available_eras = set(["All Eras"])
            available_lenses = []
            available_personas = []

            # For each lens, check if it matches the OTHER filters (not including current_lens)
            for lens_name in SORTED_LENS_NAMES:
                disc_match = (current_discipline == "All Disciplines" or lens_name in LENSES_HIERARCHY.get(current_discipline, []))
                func_match = (current_function == "All Functions" or lens_name in LENSES_FUNCTIONAL.get(current_function, []))
                era_match = (current_era == "All Eras" or lens_name in LENSES_BY_ERA.get(current_era, []))

                # Check if lens matches selected persona (if any)
                persona_match = True
                if current_persona and current_persona not in ["(AI Decides)", "(No Persona)"]:
                    persona_match = lens_name in PERSONA_METADATA[current_persona]['lenses']

                # If matches discipline + function + era + persona, add to available lenses
                if disc_match and func_match and era_match and persona_match:
                    available_lenses.append(lens_name)

                # For filter dropdowns: if lens matches OTHER TWO filters + persona, add its categories
                if func_match and era_match and persona_match:
                    for cat, lenses in LENSES_HIERARCHY.items():
                        if lens_name in lenses:
                            available_disciplines.add(cat)

                if disc_match and era_match and persona_match:
                    for tier, lenses in LENSES_FUNCTIONAL.items():
                        if lens_name in lenses:
                            available_functions.add(tier)

                if disc_match and func_match and persona_match:
                    lens_data = get_lens_data(lens_name)
                    if lens_data:
                        for era in lens_data.get('eras', []):
                            available_eras.add(era)

            # For each persona, check if it matches the OTHER filters (not including current_persona)
            for persona_name in SORTED_PERSONA_NAMES:
                persona_meta = PERSONA_METADATA[persona_name]

                disc_match = (current_discipline == "All Disciplines" or current_discipline in persona_meta['disciplines'])
                func_match = (current_function == "All Functions" or current_function in persona_meta['functions'])
                era_match = (current_era == "All Eras" or current_era in persona_meta['eras'])

                # Check if persona matches selected lens (if any)
                lens_match = True
                if current_lens and current_lens != "(No Lens Selected)":
                    lens_match = current_lens in persona_meta['lenses']

                # If matches all filters + lens, add to available personas
                if disc_match and func_match and era_match and lens_match:
                    available_personas.append(persona_name)

            # Convert to sorted lists
            available_disciplines = ["All Disciplines"] + sorted([d for d in available_disciplines if d != "All Disciplines"])
            available_functions = ["All Functions"] + sorted([f for f in available_functions if f != "All Functions"])
            available_eras_list = ["All Eras"] + [e for e in ERA_ORDER if e in available_eras]

            # Step 2: Render filter dropdowns with restricted options
            # v10.5: Restructured layout - Row 1: Discipline + Function, Row 2: Era + Geography

            # Row 1: Discipline + Function
            filter_row1_col1, filter_row1_col2 = st.columns(2)

            with filter_row1_col1:
                # Reset to "All" if current selection is no longer available
                if current_discipline not in available_disciplines:
                    current_discipline = "All Disciplines"

                # Show count inline with label
                from lenses import LENSES_HIERARCHY
                total_disciplines = len(LENSES_HIERARCHY)
                filtered_count = len([d for d in available_disciplines if d != "All Disciplines"])
                if filtered_count < total_disciplines:
                    disc_label = f"**Discipline** ({filtered_count}):"
                else:
                    disc_label = "**Discipline:**"

                discipline_filter = st.selectbox(
                    disc_label,
                    available_disciplines,
                    index=available_disciplines.index(current_discipline),
                    help="Filter by academic discipline",
                    key="single_discipline_filter"
                )

            with filter_row1_col2:
                # Reset to "All" if current selection is no longer available
                if current_function not in available_functions:
                    current_function = "All Functions"

                # Show count inline with label
                from lenses import LENSES_FUNCTIONAL
                total_functions = len(LENSES_FUNCTIONAL)
                filtered_count = len([f for f in available_functions if f != "All Functions"])
                if filtered_count < total_functions:
                    func_label = f"**Function Tier** ({filtered_count}):"
                else:
                    func_label = "**Function Tier:**"

                function_filter = st.selectbox(
                    func_label,
                    available_functions,
                    index=available_functions.index(current_function),
                    help="Filter by analytical tier (What/How/Why)",
                    key="single_function_filter"
                )

            # Row 2: Era + Geography
            filter_row2_col1, filter_row2_col2 = st.columns(2)

            with filter_row2_col1:
                # Reset to "All" if current selection is no longer available
                if current_era not in available_eras_list:
                    current_era = "All Eras"

                # Show count inline with label
                from lenses import ERA_ORDER
                total_eras = len(ERA_ORDER)
                filtered_count = len([e for e in available_eras_list if e != "All Eras"])
                if filtered_count < total_eras:
                    era_label = f"**Historical Era** ({filtered_count}):"
                else:
                    era_label = "**Historical Era:**"

                era_filter = st.selectbox(
                    era_label,
                    available_eras_list,
                    index=available_eras_list.index(current_era),
                    help="Filter by historical period",
                    key="single_era_filter"
                )

            with filter_row2_col2:
                # v10.5: Geographic filter
                from lenses import LENSES_GEOGRAPHIC
                geographic_regions = ["All Regions"] + sorted(list(LENSES_GEOGRAPHIC.keys()))
                current_geographic = st.session_state.get("single_geographic_filter", "All Regions")

                geographic_filter = st.selectbox(
                    "**Geographic Region:**",
                    geographic_regions,
                    index=geographic_regions.index(current_geographic) if current_geographic in geographic_regions else 0,
                    help="Filter by cultural-geographic region",
                    key="single_geographic_filter"
                )

            st.markdown("---")

            # Step 3: Lens and Persona selection (only visible in Narrow mode)
            if scope == "Narrow":
                col_lens, col_persona = st.columns([3, 2])

                with col_lens:
                    lens_options = ["(No Lens Selected)"] + available_lenses

                    # Handle case where current selection isn't in available list
                    try:
                        if current_lens and current_lens in lens_options:
                            index = lens_options.index(current_lens)
                        else:
                            index = 0
                    except (ValueError, TypeError):
                        index = 0

                    # Show filter count inline with label
                    total_lenses = len(SORTED_LENS_NAMES)
                    filtered_count = len(available_lenses)
                    if filtered_count < total_lenses:
                        lens_label = f"Select Lens ({filtered_count}):"
                    else:
                        lens_label = "Select Lens:"

                    selected_lens = st.selectbox(
                        lens_label,
                        options=lens_options,
                        index=index,
                        key="single_lens_select",
                        help=utils.get_lens_tooltip(current_lens) if current_lens and current_lens != "(No Lens Selected)" else "Choose from filtered lenses"
                    )

                    # Update selection
                    selection['lens'] = selected_lens if selected_lens != "(No Lens Selected)" else None

                    # Store filter context for AI
                    if selected_lens and selected_lens != "(No Lens Selected)":
                        selection['discipline_context'] = discipline_filter if discipline_filter != "All Disciplines" else None
                        selection['function_context'] = function_filter if function_filter != "All Functions" else None
                        selection['era_context'] = era_filter if era_filter != "All Eras" else None
                        selection['geographic_context'] = geographic_filter if geographic_filter != "All Regions" else None

                # v10.2: Persona selection - visible in Narrow mode, filtered by current selections
                with col_persona:
                    persona_options = ["(AI Decides)", "(No Persona)"] + available_personas

                    # Handle case where current selection isn't in available list
                    try:
                        if current_persona and current_persona in persona_options:
                            persona_index = persona_options.index(current_persona)
                        else:
                            persona_index = 0
                    except (ValueError, TypeError):
                        persona_index = 0

                    # Show filter count inline with label
                    total_personas = len(SORTED_PERSONA_NAMES)
                    filtered_count = len(available_personas)
                    if filtered_count < total_personas:
                        label = f"Specify Persona ({filtered_count}):"
                    else:
                        label = "Specify Persona:"

                    selected_persona = st.selectbox(
                        label,
                        options=persona_options,
                        index=persona_index,
                        key="single_persona_select",
                        help="Choose a specific historical figure, let AI decide from filtered pool, or use generic archetypal title"
                    )

                    # Update selection
                    if selected_persona == "(AI Decides)":
                        selection['persona'] = None
                    elif selected_persona == "(No Persona)":
                        selection['persona'] = "(No Persona)"
                    else:
                        selection['persona'] = selected_persona
            else:
                # Broad mode - clear lens and persona selections
                selection['lens'] = None
                selection['persona'] = None
        
        elif selection_method == utils.SELECT_SMART:
            st.info("🤖 **Smart Selection Activated.** The Janus 'Analyst-in-Chief' will choose the single most potent lens after analyzing your input.")
            # Clear manual selections to avoid state conflicts
            selection['lens'] = None
            selection['persona'] = None

    # Determine if configuration is complete (validation inside expander)
    is_configured = False
    if selection['is_zeitgeist']:
        if selection['zeitgeist_context'] and selection['zeitgeist_persona']:
            is_configured = True
    elif selection_method == utils.SELECT_SMART:
        is_configured = True
    elif selection_method == utils.SELECT_MANUAL:
        # v10.2: Validation with hierarchy priority
        scope = st.session_state.get("single_scope", "Narrow")
        discipline = st.session_state.get("single_discipline_filter", "All Disciplines")
        function = st.session_state.get("single_function_filter", "All Functions")
        era = st.session_state.get("single_era_filter", "All Eras")

        # Check for invalid selections
        persona_only_invalid = (selection['persona'] in ["(No Persona)", "(AI Decides)"] and
                               not selection['lens'] and
                               discipline == "All Disciplines" and
                               function == "All Functions" and
                               era == "All Eras")

        if persona_only_invalid:
            is_configured = False
        elif scope == "Broad":
            # Broad mode: at least one category filter must be selected
            geographic = st.session_state.get("single_geographic_filter", "All Regions")
            if discipline != "All Disciplines" or function != "All Functions" or era != "All Eras" or geographic != "All Regions":
                is_configured = True
                # Store filter selections as primary instructions
                selection['discipline_context'] = discipline if discipline != "All Disciplines" else None
                selection['function_context'] = function if function != "All Functions" else None
                selection['era_context'] = era if era != "All Eras" else None
                selection['geographic_context'] = geographic if geographic != "All Regions" else None
                selection['scope_mode'] = 'broad'
        else:
            # Narrow mode: requires meaningful selection
            geographic = st.session_state.get("single_geographic_filter", "All Regions")
            has_lens = selection.get('lens') is not None
            has_persona = selection.get('persona') not in [None, "(AI Decides)", "(No Persona)"]
            has_filters = (discipline != "All Disciplines" or function != "All Functions" or era != "All Eras" or geographic != "All Regions")

            if has_lens or has_persona or has_filters:
                is_configured = True
                selection['scope_mode'] = 'narrow'
                # Store filter context
                selection['discipline_context'] = discipline if discipline != "All Disciplines" else None
                selection['function_context'] = function if function != "All Functions" else None
                selection['era_context'] = era if era != "All Eras" else None
                selection['geographic_context'] = geographic if geographic != "All Regions" else None

    # Show status message if configuration incomplete
    st.markdown("---")
    if not is_configured:
        st.info("Complete your configuration above to proceed with execution.")

# --- STEP 3: EXECUTION (Shows when configuration is valid) ---
if not is_configured:
    st.stop()  # Stop rendering if config not complete

# Construct header text
if selection['is_zeitgeist']:
    header_text = "Analysis | Zeitgeist Simulation Mode"
elif selection_method == utils.SELECT_SMART:
    header_text = "Analysis | Smart Selection"
else: # Manual
    header_text = f"Analysis | Lens: {selection['lens']}"
    if selection['persona']:
        header_text += f" | Persona: {selection['persona']}"

st.markdown("---")
st.header(header_text)

# Execution Button
button_label = "Execute Analysis Engine"
if st.session_state.single_lens_state == 'executed':
    button_label = "Re-Execute Analysis (Start Over)"

if st.button(button_label, type="primary", width="stretch"):
    # If re-executing, reset state first (this also cleans up old files)
    if st.session_state.single_lens_state == 'executed':
        reset_analysis_state()

    # --- Centralized Execution Block ---
    st.markdown("---")

    # v10.2: Create container for displaying strategy during execution
    st.subheader("🧠 Analysis Strategy")
    st.caption("Generated strategy appears here as the analysis begins:")
    strategy_display = st.container()

    try:
        analysis_result, raw_analyses, strategies = utils.run_analysis_pipeline(
            work_input=work_a,
            manual_configs=[selection] if selection_method == utils.SELECT_MANUAL or selection['is_zeitgeist'] else [],
            smart_select_count=1,
            page_key_prefix='single',
            stream_container=None,
            strategy_container=strategy_display
        )

        if analysis_result:
            # Update session state on success
            st.session_state.single_lens_result = analysis_result
            st.session_state.single_lens_strategy = strategies[0] if strategies else None
            st.session_state.single_lens_state = 'executed'
    finally:
        # If successful, we need the cache for refinement. Only clean up on failure.
        if st.session_state.single_lens_state != 'executed':
            work_a.cleanup_gemini_file()

# --- DISPLAY RESULTS FROM SESSION STATE ---
if st.session_state.single_lens_state == 'executed' and st.session_state.single_lens_result:
    st.markdown("---")
    st.subheader("📄 Analysis Result")
    st.markdown(st.session_state.single_lens_result)

# --- EXPORT BUTTONS ---
if st.session_state.single_lens_state == 'executed' and st.session_state.single_lens_result:
    st.markdown("---")
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    col1, col2 = st.columns(2)
    with col1:
        markdown_export = utils.create_export_content(
            result_text=st.session_state.single_lens_result,
            work_input=work_a,
            analysis_type="Single Lens",
            config_info=selection,
            format_type="markdown"
        )
        st.download_button(
            label="📥 Download as Markdown",
            data=markdown_export,
            file_name=f"janus_single_lens_{timestamp}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_single_md"
        )
    with col2:
        text_export = utils.create_export_content(
            result_text=st.session_state.single_lens_result,
            work_input=work_a,
            analysis_type="Single Lens",
            config_info=selection,
            format_type="text"
        )
        st.download_button(
            label="📥 Download as Text",
            data=text_export,
            file_name=f"janus_single_lens_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_single_txt"
        )

    # v10.2: Display metadata after completion
    st.markdown("---")
    utils.display_metadata(work_a, label=work_a.get_display_title())

# --- REFINEMENT LOOP ---
# v10.2: This section is only displayed after execution completes

if st.session_state.single_lens_state == 'executed' and st.session_state.single_lens_result:
    st.markdown("---")
    st.subheader("🔄 Refinement Loop")
    with st.container(border=True):
        st.write("Provide instructions to iteratively refine the analysis above.")
        refinement_instruction = st.text_area("Refinement Instruction:", height=100, key="refinement_instruction", placeholder="e.g., 'Focus more deeply on the symbolism of the color blue', or 'Make the tone more academic and less conversational.'")

        if st.button("Refine Analysis", type="secondary"):
            if not refinement_instruction:
                st.warning("Please enter a refinement instruction.")
            else:
                # Set a flag to run the refinement logic on the next script rerun.
                # This avoids the error caused by modifying widget state after it's been drawn.
                st.session_state.run_refinement_on_next_load = True
                st.session_state.instruction_to_run = refinement_instruction
                st.rerun()
                # The actual execution now happens at the top of the script in the next run