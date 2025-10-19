import streamlit as st
import utils

# --- PAGE SETUP ---
PAGE_TITLE = "Janus | Documentation"
utils.initialize_page_config(PAGE_TITLE)
st.title("📖 Documentation")
st.write("Complete guide to using the Janus Engine for multi-perspective analysis.")

# --- SIDEBAR ---
utils.render_sidebar_settings()

# --- TABLE OF CONTENTS ---
st.markdown("---")
st.markdown("### 📑 Table of Contents")
st.markdown("""
- [Getting Started](#getting-started)
- [Core Architecture](#core-architecture)
- [Analysis Modes](#analysis-modes)
- [Lens Library](#lens-library)
- [Configuration Options](#configuration-options)
- [Export & Results](#export-results)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Version History](#version-history)
- [Glossary](#glossary)
""")

# --- GETTING STARTED ---
st.markdown("---")
st.markdown("## Getting Started")
st.markdown("""
### What is the Janus Engine?

The Janus Engine is an AI-powered pedagogical platform that analyzes creative works (text, images, audio, video) through multiple theoretical lenses simultaneously. It leverages Gemini 2.5 Pro and Flash-Lite to provide deep, multi-perspective analysis.

### Quick Start (3 Steps)

1. **Configure API & Analysis Mode**
   - Enter your Google Gemini API key on the Home page
   - Choose your analysis mode in sidebar: Adaptive Analysis (default), Surface Scrape, or Deep Dive

2. **Select an Analysis Page**
   - **Single Lens:** One work, one perspective
   - **Dialectical:** One work, two perspectives (thesis vs. antithesis)
   - **Symposium:** One work, 3-6 perspectives (multi-participant discussion)
   - **Comparative:** Two works, one perspective (comparative synthesis)

3. **Upload & Analyze**
   - Upload your work (text, image, audio, video, or PDF)
   - Select lens(es) and persona(s)
   - Click "Execute Analysis"
   - Export results as Markdown or Plain Text

### Supported File Types

- **Text:** `.txt`, `.md`, `.pdf`, `.docx`
- **Images:** `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.heic`, `.heif`
- **Audio:** `.mp3`, `.wav`, `.aac`, `.ogg`, `.flac`
- **Video:** `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`

File size limits apply based on file type and analysis mode.
""")

# --- CORE ARCHITECTURE ---
st.markdown("---")
st.markdown("## Core Architecture")
st.markdown("""
The Janus Engine uses a **"Generative & Adaptive"** four-stage architecture:

### Stage 1: Triage (Optional)
- Fast assessment of work complexity
- Uses Gemini Flash-Lite for quick evaluation
- Determines if specialized handling is needed

### Stage 2: Theoretician
- Analyzes the work to understand its core themes
- **Dynamically generates** the most relevant analytical concepts for the chosen lens
- Creates a bespoke analytical strategy tailored to the specific artwork
- Example: For "Marxism" → might generate concepts like "Class Struggle", "Commodity Fetishism", "Alienation of Labor"

### Stage 3: Specialist Swarm
- Spawns parallel AI instances (Gemini 2.5 Pro)
- Each specialist performs a deep dive on one generated concept
- All specialists analyze simultaneously for efficiency

### Stage 4: Master Synthesizer
- Integrates all specialist reports into a holistic analysis
- Adopts an appropriate persona (if selected)
- Produces final coherent synthesis

This architecture moves beyond static frameworks, generating custom analytical strategies for each unique work.
""")

# --- ANALYSIS MODES ---
st.markdown("---")
st.markdown("## Analysis Modes")

st.markdown("### 🔬 Single Lens Analysis")
st.markdown("""
**Purpose:** Focused analysis of one work through one theoretical perspective.

**Use Cases:**
- Deep dive into a specific theoretical framework
- Iterative refinement of analysis
- Testing different personas within the same lens

**Workflow:**
1. Upload one work
2. Select one lens (with optional persona)
3. Execute analysis
4. Refine with follow-up questions (Refinement Loop)
5. Export results
""")

