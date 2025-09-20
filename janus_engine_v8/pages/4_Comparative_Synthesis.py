# pages/4_Comparative_Synthesis.py
import streamlit as st
import utils
from utils import WorkInput

# --- PAGE SETUP ---
PAGE_TITLE = "Janus v8.0 | Comparative Synthesis"
utils.initialize_page_config(PAGE_TITLE)
st.title("4 | Comparative Synthesis (2 Works)")
st.write("Analyze TWO different works through the SAME lens.")

# --- SIDEBAR ---
utils.render_sidebar_settings()

# Initialize Session State for this page's specific selection
if 'comparative_lens_selection' not in st.session_state:
    st.session_state.comparative_lens_selection = None

# Initialize WorkInput objects in session state
if 'work_input_comparative_a' not in st.session_state:
    st.session_state.work_input_comparative_a = WorkInput()
if 'work_input_comparative_b' not in st.session_state:
    st.session_state.work_input_comparative_b = WorkInput()

# --- LENS SELECTION (Sidebar) ---
with st.sidebar:
    st.markdown("---")
    st.subheader("🔬 Lens Selection")
    st.caption("Select the common lens for comparison.")

    # Render the standard Library/Workshop interface
    current_hierarchy, labels = utils.render_lens_selection_interface("comparative")

    # Hierarchical selection
    main_lens_category = st.selectbox(
        labels["category_label_single"],
        options=sorted(list(current_hierarchy.keys())),
        index=None,
        placeholder=labels["placeholder_text_single"],
        key="comparative_category_select"
    )

    if main_lens_category:
        lens_options = current_hierarchy[main_lens_category]
        
        specific_lens = st.selectbox(
            "2. Specific Lens:",
            options=lens_options,
            index=None,
            placeholder="Select a specific lens...",
            key="comparative_lens_select"
        )
        if specific_lens:
            # Store the keyword directly
            st.session_state.comparative_lens_selection = specific_lens
        else:
            st.session_state.comparative_lens_selection = None
    else:
        st.session_state.comparative_lens_selection = None

# --- MAIN PAGE ---

selection = st.session_state.comparative_lens_selection
# Reference the WorkInput objects stored in session state
work_a = st.session_state.work_input_comparative_a
work_b = st.session_state.work_input_comparative_b
api_key = st.session_state.get("api_key", "")

if selection:
    st.header(f"Analysis | Lens: {selection}")
    st.info(f"Ready to compare two different works through the **{selection}** lens.")
    
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
        # Validation
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

        if is_valid:
            # --- Execution Block ---
            model = utils.get_model(api_key)
            if model:
                st.markdown("---")
                results_area = st.container()

                with results_area:
                    try:
                        # Call 1: Analyze Work A
                        st.subheader(f"Step 1/3: Analyzing Work A")
                        # The General will tailor the prompt specifically to Work A
                        analysis_a = utils.generate_analysis(
                            model,
                            selection,
                            work_a
                        )

                        # Call 2: Analyze Work B
                        analysis_b = None
                        if analysis_a:
                            st.subheader(f"Step 2/3: Analyzing Work B")
                            # The General must be called again to tailor the prompt specifically to Work B
                            analysis_b = utils.generate_analysis(
                                model,
                                selection,
                                work_b
                            )

                        # Call 3: Comparative Synthesis
                        if analysis_a and analysis_b:
                            st.subheader("Step 3/3: Comparative Synthesis")
                            with st.spinner("Generating comparative synthesis..."):
                                synthesis_text = utils.generate_comparative_synthesis(
                                    model,
                                    selection,
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
    st.info("⬅️ Please select the single lens you wish to use for comparison from the sidebar.")
