# =============================================================================
# JANUS ENGINE v9.5a LENS LIBRARY ("The General's Toolkit")
# This file defines the analytical frameworks (lenses) used by the Janus Engine.
# v9.5a: Implementation of the "General's Toolkit" architecture (sub_primers).
# =============================================================================

# -----------------------------------------------------------------------------
# 1. LENS DEFINITIONS (The Source of Truth)
# Defines the core data object for each lens.
# -----------------------------------------------------------------------------

# Helper function to create a standard lens object
# v9.5a: Updated parameters to support the General's Toolkit (sub_primers)
def create_lens(description, conceptual_primer=None, requires_nuance=False, eras=None, prompt_name=None, sub_primers=None):
    if eras is None:
        eras = []
    
    # v9.5a: Validation check for the new architecture
    if conceptual_primer and sub_primers:
        raise ValueError("A lens cannot have both a conceptual_primer and sub_primers.")

    return {
        "description": description,
        "conceptual_primer": conceptual_primer,
        "sub_primers": sub_primers, # v9.5a Added
        "requires_nuance": requires_nuance,
        "eras": eras,
        "prompt_name": prompt_name, # v9.4b Added
    }

# Define Era Constants
E1_ANCIENT = "Ancient & Classical (c. 800 BCE – 500 CE)"
E2_MEDIEVAL = "Medieval & Renaissance (c. 500 – 1600)"
E3_ENLIGHTENMENT = "Enlightenment & Early Modernity (c. 1600 – 1800)"
E4_19TH = "The Long 19th Century (c. 1800 – 1914)"
E5_EARLY_20TH = "Early-Mid 20th Century (c. 1914 – 1960)"
E6_LATE_20TH = "Late 20th Century (c. 1960 – 2000)"
E7_CONTEMPORARY = "Contemporary (21st Century)"


# v9.5a: LENS_DEFINITIONS Refactor (Implementing the General's Toolkit)

