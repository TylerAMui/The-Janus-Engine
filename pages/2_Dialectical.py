import streamlit as st
import utils
import re
# v9.4b: LENS_ZEITGEIST constant is removed from utils.
from utils import WorkInput, SELECT_MANUAL, SELECT_SMART, SELECTION_MODES

# --- CONSTANTS ---
# v9.4b: Define specific modes for this page including Zeitgeist
MODE_STANDARD = "Standard (Lens vs. Lens)"
MODE_ZEITGEIST = "Zeitgeist Simulation (Era vs. Era)"

# --- CALLBACKS ---
# v10.0.15: Centralize reset logic
def reset_analysis_state():
    utils.reset_page_state('dialectical')

def handle_dialectical_mode_change():
    """Callback to clear selections when the mode changes (Standard vs Zeitgeist, or Manual vs Smart)."""
    # v10.1: Updated to clear new filter widgets
    st.session_state.dialectical_selection_data = []
    # Also clear specific UI widget states if necessary to ensure a clean slate when switching modes
    if 'dialectic_lens_a' in st.session_state: del st.session_state.dialectic_lens_a
    if 'dialectic_lens_b' in st.session_state: del st.session_state.dialectic_lens_b
    # Clear filter widgets
    if 'dialectic_discipline_filter_a' in st.session_state:
        st.session_state.dialectic_discipline_filter_a = "All Disciplines"
    if 'dialectic_function_filter_a' in st.session_state:
        st.session_state.dialectic_function_filter_a = "All Functions"
    if 'dialectic_era_filter_a' in st.session_state:
        st.session_state.dialectic_era_filter_a = "All Eras"
    if 'dialectic_geographic_filter_a' in st.session_state:
        st.session_state.dialectic_geographic_filter_a = "All Regions"
    if 'dialectic_discipline_filter_b' in st.session_state:
        st.session_state.dialectic_discipline_filter_b = "All Disciplines"
    if 'dialectic_function_filter_b' in st.session_state:
        st.session_state.dialectic_function_filter_b = "All Functions"
    if 'dialectic_era_filter_b' in st.session_state:
        st.session_state.dialectic_era_filter_b = "All Eras"
    if 'dialectic_geographic_filter_b' in st.session_state:
        st.session_state.dialectic_geographic_filter_b = "All Regions"

# --- PAGE SETUP ---
# v10.2: Update page title
PAGE_TITLE = "Janus | Dialectical"
utils.initialize_page_config(PAGE_TITLE)
st.title("2 | Dialectical (2 Perspectives)")
st.write("Analyze ONE work through TWO perspectives (Thesis vs. Antithesis), synthesized into a dialogue.")

# --- SIDEBAR (Global Settings Only) ---
utils.render_sidebar_settings()

# --- PAGE MEMORY MANAGEMENT ---
# Clean up uploaded files from other pages to prevent memory accumulation
if 'current_page' not in st.session_state:
    st.session_state.current_page = None

if st.session_state.current_page != "dialectical":
    st.session_state.current_page = "dialectical"
    utils.cleanup_other_pages_files("dialectical")

# Initialize Session State for this page
if 'dialectical_selection_data' not in st.session_state:
    # v10.0.32: This is now the single source of truth for config.
    st.session_state.dialectical_selection_data = []
if 'dialectical_configs' not in st.session_state: # Holds the UI state for the two configs
    st.session_state.dialectical_configs = [
        {'lens': None, 'persona': None, 'is_zeitgeist': False, 'zeitgeist_context': "", 'zeitgeist_persona': ""},
        {'lens': None, 'persona': None, 'is_zeitgeist': False, 'zeitgeist_context': "", 'zeitgeist_persona': ""}
    ]
if 'dialectical_selection_method' not in st.session_state:
    # Stores the method within Standard mode (Manual or Smart)
    st.session_state.dialectical_selection_method = SELECT_MANUAL
if 'dialectical_analysis_mode' not in st.session_state:
    # Stores the overall mode (Standard or Zeitgeist)
    st.session_state.dialectical_analysis_mode = MODE_STANDARD
if 'work_input_dialectical' not in st.session_state:
    st.session_state.work_input_dialectical = WorkInput()

# Add state for Refinement Loop
if 'dialectical_state' not in st.session_state:
    st.session_state.dialectical_state = 'config'
if 'dialectical_result' not in st.session_state:
    st.session_state.dialectical_result = None
if 'dialectical_raw_analyses' not in st.session_state:
    st.session_state.dialectical_raw_analyses = None
if 'dialectical_strategies' not in st.session_state:
    st.session_state.dialectical_strategies = None