st.markdown("### 🎭 Dialectical Dialogue")
st.markdown("""
**Purpose:** Thesis vs. Antithesis analysis with synthetic resolution.

**Use Cases:**
- Exploring contradictory interpretations
- Understanding tensions between frameworks
- Generating creative insights from opposition

**Workflow:**
1. Upload one work
2. Select two lenses (Lens A vs. Lens B)
3. System performs two parallel analyses
4. Synthesizer creates dialogue between perspectives
5. Export dialectical synthesis
""")

st.markdown("### 🏛️ Symposium")
st.markdown("""
**Purpose:** Multi-participant discussion (3-6 perspectives).

**Use Cases:**
- Comprehensive multi-perspective analysis
- Exploring complex works requiring diverse viewpoints
- Generating rich, polyphonic interpretations

**Workflow:**
1. Upload one work
2. Select 3-6 lenses from the Lens Library
3. System performs parallel analyses for all perspectives
4. Synthesizer weaves results into multi-participant dialogue
5. Export symposium discussion
""")

st.markdown("### 🔄 Comparative Synthesis")
st.markdown("""
**Purpose:** Analyze two different works through the same lens.

**Use Cases:**
- Comparing two artworks, texts, or media
- Understanding evolution across works by same creator
- Cross-cultural or cross-temporal comparisons

**Workflow:**
1. Upload Work A and Work B
2. Select one lens (same for both works)
3. System analyzes both works separately
4. Synthesizer creates comparative analysis
5. Export comparative synthesis (includes metadata for both works)
""")

# --- LENS LIBRARY ---
st.markdown("---")
st.markdown("## Lens Library")
st.markdown("""
The Janus Engine includes **157 theoretical lenses** spanning multiple disciplines and historical eras.

### Multi-Dimensional Filtering

Navigate the library using three independent filter dimensions:

**1. Discipline Filter** (Academic domain)
- Art History, Ethics, Film Studies, Literary Theory, Metaphysics, Mythology, Philosophy, Political Theory, Psychology, Sociology, Theology, etc.
- Lenses can appear in multiple disciplines (e.g., Post-Structuralism spans Metaphysics, Literary Theory, Individual Philosophy, Sociology)

**2. Function Tier Filter** (Analytical focus)
- **What it is:** Descriptive, taxonomic lenses
- **How it works:** Mechanistic, structural lenses
- **Why it matters:** Evaluative, normative lenses

**3. Era Filter** (Historical period)
- Ancient & Classical, Medieval Period, Early Modern Period, 19th Century, Early-Mid 20th Century, Late 20th Century, Contemporary

### Persona Pools

Many lenses include **persona pools** — collections of historical figures who can embody that framework:

**Persona Selection Modes:**
1. **All Personas (AI Decides)** — Default. AI selects the most contextually appropriate figure from the pool
2. **No Persona (Generic Title)** — Uses archetypal title (e.g., "The Republican Theorist")
3. **Specific Persona** — Lock to a particular historical figure

**Example: Republicanism Persona Pool**
- Cicero (Ancient)
- Thomas Jefferson (Early Modern Period)
- James Madison (Early Modern Period)
- Abraham Lincoln (19th Century)
- Hannah Arendt (20th Century)

The AI will select (or you can manually choose) the persona that best matches your work's context.

### Toolkit Lenses

Some lenses use a **toolkit structure** with sub-primers for specialized analysis:

**Examples:**
- **Psychoanalytic Theory:** 11 sub-primers (Freudian, Jungian, Lacanian schools)
- **Buddhism:** 3 sub-primers (Chan/Zen, Theravāda, Tibetan)
- **Christian Theology:** 3 sub-primers (Catholic, Protestant, Liberation Theology)

These provide depth while reducing library bloat.

### Zeitgeist Perspective

The special **"Zeitgeist Perspective"** lens allows AI to:
- Simulate the cultural/intellectual climate of any historical period
- Apply era-specific analytical frameworks without predefined theory
- Useful for historically contextualized analysis
""")

# --- CONFIGURATION OPTIONS ---
st.markdown("---")
st.markdown("## Configuration Options")

