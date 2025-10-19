import streamlit as st
import utils
import re
from utils import WorkInput, SELECT_MANUAL, SELECT_SMART, SELECTION_MODES

# --- CALLBACKS ---
# v10.0.15: Centralize reset logic
def reset_analysis_state():
    utils.reset_page_state('symposium')

def handle_symposium_mode_change():
    """Callback to clear selections when the mode changes (Manual vs Smart)."""
    # v10.1: Updated to clear new filter widgets
    st.session_state.symposium_selection_data = []
    # Clear UI widgets - need to clear for all possible perspectives (up to 6)
    for i in range(6):
        if f'symposium_lens_{i}' in st.session_state:
            del st.session_state[f'symposium_lens_{i}']
        if f'symposium_discipline_filter_{i}' in st.session_state:
            st.session_state[f'symposium_discipline_filter_{i}'] = "All Disciplines"
        if f'symposium_function_filter_{i}' in st.session_state:
            st.session_state[f'symposium_function_filter_{i}'] = "All Functions"
        if f'symposium_era_filter_{i}' in st.session_state:
            st.session_state[f'symposium_era_filter_{i}'] = "All Eras"
        if f'symposium_geographic_filter_{i}' in st.session_state:
            st.session_state[f'symposium_geographic_filter_{i}'] = "All Regions"
    reset_analysis_state()

# --- PAGE SETUP ---
# v10.2: Update page title
PAGE_TITLE = "Janus | Symposium"
utils.initialize_page_config(PAGE_TITLE)
st.title("3 | Symposium (3+ Perspectives)")
st.write("Analyze ONE work through THREE or more perspectives, synthesized into a roundtable dialogue.")

# --- SIDEBAR (Global Settings Only) ---
utils.render_sidebar_settings()

# --- PAGE MEMORY MANAGEMENT ---
# Clean up uploaded files from other pages to prevent memory accumulation
if 'current_page' not in st.session_state:
    st.session_state.current_page = None

if st.session_state.current_page != "symposium":
    st.session_state.current_page = "symposium"
    utils.cleanup_other_pages_files("symposium")

# Initialize Session State for this page
if 'symposium_selection_data' not in st.session_state:
    st.session_state.symposium_selection_data = []
if 'symposium_selection_method' not in st.session_state:
    st.session_state.symposium_selection_method = SELECT_MANUAL
if 'symposium_num_perspectives' not in st.session_state:
    st.session_state.symposium_num_perspectives = 3
if 'symposium_smart_select_count' not in st.session_state:
    st.session_state.symposium_smart_select_count = 3
if 'symposium_configs' not in st.session_state:
    st.session_state.symposium_configs = []
if 'work_input_symposium' not in st.session_state:
    st.session_state.work_input_symposium = WorkInput()

# Add state for Refinement Loop
if 'symposium_state' not in st.session_state:
    st.session_state.symposium_state = 'config'
if 'symposium_result' not in st.session_state:
    st.session_state.symposium_result = None
if 'symposium_raw_analyses' not in st.session_state:
    st.session_state.symposium_raw_analyses = None
if 'symposium_strategies' not in st.session_state:
    st.session_state.symposium_strategies = None

# v10.1: Handle Library Cart Pre-selection (MUST happen before any widgets are created)
if 'library_symposium_cart' in st.session_state and st.session_state.library_symposium_cart:
    cart = st.session_state.library_symposium_cart
    if len(cart) >= 3:
        # Reset filters and set lenses for all cart items
        for i, lens_name in enumerate(cart):
            st.session_state[f'symposium_discipline_filter_{i}'] = "All Disciplines"
            st.session_state[f'symposium_function_filter_{i}'] = "All Functions"
            st.session_state[f'symposium_era_filter_{i}'] = "All Eras"
            st.session_state[f'symposium_geographic_filter_{i}'] = "All Regions"
            st.session_state[f'symposium_lens_{i}'] = lens_name
        # Set number of perspectives to match cart size
        st.session_state.symposium_num_perspectives = len(cart)
        # Clear the cart (one-time use)
        st.session_state.library_symposium_cart = []
        st.rerun()

