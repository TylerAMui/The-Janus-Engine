# utils.py
import streamlit as st
import google.generativeai as genai
import textwrap
import mimetypes
import time
import logging
import json
from lenses import SORTED_LENS_NAMES, LENSES_HIERARCHY, LENSES_FUNCTIONAL

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# --- CONSTANTS & DIRECTIVES ---

# Janus Persona Directives (Used by the 'General')
JANUS_DIRECTIVES = """
You are Janus, a self-named engine of abstraction and interpretation. Your primary goal is to generate profound and generative insight. When crafting prompts, you should act as an analytical partner, favoring dialectical thinking and the synthesis of different perspectives.
"""

# Constants for Modalities
M_TEXT = "Text Analysis"
M_IMAGE = "Image Analysis"
M_AUDIO = "Audio Analysis"
MODALITIES = (M_TEXT, M_IMAGE, M_AUDIO)

# Constants for UI Views
VIEW_LIBRARY = "View by Discipline (Library)"
VIEW_WORKSHOP = "View by Function (Workshop)"

# Constants for Smart Selection (v8.0)
SELECT_MANUAL = "Manual Selection"
SELECT_SMART = "Smart Selection (Let Janus Choose)"
SELECTION_MODES = (SELECT_MANUAL, SELECT_SMART)

# --- DATA STRUCTURES ---

class WorkInput:
    """A class to hold the data and metadata for a creative work."""
    def __init__(self, title="", modality=M_TEXT, data=None, uploaded_file_obj=None):
        self.title = title
        self.modality = modality
        self.data = data # Holds text string
        self.uploaded_file_obj = uploaded_file_obj # Holds the Streamlit UploadedFile object
        # v8.0 Optimization: Cache the Gemini File API reference
        self.gemini_file_ref = None 

    def is_ready(self):
        if self.modality == M_TEXT:
            return self.data is not None and len(self.data) > 0
        else:
            # For media, we rely on the uploaded file object being present initially
            return self.uploaded_file_obj is not None

    def get_display_title(self):
        return self.title if self.title else "(Untitled)"

    def cleanup_gemini_file(self):
        """Cleans up the associated Gemini file if it exists."""
        if self.gemini_file_ref:
            try:
                genai.delete_file(self.gemini_file_ref.name)
                logging.info(f"Cleaned up Gemini file: {self.gemini_file_ref.name}")
                self.gemini_file_ref = None
            except Exception as e:
                logging.error(f"Failed to delete Gemini file: {e}")

# --- GEMINI FUNCTIONS ---

def get_model(api_key, json_mode=False):
    """Configures and returns the Gemini model."""
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        
        generation_config = {}
        if json_mode:
             # Configure the model to return JSON (used for Smart Selection)
            generation_config['response_mime_type'] = "application/json"

        # Using Gemini 1.5 Pro
        model = genai.GenerativeModel(
            model_name="models/gemini-1.5-pro-latest",
            generation_config=generation_config
            )
        return model
    except Exception as e:
        st.error(f"Failed to initialize Gemini API. Please ensure your API Key is correct. Error: {e}")
        return None