st.markdown("### Analysis Mode (Sidebar Global Setting)")
st.markdown("""
**Adaptive Analysis (Default)**
- Balances quality, cost, and speed using Triage
- Uses Flash-Lite for simple works, Pro for complex works
- Best for most use cases
- Recommended for new users

**Surface Scrape**
- Fastest and most cost-effective option
- Uses Flash-Lite for all stages
- Good for quick explorations or simple works

**Deep Dive**
- Maximum depth and thoroughness
- Uses Gemini 2.5 Pro for all stages
- Higher token usage and cost
- Best for academic research or critical works
""")

st.markdown("### Refinement Loop")
st.markdown("""
After initial analysis, you can ask follow-up questions:
- Clarify specific points
- Request deeper analysis of a particular theme
- Apply the same lens to a different aspect
- Compare with another theoretical perspective

The AI retains context from the original analysis for coherent refinement.
""")

st.markdown("### Work Input Options")
st.markdown("""
**Text Input:**
- Paste directly into text area
- Upload text file
- Upload PDF (text will be extracted)

**Media Input:**
- Upload image, audio, or video file
- System uses Gemini's multimodal capabilities for analysis
- No transcription needed — direct media understanding

**Metadata:**
- Optional title and creator fields
- Used for context in persona selection and synthesis
""")

# --- EXPORT & RESULTS ---
st.markdown("---")
st.markdown("## Export & Results")
st.markdown("""
### Export Formats (New in v10.2)

Every analysis result can be exported in two formats:

**📥 Markdown (.md)**
- Formatted document with headers and structure
- Ideal for documentation, wikis, note-taking apps
- Preserves visual hierarchy

**📥 Plain Text (.txt)**
- Universal compatibility
- ASCII separators for readability
- Works in any text editor

### Export Contents

All exports include:
- **Timestamp:** Analysis completion date and time
- **Analysis Type:** Single Lens, Dialectical, Symposium, or Comparative
- **Analysis Mode:** Adaptive Analysis, Surface Scrape, or Deep Dive
- **Configuration:** Lens, persona, work details
- **Work Details:** Title, type, character/token count
- **API Usage Metrics:** Input tokens, output tokens, estimated cost, duration
- **Full Analysis Result:** Complete synthesized text

For **Comparative Analysis**, metadata for both Work A and Work B is included.

### Metadata Display

After each analysis, the system displays:
- Total tokens used (input + output)
- Estimated cost in USD
- Analysis duration
- Work character count

This helps track usage and costs across sessions.
""")

# --- BEST PRACTICES ---
st.markdown("---")
st.markdown("## Best Practices")

st.markdown("### Lens Selection")
st.markdown("""
**For single works:**
- Use **Single Lens** for deep, focused analysis
- Use **Dialectical** to explore contradictions (e.g., Capitalism vs. Marxism)
- Use **Symposium** for complex works requiring multiple viewpoints

**For comparisons:**
- Use **Comparative** to analyze two works through the same lens
- Consider Zeitgeist Perspective for cross-temporal comparisons
""")

st.markdown("### Persona Selection")
st.markdown("""
**Let AI decide (default)** when:
- You want contextually appropriate voice
- Work has clear historical/cultural context
- You're unsure which persona fits best

**Select specific persona** when:
- You need consistency across multiple analyses
- You're exploring how different thinkers would interpret the same work
- You want a particular rhetorical style

**Use no persona** when:
- You want pure framework analysis without personality
- You prefer archetypal voice over historical figure
""")

st.markdown("### Analysis Mode Selection")
st.markdown("""
**Use Adaptive Analysis** for:
- General analysis
- Iterative exploration
- Automatic quality/cost optimization based on work complexity

**Use Surface Scrape** for:
- Quick explorations
- Simple works
- Cost-conscious workflows
- Draft-stage analysis

**Use Deep Dive** for:
- Academic research
- Critical publications
- Maximum analytical depth required
- Complex works requiring thorough analysis
""")

st.markdown("### Refinement Loop Tips")
st.markdown("""
Effective follow-up questions:
- "Analyze the symbolism of [specific element] in more depth"
- "How would this analysis change if viewed through [alternative lens]?"
- "What are the implications of this interpretation for [specific context]?"
- "Compare this analysis to the work of [specific scholar/thinker]"

Avoid:
- Requesting entirely new analysis (better to re-run with different config)
- Asking about unrelated works (use Comparative mode instead)
""")

