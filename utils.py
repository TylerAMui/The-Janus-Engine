import streamlit as st
from google import genai
from google.api_core import exceptions as google_exceptions
import textwrap
import mimetypes
import time
import logging
import json
import asyncio
import random
import functools
from pydantic import BaseModel, Field
# v10.0: Updated imports (Removed PERSONA_STYLE_GUIDES as it's deprecated)
from lenses import SORTED_LENS_NAMES, LENSES_HIERARCHY, LENSES_FUNCTIONAL, LENSES_BY_ERA, PERSONA_POOL, get_lens_data

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# --- RETRY UTILITY ---

def retry_with_backoff(max_retries=3, base_delay=2, max_delay=60, exponential_base=2):
    """
    Decorator for retrying functions with exponential backoff and jitter.

    Handles transient API failures including:
    - ResourceExhausted (429 rate limit)
    - ServiceUnavailable (503)
    - DeadlineExceeded (timeout)
    - InternalServerError (500)

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 2)
        max_delay: Maximum delay in seconds (default: 60)
        exponential_base: Base for exponential calculation (default: 2)
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (
                    google_exceptions.ResourceExhausted,
                    google_exceptions.ServiceUnavailable,
                    google_exceptions.DeadlineExceeded,
                    google_exceptions.InternalServerError
                ) as e:
                    last_exception = e

                    # Don't retry on the last attempt
                    if attempt >= max_retries:
                        break

                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.1)  # Add 0-10% jitter
                    total_delay = delay + jitter

                    # Determine error type for user message
                    if isinstance(e, google_exceptions.ResourceExhausted):
                        error_type = "Rate limit reached"
                    elif isinstance(e, google_exceptions.ServiceUnavailable):
                        error_type = "Service temporarily unavailable"
                    elif isinstance(e, google_exceptions.DeadlineExceeded):
                        error_type = "Request timeout"
                    else:
                        error_type = "API error"

                    # Show retry notification to user
                    retry_msg = f"⏱️ {error_type}. Retrying in {int(total_delay)}s... (Attempt {attempt + 2}/{max_retries + 1})"
                    logging.warning(f"{func.__name__}: {retry_msg}")
                    st.info(retry_msg)

                    # Wait before retrying
                    await asyncio.sleep(total_delay)

            # All retries exhausted
            if last_exception:
                raise last_exception

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (
                    google_exceptions.ResourceExhausted,
                    google_exceptions.ServiceUnavailable,
                    google_exceptions.DeadlineExceeded,
                    google_exceptions.InternalServerError
                ) as e:
                    last_exception = e

                    # Don't retry on the last attempt
                    if attempt >= max_retries:
                        break

                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.1)  # Add 0-10% jitter
                    total_delay = delay + jitter

                    # Determine error type for user message
                    if isinstance(e, google_exceptions.ResourceExhausted):
                        error_type = "Rate limit reached"
                    elif isinstance(e, google_exceptions.ServiceUnavailable):
                        error_type = "Service temporarily unavailable"
                    elif isinstance(e, google_exceptions.DeadlineExceeded):
                        error_type = "Request timeout"
                    else:
                        error_type = "API error"

                    # Show retry notification to user
                    retry_msg = f"⏱️ {error_type}. Retrying in {int(total_delay)}s... (Attempt {attempt + 2}/{max_retries + 1})"
                    logging.warning(f"{func.__name__}: {retry_msg}")
                    st.info(retry_msg)

                    # Wait before retrying
                    time.sleep(total_delay)

            # All retries exhausted
            if last_exception:
                raise last_exception

        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# --- CONSTANTS & DIRECTIVES ---

# Janus Persona Directives (Used by Adaptive Agents)
# v10.0: Updated directive
JANUS_DIRECTIVES = """
You are Janus (v10.0), an engine of abstraction and interpretation operating within a generative and adaptive architecture. Your primary goal is to generate profound, bespoke insight by dynamically formulating and executing analytical strategies tailored to the specific work and the chosen framework.
"""

# v10.0: Model Constants
MODEL_PRO = "models/gemini-2.5-pro"
# v10.0: Using Flash-Lite as requested
MODEL_FLASH = "models/gemini-2.5-flash-lite" 

# v10.0: Constants for Analysis Modes
MODE_ADAPTIVE = "Adaptive Analysis"
MODE_SURFACE_SCRAPE = "Surface Scrape"
MODE_DEEP_DIVE = "Deep Dive"
ANALYSIS_MODES = (MODE_ADAPTIVE, MODE_SURFACE_SCRAPE, MODE_DEEP_DIVE)

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

# --- TOOLTIP DEFINITIONS ---
# v10.2: Centralized glossary for UI tooltips

TOOLTIPS = {
    # Architecture / Pipeline
    "triage": "Fast AI assessment of work complexity. Determines optimal analysis strategy (Flash-Lite for simple works, Pro for complex works).",
    "theoretician": "AI agent that analyzes your work and dynamically generates the most relevant analytical concepts for the chosen lens/framework.",
    "specialist_swarm": "Parallel AI instances that perform deep analysis on each generated concept simultaneously for efficiency.",
    "synthesizer": "Final AI agent that integrates all specialist reports into a coherent, holistic analysis.",
    "adaptive_architecture": "Four-stage pipeline (Triage → Theoretician → Specialist Swarm → Synthesizer) that generates custom analytical strategies for each work.",

    # Analysis Modes
    "adaptive_analysis": "Balances quality and cost. Uses Triage to assess complexity, then applies Flash-Lite for simple works or Pro for complex works. Recommended for most users.",
    "surface_scrape": "Fastest and most cost-effective option. Uses Flash-Lite for all stages. Good for quick explorations or simple works.",
    "deep_dive": "Highest quality and most thorough analysis. Uses Gemini 2.5 Pro for all stages. Best for academic research or complex works. Higher token cost.",

    # Core Concepts
    "lens": "A theoretical framework or critical perspective (e.g., Marxism, Feminism, Formalism) used to analyze creative works from a specific angle.",
    "persona_pool": "Collection of historical figures who can embody a framework. AI selects contextually appropriate voice, or you can manually choose a specific person.",
    "zeitgeist": "AI simulates the cultural/intellectual climate of a specific historical period for era-specific analysis without predefined theory.",
    "refinement_loop": "Ask follow-up questions after initial analysis. AI retains context from the original analysis for iterative refinement and deeper exploration.",
    "smart_selection": "AI automatically chooses the most potent lens(es) for your work by analyzing its themes, structure, and content.",

    # Lens Organization
    "discipline": "Academic domain classification (e.g., Philosophy, Literary Theory, Art History). Many lenses belong to multiple disciplines for contextual flexibility.",
    "function_tier": "Three-tier analytical framework: (1) Contextual = What it is, (2) Mechanical = How it works, (3) Interpretive = Why it matters.",
    "function_tier_contextual": "Tier 1: What it is — Descriptive, taxonomic lenses that establish facts, background, and context (What/Who/When).",
    "function_tier_mechanical": "Tier 2: How it works — Lenses analyzing structure, form, technique, and function (How).",
    "function_tier_interpretive": "Tier 3: Why it matters — Evaluative lenses exploring deeper meaning, significance, and implications (Why).",
    "era_filter": "Historical period when the lens/framework emerged or was most prominent. Helps contextualize theoretical perspectives.",
    "toolkit_lens": "Lenses with sub-primers for specialized analysis within broader frameworks (e.g., Psychoanalytic Theory has Freudian, Jungian, and Lacanian sub-primers).",

    # Technical / Performance
    "context_caching": "Stores uploaded file on Gemini's servers temporarily for faster multi-lens analysis. Significantly reduces costs and latency for Symposium/Dialectical modes with 3+ lenses.",
    "rigor_level": "Complexity assessment from Triage. Determines which model (Flash-Lite or Pro) is used for analysis stages in Adaptive mode.",

    # UI Elements
    "execute_analysis": "Begins the multi-stage analysis pipeline. Uploads media (if needed), runs Triage (if Adaptive mode), generates strategy, and synthesizes results.",
    "export_analysis": "Downloads complete analysis with metadata (timestamp, configuration, API usage) in Markdown (.md) or Plain Text (.txt) format.",
}

def get_tooltip(key: str) -> str:
    """
    Retrieve tooltip text by key from centralized glossary.

    Args:
        key: The tooltip identifier

    Returns:
        Tooltip text string, or empty string if key not found
    """
    return TOOLTIPS.get(key, "")

# --- PYDANTIC RESPONSE SCHEMAS ---
# v10.2: Structured output schemas for better type safety and automatic parsing

class LensSelectionResponse(BaseModel):
    """Response schema for analyst_in_chief smart lens selection."""
    selected_lenses: list[str] = Field(description="List of selected lens names")
    justification: str = Field(description="Rationale for selecting these lenses")

class SingleLensSelectionResponse(BaseModel):
    """Response schema for comparative_strategist single lens selection."""
    selected_lens: str = Field(description="The selected lens name")
    justification: str = Field(description="Rationale for selecting this lens")

class TriageResponse(BaseModel):
    """Response schema for complexity triage analysis."""
    complexity_classification: str = Field(description="Either 'Simple' or 'Complex'")
    justification: str = Field(description="Brief explanation of the classification")

class AdaptiveTheoryResponse(BaseModel):
    """Response schema for adaptive theoretician strategy generation."""
    analytical_tasks: list[str] = Field(description="List of analytical tasks/concepts to explore")
    persona_instruction: str = Field(description="Persona directive for the analysis")

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
        # File metadata for tracking uploads (persists even after uploaded_file_obj is freed)
        self.uploaded_file_name = None
        self.uploaded_file_size = None
        # v10.2: Context caching support for multi-lens analysis
        self.cache_ref = None  # Stores the CachedContent object
        self.cache_enabled = False  # Flag to enable/disable caching
        self.cache_creation_mode = None  # Stores the analysis mode used to create the cache
        # v10.2: API usage metadata tracking
        self.metadata = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "cached_content_tokens": 0,
            "api_calls": 0
        }
        # Video processing options
        self.video_mode = V_MODE_FULL
        self.keyframe_interval = 10 # Default interval in seconds

    def is_ready(self):
        if self.modality == M_TEXT:
            return self.data is not None and len(self.data) > 0
        else:
            # Media is ready if we have a file object OR if we have uploaded file metadata
            # Using uploaded_file_name instead of gemini_file_ref prevents stale reference bugs
            return self.uploaded_file_obj is not None or self.uploaded_file_name is not None

    def get_display_title(self):
        return self.title if self.title else "(Untitled)"

    def cleanup_gemini_file(self):
        # v10.1: Migrated to google-genai SDK
        # v10.2: Also cleanup context cache if present
        """Cleans up the associated Gemini file and cache if they exist."""
        api_key = st.session_state.get("api_key")

        # Always clear local references, even if deletion fails
        cache_ref_to_delete = self.cache_ref
        file_ref_to_delete = self.gemini_file_ref

        # Clear local references immediately to prevent stale reference bugs
        self.cache_ref = None
        self.cache_creation_mode = None
        self.gemini_file_ref = None
        self.uploaded_file_name = None
        self.uploaded_file_size = None

        # If we have API access, try to delete from Gemini's servers
        if not api_key:
            logging.warning("API key missing - cleared local references but couldn't delete from Gemini servers")
            return

        client = get_client(api_key)
        if not client:
            logging.warning("Client initialization failed - cleared local references but couldn't delete from Gemini servers")
            return

        # Try to delete cache
        if cache_ref_to_delete:
            try:
                client.caches.delete(name=cache_ref_to_delete.name)
                logging.info(f"Cleaned up context cache: {cache_ref_to_delete.name}")
            except Exception as e:
                logging.error(f"Failed to delete context cache (local ref already cleared): {e}")

        # Try to delete file
        if file_ref_to_delete:
            try:
                client.files.delete(name=file_ref_to_delete.name)
                logging.info(f"Cleaned up Gemini file: {file_ref_to_delete.name}")
            except Exception as e:
                logging.error(f"Failed to delete Gemini file (local ref already cleared): {e}")

# --- GEMINI FUNCTIONS ---

# v10.1: Migrated to google-genai SDK - Returns client instead of model
def get_client(api_key):
    """Creates and returns a Gemini API client with extended timeout."""
    if not api_key:
        return None
    try:
        from google.genai import types
        # Set timeout to 15 minutes (900 seconds = 900000 milliseconds)
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=900_000)
        )
        return client
    except Exception as e:
        st.error(f"Failed to initialize Gemini API client. Please ensure your API Key is correct and has access. Error: {e}")
        return None

# Backwards compatibility wrapper
def get_model(api_key, model_name=MODEL_PRO, json_mode=False):
    """Legacy function - now returns client. Model name and json_mode are handled per-call in new SDK."""
    # Note: model_name and json_mode are now passed to generate_content() instead
    return get_client(api_key)

@retry_with_backoff(max_retries=3, base_delay=2)
def upload_to_gemini(work_input: WorkInput):
    # v10.1: Migrated to google-genai SDK
    # v10.2: Added retry logic with exponential backoff
    """
    Handles uploading media files (Image/Audio/Video) to the Gemini API.
    Utilizes caching within the WorkInput object.
    """
    # Check if already uploaded
    if work_input.gemini_file_ref:
        # File already uploaded, skip re-upload
        return work_input.gemini_file_ref

    if not work_input.uploaded_file_obj:
        logging.warning("Attempted to upload media when no file object was available.")
        return None

    # Get API client
    api_key = st.session_state.get("api_key")
    client = get_client(api_key)
    if not client:
        st.error("Failed to initialize API client.")
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

    # Pass Streamlit's UploadedFile directly (no temp storage, no memory copy)
    try:
        # 2. Prepare file for upload - Streamlit's UploadedFile is already seekable and binary
        work_input.uploaded_file_obj.seek(0)

        # 3. Upload directly to Gemini using UploadedFile (no BytesIO copy needed)
        uploaded_file = client.files.upload(
            file=work_input.uploaded_file_obj,
            config={'mime_type': mime_type}
        )

        # 4. Poll for Processing (happens on Gemini's servers, not in Streamlit RAM)
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
            uploaded_file = client.files.get(name=uploaded_file.name)
            current_state_name = get_state_name(uploaded_file)

        # 5. Final State Check
        if current_state_name == "FAILED":
            st.error("File processing failed. Please try again or use a different file.")
            return None

        if current_state_name == "ACTIVE":
            # Store the reference in the WorkInput object
            work_input.gemini_file_ref = uploaded_file

            # Free memory: File is now on Gemini's servers, we only need the reference
            work_input.uploaded_file_obj = None

            return uploaded_file

        st.error("File upload encountered an unexpected issue. Please try again.")
        return None

    # Catch specific Google API errors
    except google_exceptions.PermissionDenied:
        st.error("Permission Denied. Please ensure your API Key is valid and has access to the Gemini 2.5 Pro model.")
        return None
    except google_exceptions.ResourceExhausted:
        st.error("⏱️ **Rate Limit Reached** - You've made too many requests in a short time. Please wait 1-2 minutes and try again, or check your Google Cloud quota.")
        return None
    except TimeoutError:
        st.error("File upload timed out.")
        return None
    except Exception as e:
        st.error("An error occurred while uploading your file. Please try again.")
        with st.expander("🔍 Technical Details"):
            st.code(str(e))
        logging.error(f"File upload error: {e}")
        return None

@retry_with_backoff(max_retries=3, base_delay=2)
async def upload_to_gemini_async(work_input: WorkInput, status_container):
    # v10.1: Migrated to google-genai SDK with native async support
    # v10.2: Added retry logic with exponential backoff
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

    # Get API client
    api_key = st.session_state.get("api_key")
    client = get_client(api_key)
    if not client:
        st.error("Failed to initialize API client.")
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

    # Pass Streamlit's UploadedFile directly (no temp storage, no memory copy)
    try:
        # Prepare file for upload - Streamlit's UploadedFile is already seekable and binary
        work_input.uploaded_file_obj.seek(0)

        display_name = work_input.get_display_title()[:128]
        status_container.write(f"Uploading '{display_name}' to Gemini...")

        # Use native async API with UploadedFile directly (no BytesIO copy needed)
        uploaded_file = await client.aio.files.upload(
            file=work_input.uploaded_file_obj,
            config={'mime_type': mime_type}
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
            uploaded_file = await client.aio.files.get(name=uploaded_file.name)
            current_state_name = get_state_name(uploaded_file)
            status_container.write("Processing your file...")

        # 4. Final State Check
        if current_state_name == "FAILED":
            st.error("File processing failed. Please try again or use a different file.")
            return None

        if current_state_name == "ACTIVE":
            # Store the reference in the WorkInput object
            work_input.gemini_file_ref = uploaded_file

            # Free memory: File is now on Gemini's servers, we only need the reference
            work_input.uploaded_file_obj = None

            return uploaded_file

        st.error("File upload encountered an unexpected issue. Please try again.")
        return None

    except google_exceptions.PermissionDenied:
        st.error("Permission Denied. Please ensure your API Key is valid and has access to the Gemini 2.5 Pro model.")
        return None
    except google_exceptions.ResourceExhausted:
        st.error("⏱️ **Rate Limit Reached** - You've made too many requests in a short time. Please wait 1-2 minutes and try again, or check your Google Cloud quota.")
        return None
    except TimeoutError:
        st.error("File upload timed out.")
        return None
    except Exception as e:
        st.error("An error occurred while uploading your file. Please try again.")
        with st.expander("🔍 Technical Details"):
            st.code(str(e))
        logging.error(f"File upload error: {e}")
        return None

# v10.2: Context Caching for Multi-Lens Analysis
async def create_context_cache_async(client, work_input: WorkInput, model: str, status_container, ttl="3600s", analysis_mode=None):
    """
    Creates a context cache for a work input to optimize multi-lens analysis.

    Args:
        client: The Gemini API client
        work_input: The WorkInput object (must have gemini_file_ref set)
        model: The model name to use for caching (e.g., MODEL_PRO, MODEL_FLASH)
        status_container: Status display container
        ttl: Time-to-live for the cache (default: 1 hour)

    Returns:
        CachedContent object or None on failure
    """
    from google.genai import types

    # Only cache for media files (text doesn't benefit from caching due to low token count)
    if work_input.modality not in [M_IMAGE, M_AUDIO, M_VIDEO]:
        logging.info("Skipping cache creation for text modality (below minimum token threshold)")
        return None

    # Ensure file is uploaded first
    if not work_input.gemini_file_ref:
        logging.error("Cannot create cache without uploaded file reference")
        return None

    try:
        status_container.write("Creating context cache for efficient multi-lens analysis...")

        # Build cache content: base directives + modality instructions + file
        modality_instructions = get_modality_instructions(work_input)

        system_instruction = textwrap.dedent(f"""
        {JANUS_DIRECTIVES}

        **Modality Context:**
        {modality_instructions}

        **Note:** This cached context will be reused across multiple analytical lenses.
        Specific lens instructions and persona directives will be provided in each request.
        """)

        # Create the cache
        cache = await client.aio.caches.create(
            model=model,
            config=types.CreateCachedContentConfig(
                display_name=f"janus_analysis_{work_input.get_display_title()[:50]}",
                system_instruction=system_instruction,
                contents=[work_input.gemini_file_ref],
                ttl=ttl,
            )
        )

        # Store cache reference and creation mode in WorkInput
        work_input.cache_ref = cache
        work_input.cache_creation_mode = analysis_mode  # Track which mode was used to create cache
        status_container.write(f"Context cache created successfully (TTL: {ttl})")
        logging.info(f"Created context cache: {cache.name} for mode: {analysis_mode}")

        return cache

    except Exception as e:
        logging.error(f"Failed to create context cache: {e}")
        status_container.write(f"Cache creation failed (will proceed without caching): {e}")
        return None

def invalidate_cache_if_mode_changed(work_input: WorkInput, current_mode: str, api_key: str = None):
    """
    Invalidates the cache if the analysis mode has changed since cache creation.

    Args:
        work_input: The WorkInput object
        current_mode: The current analysis mode
        api_key: API key for cache deletion (optional)

    Returns:
        True if cache was invalidated, False otherwise
    """
    if work_input.cache_ref and work_input.cache_creation_mode:
        if work_input.cache_creation_mode != current_mode:
            logging.info(f"Cache invalidation: mode changed from {work_input.cache_creation_mode} to {current_mode}")
            work_input.clear(api_key)
            return True
    return False

# --- UTILITY FUNCTIONS ---

# v10.2: Backward compatibility helper
def ensure_metadata(work_input: WorkInput):
    """Ensures metadata dict exists on WorkInput (for backward compatibility with old session objects)."""
    if not hasattr(work_input, 'metadata'):
        work_input.metadata = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "cached_content_tokens": 0,
            "api_calls": 0
        }

# v10.2: Metadata tracking helper
def accumulate_metadata(work_input: WorkInput, response):
    """
    Extracts usage metadata from API response and accumulates it in WorkInput.

    Args:
        work_input: The WorkInput object to update
        response: The API response object with usage_metadata
    """
    # Ensure metadata exists (backward compatibility)
    ensure_metadata(work_input)

    try:
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            metadata = response.usage_metadata

            # Accumulate token counts - handle None values defensively
            input_tokens = getattr(metadata, 'prompt_token_count', None) or 0
            output_tokens = getattr(metadata, 'candidates_token_count', None) or 0
            cached_tokens = getattr(metadata, 'cached_content_token_count', None) or 0

            work_input.metadata["total_input_tokens"] += input_tokens
            work_input.metadata["total_output_tokens"] += output_tokens
            work_input.metadata["cached_content_tokens"] += cached_tokens
            work_input.metadata["api_calls"] += 1

            logging.info(f"✓ Accumulated metadata - API call #{work_input.metadata['api_calls']}: "
                        f"Input={input_tokens}, Output={output_tokens}, Cached={cached_tokens}, "
                        f"Running totals: {work_input.metadata}")
        else:
            logging.warning(f"✗ Response has no usage_metadata attribute or it's None")
    except Exception as e:
        logging.error(f"✗ Failed to extract metadata: {e}", exc_info=True)

def display_metadata(work_input: WorkInput, label="Analysis Complete"):
    """
    Displays API usage metadata in an expander for the given WorkInput.

    Args:
        work_input: The WorkInput object with accumulated metadata
        label: Optional label for the metadata section
    """
    # Ensure metadata exists (backward compatibility)
    ensure_metadata(work_input)
    metadata = work_input.metadata

    # Debug: Log the metadata state
    logging.info(f"display_metadata called for '{label}': {metadata}")

    # Show metadata if there's any token data, even if api_calls wasn't incremented
    has_data = (metadata["api_calls"] > 0 or
                metadata["total_input_tokens"] > 0 or
                metadata["total_output_tokens"] > 0)

    if not has_data:
        logging.info(f"Skipping metadata display for '{label}' - no data recorded")
        return  # No metadata to display

    with st.expander(f"📊 {label} - API Usage Metrics", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("API Calls", metadata["api_calls"])
            st.metric("Input Tokens", f"{metadata['total_input_tokens']:,}")

        with col2:
            st.metric("Output Tokens", f"{metadata['total_output_tokens']:,}")
            total_tokens = metadata['total_input_tokens'] + metadata['total_output_tokens']
            st.metric("Total Tokens", f"{total_tokens:,}")

        with col3:
            if metadata["cached_content_tokens"] > 0:
                st.metric("Cached Tokens", f"{metadata['cached_content_tokens']:,}",
                         delta="Cache Hit!", delta_color="normal")
                # Calculate savings (cached tokens would have been counted as input otherwise)
                savings_pct = (metadata["cached_content_tokens"] /
                              (metadata["total_input_tokens"] + metadata["cached_content_tokens"])) * 100
                st.metric("Cost Savings", f"{savings_pct:.1f}%",
                         delta="via context caching", delta_color="normal")
            else:
                st.metric("Cached Tokens", "0", delta="No cache used", delta_color="off")

# v10.2: Export utility function
def create_export_content(
    result_text: str,
    work_input: WorkInput,
    analysis_type: str,
    config_info: dict,
    work_input_b: WorkInput = None,
    format_type: str = "markdown"
):
    """
    Creates formatted export content for analysis results.

    Args:
        result_text: The analysis/synthesis text to export
        work_input: Primary WorkInput object (or Work A for comparative)
        analysis_type: "Single Lens", "Dialectical", "Symposium", or "Comparative"
        config_info: Dict with configuration details (lens, persona, mode, etc.)
        work_input_b: Optional second WorkInput for Comparative analysis
        format_type: "markdown" or "text"

    Returns:
        Formatted export string
    """
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get analysis mode from session state
    analysis_mode = st.session_state.get("analysis_mode", "Adaptive Analysis")

    # Gather metadata
    ensure_metadata(work_input)
    metadata = work_input.metadata
    total_tokens = metadata['total_input_tokens'] + metadata['total_output_tokens']

    # Build export content
    if format_type == "markdown":
        lines = [
            "---",
            "# Janus Engine Analysis Export",
            f"**Generated:** {timestamp}",
            f"**Analysis Mode:** {analysis_mode}",
            f"**Analysis Type:** {analysis_type}",
            "---",
            "",
            "## Configuration",
            ""
        ]

        # Add configuration details
        if config_info.get('is_zeitgeist'):
            lines.append("**Mode:** Zeitgeist Simulation")
            if config_info.get('zeitgeist_context'):
                lines.append(f"**Context:** {config_info['zeitgeist_context'][:100]}...")
            if config_info.get('zeitgeist_persona'):
                lines.append(f"**Persona:** {config_info['zeitgeist_persona'][:100]}...")
        else:
            lens = config_info.get('lens') or config_info.get('selection_method', 'Smart Selection')
            persona = config_info.get('persona', 'AI Decided')
            lines.append(f"**Lens:** {lens}")
            lines.append(f"**Persona:** {persona if persona and persona != '(No Persona)' else 'Generic Archetypal Title'}")

        # Add work information
        lines.append(f"**Work Title:** {work_input.get_display_title()}")
        lines.append(f"**Work Modality:** {work_input.modality}")

        # For Comparative, add Work B info
        if work_input_b:
            lines.append(f"**Work B Title:** {work_input_b.get_display_title()}")
            lines.append(f"**Work B Modality:** {work_input_b.modality}")

        lines.extend([
            "",
            "## API Usage Metrics",
            f"**API Calls:** {metadata['api_calls']}",
            f"**Input Tokens:** {metadata['total_input_tokens']:,}",
            f"**Output Tokens:** {metadata['total_output_tokens']:,}",
            f"**Total Tokens:** {total_tokens:,}",
            f"**Cached Tokens:** {metadata['cached_content_tokens']:,}"
        ])

        # For Comparative, add Work B metadata
        if work_input_b:
            ensure_metadata(work_input_b)
            metadata_b = work_input_b.metadata
            total_tokens_b = metadata_b['total_input_tokens'] + metadata_b['total_output_tokens']
            lines.extend([
                "",
                "### Work B API Usage",
                f"**API Calls:** {metadata_b['api_calls']}",
                f"**Input Tokens:** {metadata_b['total_input_tokens']:,}",
                f"**Output Tokens:** {metadata_b['total_output_tokens']:,}",
                f"**Total Tokens:** {total_tokens_b:,}",
                f"**Cached Tokens:** {metadata_b['cached_content_tokens']:,}"
            ])

        lines.extend([
            "",
            "---",
            "",
            "## Analysis Result",
            "",
            result_text,
            "",
            "---",
            "",
            f"*Generated by Janus Engine v10.0 • {timestamp}*"
        ])

        return "\n".join(lines)

    else:  # Plain text format
        lines = [
            "=" * 80,
            "JANUS ENGINE ANALYSIS EXPORT",
            "=" * 80,
            f"Generated: {timestamp}",
            f"Analysis Mode: {analysis_mode}",
            f"Analysis Type: {analysis_type}",
            "",
            "-" * 80,
            "CONFIGURATION",
            "-" * 80,
            ""
        ]

        # Add configuration details
        if config_info.get('is_zeitgeist'):
            lines.append("Mode: Zeitgeist Simulation")
            if config_info.get('zeitgeist_context'):
                lines.append(f"Context: {config_info['zeitgeist_context'][:100]}...")
            if config_info.get('zeitgeist_persona'):
                lines.append(f"Persona: {config_info['zeitgeist_persona'][:100]}...")
        else:
            lens = config_info.get('lens') or config_info.get('selection_method', 'Smart Selection')
            persona = config_info.get('persona', 'AI Decided')
            lines.append(f"Lens: {lens}")
            lines.append(f"Persona: {persona if persona and persona != '(No Persona)' else 'Generic Archetypal Title'}")

        # Add work information
        lines.append(f"Work Title: {work_input.get_display_title()}")
        lines.append(f"Work Modality: {work_input.modality}")

        # For Comparative, add Work B info
        if work_input_b:
            lines.append(f"Work B Title: {work_input_b.get_display_title()}")
            lines.append(f"Work B Modality: {work_input_b.modality}")

        lines.extend([
            "",
            "-" * 80,
            "API USAGE METRICS",
            "-" * 80,
            f"API Calls: {metadata['api_calls']}",
            f"Input Tokens: {metadata['total_input_tokens']:,}",
            f"Output Tokens: {metadata['total_output_tokens']:,}",
            f"Total Tokens: {total_tokens:,}",
            f"Cached Tokens: {metadata['cached_content_tokens']:,}"
        ])

        # For Comparative, add Work B metadata
        if work_input_b:
            ensure_metadata(work_input_b)
            metadata_b = work_input_b.metadata
            total_tokens_b = metadata_b['total_input_tokens'] + metadata_b['total_output_tokens']
            lines.extend([
                "",
                "Work B API Usage:",
                f"API Calls: {metadata_b['api_calls']}",
                f"Input Tokens: {metadata_b['total_input_tokens']:,}",
                f"Output Tokens: {metadata_b['total_output_tokens']:,}",
                f"Total Tokens: {total_tokens_b:,}",
                f"Cached Tokens: {metadata_b['cached_content_tokens']:,}"
            ])

        lines.extend([
            "",
            "=" * 80,
            "ANALYSIS RESULT",
            "=" * 80,
            "",
            result_text,
            "",
            "=" * 80,
            f"Generated by Janus Engine v10.0 • {timestamp}",
            "=" * 80
        ])

        return "\n".join(lines)

# (v10.0: New Helper Function)
def get_modality_instructions(work_input: WorkInput):
    """Extracts modality-specific analysis instructions."""
    work_modality = work_input.modality
    if work_modality == M_IMAGE:
        return "The work is an image. The analysis MUST first provide a detailed visual description (composition, color, texture, subject) before applying the lens, focusing strictly on visual evidence."
    elif work_modality == M_AUDIO:
        return "The work is audio. The analysis MUST first provide a detailed sonic description (instrumentation, tone, tempo, lyrics, structure) before applying the lens, focusing strictly on audible evidence."
    elif work_modality == M_TEXT:
        return "The work is text. The analysis should focus on close reading, literary devices, structure, rhetoric, and theme."
    elif work_modality == M_VIDEO:
        # v10.0.29: Add instruction for pre-formatted text to handle special characters correctly.
        # This is a placeholder as video has its own detailed instructions.
        video_mode = work_input.video_mode
        if video_mode == V_MODE_FULL:
            return """
            The work is a video (Full Analysis requested). The analysis MUST be comprehensive, considering visual composition, audio track (transcript), narrative progression, editing, and timing. The analysis must utilize specific timestamps to reference evidence.
            """
        elif video_mode == V_MODE_KEYFRAMES:
            interval = work_input.keyframe_interval
            return f"""
            The work is a video (Keyframe Analysis requested). The analysis MUST analyze both the audio track (transcript) AND key visual moments occurring approximately every {interval} seconds. 
            The analysis should synthesize these visual moments with the audio to understand the overall work, utilizing timestamps for reference. Do not analyze every frame; use the interval as the primary guide for visual attention.
            """
        elif video_mode == V_MODE_TRANSCRIPT:
            return """
            The work is a video (Transcript-Only Analysis requested). The analysis MUST explicitly ignore all visual information and analyze ONLY the audio transcript (dialogue, narration). 
            The analysis should treat the input as a purely textual work derived from the audio track.
            """
    return ""

# --- SMART SELECTION (Analyst-in-Chief) ---

@retry_with_backoff(max_retries=3, base_delay=2)
def analyst_in_chief(client, work_input: WorkInput, required_count: int, status_container):
    # v10.1: Migrated to google-genai SDK - now accepts client instead of model
    # v9.4b: Updated prompt to remove the constraint about Zeitgeist, as it's no longer a lens.
    # v10.2: Added retry logic with exponential backoff
    """
    The "Analyst-in-Chief" meta-call. Selects the most potent lenses.
    Uses JSON mode via response_mime_type config.
    """
    status_container.write("Phase 0: Consulting the Analyst-in-Chief (Smart Selection)...")

    # Prepare the input package
    content_input = []
    
    # 1. Handle Media Upload if necessary (and utilize cache)
    if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
        # This function handles upload/caching and stores the reference
        gemini_file = upload_to_gemini(work_input)
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

    # 3. Execute the API call with Pydantic schema
    try:
        # v10.2: Use Pydantic schema for automatic validation and parsing
        response = client.models.generate_content(
            model=MODEL_FLASH,  # Using flash for smart selection
            contents=content_input,
            config={
                "response_mime_type": "application/json",
                "response_schema": LensSelectionResponse
            }
        )

        # v10.2: Accumulate metadata for Smart Selection
        accumulate_metadata(work_input, response)

        # Access validated parsed response
        if not response.parsed:
            # v10.2: Fallback to manual JSON parsing if automatic parsing fails
            logging.warning(f"Automatic parsing failed, attempting manual parse. Response text: {response.text}")
            try:
                # Try to parse the JSON manually
                json_text = response.text
                # Sometimes the response is wrapped in ```json ... ```
                if json_text.strip().startswith("```json"):
                    json_text = json_text.strip().split("```json")[1].split("```")[0].strip()
                elif json_text.strip().startswith("```"):
                    json_text = json_text.strip().split("```")[1].split("```")[0].strip()

                parsed_data = json.loads(json_text)
                selected_lenses = parsed_data.get("selected_lenses", [])
                justification = parsed_data.get("justification", "")
            except Exception as e:
                st.error("Failed to parse AI response. Please try again or use manual selection.")
                logging.error(f"Empty parsed response and manual parse failed: {response.text}. Error: {e}")
                return None
        else:
            result = response.parsed
            selected_lenses = result.selected_lenses
            justification = result.justification

        if not selected_lenses or len(selected_lenses) != required_count:
            st.error(f"AI did not select the required number of lenses ({required_count}). Please use manual selection.")
            logging.error(f"Invalid lens count: {len(selected_lenses)}. Selected: {selected_lenses}")
            return None

        # Ensure selected lenses exist in the master list
        for lens in selected_lenses:
            if lens not in SORTED_LENS_NAMES:
                    st.error(f"AI selected an unknown lens: '{lens}'. Please use manual selection.")
                    logging.error(f"Unknown lens selected: {lens}. Selected: {selected_lenses}")
                    return None

        status_container.write("Lenses selected by Analyst-in-Chief.")
        # Display results in the main area for visibility
        st.success(f"**Janus Smart Selection:** {', '.join(selected_lenses)}")
        with st.expander("View Justification"):
            st.write(justification)
            
        return selected_lenses

    except google_exceptions.ResourceExhausted:
        st.error("⏱️ **Rate Limit Reached** - You've made too many requests in a short time. Please wait 1-2 minutes and try again, or check your Google Cloud quota.")
        logging.error("Smart Selection failed: ResourceExhausted")
        return None
    except Exception as e:
        st.error(f"An error occurred during Smart Selection: {e}. Please try again or use manual selection.")
        logging.error(f"Smart Selection error: {e}")
        return None

# v10.0.5: New function for Comparative Smart Selection
@retry_with_backoff(max_retries=3, base_delay=2)
def comparative_strategist(client, work_a: WorkInput, work_b: WorkInput, status_container):
    # v10.1: Migrated to google-genai SDK - now accepts client instead of model
    # v10.2: Added retry logic with exponential backoff
    """
    The "Comparative Strategist" meta-call. Selects a single potent lens for comparing two works.
    Uses JSON mode via response_mime_type config.
    """
    status_container.write("Phase 0: Consulting the Comparative Strategist (Smart Selection)...")

    # Prepare the input package
    content_input = []
    
    # 1. Handle Media Upload for both works (concurrently)
    upload_tasks = []
    if work_a.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
        upload_tasks.append(upload_to_gemini_async(work_a, status_container))
    if work_b.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
        upload_tasks.append(upload_to_gemini_async(work_b, status_container))

    if upload_tasks:
        uploaded_files = run_async_tasks(upload_tasks)
        if not all(uploaded_files):
            status_container.update(label="Smart Selection failed due to upload error.", state="error")
            return None
        # The file references are now cached in the work_input objects.

    # 2. Construct the Prompt
    prompt = textwrap.dedent(f"""
    {JANUS_DIRECTIVES}
    
    **Role:** You are the "Comparative Strategist". Your task is to review two distinct creative works and select the single most potent analytical lens that creates a strong basis for their comparison.

    **Context:**
    - Work A: Title '{work_a.get_display_title()}', Modality '{work_a.modality}'
    - Work B: Title '{work_b.get_display_title()}', Modality '{work_b.modality}'
    - Available Lenses: {json.dumps(SORTED_LENS_NAMES)}

    **Instructions:**
    1. **Analyze Both Works:** Examine the content, themes, style, and structure of both Work A and Work B.
    2. **Identify Common Ground:** Find the most compelling shared theme, structural similarity, or contextual link between the two works.
    3. **Select a Bridge Lens:** Choose the single lens from the available list that would best illuminate this common ground. The lens should be insightful for *both* works, not just one.
    4. **Justify:** Provide a brief, compelling justification for why this specific lens is the ideal choice for comparing these two specific works.
    
    **Output Format (Strict JSON):**
    Your response MUST be a JSON object matching this schema:
    {{
      "selected_lens": "LensName",
      "justification": "The rationale for selecting this lens to bridge the two works..."
    }}
    
    Ensure the lens name matches the Available Lenses list exactly.
    """)
    
    # Add prompt and work data to the content input
    content_input.append(prompt)
    content_input.append(f"\n--- Work A ---\n")
    if work_a.gemini_file_ref: content_input.append(work_a.gemini_file_ref)
    if work_a.data: content_input.append(work_a.data)
    
    content_input.append(f"\n--- Work B ---\n")
    if work_b.gemini_file_ref: content_input.append(work_b.gemini_file_ref)
    if work_b.data: content_input.append(work_b.data)

    # 3. Execute the API call with Pydantic schema
    try:
        # v10.2: Use Pydantic schema for automatic validation and parsing
        response = client.models.generate_content(
            model=MODEL_FLASH,
            contents=content_input,
            config={
                "response_mime_type": "application/json",
                "response_schema": SingleLensSelectionResponse
            }
        )

        # v10.2: Accumulate metadata for Smart Selection (both works)
        accumulate_metadata(work_a, response)
        accumulate_metadata(work_b, response)

        # Access validated parsed response
        if not response.parsed:
            st.error("Failed to parse AI response. Please try again or use manual selection.")
            logging.error(f"Empty parsed response: {response.text}")
            return None

        result = response.parsed
        selected_lens = result.selected_lens
        justification = result.justification

        if selected_lens and selected_lens in SORTED_LENS_NAMES:
            status_container.write("Lens selected by Comparative Strategist.")
            st.success(f"**Janus Smart Selection:** {selected_lens}")
            with st.expander("View Justification"):
                st.write(justification)
            return selected_lens
    except google_exceptions.ResourceExhausted:
        st.error("⏱️ **Rate Limit Reached** - You've made too many requests in a short time. Please wait 1-2 minutes and try again, or check your Google Cloud quota.")
        logging.error("Comparative Smart Selection failed: ResourceExhausted")
        return None
    except Exception as e:
        st.error(f"An error occurred during Comparative Smart Selection: {e}")
        logging.error(f"Comparative Strategist error: {e}")
    return None


# =============================================================================
# CORE GENERATION FUNCTIONS (v10.0: Generative & Adaptive Architecture)
# =============================================================================

# -----------------------------------------------------------------------------
# STAGE 1: TRIAGE ANALYST
# -----------------------------------------------------------------------------

@retry_with_backoff(max_retries=3, base_delay=2)
async def execute_triage_analyst(client, work_input: WorkInput, status_container):
    # v10.1: Migrated to google-genai SDK - now accepts client instead of model
    # v10.2: Added retry logic with exponential backoff
    """
    Assesses the intrinsic complexity of the input work using a fast model (Flash-Lite).
    Output: 'Simple' or 'Complex'.
    """
    status_container.write("Phase 1: Triage Analysis (Assessing Complexity)...")
    
    content_input = []

    # 1. Prepare Input (Upload if necessary - handled asynchronously)
    if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
        # This handles the upload if not cached, or retrieves the cache.
        gemini_file = await upload_to_gemini_async(work_input, status_container)
        if not gemini_file:
            return None # Upload failed
        content_input.append(gemini_file)

    # 2. Construct Prompt
    prompt = textwrap.dedent(f"""
    {JANUS_DIRECTIVES}
    **Formatting Note:** The provided text work is pre-formatted. Do not interpret characters like '*' or '~' as markdown. Treat all characters as literal content.
    
    **Role:** Triage Analyst
    **Task:** Perform a rapid, multi-factor assessment of the provided creative work to determine its intrinsic complexity for analytical purposes.
    
    **Context:**
    1. Modality: `{work_input.modality}`
    2. The Creative Work: [Provided in the input context]

    **Assessment Factors:**
    1. **Structural Clarity:** How conventional or unconventional is the structure? (e.g., linear narrative vs. fragmented; clear composition vs. chaotic)
    2. **Symbolic Novelty/Density:** How dense is the work with symbols, metaphors, or references? Are they standard or highly novel?
    3. **Thematic Ambiguity:** Is the central theme straightforward or ambiguous/multifaceted?

    **Instructions:**
    1. Analyze the work based on the factors above.
    2. Synthesize these factors into a single complexity classification: 'Simple' or 'Complex'.
    
    **Output Format (Strict JSON):**
    {{
      "complexity_classification": "Simple" | "Complex",
      "justification": "Brief summary (1-2 sentences) of the key factors leading to the classification."
    }}
    """)

    content_input.append(prompt)

    if work_input.modality == M_TEXT:
        content_input.append(f"\n--- The Creative Work ---\n{work_input.data}")

    # 3. Execute API call with Pydantic schema
    try:
        # v10.2: Use Pydantic schema for automatic validation and parsing
        response = await client.aio.models.generate_content(
            model=MODEL_FLASH,
            contents=content_input,
            config={
                "response_mime_type": "application/json",
                "response_schema": TriageResponse
            }
        )

        # v10.2: Accumulate metadata
        accumulate_metadata(work_input, response)

        # Access validated parsed response
        if not response.parsed:
            status_container.write("Failed to parse Triage response. Defaulting to 'Complex'.")
            logging.error(f"Empty parsed response: {response.text}")
            return 'Complex'

        result = response.parsed
        classification = result.complexity_classification
        justification = result.justification

        if classification in ['Simple', 'Complex']:
            status_container.write(f"Triage complete. Complexity: {classification}. (Justification: {justification})")
            return classification
        else:
            # Fallback if classification is invalid
            status_container.write("Triage resulted in invalid classification. Defaulting to 'Complex'.")
            logging.error(f"Unexpected classification: {classification}")
            return 'Complex'

    except google_exceptions.ResourceExhausted:
        st.error("⏱️ **Rate Limit Reached** - You've made too many requests in a short time. Please wait 1-2 minutes and try again, or check your Google Cloud quota.")
        logging.error("Triage failed: ResourceExhausted")
        return 'Complex'  # Fallback to Complex mode
    except Exception as e:
        logging.error(f"Triage Analyst error: {e}")
        st.warning("An error occurred during analysis triage. Using comprehensive analysis mode instead.")
        with st.expander("🔍 Technical Details"):
            st.code(str(e))
        return 'Complex'

# -----------------------------------------------------------------------------
# STAGE 2: ADAPTIVE THEORETICIAN
# -----------------------------------------------------------------------------

@retry_with_backoff(max_retries=3, base_delay=2)
async def execute_adaptive_theoretician(client, work_input: WorkInput, lens_config: dict, status_container, cached_content_name=None, model=MODEL_FLASH):
    # v10.1: Migrated to google-genai SDK - now accepts client instead of model
    # v10.2: Added cached_content_name parameter for context caching optimization
    # v10.2: Now returns framework_name for proper display labeling
    # v10.2: Added retry logic with exponential backoff
    """
    Dynamically generates a custom list of analytical concepts/tasks for the work
    within the chosen framework. Also determines the optimal persona strategy.
    Output: (List of tasks, Persona instruction string, Framework name string).

    Args:
        cached_content_name: Optional cache name to use for cached context (file + system instructions)
    """
    status_container.write("Phase 2: Adaptive Theoretician (Generating Strategy)...")

    # Determine the framework name
    is_zeitgeist_mode = lens_config.get('is_zeitgeist', False)
    lens_keyword = lens_config.get('lens')
    
    # Retrieve backend name if available (for standard lenses)
    framework_name = lens_keyword
    if lens_keyword:
        lens_data = get_lens_data(lens_keyword)
        if lens_data:
            framework_name = lens_data.get("prompt_name") or lens_keyword

    content_input = []

    # 1. Prepare Input (Rely on cache from Triage or previous steps)
    # v10.2: If using cached content, file reference is already in the cache - don't add it again
    if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
        if cached_content_name:
            # Using cached content - file is already in cache, skip adding it
            pass
        else:
            # Not using cache - add file reference as usual
            # We rely on the cache established during Triage or upload_to_gemini_async if Triage was skipped.
            if not work_input.gemini_file_ref:
                 # Safety check: Ensure file is uploaded if somehow it wasn't during Triage/preload.
                gemini_file = await upload_to_gemini_async(work_input, status_container)
                if not gemini_file:
                    return None, None # Upload failed
                content_input.append(gemini_file)
            else:
                content_input.append(work_input.gemini_file_ref)


    # 2. Construct Prompt (Handles Zeitgeist vs. Standard Lenses)

    if is_zeitgeist_mode:
        zeitgeist_context = lens_config.get('zeitgeist_context')
        zeitgeist_persona = lens_config.get('zeitgeist_persona')
        framework_name = "Zeitgeist Simulation"

        # v10.2: When using cache, JANUS_DIRECTIVES are already in the cache
        directives_section = "" if cached_content_name else f"{JANUS_DIRECTIVES}\n        "

        prompt = textwrap.dedent(f"""
        {directives_section}**Formatting Note:** The provided text work is pre-formatted. Do not interpret characters like '*' or '~' as markdown. Treat all characters as literal content.

        **Role:** Adaptive Theoretician (Zeitgeist Specialist)
        **Task:** Analyze the creative work and dynamically generate a bespoke list of analytical tasks required to execute a "Zeitgeist Simulation".

        **Context: Zeitgeist Simulation**
        The goal is to understand how the work would be perceived by a specific witness within a specific historical moment.

        1. Modality: `{work_input.modality}`
        2. The Creative Work: [Provided in the input context]
        
        3. **User-Defined Historical Context:**
        <historical_context>
        {zeitgeist_context}
        </historical_context>

        4. **User-Defined Witness Persona:**
        <witness_persona>
        {zeitgeist_persona}
        </witness_persona>

        **Instructions:**
        1. **Analyze the Inputs:** Deeply review the work AND the context/persona. Identify the key intersections between the work's content/style and the historical moment/witness perspective.
        2. **Generate Analytical Tasks:** {"Formulate exactly 10 distinct, granular analytical tasks (concepts)" if model == MODEL_PRO else "Formulate 4 to 6 distinct, granular analytical tasks (concepts)"} that, when executed in parallel, will cover the most relevant aspects of this specific simulation.
        3. **Focus:** Tasks should focus on historical perception, valuation, critique, and potential misunderstandings or biases inherent in the defined Zeitgeist.
        4. **Clarity:** Each task must be a clear instruction for a specialist analyst.

        **Output Format (Strict JSON):**
        {{
          "framework": "{framework_name}",
          "persona_instruction": "The analysis must fully embody the defined Witness Persona (identified as '{zeitgeist_persona[:50]}...'), using their language and adhering strictly to the knowledge and biases of the Historical Context. Avoid anachronism.",
          "analytical_tasks": [
            "Task/Concept 1 description...",
            "Task/Concept 2 description...",
            // ... ({"exactly 10 tasks" if model == MODEL_PRO else "4-6 tasks"})
          ]
        }}
        """)
    else:
        # v10.2: Standard Lens Mode with Enhanced Selection Logic
        # Handles: Lens+Persona, Lens only, Persona only, Filters (Broad/Narrow)
        user_persona = lens_config.get('persona')
        scope_mode = lens_config.get('scope_mode', 'narrow')
        discipline_context = lens_config.get('discipline_context')
        function_context = lens_config.get('function_context')
        era_context = lens_config.get('era_context')
        geographic_context = lens_config.get('geographic_context')  # v10.4: Added geographic filter

        # Build context string for filter-based analyses
        filter_context_str = ""
        if discipline_context or function_context or era_context or geographic_context:
            filter_parts = []
            if discipline_context:
                filter_parts.append(f"Discipline: {discipline_context}")
            if function_context:
                filter_parts.append(f"Function: {function_context}")
            if era_context:
                filter_parts.append(f"Era: {era_context}")
            if geographic_context:
                filter_parts.append(f"Geography: {geographic_context}")
            filter_context_str = ", ".join(filter_parts)

        # v10.4: Helper function to build function-aware weighting instructions
        def get_function_weighting_instruction(lens_name, selected_function):
            """
            Returns additional prompt instructions when user specifies both a lens and a function filter.
            Checks if the lens appears in the selected functional tier and adds weighting guidance.
            """
            if not selected_function or not lens_name:
                return ""

            from lenses import LENSES_FUNCTIONAL

            # Find which functional tier(s) contain this lens
            lens_functions = []
            for tier_name, tier_lenses in LENSES_FUNCTIONAL.items():
                if lens_name in tier_lenses:
                    lens_functions.append(tier_name)

            # If lens doesn't appear in the selected function tier, return empty string
            if selected_function not in lens_functions:
                return ""

            # Build weighting instructions based on function type
            function_emphasis = {
                "Tier 1: Contextual (What/Who/When)": "historical context, cultural background, temporal placement, and situational factors",
                "Tier 2: Mechanical (How it Works)": "structural elements, formal mechanisms, technical processes, and systematic operations",
                "Tier 3: Interpretive (Why it Matters)": "meaning-making, philosophical significance, ethical implications, and interpretive depth"
            }

            emphasis = function_emphasis.get(selected_function, "")

            return f"""
            - **Function Weighting:** The user has specified '{selected_function}' as the functional emphasis.
            - Weight your analysis toward {emphasis}.
            - While maintaining the {lens_name} framework, prioritize this functional dimension in your analytical tasks.
            """

        # v10.4: Helper function to build discipline-aware weighting instructions
        def get_discipline_weighting_instruction(lens_name, selected_discipline):
            """
            Returns additional prompt instructions when user specifies both a lens and a discipline filter.
            Checks if the lens appears in the selected discipline and adds weighting guidance.
            """
            if not selected_discipline or not lens_name:
                return ""

            from lenses import LENSES_HIERARCHY

            # Find which discipline(s) contain this lens
            lens_disciplines = []
            for discipline_name, discipline_lenses in LENSES_HIERARCHY.items():
                if lens_name in discipline_lenses:
                    lens_disciplines.append(discipline_name)

            # If lens doesn't appear in the selected discipline, return empty string
            if selected_discipline not in lens_disciplines:
                return ""

            # Build weighting instructions based on discipline type
            discipline_emphasis = {
                "Art History": "visual aesthetics, artistic movements, formal composition, and art-historical context",
                "Aesthetics": "beauty, taste, artistic experience, and aesthetic judgment",
                "Literary Theory": "textual analysis, narrative structure, literary devices, and reader response",
                "Film Studies": "cinematic techniques, visual storytelling, montage, and film-specific aesthetics",
                "Media Studies": "media technologies, communication channels, audience reception, and media ecology",
                "Philosophy": "conceptual analysis, logical argumentation, metaphysical questions, and epistemological concerns",
                "Political Philosophy": "governance, justice, rights, political legitimacy, and power structures",
                "Ethics": "moral reasoning, virtue, duty, consequences, and ethical principles",
                "Theology": "divine nature, religious doctrine, faith, revelation, and spiritual interpretation",
                "Psychology": "mental processes, behavior, cognition, emotion, and psychological development",
                "Sociology": "social structures, group dynamics, institutions, and collective behavior",
                "Economics": "resource allocation, markets, incentives, scarcity, and economic behavior",
                "Anthropology": "cultural practices, human diversity, kinship systems, and cross-cultural comparison",
                "History": "temporal development, causation, historical evidence, and contextual change over time",
                "Linguistics": "language structure, meaning-making, syntax, semantics, and linguistic patterns",
                "Science & Technology Studies": "scientific methodology, technological systems, innovation, and science-society relations"
            }

            emphasis = discipline_emphasis.get(selected_discipline, f"the methodologies and concerns of {selected_discipline}")

            return f"""
            - **Discipline Weighting:** The user has specified '{selected_discipline}' as the disciplinary emphasis.
            - Weight your analysis toward {emphasis}.
            - While maintaining the {lens_name} framework, prioritize this disciplinary dimension in your analytical tasks.
            """

        # v10.4: Helper function to build era-aware weighting instructions
        def get_era_weighting_instruction(lens_name, selected_era):
            """
            Returns additional prompt instructions when user specifies both a lens and an era filter.
            Checks if the lens is associated with the selected era and adds weighting guidance.
            """
            if not selected_era or not lens_name:
                return ""

            from lenses import LENS_DEFINITIONS

            lens_data = LENS_DEFINITIONS.get(lens_name)
            if not lens_data:
                return ""

            lens_eras = lens_data.get('eras', [])

            # If lens doesn't appear in the selected era, return empty string
            if selected_era not in lens_eras:
                return ""

            return f"""
            - **Era Weighting:** The user has specified '{selected_era}' as the temporal emphasis.
            - Weight your analysis toward perspectives and concerns from {selected_era}.
            - While maintaining the {lens_name} framework, prioritize how this framework manifests in this historical period.
            """

        # v10.4: Helper function to build geographic-aware weighting instructions
        def get_geographic_weighting_instruction(lens_name, selected_geography):
            """
            Returns additional prompt instructions when user specifies both a lens and a geographic filter.
            Checks if the lens appears in the selected geographic region and adds weighting guidance.
            """
            if not selected_geography or not lens_name:
                return ""

            from lenses import LENSES_GEOGRAPHIC

            # Find which geographic region(s) contain this lens
            lens_geographies = []
            for region_name, region_lenses in LENSES_GEOGRAPHIC.items():
                if lens_name in region_lenses:
                    lens_geographies.append(region_name)

            # If lens doesn't appear in the selected geography, return empty string
            if selected_geography not in lens_geographies:
                return ""

            return f"""
            - **Geographic Weighting:** The user has specified '{selected_geography}' as the regional emphasis.
            - Weight your analysis toward perspectives and concerns from {selected_geography}.
            - While maintaining the {lens_name} framework, prioritize how this framework manifests in {selected_geography}.
            """

        # PRIORITY HIERARCHY:
        # 1. Lens + Persona (most specific)
        # 2. Lens only
        # 3. Persona only (Option B - flexible persona analysis)
        # 4. Filters + Narrow (smart select lens)
        # 5. Filters + Broad (category-level analysis)

        if lens_keyword and user_persona and user_persona != "(No Persona)":
            # CASE 1: Lens + Specific Persona
            # v10.4: Add function/discipline/era/geographic weighting if specified
            function_instruction = get_function_weighting_instruction(lens_keyword, function_context)
            discipline_instruction = get_discipline_weighting_instruction(lens_keyword, discipline_context)
            era_instruction = get_era_weighting_instruction(lens_keyword, era_context)
            geographic_instruction = get_geographic_weighting_instruction(lens_keyword, geographic_context)
            persona_strategy_instruction = f"""
            **Persona Strategy (User Override - Specific Figure with Lens):**
            The user has explicitly requested the persona: '{user_persona}' with the {lens_keyword} lens.
            You MUST adopt this persona for the final analysis, applying their perspective through the {lens_keyword} framework.{function_instruction}{discipline_instruction}{era_instruction}{geographic_instruction}
            """
        elif lens_keyword and (not user_persona or user_persona == "(No Persona)"):
            # CASE 2: Lens only (with optional generic title or AI picks persona)
            # v10.3: Fixed bug - if lens has no pool, use generic title instead of letting AI invent personas
            # v10.4: Add function/discipline/era/geographic weighting if specified
            function_instruction = get_function_weighting_instruction(lens_keyword, function_context)
            discipline_instruction = get_discipline_weighting_instruction(lens_keyword, discipline_context)
            era_instruction = get_era_weighting_instruction(lens_keyword, era_context)
            geographic_instruction = get_geographic_weighting_instruction(lens_keyword, geographic_context)

            if user_persona == "(No Persona)" or lens_keyword not in PERSONA_POOL:
                persona_strategy_instruction = f"""
                **Persona Strategy (Generic Title):**
                {"The user has requested NO specific historical figure." if user_persona == "(No Persona)" else "This framework has no associated persona pool."}
                You MUST use a generic archetypal title based on the framework name.
                - Define a simple, clear archetypal title (e.g., 'The Republican Theorist' for Republicanism, 'The Democratic Philosopher' for Democracy, 'The Conservative Thinker' for Conservatism).
                - **CRITICAL:** The title MUST be specific to the framework. Avoid generic titles like 'The Analyst' or 'The Critic' that could apply to any framework.
                - Do NOT use a specific historical figure's name.{function_instruction}{discipline_instruction}{era_instruction}{geographic_instruction}
                """
            else:
                # AI has discretion to pick from the pool (pool exists at this point)
                pool = PERSONA_POOL[lens_keyword]
                pool_instruction = f"- **Available Pool (REQUIRED):** {', '.join(pool)}\n            - You MUST select one persona from this pool for the final analysis."

                persona_strategy_instruction = f"""
                **Persona Strategy (AI Discretion from Pool):**
                Determine the optimal persona for the final analysis based on the `{framework_name}` framework and the content of the work.
                {pool_instruction}
                - **Selection Criteria:** Choose the figure from the pool whose historical perspective, writings, or era most directly resonates with the work's themes, context, or subject matter.
                - **CRITICAL:** You MUST pick a specific person from the pool. Each persona MUST be unique and immediately distinguishable from others.{function_instruction}{discipline_instruction}{era_instruction}{geographic_instruction}
                """

        elif user_persona and user_persona not in ["(No Persona)", "(AI Decides)"]:
            # CASE 3: Persona only (no specific lens)
            # v10.4: Respect narrow vs broad scope_mode
            # v10.5: Enable smart-selection of unset filter dimensions in narrow mode
            from lenses import PERSONA_METADATA
            persona_meta = PERSONA_METADATA.get(user_persona, {})
            persona_lenses = persona_meta.get('lenses', [])
            lenses_str = ", ".join(persona_lenses) if persona_lenses else "their associated philosophical frameworks"

            framework_name = f"{user_persona}'s Perspective"

            if scope_mode == 'narrow':
                # Narrow mode: AI must smart-select the SINGLE best lens from persona's associations
                # v10.5: Build optional refinement instructions for unset dimensions
                optional_refinements = []
                if not era_context:
                    optional_refinements.append("   - **Era (Optional):** You may select a specific historical era if it would meaningfully enhance the analysis, or leave unset if not valuable")
                if not geographic_context:
                    optional_refinements.append("   - **Geography (Optional):** You may select a specific geographic region if it would meaningfully enhance the analysis, or leave unset if not valuable")
                if not discipline_context:
                    optional_refinements.append("   - **Discipline (Optional):** You may select a specific academic discipline if it would meaningfully enhance the analysis, or leave unset if not valuable")

                optional_refinement_str = "\n".join(optional_refinements) if optional_refinements else ""

                persona_strategy_instruction = f"""
                **Persona Strategy (Persona-Driven, Narrow Focus):**
                The user has selected the persona '{user_persona}' without specifying a lens, in Narrow mode.
                You MUST:
                1. Smart-select the SINGLE most appropriate lens from {user_persona}'s associated frameworks: {lenses_str}
                2. Choose the lens that best applies to this specific work's content, themes, and context
                3. Adopt {user_persona}'s persona for the final analysis, applying it through that ONE chosen framework
                4. Justify your lens selection briefly in the persona instruction
                - **CRITICAL:** Select exactly ONE lens. Do not attempt to synthesize across multiple frameworks.

                **Additional Filter Refinement (Optional):**
{optional_refinement_str}
                """
            else:
                # Broad mode: Synthesize across ALL associated lenses
                persona_strategy_instruction = f"""
                **Persona Strategy (Persona-Driven, Broad Synthesis):**
                The user has selected the persona '{user_persona}' without specifying a lens, in Broad mode.
                You MUST adopt {user_persona}'s persona for the final analysis, drawing flexibly from their full philosophical range.
                - Associated frameworks: {lenses_str}
                - Synthesize insights across ALL of {user_persona}'s associated frameworks
                - Apply {user_persona}'s general worldview, values, and analytical approach holistically
                - You have flexibility to draw from any aspect of their thinking that's relevant to the work
                """

        elif scope_mode == 'broad' and filter_context_str:
            # CASE 4: Filters only + Broad mode - Category-level analysis
            framework_name = f"Broad {filter_context_str} Analysis"
            persona_strategy_instruction = f"""
            **Persona Strategy (Broad Category Analysis):**
            The user has requested a broad analysis from the perspective of: {filter_context_str}
            You MUST provide a BROAD, category-level analysis that draws from the general principles and themes of this perspective.
            - Do NOT select a specific lens or historical figure
            - Synthesize insights from across the category
            - Adopt an authoritative but general analytical voice appropriate to the category
            """

        elif scope_mode == 'narrow' and filter_context_str:
            # CASE 5: Filters only + Narrow mode - Smart select lens
            # v10.5: Enable smart-selection of unset filter dimensions
            framework_name = f"Smart Selection ({filter_context_str})"

            # Build optional refinement instructions for unset dimensions
            optional_refinements = []
            if not discipline_context:
                optional_refinements.append("   - **Discipline (Optional):** You may select a specific academic discipline if it would meaningfully enhance the analysis, or leave unset if not valuable")
            if not function_context:
                optional_refinements.append("   - **Function (Optional):** You may select a specific functional tier (Contextual/Mechanical/Interpretive) if it would meaningfully enhance the analysis, or leave unset if not valuable")
            if not era_context:
                optional_refinements.append("   - **Era (Optional):** You may select a specific historical era if it would meaningfully enhance the analysis, or leave unset if not valuable")
            if not geographic_context:
                optional_refinements.append("   - **Geography (Optional):** You may select a specific geographic region if it would meaningfully enhance the analysis, or leave unset if not valuable")

            optional_refinement_str = "\n".join(optional_refinements) if optional_refinements else ""

            persona_strategy_instruction = f"""
            **Persona Strategy (Smart Selection - Narrow Scope):**
            The user has provided filter criteria: {filter_context_str}

            You MUST smart-select the optimal analytical configuration for this work:
            1. **Lens Selection (REQUIRED):** Select the SINGLE most potent lens that matches the filter criteria and best applies to this work
            2. **Persona Selection (if applicable):** Adopt the appropriate persona from the lens's pool (if available)
            3. **Additional Filter Refinement (Optional):**
{optional_refinement_str}

            Justify your selections briefly in the persona instruction.
            """

        else:
            # Fallback: No meaningful selection (should not reach here due to validation)
            framework_name = "General Analysis"
            persona_strategy_instruction = """
            **Persona Strategy (General Analysis):**
            Provide a thoughtful analytical perspective appropriate to the work.
            """

        # v10.2: When using cache, JANUS_DIRECTIVES are already in the cache
        directives_section = "" if cached_content_name else f"{JANUS_DIRECTIVES}\n        "

        prompt = textwrap.dedent(f"""
        {directives_section}**Formatting Note:** The provided text work is pre-formatted. Do not interpret characters like '*' or '~' as markdown. Treat all characters as literal content.

        **Role:** Adaptive Theoretician
        **Task:** Analyze the creative work against your vast knowledge of the specified analytical framework. Dynamically generate a bespoke list of the most relevant concepts and analytical tasks required for a deep analysis.

        **Context:**
        1. Analytical Framework: `{framework_name}`
        2. Modality: `{work_input.modality}`
        3. The Creative Work: [Provided in the input context]

        **Instructions:**
        1. **Analyze the Work:** Identify the key features, themes, structures, and ambiguities of the creative work.
        2. **Consult Framework Knowledge:** Access your internal knowledge base regarding the `{framework_name}` framework (its history, key proponents, core concepts, methodologies, and internal debates).
        3. **Generate Bespoke Strategy:** {"Identify exactly 10 granular concepts or analytical tasks" if model == MODEL_PRO else "Identify the 4 to 6 most potent, granular concepts or analytical tasks"} *within* this framework that apply specifically to this work. This replaces any static checklist.
        4. **Granularity:** Tasks should be distinct enough to be executed in parallel by specialists.
        5. **Clarity:** Each task must be a clear instruction for a specialist analyst focusing on that specific concept.

        {persona_strategy_instruction}

        **Output Format (Strict JSON):**
        {{
          "framework": "{framework_name}",
          "persona_instruction": "A detailed instruction defining the persona the final analysis MUST adopt (e.g., 'Adopt the authoritative persona of Seneca, focusing on...' or 'Adopt the persona of The Formalist Critic, emphasizing...')",
          "analytical_tasks": [
            "Task/Concept 1 description...",
            "Task/Concept 2 description...",
            // ... ({"exactly 10 tasks" if model == MODEL_PRO else "4-6 tasks"})
          ]
        }}
        """)

    content_input.append(prompt)

    if work_input.modality == M_TEXT:
        content_input.append(f"\n--- The Creative Work ---\n{work_input.data}")

    # 3. Execute API call with JSON mode
    try:
        from google.genai import types
        # v10.2: Use Pydantic schema for automatic validation and parsing
        # v10.2: Use cached content if available
        config_dict = {
            "response_mime_type": "application/json",
            "response_schema": AdaptiveTheoryResponse
        }
        if cached_content_name:
            config_dict["cached_content"] = cached_content_name

        response = await client.aio.models.generate_content(
            model=model,  # Model selection based on analysis mode (matches cache model)
            contents=content_input,
            config=types.GenerateContentConfig(**config_dict)
        )

        # v10.2: Accumulate metadata
        accumulate_metadata(work_input, response)

        # Access validated parsed response
        if not response.parsed:
            status_container.write("Failed to parse Theoretician response.")
            logging.error(f"Empty parsed response: {response.text}")
            return None, None

        result = response.parsed
        tasks = result.analytical_tasks
        persona_instruction = result.persona_instruction

        if tasks and persona_instruction:
            status_container.write(f"Theoretician complete. Generated {len(tasks)} analytical tasks.")
            # v10.2: Return framework_name for proper display labeling
            return tasks, persona_instruction, framework_name
        else:
            status_container.write("Theoretician failed to generate tasks or persona instruction.")
            logging.error(f"Empty tasks or persona: {result}")
            return None, None, None

    except Exception as e:
        logging.error(f"Adaptive Theoretician error: {e}")
        status_container.write(f"An error occurred during the Theoretician phase. Error: {e}")
        return None, None, None

# -----------------------------------------------------------------------------
# STAGE 3: SPECIALIST SWARM (Helper Function for individual specialist)
# -----------------------------------------------------------------------------

@retry_with_backoff(max_retries=3, base_delay=2)
async def execute_specialist(client, work_input: WorkInput, task_description: str, status_container, cached_content_name=None, model=MODEL_FLASH):
    # v10.1: Migrated to google-genai SDK - now accepts client instead of model
    # v10.2: Added cached_content_name parameter for context caching optimization
    # v10.2: Added retry logic with exponential backoff
    # v10.2: Added model parameter to support dynamic model selection based on analysis mode
    """
    Executes a single, granular analysis based on a specific task/concept.

    Args:
        cached_content_name: Optional cache name to use for cached context (file + system instructions)
        model: The model to use for analysis (default: MODEL_FLASH). Must match cache model if cache is used.
    """
    # Note: We do not update the main status_container here extensively as these run in parallel.

    content_input = []
    modality_instructions = get_modality_instructions(work_input)

    # 1. Prepare Input (Rely on existing cache)
    # v10.2: If using cached content, file reference is already in the cache
    if not cached_content_name and work_input.gemini_file_ref:
        content_input.append(work_input.gemini_file_ref)

    # 2. Construct Prompt
    # v10.2: When using cache, JANUS_DIRECTIVES and modality instructions are already in the cache
    if cached_content_name:
        prompt = textwrap.dedent(f"""
        **Formatting Note:** The provided text work is pre-formatted. Do not interpret characters like '*' or '~' as markdown. Treat all characters as literal content.

        **Role:** Specialist Analyst
        **Task:** Perform a deep, granular analysis of the creative work focusing strictly on the specific analytical task assigned to you.

        **Assigned Analytical Task (CRITICAL FOCUS):**
        <task>
        {task_description}
        </task>

        **Instructions:**
        1. **Analyze:** Focus your analysis entirely on the assigned task. Ignore aspects of the work irrelevant to this specific concept.
        2. **Depth:** Provide a detailed, profound analysis.
        3. **Evidence:** Ground all claims in specific evidence from the work.
        4. **Format:** Output the analysis directly. Do not use any headers, titles, or introductory phrases. This output will be synthesized later by a master agent.
        5. **Formatting Constraint (CRITICAL):** Use standard characters and markdown (e.g., bold, italics) for all text. Do NOT use special Unicode characters, script fonts, or other non-standard character sets. Use standard quotation marks, dollar signs, and punctuation. The entire output must be readable and use standard typography.
        """)
    else:
        prompt = textwrap.dedent(f"""
        {JANUS_DIRECTIVES}
        **Formatting Note:** The provided text work is pre-formatted. Do not interpret characters like '*' or '~' as markdown. Treat all characters as literal content.

        **Role:** Specialist Analyst
        **Task:** Perform a deep, granular analysis of the creative work focusing strictly on the specific analytical task assigned to you.

        **Context:**
        1. Modality: `{work_input.modality}`
        2. The Creative Work: [Provided in the input context]

        **Assigned Analytical Task (CRITICAL FOCUS):**
        <task>
        {task_description}
        </task>

        **Instructions:**
        1. **Analyze:** Focus your analysis entirely on the assigned task. Ignore aspects of the work irrelevant to this specific concept.
        2. **Depth:** Provide a detailed, profound analysis.
        3. **Evidence:** Ground all claims in specific evidence from the work.
        4. **Modality Requirements:** Adhere to these instructions regarding the medium:
        {textwrap.indent(modality_instructions.strip(), '    ')}
        5. **Format:** Output the analysis directly. Do not use any headers, titles, or introductory phrases. This output will be synthesized later by a master agent.
        6. **Formatting Constraint (CRITICAL):** Use standard characters and markdown (e.g., bold, italics) for all text. Do NOT use special Unicode characters, script fonts, or other non-standard character sets. Use standard quotation marks, dollar signs, and punctuation. The entire output must be readable and use standard typography.
        """)

    content_input.append(prompt)

    if work_input.modality == M_TEXT:
        content_input.append(f"\n--- The Creative Work ---\n{work_input.data}")

    # 3. Execute API call (standard text output)
    try:
        from google.genai import types
        # v10.2: Use cached content if available
        config_dict = {}
        if cached_content_name:
            config_dict["cached_content"] = cached_content_name

        response = await client.aio.models.generate_content(
            model=model,  # Model selection based on analysis mode (Flash for Adaptive/Surface, Pro for Deep Dive)
            contents=content_input,
            config=types.GenerateContentConfig(**config_dict) if config_dict else None
        )

        # v10.2: Accumulate metadata
        accumulate_metadata(work_input, response)

        return response.text.strip()
    except Exception as e:
        logging.error(f"Specialist error for task '{task_description[:50]}...': {e}")
        # Return an error message so the synthesizer knows this part failed, but can continue.
        return f"[Error during specialist analysis for this concept: {e}]"

# -----------------------------------------------------------------------------
# STAGE 4A: MID SYNTHESIZER (Deep Dive Only)
# -----------------------------------------------------------------------------

@retry_with_backoff(max_retries=3, base_delay=2)
async def execute_mid_synthesizer(client, work_input: WorkInput, lens_config: dict, persona_instruction: str, specialist_reports: list, status_container, synthesizer_id: str):
    # v10.3: New function for Deep Dive two-stage synthesis
    """
    Integrates 6 specialist reports into an intermediate synthesis.
    Used in Deep Dive mode to create two parallel mid-level syntheses.

    Args:
        synthesizer_id: Identifier for this mid-synthesizer (e.g., "A" or "B")
        specialist_reports: List of exactly 6 specialist reports
    """
    status_container.write(f"Mid-Synthesis {synthesizer_id}: Integrating {len(specialist_reports)} specialist reports...")

    # Determine the framework name (similar logic as Master Synthesizer)
    is_zeitgeist_mode = lens_config.get('is_zeitgeist', False)
    lens_keyword = lens_config.get('lens')
    framework_name = lens_keyword or "Analysis"
    if lens_keyword:
        lens_data = get_lens_data(lens_keyword)
        if lens_data:
            framework_name = lens_data.get("prompt_name") or lens_keyword
    if is_zeitgeist_mode:
        framework_name = "Zeitgeist Simulation"

    # Format the specialist reports
    reports_formatted = []
    for i, report in enumerate(specialist_reports):
        reports_formatted.append(f"<specialist_report id='{i+1}'>\n{report}\n</specialist_report>")
    reports_string = "\n\n".join(reports_formatted)

    # Construct Prompt
    prompt = textwrap.dedent(f"""
    {JANUS_DIRECTIVES}

    **Role:** Mid-Level Synthesizer
    **Task:** Integrate a subset of specialist reports into an intermediate synthesis.

    **Context:**
    1. Framework: `{framework_name}`
    2. Work Title: `{work_input.get_display_title()}`
    3. Specialist Reports: [Provided below - {len(specialist_reports)} reports]

    **Persona Instruction (MANDATORY):**
    <persona_instruction>
    {persona_instruction}
    </persona_instruction>

    **Specialist Reports:**
    <reports>
    {reports_string}
    </reports>

    **Instructions:**
    1. **Synthesize:** Weave the insights from these specialist reports together. Find connections, contrasts, and emergent themes.
    2. **Critical Constraint:** Do NOT reference the internal analysis process, pipeline, specialist reports, or analytical frameworks in your output.
    3. **Adopt Persona:** Fully embody the persona defined in the Persona Instruction.
    4. **Intermediate Output:** This is a mid-level synthesis. Create a cohesive integration of these reports that will later be combined with another mid-synthesis.
    5. **Structure:** Organize logically (thematically or structurally).
    6. **No Header:** Do NOT include the persona header (e.g., "### Analysis by..."). That will be added in the final synthesis stage.
    7. **Formatting Constraint:** Use standard characters and markdown only.

    Output the intermediate synthesized analysis.
    """)

    # Execute API call (Uses Pro model, no streaming for mid-synthesis)
    try:
        response = await client.aio.models.generate_content(
            model=MODEL_PRO,
            contents=prompt
        )

        # Accumulate metadata
        accumulate_metadata(work_input, response)

        status_container.write(f"Mid-Synthesis {synthesizer_id} complete.")
        return response.text.strip()
    except Exception as e:
        logging.error(f"Mid-Synthesizer {synthesizer_id} error: {e}")
        status_container.write(f"An error occurred during Mid-Synthesis {synthesizer_id}. Error: {e}")
        return None

# -----------------------------------------------------------------------------
# STAGE 4: MASTER SYNTHESIZER
# -----------------------------------------------------------------------------

@retry_with_backoff(max_retries=3, base_delay=2)
async def execute_master_synthesizer(client, work_input: WorkInput, lens_config: dict, persona_instruction: str, specialist_reports: list, status_container, stream_container=None):
    # v10.1: Migrated to google-genai SDK - now accepts client instead of model
    # v10.2: Added streaming support via optional stream_container
    # v10.2: Added retry logic with exponential backoff
    # v10.3: Now handles both specialist reports (Adaptive/Surface Scrape) and mid-syntheses (Deep Dive)
    """
    Integrates specialist reports or mid-syntheses into a single, holistic analysis.

    Args:
        specialist_reports: Either a list of specialist reports (4-6) OR a list of 2 mid-syntheses (for Deep Dive)
        stream_container: Optional Streamlit container for streaming output. If provided, text streams in real-time.
    """
    # v10.3: Detect if we're integrating mid-syntheses (Deep Dive) or specialist reports
    is_deep_dive_final = len(specialist_reports) == 2

    if is_deep_dive_final:
        status_container.write("Final Synthesizer (Integrating 2 mid-syntheses)...")
    else:
        status_container.write("Phase 4: Master Synthesizer (Integrating Analysis)...")

    # Determine the framework name (similar logic as Theoretician)
    is_zeitgeist_mode = lens_config.get('is_zeitgeist', False)
    lens_keyword = lens_config.get('lens')
    framework_name = lens_keyword or "Analysis"
    if lens_keyword:
        lens_data = get_lens_data(lens_keyword)
        if lens_data:
            framework_name = lens_data.get("prompt_name") or lens_keyword
    if is_zeitgeist_mode:
        framework_name = "Zeitgeist Simulation"

    # v10.3: Format inputs differently based on type (specialist reports vs mid-syntheses)
    if is_deep_dive_final:
        # Deep Dive Final: Integrating 2 mid-syntheses
        reports_formatted = []
        for i, synthesis in enumerate(specialist_reports):
            reports_formatted.append(f"<mid_synthesis id='{chr(65+i)}'>\n{synthesis}\n</mid_synthesis>")
        reports_string = "\n\n".join(reports_formatted)
        input_type = "Mid-Syntheses"
        task_description = "Integrate two intermediate syntheses into a single, final, cohesive analysis."
        synthesis_instruction = "Weave the insights from both mid-syntheses together. These are already refined analyses - your task is to create a seamless integration that reads as a single, unified whole."
    else:
        # Adaptive/Surface Scrape: Integrating specialist reports
        reports_formatted = []
        for i, report in enumerate(specialist_reports):
            reports_formatted.append(f"<specialist_report id='{i+1}'>\n{report}\n</specialist_report>")
        reports_string = "\n\n".join(reports_formatted)
        input_type = "Specialist Reports"
        task_description = "Integrate a collection of specialist reports into a single, cohesive, holistic analysis of the creative work."
        synthesis_instruction = "Weave the insights from all specialist reports together. Do not simply summarize them sequentially. Find the connections, contrasts, and emergent themes across the reports."

    # Construct Prompt
    prompt = textwrap.dedent(f"""
    {JANUS_DIRECTIVES}

    **Role:** Master Synthesizer
    **Task:** {task_description}

    **Context:**
    1. Framework: `{framework_name}`
    2. Work Title: `{work_input.get_display_title()}`
    3. {input_type}: [Provided below]

    **Persona Instruction (MANDATORY):**
    <persona_instruction>
    {persona_instruction}
    </persona_instruction>

    **{input_type}:**
    <reports>
    {reports_string}
    </reports>

    **Instructions:**
    1. **Synthesize:** {synthesis_instruction}
    2. **Critical Constraint:** Do NOT reference the internal analysis process, pipeline, specialist reports, or analytical frameworks in your output. Your task is to synthesize insights about the creative work itself, not to engage with or critique the theoretical frameworks used as tools.
    3. **Adopt Persona:** Fully embody the persona defined in the Persona Instruction. The tone, style, and perspective of the final output must be consistent with this persona.
    4. **Holistic View:** The final output should read as a single, unified analysis, not a collection of parts.
    5. **Structure:** Organize the analysis logically (e.g., thematically or structurally).
    6. **Header Requirement:** Begin the entire response with a single markdown H3 header identifying the persona, derived from the Persona Instruction. For example: '### Analysis by Seneca' or '### Analysis by The Witness from 1905'. This is critical for later stages (e.g., Dialectical Dialogue).
    7. **Formatting Constraint:** Use standard characters and markdown (e.g., bold, italics) for all text. Do NOT use special Unicode characters, script fonts (e.g., 𝓉𝑒𝓍𝓉), or other non-standard character sets for stylistic purposes. The entire output must be readable and use standard typography.

    Output the final, synthesized analysis.
    """)

    # Execute API call (Uses Pro model, with optional streaming)
    try:
        # v10.2: Use streaming if container provided
        if stream_container:
            # Streaming mode - text appears word-by-word
            full_text = ""
            placeholder = stream_container.empty()

            async for chunk in await client.aio.models.generate_content_stream(
                model=MODEL_PRO,
                contents=prompt
            ):
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text)

            # Accumulate metadata from final response
            # Note: In streaming mode, metadata comes with the last chunk
            if hasattr(chunk, 'usage_metadata'):
                # Create a pseudo-response object for metadata accumulation
                class StreamResponse:
                    def __init__(self, usage_metadata, text):
                        self.usage_metadata = usage_metadata
                        self.text = text
                accumulate_metadata(work_input, StreamResponse(chunk.usage_metadata, full_text))

            status_container.write("Synthesis complete.")
            return full_text.strip()
        else:
            # Non-streaming mode (backward compatible)
            response = await client.aio.models.generate_content(
                model=MODEL_PRO,
                contents=prompt
            )

            # v10.2: Accumulate metadata
            accumulate_metadata(work_input, response)

            return response.text.strip()
    except Exception as e:
        logging.error(f"Master Synthesizer error: {e}")
        status_container.write(f"An error occurred during the Synthesis phase. Error: {e}")
        return None

# -----------------------------------------------------------------------------
# ENGINE ENTRY POINTS (The Orchestrator)
# -----------------------------------------------------------------------------

# v10.0: REWRITTEN (The main asynchronous pipeline)
# v10.2: Added cache support for multi-lens optimization
async def async_generate_analysis(lens_config: dict, work_input: WorkInput, enforced_complexity=None, use_cache=False, strategy_container=None, stream_container=None):
    """
    The main engine pipeline (v10.0: Generative & Adaptive).
    Manages Triage, Theoretician, Swarm, and Synthesizer stages.

    Args:
        lens_config: Configuration for the lens/framework to use
        work_input: The creative work to analyze
        enforced_complexity: Optional complexity level to enforce (for comparative rigor)
        use_cache: If True, will use cached content (work_input must have cache_ref set)
        strategy_container: Optional container for displaying strategy during execution
        stream_container: Optional container for streaming synthesis output
    """
    api_key = st.session_state.get("api_key")
    if not api_key:
        st.error("API Key missing for analysis pipeline.")
        return None

    # Determine Execution Mode (Standard Adaptive vs. Max Depth)
    analysis_mode = st.session_state.get("analysis_mode", MODE_ADAPTIVE) # Default to Adaptive
    deep_dive_mode = (analysis_mode == MODE_DEEP_DIVE)
    surface_scrape_mode = (analysis_mode == MODE_SURFACE_SCRAPE)

    # --- Setup Status Display ---
    lens_keyword = lens_config.get('lens')
    specific_persona = lens_config.get('persona')
    is_zeitgeist_mode = lens_config.get('is_zeitgeist', False)

    if is_zeitgeist_mode:
        status_text = f"Simulating Zeitgeist for '{work_input.get_display_title()}'..."
    elif lens_keyword:
        status_text = f"Analyzing '{work_input.get_display_title()}' through {lens_keyword} lens..."
        if specific_persona:
            status_text = f"Analyzing '{work_input.get_display_title()}' as {specific_persona} ({lens_keyword})..."
    else:
        status_text = f"Analyzing '{work_input.get_display_title()}'..."
    
    # v10.0: Add mode indicator to status
    status_text += f" [{analysis_mode}]"

    status_container = st.status(status_text, expanded=False)
    
    with status_container as status:
        try:
            # v10.1: Initialize API Client
            # The pipeline now uses a single client for all API calls
            client = get_client(api_key)

            # Validation
            if not client:
                 status.update(label="Analysis failed due to client initialization error.", state="error")
                 return None

            # v10.2: Extract cache name if using cached content
            cache_name = work_input.cache_ref.name if (use_cache and work_input.cache_ref) else None

            # --- STAGE 1: TRIAGE ANALYST (Adaptive Mode Only) ---
            # v10.0.6: Support enforced complexity for comparative rigor
            if enforced_complexity:
                # Comparative mode: Use pre-determined complexity level
                complexity = enforced_complexity
                status.write(f"Phase 1: Triage skipped (Comparative Rigor enforced: {complexity}).")
                # Ensure file is uploaded if needed
                if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
                    if not await upload_to_gemini_async(work_input, status):
                        status.update(label="Analysis failed due to upload error (pre-load).", state="error")
                        return None
            elif analysis_mode == MODE_ADAPTIVE:
                # Standard Adaptive mode: Run triage
                complexity = await execute_triage_analyst(client, work_input, status)
                if complexity is None:
                     # This typically means the upload failed within Triage.
                     status.update(label="Analysis failed during Triage (likely upload error).", state="error")
                     return None
            else: # Deep Dive or Surface Scrape
                complexity = 'Complex' # Default if skipped
                status.write(f"Phase 1: Triage skipped ({analysis_mode}).")
                # If skipping Triage, we MUST ensure the file is uploaded before the next stage.
                if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
                    if not await upload_to_gemini_async(work_input, status):
                        status.update(label="Analysis failed due to upload error (pre-load).", state="error")
                        return None


            # --- STAGE 2: ADAPTIVE THEORETICIAN ---
            # Determine model selection based on mode (must match cache model)
            if deep_dive_mode or (analysis_mode == MODE_ADAPTIVE and complexity == 'Complex'):
                status.write("Theoretician using Gemini Pro.")
                theoretician_model = MODEL_PRO
            else: # Adaptive (Simple) or Surface Scrape
                status.write("Theoretician using Gemini Flash-Lite.")
                theoretician_model = MODEL_FLASH

            analytical_tasks, persona_instruction, framework_name = await execute_adaptive_theoretician(client, work_input, lens_config, status, cache_name, theoretician_model)

            if not analytical_tasks or not persona_instruction:
                status.update(label="Analysis failed during Theoretician stage.", state="error")
                return None

            # v10.2: Package the strategy data using the framework_name from theoretician
            strategy_data = {
                "persona_instruction": persona_instruction,
                "analytical_tasks": analytical_tasks,
                "framework_name": framework_name  # Now using the actual framework name from theoretician
            }

            # v10.2: Display strategy in the provided container (gives user something to read during swarm execution)
            if strategy_container:
                with strategy_container:
                    framework_name = strategy_data['framework_name']
                    with st.expander(f"📋 {framework_name}", expanded=False):
                        st.markdown(f"**Persona Instruction:**")
                        st.markdown(persona_instruction)
                        st.markdown(f"**Analytical Tasks:** ({len(analytical_tasks)} tasks)")
                        for i, task in enumerate(analytical_tasks, 1):
                            st.markdown(f"{i}. {task}")

            # --- STAGE 3: SPECIALIST SWARM ---
            status.write("Phase 3: Specialist Swarm (Executing Parallel Tasks)...")

            # Determine model selection message and model based on mode
            # v10.3: Deep Dive now uses Flash-Lite specialists for cost efficiency
            status.write("Swarm using Gemini Flash-Lite.")
            specialist_model = MODEL_FLASH

            # Create async tasks for the swarm with appropriate model
            swarm_tasks = [
                execute_specialist(client, work_input, task, status, cache_name, specialist_model)
                for task in analytical_tasks
            ]
            
            # Execute concurrently
            specialist_reports = await asyncio.gather(*swarm_tasks)
            status.write("Swarm execution complete.")

            # --- STAGE 4: SYNTHESIS ---
            # v10.3: Single-stage synthesis for all modes (reverted from two-stage)
            if surface_scrape_mode:
                status.write("Synthesizer using Gemini Flash-Lite.")
            else: # Adaptive or Deep Dive
                status.write("Synthesizer using Gemini Pro.")

            final_analysis = await execute_master_synthesizer(client, work_input, lens_config, persona_instruction, specialist_reports, status, stream_container)

            if final_analysis:
                status.update(label="Analysis pipeline complete!", state="complete")
                # Return both the final analysis and the generated strategy data
                return final_analysis, strategy_data
            else:
                status.update(label="Analysis failed during Synthesis stage.", state="error")
                return None, None

        except Exception as e:
            st.error("A critical error occurred during analysis. Please check your inputs and try again.")
            with st.expander("🔍 Technical Details"):
                st.code(str(e))
            logging.error(f"Pipeline error: {e}", exc_info=True)
            status.update(label="Analysis pipeline failed.", state="error")
            return None, None

# v10.0: REWRITTEN (Synchronous wrapper for the async pipeline)
def generate_analysis(lens_config: dict, work_input: WorkInput):
    """
    Synchronous wrapper for the async analysis pipeline.
    """
    # This function primarily exists to maintain compatibility with synchronous UI calls (e.g., Single Lens page)
    async def run_pipeline():
        # Call the main async function
        return await async_generate_analysis(lens_config, work_input)

    # Use the utility function to run the async task synchronously
    # run_async_tasks returns a list of results, we extract the first one.
    results = run_async_tasks([run_pipeline()])
    if results:
        # The result from run_pipeline is a tuple (final_analysis, strategy_data)
        return results[0]
    return None, None

# -----------------------------------------------------------------------------
# REFINEMENT LOOP
# -----------------------------------------------------------------------------

# v10.0: Updated Refinement Loop (Maintains functionality, ensures Pro model usage)
@retry_with_backoff(max_retries=3, base_delay=2)
def generate_refined_analysis(work_input: WorkInput, previous_analysis: str, refinement_instruction: str):
    """
    Refines a previous analysis based on user feedback.
    Refinement always uses the Pro model.
    """
    # v10.0: Internal Model Management
    api_key = st.session_state.get("api_key")
    if not api_key:
        st.error("API Key missing for refinement.")
        return None

    # Refinement always uses the Pro model.
    model = get_model(api_key, MODEL_PRO, json_mode=False)
    if not model:
        return None
    
    if not refinement_instruction or not previous_analysis:
        st.warning("Refinement instruction or previous analysis is missing.")
        return None

    content_input_refiner = []
    status_container = st.status("Executing Refinement Loop...", expanded=False)

    with status_container as status:
        try:
            # --- Step 0: Prepare Input Work (Upload if media) ---
            # Ensure the work is available for the Refiner (handles caching)
            if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
                if not upload_to_gemini(work_input):
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

            # v10.2: Accumulate metadata for Refinement
            accumulate_metadata(work_input, response_refiner)

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


# v10.2: Refinement function for comparative synthesis
@retry_with_backoff(max_retries=3, base_delay=2)
def generate_refined_comparative_synthesis(work_a: WorkInput, work_b: WorkInput, previous_synthesis: str, refinement_instruction: str):
    """
    Refines a previous comparative synthesis based on user feedback.
    Refinement always uses the Pro model.
    """
    # v10.2: Internal Model Management
    api_key = st.session_state.get("api_key")
    if not api_key:
        st.error("API Key missing for refinement.")
        return None

    # Refinement always uses the Pro model.
    model = get_model(api_key, MODEL_PRO, json_mode=False)
    if not model:
        return None

    if not refinement_instruction or not previous_synthesis:
        st.warning("Refinement instruction or previous synthesis is missing.")
        return None

    content_input_refiner = []
    status_container = st.status("Executing Refinement Loop...", expanded=False)

    with status_container as status:
        try:
            # --- Step 0: Prepare Input Works (Upload if media) ---
            # Ensure both works are available for the Refiner (handles caching)
            if work_a.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
                if not upload_to_gemini(work_a):
                    status.update(label="Refinement failed due to Work A upload error.", state="error")
                    return None

            if work_b.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
                if not upload_to_gemini(work_b):
                    status.update(label="Refinement failed due to Work B upload error.", state="error")
                    return None

            # --- Step 1: Construct the Refinement Prompt ---
            status.write("Phase 1: Analyzing instructions and previous synthesis...")

            refinement_prompt = textwrap.dedent(f"""
            {JANUS_DIRECTIVES}

            **Task:** You are the "Refiner". Your goal is to iteratively improve a previous comparative synthesis based on specific user instructions.

            **Context:**
            1. Work A:
               - Modality: {work_a.modality}
               - Title: {work_a.get_display_title()}
            2. Work B:
               - Modality: {work_b.modality}
               - Title: {work_b.get_display_title()}

            **Previous Comparative Synthesis:**
            <previous_synthesis>
            {previous_synthesis}
            </previous_synthesis>

            **Refinement Instruction (CRITICAL):**
            The user has requested the following refinement to the comparative synthesis:
            <instruction>
            {refinement_instruction}
            </instruction>

            **Instructions:**
            1. **Analyze the Instruction:** Understand the user's intent (e.g., emphasize structural differences, add more specific examples, change focus, address a missed comparison point).
            2. **Review Both Works and Previous Synthesis:** Evaluate how the previous synthesis compares the two works and where it needs modification according to the instruction.
            3. **Generate Revised Synthesis:** Create a complete, revised comparative synthesis that incorporates the refinement instruction seamlessly. This is NOT a delta or commentary on the previous synthesis; it is the new, improved synthesis replacing the old one.
            4. **Maintain Quality:** Ensure the revised synthesis remains profound, nuanced, and well-supported by evidence from both creative works. Maintain the original analytical lens unless the instruction explicitly asks to change it.

            Output the revised comparative synthesis immediately.
            """)

            # Prepare input package for the Refiner (Prompt + Both Works)
            content_input_refiner.append(refinement_prompt)

            # Add work A
            if work_a.modality == M_TEXT:
                content_input_refiner[0] += f"\n\n--- Work A (For Re-Analysis) ---\nTitle: {work_a.get_display_title()}\n\nWork:\n{work_a.data}"
            elif work_a.gemini_file_ref:
                content_input_refiner.append(work_a.gemini_file_ref)

            # Add work B
            if work_b.modality == M_TEXT:
                content_input_refiner[0] += f"\n\n--- Work B (For Re-Analysis) ---\nTitle: {work_b.get_display_title()}\n\nWork:\n{work_b.data}"
            elif work_b.gemini_file_ref:
                content_input_refiner.append(work_b.gemini_file_ref)

            # --- Step 2: Execute Refinement ---
            status.write("Phase 2: Generating revised comparative synthesis...")

            # Execute the Refiner API call
            response_refiner = model.generate_content(content_input_refiner, request_options={"timeout": 900})

            # v10.2: Accumulate metadata for Comparative Refinement (to both works)
            accumulate_metadata(work_a, response_refiner)
            accumulate_metadata(work_b, response_refiner)

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


# v10.0: New Centralized Pipeline Runner
# v10.2: Added stream_container for synthesis streaming
def run_analysis_pipeline(
    work_input: WorkInput,
    manual_configs: list,
    smart_select_count: int,
    page_key_prefix: str,
    stream_container=None,
    strategy_container=None
):
    """
    A centralized function to run the entire analysis pipeline for any page.
    Handles validation, concurrent execution, and state management.

    Args:
        work_input: The WorkInput object.
        manual_configs: A list of lens_config dicts (from manual selection or smart selection).
        smart_select_count: The number of lenses required.
        page_key_prefix: A unique prefix for session state keys (e.g., 'single', 'dialectic').
        stream_container: Optional Streamlit container for streaming synthesis output.
        strategy_container: Optional Streamlit container for displaying strategies during execution.

    Returns:
        A tuple of (synthesis_result, raw_analyses, strategies) or (None, None, None) on failure.
    """
    api_key = st.session_state.get("api_key")

    # --- 1. Validation ---
    if not api_key:
        st.error("API Key is not configured. Please enter it on the Home page.")
        return None, None, None
    if not work_input.is_ready():
        st.warning("Please provide the creative work to be analyzed.")
        return None, None, None

    final_execution_configs = []

    # --- 2. Determine Execution Configs (Smart vs. Manual) ---
    if not manual_configs and smart_select_count > 0:
        # Smart Selection: Call analyst_in_chief to select lenses
        client = get_client(api_key)
        if not client:
            st.error("Could not initialize API client for smart selection.")
            return None, None, None

        with st.status("Running Smart Selection...", expanded=True) as smart_status:
            selected_lenses = analyst_in_chief(client, work_input, smart_select_count, smart_status)
            if not selected_lenses:
                st.error("Smart Selection failed. Please try manual selection.")
                return None, None, None

            # Convert lens names to config dicts
            final_execution_configs = [
                {'lens': lens_name, 'persona': None, 'is_zeitgeist': False}
                for lens_name in selected_lenses
            ]
    else:
        # Manual selection: use provided configs
        final_execution_configs = manual_configs

    if not final_execution_configs or len(final_execution_configs) < smart_select_count:
        st.warning(f"Configuration is incomplete. Please select at least {smart_select_count} perspective(s).")
        return None, None, None

    # --- 3. Context Caching Setup (for multi-lens optimization) ---
    # v10.2: Create context cache for media files when running multiple analyses
    use_cache = False
    num_tasks = len(final_execution_configs)

    # Check if cache needs to be invalidated due to mode change
    current_analysis_mode = st.session_state.get("analysis_mode", MODE_ADAPTIVE)
    if invalidate_cache_if_mode_changed(work_input, current_analysis_mode, api_key):
        st.info("Cache invalidated due to analysis mode change. A new cache will be created.")

    if num_tasks > 1:  # Only cache for multi-lens
        if work_input.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
            with st.status("Preparing context cache for multi-lens analysis...", expanded=False) as cache_status:
                try:
                    client = get_client(api_key)
                    if client:
                        # Upload file first if not already uploaded
                        if not work_input.gemini_file_ref:
                            if not run_async_tasks([upload_to_gemini_async(work_input, cache_status)])[0]:
                                cache_status.update(label="File upload failed", state="error")
                            else:
                                cache_status.write("File uploaded successfully")

                        # Create cache with appropriate model based on analysis mode
                        if work_input.gemini_file_ref:
                            # Determine cache model based on analysis mode
                            analysis_mode = st.session_state.get("analysis_mode", MODE_ADAPTIVE)
                            cache_model = MODEL_PRO if analysis_mode == MODE_DEEP_DIVE else MODEL_FLASH

                            cache_result = run_async_tasks([
                                create_context_cache_async(client, work_input, cache_model, cache_status, analysis_mode=analysis_mode)
                            ])[0]
                            if cache_result:
                                use_cache = True
                                cache_status.update(label="Context cache created successfully", state="complete")
                            else:
                                cache_status.update(label="Cache creation skipped (will proceed without caching)", state="complete")
                except Exception as e:
                    logging.warning(f"Cache setup failed: {e}. Proceeding without cache.")
                    cache_status.update(label="Cache creation failed (proceeding without cache)", state="complete")

    # --- 4. Run Concurrent Analyses ---
    analysis_label = "analysis" if num_tasks == 1 else "concurrent analyses"
    st.subheader(f"⚙️ Executing Swarm ({num_tasks} {analysis_label})")

    # v10.2: Pass strategy_container so strategies display during execution
    # Pass stream_container only for single-lens analysis (not multi-lens, which has separate synthesis)
    single_lens = (len(final_execution_configs) == 1)
    tasks = [async_generate_analysis(config, work_input, use_cache=use_cache, strategy_container=strategy_container, stream_container=stream_container if single_lens else None) for config in final_execution_configs]
    results = run_async_tasks(tasks) # Returns list of (analysis_text, strategy_data) tuples

    # --- 5. Process Results ---
    successful_analyses = [] # List of (config, analysis_text)
    strategies = []
    for i, res in enumerate(results):
        if res and res[0]: # Check if analysis_text is not None
            analysis_text, strategy_data = res
            successful_analyses.append((final_execution_configs[i], analysis_text))
            strategies.append(strategy_data)
        else:
            # Log or notify about the failed analysis
            failed_lens = final_execution_configs[i].get('lens', 'Unknown')
            logging.warning(f"Analysis failed for lens: {failed_lens}")

    if not successful_analyses:
        st.error("All analyses failed. Cannot proceed.")
        return None, None, None

    # --- 6. Synthesize Results ---
    # For single lens, the "synthesis" is just the analysis itself.
    if len(successful_analyses) == 1:
        synthesis_result = successful_analyses[0][1] # The analysis text
        return synthesis_result, successful_analyses, strategies

    # v10.2: Removed "Step 2/2" header - synthesis header now displayed on page
    client = get_client(api_key)
    if not client:
        return None, None, None

    # v10.2: Use streaming synthesis if container provided, otherwise use spinner
    if stream_container:
        if page_key_prefix == 'dialectic':
            synthesis_result = generate_dialectical_synthesis(client, successful_analyses[0][0], successful_analyses[0][1], successful_analyses[1][0], successful_analyses[1][1], work_input.get_display_title(), work_input, stream_container)
        elif page_key_prefix == 'symposium':
            synthesis_result = generate_symposium_synthesis(client, successful_analyses, work_input.get_display_title(), work_input, stream_container)
        else: # Add other synthesis types here if needed
            synthesis_result = "Synthesis type not implemented for this page."
    else:
        with st.spinner("Generating synthesis..."):
            if page_key_prefix == 'dialectic':
                synthesis_result = generate_dialectical_synthesis(client, successful_analyses[0][0], successful_analyses[0][1], successful_analyses[1][0], successful_analyses[1][1], work_input.get_display_title(), work_input)
            elif page_key_prefix == 'symposium':
                synthesis_result = generate_symposium_synthesis(client, successful_analyses, work_input.get_display_title(), work_input)
            else: # Add other synthesis types here if needed
                synthesis_result = "Synthesis type not implemented for this page."

    return synthesis_result, successful_analyses, strategies

# v10.0.6: New helper for Comparative Rigor
async def run_comparative_triage(client, work_a: WorkInput, work_b: WorkInput, status_container):
    # v10.1: Migrated to google-genai SDK - now accepts client instead of model
    """
    Runs Triage on two works concurrently and returns the highest complexity level.
    Ensures both works are analyzed with the same rigor.
    """
    status_container.write("Phase 1: Comparative Triage (Assessing Complexity for Rigor)...")
    
    triage_tasks = [
        execute_triage_analyst(client, work_a, status_container),
        execute_triage_analyst(client, work_b, status_container)
    ]
    
    results = await asyncio.gather(*triage_tasks)
    complexity_a, complexity_b = results

    # If either analysis is deemed complex, the entire comparison must be run at high rigor.
    if 'Complex' in (complexity_a, complexity_b):
        status_container.update(label="Comparative Triage complete. Rigor level: Complex.", state="complete")
        return 'Complex'

    status_container.update(label="Comparative Triage complete. Rigor level: Simple.", state="complete")
    return 'Simple'

# v10.0: New Centralized Pipeline Runner for Comparative Analysis
def run_comparative_analysis_pipeline(
    work_a: WorkInput,
    work_b: WorkInput,
    selection_method: str,
    manual_lens_config: dict,
    strategy_container=None
):
    """
    A centralized function to run the comparative analysis pipeline.
    Handles validation, concurrent execution of two works with one lens, and synthesis.

    Args:
        selection_method: 'Manual Selection' or 'Smart Selection'.
        work_a: The first WorkInput object.
        work_b: The second WorkInput object.
        manual_lens_config: The single lens_config dict to apply to both works.
        strategy_container: Optional Streamlit container for displaying strategies during execution.

    Returns:
        A tuple of (synthesis_result, analysis_a, analysis_b, strategy_a, strategy_b) or (None, None, None, None, None) on failure.
    """
    api_key = st.session_state.get("api_key")

    # --- 1. Validation ---
    if not api_key:
        st.error("API Key is not configured. Please enter it on the Home page.")
        return None, None, None, None, None
    if not work_a.is_ready():
        st.warning("Please provide the first creative work (Work A).")
        return None, None, None, None, None
    if not work_b.is_ready():
        st.warning("Please provide the second creative work (Work B).")
        return None, None, None, None, None

    # --- 2. Determine Execution Config (Smart vs. Manual) ---
    final_lens_config = None
    if selection_method == SELECT_SMART:
        client = get_client(api_key)
        if not client:
            return None, None, None, None, None

        with st.status("Executing Smart Selection...", expanded=False) as status:
            smart_lens = comparative_strategist(client, work_a, work_b, status)

        if smart_lens:
            final_lens_config = {'lens': smart_lens, 'persona': None, 'is_zeitgeist': False}
        else:
            st.error("Smart Selection failed to return a valid lens.")
            return None, None, None, None, None
    else: # Manual Selection
        final_lens_config = manual_lens_config


    # --- 3. Enforce Comparative Rigor (v10.0.6) ---
    # In comparative mode, both analyses must run at the same complexity level
    # to ensure a fair comparison. We triage both and take the highest complexity.
    enforced_complexity = None
    analysis_mode = st.session_state.get("analysis_mode", MODE_ADAPTIVE) # Default to Adaptive
    if analysis_mode == MODE_ADAPTIVE:
        # Max Depth mode skips triage entirely, so we only run this for Adaptive mode.
        client = get_client(api_key)
        if not client:
            return None, None, None, None, None

        # This is an async function, so we need to wrap it to run it here.
        async def get_rigor_level():
            return await run_comparative_triage(client, work_a, work_b, st.status("Enforcing Comparative Rigor...", expanded=False))

        # run_async_tasks returns a list, so we get the first element.
        enforced_complexity = run_async_tasks([get_rigor_level()])[0]
        if not enforced_complexity:
            st.error("Failed to determine comparative rigor level.")
            return None, None, None, None, None


    # --- 4. Context Caching Setup (for comparative analysis optimization) ---
    # v10.2: Create context caches for both media files
    use_cache_a = False
    use_cache_b = False

    # Check if caches need to be invalidated due to mode change
    current_analysis_mode = st.session_state.get("analysis_mode", MODE_ADAPTIVE)
    invalidated_a = invalidate_cache_if_mode_changed(work_a, current_analysis_mode, api_key)
    invalidated_b = invalidate_cache_if_mode_changed(work_b, current_analysis_mode, api_key)
    if invalidated_a or invalidated_b:
        st.info("Cache(s) invalidated due to analysis mode change. New caches will be created.")

    # Cache for Work A
    if work_a.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
        with st.status("Preparing context cache for Work A...", expanded=False) as cache_status_a:
            try:
                client = get_client(api_key)
                if client:
                    # Upload file first if not already uploaded
                    if not work_a.gemini_file_ref:
                        if not run_async_tasks([upload_to_gemini_async(work_a, cache_status_a)])[0]:
                            cache_status_a.update(label="File upload failed for Work A", state="error")
                        else:
                            cache_status_a.write("File uploaded successfully")

                    # Create cache with appropriate model based on analysis mode
                    if work_a.gemini_file_ref:
                        # Determine cache model based on analysis mode
                        analysis_mode = st.session_state.get("analysis_mode", MODE_ADAPTIVE)
                        cache_model = MODEL_PRO if analysis_mode == MODE_DEEP_DIVE else MODEL_FLASH

                        cache_result = run_async_tasks([
                            create_context_cache_async(client, work_a, cache_model, cache_status_a, analysis_mode=analysis_mode)
                        ])[0]
                        if cache_result:
                            use_cache_a = True
                            cache_status_a.update(label="Context cache created for Work A", state="complete")
                        else:
                            cache_status_a.update(label="Cache creation skipped for Work A", state="complete")
            except Exception as e:
                logging.warning(f"Cache setup failed for Work A: {e}")
                cache_status_a.update(label="Cache creation failed for Work A (proceeding without cache)", state="complete")

    # Cache for Work B
    if work_b.modality in [M_IMAGE, M_AUDIO, M_VIDEO]:
        with st.status("Preparing context cache for Work B...", expanded=False) as cache_status_b:
            try:
                client = get_client(api_key)
                if client:
                    # Upload file first if not already uploaded
                    if not work_b.gemini_file_ref:
                        if not run_async_tasks([upload_to_gemini_async(work_b, cache_status_b)])[0]:
                            cache_status_b.update(label="File upload failed for Work B", state="error")
                        else:
                            cache_status_b.write("File uploaded successfully")

                    # Create cache with appropriate model based on analysis mode
                    if work_b.gemini_file_ref:
                        # Determine cache model based on analysis mode
                        analysis_mode = st.session_state.get("analysis_mode", MODE_ADAPTIVE)
                        cache_model = MODEL_PRO if analysis_mode == MODE_DEEP_DIVE else MODEL_FLASH

                        cache_result = run_async_tasks([
                            create_context_cache_async(client, work_b, cache_model, cache_status_b, analysis_mode=analysis_mode)
                        ])[0]
                        if cache_result:
                            use_cache_b = True
                            cache_status_b.update(label="Context cache created for Work B", state="complete")
                        else:
                            cache_status_b.update(label="Cache creation skipped for Work B", state="complete")
            except Exception as e:
                logging.warning(f"Cache setup failed for Work B: {e}")
                cache_status_b.update(label="Cache creation failed for Work B (proceeding without cache)", state="complete")

    # --- 5. Run Concurrent Analyses ---
    st.subheader(f"Step 1/2: Analyzing Work A and Work B concurrently...")

    tasks = [
        async_generate_analysis(final_lens_config, work_a, enforced_complexity=enforced_complexity, use_cache=use_cache_a, strategy_container=strategy_container),
        async_generate_analysis(final_lens_config, work_b, enforced_complexity=enforced_complexity, use_cache=use_cache_b, strategy_container=strategy_container)
    ]
    results = run_async_tasks(tasks)

    # v10.2: Unpack results, capturing both analysis text and strategy data
    analysis_a_text, strategy_a = results[0] if results and results[0] else (None, None)
    analysis_b_text, strategy_b = results[1] if results and results[1] else (None, None)

    if not analysis_a_text or not analysis_b_text:
        st.error("One or both of the initial analyses failed. Cannot proceed to comparison.")
        return None, None, None, None, None

    # --- 5. Synthesize Results ---
    st.subheader("Step 2/2: Comparative Synthesis")
    client = get_client(api_key)
    if not client:
        return None, None, None, None, None

    st.info(f"**Synthesizing Comparison Between:** '{work_a.get_display_title()}' **and** '{work_b.get_display_title()}'")
    with st.spinner("Generating comparative synthesis..."):
        synthesis_result = generate_comparative_synthesis(client, final_lens_config, analysis_a_text, work_a.get_display_title(), analysis_b_text, work_b.get_display_title(), work_a, work_b)

    return synthesis_result, analysis_a_text, analysis_b_text, strategy_a, strategy_b


# --- SYNTHESIS FUNCTIONS ---

@retry_with_backoff(max_retries=3, base_delay=2)
def generate_dialectical_synthesis(client, data_a, analysis_a, data_b, analysis_b, work_title, work_input, stream_container=None):
    # v10.1: Migrated to google-genai SDK - now accepts client instead of model
    # v9.4b: Updated to handle the new is_zeitgeist flag instead of checking lens name.
    # v10.2: Added retry logic with exponential backoff
    # v10.2: Added streaming support via optional stream_container
    # v10.2: Added work_input parameter for metadata tracking
    """
    Synthesizes two analyses of the SAME work into a dialectical dialogue.

    Args:
        work_input: WorkInput object for metadata tracking
        stream_container: Optional Streamlit container for streaming output. If provided, text streams in real-time.
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
        # v10.2: Use streaming if container provided
        if stream_container:
            # Streaming mode - text appears word-by-word
            full_text = ""
            placeholder = stream_container.empty()

            for chunk in client.models.generate_content_stream(
                model=MODEL_PRO,
                contents=synthesis_prompt
            ):
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text)

            # v10.2: Accumulate metadata from final chunk
            if hasattr(chunk, 'usage_metadata'):
                # Create a pseudo-response object for metadata accumulation
                class StreamResponse:
                    def __init__(self, usage_metadata, text):
                        self.usage_metadata = usage_metadata
                        self.text = text
                accumulate_metadata(work_input, StreamResponse(chunk.usage_metadata, full_text))

            return full_text
        else:
            # Non-streaming mode (backward compatible)
            response = client.models.generate_content(
                model=MODEL_PRO,
                contents=synthesis_prompt
            )
            # v10.2: Accumulate metadata for synthesis
            accumulate_metadata(work_input, response)
            return response.text
    except google_exceptions.ResourceExhausted:
        st.error("⏱️ **Rate Limit Reached** - You've made too many requests in a short time. Please wait 1-2 minutes and try again, or check your Google Cloud quota.")
        return None
    except Exception as e:
        st.error(f"An error occurred during dialectical synthesis: {e}")
        return None

