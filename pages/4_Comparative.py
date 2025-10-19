import streamlit as st
import utils
# v9.4b: LENS_ZEITGEIST constant is removed from utils.
from utils import WorkInput

# --- CONSTANTS ---
# v9.4b: Define specific modes for this page including Zeitgeist
MODE_STANDARD = "Standard (Common Lens)"
MODE_ZEITGEIST = "Zeitgeist Simulation (Common Context)"

# --- CALLBACKS ---
# v10.1: Updated to clear new filter widgets
def handle_comparative_mode_change():
    """Callback to clear selections when the mode changes (Standard vs Zeitgeist)."""
    # Reset the selection data structure
    st.session_state.comparative_selection_method = utils.SELECT_MANUAL # Default back to manual on mode change
    st.session_state.comparative_selection = {'lens': None, 'persona': None, 'is_zeitgeist': False, 'zeitgeist_context': "", 'zeitgeist_persona': ""}
    # Clear specific UI widget states to prevent state conflicts
    if 'comparative_lens_select' in st.session_state: del st.session_state.comparative_lens_select
    # Clear filter widgets
    if 'comparative_discipline_filter' in st.session_state:
        st.session_state.comparative_discipline_filter = "All Disciplines"
    if 'comparative_function_filter' in st.session_state:
        st.session_state.comparative_function_filter = "All Functions"
    if 'comparative_era_filter' in st.session_state:
        st.session_state.comparative_era_filter = "All Eras"
    if 'comparative_geographic_filter' in st.session_state:
        st.session_state.comparative_geographic_filter = "All Regions"
    # Do NOT call reset_analysis_state here, as it clears results prematurely.

# v10.2: Reset callback for analysis state
def reset_comparative_state():
    """Reset analysis results and cleanup files."""
    utils.reset_page_state('comparative')
    st.session_state.work_input_comparative_a.cleanup_gemini_file()
    st.session_state.work_input_comparative_b.cleanup_gemini_file()


# --- PAGE SETUP ---
# v10.2: Update page title
PAGE_TITLE = "Janus | Comparative"
utils.initialize_page_config(PAGE_TITLE)
st.title("4 | Comparative (2 Works)")
st.write("Analyze TWO different works through the SAME analytical framework.")

# --- SIDEBAR (Global Settings Only) ---
utils.render_sidebar_settings()

# --- PAGE MEMORY MANAGEMENT ---
# Clean up uploaded files from other pages to prevent memory accumulation
if 'current_page' not in st.session_state:
    st.session_state.current_page = None

if st.session_state.current_page != "comparative":
    st.session_state.current_page = "comparative"
    utils.cleanup_other_pages_files("comparative")

# Initialize Session State
if 'comparative_selection' not in st.session_state:
    # v9.4b: Updated structure
    st.session_state.comparative_selection = {'lens': None, 'persona': None, 'is_zeitgeist': False, 'zeitgeist_context': "", 'zeitgeist_persona': ""}

if 'comparative_analysis_mode' not in st.session_state:
    # Stores the overall mode (Standard or Zeitgeist)
    st.session_state.comparative_analysis_mode = MODE_STANDARD
if 'comparative_selection_method' not in st.session_state:
    # Stores the method within Standard mode (Manual or Smart)
    st.session_state.comparative_selection_method = utils.SELECT_MANUAL

if 'work_input_comparative_a' not in st.session_state:
    st.session_state.work_input_comparative_a = WorkInput()
if 'work_input_comparative_b' not in st.session_state:
    st.session_state.work_input_comparative_b = WorkInput()

# v10.2: Initialize state for Refinement Loop
if 'comparative_state' not in st.session_state:
    st.session_state.comparative_state = 'config'  # 'config' or 'executed'
if 'comparative_result' not in st.session_state:
    st.session_state.comparative_result = None
if 'comparative_strategies' not in st.session_state:
    st.session_state.comparative_strategies = None