# --- REFINEMENT EXECUTION LOGIC ---
if st.session_state.get("run_refinement_on_next_load"):
    st.session_state.run_refinement_on_next_load = False
    instruction = st.session_state.get("instruction_to_run", "")
    if instruction:
        refined_result = utils.generate_refined_analysis(
            st.session_state.work_input_symposium,
            st.session_state.symposium_result,
            instruction
        )
        if refined_result:
            st.session_state.symposium_result = refined_result
            st.session_state.refinement_instruction = ""
            st.rerun()

# --- MAIN PAGE LAYOUT ---
selection_method = st.session_state.symposium_selection_method
work_a = st.session_state.work_input_symposium
api_key = st.session_state.get("api_key", "")

# --- STEP 1: INPUT WORK (Always visible first) ---

# v10.2: API Key Warning Banner
if not st.session_state.get("api_key"):
    st.warning("⚠️ API Key Required — Please configure on Home page to use the engine")

st.header("📄 Input Work")
st.caption("Upload your creative work or enter text to begin")
utils.handle_input_ui(work_a, st.container(border=True), "work_symposium", on_change_callback=reset_analysis_state)

# Check if work is ready
work_is_ready = work_a.is_ready()

if not work_is_ready:
    st.info("👆 Please upload a file or enter text above to proceed with configuration.")
    st.stop()  # Stop rendering here until work is provided