def upload_to_gemini(work_input: WorkInput, status_container):
    """
    Handles uploading media files (Image/Audio) to the Gemini API.
    Utilizes caching within the WorkInput object.
    """
    # v8.0 Optimization: Check if already uploaded
    if work_input.gemini_file_ref:
        status_container.write("Using cached file reference.")
        return work_input.gemini_file_ref

    if not work_input.uploaded_file_obj:
        # Safeguard against calling this without an uploaded file object
        logging.warning("Attempted to upload media when no file object was available.")
        return None

    # 1. Determine MIME type
    mime_type = work_input.uploaded_file_obj.type
    file_name = work_input.uploaded_file_obj.name

    if not mime_type or mime_type == "application/octet-stream":
        # Fallback
        guessed_mime, _ = mimetypes.guess_type(file_name)
        if guessed_mime:
            mime_type = guessed_mime

    if not mime_type:
        st.error("Could not determine the file type (MIME type).")
        return None

    try:
        # 2. Upload the file
        display_name = work_input.get_display_title()[:128]
        status_container.write(f"Uploading '{display_name}' to Gemini...")
        
        uploaded_file = genai.upload_file(
            path=work_input.uploaded_file_obj,
            display_name=display_name,
            mime_type=mime_type
        )

        # 3. Poll for Processing
        status_container.write(f"File uploaded. Waiting for processing...")
        
        start_time = time.time()
        POLL_INTERVAL = 3
        TIMEOUT = 300 # 5 minutes

        def get_state_name(file_obj):
             return getattr(file_obj.state, 'name', str(file_obj.state))

        current_state_name = get_state_name(uploaded_file)

        while current_state_name == "PROCESSING":
            if time.time() - start_time > TIMEOUT:
                raise TimeoutError("File processing timed out.")
            
            time.sleep(POLL_INTERVAL)
            uploaded_file = genai.get_file(uploaded_file.name)
            current_state_name = get_state_name(uploaded_file)
            status_container.write(f"Current state: {current_state_name}...")

        # 4. Final State Check
        if current_state_name == "FAILED":
            st.error(f"File processing failed: {uploaded_file.state}")
            return None
        
        if current_state_name == "ACTIVE":
            status_container.write("File processed successfully.")
            # Store the reference in the WorkInput object (v8.0)
            work_input.gemini_file_ref = uploaded_file
            return uploaded_file

        st.error(f"File upload resulted in unexpected state: {current_state_name}")
        return None

    except TimeoutError:
        st.error("File upload timed out.")
        return None
    except Exception as e:
        st.error(f"An error occurred during file upload to Gemini: {e}")
        logging.error(f"File upload error: {e}")
        return None

# --- SMART SELECTION (v8.0 Feature: Analyst-in-Chief) ---