if 'comparative_analyses' not in st.session_state:
    st.session_state.comparative_analyses = None

# v10.1: Handle Library Pre-selection (MUST happen before any widgets are created)
if 'library_selected_lens' in st.session_state:
    preselected_lens = st.session_state.library_selected_lens
    # Turn off Zeitgeist mode
    st.session_state.comparative_analysis_mode = MODE_STANDARD
    # Reset filters to ensure pre-selected lens is visible
    st.session_state.comparative_discipline_filter = "All Disciplines"
    st.session_state.comparative_function_filter = "All Functions"
    st.session_state.comparative_era_filter = "All Eras"
    st.session_state.comparative_geographic_filter = "All Regions"
    # Set the lens selection
    st.session_state.comparative_lens_select = preselected_lens
    # Clear the flag (one-time use)
    del st.session_state.library_selected_lens
    st.rerun()

# v10.2: Refinement execution logic (moved to top of script)
if st.session_state.get("run_comparative_refinement"):
    st.session_state.run_comparative_refinement = False
    instruction = st.session_state.get("comparative_refinement_instruction", "")
    if instruction:
        refinement_area = st.container()
        with refinement_area:
            refined_result = utils.generate_refined_comparative_synthesis(
                st.session_state.work_input_comparative_a,
                st.session_state.work_input_comparative_b,
                st.session_state.comparative_result,
                instruction
            )
            if refined_result:
                st.session_state.comparative_result = refined_result
                st.session_state.comparative_refinement_text_input = ""
                st.rerun()

# --- MAIN PAGE LAYOUT ---
selection = st.session_state.comparative_selection
analysis_mode = st.session_state.comparative_analysis_mode
selection_method = st.session_state.comparative_selection_method

work_a = st.session_state.work_input_comparative_a
work_b = st.session_state.work_input_comparative_b
api_key = st.session_state.get("api_key", "")

# --- STEP 1: INPUT WORKS (Always visible first) ---

# v10.2: API Key Warning Banner
if not st.session_state.get("api_key"):
    st.warning("⚠️ API Key Required — Please configure on Home page to use the engine")

st.header("📄 Input Works for Comparison")
st.caption("Upload your creative works or enter text to begin")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 🏛️ Work A")
    utils.handle_input_ui(work_a, st.container(border=True), "work_a", on_change_callback=reset_comparative_state)

with col_b:
    st.markdown("### 🏛️ Work B")
    utils.handle_input_ui(work_b, st.container(border=True), "work_b", on_change_callback=reset_comparative_state)

# Check if works are ready
works_are_ready = work_a.is_ready() and work_b.is_ready()

if not works_are_ready:
    st.info("👆 Please upload files or enter text for both works above to proceed with configuration.")
    st.stop()  # Stop rendering here until both works are provided