# v9.4b: Updated signature and implementation for Symposium.
@retry_with_backoff(max_retries=3, base_delay=2)
def generate_symposium_synthesis(client, analyses_results, work_title, work_input, stream_container=None):
    # v10.1: Migrated to google-genai SDK - now accepts client instead of model
    # v9.4b: Updated to handle the new is_zeitgeist flag and the structure of analyses_results.
    # v10.2: Added streaming support via optional stream_container
    # v10.2: Added work_input parameter for metadata tracking
    """
    Synthesizes multiple analyses (3+) into a multi-perspective symposium dialogue.

    Args:
        work_input: WorkInput object for metadata tracking
        stream_container: Optional Streamlit container for streaming output. If provided, text streams in real-time.
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
        # v10.2: Use streaming if container provided
        if stream_container:
            # Streaming mode - text appears word-by-word
            full_text = ""
            placeholder = stream_container.empty()

            for chunk in client.models.generate_content_stream(
                model=MODEL_PRO,
                contents=synthesis_prompt
            ):
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text)

            # v10.2: Accumulate metadata from final chunk
            if hasattr(chunk, 'usage_metadata'):
                # Create a pseudo-response object for metadata accumulation
                class StreamResponse:
                    def __init__(self, usage_metadata, text):
                        self.usage_metadata = usage_metadata
                        self.text = text
                accumulate_metadata(work_input, StreamResponse(chunk.usage_metadata, full_text))

            return full_text
        else:
            # Non-streaming mode (backward compatible)
            response = client.models.generate_content(
                model=MODEL_PRO,
                contents=synthesis_prompt
            )
            # v10.2: Accumulate metadata for synthesis
            accumulate_metadata(work_input, response)
            return response.text
    except google_exceptions.ResourceExhausted:
        st.error("⏱️ **Rate Limit Reached** - You've made too many requests in a short time. Please wait 1-2 minutes and try again, or check your Google Cloud quota.")
        return None
    except Exception as e:
        st.error(f"An error occurred during symposium synthesis: {e}")
        return None


@retry_with_backoff(max_retries=3, base_delay=2)
def generate_comparative_synthesis(client, lens_config, analysis_a, work_a_title, analysis_b, work_b_title, work_a, work_b):
    # v10.1: Migrated to google-genai SDK - now accepts client instead of model
    # v9.4b: Updated to accept lens_config instead of just lens_name.
    # v10.2: Added work_a and work_b parameters for metadata tracking
    # v10.2: Added retry logic with exponential backoff
    """Synthesizes two analyses of DIFFERENT works using the SAME lens/configuration."""

    # v9.4b: Determine the display name for the comparison
    if lens_config.get('is_zeitgeist', False):
        comparison_framework = "Zeitgeist Simulation (Common Context)"
    else:
        # Display the UI name here for the user's context
        comparison_framework = lens_config.get('lens')

    # The Comparative Synthesis Prompt
    synthesis_prompt = textwrap.dedent(f"""
    You are tasked with generating a "Comparative Synthesis". You will compare and contrast two different creative works that have been analyzed through the same analytical framework: **{comparison_framework}**.

    IMPORTANT: The analyses below are generated by the Janus analytical engine. If they adopt specific personas or voices (e.g., writing "as" a historical figure), treat these as stylistic choices made BY JANUS, not as analyses written BY those historical figures. Your synthesis should discuss what JANUS discovered about each work through this framework, not what the persona figures themselves said.

    Work A: {work_a_title}
    <analysis_a>
    {analysis_a}
    </analysis_a>

    Work B: {work_b_title}
    <analysis_b>
    {analysis_b}
    </analysis_b>

    Instructions:
    1. **Identify Key Themes:** Based on the provided analyses, identify the central themes, findings, or arguments that emerged for each work under the {comparison_framework} framework.
    2. **Dissonance and Resonance:** Analyze the points of contrast (dissonance) and similarity (resonance) between Work A and Work B. How does applying the same framework reveal different aspects of each work?
    3. **Emergent Insights:** Discuss what new understanding emerges from the comparison itself. How does seeing these two works side-by-side deepen the interpretation of both?
    4. **Structure:** Format your response as a cohesive essay with clear sections for comparison, contrast, and synthesis.
    5. **Attribution:** When discussing the analyses, refer to them as "the analysis of Work A" and "the analysis of Work B" rather than attributing them to persona figures who may have been adopted stylistically.
    """)

    try:
        response = client.models.generate_content(
            model=MODEL_PRO,
            contents=synthesis_prompt
        )
        # v10.2: Accumulate metadata for synthesis (both works)
        accumulate_metadata(work_a, response)
        accumulate_metadata(work_b, response)
        return response.text
    except google_exceptions.ResourceExhausted:
        st.error("⏱️ **Rate Limit Reached** - You've made too many requests in a short time. Please wait 1-2 minutes and try again, or check your Google Cloud quota.")
        return None
    except Exception as e:
        st.error(f"An error occurred during comparative synthesis: {e}")
        return None

# --- UI HELPER FUNCTIONS ---

def run_async_tasks(tasks):
    """
    Runs a list of asyncio tasks and returns the results.
    Uses asyncio.run() which is the modern Python 3.7+ approach.
    """
    async def run_all():
        return await asyncio.gather(*tasks)

    return asyncio.run(run_all())

# v10.0.15: Centralized state reset function
def reset_page_state(page_prefix: str):
    """
    A centralized function to reset the analysis state for any given page.
    
    Args:
        page_prefix (str): The prefix for the session state keys (e.g., 'single_lens', 'dialectical').
    """
    st.session_state[f'{page_prefix}_state'] = 'config'
    st.session_state[f'{page_prefix}_result'] = None
    
    # Reset optional states if they exist
    if f'{page_prefix}_raw_analyses' in st.session_state:
        st.session_state[f'{page_prefix}_raw_analyses'] = None
    if f'{page_prefix}_strategies' in st.session_state:
        st.session_state[f'{page_prefix}_strategies'] = None
    if 'refinement_instruction' in st.session_state:
        st.session_state.refinement_instruction = ""

    # Reset configuration confirmation flag
    if f'{page_prefix}_config_confirmed' in st.session_state:
        st.session_state[f'{page_prefix}_config_confirmed'] = False

    # Cleanup cached Gemini files associated with the page's WorkInput
    if page_prefix == 'comparative':
        # Comparative has two WorkInput objects
        if 'work_input_comparative_a' in st.session_state:
            st.session_state.work_input_comparative_a.cleanup_gemini_file()
        if 'work_input_comparative_b' in st.session_state:
            st.session_state.work_input_comparative_b.cleanup_gemini_file()
    else:
        # Other pages have single WorkInput
        work_input_key = f'work_input_{page_prefix.split("_")[0]}' # e.g., 'work_input_single'
        if work_input_key in st.session_state:
            st.session_state[work_input_key].cleanup_gemini_file()

def handle_input_ui(work_input: WorkInput, container, ui_key_prefix, on_change_callback=None):
    # (Implementation remains the same as v9.4a)
    """
    Renders input fields based on modality. Modifies the WorkInput object in place.
    """
    with container:
        # Title is metadata - changing it should not reset analysis or invalidate uploaded files
        work_input.title = st.text_input("Title (Optional):", key=f"{ui_key_prefix}_title", value=work_input.title)
        
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
            # v10.0.29: Revert to a stable st.text_area. The AI is instructed to treat content as pre-formatted.
            work_text = st.text_area(
                "Paste text or description:", height=250, key=f"{ui_key_prefix}_text", 
                value=work_input.data or "", on_change=on_change_callback
            )

            if work_text:
                work_input.data = work_text

        elif work_input.modality == M_IMAGE:
            uploaded_file = st.file_uploader("Upload Image (JPG, PNG, WEBP, HEIC, HEIF):", type=["jpg", "jpeg", "png", "webp", "heic", "heif"], key=f"{ui_key_prefix}_image", on_change=on_change_callback)

            # Show status if file was previously uploaded but widget has reset
            if uploaded_file is None and work_input.gemini_file_ref is not None:
                st.success(f"✓ Image '{work_input.uploaded_file_name}' ready for analysis")

            if uploaded_file is not None:
                # Check if this is a genuinely new file (compare by metadata to avoid re-upload loop)
                file_changed = (
                    work_input.uploaded_file_name != uploaded_file.name or
                    work_input.uploaded_file_size != uploaded_file.size
                )

                if file_changed:
                    # Clean up old file from Gemini if one exists
                    if work_input.gemini_file_ref is not None:
                        work_input.cleanup_gemini_file()

                    work_input.uploaded_file_obj = uploaded_file
                    work_input.uploaded_file_name = uploaded_file.name
                    work_input.uploaded_file_size = uploaded_file.size
                    # gemini_file_ref already cleared by cleanup_gemini_file() or was None
                elif work_input.uploaded_file_obj is None:
                    # File hasn't changed but uploaded_file_obj was freed - restore it
                    work_input.uploaded_file_obj = uploaded_file

                # PROACTIVE UPLOAD: Upload to Gemini if not already uploaded
                if work_input.gemini_file_ref is None and work_input.uploaded_file_obj is not None:
                    upload_placeholder = st.empty()
                    try:
                        with upload_placeholder.container():
                            with st.spinner("Uploading image to Gemini..."):
                                upload_result = upload_to_gemini(work_input)
                        if upload_result:
                            upload_placeholder.success("✓ Image ready for analysis")
                        else:
                            upload_placeholder.warning("Upload will be retried on execution")
                    except Exception as e:
                        upload_placeholder.warning("Upload will be retried when you execute analysis")
                        logging.warning(f"Proactive upload failed: {e}")

                try:
                    # Display thumbnail preview with option for full size
                    st.image(uploaded_file, caption="Preview", width=300)
                    with st.expander("🔍 View Full Size"):
                        st.image(uploaded_file, use_container_width=True)
                except Exception as e:
                    st.error(f"Error processing image: {e}")
                    work_input.uploaded_file_obj = None

        elif work_input.modality == M_AUDIO:
            uploaded_file = st.file_uploader("Upload Audio (MP3, WAV, FLAC, M4A, OGG, MP4 audio):", type=["mp3", "wav", "flac", "m4a", "ogg", "mp4"], key=f"{ui_key_prefix}_audio", on_change=on_change_callback)

            # Show status if file was previously uploaded but widget has reset
            if uploaded_file is None and work_input.gemini_file_ref is not None:
                st.success(f"✓ Audio '{work_input.uploaded_file_name}' ready for analysis")

            if uploaded_file is not None:
                # Check if this is a genuinely new file (compare by metadata to avoid re-upload loop)
                file_changed = (
                    work_input.uploaded_file_name != uploaded_file.name or
                    work_input.uploaded_file_size != uploaded_file.size
                )

                if file_changed:
                    # Clean up old file from Gemini if one exists
                    if work_input.gemini_file_ref is not None:
                        work_input.cleanup_gemini_file()

                    work_input.uploaded_file_obj = uploaded_file
                    work_input.uploaded_file_name = uploaded_file.name
                    work_input.uploaded_file_size = uploaded_file.size
                    # gemini_file_ref already cleared by cleanup_gemini_file() or was None
                elif work_input.uploaded_file_obj is None:
                    # File hasn't changed but uploaded_file_obj was freed - restore it
                    work_input.uploaded_file_obj = uploaded_file

                # PROACTIVE UPLOAD: Upload to Gemini if not already uploaded
                if work_input.gemini_file_ref is None and work_input.uploaded_file_obj is not None:
                    upload_placeholder = st.empty()
                    try:
                        with upload_placeholder.container():
                            with st.spinner("Uploading audio to Gemini..."):
                                upload_result = upload_to_gemini(work_input)
                        if upload_result:
                            upload_placeholder.success("✓ Audio ready for analysis")
                        else:
                            upload_placeholder.warning("Upload will be retried on execution")
                    except Exception as e:
                        upload_placeholder.warning("Upload will be retried when you execute analysis")
                        logging.warning(f"Proactive upload failed: {e}")

                # Display audio player (use local variable, not work_input.uploaded_file_obj)
                st.audio(uploaded_file)

        elif work_input.modality == M_VIDEO:
            uploaded_file = st.file_uploader("Upload Video (MP4, MOV, AVI, WEBM):", type=["mp4", "mov", "avi", "webm"], key=f"{ui_key_prefix}_video", on_change=on_change_callback)

            # Show status if file was previously uploaded but widget has reset
            if uploaded_file is None and work_input.gemini_file_ref is not None:
                st.success(f"✓ Video '{work_input.uploaded_file_name}' ready for analysis")

            if uploaded_file is not None:
                # Check if this is a genuinely new file (compare by metadata to avoid re-upload loop)
                file_changed = (
                    work_input.uploaded_file_name != uploaded_file.name or
                    work_input.uploaded_file_size != uploaded_file.size
                )

                if file_changed:
                    # Clean up old file from Gemini if one exists
                    if work_input.gemini_file_ref is not None:
                        work_input.cleanup_gemini_file()

                    work_input.uploaded_file_obj = uploaded_file
                    work_input.uploaded_file_name = uploaded_file.name
                    work_input.uploaded_file_size = uploaded_file.size
                    # gemini_file_ref already cleared by cleanup_gemini_file() or was None
                elif work_input.uploaded_file_obj is None:
                    # File hasn't changed but uploaded_file_obj was freed - restore it
                    work_input.uploaded_file_obj = uploaded_file

                # PROACTIVE UPLOAD: Upload to Gemini if not already uploaded
                if work_input.gemini_file_ref is None and work_input.uploaded_file_obj is not None:
                    upload_placeholder = st.empty()
                    try:
                        with upload_placeholder.container():
                            with st.spinner("Uploading video to Gemini..."):
                                upload_result = upload_to_gemini(work_input)
                        if upload_result:
                            upload_placeholder.success("✓ Video ready for analysis")
                        else:
                            upload_placeholder.warning("Upload will be retried on execution")
                    except Exception as e:
                        upload_placeholder.warning("Upload will be retried when you execute analysis")
                        logging.warning(f"Proactive upload failed: {e}")

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
                    key=f"{ui_key_prefix}_vmode"
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

def get_all_entries():
    """
    Build a unified entry database containing all 5 types for the Library's wiki-style system.

    Returns:
        list: A comprehensive list of entry dictionaries with structure:
        {
            'type': 'lens' | 'persona' | 'discipline' | 'function' | 'era',
            'name': str,
            'icon': '📖' | '🎭' | '🏛️' | '⚙️' | '📅',
            'description': str,
            'related': {
                'disciplines': list,
                'functions': list,
                'eras': list,
                'personas': list,
                'lenses': list
            },
            'tags': set  # For search functionality - all related names
        }
    """
    from lenses import (
        SORTED_LENS_NAMES, LENSES_HIERARCHY, LENSES_FUNCTIONAL,
        LENSES_BY_ERA, PERSONA_POOL, PERSONA_METADATA, ERA_ORDER,
        get_lens_data
    )

    all_entries = []

    # ============================================================
    # 1. LENSES (📖)
    # ============================================================
    for lens_name in SORTED_LENS_NAMES:
        lens_data = get_lens_data(lens_name)
        if not lens_data:
            continue

        # Find related disciplines
        related_disciplines = [disc for disc, lenses in LENSES_HIERARCHY.items() if lens_name in lenses]

        # Find related functions
        related_functions = [func for func, lenses in LENSES_FUNCTIONAL.items() if lens_name in lenses]

        # Find related eras
        related_eras = lens_data.get('eras', [])

        # Find related personas
        related_personas = PERSONA_POOL.get(lens_name, [])

        # Build tags for search (all related terms)
        tags = {lens_name.lower()}
        tags.update([d.lower() for d in related_disciplines])
        tags.update([f.lower() for f in related_functions])
        tags.update([e.lower() for e in related_eras])
        tags.update([p.lower() for p in related_personas])

        all_entries.append({
            'type': 'lens',
            'name': lens_name,
            'icon': '📖',
            'description': lens_data.get('description', 'No description available'),
            'related': {
                'disciplines': sorted(related_disciplines),
                'functions': sorted(related_functions),
                'eras': related_eras,  # Keep original order
                'personas': sorted(related_personas),
                'lenses': []  # Lenses don't relate to other lenses directly
            },
            'tags': tags
        })

    # ============================================================
    # 2. PERSONAS (🎭)
    # ============================================================
    for persona_name, metadata in PERSONA_METADATA.items():
        # Build description from persona's lenses
        persona_lenses = metadata.get('lenses', [])
        if len(persona_lenses) == 1:
            desc = f"Historical figure associated with {persona_lenses[0]}"
        else:
            desc = f"Historical figure associated with {len(persona_lenses)} analytical frameworks"

        # Get related attributes from metadata
        related_disciplines = sorted(list(metadata['disciplines']))
        related_functions = sorted(list(metadata['functions']))
        related_eras = sorted(list(metadata['eras']))
        related_lenses = sorted(persona_lenses)

        # Build tags for search
        tags = {persona_name.lower()}
        tags.update([d.lower() for d in related_disciplines])
        tags.update([f.lower() for f in related_functions])
        tags.update([e.lower() for e in related_eras])
        tags.update([l.lower() for l in related_lenses])

        all_entries.append({
            'type': 'persona',
            'name': persona_name,
            'icon': '🎭',
            'description': desc,
            'related': {
                'disciplines': related_disciplines,
                'functions': related_functions,
                'eras': related_eras,
                'personas': [],  # Personas don't relate to other personas directly
                'lenses': related_lenses
            },
            'tags': tags
        })

    # ============================================================
    # 3. DISCIPLINES (🏛️)
    # ============================================================
    for discipline_name, discipline_lenses in LENSES_HIERARCHY.items():
        # Build description
        lens_count = len(discipline_lenses)
        desc = f"Academic discipline containing {lens_count} analytical framework{'s' if lens_count != 1 else ''}"

        # Find all personas associated with this discipline's lenses
        related_personas = set()
        for lens_name in discipline_lenses:
            if lens_name in PERSONA_POOL:
                related_personas.update(PERSONA_POOL[lens_name])

        # Find all functions that contain any of this discipline's lenses
        related_functions = set()
        for func_name, func_lenses in LENSES_FUNCTIONAL.items():
            if any(lens in func_lenses for lens in discipline_lenses):
                related_functions.add(func_name)

        # Find all eras that contain any of this discipline's lenses
        related_eras = set()
        for era_name, era_lenses in LENSES_BY_ERA.items():
            if any(lens in era_lenses for lens in discipline_lenses):
                related_eras.add(era_name)

        # Build tags for search
        tags = {discipline_name.lower()}
        tags.update([l.lower() for l in discipline_lenses])
        tags.update([p.lower() for p in related_personas])

        all_entries.append({
            'type': 'discipline',
            'name': discipline_name,
            'icon': '🏛️',
            'description': desc,
            'related': {
                'disciplines': [],  # Disciplines don't relate to other disciplines directly
                'functions': sorted(list(related_functions)),
                'eras': [era for era in ERA_ORDER if era in related_eras],  # Maintain chronological order
                'personas': sorted(list(related_personas)),
                'lenses': sorted(discipline_lenses)
            },
            'tags': tags
        })

    # ============================================================
    # 4. FUNCTIONS (⚙️)
    # ============================================================
    for function_name, function_lenses in LENSES_FUNCTIONAL.items():
        # Build description based on tier
        tier_descriptions = {
            "Tier 1: Contextual (What/Who/When)": "Analytical frameworks focused on contextual grounding: historical setting, biographical context, and temporal factors",
            "Tier 2: Mechanical (How it Works)": "Analytical frameworks focused on structural analysis: formal properties, mechanisms, and systematic operations",
            "Tier 3: Interpretive (Why it Matters)": "Analytical frameworks focused on meaning-making: philosophical implications, cultural significance, and interpretive depth"
        }
        desc = tier_descriptions.get(function_name, f"Function tier containing {len(function_lenses)} analytical frameworks")

        # Find all personas associated with this function's lenses
        related_personas = set()
        for lens_name in function_lenses:
            if lens_name in PERSONA_POOL:
                related_personas.update(PERSONA_POOL[lens_name])

        # Find all disciplines that contain any of this function's lenses
        related_disciplines = set()
        for disc_name, disc_lenses in LENSES_HIERARCHY.items():
            if any(lens in disc_lenses for lens in function_lenses):
                related_disciplines.add(disc_name)

        # Find all eras that contain any of this function's lenses
        related_eras = set()
        for era_name, era_lenses in LENSES_BY_ERA.items():
            if any(lens in era_lenses for lens in function_lenses):
                related_eras.add(era_name)

        # Build tags for search
        tags = {function_name.lower()}
        tags.update([l.lower() for l in function_lenses])
        tags.update([p.lower() for p in related_personas])

        all_entries.append({
            'type': 'function',
            'name': function_name,
            'icon': '⚙️',
            'description': desc,
            'related': {
                'disciplines': sorted(list(related_disciplines)),
                'functions': [],  # Functions don't relate to other functions directly
                'eras': [era for era in ERA_ORDER if era in related_eras],  # Maintain chronological order
                'personas': sorted(list(related_personas)),
                'lenses': sorted(function_lenses)
            },
            'tags': tags
        })

    # ============================================================
    # 5. ERAS (📅)
    # ============================================================
    for era_name, era_lenses in LENSES_BY_ERA.items():
        # Build description from era name (already has date range)
        lens_count = len(era_lenses)
        desc = f"Historical period containing {lens_count} analytical framework{'s' if lens_count != 1 else ''}"

        # Find all personas associated with this era's lenses
        related_personas = set()
        for lens_name in era_lenses:
            if lens_name in PERSONA_POOL:
                related_personas.update(PERSONA_POOL[lens_name])

        # Find all disciplines that contain any of this era's lenses
        related_disciplines = set()
        for disc_name, disc_lenses in LENSES_HIERARCHY.items():
            if any(lens in disc_lenses for lens in era_lenses):
                related_disciplines.add(disc_name)

        # Find all functions that contain any of this era's lenses
        related_functions = set()
        for func_name, func_lenses in LENSES_FUNCTIONAL.items():
            if any(lens in func_lenses for lens in era_lenses):
                related_functions.add(func_name)

        # Build tags for search
        tags = {era_name.lower()}
        tags.update([l.lower() for l in era_lenses])
        tags.update([p.lower() for p in related_personas])

        all_entries.append({
            'type': 'era',
            'name': era_name,
            'icon': '📅',
            'description': desc,
            'related': {
                'disciplines': sorted(list(related_disciplines)),
                'functions': sorted(list(related_functions)),
                'eras': [],  # Eras don't relate to other eras directly
                'personas': sorted(list(related_personas)),
                'lenses': sorted(era_lenses)
            },
            'tags': tags
        })

    return all_entries

def search_library_entries(all_entries, search_query, selected_types=None):
    """
    Smart search across all library entries.

    Args:
        all_entries: List of entry dictionaries from get_all_entries()
        search_query: User's search string
        selected_types: List of entry types to include (e.g., ['lens', 'persona'])
                       If None, includes all types. If empty list, includes nothing.

    Returns:
        list: Filtered entries matching the search query and type filters
    """
    # If selected_types is an empty list, return nothing
    if selected_types is not None and len(selected_types) == 0:
        return []

    # If selected_types is None, treat as "all types selected"
    if selected_types is None:
        selected_types = ['lens', 'persona', 'discipline', 'function', 'era']

    filtered_entries = []
    query_lower = search_query.lower() if search_query else ""

    for entry in all_entries:
        # Apply type filter - only include if type is in selected_types
        if entry['type'] not in selected_types:
            continue

        # Apply search query (if provided)
        if search_query:
            # Search in name
            if query_lower in entry['name'].lower():
                filtered_entries.append(entry)
                continue

            # Search in description
            if query_lower in entry['description'].lower():
                filtered_entries.append(entry)
                continue

            # Search in tags (includes all related names)
            if any(query_lower in tag for tag in entry['tags']):
                filtered_entries.append(entry)
                continue
        else:
            # No search query, just apply type filter
            filtered_entries.append(entry)

    return filtered_entries

def get_cascading_filter_options(current_discipline, current_function, current_era, current_lens=None):
    """
    Calculate available filter options based on current selections (cascading filters).
    Each filter shows only values that will result in at least one available lens.

    Returns: (available_disciplines, available_functions, available_eras, filtered_lenses, updated_discipline, updated_function, updated_era)
    The updated values reflect lens reverse-lookup if a lens is selected.
    """
    from lenses import LENSES_HIERARCHY, LENSES_FUNCTIONAL, LENSES_BY_ERA, ERA_ORDER, SORTED_LENS_NAMES

    # If a lens is selected, reverse-lookup its attributes by checking which categories contain it
    updated_discipline = current_discipline
    updated_function = current_function
    updated_era = current_era

    if current_lens:
        # Find which discipline contains this lens
        for disc_name, lenses in LENSES_HIERARCHY.items():
            if current_lens in lenses:
                updated_discipline = disc_name
                break

        # Find which function contains this lens
        for func_name, lenses in LENSES_FUNCTIONAL.items():
            if current_lens in lenses:
                updated_function = func_name
                break

        # Find which era contains this lens
        for era_name, lenses in LENSES_BY_ERA.items():
            if current_lens in lenses:
                updated_era = era_name
                break

    # Use updated values for cascading calculation
    work_discipline = updated_discipline
    work_function = updated_function
    work_era = updated_era

    # Calculate which filter VALUES have at least one lens when combined with current selections
    available_disciplines = set(["All Disciplines"])
    available_functions = set(["All Functions"])
    available_eras = set(["All Eras"])

    # For each lens, check if it matches the current filters, and if so, add its categories as available
    for lens_name in SORTED_LENS_NAMES:
        # Check matches
        func_match = (work_function == "All Functions" or lens_name in LENSES_FUNCTIONAL.get(work_function, []))
        era_match = (work_era == "All Eras" or lens_name in LENSES_BY_ERA.get(work_era, []))
        disc_match = (work_discipline == "All Disciplines" or lens_name in LENSES_HIERARCHY.get(work_discipline, []))

        # If matches function+era, add its discipline
        if func_match and era_match:
            for disc_name, lenses in LENSES_HIERARCHY.items():
                if lens_name in lenses:
                    available_disciplines.add(disc_name)

        # If matches discipline+era, add its function
        if disc_match and era_match:
            for func_name, lenses in LENSES_FUNCTIONAL.items():
                if lens_name in lenses:
                    available_functions.add(func_name)

        # If matches discipline+function, add its era
        if disc_match and func_match:
            for era_name, lenses in LENSES_BY_ERA.items():
                if lens_name in lenses:
                    available_eras.add(era_name)

    # Build filtered lens list
    filtered_lenses = []
    for lens_name in SORTED_LENS_NAMES:
        if work_discipline != "All Disciplines" and lens_name not in LENSES_HIERARCHY.get(work_discipline, []):
            continue
        if work_function != "All Functions" and lens_name not in LENSES_FUNCTIONAL.get(work_function, []):
            continue
        if work_era != "All Eras" and lens_name not in LENSES_BY_ERA.get(work_era, []):
            continue
        filtered_lenses.append(lens_name)

    return (
        sorted(list(available_disciplines)),
        sorted(list(available_functions)),
        ["All Eras"] + [era for era in ERA_ORDER if era in available_eras and era != "All Eras"],
        filtered_lenses,
        updated_discipline,
        updated_function,
        updated_era
    )

def render_lens_search(key_prefix):
    """
    Renders a search interface that allows users to search and filter lenses by name or description.
    Returns the selected lens name or None.

    Note: Due to Streamlit limitations, the counter updates on Enter/blur, not per-keystroke.
    """
    # Get current search query from session state
    search_query = st.session_state.get(f"{key_prefix}_search_input", "")

    # Calculate matching lenses
    matching_lenses = []
    if search_query and len(search_query) >= 1:
        query_lower = search_query.lower()
        for lens_name in SORTED_LENS_NAMES:
            lens_data = get_lens_data(lens_name)
            if lens_data:
                name_match = query_lower in lens_name.lower()
                desc_match = query_lower in lens_data.get("description", "").lower()
                if name_match or desc_match:
                    matching_lenses.append(lens_name)

    # Dynamic label with result counter
    total_lenses = len(SORTED_LENS_NAMES)
    if search_query and len(search_query) >= 2:
        # Show results count
        if matching_lenses:
            label = f"🔍 **{len(matching_lenses)}** of {total_lenses} lenses match"
        else:
            label = f"🔍 **0** of {total_lenses} lenses match"
    elif search_query and len(search_query) == 1:
        label = f"🔍 Type 1 more character to search ({total_lenses} total)"
    else:
        label = f"🔍 Search {total_lenses} lenses by name or description"

    # Search input with dynamic label
    st.text_input(
        label,
        key=f"{key_prefix}_search_input",
        placeholder="e.g., 'myth', 'power', 'feminism'... (press Enter)",
        help="Type at least 2 characters and press Enter to search"
    )

    # Only show results dropdown if we have valid search and matches
    if search_query and len(search_query) >= 2:
        if matching_lenses:
            # Get currently selected lens from session state if it exists
            current_selection = st.session_state.get(f"{key_prefix}_search_select")
            try:
                index = matching_lenses.index(current_selection)
            except (ValueError, TypeError):
                index = None

            st.selectbox(
                "Select from results:",
                options=matching_lenses,
                index=index,
                key=f"{key_prefix}_search_select",
                help=get_lens_tooltip(st.session_state.get(f"{key_prefix}_search_select")),
                label_visibility="collapsed"
            )
            # Return the value from session state (which the selectbox updates)
            return st.session_state.get(f"{key_prefix}_search_select")
        else:
            st.warning(f"No lenses found matching **'{search_query}'**. Try different keywords.")
            return None

    return None

def render_persona_selector(lens_keyword, key_prefix):
    # v10.1: Three-tier persona selection system
    """
    Renders the optional persona selector if a pool exists for the lens.
    Returns:
    - None if "(All Personas - AI Decides)" is selected (default)
    - "(No Persona)" if user wants generic archetypal title
    - Specific persona name if user selects one
    """
    if lens_keyword and lens_keyword in PERSONA_POOL:
        # Ensure the pool is sorted for consistent UI
        pool = sorted(PERSONA_POOL[lens_keyword])
        # v10.1: Add three-tier options
        options = ["(All Personas - AI Decides)", "(No Persona - Generic Title)"] + pool

        # Customize label based on context
        label = f"Specify Persona (Optional):"
        if "symposium" in key_prefix or "dialectic" in key_prefix:
            label = f"Persona for {lens_keyword} (Optional):"

        selected_persona = st.selectbox(
            label,
            options=options,
            index=0,
            key=f"{key_prefix}_persona_selector",
            help="Choose: (1) Let AI pick from all personas in the pool, (2) Use a generic archetypal title instead of a specific person, or (3) Lock in a specific historical figure."
        )
        # Return the name only if a specific person is selected
        if selected_persona == "(All Personas - AI Decides)":
            return None
        elif selected_persona == "(No Persona - Generic Title)":
            return "(No Persona)"
        return selected_persona
    return None


def cleanup_other_pages_files(current_page):
    """
    Free uploaded files from pages other than the current page.
    Prevents memory accumulation when users navigate between pages.
    Also cleans up Gemini file references and resets the WorkInput object.

    Args:
        current_page: One of "single_lens", "dialectical", "symposium", "comparative", "library"
    """
    if current_page != "single_lens":
        if 'work_input_single' in st.session_state:
            work_input = st.session_state.work_input_single
            # Clean up Gemini file from servers
            work_input.cleanup_gemini_file()
            # Reset the WorkInput to fresh state
            st.session_state.work_input_single = WorkInput()

    if current_page != "dialectical":
        if 'work_input_dialectical' in st.session_state:
            work_input = st.session_state.work_input_dialectical
            work_input.cleanup_gemini_file()
            st.session_state.work_input_dialectical = WorkInput()

    if current_page != "symposium":
        if 'work_input_symposium' in st.session_state:
            work_input = st.session_state.work_input_symposium
            work_input.cleanup_gemini_file()
            st.session_state.work_input_symposium = WorkInput()

    if current_page != "comparative":
        if 'work_input_comparative_a' in st.session_state:
            work_input = st.session_state.work_input_comparative_a
            work_input.cleanup_gemini_file()
            st.session_state.work_input_comparative_a = WorkInput()
        if 'work_input_comparative_b' in st.session_state:
            work_input = st.session_state.work_input_comparative_b
            work_input.cleanup_gemini_file()
            st.session_state.work_input_comparative_b = WorkInput()


def initialize_page_config(title):
    # v10.2: Simplified page title (removed duplicate "Janus")
    """Sets the standard page configuration."""
    try:
        st.set_page_config(
            page_title=title,
            page_icon="🏛️",
            layout="wide"
        )
    except st.errors.StreamlitAPIException:
        pass # Avoid error if config is called multiple times

# v10.2: API Configuration for Home Page (Multi-Provider Ready)
def render_api_configuration():
    """Renders API configuration UI on the Home page. Designed for future multi-provider support."""
    # Initialize session state for API key if not present
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""

    # Check if API key is configured
    api_key_present = bool(st.session_state.get("api_key"))

    st.markdown("---")
    st.header("🔑 API Configuration")

    # Status indicator
    if api_key_present:
        st.success("✅ API Key Configured")
    else:
        st.warning("❌ API Key Required — Please configure below to use the engine")

    # Configuration expander (expanded when no key present, collapsed when configured)
    with st.expander("Configure API Settings", expanded=not api_key_present):
        # Future-proofing: Provider selection (currently Gemini only)
        st.markdown("### AI Provider")
        provider = st.selectbox(
            "Select Provider:",
            ["Google Gemini"],
            disabled=True,  # v10.2: Only Gemini supported for now
            help="Future versions will support OpenAI, Anthropic, Cohere, and other providers."
        )

        st.caption("🔮 **Coming Soon:** Multi-provider support (OpenAI, Anthropic, Cohere)")

        # Gemini-specific configuration
        st.markdown(f"### {provider} Settings")
        api_key_input = st.text_input(
            "Gemini API Key:",
            type="password",
            value=st.session_state.api_key,
            help="Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)"
        )

        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
            st.rerun()

        st.caption("🔗 [Get a free Gemini API key](https://aistudio.google.com/app/apikey)")

        # Future provider-specific settings placeholder
        # st.markdown("### Advanced Settings")
        # temperature = st.slider("Temperature", 0.0, 2.0, 1.0)
        # max_tokens = st.number_input("Max Tokens", 1000, 100000, 8000)

# v10.2: Updated Sidebar Settings (Workflow Configuration Only)
def render_sidebar_settings():
    """Renders workflow settings in the sidebar. API configuration moved to Home page in v10.2."""
    # v10.2: Initialize Analysis Mode state (API key now initialized in render_api_configuration)
    if 'analysis_mode' not in st.session_state:
        st.session_state.analysis_mode = MODE_ADAPTIVE

    with st.sidebar:
        st.header("🏛️ Janus Settings")

        # v10.2: Engine Configuration (Analysis Mode)
        with st.expander("⚙️ Workflow Configuration", expanded=True):
            st.radio(
                "Select Analysis Mode:",
                ANALYSIS_MODES,
                key="analysis_mode",
                help=f"**{MODE_ADAPTIVE}:** {get_tooltip('adaptive_analysis')}  \n\n**{MODE_SURFACE_SCRAPE}:** {get_tooltip('surface_scrape')}  \n\n**{MODE_DEEP_DIVE}:** {get_tooltip('deep_dive')}"
            )