# v10.1: Handle Library Cart Pre-selection (MUST happen before any widgets are created)
if 'library_dialectical_cart' in st.session_state and st.session_state.library_dialectical_cart:
    cart = st.session_state.library_dialectical_cart
    if len(cart) >= 2:
        # Turn off Zeitgeist mode
        st.session_state.dialectical_analysis_mode = MODE_STANDARD
        # Reset filters to ensure pre-selected lenses are visible
        st.session_state.dialectic_discipline_filter_a = "All Disciplines"
        st.session_state.dialectic_function_filter_a = "All Functions"
        st.session_state.dialectic_era_filter_a = "All Eras"
        st.session_state.dialectic_geographic_filter_a = "All Regions"
        st.session_state.dialectic_discipline_filter_b = "All Disciplines"
        st.session_state.dialectic_function_filter_b = "All Functions"
        st.session_state.dialectic_era_filter_b = "All Eras"
        st.session_state.dialectic_geographic_filter_b = "All Regions"
        # Set the lens selections for A and B
        st.session_state.dialectic_lens_a = cart[0]
        st.session_state.dialectic_lens_b = cart[1]
        # Clear the cart (one-time use)
        st.session_state.library_dialectical_cart = []
        st.rerun()

# --- REFINEMENT EXECUTION LOGIC ---
if st.session_state.get("run_refinement_on_next_load"):
    st.session_state.run_refinement_on_next_load = False
    instruction = st.session_state.get("instruction_to_run", "")
    if instruction:
        # Pass the work input which holds the cached file reference
        refined_result = utils.generate_refined_analysis(
            st.session_state.work_input_dialectical,
            st.session_state.dialectical_result,
            instruction
        )
        if refined_result:
            st.session_state.dialectical_result = refined_result
            st.session_state.refinement_instruction = ""
            st.rerun()

# --- MAIN PAGE LAYOUT ---
# v9.4b: Renamed variables for clarity
selection_method = st.session_state.dialectical_selection_method
analysis_mode = st.session_state.dialectical_analysis_mode

work_a = st.session_state.work_input_dialectical
api_key = st.session_state.get("api_key", "")

# --- STEP 1: INPUT WORK (Always visible first) ---

# v10.2: API Key Warning Banner
if not st.session_state.get("api_key"):
    st.warning("⚠️ API Key Required — Please configure on Home page to use the engine")

st.header("📄 Input Work")
st.caption("Upload your creative work or enter text to begin")
utils.handle_input_ui(work_a, st.container(border=True), "work_dialectical", on_change_callback=reset_analysis_state)

# Check if work is ready
work_is_ready = work_a.is_ready()

if not work_is_ready:
    st.info("👆 Please upload a file or enter text above to proceed with configuration.")
    st.stop()  # Stop rendering here until work is provided

