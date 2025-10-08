import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import textwrap
import mimetypes
import time
import logging
import json
import asyncio
# v9.4b: Updated imports (LENS_ZEITGEIST constant removed)
from lenses import SORTED_LENS_NAMES, LENSES_HIERARCHY, LENSES_FUNCTIONAL, LENSES_BY_ERA, PERSONA_STYLE_GUIDES, PERSONA_POOL, get_lens_data

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
M_VIDEO = "Video Analysis"
MODALITIES = (M_TEXT, M_IMAGE, M_AUDIO, M_VIDEO)

# Constants for Video Processing Modes
V_MODE_FULL = "Full Video Analysis (High Cost/Time)"
V_MODE_KEYFRAMES = "Keyframe Analysis (Medium Cost)"
V_MODE_TRANSCRIPT = "Transcript-Only Analysis (Low Cost)"
VIDEO_MODES = (V_MODE_FULL, V_MODE_KEYFRAMES, V_MODE_TRANSCRIPT)

# Constants for UI Views
VIEW_LIBRARY = "View by Discipline (Library)"
VIEW_WORKSHOP = "View by Function (Workshop)"
VIEW_ERA = "View by Era (Timeline)"

# Constants for Smart Selection
SELECT_MANUAL = "Manual Selection"
SELECT_SMART = "Smart Selection (Let Janus Choose)"
SELECTION_MODES = (SELECT_MANUAL, SELECT_SMART)

# v9.4b: LENS_ZEITGEIST constant removed. Zeitgeist is now handled via configuration flags (is_zeitgeist).

# --- DATA STRUCTURES ---

class WorkInput:
    """A class to hold the data and metadata for a creative work."""
    def __init__(self, title="", modality=M_TEXT, data=None, uploaded_file_obj=None):
        self.title = title
        self.modality = modality
        self.data = data # Holds text string
        self.uploaded_file_obj = uploaded_file_obj # Holds the Streamlit UploadedFile object
        # Optimization: Cache the Gemini File API reference
        self.gemini_file_ref = None
        # Video processing options
        self.video_mode = V_MODE_FULL
        self.keyframe_interval = 10 # Default interval in seconds

    def is_ready(self):
        if self.modality == M_TEXT:
            return self.data is not None and len(self.data) > 0
        else:
            return self.uploaded_file_obj is not None

    def get_display_title(self):
        return self.title if self.title else "(Untitled)"

    def cleanup_gemini_file(self):
        """Cleans up the associated Gemini file if it exists."""
        if self.gemini_file_ref:
            try:
                # Ensure the API is configured before calling delete_file
                api_key = st.session_state.get("api_key")
                if api_key:
                    genai.configure(api_key=api_key)
                    genai.delete_file(self.gemini_file_ref.name)
                    logging.info(f"Cleaned up Gemini file: {self.gemini_file_ref.name}")
                else:
                    logging.warning("Could not clean up Gemini file because API key is missing from session state.")
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

        # Using Gemini 2.5 Pro
        model = genai.GenerativeModel(
            model_name="models/gemini-2.5-pro",
            generation_config=generation_config
            )
        return model
    except Exception as e:
        st.error(f"Failed to initialize Gemini API. Please ensure your API Key is correct. Error: {e}")
        return None

def upload_to_gemini(work_input: WorkInput, status_container):
    # (Implementation remains the same as v9.4a)
    """
    Handles uploading media files (Image/Audio/Video) to the Gemini API.
    Utilizes caching within the WorkInput object.
    """
    # Check if already uploaded
    if work_input.gemini_file_ref:
        status_container.write("Using cached file reference.")
        return work_input.gemini_file_ref

    if not work_input.uploaded_file_obj:
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
        status_container.write(f"File uploaded. Waiting for processing (this may take time for video/audio)...")
        
        start_time = time.time()
        POLL_INTERVAL = 5
        TIMEOUT = 600 # 10 minutes timeout

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
            # Store the reference in the WorkInput object
            work_input.gemini_file_ref = uploaded_file
            return uploaded_file

        st.error(f"File upload resulted in unexpected state: {current_state_name}")
        return None

    # Catch specific Google API errors
    except google_exceptions.PermissionDenied:
        st.error("Permission Denied. Please ensure your API Key is valid and has access to the Gemini 2.5 Pro model.")
        return None
    except google_exceptions.ResourceExhausted:
        st.error("Resource Exhausted. You may have hit API rate limits. Please wait a moment and try again, or check your quota.")
        return None
    except TimeoutError:
        st.error("File upload timed out.")
        return None
    except Exception as e:
        st.error(f"An error occurred during file upload to Gemini: {e}")
        logging.error(f"File upload error: {e}")
        return None

async def upload_to_gemini_async(work_input: WorkInput, status_container):
    """
    Asynchronous version of upload_to_gemini.
    Handles uploading media files (Image/Audio/Video) to the Gemini API.
    Utilizes caching within the WorkInput object.
    """
    if work_input.gemini_file_ref:
        status_container.write("Using cached file reference.")
        return work_input.gemini_file_ref

    if not work_input.uploaded_file_obj:
        logging.warning("Attempted to upload media when no file object was available.")
        return None

    mime_type = work_input.uploaded_file_obj.type
    file_name = work_input.uploaded_file_obj.name

    if not mime_type or mime_type == "application/octet-stream":
        guessed_mime, _ = mimetypes.guess_type(file_name)
        if guessed_mime:
            mime_type = guessed_mime

    if not mime_type:
        st.error("Could not determine the file type (MIME type).")
        return None

    try:
        display_name = work_input.get_display_title()[:128]
        status_container.write(f"Uploading '{display_name}' to Gemini...")
        
        uploaded_file = await genai.upload_file_async(
            path=work_input.uploaded_file_obj,
            display_name=display_name,
            mime_type=mime_type
        )

        status_container.write(f"File uploaded. Waiting for processing (this may take time for video/audio)...")
        
        start_time = time.time()
        POLL_INTERVAL = 5
        TIMEOUT = 600

        def get_state_name(file_obj):
             return getattr(file_obj.state, 'name', str(file_obj.state))

        current_state_name = get_state_name(uploaded_file)

        while current_state_name == "PROCESSING":
            if time.time() - start_time > TIMEOUT:
                raise TimeoutError("File processing timed out.")
            
            await asyncio.sleep(POLL_INTERVAL)
            uploaded_file = await genai.get_file_async(uploaded_file.name)
            current_state_name = get_state_name(uploaded_file)
            status_container.write(f"Current state: {current_state_name}...")

        # 4. Final State Check
        if current_state_name == "FAILED":
            st.error(f"File processing failed: {uploaded_file.state}")
            return None
        
        if current_state_name == "ACTIVE":
            status_container.write("File processed successfully.")
            # Store the reference in the WorkInput object
            work_input.gemini_file_ref = uploaded_file
            return uploaded_file

        st.error(f"File upload resulted in unexpected state: {current_state_name}")
        return None

    except google_exceptions.PermissionDenied:
        st.error("Permission Denied. Please ensure your API Key is valid and has access to the Gemini 2.5 Pro model.")
        return None
    except google_exceptions.ResourceExhausted:
        st.error("Resource Exhausted. You may have hit API rate limits. Please wait a moment and try again, or check your quota.")
        return None
    except TimeoutError:
        st.error("File upload timed out.")
        return None
    except Exception as e:
        st.error(f"An error occurred during file upload to Gemini: {e}")
        logging.error(f"File upload error: {e}")
        return None