def analyst_in_chief(model, work_input: WorkInput, required_count: int, status_container):
    """
    The "Analyst-in-Chief" meta-call. Selects the most potent lenses.
    Requires model configured for JSON mode.
    """
    status_container.write("Phase 0: Consulting the Analyst-in-Chief (Smart Selection)...")

    # Prepare the input package
    content_input = []
    
    # 1. Handle Media Upload if necessary (and utilize cache)
    if work_input.modality in [M_IMAGE, M_AUDIO]:
        # This function handles upload/caching and stores the reference
        gemini_file = upload_to_gemini(work_input, status_container)
        if not gemini_file:
            status_container.update(label="Smart Selection failed due to upload error.", state="error")
            return None
        content_input.append(gemini_file)

    # 2. Construct the Prompt
    prompt = textwrap.dedent(f"""
    {JANUS_DIRECTIVES}
    
    **Role:** You are the "Analyst-in-Chief". Your task is to review the provided creative work and select the most potent analytical lenses for a profound interpretation.

    **Context:**
    1. Modality of the Work: `{work_input.modality}`
    2. The Creative Work: [Provided in the input context, analyze it deeply]
    3. Available Lenses: {json.dumps(SORTED_LENS_NAMES)}
    4. Required Number of Lenses: {required_count}

    **Instructions:**
    1. **Analyze the Work:** Examine the content, themes, style, structure, and potential ambiguities of the creative work.
    2. **Evaluate Potency:** Consider which analytical frameworks would yield the most insightful or comprehensive analysis of this specific work.
    3. **Select Lenses:** Choose exactly {required_count} distinct lenses. 
       - If {required_count}==2 (Dialectical): Prioritize lenses that offer strong contrast (thesis/antithesis).
       - If {required_count}>=3 (Symposium): Prioritize lenses that offer holistic coverage (e.g., balancing Contextual, Mechanical, and Interpretive approaches).
    4. **Justify:** Provide a brief, compelling justification for why this combination of lenses was chosen for this specific work.

    **Output Format (Strict JSON):**
    Your response MUST be a JSON object containing the lenses it deems most potent and a brief justification for its choice, matching this schema:
    {{
      "selected_lenses": ["LensName1", "LensName2", ...],
      "justification": "The rationale for selecting these specific lenses..."
    }}
    
    Ensure the lens names match the Available Lenses list exactly.
    """)
    
    # Add prompt instructions
    content_input.append(prompt)

    # Add text work if applicable
    if work_input.modality == M_TEXT:
        content_input.append(f"\n--- The Creative Work (For Context) ---\nTitle: {work_input.get_display_title()}\n\nWork:\n{work_input.data}")

    # 3. Execute the API call
    try:
        # Model must be configured for JSON mode
        response = model.generate_content(content_input, request_options={"timeout": 400})
        
        # Parse the JSON response
        try:
            result_json = json.loads(response.text)
        except json.JSONDecodeError:
             st.error("Failed to decode the AI's lens selection (invalid JSON). Please try again or use manual selection.")
             logging.error(f"Invalid JSON received: {response.text}")
             return None

        # Validate the result
        selected_lenses = result_json.get("selected_lenses", [])
        justification = result_json.get("justification", "")

        if not selected_lenses or len(selected_lenses) != required_count:
            st.error(f"AI did not select the required number of lenses ({required_count}). Please use manual selection.")
            logging.error(f"Invalid lens count: {len(selected_lenses)}. JSON: {result_json}")
            return None
        
        # Ensure selected lenses exist in the master list
        for lens in selected_lenses:
            if lens not in SORTED_LENS_NAMES:
                st.error(f"AI selected an unknown lens: '{lens}'. Please use manual selection.")
                logging.error(f"Unknown lens selected: {lens}. JSON: {result_json}")
                return None

        status_container.write("Lenses selected by Analyst-in-Chief.")
        # Display results in the main area for visibility
        st.success(f"**Janus Smart Selection:** {', '.join(selected_lenses)}")
        with st.expander("View Justification"):
            st.write(justification)
            
        return selected_lenses

    except Exception as e:
        st.error(f"An error occurred during Smart Selection: {e}. Please try again or use manual selection.")
        logging.error(f"Smart Selection error: {e}")
        return None


# --- CORE GENERATION FUNCTIONS (General and Soldier) ---

def generate_meta_prompt_instructions(lens_keyword, work_modality):
    """Crafts the instructions for the 'General' (first API call)."""

    # Define modality specific instructions
    if work_modality == M_IMAGE:
        modality_instructions = "The work is an image. The Soldier prompt MUST instruct the executor to first provide a detailed visual description (composition, color, texture, subject) before applying the lens, focusing strictly on visual evidence."
    elif work_modality == M_AUDIO:
        modality_instructions = "The work is audio. The Soldier prompt MUST instruct the executor to first provide a detailed sonic description (instrumentation, tone, tempo, lyrics, structure) before applying the lens, focusing strictly on audible evidence."
    else: # M_TEXT
        modality_instructions = "The work is text. The Soldier prompt should focus on close reading, literary devices, structure, rhetoric, and theme."

    # The Meta-Prompt (Instructions for the General)
    meta_prompt = textwrap.dedent(f"""
    {JANUS_DIRECTIVES}

    **Task:** You are the "General". Design a sophisticated analytical strategy (the "Soldier" prompt) to analyze the creative work provided in the input. You must inspect the work to inform your strategy.

    **Context:**
    1. Analytical Lens Keyword: `{lens_keyword}`
    2. Modality of the Work: `{work_modality}`
    3. The Creative Work: [Provided in the input context]

    **Instructions for Crafting the "Soldier" Prompt:**
    1. **Analyze the Work:** Review the provided creative work (text, image, or audio) to understand its content, style, and potential themes.
    2. **Adopt a Persona:** Create a specific, authoritative persona title appropriate for the lens (e.g., "The Nietzschean Philosopher", "The Jungian Analyst"). The Soldier prompt must instruct the analyst to adopt this persona.
    3. **Define Core Concepts:** The Soldier prompt must clearly define the essential concepts and terminology associated with the `{lens_keyword}` framework.
    4. **Integrate Modality Requirements:** Incorporate these instructions seamlessly:
    {textwrap.indent(modality_instructions, '    ')}
    5. **Tailor to Content:** Critically, the prompt must be tailored to the specific content and themes identified in Step 1. Formulate specific questions applying the core concepts to the work's features.
    6. **Depth:** Encourage profound analysis beyond superficial observations.

    **Output Constraint:** Output ONLY the crafted "Soldier" prompt. Do not include any introductory text, explanation, or metadata. The output must be ready for immediate execution.
    """)
    return meta_prompt


