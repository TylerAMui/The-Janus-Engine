# pages/1_Single_Lens.py
import streamlit as st
import utils
from utils import WorkInput

# --- PAGE SETUP ---
PAGE_TITLE = "Janus v8.0 | Single Lens"
utils.initialize_page_config(PAGE_TITLE)
st.title("1 | Single Lens Analysis")
st.write("Analyze ONE work through ONE specific lens.")

# --- SIDEBAR ---
utils.render_sidebar_settings()

# Initialize Session State for this page's specific selection
if 'single_lens_selection' not in st.session_state:
    st.session_state.single_lens_selection = None

# Initialize WorkInput object in session state to persist data across reruns
if 'work_input_single' not in st.session_state:
    st.session_state.work_input_single = WorkInput()

# --- LENS SELECTION (Sidebar) ---
with st.sidebar:
    st.markdown("---")
    st.subheader("🔬 Lens Selection")

    # Render the standard Library/Workshop interface
    current_hierarchy, labels = utils.render_lens_selection_interface("single")

    # Hierarchical selection
    main_lens_category = st.selectbox(
        labels["category_label_single"],
        options=sorted(list(current_hierarchy.keys())),
        index=None,
        placeholder=labels["placeholder_text_single"],
        key="single_category_select"
    )

    if main_lens_category:
        lens_options = current_hierarchy[main_lens_category]
        
        specific_lens = st.selectbox(
            "2. Specific Lens:",
            options=lens_options,
            index=None,
            placeholder="Select a specific lens...",
            key="single_lens_select"
        )
        if specific_lens:
            # Store the keyword directly
            st.session_state.single_lens_selection = specific_lens
        else:
            st.session_state.single_lens_selection = None
    else:
        st.session_state.single_lens_selection = None

# --- MAIN PAGE ---

selection = st.session_state.single_lens_selection
# Reference the WorkInput object stored in session state
work_a = st.session_state.work_input_single
api_key = st.session_state.get("api_key", "")

if selection:
    st.header(f"Analysis | {selection}")
    st.info(f"Analyzing using the **{selection}** lens. The engine will dynamically generate the optimal prompt strategy based on the input work.")
    
    # Input UI
    st.subheader("Input Work")
    # The handle_input_ui function modifies the work_a object (persisted in session state)
    utils.handle_input_ui(work_a, st.container(border=True), "work_single")

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
            model = utils.get_model(api_key)
            if model:
                st.markdown("---")
                results_area = st.container()

                with results_area:
                    try:
                        # generate_analysis handles the full General/Soldier flow
                        analysis_text = utils.generate_analysis(
                            model,
                            selection,
                            work_a
                        )

                        if analysis_text:
                            st.header("Analysis Result")
                            st.markdown(analysis_text)
                    
                    finally:
                        # CRITICAL: Cleanup uploaded files after analysis is complete
                        work_a.cleanup_gemini_file()

else:
    st.info("⬅️ Please select an analytical category/tier and specific lens from the sidebar to begin.")