# --- SMART SELECTION (Analyst-in-Chief) ---

def analyst_in_chief(model, work_input: WorkInput, required_count: int, status_container):
    # v9.4b: Updated prompt to remove the constraint about Zeitgeist, as it's no longer a lens.
    """
    The "Analyst-in-Chief" meta-call. Selects the most potent lenses.
    Requires model configured for JSON mode.
    """
    status_container.write("Phase 0: Consulting the Analyst-in-Chief (Smart Selection)...")

    # Prepare the input package
    content_input = []
    
    # 1. Handle Media Upload if necessary (and utilize cache)
    if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
        # This function handles upload/caching and stores the reference
        gemini_file = upload_to_gemini(work_input, status_container)
        if not gemini_file:
            status_container.update(label="Smart Selection failed due to upload error.", state="error")
            return None
        content_input.append(gemini_file)

    # Inform Analyst-in-Chief about Video Mode constraints if applicable
    video_mode_context = ""
    if work_input.modality == M_VIDEO:
        video_mode_context = f"5. Video Analysis Scope Constraint: `{work_input.video_mode}`"
        if work_input.video_mode == V_MODE_TRANSCRIPT:
            video_mode_context += " (CRITICAL: When selecting lenses, you MUST prioritize those relevant ONLY to the audio/transcript content. Lenses requiring visual analysis are inappropriate.)"
        elif work_input.video_mode == V_MODE_KEYFRAMES:
             video_mode_context += " (Focus selection on lenses appropriate for analyzing sparse visual moments combined with the audio/transcript.)"


    # 2. Construct the Prompt
    # v9.4b: Removed the constraint regarding the "Zeitgeist" lens.
    prompt = textwrap.dedent(f"""
    {JANUS_DIRECTIVES}
    
    **Role:** You are the "Analyst-in-Chief". Your task is to review the provided creative work and select the most potent analytical lenses for a profound interpretation.

    **Context:**
    1. Modality of the Work: `{work_input.modality}`
    2. The Creative Work: [Provided in the input context, analyze it deeply]
    3. Available Lenses: {json.dumps(SORTED_LENS_NAMES)}
    4. Required Number of Lenses: {required_count}
    {video_mode_context}

    **Instructions:**
    1. **Analyze the Work:** Examine the content, themes, style, structure, and potential ambiguities of the creative work.
    2. **Evaluate Potency:** Consider which analytical frameworks would yield the most insightful or comprehensive analysis of this specific work, respecting the modality constraints (if specified above).
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

# v9.5a: Updated to implement the "General's Toolkit" architecture (Lead and Support Protocol).
def generate_meta_prompt_instructions(lens_config: dict, work_input: WorkInput):
    """
    Crafts the instructions for the 'General' (first API call).
    v9.5a: Implements the "General's Toolkit" (Lead and Support Protocol).
    """
    
    lens_keyword = lens_config.get('lens') # The UI Name (dictionary key)
    specific_persona = lens_config.get('persona') # Standard persona override
    is_zeitgeist_mode = lens_config.get('is_zeitgeist', False)
    
    work_modality = work_input.modality

    # --- Modality Specific Instructions (Abstracted for reuse) ---
    def get_modality_instructions(work_input: WorkInput):
        # (Implementation remains the same as v9.4a)
        work_modality = work_input.modality
        if work_modality == M_IMAGE:
            return "The work is an image. The Soldier prompt MUST instruct the executor to first provide a detailed visual description (composition, color, texture, subject) before applying the lens, focusing strictly on visual evidence."
        elif work_modality == M_AUDIO:
            return "The work is audio. The Soldier prompt MUST instruct the executor to first provide a detailed sonic description (instrumentation, tone, tempo, lyrics, structure) before applying the lens, focusing strictly on audible evidence."
        elif work_modality == M_TEXT:
            return "The work is text. The Soldier prompt should focus on close reading, literary devices, structure, rhetoric, and theme."
        elif work_modality == M_VIDEO:
            video_mode = work_input.video_mode
            if video_mode == V_MODE_FULL:
                return """
                The work is a video (Full Analysis requested). The Soldier prompt MUST instruct the executor to analyze the video comprehensively, considering visual composition, audio track (transcript), narrative progression, editing, and timing. The analysis must utilize specific timestamps to reference evidence.
                """
            elif video_mode == V_MODE_KEYFRAMES:
                interval = work_input.keyframe_interval
                return f"""
                The work is a video (Keyframe Analysis requested). The Soldier prompt MUST instruct the executor to analyze both the audio track (transcript) AND key visual moments occurring approximately every {interval} seconds. 
                The analysis should synthesize these visual moments with the audio to understand the overall work, utilizing timestamps for reference. Do not analyze every frame; use the interval as the primary guide for visual attention.
                """
            elif video_mode == V_MODE_TRANSCRIPT:
                return """
                The work is a video (Transcript-Only Analysis requested). The Soldier prompt MUST instruct the executor to explicitly ignore all visual information and analyze ONLY the audio transcript (dialogue, narration). 
                The analysis should treat the input as a purely textual work derived from the audio track.
                """
        return ""

    modality_instructions = get_modality_instructions(work_input)

    # --- ZEITGEIST MODE IMPLEMENTATION ---
    # This is a distinct mode, not a lens. It takes priority.
    if is_zeitgeist_mode:
        zeitgeist_context = lens_config.get('zeitgeist_context')
        zeitgeist_persona = lens_config.get('zeitgeist_persona')

        # Validation
        if not zeitgeist_context or not zeitgeist_persona:
            st.error("Internal Error: Zeitgeist mode activated but context or persona data is missing.")
            return None

        # Construct the specialized Meta-Prompt for Zeitgeist
        meta_prompt = textwrap.dedent(f"""
        {JANUS_DIRECTIVES}

        **Task:** You are the "General". Design a sophisticated analytical strategy (the "Soldier" prompt) for a "Zeitgeist Simulation". You must inspect the work to inform your strategy.

        **Context: Zeitgeist Simulation**
        The user wants to analyze the creative work from a specific, simulated historical viewpoint defined by the inputs below. This overrides standard lens definitions.

        1. Modality of the Work: `{work_modality}`
        2. The Creative Work: [Provided in the input context]
        
        3. **User-Defined Historical Context:**
        <historical_context>
        {zeitgeist_context}
        </historical_context>

        4. **User-Defined Witness Persona:**
        <witness_persona>
        {zeitgeist_persona}
        </witness_persona>

        **Instructions for Crafting the "Soldier" Prompt:**
        1. **Analyze the Inputs:** Review the creative work AND the user-defined context/persona. Understand the specific historical moment, cultural assumptions, and the perspective of the witness.
        
        2. **Adopt the Persona (Mandatory):** The Soldier prompt MUST instruct the executor to fully embody the 'Witness Persona'. The analysis must be strictly limited to the knowledge, biases, and language available within the 'Historical Context'.
        
        3. **Define the Zeitgeist:** The Soldier prompt must use the 'Historical Context' as the sole analytical framework. The goal is to understand how the work would be perceived, valued, or criticized at that specific moment by that specific witness.
        
        4. **Integrate Modality Requirements:** Incorporate these instructions seamlessly:
        {textwrap.indent(modality_instructions.strip(), '    ')}
        
        5. **Tailor to Content:** Formulate specific questions that connect the features of the creative work to the specific concerns, events, or ideologies detailed in the 'Historical Context'.
        
        6. **Authenticity:** Encourage historical authenticity in tone and perspective. Avoid anachronism.
        7. **Persona Identification Header:** The Soldier prompt MUST instruct the executor to begin their entire response with a single markdown H3 header identifying their persona, using the title defined in the 'Witness Persona'. For example: '### Analysis by The Londoner, 1941'. This is a critical requirement for the final synthesis stage.

        **Output Constraint:** Output ONLY the crafted "Soldier" prompt. Do not include any introductory text, explanation, or metadata. The output must be ready for immediate execution.
        """)
        return meta_prompt

    # --- STANDARD LENS LOGIC (If not Zeitgeist) ---
    
    # Retrieve Lens Data
    lens_data = get_lens_data(lens_keyword)
    if not lens_data:
        # Fallback for safety
        st.error(f"Internal Error: Lens data not found for {lens_keyword}.")
        return None

    # Determine the Backend Name
    backend_lens_name = lens_data.get("prompt_name") or lens_keyword

    # --- Persona System Logic ---
    persona_instructions = ""

    # --- Hierarchy Implementation ---

    # Tier 1: User-Specified Persona (Highest Priority)
    if specific_persona:
        persona_instructions = textwrap.dedent(f"""
        2. **Adopt a Persona (User Override):** The user has explicitly requested the analysis be conducted by '{specific_persona}'. The Soldier prompt MUST adopt this specific persona authoritatively and authentically, reflecting their known style and focus areas.
        """)

    # Tier 2: Persona Pool (AI Discretion)
    # Note: We use the UI name (lens_keyword) to look up the pool in the dictionary.
    elif lens_keyword in PERSONA_POOL:
        pool = PERSONA_POOL[lens_keyword]
        persona_instructions = textwrap.dedent(f"""
        2. **Adopt a Persona (Proponent Pool):** A pool of known proponents or central figures exists for the '{backend_lens_name}' lens. You MUST choose the single most appropriate persona from this pool based on the specific context and content of the creative work.
        * **Available Pool:** {', '.join(pool)}
        * The Soldier prompt must instruct the executor to adopt the chosen persona authoritatively.
        """)

    # Tier 3: Persona Style Guide (Abstract Persona / Interpreter)
    # Note: We use the UI name (lens_keyword) to look up the guide.
    elif lens_keyword in PERSONA_STYLE_GUIDES:
        style_guide = PERSONA_STYLE_GUIDES[lens_keyword]
        persona_instructions = textwrap.dedent(f"""
        2. **Adopt a Persona (Style Guide):** A specific style guide exists for the '{backend_lens_name}' lens. The Soldier prompt MUST enforce this guide rigorously.
        * **Target Persona:** {style_guide['persona']}
        * **Style Guide Instructions (Tone, Format, Focus):** 
        {textwrap.indent(style_guide['guide'].strip(), '        ')}
        """)

    # Tier 4: Generic Fallback (Lowest Priority)
    else:
        persona_instructions = textwrap.dedent(f"""
        2. **Adopt a Persona (Generated):** Create a specific, authoritative persona for the '{backend_lens_name}' lens.
        * You SHOULD prioritize using the name of a famous, historical proponent if one is widely known (e.g., 'Adam Smith' for Classical Liberalism).
        * **Fallback:** If no single proponent is dominant, or if using a specific name would be clearly anachronistic or misleading, THEN use a descriptive archetypal title (e.g., 'The Phenomenologist').
        * The goal is to give the analysis maximum personality and historical flavor.
        """)

    # --- v9.5a: Conceptual Primer vs. General's Toolkit (The Core Logic) ---
    core_concept_instructions = ""
    conceptual_primer = lens_data.get("conceptual_primer")
    sub_primers_toolkit = lens_data.get("sub_primers")

    # --- v9.5a IMPLEMENTATION: The General's Toolkit (Lead and Support Protocol) ---
    if sub_primers_toolkit and isinstance(sub_primers_toolkit, dict):
        
        # Format the toolkit for the prompt
        toolkit_formatted = []
        for name, primer in sub_primers_toolkit.items():
            toolkit_formatted.append(f"<sub_primer name='{name}'>\n{primer.strip()}\n</sub_primer>")
        
        toolkit_string = "\n\n".join(toolkit_formatted)

        # Define the "Lead and Support" Protocol Instructions
        core_concept_instructions = textwrap.dedent(f"""
        3. **Apply the "General's Toolkit" (Lead and Support Protocol):**
        The '{backend_lens_name}' framework is a "mega-lens" containing a toolkit of specialized sub-primers. You MUST use the following protocol instead of a generalized approach:

        * **The Toolkit:**
        <toolkit>
        {toolkit_string}
        </toolkit>

        * **The Protocol:**
            A. **Diagnose (The Lead):** Analyze the creative work to identify the SINGLE most dominant, potent, or relevant sub-primer from the toolkit. This will be the "Lead" framework for the analysis.
            B. **Identify Support:** Identify any secondary or supporting themes from the OTHER available sub-primers in the toolkit. These will be the "Support" frameworks.
            C. **Strategize (The Soldier Prompt):** Craft the Soldier prompt such that it focuses the analysis primarily on the "Lead" framework. However, the prompt MUST explicitly direct the Soldier to weave in the "Support" frameworks to add nuance, depth, contrast, and a more holistic perspective.
        
        * **Constraint:** You must ONLY use the frameworks provided in the toolkit above.
        """)

    # --- STANDARD IMPLEMENTATION: Conceptual Primer (Fallback) ---
    elif conceptual_primer:
        core_concept_instructions = textwrap.dedent(f"""
        3. **Apply Conceptual Primer:** The Soldier prompt MUST use the following methodological primer as the core framework for the analysis. This defines the specific methodology for the '{backend_lens_name}' approach.
        * **Methodological Primer:**
        {textwrap.indent(conceptual_primer.strip(), '        ')}
        """)
    
    # --- GENERIC IMPLEMENTATION (No Primer Provided) ---
    else:
        core_concept_instructions = textwrap.dedent(f"""
        3. **Define Core Concepts:** The Soldier prompt must clearly define the essential concepts and terminology associated with the `{backend_lens_name}` framework (unless the persona or style guide implies otherwise).
        """)

    # --- Directive for Nuance (The Drill) ---
    nuance_directive = ""
    if lens_data.get("requires_nuance", False):
        nuance_directive = textwrap.dedent("""
        **DIRECTIVE FOR NUANCE (The Drill):**
        The Soldier prompt MUST instruct the analyst to move beyond a general application of the theory. 
        The analysis must focus on the specificity and intersectionality of the identities and situations presented in the work. 
        It must avoid generalizations and ground all claims in a close reading of the specific textual, visual, auditory, or temporal evidence.
        """)

    # The Meta-Prompt (Instructions for the General)
    meta_prompt = textwrap.dedent(f"""
    {JANUS_DIRECTIVES}

    **Task:** You are the "General". Design a sophisticated analytical strategy (the "Soldier" prompt) to analyze the creative work provided in the input. You must inspect the work to inform your strategy.

    **Context:**
    1. Analytical Framework: `{backend_lens_name}`
    2. Modality of the Work: `{work_modality}`
    3. The Creative Work: [Provided in the input context]

    {nuance_directive}

    **Instructions for Crafting the "Soldier" Prompt:**
    1. **Analyze the Work:** Review the provided creative work (text, image, audio, or video) to understand its content, style, and potential themes.
    
    {persona_instructions}
    
    {core_concept_instructions}

    4. **Integrate Modality Requirements:** Incorporate these instructions seamlessly. They define how the Soldier must handle the input medium:
    {textwrap.indent(modality_instructions.strip(), '    ')}
    
    5. **Tailor to Content:** Critically, the prompt must be tailored to the specific content and themes identified in Step 1. Formulate specific questions applying the core concepts (or the chosen primers) to the work's features.
    6. **Depth:** Encourage profound analysis beyond superficial observations.
    7. **Persona Identification Header:** The Soldier prompt MUST instruct the executor to begin their entire response with a single markdown H3 header identifying their persona. For example: '### Analysis by Jean-Paul Sartre' or '### Analysis by The Systems Analyst'. This is a critical requirement for the final synthesis stage.

    **Output Constraint:** Output ONLY the crafted "Soldier" prompt. Do not include any introductory text, explanation, or metadata. The output must be ready for immediate execution.
    """)
    return meta_prompt


# v9.4b: Updated signature to accept lens_config dictionary
def generate_analysis(model, lens_config: dict, work_input: WorkInput):
    """
    Handles the two-tiered analysis process (General -> Soldier).
    v9.4b: Updated status display for new Zeitgeist mode.
    """
    
    lens_keyword = lens_config.get('lens')
    specific_persona = lens_config.get('persona')
    is_zeitgeist_mode = lens_config.get('is_zeitgeist', False)

    content_input_general = []
    content_input_soldier = []

    # Status text setup
    # v9.4b: Handle Zeitgeist Mode status
    if is_zeitgeist_mode:
        status_text = f"Simulating Zeitgeist for '{work_input.get_display_title()}'..."
    elif lens_keyword:
        status_text = f"Analyzing '{work_input.get_display_title()}' through {lens_keyword} lens..."
        if specific_persona:
            status_text = f"Analyzing '{work_input.get_display_title()}' as {specific_persona} ({lens_keyword})..."
    else:
        status_text = f"Analyzing '{work_input.get_display_title()}'..."


    # Use a dedicated status container for this analysis run
    status_container = st.status(status_text, expanded=True)
    
    with status_container as status:
        try:
            # --- Step 0: Prepare Input Work (Upload if media) ---
            if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
                # This checks cache, uploads if necessary, and updates the reference.
                if not upload_to_gemini(work_input, status):
                    status.update(label="Analysis failed due to upload error.", state="error")
                    return None

            # --- Step 1: The General (Meta-Prompt Generation) ---
            status.write("Phase 1: Consulting the General (Crafting Strategy)...")
            
            # Pass the full lens_config dictionary
            meta_prompt_instructions = generate_meta_prompt_instructions(
                lens_config,
                work_input
            )

            if meta_prompt_instructions is None:
                status.update(label="Analysis failed during strategy generation.", state="error")
                return None
            
            # Prepare input package for the General (Instructions + Work)
            content_input_general.append(meta_prompt_instructions)
            if work_input.modality == M_TEXT:
                content_input_general.append(f"\n--- The Creative Work (For Context) ---\nTitle: {work_input.get_display_title()}\n\nWork:\n{work_input.data}")
            elif work_input.gemini_file_ref:
                # Works for Image, Audio, and Video
                content_input_general.append(work_input.gemini_file_ref)

            # Execute the General API call
            response_general = model.generate_content(content_input_general, request_options={"timeout": 600})
            soldier_prompt = response_general.text.strip()

            status.write("Strategy received.")
            
            # Display the generated prompt for transparency
            # v9.4b: Customize expander label
            expander_label = f"View Generated Strategy ({lens_keyword or 'Zeitgeist'})"
            with st.expander(expander_label):
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
            response_soldier = model.generate_content(content_input_soldier, request_options={"timeout": 900})
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

async def async_generate_analysis(model, lens_config: dict, work_input: WorkInput):
    """
    Asynchronous version of generate_analysis.
    Handles the two-tiered analysis process (General -> Soldier).
    """
    lens_keyword = lens_config.get('lens')
    specific_persona = lens_config.get('persona')
    is_zeitgeist_mode = lens_config.get('is_zeitgeist', False)

    content_input_general = []
    content_input_soldier = []

    if is_zeitgeist_mode:
        status_text = f"Simulating Zeitgeist for '{work_input.get_display_title()}'..."
    elif lens_keyword:
        status_text = f"Analyzing '{work_input.get_display_title()}' through {lens_keyword} lens..."
        if specific_persona:
            status_text = f"Analyzing '{work_input.get_display_title()}' as {specific_persona} ({lens_keyword})..."
    else:
        status_text = f"Analyzing '{work_input.get_display_title()}'..."

    status_container = st.status(status_text, expanded=True)
    
    with status_container as status:
        try:
            if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
                if not await upload_to_gemini_async(work_input, status):
                    status.update(label="Analysis failed due to upload error.", state="error")
                    return None

            status.write("Phase 1: Consulting the General (Crafting Strategy)...")
            
            meta_prompt_instructions = generate_meta_prompt_instructions(
                lens_config,
                work_input
            )

            if meta_prompt_instructions is None:
                status.update(label="Analysis failed during strategy generation.", state="error")
                return None
            
            content_input_general.append(meta_prompt_instructions)
            if work_input.modality == M_TEXT:
                content_input_general.append(f"\n--- The Creative Work (For Context) ---\nTitle: {work_input.get_display_title()}\n\nWork:\n{work_input.data}")
            elif work_input.gemini_file_ref:
                content_input_general.append(work_input.gemini_file_ref)

            response_general = await model.generate_content_async(content_input_general, request_options={"timeout": 600})
            soldier_prompt = response_general.text.strip()

            status.write("Strategy received.")
            
            expander_label = f"View Generated Strategy ({lens_keyword or 'Zeitgeist'})"
            with st.expander(expander_label):
                st.code(soldier_prompt)

            status.write("Phase 2: Deploying the Soldier (Executing Analysis)...")

            content_input_soldier.append(soldier_prompt)
            if work_input.modality == M_TEXT:
                content_input_soldier[0] += f"\n\n--- The Creative Work (To Be Analyzed) ---\nTitle: {work_input.get_display_title()}\n\nWork:\n{work_input.data}"
            elif work_input.gemini_file_ref:
                content_input_soldier.append(work_input.gemini_file_ref)

            response_soldier = await model.generate_content_async(content_input_soldier, request_options={"timeout": 900})
            status.update(label="Analysis complete!", state="complete")
            return response_soldier.text

        except Exception as e:
            st.error(f"An error occurred during analysis generation: {e}")
            logging.error(f"Analysis error: {e}")
            status.update(label="Analysis failed.", state="error")
            try:
                if hasattr(e, 'response'):
                    if hasattr(e.response, 'prompt_feedback') and e.response.prompt_feedback:
                            st.warning(f"Generation blocked. Feedback: {e.response.prompt_feedback}")
                    elif hasattr(e.response, 'candidates') and not e.response.candidates:
                        st.warning("Generation finished without output. This may be due to safety settings or an issue with the prompt.")
            except Exception as inner_e:
                logging.warning(f"Could not retrieve detailed error feedback: {inner_e}")
            return None

def generate_refined_analysis(model, work_input: WorkInput, previous_analysis: str, refinement_instruction: str):
    # (Implementation remains the same as v9.4a)
    """
    Refines a previous analysis based on user feedback (Refinement Loop).
    """
    
    if not refinement_instruction or not previous_analysis:
        st.warning("Refinement instruction or previous analysis is missing.")
        return None

    content_input_refiner = []
    status_container = st.status("Executing Refinement Loop...", expanded=True)

    with status_container as status:
        try:
            # --- Step 0: Prepare Input Work (Upload if media) ---
            # Ensure the work is available for the Refiner (handles caching)
            if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
                if not upload_to_gemini(work_input, status):
                    status.update(label="Refinement failed due to upload error.", state="error")
                    return None

            # --- Step 1: Construct the Refinement Prompt ---
            status.write("Phase 1: Analyzing instructions and previous analysis...")

            refinement_prompt = textwrap.dedent(f"""
            {JANUS_DIRECTIVES}

            **Task:** You are the "Refiner". Your goal is to iteratively improve a previous analysis of a creative work based on specific user instructions.

            **Context:**
            1. The Creative Work: [Provided in the input context]
            2. Modality: {work_input.modality}
            3. Title: {work_input.get_display_title()}

            **Previous Analysis:**
            <previous_analysis>
            {previous_analysis}
            </previous_analysis>

            **Refinement Instruction (CRITICAL):**
            The user has requested the following refinement to the analysis:
            <instruction>
            {refinement_instruction}
            </instruction>

            **Instructions:**
            1. **Analyze the Instruction:** Understand the user's intent (e.g., deeper focus on a specific element, change in tone, exploring a contradiction, addressing a missed detail).
            2. **Review the Work and Previous Analysis:** Evaluate how the previous analysis aligns with the work and where it needs modification according to the instruction.
            3. **Generate Revised Analysis:** Create a complete, revised analysis that incorporates the refinement instruction seamlessly. This is NOT a delta or a commentary on the previous analysis; it is the new, improved analysis replacing the old one.
            4. **Maintain Quality:** Ensure the revised analysis remains profound, nuanced, and well-supported by evidence from the creative work. Maintain the original persona and analytical lens unless the instruction explicitly asks to change them.
            
            Output the revised analysis immediately.
            """)

            # Prepare input package for the Refiner (Prompt + Work)
            content_input_refiner.append(refinement_prompt)
            if work_input.modality == M_TEXT:
                # Append the work clearly delineated for the Refiner.
                content_input_refiner[0] += f"\n\n--- The Creative Work (To Be Re-Analyzed) ---\nTitle: {work_input.get_display_title()}\n\nWork:\n{work_input.data}"
            elif work_input.gemini_file_ref:
                # For media, we reuse the same uploaded file reference.
                content_input_refiner.append(work_input.gemini_file_ref)

            # --- Step 2: Execute Refinement ---
            status.write("Phase 2: Generating revised analysis...")

            # Execute the Refiner API call
            response_refiner = model.generate_content(content_input_refiner, request_options={"timeout": 900})
            status.update(label="Refinement complete!", state="complete")
            return response_refiner.text

        except Exception as e:
            st.error(f"An error occurred during refinement: {e}")
            logging.error(f"Refinement error: {e}")
            status.update(label="Refinement failed.", state="error")
            # Attempt to retrieve feedback if generation failed
            try:
                if hasattr(e, 'response'):
                    if hasattr(e.response, 'prompt_feedback') and e.response.prompt_feedback:
                            st.warning(f"Refinement blocked. Feedback: {e.response.prompt_feedback}")
            except Exception as inner_e:
                logging.warning(f"Could not retrieve detailed error feedback: {inner_e}")
            return None


# --- SYNTHESIS FUNCTIONS ---

def generate_dialectical_synthesis(model, data_a, analysis_a, data_b, analysis_b, work_title):
    # v9.4b: Updated to handle the new is_zeitgeist flag instead of checking lens name.
    """
    Synthesizes two analyses of the SAME work into a dialectical dialogue.
    """
    
    # data_a/b are dictionaries (lens_config structure)
    # Helper function to generate speaker instructions
    def get_speaker_instruction(data, perspective_id):
        lens_name = data.get('lens')
        persona_name = data.get('persona')
        is_zeitgeist = data.get('is_zeitgeist', False)
        
        # v9.4b: Handle Zeitgeist naming specifically using the flag
        if is_zeitgeist:
            # The AI must look at the generated analysis to find the specific persona name used (e.g., "The Witness from 1905")
            return f"* Perspective {perspective_id} (Zeitgeist Simulation) MUST be represented by the user-defined witness persona. Examine the corresponding analysis text to determine the exact title/name used."

        if persona_name:
            # User explicitly chose this persona
            return f"* Perspective {perspective_id} ('{lens_name}') MUST be represented by the specific historical figure: **{persona_name}**."
        else:
            # AI (General) chose the persona.
            return textwrap.dedent(f"""
            * Perspective {perspective_id} ('{lens_name}') was generated by an AI persona chosen specifically for this work (e.g., a specific proponent like 'Carl Jung' or a specific title like 'The Systems Analyst').
              You MUST identify and use that specific, intended persona name as the speaker title by examining the corresponding analysis text. Do NOT use a generic title derived only from the lens name.
            """)

    speaker_instruction_a = get_speaker_instruction(data_a, "A")
    speaker_instruction_b = get_speaker_instruction(data_b, "B")
    
    # v9.4b: Get lens names or "Zeitgeist" for display in the prompt context
    display_name_a = data_a.get('lens') or "Zeitgeist Simulation A"
    display_name_b = data_b.get('lens') or "Zeitgeist Simulation B"

    # The Synthesis Prompt
    synthesis_prompt = textwrap.dedent(f"""
    You are tasked with creating a "Dialectical Dialogue" regarding the creative work titled "{work_title}". This dialogue must synthesize two distinct analytical perspectives.

    Perspective A: {display_name_a}
    <analysis_a>
    {analysis_a}
    </analysis_a>

    Perspective B: {display_name_b}
    <analysis_b>
    {analysis_b}
    </analysis_b>

    Instructions:
    1. **Format as Dialogue:** Create a structured conversation.
    
    2. **Determine Speaker Personas (CRITICAL REQUIREMENT):**
    {textwrap.indent(speaker_instruction_a.strip(), '    ')}
    {textwrap.indent(speaker_instruction_b.strip(), '    ')}
    - The persona's name or title is explicitly stated in a markdown H3 header at the very beginning of each analysis text (e.g., '### Analysis by Jean-Paul Sartre'). You MUST use this header to identify the speakers.

    3. **Dialogue Flow and Structure (CRITICAL):**
        a. **Initial Statements:** The dialogue MUST begin with each participant presenting their core analysis sequentially, in the order their analyses are provided in this prompt. Do not deviate from this initial speaking order.
        b. **Open Discussion:** After all participants have made their initial statement, they may then engage in a more dynamic discussion. Ensure that all claims, arguments, and rebuttals are directly supported by the content of the provided analysis texts. While the dialogue should flow naturally, do not introduce new concepts or conclusions that cannot be traced back to the source analyses.

    4. **Aufheben / Synthesis:** After the dialogue, provide a concluding section titled "## Aufheben / Synthesis". This section must resolve the tensions (thesis and antithesis) and offer a higher-level interpretation (synthesis).

    Begin the dialogue immediately.
    """)

    try:
        response = model.generate_content(synthesis_prompt, request_options={"timeout": 600})
        return response.text
    except Exception as e:
        st.error(f"An error occurred during dialectical synthesis: {e}")
        return None

# v9.4b: Updated signature and implementation for Symposium.
def generate_symposium_synthesis(model, analyses_results, work_title):
    # v9.4b: Updated to handle the new is_zeitgeist flag and the structure of analyses_results.
    """
    Synthesizes multiple analyses (3+) into a multi-perspective symposium dialogue.
    """
    # analyses_results: List of (lens_config, analysis_text) tuples (to handle potential duplicate lenses/Zeitgeist entries)

    # Construct the input prompt
    prompt_parts = [textwrap.dedent(f"""
    You are tasked with creating a "Symposium Dialogue" regarding the creative work titled "{work_title}".
    This dialogue must synthesize multiple distinct analytical perspectives into a cohesive discussion.

    --- Provided Analyses ---
    """)]

    # Add the analyses
    # v9.4b: Iterate over the results list which contains tuples of (config, text)
    for idx, (config, analysis_text) in enumerate(analyses_results):
        display_name = config.get('lens') or "Zeitgeist Simulation"
        prompt_parts.append(f"<analysis id='{idx+1}' perspective='{display_name}'>\n{analysis_text}\n</analysis>\n")

    # Generate speaker instructions
    speaker_instructions_parts = []

    # v9.4b: Iterate over the successful results (which are tuples)
    for idx, (config, _) in enumerate(analyses_results):
        lens_name = config.get('lens')
        persona_name = config.get('persona')
        is_zeitgeist = config.get('is_zeitgeist', False)
        
        # v9.4b: Handle Zeitgeist naming specifically using the flag
        if is_zeitgeist:
            instruction = f"* Analysis {idx+1} (Zeitgeist Simulation) MUST be represented by the user-defined witness persona. Examine the corresponding analysis text to determine the exact title/name used."
        elif persona_name:
            # User explicitly chose this persona
            instruction = f"* Analysis {idx+1} ('{lens_name}') MUST be represented by the specific historical figure: **{persona_name}**."
        else:
            # AI (General) chose the persona.
            instruction = textwrap.dedent(f"""
            * Analysis {idx+1} ('{lens_name}') was generated by an AI persona chosen specifically for this work (e.g., 'Carl Jung' or 'The Systems Analyst').
              You MUST identify and use that specific, intended persona name as the speaker title by examining the corresponding analysis text. Do NOT use a generic title derived only from the lens name.
            """)
        speaker_instructions_parts.append(instruction.strip())

    speaker_instructions = "\n".join(speaker_instructions_parts)


    # Add the instructions
    prompt_parts.append(textwrap.dedent(f"""
    --- Instructions ---
    1. **Format as Dialogue:** Create a structured conversation between the perspectives.
    
    2. **Determine Speaker Personas (CRITICAL REQUIREMENT):**
    {textwrap.indent(speaker_instructions, '    ')}
    - The persona's name or title is explicitly stated in a markdown H3 header at the very beginning of each analysis text (e.g., '### Analysis by Jean-Paul Sartre'). You MUST use this header to identify the speakers.

    3. **Formatting:** All speaker names MUST be formatted in markdown bold (e.g., **Ayn Rand:** or **The Witness from 1905:**).
    
    4. **Dialogue Flow and Structure (CRITICAL):**
        a. **Initial Statements:** The dialogue MUST begin with each participant presenting their core analysis sequentially, in the order their analyses are provided in this prompt. Do not deviate from this initial speaking order.
        b. **Open Discussion:** After all participants have made their initial statement, they may then engage in a more dynamic discussion. Ensure that all claims, arguments, and rebuttals are directly supported by the content of the provided analysis texts. While the dialogue should flow naturally, do not introduce new concepts or conclusions that cannot be traced back to the source analyses.

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


def generate_comparative_synthesis(model, lens_config, analysis_a, work_a_title, analysis_b, work_b_title):
    # v9.4b: Updated to accept lens_config instead of just lens_name.
    """Synthesizes two analyses of DIFFERENT works using the SAME lens/configuration."""

    # v9.4b: Determine the display name for the comparison
    if lens_config.get('is_zeitgeist', False):
        comparison_framework = "Zeitgeist Simulation (Common Context)"
    else:
        # Display the UI name here for the user's context
        comparison_framework = lens_config.get('lens')

    # The Comparative Synthesis Prompt
    synthesis_prompt = textwrap.dedent(f"""
    You are tasked with generating a "Comparative Synthesis". You will compare and contrast two different creative works analyzed through the same analytical framework: **{comparison_framework}**.

    Work A Title: {work_a_title}
    <analysis_a>
    {analysis_a}
    </analysis_a>

    Work B Title: {work_b_title}
    <analysis_b>
    {analysis_b}
    </analysis_b>

    Instructions:
    1. **Identify Key Themes:** Based on the provided analyses, identify the central themes, findings, or arguments that emerged for each work under the {comparison_framework} framework.
    2. **Dissonance and Resonance:** Analyze the points of contrast (dissonance) and similarity (resonance) between Work A and Work B. How does applying the same framework reveal different aspects of each work?
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

def run_async_tasks(tasks):
    """Runs a list of asyncio tasks and returns the results."""
    # This is a simple way to run asyncio code from a synchronous Streamlit app
    async def run_all():
        return await asyncio.gather(*tasks)
    
    # Check if an event loop is already running
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(run_all())

def handle_input_ui(work_input: WorkInput, container, ui_key_prefix, on_change_callback=None):
    # (Implementation remains the same as v9.4a)
    """
    Renders input fields based on modality. Modifies the WorkInput object in place.
    """
    with container:
        work_input.title = st.text_input("Title (Optional):", key=f"{ui_key_prefix}_title", value=work_input.title, on_change=on_change_callback)
        
        # Handle modality switching robustly
        current_modality = work_input.modality
        try:
            current_index = MODALITIES.index(current_modality)
        except ValueError:
            current_index = 0

        new_modality = st.selectbox("Modality:", MODALITIES, index=current_index, key=f"{ui_key_prefix}_modality", on_change=on_change_callback)
        
        # If the modality changes, clear previous data/files
        if new_modality != current_modality:
            work_input.modality = new_modality
            work_input.data = None
            work_input.uploaded_file_obj = None
            # We must rerun to update the input widgets correctly
            st.rerun()

        if work_input.modality == M_TEXT:
            work_text = st.text_area("Paste text or description:", height=250, key=f"{ui_key_prefix}_text", value=work_input.data or "", on_change=on_change_callback)
            if work_text:
                work_input.data = work_text

        elif work_input.modality == M_IMAGE:
            uploaded_file = st.file_uploader("Upload Image (JPG, PNG, WEBP, HEIC, HEIF):", type=["jpg", "jpeg", "png", "webp", "heic", "heif"], key=f"{ui_key_prefix}_image", on_change=on_change_callback)
            if uploaded_file is not None:
                # Check if the newly uploaded file is different from the previous one
                if work_input.uploaded_file_obj != uploaded_file:
                    work_input.uploaded_file_obj = uploaded_file
                    # If the file changed, we must clear the old Gemini reference
                    work_input.gemini_file_ref = None 
                
                try:
                    # Display the image preview
                    st.image(uploaded_file, caption="Preview", use_container_width=True)
                except Exception as e:
                    st.error(f"Error processing image: {e}")
                    work_input.uploaded_file_obj = None

        elif work_input.modality == M_AUDIO:
            uploaded_file = st.file_uploader("Upload Audio (MP3, WAV, FLAC, M4A, OGG, MP4 audio):", type=["mp3", "wav", "flac", "m4a", "ogg", "mp4"], key=f"{ui_key_prefix}_audio", on_change=on_change_callback)
            if uploaded_file is not None:
                # Check if the newly uploaded file is different
                if work_input.uploaded_file_obj != uploaded_file:
                    work_input.uploaded_file_obj = uploaded_file
                    # Clear the old Gemini reference
                    work_input.gemini_file_ref = None

                # Display audio player
                st.audio(uploaded_file)

        elif work_input.modality == M_VIDEO:
            uploaded_file = st.file_uploader("Upload Video (MP4, MOV, AVI, WEBM):", type=["mp4", "mov", "avi", "webm"], key=f"{ui_key_prefix}_video", on_change=on_change_callback)
            if uploaded_file is not None:
                # Check if the newly uploaded file is different
                if work_input.uploaded_file_obj != uploaded_file:
                    work_input.uploaded_file_obj = uploaded_file
                    # Clear the old Gemini reference
                    work_input.gemini_file_ref = None
                
                # Display video player
                st.video(uploaded_file)

                # --- Pre-Processing UI (Cost Management) ---
                st.markdown("#### Video Processing Options (Cost Management)")
                
                try:
                    current_vmode_index = VIDEO_MODES.index(work_input.video_mode)
                except ValueError:
                    current_vmode_index = 0

                selected_mode = st.radio(
                    "Select Analysis Scope:",
                    VIDEO_MODES,
                    index=current_vmode_index,
                    key=f"{ui_key_prefix}_vmode",
                    help="Selecting a narrower scope focuses the AI's attention and significantly reduces processing time and API cost.",
                    on_change=on_change_callback
                )
                work_input.video_mode = selected_mode

                if selected_mode == V_MODE_FULL:
                    st.warning("⚠️ Warning: Full video analysis can be time-consuming and incur higher API costs for long videos.")
                
                elif selected_mode == V_MODE_KEYFRAMES:
                    interval = st.slider(
                        "Analysis Interval (Seconds):",
                        min_value=1,
                        max_value=60,
                        value=work_input.keyframe_interval,
                        step=1,
                        key=f"{ui_key_prefix}_vinterval",
                        help="The AI will focus its visual analysis on moments spaced at this interval, combined with the audio transcript.",
                        on_change=on_change_callback
                    )
                    work_input.keyframe_interval = interval
                elif selected_mode == V_MODE_TRANSCRIPT:
                    st.success("✅ Transcript-only analysis is the fastest and cheapest option. Visuals will be ignored.")

# v9.4b: Updated return signature (LENS_ZEITGEIST removed)
def render_view_toggle_and_help(selection_key_prefix=""):
    """
    Renders the standardized Library/Workshop/Timeline toggle and help system in the main area.
    Returns the current hierarchy and appropriate labels.
    """
    # Layout for Toggle and Help Icon
    col_view, col_help = st.columns([5, 1])

    with col_view:
        # Implement the "View As" Toggle
        view_mode = st.radio(
            "View Lenses As:",
            (VIEW_LIBRARY, VIEW_WORKSHOP, VIEW_ERA),
            index=0,
            horizontal=True,
            help=f"Switch views. Click the ❓ icon for details on the organizational structures.",
            key=f"{selection_key_prefix}_view_mode"
        )

    with col_help:
        # This HTML/CSS centers the button vertically relative to the radio group label
        st.markdown(
            """<style>
            .help-button-container {
                display: flex;
                align-items: center;
                height: 2.5rem; /* Approximate height of the radio label */
            }
            </style>""", unsafe_allow_html=True
        )
        
        # On Click detailed explanation (Progressive Disclosure)
        with st.container():
            st.markdown('<div class="help-button-container">', unsafe_allow_html=True)
            with st.popover("❓ Help"):
                st.markdown("#### 🏛️ Organizational Structures")
                st.markdown(f"**{VIEW_LIBRARY}:** Organized by academic discipline. Best for finding known frameworks.")
                st.markdown(f"**{VIEW_WORKSHOP}:** Organized by function (The Three Tiers of Inquiry). Best for designing holistic strategies.")
                st.markdown(f"**{VIEW_ERA}:** Organized chronologically by historical period. Best for tracing intellectual history.")

                
                st.markdown("---")
                st.markdown("##### The Three Tiers of Inquiry (Workshop)")
                st.markdown(
                    """
                    * **1. Contextual (What/Who/When):** Establishes background and facts.
                    * **2. Mechanical (How):** Analyzes structure, form, and function.
                    * **3. Interpretive (Why):** Explores deeper meaning and implications.
                    """
                )
                # v9.4b: Update help for Zeitgeist Mode
                st.markdown("---")
                st.markdown("##### 🕰️ Zeitgeist Simulation Mode")
                st.markdown(
                    f"""
                    The **Zeitgeist Simulation** toggle allows you to bypass standard lens selection (or supplement it in Symposium mode) and define a custom historical context and witness persona. The AI will simulate how that witness, in that context, would analyze the work.
                    """
                )

            st.markdown('</div>', unsafe_allow_html=True)


    # Determine which hierarchy and labels to use based on the view mode
    if view_mode == VIEW_LIBRARY:
        current_hierarchy = LENSES_HIERARCHY
        labels = {
            "category_label_single": "1. Discipline Category:",
            "category_label_multi": "1. Select Discipline Categories:",
            "placeholder_text_single": "Select a category...",
            "placeholder_text_multi": "Select categories..."
        }
    elif view_mode == VIEW_WORKSHOP:
        current_hierarchy = LENSES_FUNCTIONAL
        labels = {
            "category_label_single": "1. Functional Tier:",
            "category_label_multi": "1. Select Functional Tiers:",
            "placeholder_text_single": "Select a functional tier...",
            "placeholder_text_multi": "Select tiers..."
        }
    else: # VIEW_ERA
        current_hierarchy = LENSES_BY_ERA
        labels = {
            "category_label_single": "1. Historical Era:",
            "category_label_multi": "1. Select Historical Eras:",
            "placeholder_text_single": "Select an era...",
            "placeholder_text_multi": "Select eras..."
        }
    
    # v9.4b: Return updated signature
    return current_hierarchy, labels

def get_lens_tooltip(lens_name):
    """Retrieves the description for a lens to be used as a tooltip."""
    if lens_name:
        data = get_lens_data(lens_name)
        if data and data.get("description"):
            return data["description"]
    return None

def render_persona_selector(lens_keyword, key_prefix):
    # (Implementation remains the same as v9.4a)
    """
    Renders the optional persona selector if a pool exists for the lens.
    Returns the selected persona name or None.
    """
    if lens_keyword and lens_keyword in PERSONA_POOL:
        # Ensure the pool is sorted for consistent UI
        pool = sorted(PERSONA_POOL[lens_keyword])
        # Add a "Let AI Decide" option at the beginning
        options = ["(Let AI Decide)"] + pool
        
        # Customize label based on context
        label = f"Specify Persona (Optional):"
        if "symposium" in key_prefix or "dialectic" in key_prefix:
            label = f"Persona for {lens_keyword} (Optional):"

        selected_persona = st.selectbox(
            label,
            options=options,
            index=0,
            key=f"{key_prefix}_persona_selector",
            help="Select a specific historical figure or central entity to conduct the analysis, or let the AI choose the most appropriate one from the pool."
        )
        # Return the name only if a specific person is selected
        if selected_persona == "(Let AI Decide)":
            return None
        return selected_persona
    return None


def initialize_page_config(title):
    # (Implementation remains the same as v9.4a)
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
    # (Implementation remains the same as v9.4a)
    """Renders the global settings in the sidebar."""
    # Initialize session state for API key if not present
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""

    with st.sidebar:
        st.header("🏛️ Janus Settings")

        # Check if an API key is currently present in the session state.
        api_key_present = bool(st.session_state.get("api_key"))

        # 1. Settings
        # The expander is now only expanded if the key is NOT present.
        with st.expander("🔑 API Configuration", expanded=not api_key_present):
            api_key_input = st.text_input("Enter your Gemini API Key", type="password", value=st.session_state.api_key)
            if api_key_input != st.session_state.api_key:
                st.session_state.api_key = api_key_input
                # Rerun to ensure the key is available immediately
                st.rerun()
            st.caption("API key is required to execute the engine.")