LENS_DEFINITIONS = {
    # =====================================================================
    # THE GENERAL'S TOOLKIT (v9.5a Mega-Lenses)
    # These lenses utilize the 'sub_primers' architecture.
    # =====================================================================
    
    # --- Marxism Toolkit ---
    "Marxism": create_lens(
        description="Analyzes the distribution of resources, capital, and power dynamics (Marxist Criticism).",
        prompt_name="Marxist Criticism",
        # v9.5a: Replaced conceptual_primer with sub_primers toolkit
        sub_primers={
            "Classical Marxism (Base/Superstructure)": """
            Analyze the work by focusing on the economic base (means and relations of production) and how it determines the cultural superstructure (ideology, art, religion, law). 
            Examine class struggle, alienation, and the commodification of labor. Identify how the work reflects, reinforces, or critiques the dominant capitalist ideology.
            """,
            "Cultural Hegemony (Gramsci)": """
            Analyze how the dominant class maintains control not just through economic coercion, but by making their worldview seem like 'common sense' (hegemony). 
            Examine the role of intellectuals, media, and cultural institutions in manufacturing consent. Identify counter-hegemonic elements or resistance within the work.
            """,
            "Historical Materialism": """
            Analyze the work within the broader context of historical development driven by material conditions and technological change. 
            Examine how the narrative or themes reflect a specific stage of economic development (e.g., feudalism, nascent capitalism, late capitalism) and the contradictions inherent in that stage.
            """,
            "Frankfurt School (Adorno/Horkheimer)": """
            Focus on the 'culture industry' and how mass-produced art serves as a tool of social control and pacification. 
            Analyze the standardization, pseudo-individualization, and commodification of the work itself. Critique the loss of authentic aesthetic experience and the dominance of instrumental reason.
            """
        },
        requires_nuance=False,
        eras=[E4_19TH]
    ),

    # --- Feminism Toolkit ---
    "Feminism": create_lens(
        description="Examines character roles, agency, and power dynamics within social structures and relationships (Feminist Criticism).",
        prompt_name="Feminist Criticism",
        # v9.5a: Replaced conceptual_primer with sub_primers toolkit
        sub_primers={
            "Liberal Feminism (First Wave/Equality)": """
            Analyze the work focusing on the pursuit of equal rights, opportunities, and access within existing social structures. 
            Examine characters' struggles against legal or explicit discrimination, their access to education and property, and their political agency. Focus on individual autonomy and rationality.
            """,
            "Radical Feminism (Second Wave/Patriarchy)": """
            Analyze the work by focusing on the systemic nature of patriarchy as the fundamental structure of oppression. 
            Examine how gender roles are constructed and enforced, the objectification and commodification of bodies, and the dynamics of power in intimate relationships. Focus on collective liberation and the critique of gender essentialism.
            """,
            "Intersectionality (Third Wave/Crenshaw)": """
            Analyze how different forms of social stratification (race, class, gender, sexuality, ability) intersect and create overlapping systems of discrimination or disadvantage. 
            Avoid analyzing gender in isolation; focus on the specific, situated experiences of characters based on their multiple identities.
            """,
            "Postfeminism (Contemporary/Choice Culture)": """
            Analyze the work through the lens of postfeminist sensibilities, where feminism is often depicted as having achieved its goals. 
            Examine themes of individual choice, empowerment through consumerism, the embrace of traditional femininity as a choice, and the tension between autonomy and societal expectations in a supposedly 'post-patriarchal' world.
            """
        },
        requires_nuance=True,
        eras=[E6_LATE_20TH]
    ),

    # --- Stoicism Toolkit ---
    "Stoicism": create_lens(
        description="Emphasis on virtue, reason, emotional resilience, and living in harmony with nature (Epictetus, Seneca, Aurelius).",
        # v9.5a: Added sub_primers toolkit
        sub_primers={
            "The Dichotomy of Control (Discipline of Assent)": """
            Analyze the work by focusing strictly on what is within the characters' control (their judgments, intentions, responses) versus what is outside their control (external events, reputation, health, wealth). 
            Examine how characters manage their impressions (phantasiai) and assent to judgments. Evaluate their resilience and tranquility (ataraxia) based on this distinction.
            """,
            "Managing Desire and Aversion (Discipline of Desire)": """
            Analyze how characters manage their desires and aversions. Evaluate whether they desire what is good (virtue) and are averse to what is bad (vice), or if they mistakenly desire external 'indifferents'. 
            Examine the emotional consequences of their desires (e.g., frustration, grief, envy) and their progress towards apatheia (freedom from irrational passions).
            """,
            "The Ethics of Action (Discipline of Action)": """
            Analyze the characters' actions in the world. Evaluate whether their actions are motivated by virtue, reason, and duty (kathēkonta). 
            Examine how they treat others, whether they act with a 'reserve clause' (acknowledging fate), and if their actions align with their moral principles even in adversity.
            """,
            "Cosmopolitanism and Nature (The View from Above)": """
            Analyze the work's perspective on the interconnectedness of humanity (cosmopolitanism) and the natural order (Logos/Fate). 
            Examine how characters perceive their place in the universe, their relationship to society, and their acceptance of mortality and change as natural processes.
            """
        },
        eras=[E1_ANCIENT]
    ),

    # --- Jungian Analysis Toolkit ---
    "Jungian Analysis": create_lens(
        description="Focus on the collective unconscious, archetypes (Shadow, Anima/Animus), and individuation (Jung).",
        prompt_name="Jungian (Archetypal) Criticism",
        # v9.5a: Added sub_primers toolkit
        sub_primers={
            "Archetypal Mapping (The Collective Unconscious)": """
            Analyze the work by identifying dominant archetypes (e.g., The Hero, The Mentor, The Trickster, The Mother) present in characters, symbols, and narrative patterns. 
            Examine how these elements draw power from the collective unconscious and how they structure the work's meaning and emotional impact.
            """,
            "Shadow Work and Integration": """
            Focus on the 'Shadow'—the repressed, denied, or unconscious aspects of the personality. 
            Analyze how characters confront (or fail to confront) their Shadow, often projected onto antagonists or symbolized by dark imagery. Examine the psychological consequences of this confrontation and the potential for integration.
            """,
            "Anima/Animus Dynamics": """
            Analyze the dynamics of the contrasexual archetypes: the Anima (the unconscious feminine aspect in men) and the Animus (the unconscious masculine aspect in women). 
            Examine how these figures appear in dreams, fantasies, or projections onto others, and how they influence relationships and personal development.
            """,
            "The Individuation Process": """
            Analyze the work as a narrative of individuation—the journey toward psychological wholeness and self-realization. 
            Examine the stages of this process: the breakdown of the Persona (social mask), the confrontation with the Shadow and Anima/Animus, and the realization of the Self (the unifying center of the psyche).
            """
        },
        eras=[E5_EARLY_20TH]
    ),

    # --- Freudian Psychoanalysis Toolkit ---
    "Freudianism": create_lens(
        description="Focus on the unconscious mind, defense mechanisms (id/ego/superego), and psychosexual stages (Freud).",
        prompt_name="Freudian Psychoanalysis",
        # v9.5a: Added sub_primers toolkit
        sub_primers={
            "Id, Ego, and Superego Conflict": """
            Analyze the psychological structure of the characters based on the tripartite model. Identify the drives of the Id (pleasure principle), the constraints of the Superego (morality/ideal self), and the mediation of the Ego (reality principle). 
            Examine the internal conflicts arising from these competing forces and how they drive the narrative.
            """,
            "Defense Mechanisms": """
            Analyze the defense mechanisms employed by characters to manage anxiety and protect the ego from unacceptable thoughts or feelings. 
            Identify instances of repression, projection, denial, displacement, sublimation, and rationalization. Examine how these mechanisms affect behavior and relationships.
            """,
            "Psychosexual Stages and Complexes (Oedipal/Electra)": """
            Analyze the work for evidence of unresolved issues stemming from psychosexual development (oral, anal, phallic, latency, genital). 
            Focus particularly on the Oedipus or Electra complexes: examine the dynamics of desire, rivalry, and identification within family structures and how these complexes shape adult identity and neuroses.
            """,
            "Symbolism and The Unconscious (Dream Logic)": """
            Analyze the work as if it were a dream, focusing on the manifestation of the unconscious. 
            Examine symbols (especially phallic/yonic), slips of the tongue (parapraxes), condensation (compressing multiple ideas into one symbol), and displacement (shifting focus from the important to the trivial). Interpret the latent content beneath the manifest surface.
            """
        },
        eras=[E5_EARLY_20TH]
    ),
    
    # --- Existentialism Toolkit ---
    "Existentialism": create_lens(
        description="Emphasis on individual freedom, responsibility, and the subjective experience; existence precedes essence (Sartre, de Beauvoir).",
        # v9.5a: Added sub_primers toolkit
        sub_primers={
            "Existence Precedes Essence (The Subjective Experience)": """
            Analyze the work focusing on the primacy of individual subjective experience. Examine how characters construct their own identity and values (essence) through their actions and choices, rather than conforming to predefined roles or essential natures.
            """,
            "Radical Freedom and Responsibility (Anguish/Dread)": """
            Focus on the concept that humans are 'condemned to be free'. Analyze the characters' confrontation with their absolute freedom of choice and the overwhelming responsibility that entails. Examine the resulting emotional states of anguish (Sartre), dread (Kierkegaard), or anxiety.
            """,
            "Authenticity vs. Bad Faith (Mauvaise Foi)": """
            Analyze the distinction between living authentically (embracing freedom and creating meaning) and living in 'Bad Faith' (denying freedom, adopting false roles, conforming to external pressure). Examine how characters deceive themselves or others about their true nature and possibilities.
            """,
            "The Absurd and Meaning-Making (Camus/Nietzsche)": """
            Analyze the confrontation between the human desire for meaning and the apparent meaninglessness or irrationality of the universe (The Absurd). Examine how characters respond to this confrontation: despair, suicide, religious leaps of faith, or rebellion/creation of subjective meaning (e.g., the Übermensch or the Absurd Hero).
            """
        },
        eras=[E4_19TH, E5_EARLY_20TH]
    ),

    # --- Postcolonialism Toolkit ---
    "Postcolonialism": create_lens(
        description="Examines the cultural, political, and economic legacy of colonialism and imperialism.",
        # v9.5a: Added sub_primers toolkit
        sub_primers={
            "Colonial Discourse Analysis (Orientalism/Said)": """
            Analyze how the work constructs the 'Other' (the colonized subject or culture) in relation to the 'Self' (the colonizing power). Examine the stereotypes, generalizations, and binaries (e.g., civilized/savage, rational/irrational) used to justify colonial domination (Orientalism).
            """,
            "Hybridity and Mimicry (Bhabha)": """
            Focus on the creation of new cultural forms and identities in the contact zone between colonizer and colonized. Analyze instances of 'mimicry' (the colonized imitating the colonizer, often imperfectly and threateningly) and 'hybridity' (the blurring of boundaries and the emergence of interstitial spaces).
            """,
            "Decolonization, Resistance, and Nationalism": """
            Analyze the themes of resistance against colonial rule, the struggle for independence, and the formation of postcolonial national identity. Examine the physical, psychological, and cultural mechanisms of decolonization and the challenges of nation-building after empire.
            """,
            "The Subaltern and Representation (Spivak)": """
            Focus on the voices and experiences of the most marginalized groups (the subaltern) who are excluded from both colonial and dominant indigenous narratives. Analyze the difficulties of representing the subaltern ("Can the subaltern speak?") and the ethical implications of speaking for others.
            """
        },
        eras=[E6_LATE_20TH]
    ),

    # --- Critical Theory (Frankfurt School) Toolkit ---
    # Note: This is distinct from the Marxism entry, focusing specifically on the Frankfurt School's broader critique.
    "Critical Theory": create_lens(
        description="Critique of society and culture, focusing on power structures, ideology, and the potential for emancipation (Frankfurt School).",
        prompt_name="Critical Theory (Frankfurt School)",
        # v9.5a: Added sub_primers toolkit
        sub_primers={
            "Critique of Instrumental Reason (Dialectic of Enlightenment)": """
            Analyze how the Enlightenment's emphasis on reason has devolved into 'instrumental reason'—a focus on efficiency, control, and domination of both nature and humanity. Examine how this logic manifests in technology, bureaucracy, and social structures within the work.
            """,
            "The Culture Industry (Mass Deception)": """
            Analyze the work in the context of the 'culture industry'. Examine how mass media and popular culture function as tools of ideological control, standardization, and the suppression of critical thinking. Focus on the commodification of art and the pacification of the audience.
            """,
            "Ideology Critique": """
            Analyze the underlying ideologies that legitimize existing power structures and social inequalities. Examine how the work reveals, conceals, or critiques dominant ideologies (e.g., consumerism, technocracy, neoliberalism). Focus on the gap between appearance and reality.
            """,
            "Emancipatory Potential and Negative Dialectics": """
            Analyze the work for its emancipatory potential—its ability to challenge the status quo and point towards a more rational and just society. Focus on 'negative dialectics'—the refusal of easy synthesis and the acknowledgment of contradictions, suffering, and the non-identical.
            """
        },
        eras=[E5_EARLY_20TH]
    ),

    # --- Bourdieuian Analysis Toolkit ---
    "Bourdieuian Analysis": create_lens(
        description="Analyzes social dynamics through concepts of habitus (dispositions), field (social space), and various forms of capital (Bourdieu).",
        prompt_name="Bourdieu (Habitus/Field/Capital)",
        # v9.5a: Added sub_primers toolkit
        sub_primers={
            "Analysis of Capital (Economic, Social, Cultural)": """
            Analyze the distribution and exchange of different forms of capital among characters or groups. Examine Economic Capital (money, assets), Social Capital (networks, connections), and Cultural Capital (education, tastes, skills). Analyze how these capitals confer power and status.
            """,
            "Analysis of Habitus (Embodied Dispositions)": """
            Analyze the 'habitus'—the system of internalized dispositions, tastes, mannerisms, and ways of perceiving the world that are shaped by social class and background. Examine how the habitus influences characters' actions, choices, and interactions, often unconsciously.
            """,
            "Analysis of Field Dynamics (The Rules of the Game)": """
            Analyze the specific 'field' (e.g., the art world, the academic system, the political arena) in which the action takes place. Examine the structure of the field, the stakes (what is being fought over), and the strategies employed by agents to improve their position within it.
            """,
            "Symbolic Violence and Misrecognition (Doxa)": """
            Analyze the mechanisms of 'symbolic violence'—the subtle ways in which power relations are legitimized and reproduced, often with the complicity of the dominated. Examine the 'doxa' (the taken-for-granted beliefs and assumptions) and how the existing social order is misrecognized as natural or just.
            """
        },
        eras=[E6_LATE_20TH]
    ),

    # --- Post-Structuralism (Foucault) Toolkit ---
    "Post-Structuralism": create_lens(
        description="Examines the relationship between power, knowledge, discourse, and the construction of subjectivity (Foucault).",
        prompt_name="Post-Structuralism (Foucault)",
        # v9.5a: Added sub_primers toolkit
        sub_primers={
            "Discourse Analysis (The Rules of Speech)": """
            Analyze the dominant discourses (ways of speaking, writing, and thinking) within the work. Examine the rules that govern what can be said, who can speak with authority, and what is considered true or false within a specific context. Focus on how discourse shapes understanding and reality.
            """,
            "The Power/Knowledge Nexus": """
            Analyze the relationship between power and knowledge. Examine how systems of knowledge (e.g., science, medicine, psychology) are not neutral but are intrinsically linked to the exercise of power. Analyze how power produces knowledge and how knowledge reinforces power relations.
            """,
            "Genealogy and Archaeology (History of the Present)": """
            Analyze the historical contingency of concepts or institutions presented in the work (e.g., madness, sexuality, the state). Examine how these concepts have evolved over time through ruptures and transformations, challenging the idea of a linear or progressive history.
            """,
            "Discipline, Surveillance, and Biopower": """
            Analyze the mechanisms of disciplinary power that regulate behavior and produce docile bodies. Examine institutions (e.g., schools, prisons, hospitals) and practices of surveillance (the Panopticon effect). Analyze 'biopower'—the control and management of populations through health, reproduction, and life itself.
            """
        },
        eras=[E6_LATE_20TH]
    ),

    # =====================================================================
    # STANDARD LENSES
    # =====================================================================

    # --- Refactored Standard Lenses (v9.4b, preserved in v9.5a) ---
    
    # v9.4b: Key changed from "Normativity & Variance Analysis" to "Queer Theory" (Step A). No simplification needed (Step B).
    "Queer Theory": create_lens(
        description="Analyzes how norms regarding identity, desire, and social structures are established or challenged.",
        conceptual_primer="""
        Analyze how the work establishes, reinforces, or challenges norms regarding identity, desire, and social structures. 
        Examine elements that deviate from established conventions (variance). 
        Focus on the instability of categories and the fluidity of expression, identifying how the work addresses the boundaries between the conventional and the unconventional, and the mechanisms used to police those boundaries.
        """,
        requires_nuance=True,
        eras=[E6_LATE_20TH]
    ),

    # === Standard Lenses (Applying the Simplification Principle) ===
    
    # Aesthetics, Art Theory, & Literature
    "Aestheticism": create_lens("Focus on beauty, sensory experience, and the concept of 'art for art's sake.'", eras=[E4_19TH]),
    "Affect Theory": create_lens("Focus on embodied experiences, emotional responses, and the transmission of feeling.", eras=[E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Auteur Theory": create_lens(description="Analyzes a film as a reflection of the director's personal creative vision and style.", eras=[E5_EARLY_20TH], prompt_name="Auteur Theory (Film)"),
    
    "Avant-Garde Studies": create_lens("Examines experimental, radical, or unorthodox art movements that challenge conventions.", eras=[E5_EARLY_20TH]),
    
    # v9.4b Refactor
    "Baroque Aesthetics": create_lens(description="Analyzes themes of drama, grandeur, movement, emotional intensity, and sensory richness in 17th/18th-century art.", eras=[E3_ENLIGHTENMENT], prompt_name="Baroque Art Theory"),
    
    # v9.4b Refactor
    "Biographical Analysis": create_lens("Interprets the work based on the author's life, experiences, and context.", eras=[E2_MEDIEVAL], prompt_name="Biographical Criticism"),

    "Cubism": create_lens(description="Analyzes the deconstruction of objects into geometric forms and the presentation of multiple viewpoints simultaneously.", eras=[E5_EARLY_20TH]),
    "Dadaism": create_lens(description="Focuses on the rejection of logic and reason, embracing nonsense, irrationality, and anti-art principles.", eras=[E5_EARLY_20TH]),
    "Ecocriticism": create_lens("Examines the relationship between literature/art and the physical environment.", eras=[E6_LATE_20TH]),
    
    # v9.4b Refactor
    "Formalism": create_lens("Focus on the intrinsic properties of the text (form, structure, literary devices); rejects external context (New Criticism).", eras=[E5_EARLY_20TH], prompt_name="Formalism (New Criticism)"),
    
    "Iconography/Iconology": create_lens("Study of the identification, description, and interpretation of visual images and symbols in art (Panofsky).", eras=[E5_EARLY_20TH]),
    "Impressionism": create_lens(description="Focuses on capturing the fleeting sensory effect of a moment through light and color, rather than precise detail.", eras=[E4_19TH]),
    "Impressionistic Criticism": create_lens("Subjective appreciation and personal response to the work.", eras=[E4_19TH]),
    "Intentional Fallacy": create_lens("Argues against using the author's intended meaning as the basis for interpretation (Wimsatt and Beardsley).", eras=[E5_EARLY_20TH]),
    
    # v9.4b Refactor
    "Ludology": create_lens(description="Analyzes games based on their rules, mechanics, and systems of play, rather than narrative or visuals (Game Studies).", eras=[E6_LATE_20TH], prompt_name="Ludology (Game Studies)"),
    
    # v9.4b Refactor
    "Media Ecology": create_lens(description="Analyzes how media, independent of content, influence society and perception ('the medium is the message') (McLuhan).", eras=[E6_LATE_20TH], prompt_name="Media Ecology (McLuhan)"),
    
    "Modernism": create_lens("Analyzes themes and styles of early 20th-century art, focusing on experimentation and a break from tradition.", eras=[E5_EARLY_20TH]),
    "Postmodernism": create_lens("Focus on skepticism toward grand narratives, irony, pastiche, and the blurring of high/low culture.", eras=[E6_LATE_20TH]),
    "Pragmatic Criticism": create_lens("Evaluates the work based on its success in achieving a specific effect or purpose on the audience.", eras=[E1_ANCIENT]),
    "Reception Theory": create_lens("Focus on the audience's reception and interpretation of the work over time (Jauss).", eras=[E6_LATE_20TH]),
    
    # v9.4b Refactor
    "Renaissance Aesthetics": create_lens(description="Focuses on humanism, perspective (linear), classical ideals (Greco-Roman), and the elevation of the artist's status.", eras=[E2_MEDIEVAL], prompt_name="Renaissance Art Theory"),
    
    "Romanticism": create_lens("Emphasis on emotion, individualism, the sublime, and the glorification of nature and the past.", eras=[E4_19TH]),
    
    # v9.4b Refactor
    "Semiotics": create_lens("Study of signs and symbols and their interpretation (Saussure, Peirce).", eras=[E5_EARLY_20TH], prompt_name="Semiotics (Sign/Signifier)"),
    
    "Structuralism": create_lens("Analyzes the underlying structures, systems, and binary oppositions that govern a work.", eras=[E5_EARLY_20TH]),
    "Surrealism": create_lens("Focus on the subconscious mind, dreamlike imagery, and the irrational juxtaposition of images (Breton).", eras=[E5_EARLY_20TH]),

    # Cultural & Identity Studies
    "Afrofuturism": create_lens("Examines the intersection of African diaspora culture, technology, and speculative futures.", eras=[E7_CONTEMPORARY]),
    
    # v9.4b Refactor: Added prompt_name for explicit backend instruction, though key remains the same for UI visibility.
    "Critical Race Theory (CRT)": create_lens("Examines society and culture as they relate to the intersection of race, law, and power.", requires_nuance=True, eras=[E7_CONTEMPORARY], prompt_name="Critical Race Theory"),
    
    "Disability Studies": create_lens("Analyzes the representation, experience, and social construction of disability.", requires_nuance=True, eras=[E7_CONTEMPORARY]),
    "Gender Studies": create_lens("Examines the social construction and impact of gender roles, identity, and power.", requires_nuance=True, eras=[E6_LATE_20TH]),
    "Indigenous Methodologies": create_lens("Utilizes Indigenous knowledge systems, perspectives, and ethical frameworks for analysis.", eras=[E7_CONTEMPORARY]),
    "Intersectionality": create_lens("Analyzes the interconnected nature of social categorizations (race, class, gender) as they create overlapping systems of disadvantage (Crenshaw).", requires_nuance=True, eras=[E6_LATE_20TH]),
    "Orientalism": create_lens("Analyzes the stereotypical and often patronizing Western representations of the 'Orient' (Said).", eras=[E6_LATE_20TH]),
    # "Postcolonialism" moved to Toolkit section v9.5a
    "Subaltern Studies": create_lens("Focus on marginalized groups excluded from the dominant historical narrative (Spivak).", eras=[E6_LATE_20TH]),
    "Whiteness Studies": create_lens("Examines the construction, history, and implications of 'whiteness' as a racial category.", requires_nuance=True, eras=[E7_CONTEMPORARY]),

    # Economics & Political Science
    "Anarchism": create_lens(description="Advocates for the abolition of all involuntary, coercive forms of hierarchy and the state.", eras=[E6_LATE_20TH]),
    "Behavioral Economics": create_lens("Applies psychological insights into human behavior to explain economic decision-making.", eras=[E7_CONTEMPORARY]),
    "Classical Liberalism": create_lens("Focus on individual liberty, consent of the governed, limited government, and free markets (Locke, Smith).", eras=[E3_ENLIGHTENMENT]),
    "Communitarianism": create_lens(description="Emphasizes the connection between the individual and the community, balancing rights with social responsibilities.", eras=[E6_LATE_20TH]),
    "Game Theory": create_lens("Analyzes strategic interactions and decision-making among rational agents.", eras=[E6_LATE_20TH]),
    "Geopolitical Analysis": create_lens("Examines the influence of geography (territory, resources, location) on politics and international relations.", eras=[E4_19TH]),
    "Libertarianism": create_lens(description="Prioritizes individual liberty, minimizing the state, free association, and strong private property rights.", eras=[E6_LATE_20TH]),
    "Neoliberalism": create_lens("Analyzes the impact of policies emphasizing free-market capitalism, deregulation, and privatization.", eras=[E6_LATE_20TH]),
    "Political Economy": create_lens("Examines the relationship between political institutions, the economic system, and social structures.", eras=[E3_ENLIGHTENMENT]),
    "Realpolitik": create_lens("Focus on practical considerations of national interest and power, rather than ideological concerns.", eras=[E2_MEDIEVAL]),
    "Social Contract Theory": create_lens("Examines the implicit agreements by which people form nations and maintain social order (Hobbes, Locke, Rousseau).", eras=[E3_ENLIGHTENMENT]),
    "Utilitarianism": create_lens("Focus on maximizing overall happiness or utility; the greatest good for the greatest number (Bentham, Mill).", eras=[E3_ENLIGHTENMENT]),

    # History & Anthropology
    "Annales School": create_lens("Focus on long-term social history (la longue durée) and structural changes, rather than events.", eras=[E5_EARLY_20TH]),
    "Archaeological Analysis": create_lens("Interprets material remains, artifacts, and environmental data to understand past human societies.", eras=[E4_19TH]),
    "Cultural Materialism": create_lens("Examines the relationship between culture and material conditions (infrastructure, technology, environment) (Harris).", eras=[E6_LATE_20TH]),
    "Ethnomethodology": create_lens("Study of the methods people use to understand and produce the social order in which they live (Garfinkel).", eras=[E6_LATE_20TH]),
    "Great Man Theory": create_lens("History explained primarily by the impact of highly influential individuals (Carlyle).", eras=[E4_19TH]),
    "Historical Contextualism": create_lens("Emphasis on understanding the work within its original historical and cultural context.", eras=[E4_19TH]),
    "New Historicism": create_lens("Analyzes the work alongside other contemporary texts and discourses, emphasizing the circulation of social energy (Greenblatt).", eras=[E6_LATE_20TH]),
    "Oral History": create_lens("Analyzes spoken accounts, personal narratives, and traditions as historical evidence.", eras=[E5_EARLY_20TH]),
    "Presentism": create_lens("Analyzes the tendency to interpret the past through the lens of modern values and concepts (often as a critique).", eras=[E6_LATE_20TH]),
    
    # v9.4b: Zeitgeist Removed. It is now a dedicated analysis mode.

    # Philosophy & Ethics
    "Absurdism": create_lens("Focus on the conflict between the human tendency to seek inherent value and the meaningless, irrational universe (Camus).", eras=[E5_EARLY_20TH]),
    "Analytic Philosophy": create_lens("Emphasis on clarity, logic, argumentation, and the analysis of language (Russell, Wittgenstein).", eras=[E5_EARLY_20TH]),
    "Aristotelianism": create_lens("Focus on virtue, rhetoric (ethos/pathos/logos), causality, and empirical observation.", eras=[E1_ANCIENT]),
    "Bushido": create_lens("The ethical code of the samurai; focus on honor, loyalty, duty, and martial prowess.", eras=[E2_MEDIEVAL]),
    "Chivalry": create_lens("The medieval knightly system; focus on valor, courtesy, honor, and service.", eras=[E2_MEDIEVAL]),
    "Confucianism": create_lens("Emphasis on ethics, social harmony, filial piety, ritual (li), and self-cultivation.", eras=[E1_ANCIENT]),
    
    # v9.4b Refactor
    "Deconstruction": create_lens("Focus on revealing the instability of meaning in texts, analyzing binary oppositions, and 'différance' (Derrida).", eras=[E6_LATE_20TH], prompt_name="Deconstruction (Derrida)"),
    
    "Dialectical Materialism": create_lens("Philosophical basis of Marxism; change driven by material contradictions and class struggle.", eras=[E4_19TH]),
    "Empiricism": create_lens("Knowledge derived primarily from sensory experience and observation (Locke, Hume).", eras=[E3_ENLIGHTENMENT]),
    "Epicureanism": create_lens("Focus on attaining pleasure (defined as tranquility/ataraxia) and avoiding pain.", eras=[E1_ANCIENT]),
    # "Existentialism" moved to Toolkit section v9.5a
    "Hermeneutics": create_lens("The theory and methodology of interpretation, especially of texts, wisdom literature, and philosophical texts (Gadamer).", eras=[E5_EARLY_20TH]),
    
    # v9.4b Refactor
    "Hegelian Idealism": create_lens("Reality is fundamentally mental or spiritual; focus on the dialectical progression of history and ideas (Hegel).", eras=[E4_19TH], prompt_name="Idealism (Hegelian)"),
    
    # v9.4b Refactor
    "Kantianism": create_lens("Focus on moral duties, reason, and universalizable rules (the Categorical Imperative) (Kant).", eras=[E3_ENLIGHTENMENT], prompt_name="Kantianism (Categorical Imperative)"),

    # v9.4b Refactor
    "Legalism": create_lens(description="Focus on strict adherence to law, administrative efficiency, and state power, as developed in ancient China (Han Feizi).", eras=[E1_ANCIENT], prompt_name="Legalism (Chinese Philosophy)"),
    
    "Nihilism": create_lens("The rejection of objective meaning, value, and truth; the belief that life is meaningless.", eras=[E4_19TH]),
    
    # v9.4b Refactor
    "Objectivism": create_lens("Focus on reason, individualism, rational self-interest, and laissez-faire capitalism (Rand).", eras=[E5_EARLY_20TH], prompt_name="Objectivism (Rand)"),
    
    "Phenomenology": create_lens("Study of the structures of consciousness and subjective experience (Husserl, Heidegger).", eras=[E5_EARLY_20TH]),
    
    # v9.4b Refactor
    "Platonism": create_lens("Focus on the distinction between the perceived material reality and the higher, abstract reality of Forms (Ideals) (Plato).", eras=[E1_ANCIENT], prompt_name="Platonism (Theory of Forms)"),
    
    # "Post-Structuralism" moved to Toolkit section v9.5a
    
    "Pragmatism": create_lens("Focus on the practical consequences and utility of ideas and beliefs (James, Dewey).", eras=[E4_19TH]),
    "Rationalism": create_lens("Reason as the chief source and test of knowledge, independent of sensory experience (Descartes, Spinoza).", eras=[E3_ENLIGHTENMENT]),
    # "Stoicism" moved to Toolkit section v9.5a
    "Taoism": create_lens("Emphasis on living in harmony with the Tao (the Way), naturalness, simplicity, and wu wei (effortless action).", eras=[E1_ANCIENT]),
    "Transcendentalism": create_lens(description="Focuses on the inherent goodness of humanity and nature, and the primacy of individual intuition and self-reliance (Emerson, Thoreau).", eras=[E4_19TH]),
    "Virtue Ethics": create_lens("Focus on moral character and virtues (eudaimonia) rather than rules (deontology) or consequences (utilitarianism).", eras=[E1_ANCIENT]),
    
    # Psychology & Cognitive Science
    "Attachment Theory": create_lens("Examines long-term interpersonal relationships and the bonds between humans (Bowlby, Ainsworth).", eras=[E6_LATE_20TH]),
    "Behaviorism": create_lens("Focus on observable behavior and conditioning, rather than internal mental states (Skinner, Watson).", eras=[E5_EARLY_20TH]),
    
    # v9.4b Refactor
    "CBT Principles": create_lens("Examines the relationship between thoughts, feelings, and behaviors; identifying cognitive distortions (Cognitive Behavioral Therapy).", eras=[E6_LATE_20TH], prompt_name="Cognitive Behavioral Therapy (CBT) Principles"),
    
    "Cognitive Dissonance": create_lens("Analyzes the mental discomfort experienced when holding contradictory beliefs, values, or ideas (Festinger).", eras=[E5_EARLY_20TH]),
    "Cognitive Linguistics": create_lens("Study of language based on human experience, conceptual metaphors, and cognition (Lakoff).", eras=[E6_LATE_20TH]),
    "Evolutionary Psychology": create_lens("Explains psychological traits and behaviors as evolved adaptations resulting from natural selection.", eras=[E7_CONTEMPORARY]),
    
    # "Freudianism" moved to Toolkit section v9.5a
    
    "Gestalt Psychology": create_lens("Focus on perception and the idea that the whole is greater than the sum of its parts; principles of grouping.", eras=[E5_EARLY_20TH]),
    "Humanistic Psychology": create_lens("Emphasis on individual potential, free will, and the drive toward self-actualization (Rogers, Maslow).", eras=[E6_LATE_20TH]),
    
    # "Jungian Analysis" moved to Toolkit section v9.5a
    
    # v9.4b Refactor
    "Lacanianism": create_lens("Focus on the mirror stage, the Imaginary, Symbolic, and Real orders, and the structure of language (Lacan).", eras=[E6_LATE_20TH], prompt_name="Lacanian Psychoanalysis"),
    
    "Maslow's Hierarchy": create_lens("Analyzes motivation based on a hierarchy of needs, from physiological to self-actualization.", eras=[E5_EARLY_20TH]),
    "Trauma Studies": create_lens("Examines the psychological, cultural, and societal impact of traumatic events.", eras=[E6_LATE_20TH]),

    # Rhetoric & Literary Theory
    # v9.4b Refactor
    "Archetypal Criticism": create_lens("Analyzes myths, symbols, genres, and recurring patterns in literature (Northrop Frye).", eras=[E5_EARLY_20TH], prompt_name="Archetypal Criticism (Frye)"),

    "Bakhtinian Dialogism": create_lens("Focus on dialogue, heteroglossia (multiple voices), and the carnivalesque in texts (Mikhail Bakhtin).", eras=[E6_LATE_20TH]),

    "Close Reading": create_lens("Detailed, careful analysis of the specific features, language, and structure of a text.", eras=[E5_EARLY_20TH]),
    
    # v9.4b Refactor
    "Defamiliarization": create_lens("Technique of presenting common things in an unfamiliar way to enhance perception (Viktor Shklovsky).", eras=[E5_EARLY_20TH], prompt_name="Defamiliarization (Shklovsky)"),
    
    # v9.4b Refactor
    "Dramatism": create_lens("Analyzes human motivation and relationships using the pentad: Act, Scene, Agent, Agency, Purpose (Kenneth Burke).", eras=[E5_EARLY_20TH], prompt_name="Dramatism (Burke)"),
    
    "Genre Studies": create_lens("Examines the conventions, structures, and evolution of different literary or artistic genres.", eras=[E6_LATE_20TH]),
    "Intertextuality": create_lens("Analyzes the relationship between texts; how one text shapes the meaning of another (Kristeva).", eras=[E6_LATE_20TH]),
    "Narratology": create_lens("The structural study of narrative; analyzing story, discourse, focalization, and narrative voice (Genette).", eras=[E6_LATE_20TH]),
    
    # v9.4b Refactor
    "Reader-Response": create_lens("Focus on the reader's experience and active role in creating the meaning of the text (Fish, Iser).", eras=[E6_LATE_20TH], prompt_name="Reader-Response Criticism"),
    
    # v9.4b Refactor
    "Rhetorical Analysis": create_lens("Analyzes the means of persuasion: ethical appeal (ethos), emotional appeal (pathos), and logical appeal (logos).", eras=[E1_ANCIENT], prompt_name="Rhetorical Analysis (Ethos/Pathos/Logos)"),
    
    "Stylistics": create_lens("Study of linguistic style, tone, and the interpretation of texts based on linguistic features.", eras=[E5_EARLY_20TH]),

    # Sociology & Systems
    # v9.4b Refactor: Kept (ANT) in UI name as it's common usage, but added standard prompt_name.
    "Actor-Network Theory (ANT)": create_lens("Traces connections between human and non-human actors (actants), treating them symmetrically (Latour, Callon).", eras=[E6_LATE_20TH], prompt_name="Actor-Network Theory"),
    
    # "Bourdieuian Analysis" moved to Toolkit section v9.5a
    
    "Chaos Theory": create_lens("Focus on dynamic systems highly sensitive to initial conditions (the butterfly effect) and patterns within apparent randomness.", eras=[E6_LATE_20TH]),
    "Conflict Theory": create_lens("Analyzes society based on the conflicts, power struggles, and inequalities between different social groups.", eras=[E4_19TH]),
    
    # "Critical Theory" moved to Toolkit section v9.5a
    
    "Cybernetics": create_lens("Study of communication, control systems, and feedback loops in both machines and living organisms.", eras=[E5_EARLY_20TH]),
    
    # v9.4b Refactor
    "Functionalism": create_lens("Analyzes society as a complex system whose parts work together to promote solidarity and stability (Durkheim, Parsons).", eras=[E5_EARLY_20TH], prompt_name="Functionalism (Sociological)"),
    
    "Network Analysis": create_lens("Maps and measures relationships and flows between people, groups, organizations, or other information-processing entities.", eras=[E7_CONTEMPORARY]),
    "Social Constructionism": create_lens("Examines how shared understandings and meanings of the world are jointly constructed through social interaction.", eras=[E6_LATE_20TH]),
    "Symbolic Interactionism": create_lens("Focus on how individuals interact using shared symbols and meanings to create their social reality (Mead, Blumer).", eras=[E6_LATE_20TH]),
    "Systems Theory": create_lens("Analyzes complex systems and their interactions, focusing on feedback loops, boundaries, inputs/outputs, and emergent properties.", eras=[E5_EARLY_20TH]),

    # Theology, Religion & Mythology
    
    # Buddhism
    "Buddhism: Chan / Zen": create_lens(description="Focus on direct experience, meditation (zazen), kōans, and the nature of mind as taught in Chinese/Japanese traditions.", eras=[E2_MEDIEVAL]),
    "Buddhism: Theravāda": create_lens(description="Focus on the Pali Canon, the Four Noble Truths, the Eightfold Path, and the path of the Arhat ('School of the Elders').", eras=[E1_ANCIENT]),
    "Buddhism: Tibetan (Vajrayāna)": create_lens(description="Focus on tantric practices, compassion (bodhicitta), the concept of emptiness (śūnyatā), and the role of the guru (lama).", eras=[E2_MEDIEVAL]),
    
    # Christianity (v9.4b Refactor: Simplified Naming)
    "Catholic Theology": create_lens(description="Analyzes through the lens of Catholic doctrine, natural law, sacramentology, tradition, and magisterial teaching.", eras=[E1_ANCIENT, E2_MEDIEVAL], prompt_name="Christianity: Catholic Theology"),
    "Liberation Theology": create_lens(description="Emphasis on liberation from social, political, and economic oppression, interpreting scripture through the experience of the poor.", eras=[E6_LATE_20TH], prompt_name="Christianity: Liberation Theology"),
    "Protestant Theology": create_lens(description="Analyzes through the lens of Protestant doctrine, focusing on grace (Sola Gratia), faith (Sola Fide), and scripture (Sola Scriptura).", eras=[E2_MEDIEVAL], prompt_name="Christianity: Protestant Theology"),

    # Hinduism
    "Hinduism: Advaita Vedanta": create_lens(description="Focuses on non-dualistic Hindu philosophy; the unity of Atman (the self) and Brahman (the ultimate reality) (Shankara).", eras=[E2_MEDIEVAL]),
    "Hinduism: General Philosophy": create_lens(description="Focus on core concepts across various schools, such as dharma (duty), karma (action/consequence), maya (illusion), and moksha (liberation).", eras=[E1_ANCIENT]),

    # Islam
    "Islam: Sufism": create_lens(description="Focuses on Islamic mysticism, the inner spiritual path (tariqa), divine love, and the poetry of figures like Rumi and Hafez.", eras=[E2_MEDIEVAL]),
    
    # v9.4b Refactor
    "Islamic Theology (Kalam)": create_lens(description="Focus on Islamic scholastic theology, reason, scriptural interpretation, and doctrinal debates.", eras=[E2_MEDIEVAL], prompt_name="Islam: Theology (Kalam)"),

    # Judaism
    "Judaism: Kabbalah": create_lens(description="Analyzes esoteric Jewish mysticism, focusing on symbolic interpretation, the Sefirot (divine emanations), and the nature of divinity.", eras=[E2_MEDIEVAL]),
    "Judaism: Talmudic/Rabbinic": create_lens(description="Focus on textual interpretation (midrash), law (halakha), ethics, and debate within the Rabbinic tradition.", eras=[E1_ANCIENT]),

    # Mythology & Comparative
    # v9.4b Refactor
    "Comparative Mythology": create_lens(description="Focus on the monomyth (hero's journey), universal archetypes, and structural patterns across different cultures (Joseph Campbell).", eras=[E6_LATE_20TH], prompt_name="Comparative Mythology (Campbell)"),
    
    "Mythology: Egyptian": create_lens(description="Analysis based on the Egyptian pantheon, cosmology, concepts of Ma'at (order/truth), divine kingship, and the afterlife.", eras=[E1_ANCIENT]),
    "Mythology: Greco-Roman": create_lens(description="Analysis of the Olympian/Roman pantheon, heroic cycles (e.g., Homeric epics), fate (moira), hubris, and the relationship between gods and mortals.", eras=[E1_ANCIENT]),
    "Mythology: Mesoamerican": create_lens(description="Analysis based on Aztec, Maya, and other regional pantheons, focusing on cyclical time, sacrifice, duality, and cosmology.", eras=[E1_ANCIENT, E2_MEDIEVAL]),
    "Mythology: Norse": create_lens(description="Analysis based on the Norse pantheon (Æsir/Vanir), concepts of fate (Wyrd), honor, the Nine Worlds, and the cycle of Ragnarök.", eras=[E2_MEDIEVAL]),
    "Mythopoeic Analysis": create_lens(description="Analyzes the creation and function of myths within a culture, and the human propensity to create mythology.", eras=[E6_LATE_20TH]),

    # Other
    "Secular Humanism": create_lens(description="Focus on human reason, ethics, and justice, affirming human agency and rejecting religious dogma or supernaturalism.", eras=[E5_EARLY_20TH]),
    "Shinto": create_lens(description="Analysis based on Japanese indigenous beliefs, focusing on kami (spirits), purity (kegare), ritual, and the sacredness of nature.", eras=[E2_MEDIEVAL]),
}


# -----------------------------------------------------------------------------
# 2. LENSES BY DISCIPLINE (The Library)
# Organized by academic field.
# v9.5a: Updated to reflect lenses moved to the Toolkit architecture (no changes needed here, only in definitions).
# -----------------------------------------------------------------------------

LENSES_HIERARCHY = {
    "Art History & Visual Culture": [
        "Baroque Aesthetics", # v9.4b Updated
        "Cubism",
        "Dadaism",
        "Iconography/Iconology",
        "Impressionism",
        "Renaissance Aesthetics", # v9.4b Updated
        "Surrealism",
    ],
    "Aesthetics & Literary Theory": [
        "Aestheticism",
        "Affect Theory",
        "Archetypal Criticism", # v9.4b Updated
        "Avant-Garde Studies",
        "Bakhtinian Dialogism",
        "Biographical Analysis", # v9.4b Updated
        "Close Reading",
        "Deconstruction", # v9.4b Updated
        "Defamiliarization", # v9.4b Updated
        "Dramatism", # v9.4b Updated
        "Ecocriticism",
        "Formalism", # v9.4b Updated
        "Genre Studies",
        "Hermeneutics",
        "Impressionistic Criticism",
        "Intentional Fallacy",
        "Intertextuality",
        "Modernism",
        "Narratology",
        "Postmodernism",
        "Pragmatic Criticism",
        "Reader-Response", # v9.4b Updated
        "Reception Theory",
        "Rhetorical Analysis", # v9.4b Updated
        "Romanticism",
        "Semiotics", # v9.4b Updated
        "Structuralism",
        "Stylistics",
    ],
    "Media & Communication Studies": [
        "Auteur Theory", # v9.4b Updated
        "Cybernetics",
        "Ludology", # v9.4b Updated
        "Media Ecology", # v9.4b Updated
    ],
    "Cultural & Identity Studies": [
        "Afrofuturism",
        "Critical Race Theory (CRT)",
        "Disability Studies",
        "Feminism", # v9.4b Updated
        "Gender Studies",
        "Indigenous Methodologies",
        "Intersectionality",
        "Orientalism",
        "Postcolonialism",
        "Queer Theory", # v9.4b Updated
        "Subaltern Studies",
        "Whiteness Studies",
    ],
    "Economics & Political Science": [
        "Anarchism",
        "Behavioral Economics",
        "Classical Liberalism",
        "Communitarianism",
        "Game Theory",
        "Geopolitical Analysis",
        "Libertarianism",
        "Marxism", # v9.4b Updated
        "Neoliberalism",
        "Political Economy",
        "Realpolitik",
        "Social Contract Theory",
        "Utilitarianism",
    ],
    "History & Anthropology": [
        "Annales School",
        "Archaeological Analysis",
        "Cultural Materialism",
        "Ethnomethodology",
        "Great Man Theory",
        "Historical Contextualism",
        "New Historicism",
        "Oral History",
        "Presentism",
        # "Zeitgeist" removed v9.4b
    ],
    "Philosophy: Ethics & Morality": [
        "Bushido",
        "Chivalry",
        "Kantianism", # v9.4b Updated
        "Objectivism", # v9.4b Updated
        "Secular Humanism",
        "Virtue Ethics",
    ],
    "Philosophy: Metaphysics & Epistemology": [
        "Absurdism",
        "Analytic Philosophy",
        "Deconstruction", # Also in Literary Theory
        "Empiricism",
        "Hegelian Idealism", # v9.4b Updated
        "Nihilism",
        "Phenomenology",
        "Platonism", # v9.4b Updated
        "Pragmatism",
        "Rationalism",
    ],
    "Philosophy: Social & Political Thought": [
        "Aristotelianism",
        "Confucianism",
        "Dialectical Materialism",
        "Existentialism",
        "Legalism", # v9.4b Updated
        "Post-Structuralism", # v9.4b Updated
        "Stoicism",
        "Taoism",
        "Transcendentalism",
    ],
    "Psychology & Cognitive Science": [
        "Attachment Theory",
        "Behaviorism",
        "CBT Principles", # v9.4b Updated
        "Cognitive Dissonance",
        "Cognitive Linguistics",
        "Evolutionary Psychology",
        "Freudianism", # v9.4b Updated
        "Gestalt Psychology",
        "Humanistic Psychology",
        "Jungian Analysis", # v9.4b Updated
        "Lacanianism", # v9.4b Updated
        "Maslow's Hierarchy",
        "Trauma Studies",
    ],
    "Sociology & Systems Theory": [
        "Actor-Network Theory (ANT)",
        "Bourdieuian Analysis", # v9.4b Updated
        "Chaos Theory",
        "Conflict Theory",
        "Critical Theory", # v9.4b Updated
        "Functionalism", # v9.4b Updated
        "Network Analysis",
        "Social Constructionism",
        "Symbolic Interactionism",
        "Systems Theory",
    ],
    "Mythology & Comparative Religion": [
        "Comparative Mythology", # v9.4b Updated
        "Mythology: Egyptian",
        "Mythology: Greco-Roman",
        "Mythology: Mesoamerican",
        "Mythology: Norse",
        "Mythopoeic Analysis",
        "Shinto",
    ],
    "Theology & Religious Studies": [
        "Buddhism: Chan / Zen",
        "Buddhism: Theravāda",
        "Buddhism: Tibetan (Vajrayāna)",
        "Catholic Theology", # v9.4b Updated
        "Hinduism: Advaita Vedanta",
        "Hinduism: General Philosophy",
        "Islam: Sufism",
        "Islamic Theology (Kalam)", # v9.4b Updated
        "Judaism: Kabbalah",
        "Judaism: Talmudic/Rabbinic",
        "Liberation Theology", # v9.4b Updated
        "Protestant Theology", # v9.4b Updated
    ],
}

# -----------------------------------------------------------------------------
# 3. LENSES BY FUNCTION (The Workshop)
# Organized by the Three Tiers of Inquiry.
# v9.5a: Updated to reflect lenses moved to the Toolkit architecture (no changes needed here, only in definitions).
# -----------------------------------------------------------------------------

LENSES_FUNCTIONAL = {
    "Tier 1: Contextual (What/Who/When)": [
        "Annales School",
        "Archaeological Analysis",
        "Biographical Analysis", # v9.4b Updated
        "Cultural Materialism",
        "Geopolitical Analysis",
        "Great Man Theory",
        "Historical Contextualism",
        "Intentional Fallacy",
        "New Historicism",
        "Oral History",
        "Political Economy",
        "Presentism",
        "Reception Theory",
        "Social Contract Theory",
        # "Zeitgeist" removed v9.4b
    ],
    "Tier 2: Mechanical (How it Works)": [
        "Aestheticism",
        "Affect Theory",
        "Auteur Theory", # v9.4b Updated
        "Behavioral Economics",
        "Behaviorism",
        "Chaos Theory",
        "Close Reading",
        "Cognitive Linguistics",
        "Cybernetics",
        "Defamiliarization", # v9.4b Updated
        "Dramatism", # v9.4b Updated
        "Ethnomethodology",
        "Formalism", # v9.4b Updated
        "Functionalism", # v9.4b Updated
        "Game Theory",
        "Genre Studies",
        "Gestalt Psychology",
        "Iconography/Iconology",
        "Intertextuality",
        "Ludology", # v9.4b Updated
        "Media Ecology", # v9.4b Updated
        "Narratology",
        "Network Analysis",
        "Rhetorical Analysis", # v9.4b Updated
        "Semiotics", # v9.4b Updated
        "Structuralism",
        "Stylistics",
        "Systems Theory",
    ],
    # Tier 3 combines many diverse interpretive frameworks.
    "Tier 3: Interpretive (Why it Matters)": [
        # Philosophy & Ethics
        "Absurdism",
        "Analytic Philosophy",
        "Anarchism",
        "Aristotelianism",
        "Bushido",
        "Chivalry",
        "Communitarianism",
        "Confucianism",
        "Deconstruction", # v9.4b Updated
        "Dialectical Materialism",
        "Empiricism",
        "Epicureanism",
        "Existentialism",
        "Hermeneutics",
        "Hegelian Idealism", # v9.4b Updated
        "Kantianism", # v9.4b Updated
        "Legalism", # v9.4b Updated
        "Libertarianism",
        "Nihilism",
        "Objectivism", # v9.4b Updated
        "Phenomenology",
        "Platonism", # v9.4b Updated
        "Post-Structuralism", # v9.4b Updated
        "Pragmatism",
        "Rationalism",
        "Stoicism",
        "Taoism",
        "Transcendentalism",
        "Utilitarianism",
        "Virtue Ethics",

        # Psychology
        "Attachment Theory",
        "CBT Principles", # v9.4b Updated
        "Cognitive Dissonance",
        "Evolutionary Psychology",
        "Freudianism", # v9.4b Updated
        "Humanistic Psychology",
        "Jungian Analysis", # v9.4b Updated
        "Lacanianism", # v9.4b Updated
        "Maslow's Hierarchy",
        "Trauma Studies",

        # Cultural & Identity
        "Afrofuturism",
        "Critical Race Theory (CRT)",
        "Disability Studies",
        "Feminism", # v9.4b Updated
        "Gender Studies",
        "Intersectionality",
        "Indigenous Methodologies",
        "Orientalism",
        "Postcolonialism",
        "Queer Theory", # v9.4b Updated
        "Subaltern Studies",
        "Whiteness Studies",

        # Sociology & Economics
        "Actor-Network Theory (ANT)",
        "Bourdieuian Analysis", # v9.4b Updated
        "Classical Liberalism",
        "Conflict Theory",
        "Critical Theory", # v9.4b Updated
        "Marxism", # v9.4b Updated
        "Neoliberalism",
        "Realpolitik",
        "Social Constructionism",
        "Symbolic Interactionism",

        # Art & Literary Theory
        "Archetypal Criticism", # v9.4b Updated
        "Avant-Garde Studies",
        "Bakhtinian Dialogism",
        "Baroque Aesthetics", # v9.4b Updated
        "Cubism",
        "Dadaism",
        "Ecocriticism",
        "Impressionism",
        "Impressionistic Criticism",
        "Modernism",
        "Postmodernism",
        "Pragmatic Criticism",
        "Reader-Response", # v9.4b Updated
        "Renaissance Aesthetics", # v9.4b Updated
        "Romanticism",
        "Surrealism",

        # Theology, Religion & Mythology
        "Buddhism: Chan / Zen",
        "Buddhism: Theravāda",
        "Buddhism: Tibetan (Vajrayāna)",
        "Catholic Theology", # v9.4b Updated
        "Comparative Mythology", # v9.4b Updated
        "Hinduism: Advaita Vedanta",
        "Hinduism: General Philosophy",
        "Islam: Sufism",
        "Islamic Theology (Kalam)", # v9.4b Updated
        "Judaism: Kabbalah",
        "Judaism: Talmudic/Rabbinic",
        "Liberation Theology", # v9.4b Updated
        "Mythology: Egyptian",
        "Mythology: Greco-Roman",
        "Mythology: Mesoamerican",
        "Mythology: Norse",
        "Mythopoeic Analysis",
        "Protestant Theology", # v9.4b Updated
        "Secular Humanism",
        "Shinto",
    ],
}

# -----------------------------------------------------------------------------
# 4. LENSES BY ERA (The Timeline)
# Dynamically generated from LENS_DEFINITIONS['eras'] tags.
# -----------------------------------------------------------------------------

# Define the chronological order of Eras
ERA_ORDER = [
    E1_ANCIENT,
    E2_MEDIEVAL,
    E3_ENLIGHTENMENT,
    E4_19TH,
    E5_EARLY_20TH,
    E6_LATE_20TH,
    E7_CONTEMPORARY
]

# Initialize the dictionary with ordered keys and empty lists
LENSES_BY_ERA = {era: [] for era in ERA_ORDER}

# Populate the dictionary dynamically
for lens_name, lens_data in LENS_DEFINITIONS.items():
    for era in lens_data.get('eras', []):
        if era in LENSES_BY_ERA:
            LENSES_BY_ERA[era].append(lens_name)
        else:
            # Safety check during development
            print(f"LENS LIBRARY WARNING: Era '{era}' used by lens '{lens_name}' is not defined in ERA_ORDER.")


# Enforce Alphabetization of all contents (except Era keys)
for structure in [LENSES_HIERARCHY, LENSES_FUNCTIONAL]:
    for key in structure:
        structure[key].sort()

# Era needs special handling to sort values but maintain key order
for key in LENSES_BY_ERA:
    LENSES_BY_ERA[key].sort()


# -----------------------------------------------------------------------------
# 5. PERSONA STYLE GUIDES (The Interpreter Model)
# Defines specific voice, tone, and formatting for abstract lenses.
# v9.4b: Updated keys to match simplified UI names.
# -----------------------------------------------------------------------------

PERSONA_STYLE_GUIDES = {
    "Systems Theory": {
        "persona": "The Systems Analyst (e.g., A detached field analyst inspired by Donella Meadows)",
        "guide": """
        Adopt the persona of a detached, clinical field analyst. 
        Structure the response as a technical report. 
        Use precise, objective language. 
        Prioritize identifying feedback loops, inputs, outputs, boundaries, and emergent properties. 
        Avoid subjective interpretation of meaning; focus entirely on mechanics and dynamics.
        Use mandatory section headings: 1. System Boundaries, 2. Key Components and Interactions, 3. Feedback Mechanisms, 4. Emergent Behavior.
        """
    },
    "Formalism": { # v9.4b Updated Key
        "persona": "The Formalist Critic (e.g., A stern academic reminiscent of Cleanth Brooks)",
        "guide": """
        Adopt the persona of a stern, authoritative academic focused solely on the work itself. 
        Explicitly reject any consideration of authorial intent or historical context ("The text must stand on its own"). 
        Use sophisticated literary terminology (irony, paradox, ambiguity, tension). 
        The tone should be rigorous and exacting. 
        Structure the analysis as a meticulous dissection of the work's internal structure and form.
        """
    },
    "Ecocriticism": {
        "persona": "The Ecological Advocate (e.g., A passionate naturalist inspired by Rachel Carson)",
        "guide": """
        Adopt the persona of a passionate, observant naturalist and advocate. 
        The tone should be earnest, perhaps slightly melancholic or urgent, but always deeply connected to the natural world. 
        Analyze how the work represents the environment, the relationship between humans and nature, and underlying ecological ethics (anthropocentrism vs biocentrism). 
        Use evocative descriptions of nature (if present in the work) and connect them to broader environmental concerns.
        """
    },
    "Semiotics": { # v9.4b Updated Key
        "persona": "The Semiotician (e.g., A meticulous decoder inspired by Roland Barthes)",
        "guide": """
        Adopt the persona of a meticulous decoder of signs. 
        The tone should be analytical and inquisitive, constantly questioning the surface meaning. 
        Structure the response by identifying key signs within the work and breaking them down into the Signifier (the form) and the Signified (the concept). 
        Analyze the interplay between denotation (literal meaning) and connotation (cultural association/myth). 
        Use specialized terminology precisely (e.g., index, icon, symbol).
        """
    },
    "Deconstruction": { # v9.4b Updated Key
        "persona": "The Deconstructionist (e.g., A playful yet challenging philosopher inspired by Derrida)",
        "guide": """
        Adopt a persona that is playful, elusive, and challenging. The language should be complex, utilizing wordplay and questioning the stability of meaning. 
        The goal is not to find *the* meaning, but to reveal the instability of meaning within the text (différance). 
        Identify binary oppositions and demonstrate how the text privileges one over the other, then overturn that hierarchy. 
        Focus on contradictions, gaps (aporia), and the limitations of language itself.
        """
    },
    "Actor-Network Theory (ANT)": {
        "persona": "The ANT Ethnographer (e.g., A rigorous sociologist inspired by Bruno Latour)",
        "guide": """
        Adopt the persona of a rigorous ethnographer tracing associations. 
        Crucially, treat all elements (human and non-human) as "actants" with equal agency. 
        The tone must be strictly neutral and descriptive ("Follow the actors"). 
        Avoid imposing pre-existing social theories. 
        Focus on mapping the network: how actants are enrolled, how the network is stabilized or destabilized, and the transformations that occur.
        """
    },
    "Mythology: Norse": {
        "persona": "The Skald (An ancient Norse storyteller and poet)",
        "guide": """
        Adopt the persona of a Norse Skald. The tone should be epic, somewhat fatalistic, and deeply respectful of the gods and heroes. 
        Use vivid, rhythmic language, incorporating kennings (e.g., "whale-road" for the sea) and alliteration where appropriate, but ensure the analysis remains clear.
        Focus on themes of honor, fate (Wyrd), the struggles between the Æsir/Vanir and the Jötnar, and the looming shadow of Ragnarök. 
        Relate the elements of the work to the cosmology of the Nine Worlds.
        Begin the analysis with an invocation or a traditional storytelling opening.
        """
    },
    "Mythology: Greco-Roman": {
        "persona": "Homer (The archetypal epic poet of ancient Greece)",
        "guide": """
        Adopt the persona of Homer (or a poet in the Homeric tradition). The tone must be grand, formal, and eloquent. 
        Use elevated language, invoking the Muses at the start of the analysis.
        Focus on the intervention of the Olympian gods in mortal affairs, the nature of heroism (areté), the dangers of pride (hubris), and the inexorability of fate (moira).
        Analyze the work as if it were a scene in an epic poem, paying attention to character epithets and dramatic irony.
        """
    },
}

# -----------------------------------------------------------------------------
# 6. PERSONA POOLS (The Persona/God's-Eye Model)
# Maps lenses to a list of famous proponents or central figures.
# v9.4b: Updated keys to match simplified UI names.
# -----------------------------------------------------------------------------

PERSONA_POOL = {
    "Stoicism": ["Marcus Aurelius", "Seneca the Younger", "Epictetus", "Zeno of Citium"],
    "Existentialism": ["Jean-Paul Sartre", "Simone de Beauvoir", "Albert Camus", "Søren Kierkegaard", "Friedrich Nietzsche"],
    "Freudianism": ["Sigmund Freud"], # v9.4b Updated Key
    "Jungian Analysis": ["Carl Jung", "Marie-Louise von Franz"], # v9.4b Updated Key
    "Marxism": ["Karl Marx", "Friedrich Engels", "Walter Benjamin", "Georg Lukács", "Terry Eagleton", "Antonio Gramsci"], # v9.5a Added Gramsci
    "Post-Structuralism": ["Michel Foucault"], # v9.4b Updated Key
    "Objectivism": ["Ayn Rand"], # v9.4b Updated Key
    "Confucianism": ["Confucius", "Mencius"],
    "Platonism": ["Plato"], # v9.4b Updated Key
    "Aristotelianism": ["Aristotle"],
    "Kantianism": ["Immanuel Kant"], # v9.4b Updated Key
    "Feminism": ["Virginia Woolf", "bell hooks", "Judith Butler", "Mary Wollstonecraft", "Simone de Beauvoir"], # v9.5a Added de Beauvoir
    "Bushido": ["Miyamoto Musashi", "Yamamoto Tsunetomo", "Inazo Nitobe"],
    "Chivalry": ["Geoffroi de Charny", "Christine de Pizan", "Sir Thomas Malory"],
    "Transcendentalism": ["Ralph Waldo Emerson", "Henry David Thoreau", "Margaret Fuller"],
    "Postcolonialism": ["Edward Said", "Homi K. Bhabha", "Gayatri Chakravorty Spivak", "Frantz Fanon"], # v9.5a Added
    "Critical Theory": ["Theodor Adorno", "Max Horkheimer", "Herbert Marcuse", "Walter Benjamin"], # v9.5a Added
    "Bourdieuian Analysis": ["Pierre Bourdieu"], # v9.5a Added
    
    # Mythological Personas (God's-Eye View)
    "Mythology: Greco-Roman": ["Zeus", "Athena", "Hades", "Apollo", "Hera", "Odysseus"],
    "Mythology: Norse": ["Odin (The Allfather)", "Thor", "Loki", "Freyja"],
}


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS AND DATA
# -----------------------------------------------------------------------------

def get_lens_data(lens_keyword):
    """Retrieves the data object for a given lens keyword."""
    return LENS_DEFINITIONS.get(lens_keyword)

def _get_all_lenses():
    """Collects all unique lens names from the definitions."""
    return set(LENS_DEFINITIONS.keys())

# A sorted list of all unique lens names, used for validation and UI elements.
SORTED_LENS_NAMES = sorted(list(_get_all_lenses()))

def get_filtered_lenses(hierarchy, selected_categories):
    """
    Returns a sorted list of lenses filtered by the selected categories.
    Used primarily for the multi-select UI in Symposium mode.
    """
    filtered_lenses = set()
    for category in selected_categories:
        if category in hierarchy:
            filtered_lenses.update(hierarchy[category])
    return sorted(list(filtered_lenses))

# --- VALIDATION CHECK (Ensure consistency across structures) ---
_all_defined_lenses = _get_all_lenses()
_structures_to_check = [LENSES_HIERARCHY, LENSES_FUNCTIONAL]

for structure in _structures_to_check:
    for category, lenses in structure.items():
        for lens_name in lenses:
            if lens_name not in _all_defined_lenses:
                # This is a development-time check to catch migration errors.
                print(f"LENS LIBRARY ERROR: Lens '{lens_name}' found in category '{category}' but is not present in LENS_DEFINITIONS.")