# --- STEP 2: CONFIGURATION & FRAMEWORK SELECTION (Only appears after works are ready) ---
st.markdown("---")
with st.expander("🔬 Configuration & Framework Selection", expanded=True):

    # v10.2: Zeitgeist toggle on same line as Selection Method (mirroring Single Lens/Dialectical)
    # === ZEITGEIST MODE UI ===
    if analysis_mode == MODE_ZEITGEIST:
        # v10.2: Zeitgeist toggle (allows deactivation)
        zeitgeist_header_col, zeitgeist_toggle_col = st.columns([3, 1])
        with zeitgeist_header_col:
            st.info("🕰️ **Zeitgeist Simulation Activated.** Define the common historical context and witness persona.")
        with zeitgeist_toggle_col:
            deactivate_zeitgeist = st.toggle(
                "Activate Zeitgeist",
                value=True,
                on_change=handle_comparative_mode_change,
                help="Switch back to Standard mode"
            )

        # Handle deactivation
        if not deactivate_zeitgeist:
            st.session_state.comparative_analysis_mode = MODE_STANDARD
            st.rerun()

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
        # v10.2: Selection Method and Zeitgeist toggle on same line (mirroring Single Lens/Dialectical)
        method_col, zeitgeist_col = st.columns([3, 1])
        with method_col:
            st.radio(
                "**Selection Method:**",
                utils.SELECTION_MODES,
                horizontal=True,
                key="comparative_selection_method"
            )
        with zeitgeist_col:
            activate_zeitgeist = st.toggle(
                "Activate Zeitgeist",
                value=False,
                on_change=handle_comparative_mode_change,
                help="Switch to Zeitgeist Simulation mode (Common Context)"
            )

        # Update the analysis mode based on the toggle
        if activate_zeitgeist:
            st.session_state.comparative_analysis_mode = MODE_ZEITGEIST
            analysis_mode = MODE_ZEITGEIST
            selection['is_zeitgeist'] = True
            selection['lens'] = None
            selection['persona'] = None
            st.rerun()

        selection_method = st.session_state.comparative_selection_method

        # v10.2: Add Scope toggle for Manual mode
        if selection_method == utils.SELECT_MANUAL:
            st.markdown("---")
            st.radio(
                "**Scope:**",
                ["Narrow", "Broad"],
                horizontal=True,
                index=0,
                help="Narrow: Select specific lens or let AI choose. Broad: AI analyzes from broad category perspective.",
                key="comparative_scope"
            )

        if selection_method == utils.SELECT_MANUAL:
            # v10.2: Get scope mode and clear lens/persona in Broad mode
            scope = st.session_state.get("comparative_scope", "Narrow")

            st.markdown("---")
            if scope == "Narrow":
                st.caption("Select the common lens for comparison.")
            else:
                st.caption("Filter-based analysis (AI will analyze from category perspective).")
                # v10.2: Clear lens and persona selections in session state when in Broad mode
                if st.session_state.get("comparative_lens_select"):
                    st.session_state.comparative_lens_select = None
                if st.session_state.get("comparative_persona_select") and st.session_state.get("comparative_persona_select") not in ["(AI Decides)", "(No Persona)"]:
                    st.session_state.comparative_persona_select = "(AI Decides)"

            # v10.2: Cascading Filter System with Persona Integration
            from lenses import SORTED_LENS_NAMES, PERSONA_METADATA, SORTED_PERSONA_NAMES

            # Reset button
            col_clear1, col_clear2 = st.columns([4, 1])
            with col_clear1:
                st.markdown("**Filter Selection:**")
            with col_clear2:
                # v10.2: Clear button - rely on Streamlit's automatic rerun instead of explicit st.rerun()
                if st.button("✕", key="reset_comparative", help="Clear all filters, lens, and persona"):
                    st.session_state.comparative_lens_select = None
                    st.session_state.comparative_discipline_filter = "All Disciplines"
                    st.session_state.comparative_function_filter = "All Functions"
                    st.session_state.comparative_era_filter = "All Eras"
                    st.session_state.comparative_geographic_filter = "All Regions"
                    if 'comparative_persona_select' in st.session_state:
                        st.session_state.comparative_persona_select = "(AI Decides)"

            if scope == "Narrow":
                st.caption("Select any combination - filters cascade to show compatible options.")
            else:
                st.caption("Filter-based analysis (AI will analyze from category perspective).")

            # Get current filter states (including persona)
            current_discipline = st.session_state.get("comparative_discipline_filter", "All Disciplines")
            current_function = st.session_state.get("comparative_function_filter", "All Functions")
            current_era = st.session_state.get("comparative_era_filter", "All Eras")
            current_lens = st.session_state.get("comparative_lens_select")
            current_persona = st.session_state.get("comparative_persona_select", "(AI Decides)")
            if current_lens == "(No Lens Selected)":
                current_lens = None

            # v10.2: Bidirectional cascading logic (matching Single Lens)
            # Rule: Each dropdown filters based on ALL OTHER selections (not including itself)
            from lenses import LENSES_HIERARCHY, LENSES_FUNCTIONAL, LENSES_BY_ERA, get_lens_data

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
            from lenses import ERA_ORDER
            available_eras_list = ["All Eras"] + [e for e in ERA_ORDER if e in available_eras]

            # Render filter dropdowns with inline counts
            # v10.5: Restructured layout - Row 1: Discipline + Function, Row 2: Era + Geography

            # Row 1: Discipline + Function
            filter_row1_col1, filter_row1_col2 = st.columns(2)

            with filter_row1_col1:
                # Reset to "All" if current selection is no longer available
                if current_discipline not in available_disciplines:
                    current_discipline = "All Disciplines"

                # Show count inline with label
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
                    key="comparative_discipline_filter"
                )

            with filter_row1_col2:
                # Reset to "All" if current selection is no longer available
                if current_function not in available_functions:
                    current_function = "All Functions"

                # Show count inline with label
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
                    key="comparative_function_filter"
                )

            # Row 2: Era + Geography
            filter_row2_col1, filter_row2_col2 = st.columns(2)

            with filter_row2_col1:
                # Reset to "All" if current selection is no longer available
                if current_era not in available_eras_list:
                    current_era = "All Eras"

                # Show count inline with label
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
                    key="comparative_era_filter"
                )

            with filter_row2_col2:
                # v10.5: Geographic filter
                from lenses import LENSES_GEOGRAPHIC
                geographic_regions = ["All Regions"] + sorted(list(LENSES_GEOGRAPHIC.keys()))
                current_geographic = st.session_state.get("comparative_geographic_filter", "All Regions")

                geographic_filter = st.selectbox(
                    "**Geographic Region:**",
                    geographic_regions,
                    index=geographic_regions.index(current_geographic) if current_geographic in geographic_regions else 0,
                    help="Filter by cultural-geographic region",
                    key="comparative_geographic_filter"
                )

            st.markdown("---")

            # v10.2: Lens and Persona selection only visible in Narrow mode
            if scope == "Narrow":
                # Lens selection (full width)
                total_lenses = len(SORTED_LENS_NAMES)
                filtered_count = len(available_lenses)
                if filtered_count < total_lenses:
                    lens_label = f"**Lens** ({filtered_count}):"
                else:
                    lens_label = "**Lens:**"

                # Handle case where current selection isn't in available list
                try:
                    if current_lens and current_lens in available_lenses:
                        lens_index = available_lenses.index(current_lens)
                    else:
                        lens_index = None
                except (ValueError, TypeError):
                    lens_index = None

                selected_lens = st.selectbox(
                    lens_label,
                    options=available_lenses,
                    index=lens_index,
                    placeholder="Select lens...",
                    key="comparative_lens_select",
                    help=utils.get_lens_tooltip(current_lens) if current_lens else "Choose from filtered lenses"
                )

                selection['lens'] = selected_lens

                # Store filter context for AI
                selection['discipline_context'] = discipline_filter if discipline_filter != "All Disciplines" else None
                selection['function_context'] = function_filter if function_filter != "All Functions" else None
                selection['era_context'] = era_filter if era_filter != "All Eras" else None
                selection['geographic_context'] = geographic_filter if geographic_filter != "All Regions" else None

                # v10.2: Persona selection (full width, below lens) - ALWAYS shown
                # Show inline count for personas
                total_personas = len(SORTED_PERSONA_NAMES)
                filtered_count_p = len(available_personas)
                if filtered_count_p < total_personas:
                    persona_label = f"**Persona** ({filtered_count_p}):"
                else:
                    persona_label = "**Persona:**"

                # Build persona options
                persona_options = ["(AI Decides)", "(No Persona)"] + available_personas

                # Handle case where current selection isn't in available list
                try:
                    if current_persona in persona_options:
                        persona_index = persona_options.index(current_persona)
                    else:
                        persona_index = 0
                except (ValueError, TypeError):
                    persona_index = 0

                selected_persona = st.selectbox(
                    persona_label,
                    options=persona_options,
                    index=persona_index,
                    key="comparative_persona_select",
                    help="Choose a specific historical figure, let AI decide from filtered pool, or use generic archetypal title"
                )

                # Update selection - map special values
                if selected_persona == "(AI Decides)":
                    selection['persona'] = None
                elif selected_persona == "(No Persona)":
                    selection['persona'] = "(No Persona)"
                else:
                    selection['persona'] = selected_persona
            else:
                # Broad mode - clear lens and persona from config
                selection['lens'] = None
                selection['persona'] = None
                # Store filter context for AI in Broad mode
                selection['discipline_context'] = discipline_filter if discipline_filter != "All Disciplines" else None
                selection['function_context'] = function_filter if function_filter != "All Functions" else None
                selection['era_context'] = era_filter if era_filter != "All Eras" else None
                selection['geographic_context'] = geographic_filter if geographic_filter != "All Regions" else None
                selection['scope_mode'] = 'broad'
        
        elif selection_method == utils.SELECT_SMART:
            st.info("🤖 **Smart Selection Activated.** The Janus 'Comparative Strategist' will choose the single most potent lens to bridge your two inputs.")
            # Clear manual selections to avoid state conflicts
            selection['lens'] = None
            selection['persona'] = None