# --- STEP 2: CONFIGURATION & PERSPECTIVE SELECTION (Only appears after work is ready) ---
st.markdown("---")
with st.expander("🔬 Configuration & Perspective Selection", expanded=True):
    st.radio(
        "**Selection Method:**",
        SELECTION_MODES,
        horizontal=True,
        key="symposium_selection_method"
    )
    selection_method = st.session_state.symposium_selection_method

    # v10.2: Add Scope toggle for Manual mode
    if selection_method == SELECT_MANUAL:
        st.markdown("---")
        st.radio(
            "**Scope:**",
            ["Narrow", "Broad"],
            horizontal=True,
            index=0,
            help="Narrow: Select specific lenses or let AI choose. Broad: AI analyzes from broad category perspectives.",
            key="symposium_scope"
        )

    if selection_method == SELECT_MANUAL:
        # v10.2: Get scope mode
        scope = st.session_state.get("symposium_scope", "Narrow")

        st.markdown("---")
        if scope == "Narrow":
            st.caption("Configure each perspective with specific lenses or filters.")
        else:
            st.caption("Filter-based analysis (AI will analyze from broad category perspectives).")

        # v10.1: Unified Filter System (replaces view toggle)
        # Import filter data structures
        from lenses import LENSES_HIERARCHY, LENSES_FUNCTIONAL, LENSES_BY_ERA, ERA_ORDER, SORTED_LENS_NAMES, PERSONA_METADATA, SORTED_PERSONA_NAMES, get_lens_data

        # v10.0.19: New UI for selecting number of perspectives with Reset All button
        num_col, reset_col = st.columns([4, 1])
        with num_col:
            num_perspectives = st.number_input(
                "Number of Perspectives:",
                min_value=3,
                max_value=6,
                step=1,
                key="symposium_num_perspectives",
            )
        with reset_col:
            st.markdown("")  # Spacing to align with number input
            if st.button("🔄 Reset All", key="reset_all_symposium", help="Clear all perspectives"):
                # Clear all perspective configurations for all 6 possible slots
                for i in range(6):
                    st.session_state[f'symposium_discipline_filter_{i}'] = "All Disciplines"
                    st.session_state[f'symposium_function_filter_{i}'] = "All Functions"
                    st.session_state[f'symposium_era_filter_{i}'] = "All Eras"
                    st.session_state[f'symposium_geographic_filter_{i}'] = "All Regions"
                    st.session_state[f'symposium_lens_{i}'] = None
                    if f'symposium_persona_{i}' in st.session_state:
                        st.session_state[f'symposium_persona_{i}'] = "(AI Decides)"
                    if f'symposium_type_{i}' in st.session_state:
                        st.session_state[f'symposium_type_{i}'] = "Library Lens"
                    if f'symposium_z_context_{i}' in st.session_state:
                        st.session_state[f'symposium_z_context_{i}'] = ""
                    if f'symposium_z_witness_{i}' in st.session_state:
                        st.session_state[f'symposium_z_witness_{i}'] = ""
                # Reset configs
                st.session_state.symposium_configs = []
                st.rerun()

        st.markdown("---")

        # v10.0.32: Ensure the persistent config list matches the desired number of perspectives
        current_configs = st.session_state.symposium_configs
        if len(current_configs) != num_perspectives:
            # Resize the list, preserving existing configs where possible
            new_configs = current_configs[:num_perspectives]
            while len(new_configs) < num_perspectives:
                new_configs.append({'lens': None, 'persona': None, 'is_zeitgeist': False})
            st.session_state.symposium_configs = new_configs

        # Dynamically generate selection UI for each perspective
        # v10.0.20: New layout logic to wrap columns for better UX
        MAX_COLS_PER_ROW = 3
        # Create a list to hold the column objects for the current row
        row_cols = []

        for i in range(num_perspectives):
            # Start a new row every MAX_COLS_PER_ROW perspectives
            if i % MAX_COLS_PER_ROW == 0:
                row_cols = st.columns(MAX_COLS_PER_ROW)

            # The current column index within the current row
            col_index = i % MAX_COLS_PER_ROW
            with row_cols[col_index]:
                # Get the persistent config for this slot
                p_config = st.session_state.symposium_configs[i]

                with st.container(border=True):
                    st.markdown(f"#### Perspective {i+1}")

                    # v10.0.22: Add perspective type selector
                    perspective_type = st.radio(
                        "Perspective Type:",
                        ("Library Lens", "Zeitgeist"),
                        key=f"symposium_type_{i}",
                        horizontal=True
                    )
                    p_config['is_zeitgeist'] = (perspective_type == "Zeitgeist")

                    if perspective_type == "Library Lens":
                        # v10.2: Get scope mode and clear lens/persona in Broad mode
                        scope = st.session_state.get("symposium_scope", "Narrow")

                        if scope == "Broad":
                            # Clear lens and persona selections in session state when in Broad mode
                            if st.session_state.get(f"symposium_lens_{i}"):
                                st.session_state[f"symposium_lens_{i}"] = None
                            if st.session_state.get(f"symposium_persona_{i}") and st.session_state.get(f"symposium_persona_{i}") not in ["(AI Decides)", "(No Persona)"]:
                                st.session_state[f"symposium_persona_{i}"] = "(AI Decides)"

                        # v10.2: Add Clear/Reset button
                        col_clear1, col_clear2 = st.columns([4, 1])
                        with col_clear1:
                            st.caption("**Filter Selection:**")
                        with col_clear2:
                            # v10.2: Clear button - rely on Streamlit's automatic rerun instead of explicit st.rerun()
                            if st.button("✕", key=f"symposium_clear_{i}", help="Clear all filters, lens, and persona"):
                                st.session_state[f'symposium_discipline_filter_{i}'] = "All Disciplines"
                                st.session_state[f'symposium_function_filter_{i}'] = "All Functions"
                                st.session_state[f'symposium_era_filter_{i}'] = "All Eras"
                                st.session_state[f'symposium_geographic_filter_{i}'] = "All Regions"
                                st.session_state[f'symposium_lens_{i}'] = None
                                if f'symposium_persona_{i}' in st.session_state:
                                    st.session_state[f'symposium_persona_{i}'] = "(AI Decides)"

                        # Get current filter values, lens, and persona
                        current_lens = st.session_state.get(f"symposium_lens_{i}")
                        current_discipline = st.session_state.get(f"symposium_discipline_filter_{i}", "All Disciplines")
                        current_function = st.session_state.get(f"symposium_function_filter_{i}", "All Functions")
                        current_era = st.session_state.get(f"symposium_era_filter_{i}", "All Eras")
                        current_persona = st.session_state.get(f"symposium_persona_{i}", "(AI Decides)")

                        # v10.2: Bidirectional cascading logic (matching Single Lens/Comparative)
                        # Rule: Each dropdown filters based on ALL OTHER selections (not including itself)
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
                            if current_lens:
                                lens_match = current_lens in persona_meta['lenses']

                            # If matches all filters + lens, add to available personas
                            if disc_match and func_match and era_match and lens_match:
                                available_personas.append(persona_name)

                        # Convert to sorted lists
                        available_disciplines = ["All Disciplines"] + sorted([d for d in available_disciplines if d != "All Disciplines"])
                        available_functions = ["All Functions"] + sorted([f for f in available_functions if f != "All Functions"])
                        available_eras_list = ["All Eras"] + [e for e in ERA_ORDER if e in available_eras]

                        # Filters with cascading options and inline counts
                        # Reset to "All" if current selection is no longer available
                        if current_discipline not in available_disciplines:
                            current_discipline = "All Disciplines"
                        if current_function not in available_functions:
                            current_function = "All Functions"
                        if current_era not in available_eras_list:
                            current_era = "All Eras"

                        # Show count inline with label
                        total_disciplines = len(LENSES_HIERARCHY)
                        filtered_count_d = len([d for d in available_disciplines if d != "All Disciplines"])
                        if filtered_count_d < total_disciplines:
                            disc_label = f"**Discipline** ({filtered_count_d}):"
                        else:
                            disc_label = "**Discipline:**"

                        total_functions = len(LENSES_FUNCTIONAL)
                        filtered_count_f = len([f for f in available_functions if f != "All Functions"])
                        if filtered_count_f < total_functions:
                            func_label = f"**Function Tier** ({filtered_count_f}):"
                        else:
                            func_label = "**Function Tier:**"

                        total_eras = len(ERA_ORDER)
                        filtered_count_e = len([e for e in available_eras_list if e != "All Eras"])
                        if filtered_count_e < total_eras:
                            era_label = f"**Historical Era** ({filtered_count_e}):"
                        else:
                            era_label = "**Historical Era:**"

                        discipline_filter = st.selectbox(
                            disc_label,
                            available_disciplines,
                            index=available_disciplines.index(current_discipline),
                            key=f"symposium_discipline_filter_{i}"
                        )
                        function_filter = st.selectbox(
                            func_label,
                            available_functions,
                            index=available_functions.index(current_function),
                            key=f"symposium_function_filter_{i}"
                        )
                        era_filter = st.selectbox(
                            era_label,
                            available_eras_list,
                            index=available_eras_list.index(current_era),
                            key=f"symposium_era_filter_{i}"
                        )

                        # v10.5: Geographic filter
                        from lenses import LENSES_GEOGRAPHIC
                        geographic_regions = ["All Regions"] + sorted(list(LENSES_GEOGRAPHIC.keys()))
                        current_geographic = st.session_state.get(f"symposium_geographic_filter_{i}", "All Regions")
                        geographic_filter = st.selectbox(
                            "**Geographic Region:**",
                            geographic_regions,
                            index=geographic_regions.index(current_geographic) if current_geographic in geographic_regions else 0,
                            key=f"symposium_geographic_filter_{i}"
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

                            # Only show help tooltip on first perspective
                            lens_help = utils.get_lens_tooltip(current_lens) if i == 0 else None
                            st.selectbox(
                                lens_label,
                                options=available_lenses,
                                index=lens_index,
                                placeholder="Select lens...",
                                key=f"symposium_lens_{i}",
                                help=lens_help
                            )
                            p_config['lens'] = st.session_state.get(f"symposium_lens_{i}")

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

                            # Only show help tooltip on first perspective
                            persona_help = "Choose a specific historical figure, let AI decide from filtered pool, or use generic archetypal title" if i == 0 else None
                            selected_persona = st.selectbox(
                                persona_label,
                                options=persona_options,
                                index=persona_index,
                                key=f"symposium_persona_{i}",
                                help=persona_help
                            )

                            # Update p_config - map special values
                            if selected_persona == "(AI Decides)":
                                p_config['persona'] = None
                            elif selected_persona == "(No Persona)":
                                p_config['persona'] = "(No Persona)"
                            else:
                                p_config['persona'] = selected_persona
                        else:
                            # Broad mode - clear lens and persona from config
                            p_config['lens'] = None
                            p_config['persona'] = None
                            # Store filter context for AI in Broad mode
                            p_config['discipline_context'] = discipline_filter if discipline_filter != "All Disciplines" else None
                            p_config['function_context'] = function_filter if function_filter != "All Functions" else None
                            p_config['era_context'] = era_filter if era_filter != "All Eras" else None
                            p_config['geographic_context'] = geographic_filter if geographic_filter != "All Regions" else None
                            p_config['scope_mode'] = 'broad'

                    elif perspective_type == "Zeitgeist":
                        p_config['zeitgeist_context'] = st.text_area("Context:", height=100, key=f"symposium_z_context_{i}", placeholder="e.g., Vienna, 1905...")
                        p_config['zeitgeist_persona'] = st.text_area("Witness:", height=100, key=f"symposium_z_witness_{i}", placeholder="e.g., A conservative art critic...")
                        # v10.0.33: Clear lens/persona if switching to Zeitgeist
                        p_config['lens'] = None
                        p_config['persona'] = None

        st.session_state.symposium_selection_data = st.session_state.symposium_configs

    elif selection_method == SELECT_SMART:
        st.info("🤖 **Smart Selection Activated.** The Janus 'Analyst-in-Chief' will choose the most potent lenses after analyzing your input.")
        # v10.0.21: Add user choice for number of smart-selected perspectives
        st.number_input(
            "Number of Perspectives for Smart Selection:",
            min_value=3,
            max_value=6,
            value=st.session_state.symposium_smart_select_count,
            step=1,
            key="symposium_smart_select_count",
            help="Select how many perspectives you want Janus to choose for the symposium."
        )
        st.session_state.symposium_selection_data = []

# --- STEP 3: EXECUTION (Shows when configuration is valid) ---
is_configured = False
total_perspectives = len(st.session_state.get('symposium_selection_data', []))
header_text = "Analysis"

if (selection_method == SELECT_MANUAL):
    # v10.2: Flexible validation - accept lens, persona, OR filters for each perspective
    # Count only configured perspectives (ignore empty/default slots)
    scope = st.session_state.get("symposium_scope", "Narrow")

    def is_perspective_configured(p, idx):
        """Check if a perspective has meaningful configuration (not all defaults)."""
        # Zeitgeist perspective must have both fields
        if p['is_zeitgeist']:
            return p.get('zeitgeist_context') and p.get('zeitgeist_persona')

        # Library Lens perspective in Narrow mode: accept lens, persona, OR filters
        if scope == "Narrow":
            has_lens = p.get('lens') is not None
            has_persona = p.get('persona') not in [None, "(No Persona)"]
            has_filters = (
                st.session_state.get(f"symposium_discipline_filter_{idx}", "All Disciplines") != "All Disciplines" or
                st.session_state.get(f"symposium_function_filter_{idx}", "All Functions") != "All Functions" or
                st.session_state.get(f"symposium_era_filter_{idx}", "All Eras") != "All Eras" or
                st.session_state.get(f"symposium_geographic_filter_{idx}", "All Regions") != "All Regions"
            )
            return has_lens or has_persona or has_filters
        else:  # Broad mode
            # Must have at least one filter selected
            has_filters = (
                st.session_state.get(f"symposium_discipline_filter_{idx}", "All Disciplines") != "All Disciplines" or
                st.session_state.get(f"symposium_function_filter_{idx}", "All Functions") != "All Functions" or
                st.session_state.get(f"symposium_era_filter_{idx}", "All Eras") != "All Eras" or
                st.session_state.get(f"symposium_geographic_filter_{idx}", "All Regions") != "All Regions"
            )
            return has_filters

    # Count how many perspectives are actually configured (not empty/default)
    configured_count = sum(
        1 for i, p in enumerate(st.session_state.symposium_selection_data)
        if is_perspective_configured(p, i)
    )

    # Require at least 3 configured perspectives
    if configured_count >= 3:
        is_configured = True
        header_text = f"Analysis | {configured_count} Perspectives"
        if scope == "Broad":
            header_text += " (Broad)"
elif (selection_method == SELECT_SMART):
    is_configured = True
    header_text = "Analysis | Smart Selection"

# Show status message if configuration incomplete
st.markdown("---")
if not is_configured:
    if selection_method == SELECT_MANUAL:
        st.info(f"Complete your configuration above to proceed with execution. ({configured_count}/3 configured)")
    else:
        st.info("Complete your configuration above to proceed with execution.")
    st.stop()  # Stop rendering if config not complete

# Construct header text
st.header(header_text)

# Execution Button
# Change button label if already executed
button_label = "Execute Analysis Engine"
if st.session_state.symposium_state == 'executed':
    button_label = "Re-Execute Analysis (Start Over)"

if st.button(button_label, type="primary", width="stretch"):
    # If re-executing, reset state first (this also cleans up old files)
    if st.session_state.symposium_state == 'executed':
        reset_analysis_state()

    # --- Centralized Execution Block ---
    st.markdown("---")

    # v10.2: Filter to only configured perspectives (ignore empty/default slots)
    if selection_method == SELECT_MANUAL:
        # Reuse the validation function from above
        scope = st.session_state.get("symposium_scope", "Narrow")

        def is_perspective_configured(p, idx):
            """Check if a perspective has meaningful configuration (not all defaults)."""
            if p['is_zeitgeist']:
                return p.get('zeitgeist_context') and p.get('zeitgeist_persona')

            if scope == "Narrow":
                has_lens = p.get('lens') is not None
                has_persona = p.get('persona') not in [None, "(No Persona)"]
                has_filters = (
                    st.session_state.get(f"symposium_discipline_filter_{idx}", "All Disciplines") != "All Disciplines" or
                    st.session_state.get(f"symposium_function_filter_{idx}", "All Functions") != "All Functions" or
                    st.session_state.get(f"symposium_era_filter_{idx}", "All Eras") != "All Eras" or
                    st.session_state.get(f"symposium_geographic_filter_{idx}", "All Regions") != "All Regions"
                )
                return has_lens or has_persona or has_filters
            else:  # Broad mode
                has_filters = (
                    st.session_state.get(f"symposium_discipline_filter_{idx}", "All Disciplines") != "All Disciplines" or
                    st.session_state.get(f"symposium_function_filter_{idx}", "All Functions") != "All Functions" or
                    st.session_state.get(f"symposium_era_filter_{idx}", "All Eras") != "All Eras" or
                    st.session_state.get(f"symposium_geographic_filter_{idx}", "All Regions") != "All Regions"
                )
                return has_filters

        # Filter out empty perspectives before sending to API
        final_configs = [
            p for i, p in enumerate(st.session_state.symposium_selection_data)
            if is_perspective_configured(p, i)
        ]
    else:
        final_configs = st.session_state.symposium_selection_data

    # v10.2: Run Smart Selection (if applicable)
    if selection_method == SELECT_SMART:
        with st.status("🤖 Smart Selection", expanded=True) as smart_status:
            smart_status.write("Consulting Analyst-in-Chief...")
            client = utils.get_client(st.session_state.get("api_key"))
            if client:
                smart_lenses = utils.analyst_in_chief(client, work_a, required_count=st.session_state.symposium_smart_select_count, status_container=smart_status)
                if smart_lenses:
                    final_configs = [{'lens': lens, 'persona': None, 'is_zeitgeist': False} for lens in smart_lenses]
                    smart_status.update(label="✅ Smart Selection Complete", state="complete")
                else:
                    st.error("Smart Selection failed to return valid lenses.")
                    st.stop()
            else:
                st.error("Failed to initialize API client.")
                st.stop()

        st.markdown("---")

    # v10.2: Create container for displaying strategies during execution
    st.subheader("🧠 Analysis Strategies")
    st.caption("Generated strategies appear here as each analysis begins:")
    strategy_display = st.container()

    try:
        synthesis_result, raw_analyses, strategies = utils.run_analysis_pipeline(
            work_input=work_a,
            manual_configs=final_configs,
            smart_select_count=st.session_state.symposium_smart_select_count,
            page_key_prefix='symposium',
            stream_container=None,  # Will display synthesis after we have persona info
            strategy_container=strategy_display
        )

        if synthesis_result:
            st.session_state.symposium_result = synthesis_result
            st.session_state.symposium_state = 'executed'
            st.session_state.symposium_raw_analyses = raw_analyses
            st.session_state.symposium_strategies = strategies
        else:
            st.error("The analysis pipeline did not complete successfully.")

    finally:
        if st.session_state.symposium_state != 'executed':
            work_a.cleanup_gemini_file()

# --- DISPLAY RESULTS FROM SESSION STATE ---
if st.session_state.symposium_state == 'executed' and st.session_state.symposium_result:
    # v10.2: Extract persona names from strategy data (persona instructions)
    st.markdown("---")
    st.subheader("💬 Symposium Dialogue")
    st.caption("**Personas Adopted:**")
    if st.session_state.symposium_raw_analyses and st.session_state.symposium_strategies:
        persona_list = []
        for i, (config, text) in enumerate(st.session_state.symposium_raw_analyses):
            persona_name = "Unknown"

            # Extract from persona instruction like "Adopt the persona of..."
            if i < len(st.session_state.symposium_strategies) and st.session_state.symposium_strategies[i].get('persona_instruction'):
                match = re.search(r"(?:Adopt the persona of|You are)\s+(.+?)(?:\.|,|\n|$)", st.session_state.symposium_strategies[i]['persona_instruction'], re.IGNORECASE)
                if match:
                    persona_name = match.group(1).strip()

            lens_name = config.get('lens') or "Zeitgeist Perspective"
            persona_list.append(f"**{persona_name}** ({lens_name})")
        st.caption(" • ".join(persona_list))

    # Display the synthesis
    st.markdown(st.session_state.symposium_result)

    # v10.2: Export buttons
    st.markdown("---")
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    col1, col2 = st.columns(2)
    with col1:
        # Get config from session state
        symposium_configs = st.session_state.get('symposium_selection_data', [{}])
        markdown_export = utils.create_export_content(
            result_text=st.session_state.symposium_result,
            work_input=work_a,
            analysis_type="Symposium",
            config_info=symposium_configs[0] if symposium_configs else {},
            format_type="markdown"
        )
        st.download_button(
            label="📥 Download as Markdown",
            data=markdown_export,
            file_name=f"janus_symposium_{timestamp}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_symposium_md"
        )
    with col2:
        text_export = utils.create_export_content(
            result_text=st.session_state.symposium_result,
            work_input=work_a,
            analysis_type="Symposium",
            config_info=symposium_configs[0] if symposium_configs else {},
            format_type="text"
        )
        st.download_button(
            label="📥 Download as Text",
            data=text_export,
            file_name=f"janus_symposium_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_symposium_txt"
        )

    # Display metadata after completion
    st.markdown("---")
    utils.display_metadata(work_a, label=work_a.get_display_title())

# --- REFINEMENT LOOP ---
if st.session_state.symposium_state == 'executed' and st.session_state.symposium_result:
    # Refinement Loop UI
    st.markdown("---")
    st.subheader("🔄 Refinement Loop")
    with st.container(border=True):
        st.write("Provide instructions to iteratively refine the analysis above.")
        refinement_instruction = st.text_area("Refinement Instruction:", height=100, key="refinement_instruction", placeholder="e.g., 'Make the synthesis more concise', or 'Have the speakers challenge each other more directly.'")

        if st.button("Refine Analysis", type="secondary"):
            if not refinement_instruction:
                st.warning("Please enter a refinement instruction.")
            else:
                st.session_state.run_refinement_on_next_load = True
                st.session_state.instruction_to_run = refinement_instruction
                st.rerun()