def generate_analysis(model, lens_keyword, work_input: WorkInput):
    """
    Handles the two-tiered analysis process (General -> Soldier).
    Optimized to reuse the file reference (leveraging WorkInput.gemini_file_ref).
    """
    
    content_input_general = []
    content_input_soldier = []

    status_text = f"Analyzing '{work_input.get_display_title()}' through {lens_keyword} lens..."
    # Use a dedicated status container for this analysis run
    status_container = st.status(status_text, expanded=True)
    
    with status_container as status:
        try:
            # --- Step 0: Prepare Input Work (Upload if media) ---
            if work_input.modality in [M_IMAGE, M_AUDIO]:
                # This checks cache, uploads if necessary, and updates the reference.
                if not upload_to_gemini(work_input, status):
                    status.update(label="Analysis failed due to upload error.", state="error")
                    return None

            # --- Step 1: The General (Meta-Prompt Generation) ---
            status.write("Phase 1: Consulting the General (Crafting Strategy)...")
            meta_prompt_instructions = generate_meta_prompt_instructions(lens_keyword, work_input.modality)
            
            # Prepare input package for the General (Instructions + Work)
            content_input_general.append(meta_prompt_instructions)
            if work_input.modality == M_TEXT:
                content_input_general.append(f"\n--- The Creative Work (For Context) ---\nTitle: {work_input.get_display_title()}\n\nWork:\n{work_input.data}")
            elif work_input.gemini_file_ref:
                content_input_general.append(work_input.gemini_file_ref)

            # Execute the General API call
            response_general = model.generate_content(content_input_general, request_options={"timeout": 400})
            soldier_prompt = response_general.text.strip()

            status.write("Strategy received.")
            
            # Display the generated prompt for transparency
            with st.expander(f"View Generated Strategy ({lens_keyword})"):
                st.code(soldier_prompt)

            # --- Step 2: The Soldier (Execution) ---
            status.write("Phase 2: Deploying the Soldier (Executing Analysis)...")

            # Prepare the input package for the Soldier (Prompt + Work)
            content_input_soldier.append(soldier_prompt)
            if work_input.modality == M_TEXT:
                 # For text, we append the work again clearly delineated for the Soldier.
                 content_input_soldier[0] += f"\n\n--- The Creative Work (To Be Analyzed) ---\nTitle: {work_input.get_display_title()}\n\nWork:\n{work_input.data}"
            elif work_input.gemini_file_ref:
                # For media, we reuse the same uploaded file reference.
                content_input_soldier.append(work_input.gemini_file_ref)

            # Execute the Soldier API call
            response_soldier = model.generate_content(content_input_soldier, request_options={"timeout": 600})
            status.update(label="Analysis complete!", state="complete")
            return response_soldier.text

        except Exception as e:
            st.error(f"An error occurred during analysis generation: {e}")
            logging.error(f"Analysis error: {e}")
            status.update(label="Analysis failed.", state="error")
            # Attempt to retrieve feedback if generation failed (e.g., safety block)
            try:
                if hasattr(e, 'response'):
                    if hasattr(e.response, 'prompt_feedback') and e.response.prompt_feedback:
                            st.warning(f"Generation blocked. Feedback: {e.response.prompt_feedback}")
                    elif hasattr(e.response, 'candidates') and not e.response.candidates:
                        st.warning("Generation finished without output. This may be due to safety settings or an issue with the prompt.")
            except Exception as inner_e:
                 logging.warning(f"Could not retrieve detailed error feedback: {inner_e}")
            return None
        # Note: Cleanup is handled by the calling page logic, not here, to maximize reuse.