# --- TROUBLESHOOTING ---
st.markdown("---")
st.markdown("## Troubleshooting")

st.markdown("### API Key Issues")
st.markdown("""
**"Invalid API Key" error:**
- Verify key is correct (no extra spaces)
- Check that API key is for Google Gemini (not OpenAI or other service)
- Ensure API key has appropriate permissions
- Generate a new key if needed (link available on Home page configuration)

**Rate limit errors:**
- Wait a few minutes and try again
- Consider using Surface Scrape instead of Deep Dive
- Check your Google Cloud quota
""")

st.markdown("### File Upload Issues")
st.markdown("""
**File too large:**
- Compress images/videos before upload
- For text: paste directly instead of uploading
- For PDFs: extract text and paste directly

**Unsupported file type:**
- Convert to supported format (see "Supported File Types" above)
- For audio/video: ensure file is not corrupted

**Upload fails silently:**
- Check file permissions
- Try different browser
- Clear browser cache
""")

st.markdown("### Analysis Errors")
st.markdown("""
**Analysis times out:**
- Try Surface Scrape instead of Deep Dive
- Reduce work length (summarize or excerpt)
- Check internet connection

**Results are incomplete:**
- Try using Deep Dive mode for more thorough analysis
- Try again with different lens

**Persona doesn't match expectation:**
- Select specific persona instead of "AI Decides"
- Check that lens has appropriate persona pool
- Use "No Persona" for framework-only analysis
""")

st.markdown("### Export Issues")
st.markdown("""
**Download button doesn't work:**
- Allow pop-ups in browser settings
- Try different browser
- Check browser download permissions

**Export file is empty:**
- Wait for analysis to fully complete
- Check that result is displayed on screen
- Try refreshing page and re-exporting
""")

# --- VERSION HISTORY ---
st.markdown("---")
st.markdown("## Version History")

st.markdown("### v10.2: Export System & Documentation (Current)")
st.markdown("""
**New Features:**
- 📥 **Export Functionality:** Download analysis results as Markdown or Plain Text with complete metadata
- 📖 **Documentation Page:** Comprehensive in-app guide (this page)
- 📊 **Enhanced Metadata:** All exports include timestamp, configuration, API usage metrics

**Technical Improvements:**
- Standardized export format across all analysis modes
- Dual-metadata tracking for Comparative analysis
- Timestamp-based file naming to prevent overwrites
""")

st.markdown("### v10.1: Multi-Dimensional Filtering & Lens Consolidation")
st.markdown("""
**New Features:**
- 🔍 **Unified Filter System:** Discipline × Function × Era filtering on all analysis pages
- 👤 **Three-Tier Persona Selection:** AI Decides / No Persona / Specific Persona
- 🏛️ **Era-Spanning Political Lenses:** Republicanism, Democracy, Conservatism, Socialism with multi-era persona pools
- 🎬 **Film Movement Lenses:** 10 new cinema movement lenses (Film Noir, French New Wave, etc.)
- 🔄 **Multi-Discipline Lens Membership:** Lenses can appear in multiple categories

**Library Improvements:**
- Consolidated "person-isms" into broader frameworks (Deontology, Egoism, Idealism, etc.)
- Toolkit structure for Psychoanalytic Theory, Buddhism, Christian Theology
- Optimized from ~163 to 157 lenses with deeper persona pools
""")

st.markdown("### v10.0: Adaptive Architecture")
st.markdown("""
**Core Architecture Overhaul:**
- 🧠 **Generative Strategy Engine:** AI dynamically generates analytical concepts instead of static frameworks
- ⚡ **Four-Stage Pipeline:** Triage → Theoretician → Specialist Swarm → Master Synthesizer
- 🎯 **Bespoke Analysis:** Each work gets custom-tailored analytical strategy

**Technical Improvements:**
- Parallel specialist execution for efficiency
- Adaptive concept generation based on work complexity
- Enhanced synthesis quality through structured integration
""")

st.markdown("### v9.5a: General's Toolkit")
st.markdown("""
- Introduced toolkit structure for complex lenses
- Sub-primers for specialized analysis within broader frameworks
- Improved modularity and analytical depth
""")