# --- STEP 3: EXECUTION (Shows when configuration is valid) ---

# v10.2: Determine readiness based on mode and flexible validation
is_configured = False
header_text = "Analysis"
if analysis_mode == MODE_ZEITGEIST:
    if selection['zeitgeist_context'] and selection['zeitgeist_persona']:
        is_configured = True
        header_text = "Analysis | Zeitgeist Simulation (Common Context)"
elif analysis_mode == MODE_STANDARD:
    if selection_method == utils.SELECT_SMART:
        is_configured = True
        header_text = "Analysis | Smart Selection"
    elif selection_method == utils.SELECT_MANUAL:
        # v10.2: Flexible validation - accept lens, persona, OR filters
        scope = st.session_state.get("comparative_scope", "Narrow")
        has_lens = selection.get('lens') is not None
        has_persona = selection.get('persona') not in [None, "(No Persona)"]
        has_filters = (
            st.session_state.get("comparative_discipline_filter", "All Disciplines") != "All Disciplines" or
            st.session_state.get("comparative_function_filter", "All Functions") != "All Functions" or
            st.session_state.get("comparative_era_filter", "All Eras") != "All Eras" or
            st.session_state.get("comparative_geographic_filter", "All Regions") != "All Regions"
        )

        if has_lens or has_persona or has_filters:
            is_configured = True
            # Store scope_mode in selection
            selection['scope_mode'] = scope.lower()

            # Build header text
            if scope == "Narrow":
                if has_lens:
                    header_text = f"Analysis | Lens: {selection['lens']}"
                    if has_persona:
                        header_text += f" | Persona: {selection['persona']}"
                elif has_persona:
                    header_text = f"Analysis | Persona: {selection['persona']}"
                elif has_filters:
                    header_text = "Analysis | Filter-based Selection"
            else:  # Broad mode
                header_text = "Analysis | Broad Category Perspective"