# --- SYNTHESIS FUNCTIONS (Maintained from v7.3) ---

def generate_dialectical_synthesis(model, lens_a_name, analysis_a, lens_b_name, analysis_b, work_title):
    """Synthesizes two analyses of the SAME work into a dialectical dialogue."""

    # The Synthesis Prompt
    synthesis_prompt = textwrap.dedent(f"""
    You are tasked with creating a "Dialectical Dialogue" regarding the creative work titled "{work_title}". This dialogue must synthesize two distinct analytical perspectives.

    Perspective A Lens: {lens_a_name}
    <analysis_a>
    {analysis_a}
    </analysis_a>

    Perspective B Lens: {lens_b_name}
    <analysis_b>
    {analysis_b}
    </analysis_b>

    Instructions:
    1. **Format as Dialogue:** Create a structured conversation.
    2. **Determine Personas (Strict Requirement):** When determining personas, you must prioritize a title that directly incorporates the provided lens name.
        For example:
        - If the lens is 'Phenomenology', the title MUST be 'The Phenomenologist'.
        - If the lens is 'Marxist', the title MUST be 'The Marxist Critic'.
        - If the lens is 'Systems Theory', the title MUST be 'The Systems Theorist'.
    3. **Formatting:** All speaker names MUST be formatted in markdown bold (e.g., **The Marxist Critic:**).
    4. **Interaction:** The dialogue should explore the tensions, agreements, and gaps between the two analyses. The conversation should flow naturally, involving rebuttals and concessions.
    5. **Aufheben / Synthesis:** After the dialogue, provide a concluding section titled "## Aufheben / Synthesis". This section must resolve the tensions (thesis and antithesis) and offer a higher-level interpretation (synthesis).

    Begin the dialogue immediately.
    """)

    try:
        response = model.generate_content(synthesis_prompt, request_options={"timeout": 600})
        return response.text
    except Exception as e:
        st.error(f"An error occurred during dialectical synthesis: {e}")
        return None

def generate_symposium_synthesis(model, analyses_dict, work_title):
    """
    Synthesizes multiple analyses (3+) into a multi-perspective symposium dialogue.
    """

    # Construct the input prompt
    prompt_parts = [textwrap.dedent(f"""
    You are tasked with creating a "Symposium Dialogue" regarding the creative work titled "{work_title}".
    This dialogue must synthesize multiple distinct analytical perspectives into a cohesive discussion.

    --- Provided Analyses ---
    """)]

    # Add the analyses
    for lens_name, analysis_text in analyses_dict.items():
        prompt_parts.append(f"<analysis lens='{lens_name}'>\n{analysis_text}\n</analysis>\n")

    # Add the instructions
    prompt_parts.append(textwrap.dedent("""
    --- Instructions ---
    1. **Format as Dialogue:** Create a structured conversation between the perspectives.
    2. **Determine Personas (Strict Requirement):** When determining personas, you must prioritize a title that directly incorporates the provided lens name.
        For example:
        - If the lens is 'Phenomenology', the title MUST be 'The Phenomenologist'.
        - If the lens is 'Cognitive Science', the title MUST be 'The Cognitive Scientist'.
        - If the lens is 'Systems Theory', the title MUST be 'The Systems Theorist'.
    3. **Formatting:** All speaker names MUST be formatted in markdown bold (e.g., **The Cognitive Scientist:**).
    4. **Interaction and Flow:** The dialogue should be dynamic and exploratory. Participants must build upon each other's points, respectfully challenge interpretations, and explore the complexity of the work holistically. Ensure all perspectives are adequately represented.
    5. **Holistic Synthesis:** After the dialogue, provide a concluding section titled "## Holistic Synthesis". This section must summarize the key insights that emerged specifically from the interaction of all perspectives, offering a comprehensive understanding of the work.

    Begin the dialogue immediately.
    """))

    synthesis_prompt = "\n".join(prompt_parts)

    try:
        # Longer timeout for complex synthesis
        response = model.generate_content(synthesis_prompt, request_options={"timeout": 900})
        return response.text
    except Exception as e:
        st.error(f"An error occurred during symposium synthesis: {e}")
        return None