st.markdown("### v9.4b: UX Overhaul & Zeitgeist Mode")
st.markdown("""
- 🌍 **Zeitgeist Perspective:** Era-specific cultural analysis
- UI/UX redesign for better navigation
- Enhanced sidebar configuration
""")

st.markdown("### v9.4a: Foundation Patch")
st.markdown("""
- Bug fixes and stability improvements
- Performance optimizations
- Codebase refactoring
""")

st.markdown("### v9.3: Great Library")
st.markdown("""
- 📚 **Lens Library Page:** Searchable, filterable lens catalog
- Shopping cart system for Dialectical and Symposium modes
- Lens categorization by discipline and function
""")

st.markdown("### v9.2: Refinement Loop")
st.markdown("""
- 🔄 **Follow-up Questions:** Iterative refinement after initial analysis
- Context retention across refinement sessions
- Enhanced analytical depth through conversation
""")

st.markdown("### v9.1: Primers & Video Analysis")
st.markdown("""
- 📹 **Video Support:** Direct video file analysis
- 🎵 **Audio Support:** Audio file analysis
- Framework primers for consistent specialist analysis
""")

st.markdown("### v9.0: Hybrid UI & Persona Pools")
st.markdown("""
- 👥 **Persona Pools:** Historical figures for each lens
- Hybrid Streamlit UI with multi-page navigation
- Foundation for current architecture
""")

# --- GLOSSARY ---
st.markdown("---")
st.markdown("## Glossary")
st.markdown("""
Quick reference for technical terms used throughout the Janus Engine.

### Core Architecture

**Adaptive Architecture**
{adaptive_architecture}

**Triage**
{triage}

**Theoretician**
{theoretician}

**Specialist Swarm**
{specialist_swarm}

**Master Synthesizer**
{synthesizer}

### Analysis Modes

**Adaptive Analysis**
{adaptive_analysis}

**Surface Scrape**
{surface_scrape}

**Deep Dive**
{deep_dive}

### Core Concepts

**Lens (Theoretical Lens)**
{lens}

**Persona Pool**
{persona_pool}

**Zeitgeist Simulation**
{zeitgeist}

**Smart Selection**
{smart_selection}

**Refinement Loop**
{refinement_loop}

**Context Caching**
{context_caching}

### Lens Organization

**Discipline**
{discipline}

**Function Tier**
{function_tier}

**Contextual Tier (What it is)**
{function_tier_contextual}

**Mechanical Tier (How it works)**
{function_tier_mechanical}

**Interpretive Tier (Why it matters)**
{function_tier_interpretive}

**Era Filter**
{era_filter}

**Toolkit Lens**
{toolkit_lens}

---

💡 **Tip:** Hover over any field label or info icon in the app to see contextual tooltips for these terms.
""".format(
    adaptive_architecture=utils.get_tooltip("adaptive_architecture"),
    triage=utils.get_tooltip("triage"),
    theoretician=utils.get_tooltip("theoretician"),
    specialist_swarm=utils.get_tooltip("specialist_swarm"),
    synthesizer=utils.get_tooltip("synthesizer"),
    adaptive_analysis=utils.get_tooltip("adaptive_analysis"),
    surface_scrape=utils.get_tooltip("surface_scrape"),
    deep_dive=utils.get_tooltip("deep_dive"),
    lens=utils.get_tooltip("lens"),
    persona_pool=utils.get_tooltip("persona_pool"),
    zeitgeist=utils.get_tooltip("zeitgeist"),
    smart_selection=utils.get_tooltip("smart_selection"),
    refinement_loop=utils.get_tooltip("refinement_loop"),
    context_caching=utils.get_tooltip("context_caching"),
    discipline=utils.get_tooltip("discipline"),
    function_tier=utils.get_tooltip("function_tier"),
    function_tier_contextual=utils.get_tooltip("function_tier_contextual"),
    function_tier_mechanical=utils.get_tooltip("function_tier_mechanical"),
    function_tier_interpretive=utils.get_tooltip("function_tier_interpretive"),
    era_filter=utils.get_tooltip("era_filter"),
    toolkit_lens=utils.get_tooltip("toolkit_lens")
))

st.markdown("---")
st.caption("📖 Documentation for Janus Engine v10.2 | Last Updated: October 2025")