# Show status message if configuration incomplete
st.markdown("---")
if not is_configured:
    st.info("Complete your configuration above to proceed with execution.")
    st.stop()  # Stop rendering if config not complete

# Construct header text
st.header(header_text)

# Execution Button
# Change button label if already executed
button_label = "Execute Analysis Engine"
if st.session_state.comparative_state == 'executed':
    button_label = "Re-Execute Analysis (Start Over)"

if st.button(button_label, type="primary", width="stretch"):
    # If re-executing, reset state first (this also cleans up old files)
    if st.session_state.comparative_state == 'executed':
        reset_comparative_state()

    # --- Centralized Execution Block ---
    st.markdown("---")

    # v10.2: Create container for displaying strategy during execution
    st.subheader("🧠 Analysis Strategy")
    st.caption("Generated strategy appears here as the analysis begins:")
    strategy_display = st.container()

    try:
        synthesis_text, analysis_a_text, analysis_b_text, strategy_a, strategy_b = utils.run_comparative_analysis_pipeline(
            work_a=work_a,
            work_b=work_b,
            selection_method=selection_method,
            manual_lens_config=selection,
            strategy_container=strategy_display
        )

        if synthesis_text:
            # v10.2: Update session state
            st.session_state.comparative_result = synthesis_text
            st.session_state.comparative_state = 'executed'
            st.session_state.comparative_strategies = (strategy_a, strategy_b)
            st.session_state.comparative_analyses = (analysis_a_text, analysis_b_text)
        else:
            # The pipeline function will show specific errors.
            st.error("The comparative analysis pipeline did not complete successfully.")

    finally:
        # v10.2: Only cleanup if execution failed
        if st.session_state.comparative_state != 'executed':
            work_a.cleanup_gemini_file()
            work_b.cleanup_gemini_file()