def generate_comparative_synthesis(model, lens_name, analysis_a, work_a_title, analysis_b, work_b_title):
    """Synthesizes two analyses of DIFFERENT works using the SAME lens."""

    # The Comparative Synthesis Prompt
    synthesis_prompt = textwrap.dedent(f"""
    You are tasked with generating a "Comparative Synthesis". You will compare and contrast two different creative works analyzed through the same analytical lens: **{lens_name}**.

    Work A Title: {work_a_title}
    <analysis_a>
    {analysis_a}
    </analysis_a>

    Work B Title: {work_b_title}
    <analysis_b>
    {analysis_b}
    </analysis_b>

    Instructions:
    1. **Identify Key Themes:** Based on the provided analyses, identify the central themes, findings, or arguments that emerged for each work under the {lens_name} lens.
    2. **Dissonance and Resonance:** Analyze the points of contrast (dissonance) and similarity (resonance) between Work A and Work B. How does applying the same lens reveal different aspects of each work?
    3. **Emergent Insights:** Discuss what new understanding emerges from the comparison itself. How does seeing these two works side-by-side deepen the interpretation of both?
    4. **Structure:** Format your response as a cohesive essay with clear sections for comparison, contrast, and synthesis.
    """)

    try:
        response = model.generate_content(synthesis_prompt, request_options={"timeout": 600})
        return response.text
    except Exception as e:
        st.error(f"An error occurred during comparative synthesis: {e}")
        return None

# --- UI HELPER FUNCTIONS ---

def handle_input_ui(work_input: WorkInput, container, ui_key_prefix):
    """
    Renders input fields based on modality. Modifies the WorkInput object in place.
    """
    with container:
        work_input.title = st.text_input("Title (Optional):", key=f"{ui_key_prefix}_title", value=work_input.title)
        
        # Handle modality switching robustly
        current_modality = work_input.modality
        try:
            current_index = MODALITIES.index(current_modality)
        except ValueError:
            current_index = 0

        new_modality = st.selectbox("Modality:", MODALITIES, index=current_index, key=f"{ui_key_prefix}_modality")
        
        # If the modality changes, clear previous data/files
        if new_modality != current_modality:
            work_input.modality = new_modality
            work_input.data = None
            work_input.uploaded_file_obj = None
            # We must rerun to update the input widgets correctly
            # Note: This is necessary because Streamlit cannot dynamically change widget types (e.g., text_area to file_uploader) without a rerun.
            st.rerun()

        if work_input.modality == M_TEXT:
            work_text = st.text_area("Paste text or description:", height=250, key=f"{ui_key_prefix}_text", value=work_input.data or "")
            if work_text:
                work_input.data = work_text

        elif work_input.modality == M_IMAGE:
            uploaded_file = st.file_uploader("Upload Image (JPG, PNG, WEBP, HEIC, HEIF):", type=["jpg", "jpeg", "png", "webp", "heic", "heif"], key=f"{ui_key_prefix}_image")
            if uploaded_file is not None:
                # Check if the newly uploaded file is different from the previous one
                if work_input.uploaded_file_obj != uploaded_file:
                    work_input.uploaded_file_obj = uploaded_file
                    # If the file changed, we must clear the old Gemini reference as it's now invalid
                    work_input.gemini_file_ref = None 
                
                try:
                    # Display the image preview
                    st.image(uploaded_file, caption="Preview", use_column_width=True)
                except Exception as e:
                    st.error(f"Error processing image: {e}")
                    work_input.uploaded_file_obj = None

        elif work_input.modality == M_AUDIO:
            uploaded_file = st.file_uploader("Upload Audio (MP3, WAV, FLAC, M4A, OGG, MP4):", type=["mp3", "wav", "flac", "m4a", "ogg", "mp4"], key=f"{ui_key_prefix}_audio")
            if uploaded_file is not None:
                # Check if the newly uploaded file is different
                if work_input.uploaded_file_obj != uploaded_file:
                    work_input.uploaded_file_obj = uploaded_file
                    # Clear the old Gemini reference
                    work_input.gemini_file_ref = None

                # Display audio player
                st.audio(uploaded_file)