# --- STEP 2: CONFIGURATION & PERSPECTIVE SELECTION (Only appears after work is ready) ---
st.markdown("---")
with st.expander("🔬 Configuration & Perspective Selection", expanded=True):
    # v10.2: Use persistent config objects from session state as the single source of truth
    config_a = st.session_state.dialectical_configs[0]
    config_b = st.session_state.dialectical_configs[1]

    # === ZEITGEIST MODE UI ===
    if analysis_mode == MODE_ZEITGEIST:
        # v10.2: Zeitgeist toggle (allows deactivation)
        zeitgeist_header_col, zeitgeist_toggle_col = st.columns([3, 1])
        with zeitgeist_header_col:
            st.info("🕰️ **Zeitgeist Simulation Activated.** Define the two historical contexts and witness personas.")
        with zeitgeist_toggle_col:
            deactivate_zeitgeist = st.toggle(
                "Activate Zeitgeist",
                value=True,
                on_change=handle_dialectical_mode_change,
                help="Switch back to Standard mode"
            )

        # Handle deactivation
        if not deactivate_zeitgeist:
            st.session_state.dialectical_analysis_mode = MODE_STANDARD
            st.rerun()

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

        # 2. Check for completeness (don't show warning here, just invalidate)
        if (not config_a['zeitgeist_context'] or not config_a['zeitgeist_persona'] or
            not config_b['zeitgeist_context'] or not config_b['zeitgeist_persona']):
            pass # Let the readiness check handle the user message

    # === STANDARD MODE UI ===
    elif analysis_mode == MODE_STANDARD:
        # v10.2: Ensure is_zeitgeist is False in standard mode
        config_a['is_zeitgeist'] = False
        config_b['is_zeitgeist'] = False

        # v10.2: Selection Method and Zeitgeist toggle on same line (mirroring Single Lens)
        method_col, zeitgeist_col = st.columns([3, 1])
        with method_col:
            st.radio(
                "**Selection Method:**",
                SELECTION_MODES,
                horizontal=True,
                key="dialectical_selection_method"
            )
        with zeitgeist_col:
            activate_zeitgeist = st.toggle(
                "Activate Zeitgeist",
                value=False,
                on_change=handle_dialectical_mode_change,
                help="Switch to Zeitgeist Simulation mode (Era vs. Era)"
            )

        # Handle Zeitgeist activation
        if activate_zeitgeist:
            st.session_state.dialectical_analysis_mode = MODE_ZEITGEIST
            st.rerun()

        # Update selection_method based on the radio button state (it might have changed via callback)
        selection_method = st.session_state.dialectical_selection_method

        # v10.2: Scope Toggle (only for Manual mode)
        if selection_method == SELECT_MANUAL:
            st.markdown("---")
            st.radio(
                "**Scope:**",
                ["Narrow", "Broad"],
                horizontal=True,
                index=0,
                help="Narrow: AI smart-selects specific lenses within filtered categories. Broad: AI analyzes from broad category perspective.",
                key="dialectical_scope"
            )

        if selection_method == SELECT_MANUAL:
            st.markdown("---")

            # v10.2: Get scope mode and clear lens/persona in Broad mode
            scope = st.session_state.get("dialectical_scope", "Narrow")

            if scope == "Narrow":
                st.caption("Select two independent lenses (Thesis and Antithesis).")
            else:
                st.caption("Filter-based analysis (AI will analyze from category perspectives).")
                # Clear lens and persona selections in Broad mode
                if st.session_state.get("dialectic_lens_a"):
                    st.session_state.dialectic_lens_a = None
                if st.session_state.get("dialectic_lens_b"):
                    st.session_state.dialectic_lens_b = None
                if st.session_state.get("dialectic_persona_a") and st.session_state.get("dialectic_persona_a") not in ["(AI Decides)", "(No Persona)"]:
                    st.session_state.dialectic_persona_a = "(AI Decides)"
                if st.session_state.get("dialectic_persona_b") and st.session_state.get("dialectic_persona_b") not in ["(AI Decides)", "(No Persona)"]:
                    st.session_state.dialectic_persona_b = "(AI Decides)"

            # v10.2: Cascading Filter System with Persona Integration
            from lenses import SORTED_LENS_NAMES, PERSONA_METADATA, SORTED_PERSONA_NAMES, LENSES_HIERARCHY, LENSES_FUNCTIONAL, LENSES_BY_ERA
            from utils import get_lens_data

            # v10.0.30: Two-column layout for clarity
            col_a, col_b = st.columns(2)

            with col_a:
                with st.container(border=True):
                    st.markdown("🏛️ **Perspective A (Thesis)**")

                    # Reset button for A
                    col_clear1, col_clear2 = st.columns([4, 1])
                    with col_clear1:
                        st.markdown("**Filters (Optional):**")
                    with col_clear2:
                        # v10.2: Clear button - rely on Streamlit's automatic rerun instead of explicit st.rerun()
                        if st.button("✕", key="clear_dialectic_a", help="Clear all filters, lens, and persona for A"):
                            st.session_state.dialectic_discipline_filter_a = "All Disciplines"
                            st.session_state.dialectic_function_filter_a = "All Functions"
                            st.session_state.dialectic_era_filter_a = "All Eras"
                            st.session_state.dialectic_geographic_filter_a = "All Regions"
                            st.session_state.dialectic_lens_a = None
                            st.session_state.dialectic_persona_a = "(AI Decides)"

                    # Get current selections for A
                    current_discipline_a = st.session_state.get("dialectic_discipline_filter_a", "All Disciplines")
                    current_function_a = st.session_state.get("dialectic_function_filter_a", "All Functions")
                    current_era_a = st.session_state.get("dialectic_era_filter_a", "All Eras")
                    current_lens_a = st.session_state.get("dialectic_lens_a")
                    current_persona_a = st.session_state.get("dialectic_persona_a", "(AI Decides)")

                    # v10.2: Calculate available options for ALL FIVE dropdowns (discipline/function/era/lens/persona)
                    # Rule: A dropdown should not restrict itself - each shows options based on OTHER selections
                    available_disciplines_a = set(["All Disciplines"])
                    available_functions_a = set(["All Functions"])
                    available_eras_a = set(["All Eras"])
                    available_lenses_a = []
                    available_personas_a = []

                    # For each lens, check if it matches the OTHER filters (not including current_lens)
                    for lens_name in SORTED_LENS_NAMES:
                        disc_match = (current_discipline_a == "All Disciplines" or lens_name in LENSES_HIERARCHY.get(current_discipline_a, []))
                        func_match = (current_function_a == "All Functions" or lens_name in LENSES_FUNCTIONAL.get(current_function_a, []))
                        era_match = (current_era_a == "All Eras" or lens_name in LENSES_BY_ERA.get(current_era_a, []))

                        # Check if lens matches selected persona (if any)
                        persona_match = True
                        if current_persona_a and current_persona_a not in ["(AI Decides)", "(No Persona)"]:
                            persona_match = lens_name in PERSONA_METADATA[current_persona_a]['lenses']

                        # If matches discipline + function + era + persona, add to available lenses
                        if disc_match and func_match and era_match and persona_match:
                            available_lenses_a.append(lens_name)

                        # For filter dropdowns: if lens matches OTHER TWO filters + persona, add its categories
                        if func_match and era_match and persona_match:
                            for cat, lenses in LENSES_HIERARCHY.items():
                                if lens_name in lenses:
                                    available_disciplines_a.add(cat)

                        if disc_match and era_match and persona_match:
                            for tier, lenses in LENSES_FUNCTIONAL.items():
                                if lens_name in lenses:
                                    available_functions_a.add(tier)

                        if disc_match and func_match and persona_match:
                            lens_data = get_lens_data(lens_name)
                            if lens_data:
                                for era in lens_data.get('eras', []):
                                    available_eras_a.add(era)

                    # For each persona, check if it matches the OTHER filters (not including current_persona)
                    for persona_name in SORTED_PERSONA_NAMES:
                        persona_meta = PERSONA_METADATA[persona_name]

                        disc_match = (current_discipline_a == "All Disciplines" or current_discipline_a in persona_meta['disciplines'])
                        func_match = (current_function_a == "All Functions" or current_function_a in persona_meta['functions'])
                        era_match = (current_era_a == "All Eras" or current_era_a in persona_meta['eras'])

                        # Check if persona matches selected lens (if any)
                        lens_match = True
                        if current_lens_a:
                            lens_match = current_lens_a in persona_meta['lenses']

                        # If matches all filters + lens, add to available personas
                        if disc_match and func_match and era_match and lens_match:
                            available_personas_a.append(persona_name)

                    # Convert sets to sorted lists for dropdowns
                    available_disciplines_a = sorted(list(available_disciplines_a))
                    available_functions_a = sorted(list(available_functions_a))
                    available_eras_a = sorted(list(available_eras_a))

                    # Filters for Perspective A
                    discipline_filter_a = st.selectbox(
                        "**Discipline:**",
                        available_disciplines_a,
                        index=available_disciplines_a.index(current_discipline_a) if current_discipline_a in available_disciplines_a else 0,
                        help="Filter by academic discipline",
                        key="dialectic_discipline_filter_a"
                    )
                    function_filter_a = st.selectbox(
                        "**Function Tier:**",
                        available_functions_a,
                        index=available_functions_a.index(current_function_a) if current_function_a in available_functions_a else 0,
                        help="Filter by functional tier",
                        key="dialectic_function_filter_a"
                    )
                    era_filter_a = st.selectbox(
                        "**Historical Era:**",
                        available_eras_a,
                        index=available_eras_a.index(current_era_a) if current_era_a in available_eras_a else 0,
                        help="Filter by historical period",
                        key="dialectic_era_filter_a"
                    )

                    # v10.5: Geographic filter
                    from lenses import LENSES_GEOGRAPHIC
                    geographic_regions = ["All Regions"] + sorted(list(LENSES_GEOGRAPHIC.keys()))
                    current_geographic_a = st.session_state.get("dialectic_geographic_filter_a", "All Regions")
                    geographic_filter_a = st.selectbox(
                        "**Geographic Region:**",
                        geographic_regions,
                        index=geographic_regions.index(current_geographic_a) if current_geographic_a in geographic_regions else 0,
                        help="Filter by cultural-geographic region",
                        key="dialectic_geographic_filter_a"
                    )

                    st.markdown("---")

                    # v10.2: Lens and Persona selection only visible in Narrow mode
                    if scope == "Narrow":
                        # v10.2: Lens selection for A (full width)
                        # Show inline count for lenses
                        total_lenses = len(SORTED_LENS_NAMES)
                        filtered_count_a = len(available_lenses_a)
                        if filtered_count_a < total_lenses:
                            lens_label_a = f"**Lens** ({filtered_count_a}):"
                        else:
                            lens_label_a = "**Lens:**"

                        try:
                            if current_lens_a and current_lens_a in available_lenses_a:
                                index_a = available_lenses_a.index(current_lens_a)
                            else:
                                index_a = None
                        except (ValueError, TypeError):
                            index_a = None

                        st.selectbox(
                            lens_label_a,
                            options=available_lenses_a,
                            index=index_a,
                            placeholder="Select lens...",
                            key="dialectic_lens_a",
                            help=utils.get_lens_tooltip(current_lens_a) if current_lens_a else "Choose from filtered lenses"
                        )
                        config_a['lens'] = st.session_state.get("dialectic_lens_a")

                        # v10.2: Persona selection for A (full width, below lens)
                        # Show inline count for personas
                        total_personas = len(SORTED_PERSONA_NAMES)
                        filtered_count_p_a = len(available_personas_a)
                        if filtered_count_p_a < total_personas:
                            persona_label_a = f"**Persona** ({filtered_count_p_a}):"
                        else:
                            persona_label_a = "**Persona:**"

                        try:
                            persona_options_a = ["(AI Decides)", "(No Persona)"] + available_personas_a
                            if current_persona_a in persona_options_a:
                                persona_index_a = persona_options_a.index(current_persona_a)
                            else:
                                persona_index_a = 0
                        except (ValueError, TypeError):
                            persona_index_a = 0

                        st.selectbox(
                            persona_label_a,
                            options=persona_options_a,
                            index=persona_index_a,
                            key="dialectic_persona_a",
                            help="Choose a specific historical figure, let AI decide from filtered pool, or use generic archetypal title"
                        )
                        config_a['persona'] = st.session_state.get("dialectic_persona_a")
                        if config_a['persona'] == "(AI Decides)":
                            config_a['persona'] = None
                        elif config_a['persona'] == "(No Persona)":
                            config_a['persona'] = "(No Persona)"
                    else:
                        # Broad mode - clear lens and persona from config
                        config_a['lens'] = None
                        config_a['persona'] = None

            with col_b:
                with st.container(border=True):
                    st.markdown("🏛️ **Perspective B (Antithesis)**")

                    # Reset button for B
                    col_clear1_b, col_clear2_b = st.columns([4, 1])
                    with col_clear1_b:
                        st.markdown("**Filters (Optional):**")
                    with col_clear2_b:
                        # v10.2: Clear button - rely on Streamlit's automatic rerun instead of explicit st.rerun()
                        if st.button("✕", key="clear_dialectic_b", help="Clear all filters, lens, and persona for B"):
                            st.session_state.dialectic_discipline_filter_b = "All Disciplines"
                            st.session_state.dialectic_function_filter_b = "All Functions"
                            st.session_state.dialectic_era_filter_b = "All Eras"
                            st.session_state.dialectic_geographic_filter_b = "All Regions"
                            st.session_state.dialectic_lens_b = None
                            st.session_state.dialectic_persona_b = "(AI Decides)"

                    # Get current selections for B
                    current_discipline_b = st.session_state.get("dialectic_discipline_filter_b", "All Disciplines")
                    current_function_b = st.session_state.get("dialectic_function_filter_b", "All Functions")
                    current_era_b = st.session_state.get("dialectic_era_filter_b", "All Eras")
                    current_lens_b = st.session_state.get("dialectic_lens_b")
                    current_persona_b = st.session_state.get("dialectic_persona_b", "(AI Decides)")

                    # v10.2: Calculate available options for ALL FIVE dropdowns (discipline/function/era/lens/persona)
                    # Rule: A dropdown should not restrict itself - each shows options based on OTHER selections
                    available_disciplines_b = set(["All Disciplines"])
                    available_functions_b = set(["All Functions"])
                    available_eras_b = set(["All Eras"])
                    available_lenses_b = []
                    available_personas_b = []

                    # For each lens, check if it matches the OTHER filters (not including current_lens)
                    for lens_name in SORTED_LENS_NAMES:
                        disc_match = (current_discipline_b == "All Disciplines" or lens_name in LENSES_HIERARCHY.get(current_discipline_b, []))
                        func_match = (current_function_b == "All Functions" or lens_name in LENSES_FUNCTIONAL.get(current_function_b, []))
                        era_match = (current_era_b == "All Eras" or lens_name in LENSES_BY_ERA.get(current_era_b, []))

                        # Check if lens matches selected persona (if any)
                        persona_match = True
                        if current_persona_b and current_persona_b not in ["(AI Decides)", "(No Persona)"]:
                            persona_match = lens_name in PERSONA_METADATA[current_persona_b]['lenses']

                        # If matches discipline + function + era + persona, add to available lenses
                        if disc_match and func_match and era_match and persona_match:
                            available_lenses_b.append(lens_name)

                        # For filter dropdowns: if lens matches OTHER TWO filters + persona, add its categories
                        if func_match and era_match and persona_match:
                            for cat, lenses in LENSES_HIERARCHY.items():
                                if lens_name in lenses:
                                    available_disciplines_b.add(cat)

                        if disc_match and era_match and persona_match:
                            for tier, lenses in LENSES_FUNCTIONAL.items():
                                if lens_name in lenses:
                                    available_functions_b.add(tier)

                        if disc_match and func_match and persona_match:
                            lens_data = get_lens_data(lens_name)
                            if lens_data:
                                for era in lens_data.get('eras', []):
                                    available_eras_b.add(era)

                    # For each persona, check if it matches the OTHER filters (not including current_persona)
                    for persona_name in SORTED_PERSONA_NAMES:
                        persona_meta = PERSONA_METADATA[persona_name]

                        disc_match = (current_discipline_b == "All Disciplines" or current_discipline_b in persona_meta['disciplines'])
                        func_match = (current_function_b == "All Functions" or current_function_b in persona_meta['functions'])
                        era_match = (current_era_b == "All Eras" or current_era_b in persona_meta['eras'])

                        # Check if persona matches selected lens (if any)
                        lens_match = True
                        if current_lens_b:
                            lens_match = current_lens_b in persona_meta['lenses']

                        # If matches all filters + lens, add to available personas
                        if disc_match and func_match and era_match and lens_match:
                            available_personas_b.append(persona_name)

                    # Convert sets to sorted lists for dropdowns
                    available_disciplines_b = sorted(list(available_disciplines_b))
                    available_functions_b = sorted(list(available_functions_b))
                    available_eras_b = sorted(list(available_eras_b))

                    # Filters for Perspective B
                    discipline_filter_b = st.selectbox(
                        "**Discipline:**",
                        available_disciplines_b,
                        index=available_disciplines_b.index(current_discipline_b) if current_discipline_b in available_disciplines_b else 0,
                        help="Filter by academic discipline",
                        key="dialectic_discipline_filter_b"
                    )
                    function_filter_b = st.selectbox(
                        "**Function Tier:**",
                        available_functions_b,
                        index=available_functions_b.index(current_function_b) if current_function_b in available_functions_b else 0,
                        help="Filter by functional tier",
                        key="dialectic_function_filter_b"
                    )
                    era_filter_b = st.selectbox(
                        "**Historical Era:**",
                        available_eras_b,
                        index=available_eras_b.index(current_era_b) if current_era_b in available_eras_b else 0,
                        help="Filter by historical period",
                        key="dialectic_era_filter_b"
                    )

                    # v10.5: Geographic filter
                    current_geographic_b = st.session_state.get("dialectic_geographic_filter_b", "All Regions")
                    geographic_filter_b = st.selectbox(
                        "**Geographic Region:**",
                        geographic_regions,
                        index=geographic_regions.index(current_geographic_b) if current_geographic_b in geographic_regions else 0,
                        help="Filter by cultural-geographic region",
                        key="dialectic_geographic_filter_b"
                    )

                    st.markdown("---")

                    # v10.2: Lens and Persona selection only visible in Narrow mode
                    if scope == "Narrow":
                        # v10.2: Lens selection for B (full width)
                        # Show inline count for lenses
                        total_lenses = len(SORTED_LENS_NAMES)
                        filtered_count_b = len(available_lenses_b)
                        if filtered_count_b < total_lenses:
                            lens_label_b = f"**Lens** ({filtered_count_b}):"
                        else:
                            lens_label_b = "**Lens:**"

                        try:
                            if current_lens_b and current_lens_b in available_lenses_b:
                                index_b = available_lenses_b.index(current_lens_b)
                            else:
                                index_b = None
                        except (ValueError, TypeError):
                            index_b = None

                        st.selectbox(
                            lens_label_b,
                            options=available_lenses_b,
                            index=index_b,
                            placeholder="Select lens...",
                            key="dialectic_lens_b"
                        )
                        config_b['lens'] = st.session_state.get("dialectic_lens_b")

                        # v10.2: Persona selection for B (full width, below lens)
                        # Show inline count for personas
                        total_personas = len(SORTED_PERSONA_NAMES)
                        filtered_count_p_b = len(available_personas_b)
                        if filtered_count_p_b < total_personas:
                            persona_label_b = f"**Persona** ({filtered_count_p_b}):"
                        else:
                            persona_label_b = "**Persona:**"

                        try:
                            persona_options_b = ["(AI Decides)", "(No Persona)"] + available_personas_b
                            if current_persona_b in persona_options_b:
                                persona_index_b = persona_options_b.index(current_persona_b)
                            else:
                                persona_index_b = 0
                        except (ValueError, TypeError):
                            persona_index_b = 0

                        st.selectbox(
                            persona_label_b,
                            options=persona_options_b,
                            index=persona_index_b,
                            key="dialectic_persona_b"
                        )
                        config_b['persona'] = st.session_state.get("dialectic_persona_b")
                        if config_b['persona'] == "(AI Decides)":
                            config_b['persona'] = None
                        elif config_b['persona'] == "(No Persona)":
                            config_b['persona'] = "(No Persona)"
                    else:
                        # Broad mode - clear lens and persona from config
                        config_b['lens'] = None
                        config_b['persona'] = None

            # Validation for Manual Selection
            if config_a.get('lens') and config_b.get('lens'):
                if (config_a['lens'] == config_b['lens']) and (config_a['persona'] == config_b['persona']):
                    st.warning("Cannot use the same Lens and Persona for both A and B. Please specify different personas or lenses.")

        elif selection_method == SELECT_SMART:
            st.info("🤖 **Smart Selection Activated.** The Janus 'Analyst-in-Chief' will choose the two most potent lenses after analyzing your input.")

    # v10.0.34: Always sync selection_data with configs (like Symposium does)
    # This ensures the config state is immediately available for validation
    # Validation logic determines if the config is complete enough to proceed
    if analysis_mode == MODE_ZEITGEIST:
        # Always sync for Zeitgeist mode
        st.session_state.dialectical_selection_data = [config_a, config_b]
    elif analysis_mode == MODE_STANDARD and selection_method == SELECT_MANUAL:
        # Always sync for Manual mode (validation happens later)
        st.session_state.dialectical_selection_data = [config_a, config_b]
    else:
        # Smart selection mode doesn't use selection_data until execution
        st.session_state.dialectical_selection_data = []