# --- DISPLAY RESULTS FROM SESSION STATE ---
if st.session_state.comparative_state == 'executed' and st.session_state.comparative_result:
    # v10.2: Display result
    st.markdown("---")
    st.subheader("📄 Comparative Synthesis Result")
    st.markdown(st.session_state.comparative_result)

    # v10.2: Export buttons
    st.markdown("---")
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    col1, col2 = st.columns(2)
    with col1:
        markdown_export = utils.create_export_content(
            result_text=st.session_state.comparative_result,
            work_input=work_a,
            analysis_type="Comparative",
            config_info=selection,
            work_input_b=work_b,
            format_type="markdown"
        )
        st.download_button(
            label="📥 Download as Markdown",
            data=markdown_export,
            file_name=f"janus_comparative_{timestamp}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_comparative_md"
        )
    with col2:
        text_export = utils.create_export_content(
            result_text=st.session_state.comparative_result,
            work_input=work_a,
            analysis_type="Comparative",
            config_info=selection,
            work_input_b=work_b,
            format_type="text"
        )
        st.download_button(
            label="📥 Download as Text",
            data=text_export,
            file_name=f"janus_comparative_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_comparative_txt"
        )

    # v10.2: Display metadata AFTER result
    st.markdown("---")
    utils.display_metadata(work_a, label=f"Work A: {work_a.get_display_title()}")
    utils.display_metadata(work_b, label=f"Work B: {work_b.get_display_title()}")

    # Display the raw analyses for reference
    if st.session_state.comparative_analyses:
        analysis_a_text, analysis_b_text = st.session_state.comparative_analyses
        st.markdown("---")
        st.subheader("Source Analyses (Reference)")
        with st.expander(f"View Raw Analysis A: {work_a.get_display_title()}"):
            st.markdown(analysis_a_text)
        with st.expander(f"View Raw Analysis B: {work_b.get_display_title()}"):
            st.markdown(analysis_b_text)

# v10.2: REFINEMENT LOOP
# This section is only displayed after execution completes
if st.session_state.comparative_state == 'executed' and st.session_state.comparative_result:
    st.markdown("---")
    st.subheader("🔄 Refinement Loop")
    with st.container(border=True):
        st.write("Provide instructions to iteratively refine the comparative synthesis above.")
        refinement_instruction = st.text_area(
            "Refinement Instruction:",
            height=100,
            key="comparative_refinement_text_input",
            placeholder="e.g., 'Emphasize the structural differences more', 'Add more specific examples from both works'"
        )

        if st.button("Refine Analysis", type="secondary"):
            if not refinement_instruction:
                st.warning("Please enter a refinement instruction.")
            else:
                # Set a flag to run the refinement logic on the next script rerun
                st.session_state.run_comparative_refinement = True
                st.session_state.comparative_refinement_instruction = refinement_instruction
                st.rerun()