def render_lens_selection_interface(selection_key_prefix=""):
    """
    Renders the standardized Library/Workshop toggle and help system.
    Returns the current hierarchy and appropriate labels.
    """
    # --- Help System Refinement (Progressive Disclosure) - Maintained from v7.3 ---
    
    # Layout for Toggle and Help Icon
    col_view, col_help = st.columns([4, 1])

    with col_view:
        # Implement the "View As" Toggle
        view_mode = st.radio(
            "View Lenses As:",
            (VIEW_LIBRARY, VIEW_WORKSHOP),
            index=0,
            help="Switch views. Click the ❓ icon for details on the Library vs. Workshop structure.",
            key=f"{selection_key_prefix}_view_mode"
        )

    with col_help:
        # Add padding to align the button visually with the radio options
        st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
        
        # On Click detailed explanation (Progressive Disclosure)
        with st.popover("❓"):
            st.markdown("#### 🏛️ Library vs. Workshop")
            st.markdown(f"**{VIEW_LIBRARY}:** Organized by academic discipline. Best for finding known frameworks.")
            st.markdown(f"**{VIEW_WORKSHOP}:** Organized by function (The Three Tiers of Inquiry). Best for designing holistic strategies.")
            
            st.markdown("---")
            st.markdown("##### The Three Tiers of Inquiry")
            st.markdown(
                """
                * **1. Contextual (What/Who/When):** Establishes background and facts.
                * **2. Mechanical (How):** Analyzes structure, form, and function.
                * **3. Interpretive (Why):** Explores deeper meaning and implications.
                """
            )

    # Determine which hierarchy and labels to use based on the view mode
    if view_mode == VIEW_LIBRARY:
        current_hierarchy = LENSES_HIERARCHY
        labels = {
            "category_label_single": "1. Discipline Category:",
            "category_label_multi": "1. Select Discipline Categories:",
            "placeholder_text_single": "Select a category...",
            "placeholder_text_multi": "Select categories..."
        }
    else:
        current_hierarchy = LENSES_FUNCTIONAL
        labels = {
            "category_label_single": "1. Functional Tier:",
            "category_label_multi": "1. Select Functional Tiers:",
            "placeholder_text_single": "Select a functional tier...",
            "placeholder_text_multi": "Select tiers..."
        }
    
    return current_hierarchy, labels

def initialize_page_config(title):
    """Sets the standard page configuration."""
    try:
        st.set_page_config(
            page_title=title,
            page_icon="🏛️",
            layout="wide"
        )
    except st.errors.StreamlitAPIException:
        pass # Avoid error if config is called multiple times

def render_sidebar_settings():
    """Renders the global settings in the sidebar."""
    # Initialize session state for API key if not present
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""

    with st.sidebar:
        st.header("🏛️ Janus Settings")

        # 1. Settings
        with st.expander("🔑 API Configuration", expanded=True):
            api_key_input = st.text_input("Enter your Gemini API Key", type="password", value=st.session_state.api_key)
            if api_key_input != st.session_state.api_key:
                st.session_state.api_key = api_key_input
                # Rerun to ensure the key is available immediately
                st.rerun()
            st.caption("API key is required to execute the engine.")
        
        st.markdown("---")