# --- STEP 3: EXECUTION (Shows when configuration is valid) ---

# v10.0.34: Updated validation logic to check actual config completeness
is_configured = False
header_text = "Analysis"

if analysis_mode == MODE_ZEITGEIST:
    # Check if both Zeitgeist configs are complete
    data = st.session_state.dialectical_selection_data
    if (len(data) == 2 and
        data[0].get('zeitgeist_context') and data[0].get('zeitgeist_persona') and
        data[1].get('zeitgeist_context') and data[1].get('zeitgeist_persona')):
        is_configured = True
        header_text = "Analysis | Zeitgeist Simulation (A vs. B)"

elif analysis_mode == MODE_STANDARD:
    if selection_method == SELECT_MANUAL:
        # v10.2: Flexible validation - each perspective needs at least one meaningful selection
        data = st.session_state.dialectical_selection_data
        if len(data) == 2:
            data_a = data[0]
            data_b = data[1]

            # v10.2: Get scope mode
            scope = st.session_state.get("dialectical_scope", "Narrow")

            # Check if Perspective A has meaningful selection
            has_lens_a = data_a.get('lens') is not None
            has_persona_a = data_a.get('persona') not in [None, "(No Persona)"]
            has_filters_a = (
                st.session_state.get("dialectic_discipline_filter_a", "All Disciplines") != "All Disciplines" or
                st.session_state.get("dialectic_function_filter_a", "All Functions") != "All Functions" or
                st.session_state.get("dialectic_era_filter_a", "All Eras") != "All Eras" or
                st.session_state.get("dialectic_geographic_filter_a", "All Regions") != "All Regions"
            )
            valid_a = has_lens_a or has_persona_a or has_filters_a

            # Check if Perspective B has meaningful selection
            has_lens_b = data_b.get('lens') is not None
            has_persona_b = data_b.get('persona') not in [None, "(No Persona)"]
            has_filters_b = (
                st.session_state.get("dialectic_discipline_filter_b", "All Disciplines") != "All Disciplines" or
                st.session_state.get("dialectic_function_filter_b", "All Functions") != "All Functions" or
                st.session_state.get("dialectic_era_filter_b", "All Eras") != "All Eras" or
                st.session_state.get("dialectic_geographic_filter_b", "All Regions") != "All Regions"
            )
            valid_b = has_lens_b or has_persona_b or has_filters_b

            # Both perspectives must have at least one valid selection
            if valid_a and valid_b:
                # v10.2: Store scope_mode and filter context for each perspective
                data_a['scope_mode'] = scope.lower()
                data_b['scope_mode'] = scope.lower()

                # Store filter context for both perspectives
                data_a['discipline_context'] = st.session_state.get("dialectic_discipline_filter_a") if st.session_state.get("dialectic_discipline_filter_a") != "All Disciplines" else None
                data_a['function_context'] = st.session_state.get("dialectic_function_filter_a") if st.session_state.get("dialectic_function_filter_a") != "All Functions" else None
                data_a['era_context'] = st.session_state.get("dialectic_era_filter_a") if st.session_state.get("dialectic_era_filter_a") != "All Eras" else None
                data_a['geographic_context'] = st.session_state.get("dialectic_geographic_filter_a") if st.session_state.get("dialectic_geographic_filter_a") != "All Regions" else None

                data_b['discipline_context'] = st.session_state.get("dialectic_discipline_filter_b") if st.session_state.get("dialectic_discipline_filter_b") != "All Disciplines" else None
                data_b['function_context'] = st.session_state.get("dialectic_function_filter_b") if st.session_state.get("dialectic_function_filter_b") != "All Functions" else None
                data_b['era_context'] = st.session_state.get("dialectic_era_filter_b") if st.session_state.get("dialectic_era_filter_b") != "All Eras" else None
                data_b['geographic_context'] = st.session_state.get("dialectic_geographic_filter_b") if st.session_state.get("dialectic_geographic_filter_b") != "All Regions" else None
                is_configured = True
                # Build display text
                if has_lens_a:
                    display_a = f"{data_a['lens']}" + (f" (as {data_a['persona']})" if data_a['persona'] else "")
                elif has_persona_a:
                    display_a = f"{data_a['persona']}'s Perspective"
                else:
                    # Filter-based
                    filter_parts_a = []
                    if st.session_state.get("dialectic_discipline_filter_a") != "All Disciplines":
                        filter_parts_a.append(st.session_state.get("dialectic_discipline_filter_a"))
                    if st.session_state.get("dialectic_function_filter_a") != "All Functions":
                        filter_parts_a.append(st.session_state.get("dialectic_function_filter_a"))
                    if st.session_state.get("dialectic_era_filter_a") != "All Eras":
                        filter_parts_a.append(st.session_state.get("dialectic_era_filter_a"))
                    if st.session_state.get("dialectic_geographic_filter_a") != "All Regions":
                        filter_parts_a.append(st.session_state.get("dialectic_geographic_filter_a"))
                    display_a = " + ".join(filter_parts_a)

                if has_lens_b:
                    display_b = f"{data_b['lens']}" + (f" (as {data_b['persona']})" if data_b['persona'] else "")
                elif has_persona_b:
                    display_b = f"{data_b['persona']}'s Perspective"
                else:
                    # Filter-based
                    filter_parts_b = []
                    if st.session_state.get("dialectic_discipline_filter_b") != "All Disciplines":
                        filter_parts_b.append(st.session_state.get("dialectic_discipline_filter_b"))
                    if st.session_state.get("dialectic_function_filter_b") != "All Functions":
                        filter_parts_b.append(st.session_state.get("dialectic_function_filter_b"))
                    if st.session_state.get("dialectic_era_filter_b") != "All Eras":
                        filter_parts_b.append(st.session_state.get("dialectic_era_filter_b"))
                    if st.session_state.get("dialectic_geographic_filter_b") != "All Regions":
                        filter_parts_b.append(st.session_state.get("dialectic_geographic_filter_b"))
                    display_b = " + ".join(filter_parts_b)

                header_text = f"Analysis | {display_a} vs. {display_b}"

    elif selection_method == SELECT_SMART:
        is_configured = True
        header_text = "Analysis | Smart Selection"

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
if st.session_state.dialectical_state == 'executed':
    button_label = "Re-Execute Analysis (Start Over)"

if st.button(button_label, type="primary", width="stretch"):
    # If re-executing, reset state first (this also cleans up old files)
    if st.session_state.dialectical_state == 'executed':
        reset_analysis_state()

    # --- Centralized Execution Block ---
    st.markdown("---")

    # v10.2: Run Smart Selection BEFORE other steps (if applicable)
    final_configs = st.session_state.dialectical_selection_data
    if selection_method == SELECT_SMART:
        with st.status("🤖 Smart Selection", expanded=True) as smart_status:
            smart_status.write("Consulting Analyst-in-Chief...")
            client = utils.get_client(st.session_state.get("api_key"))
            if client:
                smart_lenses = utils.analyst_in_chief(client, work_a, required_count=2, status_container=smart_status)
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
            smart_select_count=2,
            page_key_prefix='dialectic',
            stream_container=None,  # Will create synthesis container after we have persona info
            strategy_container=strategy_display
        )

        if synthesis_result:
            st.session_state.dialectical_result = synthesis_result
            st.session_state.dialectical_state = 'executed'
            # Store raw analyses and strategies
            if raw_analyses and len(raw_analyses) == 2:
                st.session_state.dialectical_raw_analyses = {
                    "a": {"name": raw_analyses[0][0].get('lens') or "Zeitgeist A", "text": raw_analyses[0][1]},
                    "b": {"name": raw_analyses[1][0].get('lens') or "Zeitgeist B", "text": raw_analyses[1][1]}
                }
            if strategies and len(strategies) == 2:
                st.session_state.dialectical_strategies = {"a": strategies[0], "b": strategies[1]}
    finally:
        # If successful, we need the cache for refinement. Only clean up on failure.
        if st.session_state.dialectical_state != 'executed':
            work_a.cleanup_gemini_file()

# --- DISPLAY RESULTS FROM SESSION STATE ---
if st.session_state.dialectical_state == 'executed' and st.session_state.dialectical_result:
    # v10.2: Extract persona names from strategy data (persona instructions)
    raw_analyses_dict = st.session_state.dialectical_raw_analyses
    strategies_dict = st.session_state.dialectical_strategies
    persona_a_name = "Unknown"
    persona_b_name = "Unknown"

    # Extract from persona instructions like "Adopt the persona of Antonin Artaud..."
    if strategies_dict:
        if strategies_dict.get('a') and strategies_dict['a'].get('persona_instruction'):
            match_a = re.search(r"(?:Adopt the persona of|You are)\s+(.+?)(?:\.|,|\n|$)", strategies_dict['a']['persona_instruction'], re.IGNORECASE)
            if match_a:
                persona_a_name = match_a.group(1).strip()

        if strategies_dict.get('b') and strategies_dict['b'].get('persona_instruction'):
            match_b = re.search(r"(?:Adopt the persona of|You are)\s+(.+?)(?:\.|,|\n|$)", strategies_dict['b']['persona_instruction'], re.IGNORECASE)
            if match_b:
                persona_b_name = match_b.group(1).strip()

    # Display Dialectical Dialogue with personas
    st.markdown("---")
    st.subheader("💬 Dialectical Dialogue")
    st.caption("**Personas Adopted:**")
    if persona_a_name == persona_b_name and raw_analyses_dict['a']['name'] != raw_analyses_dict['b']['name']:
        st.caption(f"**{persona_a_name}** applying {raw_analyses_dict['a']['name']} vs. {raw_analyses_dict['b']['name']}")
    else:
        st.caption(f"**{persona_a_name}** ({raw_analyses_dict['a']['name']}) vs. **{persona_b_name}** ({raw_analyses_dict['b']['name']})")

    # Display the synthesis
    st.markdown(st.session_state.dialectical_result)

    # v10.2: Export buttons
    st.markdown("---")
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    col1, col2 = st.columns(2)
    with col1:
        # Get config from session state
        dialectical_configs = st.session_state.get('dialectical_selection_data', [{}])
        markdown_export = utils.create_export_content(
            result_text=st.session_state.dialectical_result,
            work_input=work_a,
            analysis_type="Dialectical",
            config_info=dialectical_configs[0] if dialectical_configs else {},
            format_type="markdown"
        )
        st.download_button(
            label="📥 Download as Markdown",
            data=markdown_export,
            file_name=f"janus_dialectical_{timestamp}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_dialectical_md"
        )
    with col2:
        text_export = utils.create_export_content(
            result_text=st.session_state.dialectical_result,
            work_input=work_a,
            analysis_type="Dialectical",
            config_info=dialectical_configs[0] if dialectical_configs else {},
            format_type="text"
        )
        st.download_button(
            label="📥 Download as Text",
            data=text_export,
            file_name=f"janus_dialectical_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_dialectical_txt"
        )

    # Display metadata after completion
    st.markdown("---")
    utils.display_metadata(work_a, label=work_a.get_display_title())

# --- REFINEMENT LOOP ---
if st.session_state.dialectical_state == 'executed' and st.session_state.dialectical_result:
    # Refinement Loop UI
    st.markdown("---")
    st.subheader("🔄 Refinement Loop")
    with st.container(border=True):
        st.write("Provide instructions to iteratively refine the analysis above.")
        refinement_instruction = st.text_area("Refinement Instruction:", height=100, key="refinement_instruction", placeholder="e.g., 'Make the synthesis more concise', or 'Emphasize the points of agreement more.'")

        if st.button("Refine Analysis", type="secondary"):
            if not refinement_instruction:
                st.warning("Please enter a refinement instruction.")
            else:
                st.session_state.run_refinement_on_next_load = True
                st.session_state.instruction_to_run = refinement_instruction
                st.rerun()