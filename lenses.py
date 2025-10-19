# =============================================================================
# JANUS ENGINE v10.0 LENS LIBRARY
# This file defines the analytical frameworks (lenses) used by the Janus Engine.
# v10.0: Architecture shift to Generative & Adaptive. The engine now dynamically generates concepts. 
#        'conceptual_primer', 'sub_primers', and 'PERSONA_STYLE_GUIDES' are deprecated.
# =============================================================================

# -----------------------------------------------------------------------------
# 1. LENS DEFINITIONS (The Source of Truth)
# Defines the core data object for each lens.
# -----------------------------------------------------------------------------

# Helper function to create a standard lens object
# v10.0: Removed validation check for primer/sub_primers as they are now legacy fields.
def create_lens(description, conceptual_primer=None, requires_nuance=False, eras=None, prompt_name=None, sub_primers=None):
    if eras is None:
        eras = []
    
    # v10.0 Note: conceptual_primer, sub_primers, and requires_nuance are legacy fields, 
    # no longer actively used by the v10.0 engine pipeline.

    return {
        "description": description,
        "conceptual_primer": conceptual_primer,
        "sub_primers": sub_primers, # v9.5a Added
        "requires_nuance": requires_nuance,
        "eras": eras,
        "prompt_name": prompt_name, # v9.4b Added
    }

# Define Era Constants
# v10.4: Reduced Eurocentrism - renamed "Medieval & Renaissance" → "Medieval Period", "Enlightenment & Early Modernity" → "Early Modern Period"
E1_ANCIENT = "Ancient & Classical (c. 800 BCE – 500 CE)"
E2_MEDIEVAL = "Medieval Period (c. 500 – 1600)"
E3_EARLY_MODERN = "Early Modern Period (c. 1600 – 1800)"
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
        eras=[E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]
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
        eras=[E6_LATE_20TH, E7_CONTEMPORARY]
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
        eras=[E1_ANCIENT, E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]
    ),

    # --- Psychoanalytic Theory Toolkit (v10.1: Consolidated from Freudianism, Jungian Analysis, Lacanianism) ---
    "Psychoanalytic Theory": create_lens(
        description="Analyzes the unconscious mind, psychic structures, defense mechanisms, and symbolic interpretation across multiple psychoanalytic schools.",
        prompt_name="Psychoanalytic Theory",
        # v10.1: Merged sub_primers from Freudian, Jungian, and Lacanian schools
        sub_primers={
            # Freudian School
            "Id, Ego, and Superego Conflict (Freud)": """
            Analyze the psychological structure based on the tripartite model. Identify the drives of the Id (pleasure principle), constraints of the Superego (morality/ideal self), and mediation of the Ego (reality principle).
            Examine internal conflicts arising from these competing forces and how they drive the narrative.
            """,
            "Defense Mechanisms (Freud)": """
            Analyze the defense mechanisms employed to manage anxiety and protect the ego from unacceptable thoughts or feelings.
            Identify instances of repression, projection, denial, displacement, sublimation, and rationalization. Examine how these mechanisms affect behavior and relationships.
            """,
            "Psychosexual Stages and Complexes (Freud - Oedipal/Electra)": """
            Analyze for evidence of unresolved issues from psychosexual development (oral, anal, phallic, latency, genital).
            Focus on the Oedipus or Electra complexes: examine dynamics of desire, rivalry, and identification within family structures and how these complexes shape adult identity and neuroses.
            """,
            "Symbolism and The Unconscious (Freud - Dream Logic)": """
            Analyze as if it were a dream, focusing on manifestation of the unconscious.
            Examine symbols (especially phallic/yonic), slips of the tongue (parapraxes), condensation (compressing multiple ideas into one symbol), and displacement (shifting focus from important to trivial). Interpret the latent content beneath the manifest surface.
            """,
            # Jungian School
            "Archetypal Mapping (Jung - Collective Unconscious)": """
            Analyze by identifying dominant archetypes (e.g., The Hero, The Mentor, The Trickster, The Mother) in characters, symbols, and narrative patterns.
            Examine how these elements draw power from the collective unconscious and structure the work's meaning and emotional impact.
            """,
            "Shadow Work and Integration (Jung)": """
            Focus on the 'Shadow'—the repressed, denied, or unconscious aspects of the personality.
            Analyze how characters confront (or fail to confront) their Shadow, often projected onto antagonists or symbolized by dark imagery. Examine the psychological consequences of this confrontation and potential for integration.
            """,
            "Anima/Animus Dynamics (Jung)": """
            Analyze the dynamics of the contrasexual archetypes: the Anima (unconscious feminine aspect in men) and the Animus (unconscious masculine aspect in women).
            Examine how these figures appear in dreams, fantasies, or projections onto others, and how they influence relationships and personal development.
            """,
            "The Individuation Process (Jung)": """
            Analyze as a narrative of individuation—the journey toward psychological wholeness and self-realization.
            Examine the stages: breakdown of the Persona (social mask), confrontation with the Shadow and Anima/Animus, and realization of the Self (the unifying center of the psyche).
            """,
            # Lacanian School
            "The Mirror Stage and Identity Formation (Lacan)": """
            Analyze the formation of identity through the concept of the mirror stage, where the infant first recognizes itself as a unified being.
            Examine how characters construct their sense of self through images, reflections, and the gaze of others, and how this creates a fundamental alienation (méconnaissance) from one's true fragmented self.
            """,
            "The Symbolic, Imaginary, and Real Orders (Lacan)": """
            Analyze the work through Lacan's three orders: the Symbolic (language, law, social structure), the Imaginary (images, illusions, ego identifications), and the Real (the traumatic, unrepresentable reality beyond symbolization).
            Examine how characters navigate these orders and how the work represents the impossibility of fully accessing the Real.
            """,
            "Desire and the Other (Lacan - 'The Unconscious is Structured Like a Language')": """
            Analyze desire not as biological drive but as fundamentally linguistic and mediated by the Other (the social/symbolic order).
            Examine how characters' desires are shaped by language, how desire is always desire for recognition from the Other, and the role of the objet petit a (the unattainable object-cause of desire).
            """
        },
        eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]
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
        eras=[E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]
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
        eras=[E6_LATE_20TH, E7_CONTEMPORARY]
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
        eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]
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
        eras=[E6_LATE_20TH, E7_CONTEMPORARY]
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
        eras=[E6_LATE_20TH, E7_CONTEMPORARY]
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
        eras=[E6_LATE_20TH, E7_CONTEMPORARY]
    ),

    # === Standard Lenses (Applying the Simplification Principle) ===
    
    # Aesthetics, Art Theory, & Literature
    "Aestheticism": create_lens("Focus on beauty, sensory experience, and the concept of 'art for art's sake.'", eras=[E4_19TH]),
    "Affect Theory": create_lens("Focus on embodied experiences, emotional responses, and the transmission of feeling.", eras=[E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Auteur Theory": create_lens(description="Analyzes a film as a reflection of the director's personal creative vision and style.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Auteur Theory (Film)"),
    
    "Avant-Garde Studies": create_lens("Examines experimental, radical, or unorthodox art movements that challenge conventions.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Baroque Aesthetics": create_lens(description="Analyzes themes of drama, grandeur, movement, emotional intensity, and sensory richness in 17th/18th-century art.", eras=[E3_EARLY_MODERN], prompt_name="Baroque Art Theory"),
    
    # v9.4b Refactor
    "Biographical Analysis": create_lens("Interprets the work based on the author's life, experiences, and context.", eras=[E2_MEDIEVAL], prompt_name="Biographical Criticism"),

    "Abstract Expressionism": create_lens(description="Emphasizes spontaneous, gestural, and non-representational painting; focus on emotional intensity and the artist's inner psyche.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Art Deco": create_lens(description="Analyzes sleek, geometric elegance combined with luxury materials and modern technology; epitomizes the interwar period's optimism.", eras=[E5_EARLY_20TH]),
    "Constructivism": create_lens(description="Focuses on art as a practice for social purposes; geometric abstraction and industrial materials serving revolutionary ideals.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Cubism": create_lens(description="Analyzes the deconstruction of objects into geometric forms and the presentation of multiple viewpoints simultaneously.", eras=[E5_EARLY_20TH]),
    "Dadaism": create_lens(description="Focuses on the rejection of logic and reason, embracing nonsense, irrationality, and anti-art principles.", eras=[E5_EARLY_20TH]),
    "De Stijl": create_lens(description="Analyzes pure abstraction through primary colors, black, white, and geometric forms; pursuit of universal harmony.", eras=[E5_EARLY_20TH]),
    "Expressionism": create_lens(description="Focuses on subjective emotional experience over objective reality; distorted forms and vivid colors to evoke feeling.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Futurism": create_lens(description="Celebrates speed, technology, violence, and modernity; dynamic movement and rejection of the past.", eras=[E5_EARLY_20TH]),
    "Fauvism": create_lens(description="Emphasizes vivid, non-naturalistic color and loose, painterly brushwork; emotional intensity through bold chromatic expression.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Minimalism": create_lens(description="Analyzes reduction to essential forms; simplicity, geometric shapes, and the removal of expressive content.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Pop Art": create_lens(description="Focuses on imagery from popular and mass culture, consumerism, and the blurring of high/low art boundaries.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Suprematism": create_lens(description="Focuses on pure geometric abstraction (circles, squares, lines) and the supremacy of pure artistic feeling over visual depiction (Malevich).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    # Film Movements
    "Cinema Novo": create_lens(description="Brazilian film movement emphasizing social realism, political critique, and revolutionary aesthetics; 'a camera in hand and an idea in the head' (Glauber Rocha).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Dogme 95": create_lens(description="Danish avant-garde film movement advocating handheld cameras, natural lighting, and the 'Vow of Chastity' manifesto to strip away artifice (von Trier, Vinterberg).", eras=[E7_CONTEMPORARY]),
    "Film Noir": create_lens(description="Analyzes cynical narratives, morally ambiguous characters, expressionistic lighting (chiaroscuro), and fatalistic themes in crime dramas.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "French New Wave": create_lens(description="Focus on jump cuts, handheld cameras, breaking the fourth wall, and auteur-driven experimentation challenging classical Hollywood (Godard, Truffaut).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "German Expressionism": create_lens(description="Analyzes distorted sets, extreme shadows, psychological horror, and stylized performances reflecting post-WWI anxiety and inner turmoil.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Italian Neorealism": create_lens(description="Focuses on working-class struggles, non-professional actors, on-location shooting, and humanistic realism in post-WWII Italy (De Sica, Rossellini).", eras=[E5_EARLY_20TH]),
    "Mumblecore": create_lens(description="American independent cinema emphasizing naturalistic dialogue, low budgets, relationship-focused narratives, and DIY aesthetics.", eras=[E7_CONTEMPORARY]),
    "New Hollywood": create_lens(description="Analyzes the auteur-driven, counter-cultural American cinema of the 1960s-70s that challenged studio conventions (Scorsese, Coppola, Altman).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Soviet Montage": create_lens(description="Focus on dynamic editing (montage) to create meaning through juxtaposition; film as ideological tool for revolution (Eisenstein, Vertov).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Third Cinema": create_lens(description="Anti-colonial, anti-imperialist filmmaking from the Global South emphasizing political liberation and rejecting Hollywood/European models (Solanas, Getino).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),

    "Ecocriticism": create_lens("Examines the relationship between literature/art and the physical environment.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Formalism": create_lens("Focus on the intrinsic properties of the text (form, structure, literary devices); rejects external context (New Criticism).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Formalism (New Criticism)"),
    
    "Iconography/Iconology": create_lens("Study of the identification, description, and interpretation of visual images and symbols in art (Panofsky).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Impressionism": create_lens(description="Focuses on capturing the fleeting sensory effect of a moment through light and color, rather than precise detail.", eras=[E4_19TH]),
    "Impressionistic Criticism": create_lens("Subjective appreciation and personal response to the work.", eras=[E4_19TH]),
    "Realism": create_lens(description="Emphasizes truthful, unidealized depiction of everyday life and ordinary people; rejection of romantic idealization and classical subjects.", eras=[E4_19TH]),
    "Intentional Fallacy": create_lens("Argues against using the author's intended meaning as the basis for interpretation (Wimsatt and Beardsley).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Ludology": create_lens(description="Analyzes games based on their rules, mechanics, and systems of play, rather than narrative or visuals (Game Studies).", eras=[E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Ludology (Game Studies)"),
    
    # v9.4b Refactor
    "Media Ecology": create_lens(description="Analyzes how media, independent of content, influence society and perception ('the medium is the message') (McLuhan).", eras=[E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Media Ecology (McLuhan)"),
    
    "Modernism": create_lens("Analyzes themes and styles of early 20th-century art, focusing on experimentation and a break from tradition.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Postmodernism": create_lens("Focus on skepticism toward grand narratives, irony, pastiche, and the blurring of high/low culture.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Pragmatic Criticism": create_lens("Evaluates the work based on its success in achieving a specific effect or purpose on the audience.", eras=[E1_ANCIENT]),
    "Reception Theory": create_lens("Focus on the audience's reception and interpretation of the work over time (Jauss).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Renaissance Aesthetics": create_lens(description="Focuses on humanism, perspective (linear), classical ideals (Greco-Roman), and the elevation of the artist's status.", eras=[E2_MEDIEVAL], prompt_name="Renaissance Art Theory"),
    
    "Romanticism": create_lens("Emphasis on emotion, individualism, the sublime, and the glorification of nature and the past.", eras=[E4_19TH]),
    
    # v9.4b Refactor
    "Semiotics": create_lens("Study of signs and symbols and their interpretation (Saussure, Peirce).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Semiotics (Sign/Signifier)"),
    
    "Structuralism": create_lens("Analyzes the underlying structures, systems, and binary oppositions that govern a work.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Surrealism": create_lens("Focus on the subconscious mind, dreamlike imagery, and the irrational juxtaposition of images (Breton).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    # Cultural & Identity Studies
    "Afrofuturism": create_lens("Examines the intersection of African diaspora culture, technology, and speculative futures.", eras=[E7_CONTEMPORARY]),
    
    # v9.4b Refactor: Added prompt_name for explicit backend instruction, though key remains the same for UI visibility.
    "Critical Race Theory (CRT)": create_lens("Examines society and culture as they relate to the intersection of race, law, and power.", requires_nuance=True, eras=[E7_CONTEMPORARY], prompt_name="Critical Race Theory"),
    
    "Disability Studies": create_lens("Analyzes the representation, experience, and social construction of disability.", requires_nuance=True, eras=[E7_CONTEMPORARY]),
    "Gender Studies": create_lens("Examines the social construction and impact of gender roles, identity, and power.", requires_nuance=True, eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Indigenous Methodologies": create_lens("Utilizes Indigenous knowledge systems, perspectives, and ethical frameworks for analysis.", eras=[E7_CONTEMPORARY]),
    "Intersectionality": create_lens("Analyzes the interconnected nature of social categorizations (race, class, gender) as they create overlapping systems of disadvantage (Crenshaw).", requires_nuance=True, eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Orientalism": create_lens("Analyzes the stereotypical and often patronizing Western representations of the 'Orient' (Said).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    # "Postcolonialism" moved to Toolkit section v9.5a
    "Subaltern Studies": create_lens("Focus on marginalized groups excluded from the dominant historical narrative (Spivak).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Whiteness Studies": create_lens("Examines the construction, history, and implications of 'whiteness' as a racial category.", requires_nuance=True, eras=[E7_CONTEMPORARY]),

    # Economics & Political Science
    "Anarchism": create_lens(description="Advocates for the abolition of all involuntary, coercive forms of hierarchy and the state.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Behavioral Economics": create_lens("Applies psychological insights into human behavior to explain economic decision-making.", eras=[E7_CONTEMPORARY]),
    "Classical Liberalism": create_lens("Focus on individual liberty, consent of the governed, limited government, and free markets (Locke, Smith).", eras=[E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Communitarianism": create_lens(description="Emphasizes the connection between the individual and the community, balancing rights with social responsibilities.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Environmentalism": create_lens("Examines the relationship between humans and the natural environment; advocates for conservation, sustainability, and ecological responsibility.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Fascism": create_lens("Analyzes authoritarian ultranationalism characterized by dictatorial power, forcible suppression of opposition, and strong regimentation of society and economy.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    # Era-Spanning Political Ideologies (v10.1)
    "Conservatism": create_lens(
        description="Emphasizes tradition, social stability, incremental change, and skepticism toward radical reform; values hierarchy, custom, and organic institutions.",
        eras=[E3_EARLY_MODERN, E4_19TH, E6_LATE_20TH, E7_CONTEMPORARY]
    ),
    "Democracy": create_lens(
        description="Analyzes governance by the people, whether direct (citizen participation) or representative (elected officials); examines popular sovereignty, civic virtue, and equality of participation.",
        eras=[E1_ANCIENT, E3_EARLY_MODERN, E6_LATE_20TH, E7_CONTEMPORARY]
    ),
    "Republicanism": create_lens(
        description="Focuses on civic virtue, mixed government, checks and balances, and the rejection of monarchy; emphasizes the common good over private interests and the rule of law.",
        eras=[E1_ANCIENT, E3_EARLY_MODERN, E4_19TH, E6_LATE_20TH, E7_CONTEMPORARY]
    ),
    "Socialism": create_lens(
        description="Advocates for collective or state ownership of the means of production, economic equality, and the redistribution of wealth; emphasizes solidarity and critique of capitalism.",
        eras=[E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]
    ),

    "Game Theory": create_lens("Analyzes strategic interactions and decision-making among rational agents.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Geopolitical Analysis": create_lens("Examines the influence of geography (territory, resources, location) on politics and international relations.", eras=[E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Libertarianism": create_lens(description="Prioritizes individual liberty, minimizing the state, free association, and strong private property rights.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Neoliberalism": create_lens("Analyzes the impact of policies emphasizing free-market capitalism, deregulation, and privatization.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Political Economy": create_lens("Examines the relationship between political institutions, the economic system, and social structures.", eras=[E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Realpolitik": create_lens("Focus on practical considerations of national interest and power, rather than ideological concerns.", eras=[E2_MEDIEVAL]),
    "Social Contract Theory": create_lens("Examines the implicit agreements by which people form nations and maintain social order (Hobbes, Locke, Rousseau).", eras=[E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Utilitarianism": create_lens("Focus on maximizing overall happiness or utility; the greatest good for the greatest number (Bentham, Mill).", eras=[E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    # History & Anthropology
    "Annales School": create_lens("Focus on long-term social history (la longue durée) and structural changes, rather than events.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Archaeological Analysis": create_lens("Interprets material remains, artifacts, and environmental data to understand past human societies.", eras=[E4_19TH]),
    "Cultural Materialism": create_lens("Examines the relationship between culture and material conditions (infrastructure, technology, environment) (Harris).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Ethnomethodology": create_lens("Study of the methods people use to understand and produce the social order in which they live (Garfinkel).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Great Man Theory": create_lens("History explained primarily by the impact of highly influential individuals (Carlyle).", eras=[E4_19TH]),
    "Historiography": create_lens("The study of the methods and principles of historical writing and historical scholarship.", eras=[E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Historical Contextualism": create_lens("Emphasis on understanding the work within its original historical and cultural context.", eras=[E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "New Historicism": create_lens("Analyzes the work alongside other contemporary texts and discourses, emphasizing the circulation of social energy (Greenblatt).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Oral History": create_lens("Analyzes spoken accounts, personal narratives, and traditions as historical evidence.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Presentism": create_lens("Analyzes the tendency to interpret the past through the lens of modern values and concepts (often as a critique).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b: Zeitgeist Removed. It is now a dedicated analysis mode.

    # Philosophy & Ethics
    "Absurdism": create_lens("Focus on the conflict between the human tendency to seek inherent value and the meaningless, irrational universe (Camus).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Analytic Philosophy": create_lens("Emphasis on clarity, logic, argumentation, and the analysis of language (Russell, Wittgenstein).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Aristotelianism": create_lens("Focus on virtue, rhetoric (ethos/pathos/logos), causality, and empirical observation.", eras=[E1_ANCIENT, E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Bushido": create_lens("The ethical code of the samurai; focus on honor, loyalty, duty, and martial prowess.", eras=[E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Chivalry": create_lens("The medieval knightly system; focus on valor, courtesy, honor, and service.", eras=[E2_MEDIEVAL]),  # Dead tradition, keep historically bounded
    "Confucianism": create_lens("Emphasis on ethics, social harmony, filial piety, ritual (li), and self-cultivation.", eras=[E1_ANCIENT, E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Guerrilla Warfare": create_lens("Analyzes irregular warfare tactics emphasizing mobility, surprise, and asymmetric engagement against larger conventional forces.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Deconstruction": create_lens("Focus on revealing the instability of meaning in texts, analyzing binary oppositions, and 'différance' (Derrida).", eras=[E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Deconstruction (Derrida)"),
    
    "Dialectical Materialism": create_lens("Philosophical basis of Marxism; change driven by material contradictions and class struggle.", eras=[E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Empiricism": create_lens("Knowledge derived primarily from sensory experience and observation (Locke, Hume).", eras=[E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Epicureanism": create_lens("Focus on attaining pleasure (defined as tranquility/ataraxia) and avoiding pain.", eras=[E1_ANCIENT]),
    # "Existentialism" moved to Toolkit section v9.5a

    # v10.1: Consolidated from "Kantianism" - duty-based ethics with multiple thinkers
    "Deontology": create_lens("Focus on moral duties, rules, and obligations; actions are right or wrong in themselves, regardless of consequences.", eras=[E3_EARLY_MODERN, E6_LATE_20TH, E7_CONTEMPORARY]),

    # v10.1: Consolidated from "Objectivism" - rational self-interest ethics with multiple thinkers
    "Egoism": create_lens("Focus on rational self-interest as the foundation of morality; the individual is the proper beneficiary of their own actions.", eras=[E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    "Hermeneutics": create_lens("The theory and methodology of interpretation, especially of texts, wisdom literature, and philosophical texts (Gadamer).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    # v10.1: Consolidated from "Platonism" + "Hegelian Idealism" - mind-over-matter philosophy with multiple thinkers
    "Idealism": create_lens("Reality is fundamentally mental, spiritual, or ideal rather than material; examines the primacy of mind, ideas, or consciousness in constituting reality.", eras=[E1_ANCIENT, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    # v9.4b Refactor
    "Legalism": create_lens(description="Focus on strict adherence to law, administrative efficiency, and state power, as developed in ancient China (Han Feizi).", eras=[E1_ANCIENT], prompt_name="Legalism (Chinese Philosophy)"),

    "Nihilism": create_lens("The rejection of objective meaning, value, and truth; the belief that life is meaningless.", eras=[E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    "Phenomenology": create_lens("Study of the structures of consciousness and subjective experience (Husserl, Heidegger).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # "Post-Structuralism" moved to Toolkit section v9.5a
    
    "Pragmatism": create_lens("Focus on the practical consequences and utility of ideas and beliefs (James, Dewey).", eras=[E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Rationalism": create_lens("Reason as the chief source and test of knowledge, independent of sensory experience (Descartes, Spinoza).", eras=[E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    # "Stoicism" moved to Toolkit section v9.5a
    "Taoism": create_lens("Emphasis on living in harmony with the Tao (the Way), naturalness, simplicity, and wu wei (effortless action).", eras=[E1_ANCIENT, E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Transcendentalism": create_lens(description="Focuses on the inherent goodness of humanity and nature, and the primacy of individual intuition and self-reliance (Emerson, Thoreau).", eras=[E4_19TH]),
    "Virtue Ethics": create_lens("Focus on moral character and virtues (eudaimonia) rather than rules (deontology) or consequences (utilitarianism).", eras=[E1_ANCIENT, E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # Psychology & Cognitive Science
    "Attachment Theory": create_lens("Examines long-term interpersonal relationships and the bonds between humans (Bowlby, Ainsworth).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Behaviorism": create_lens("Focus on observable behavior and conditioning, rather than internal mental states (Skinner, Watson).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "CBT Principles": create_lens("Examines the relationship between thoughts, feelings, and behaviors; identifying cognitive distortions (Cognitive Behavioral Therapy).", eras=[E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Cognitive Behavioral Therapy (CBT) Principles"),
    
    "Cognitive Dissonance": create_lens("Analyzes the mental discomfort experienced when holding contradictory beliefs, values, or ideas (Festinger).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Cognitive Linguistics": create_lens("Study of language based on human experience, conceptual metaphors, and cognition (Lakoff).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Evolutionary Psychology": create_lens("Explains psychological traits and behaviors as evolved adaptations resulting from natural selection.", eras=[E7_CONTEMPORARY]),
    
    # "Freudianism" moved to Toolkit section v9.5a
    
    "Gestalt Psychology": create_lens("Focus on perception and the idea that the whole is greater than the sum of its parts; principles of grouping.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Humanistic Psychology": create_lens("Emphasis on individual potential, free will, and the drive toward self-actualization (Rogers, Maslow).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # "Jungian Analysis" moved to Toolkit section v9.5a
    
    "Maslow's Hierarchy": create_lens("Analyzes motivation based on a hierarchy of needs, from physiological to self-actualization.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Trauma Studies": create_lens("Examines the psychological, cultural, and societal impact of traumatic events.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),

    # Rhetoric & Literary Theory
    # v9.4b Refactor
    "Archetypal Criticism": create_lens("Analyzes myths, symbols, genres, and recurring patterns in literature (Northrop Frye).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Archetypal Criticism (Frye)"),

    "Bakhtinian Dialogism": create_lens("Focus on dialogue, heteroglossia (multiple voices), and the carnivalesque in texts (Mikhail Bakhtin).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),

    "Close Reading": create_lens("Detailed, careful analysis of the specific features, language, and structure of a text.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Defamiliarization": create_lens("Technique of presenting common things in an unfamiliar way to enhance perception (Viktor Shklovsky).", eras=[E5_EARLY_20TH], prompt_name="Defamiliarization (Shklovsky)"),
    
    # v9.4b Refactor
    "Dramatism": create_lens("Analyzes human motivation and relationships using the pentad: Act, Scene, Agent, Agency, Purpose (Kenneth Burke).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Dramatism (Burke)"),
    
    "Genre Studies": create_lens("Examines the conventions, structures, and evolution of different literary or artistic genres.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Intertextuality": create_lens("Analyzes the relationship between texts; how one text shapes the meaning of another (Kristeva).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Narratology": create_lens("The structural study of narrative; analyzing story, discourse, focalization, and narrative voice (Genette).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Reader-Response": create_lens("Focus on the reader's experience and active role in creating the meaning of the text (Fish, Iser).", eras=[E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Reader-Response Criticism"),
    
    # v9.4b Refactor
    "Rhetorical Analysis": create_lens("Analyzes the means of persuasion: ethical appeal (ethos), emotional appeal (pathos), and logical appeal (logos).", eras=[E1_ANCIENT], prompt_name="Rhetorical Analysis (Ethos/Pathos/Logos)"),
    
    "Stylistics": create_lens("Study of linguistic style, tone, and the interpretation of texts based on linguistic features.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    # Sociology & Systems
    # v9.4b Refactor: Kept (ANT) in UI name as it's common usage, but added standard prompt_name.
    "Actor-Network Theory (ANT)": create_lens("Traces connections between human and non-human actors (actants), treating them symmetrically (Latour, Callon).", eras=[E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Actor-Network Theory"),
    
    # "Bourdieuian Analysis" moved to Toolkit section v9.5a
    
    "Chaos Theory": create_lens("Focus on dynamic systems highly sensitive to initial conditions (the butterfly effect) and patterns within apparent randomness.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Conflict Theory": create_lens("Analyzes society based on the conflicts, power struggles, and inequalities between different social groups.", eras=[E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # "Critical Theory" moved to Toolkit section v9.5a
    
    "Cybernetics": create_lens("Study of communication, control systems, and feedback loops in both machines and living organisms.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Functionalism": create_lens("Analyzes society as a complex system whose parts work together to promote solidarity and stability (Durkheim, Parsons).", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Functionalism (Sociological)"),
    
    "Network Analysis": create_lens("Maps and measures relationships and flows between people, groups, organizations, or other information-processing entities.", eras=[E7_CONTEMPORARY]),
    "Social Constructionism": create_lens("Examines how shared understandings and meanings of the world are jointly constructed through social interaction.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Symbolic Interactionism": create_lens("Focus on how individuals interact using shared symbols and meanings to create their social reality (Mead, Blumer).", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),
    "Systems Theory": create_lens("Analyzes complex systems and their interactions, focusing on feedback loops, boundaries, inputs/outputs, and emergent properties.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    # Theology, Religion & Mythology
    
    # v10.1: Consolidated Buddhism Toolkit (from Chan/Zen, Theravāda, Tibetan)
    "Buddhism": create_lens(
        description="Analyzes through Buddhist traditions, examining suffering (dukkha), impermanence (anicca), non-self (anatta), and the path to liberation across multiple schools.",
        prompt_name="Buddhism",
        sub_primers={
            "Theravāda Buddhism (The Path of the Elders)": """
            Analyze through Theravāda doctrine, focusing on the Pali Canon, the Four Noble Truths, the Noble Eightfold Path, and the goal of personal liberation (Arhatship).
            Examine themes of mindfulness (sati), ethical conduct (sīla), mental discipline (samādhi), and wisdom (paññā). Emphasize the direct teachings of the Buddha and individual practice.
            """,
            "Chan/Zen Buddhism (Direct Pointing to Mind)": """
            Analyze through Chan/Zen traditions, emphasizing direct experience over scriptural study, meditation (zazen), kōans (paradoxical questions), and sudden awakening (satori).
            Examine themes of no-mind (mushin), ordinary mind (heijōshin), the nature of Buddha-nature inherent in all beings, and the integration of practice into daily life.
            """,
            "Tibetan Buddhism - Vajrayāna (The Diamond Vehicle)": """
            Analyze through Tibetan Vajrayāna traditions, focusing on tantric practices, compassion (bodhicitta), the concept of emptiness (śūnyatā), and the role of the guru (lama).
            Examine themes of skillful means (upāya), visualization practices, the Bodhisattva path, and the transformation of suffering into enlightenment through ritual and meditation.
            """
        },
        eras=[E1_ANCIENT, E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]
    ),

    # v10.1: Consolidated Christian Theology Toolkit (from Catholic, Protestant, Liberation Theology)
    "Christian Theology": create_lens(
        description="Analyzes through Christian theological traditions, examining scripture, doctrine, grace, faith, and social ethics across multiple schools.",
        prompt_name="Christian Theology",
        sub_primers={
            "Catholic Theology (Tradition and Sacrament)": """
            Analyze through Catholic doctrine, focusing on natural law, sacramental theology, the authority of tradition and magisterial teaching, and the communion of saints.
            Examine how the work reflects themes of incarnation, grace mediated through sacraments, moral virtue, and the complementary relationship between faith and reason (Aquinas).
            """,
            "Protestant Theology (Sola Scriptura/Fide/Gratia)": """
            Analyze through Protestant doctrine, emphasizing Sola Scriptura (scripture alone), Sola Fide (faith alone), and Sola Gratia (grace alone).
            Examine themes of justification by faith, the priesthood of all believers, individual conscience, and the tension between law and gospel (Luther, Calvin).
            """,
            "Liberation Theology (Preferential Option for the Poor)": """
            Analyze through the lens of liberation theology, emphasizing liberation from social, political, and economic oppression.
            Interpret scripture through the lived experience of the poor and marginalized. Examine themes of structural sin, prophetic witness, solidarity, and the Kingdom of God as social transformation (Gutiérrez, Boff).
            """
        },
        eras=[E1_ANCIENT, E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]
    ),

    # Hinduism
    "Hinduism: Advaita Vedanta": create_lens(description="Focuses on non-dualistic Hindu philosophy; the unity of Atman (the self) and Brahman (the ultimate reality) (Shankara).", eras=[E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Hinduism: General Philosophy": create_lens(description="Focus on core concepts across various schools, such as dharma (duty), karma (action/consequence), maya (illusion), and moksha (liberation).", eras=[E1_ANCIENT, E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    # Islam
    "Islam: Sufism": create_lens(description="Focuses on Islamic mysticism, the inner spiritual path (tariqa), divine love, and the poetry of figures like Rumi and Hafez.", eras=[E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    
    # v9.4b Refactor
    "Islamic Theology (Kalam)": create_lens(description="Focus on Islamic scholastic theology, reason, scriptural interpretation, and doctrinal debates.", eras=[E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Islam: Theology (Kalam)"),

    # Judaism
    "Judaism: Kabbalah": create_lens(description="Analyzes esoteric Jewish mysticism, focusing on symbolic interpretation, the Sefirot (divine emanations), and the nature of divinity.", eras=[E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Judaism: Talmudic/Rabbinic": create_lens(description="Focus on textual interpretation (midrash), law (halakha), ethics, and debate within the Rabbinic tradition.", eras=[E1_ANCIENT, E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),

    # Mythology & Comparative
    # v9.4b Refactor
    "Comparative Mythology": create_lens(description="Focus on the monomyth (hero's journey), universal archetypes, and structural patterns across different cultures (Joseph Campbell).", eras=[E6_LATE_20TH, E7_CONTEMPORARY], prompt_name="Comparative Mythology (Campbell)"),
    
    "Egyptian Myth": create_lens(description="Analysis based on the Egyptian pantheon, cosmology, concepts of Ma'at (order/truth), divine kingship, and the afterlife.", eras=[E1_ANCIENT]),
    "Greco-Roman Myth": create_lens(description="Analysis of the Olympian/Roman pantheon, heroic cycles (e.g., Homeric epics), fate (moira), hubris, and the relationship between gods and mortals.", eras=[E1_ANCIENT]),
    "Mesoamerican Myth": create_lens(description="Analysis based on Aztec, Maya, and other regional pantheons, focusing on cyclical time, sacrifice, duality, and cosmology.", eras=[E1_ANCIENT, E2_MEDIEVAL]),
    "Norse Myth": create_lens(description="Analysis based on the Norse pantheon (Æsir/Vanir), concepts of fate (Wyrd), honor, the Nine Worlds, and the cycle of Ragnarök.", eras=[E2_MEDIEVAL]),
    "Mythopoeic Analysis": create_lens(description="Analyzes the creation and function of myths within a culture, and the human propensity to create mythology.", eras=[E6_LATE_20TH, E7_CONTEMPORARY]),

    # Other
    "Secular Humanism": create_lens(description="Focus on human reason, ethics, and justice, affirming human agency and rejecting religious dogma or supernaturalism.", eras=[E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
    "Shinto": create_lens(description="Analysis based on Japanese indigenous beliefs, focusing on kami (spirits), purity (kegare), ritual, and the sacredness of nature.", eras=[E2_MEDIEVAL, E3_EARLY_MODERN, E4_19TH, E5_EARLY_20TH, E6_LATE_20TH, E7_CONTEMPORARY]),
}


# -----------------------------------------------------------------------------
# 2. LENSES BY DISCIPLINE (The Library)
# Organized by academic field.
# v9.5a: Updated to reflect lenses moved to the Toolkit architecture (no changes needed here, only in definitions).
# -----------------------------------------------------------------------------

LENSES_HIERARCHY = {
    "Art History": [
        "Abstract Expressionism",
        "Art Deco",
        "Baroque Aesthetics", # v9.4b Updated
        "Constructivism",
        "Cubism",
        "Dadaism",
        "De Stijl",
        "Expressionism",
        "Fauvism",
        "Futurism",
        "Iconography/Iconology",
        "Impressionism",
        "Minimalism",
        "Pop Art",
        "Renaissance Aesthetics", # v9.4b Updated
        "Suprematism",
        "Surrealism",
    ],
    "Aesthetics": [
        "Aestheticism",
        "Affect Theory",
        "Avant-Garde Studies",
        "Ecocriticism",
        "Impressionistic Criticism",
        "Modernism",
        "Postmodernism",
        "Pragmatic Criticism",
        "Romanticism",
        "Transcendentalism",  # v10.1 Multi-discipline: Also in Individual Philosophy
    ],
    "Literary Theory": [
        "Archetypal Criticism", # v9.4b Updated
        "Bakhtinian Dialogism",
        "Biographical Analysis", # v9.4b Updated
        "Close Reading",
        "Deconstruction",  # v10.1 Multi-discipline: Also in Metaphysics
        "Defamiliarization", # v9.4b Updated
        "Dramatism", # v9.4b Updated
        "Existentialism",  # v10.1 Multi-discipline: Also in Individual Philosophy
        "Formalism", # v9.4b Updated
        "Genre Studies",
        "Hermeneutics",
        "Intentional Fallacy",
        "Intertextuality",
        "Narratology",
        "Post-Structuralism",  # v10.1 Multi-discipline: Also in Metaphysics, Individual Philosophy, Sociology
        "Reader-Response", # v9.4b Updated
        "Reception Theory",
        "Rhetorical Analysis", # v9.4b Updated
        "Semiotics", # v9.4b Updated
        "Structuralism",
        "Stylistics",
    ],
    "Film Studies": [
        "Auteur Theory", # v9.4b Updated
        "Cinema Novo",
        "Dogme 95",
        "Film Noir",
        "French New Wave",
        "German Expressionism",
        "Italian Neorealism",
        "Mumblecore",
        "New Hollywood",
        "Soviet Montage",
        "Third Cinema",
    ],
    "Media & Communication": [
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
    "Politics & Economics": [
        "Anarchism",
        "Aristotelianism",  # v10.1 Multi-discipline: Also in Ethics, Individual Philosophy
        "Behavioral Economics",
        "Classical Liberalism",
        "Communitarianism",
        "Confucianism",  # v10.1 Multi-discipline: Also in Ethics, Individual Philosophy
        "Conservatism",  # v10.1 Era-Spanning
        "Democracy",  # v10.1 Era-Spanning
        "Game Theory",
        "Geopolitical Analysis",
        "Libertarianism",
        "Marxism", # v9.4b Updated
        "Neoliberalism",
        "Political Economy",
        "Realpolitik",
        "Republicanism",  # v10.1 Era-Spanning
        "Social Contract Theory",
        "Socialism",  # v10.1 Era-Spanning
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
    "Ethics": [
        "Aristotelianism",  # v10.1 Multi-discipline: Also in Individual Philosophy, Politics & Economics
        "Bushido",
        "Chivalry",
        "Confucianism",  # v10.1 Multi-discipline: Also in Individual Philosophy, Politics & Economics
        "Deontology",  # v10.1 Consolidated from Kantianism
        "Egoism",  # v10.1 Consolidated from Objectivism
        "Secular Humanism",
        "Stoicism",  # v10.1 Multi-discipline: Also in Individual Philosophy
        "Virtue Ethics",
    ],
    "Metaphysics": [
        "Absurdism",
        "Analytic Philosophy",
        "Deconstruction",  # v10.1 Multi-discipline: Also in Literary Theory
        "Empiricism",
        "Idealism",  # v10.1 Consolidated from Platonism + Hegelian Idealism
        "Nihilism",
        "Phenomenology",
        "Post-Structuralism",  # v10.1 Multi-discipline: Also in Individual Philosophy, Literary Theory, Sociology
        "Pragmatism",
        "Rationalism",
        "Taoism",  # v10.1 Multi-discipline: Also in Individual Philosophy
    ],
    "Individual Philosophy": [
        "Aristotelianism",  # v10.1 Multi-discipline: Also in Ethics, Politics & Economics
        "Confucianism",  # v10.1 Multi-discipline: Also in Ethics, Politics & Economics
        "Dialectical Materialism",
        "Existentialism",  # v10.1 Multi-discipline: Also in Literary Theory
        "Legalism", # v9.4b Updated
        "Post-Structuralism",  # v10.1 Multi-discipline: Also in Metaphysics, Literary Theory, Sociology
        "Stoicism",  # v10.1 Multi-discipline: Also in Ethics
        "Taoism",  # v10.1 Multi-discipline: Also in Metaphysics
        "Transcendentalism",  # v10.1 Multi-discipline: Also in Aesthetics
    ],
    "Psychology": [
        "Attachment Theory",
        "Behavioral Economics",
        "Behaviorism",
        "CBT Principles", # v9.4b Updated
        "Cognitive Dissonance",
        "Cognitive Linguistics",
        "Evolutionary Psychology",
        "Gestalt Psychology",
        "Humanistic Psychology",
        "Maslow's Hierarchy",
        "Psychoanalytic Theory",  # v10.1 Consolidated from Freudianism, Jungian Analysis, Lacanianism
        "Trauma Studies",
    ],
    "Sociology": [
        "Actor-Network Theory (ANT)",
        "Bourdieuian Analysis", # v9.4b Updated
        "Conflict Theory",
        "Critical Theory", # v9.4b Updated
        "Functionalism", # v9.4b Updated
        "Post-Structuralism",  # v10.1 Multi-discipline: Also in Metaphysics, Individual Philosophy, Literary Theory
        "Social Constructionism",
        "Symbolic Interactionism",
    ],
    "Transdisciplinary": [
        "Chaos Theory",
        "Cybernetics",
        "Network Analysis",
        "Systems Theory",
    ],
    "Mythology": [
        "Comparative Mythology", # v9.4b Updated
        "Egyptian Myth",
        "Greco-Roman Myth",
        "Mesoamerican Myth",
        "Norse Myth",
        "Mythopoeic Analysis",
        "Shinto",
    ],
    "Theology": [
        "Buddhism",  # v10.1 Consolidated from Chan/Zen, Theravāda, Tibetan
        "Christian Theology",  # v10.1 Consolidated from Catholic, Protestant, Liberation Theology
        "Hinduism: Advaita Vedanta",
        "Hinduism: General Philosophy",
        "Islam: Sufism",
        "Islamic Theology (Kalam)", # v9.4b Updated
        "Judaism: Kabbalah",
        "Judaism: Talmudic/Rabbinic",
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
        "Deontology",  # v10.1 Consolidated from Kantianism
        "Dialectical Materialism",
        "Empiricism",
        "Epicureanism",
        "Egoism",  # v10.1 Consolidated from Objectivism
        "Existentialism",
        "Hermeneutics",
        "Idealism",  # v10.1 Consolidated from Platonism + Hegelian Idealism
        "Legalism", # v9.4b Updated
        "Libertarianism",
        "Nihilism",
        "Phenomenology",
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
        "Humanistic Psychology",
        "Maslow's Hierarchy",
        "Psychoanalytic Theory",  # v10.1 Consolidated from Freudianism, Jungian Analysis, Lacanianism
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
        "Conservatism",  # v10.1 Era-Spanning
        "Critical Theory", # v9.4b Updated
        "Democracy",  # v10.1 Era-Spanning
        "Marxism", # v9.4b Updated
        "Neoliberalism",
        "Realpolitik",
        "Republicanism",  # v10.1 Era-Spanning
        "Social Constructionism",
        "Socialism",  # v10.1 Era-Spanning
        "Symbolic Interactionism",

        # Art & Literary Theory
        "Abstract Expressionism",
        "Archetypal Criticism", # v9.4b Updated
        "Art Deco",
        "Avant-Garde Studies",
        "Bakhtinian Dialogism",
        "Baroque Aesthetics", # v9.4b Updated
        "Constructivism",
        "Cubism",
        "Dadaism",
        "De Stijl",
        "Ecocriticism",
        "Expressionism",
        "Fauvism",
        "Futurism",
        "Impressionism",
        "Impressionistic Criticism",
        "Minimalism",
        "Modernism",
        "Pop Art",
        "Postmodernism",
        "Pragmatic Criticism",
        "Reader-Response", # v9.4b Updated
        "Renaissance Aesthetics", # v9.4b Updated
        "Romanticism",
        "Suprematism",
        "Surrealism",

        # Film Studies
        "Auteur Theory", # v9.4b Updated (also in Tier 2)
        "Cinema Novo",
        "Dogme 95",
        "Film Noir",
        "French New Wave",
        "German Expressionism",
        "Italian Neorealism",
        "Mumblecore",
        "New Hollywood",
        "Soviet Montage",
        "Third Cinema",

        # Theology, Religion & Mythology
        "Buddhism",  # v10.1 Consolidated from Chan/Zen, Theravāda, Tibetan
        "Christian Theology",  # v10.1 Consolidated from Catholic, Protestant, Liberation Theology
        "Comparative Mythology", # v9.4b Updated
        "Hinduism: Advaita Vedanta",
        "Hinduism: General Philosophy",
        "Islam: Sufism",
        "Islamic Theology (Kalam)", # v9.4b Updated
        "Judaism: Kabbalah",
        "Judaism: Talmudic/Rabbinic",
        "Egyptian Myth",
        "Greco-Roman Myth",
        "Mesoamerican Myth",
        "Norse Myth",
        "Mythopoeic Analysis",
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
    E3_EARLY_MODERN,
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
# 4. LENSES BY GEOGRAPHIC REGION
# v10.4: Organizes lenses by cultural-geographic region for filtering and weighting.
# Lenses can appear in multiple regions (e.g., Christianity, Marxism).
# -----------------------------------------------------------------------------

LENSES_GEOGRAPHIC = {
    "Western Europe": [
        "Abstract Expressionism",  # US but strong European avant-garde roots - multi-regional
        "Absurdism",  # Camus (France/Algeria)
        "Aestheticism",  # Wilde, Pater (Britain)
        "Analytic Philosophy",  # Russell, Wittgenstein (Britain/Austria)
        "Anarchism",  # Proudhon, Bakunin, Kropotkin (France/Russia) - multi-regional
        "Annales School",  # Bloch, Braudel (France)
        "Archaeological Analysis",  # Developed across Europe
        "Archetypal Criticism",  # Jung (Switzerland), Frye (Canada) - multi-regional
        "Aristotelianism",  # Ancient Greece
        "Art Deco",  # France/international
        "Auteur Theory",  # Truffaut, Sarris (France)
        "Avant-Garde Studies",  # European avant-garde movements
        "Baroque Aesthetics",  # Italy, Counter-Reformation Europe
        "Biographical Analysis",  # European literary tradition
        "Bourdieuian Analysis",  # Bourdieu (France)
        "Chaos Theory",  # Mathematical/scientific (international but Western academic)
        "Chivalry",  # Medieval Europe
        "Christian Theology",  # Multiple regions but Western theological tradition
        "Christianity",  # Origin Middle East, but Western Christianity distinct
        "Classical Liberalism",  # Locke, Smith (Britain)
        "Close Reading",  # New Criticism (Anglo-American)
        "Communitarianism",  # MacIntyre, Taylor (Britain/Canada)
        "Comparative Mythology",  # European academic tradition
        "Conservatism",  # Burke (Britain)
        "Constructivism",  # Russian avant-garde art movement - multi-regional
        "Critical Theory",  # Frankfurt School (Germany)
        "Cubism",  # Picasso, Braque (France/Spain)
        "Cultural Materialism",  # British cultural studies
        "Dadaism",  # Zurich/Paris avant-garde
        "De Stijl",  # Dutch art movement
        "Deconstruction",  # Derrida (France)
        "Defamiliarization",  # Shklovsky (Russian Formalism) - multi-regional
        "Democracy",  # Ancient Greece, modern European/American development - multi-regional
        "Deontology",  # Kant (Germany)
        "Dialectical Materialism",  # Marx/Engels (Germany) - multi-regional
        "Dogme 95",  # von Trier, Vinterberg (Denmark)
        "Dramatism",  # Burke (US)
        "Ecocriticism",  # Anglo-American academic movement
        "Egoism",  # Stirner, Rand (Germany/Russia/US) - multi-regional
        "Egyptian Myth",  # Ancient Egypt (North Africa & Middle East) - multi-regional
        "Empiricism",  # Locke, Hume, Berkeley (Britain)
        "Environmentalism",  # Modern environmental movement (international)
        "Epicureanism",  # Ancient Greece
        "Existentialism",  # Kierkegaard, Sartre, Heidegger (Denmark/France/Germany)
        "Expressionism",  # German art movement
        "Fascism",  # Mussolini (Italy), spread to Germany/Spain
        "Fauvism",  # French art movement
        "Feminism",  # Multiple waves, European/American origins, global variations - multi-regional
        "Film Noir",  # US/French term for American films
        "Formalism",  # Russian Formalism, New Criticism - multi-regional
        "French New Wave",  # Godard, Truffaut (France)
        "Functionalism",  # Malinowski, Durkheim (Britain/France)
        "Futurism",  # Italian avant-garde
        "Game Theory",  # von Neumann, Nash (Central European/American) - multi-regional
        "Gender Studies",  # Academic field (Western academic, global applications)
        "Genre Studies",  # Western literary/film studies
        "Geopolitical Analysis",  # European geopolitics tradition
        "German Expressionism",  # German film movement
        "Gestalt Psychology",  # German psychology
        "Great Man Theory",  # Carlyle (Britain)
        "Greco-Roman Myth",  # Ancient Greece/Rome
        "Guerrilla Warfare",  # Modern theory (multi-regional but Western theorization)
        "Hermeneutics",  # Schleiermacher, Gadamer (Germany)
        "Historical Contextualism",  # European historical method
        "Historiography",  # European academic tradition
        "Humanistic Psychology",  # Maslow, Rogers (US) - multi-regional
        "Iconography/Iconology",  # Panofsky (Germany)
        "Idealism",  # Plato, Hegel (Greece/Germany)
        "Impressionism",  # French art movement
        "Impressionistic Criticism",  # European aesthetic criticism
        "Intentional Fallacy",  # Wimsatt, Beardsley (US New Criticism)
        "Intertextuality",  # Kristeva, Barthes (France)
        "Italian Neorealism",  # De Sica, Rossellini (Italy)
        "Judaism: Kabbalah",  # Jewish mysticism (multi-regional)
        "Judaism: Talmudic/Rabbinic",  # Jewish tradition (multi-regional)
        "Libertarianism",  # Modern political philosophy (Western)
        "Ludology",  # Game studies (Scandinavian/European academic)
        "Marxism",  # Marx/Engels (Germany), global variations
        "Media Ecology",  # McLuhan (Canada)
        "Minimalism",  # US art movement but international
        "Modernism",  # European/American literary/artistic movement
        "Mythopoeic Analysis",  # European academic tradition
        "Narratology",  # Genette, Greimas (France)
        "Neoliberalism",  # Hayek, Friedman (Austria/US) - multi-regional
        "Network Analysis",  # Social science method (Western academic)
        "New Historicism",  # Greenblatt (US)
        "Nihilism",  # Nietzsche (Germany)
        "Norse Myth",  # Scandinavia/Germanic peoples
        "Oral History",  # Academic method (Western academic tradition)
        "Orientalism",  # Said (Palestinian/US)
        "Phenomenology",  # Husserl, Heidegger, Merleau-Ponty (Germany/France)
        "Political Economy",  # Smith, Ricardo, Marx (Britain/Germany)
        "Pop Art",  # US/Britain art movement
        "Post-Structuralism",  # Foucault, Deleuze, Derrida (France)
        "Postcolonialism",  # Global but significant European theorists (Said, Spivak) - multi-regional
        "Postmodernism",  # Lyotard, Baudrillard (France/Western academic)
        "Pragmatic Criticism",  # Ancient Greece (Aristotle)
        "Presentism",  # Historical method (Western academic)
        "Psychoanalytic Theory",  # Freud, Lacan (Austria/France)
        "Queer Theory",  # Butler, Sedgwick (US/French theory influence)
        "Rationalism",  # Descartes, Spinoza, Leibniz (France/Netherlands/Germany)
        "Reader-Response",  # Iser, Fish (Germany/US)
        "Realism",  # 19th century art/literary movement (France/Europe)
        "Realpolitik",  # Bismarck (Germany)
        "Reception Theory",  # Jauss (Germany)
        "Renaissance Aesthetics",  # Italian Renaissance
        "Republicanism",  # Ancient Rome, modern political philosophy
        "Rhetorical Analysis",  # Aristotle, Cicero, Quintilian (Ancient Greece/Rome)
        "Romanticism",  # European literary/artistic movement (Germany/Britain/France)
        "Secular Humanism",  # Enlightenment tradition (Western)
        "Semiotics",  # Saussure, Peirce (Switzerland/US)
        "Social Constructionism",  # Berger, Luckmann (Austria/US)
        "Social Contract Theory",  # Hobbes, Locke, Rousseau (Britain/France)
        "Socialism",  # European political philosophy (France/Germany/Britain)
        "Stoicism",  # Ancient Greece/Rome
        "Structuralism",  # Lévi-Strauss, Barthes (France)
        "Stylistics",  # Linguistic analysis (Western academic)
        "Subaltern Studies",  # Spivak, Guha (South Asian scholars) - multi-regional
        "Suprematism",  # Malevich (Russia) - multi-regional
        "Surrealism",  # Breton, Dalí (France/Spain)
        "Symbolic Interactionism",  # Mead, Blumer (US)
        "Systems Theory",  # Luhmann, von Bertalanffy (Germany/Austria)
        "Transcendentalism",  # Emerson, Thoreau (US) - multi-regional
        "Utilitarianism",  # Bentham, Mill (Britain)
        "Virtue Ethics",  # Aristotle, MacIntyre (Ancient Greece/modern revival)
    ],
    "Eastern Europe": [
        "Anarchism",  # Bakunin, Kropotkin (Russia)
        "Bakhtinian Dialogism",  # Bakhtin (Russia)
        "Christianity",  # Eastern Orthodox Christianity
        "Constructivism",  # Russian avant-garde
        "Defamiliarization",  # Shklovsky, Jakobson (Russian Formalism)
        "Dialectical Materialism",  # Soviet Marxism-Leninism
        "Formalism",  # Russian Formalism (Shklovsky, Jakobson)
        "Marxism",  # Soviet/Eastern Bloc Marxism
        "Soviet Montage",  # Eisenstein, Vertov (Soviet cinema)
        "Structuralism",  # Jakobson (Russian/Prague School) - multi-regional
        "Suprematism",  # Malevich (Russian avant-garde)
    ],
    "North America": [
        "Actor-Network Theory (ANT)",  # Latour (France), Law (Britain), Callon (France) - Western academic, multi-regional
        "Affect Theory",  # Sedgwick, Ahmed, Berlant (US/Britain)
        "Attachment Theory",  # Bowlby, Ainsworth (Britain/US)
        "Behavioral Economics",  # Kahneman, Tversky, Thaler (US/Israel)
        "Behaviorism",  # Skinner, Watson (US)
        "CBT Principles",  # Beck, Ellis (US)
        "Cognitive Dissonance",  # Festinger (US)
        "Cognitive Linguistics",  # Lakoff, Langacker (US)
        "Conflict Theory",  # US sociology
        "Critical Race Theory (CRT)",  # Bell, Crenshaw, Delgado (US)
        "Cybernetics",  # Wiener (US)
        "Disability Studies",  # US/British academic movement
        "Ethnomethodology",  # Garfinkel (US)
        "Evolutionary Psychology",  # Cosmides, Tooby (US)
        "Indigenous Methodologies",  # Multi-regional but includes North American indigenous
        "Intersectionality",  # Crenshaw (US)
        "Maslow's Hierarchy",  # Maslow (US)
        "Mumblecore",  # US independent cinema
        "New Hollywood",  # Scorsese, Coppola, Altman (US)
        "Pragmatism",  # US origin (James, Dewey, Peirce)
        "Trauma Studies",  # Caruth, Herman (US)
        "Whiteness Studies",  # US critical race studies
    ],
    "Latin America & Caribbean": [
        "Christianity",  # Liberation theology, syncretism
        "Cinema Novo",  # Glauber Rocha (Brazil)
        "Indigenous Methodologies",  # Mesoamerican, Andean, Amazonian, Caribbean
        "Marxism",  # Dependency theory, Guevarism
        "Mesoamerican Myth",  # Aztec, Maya
        "Postcolonialism",  # Latin American postcolonial thought
        "Third Cinema",  # Solanas, Getino (Argentina) - anti-colonial filmmaking
    ],
    "Sub-Saharan Africa": [
        "Afrofuturism",  # African diaspora but rooted in African identity
        "Christianity",  # African Christianity, syncretism
        "Indigenous Methodologies",  # African indigenous epistemologies
        "Postcolonialism",  # Négritude, Pan-Africanism, postcolonial theory
    ],
    "North Africa & Middle East": [
        "Christianity",  # Origin region, Coptic, Eastern Christianity
        "Egyptian Myth",  # Ancient Egyptian mythology
        "Islam: Sufism",  # Islamic mysticism
        "Islamic Theology (Kalam)",  # Islamic scholastic theology
        "Judaism: Kabbalah",  # Jewish mysticism (multi-regional)
        "Judaism: Talmudic/Rabbinic",  # Jewish tradition (multi-regional)
    ],
    "South Asia": [
        "Buddhism",  # Origin in India, spread across Asia
        "Christianity",  # South Asian Christianity
        "Hinduism: Advaita Vedanta",
        "Hinduism: General Philosophy",
        "Postcolonialism",  # Subaltern Studies, postcolonial theory
    ],
    "East Asia": [
        "Buddhism",  # Chan/Zen Buddhism (East Asian development)
        "Bushido",  # Japanese samurai code
        "Christianity",  # East Asian Christianity
        "Confucianism",  # Chinese origin
        "Legalism",  # Chinese philosophy (Han Feizi)
        "Marxism",  # Maoism, Socialism with Chinese Characteristics
        "Shinto",  # Japanese indigenous religion
        "Taoism",  # Chinese philosophy (Laozi, Zhuangzi)
    ],
    "Southeast Asia": [
        "Buddhism",  # Theravada Buddhism dominant in Southeast Asia
        "Christianity",  # Southeast Asian Christianity (Philippines, etc.)
    ],
    "Central Asia": [
        "Buddhism",  # Tibetan Buddhism (Vajrayana)
        "Islam: Sufism",  # Central Asian Sufi traditions
    ],
    "Oceania & Pacific Islands": [
        "Indigenous Methodologies",  # Pacific Islander, Aboriginal Australian
    ],
}

# Alphabetize lenses within each geographic region
for region in LENSES_GEOGRAPHIC:
    LENSES_GEOGRAPHIC[region].sort()


# -----------------------------------------------------------------------------
# 5. PERSONA STYLE GUIDES (The Interpreter Model)
# v10.0: DEPRECATED. Persona generation is now handled dynamically by the Adaptive Theoretician.
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
    "Norse Myth": {
        "persona": "The Skald (An ancient Norse storyteller and poet)",
        "guide": """
        Adopt the persona of a Norse Skald. The tone should be epic, somewhat fatalistic, and deeply respectful of the gods and heroes. 
        Use vivid, rhythmic language, incorporating kennings (e.g., "whale-road" for the sea) and alliteration where appropriate, but ensure the analysis remains clear.
        Focus on themes of honor, fate (Wyrd), the struggles between the Æsir/Vanir and the Jötnar, and the looming shadow of Ragnarök. 
        Relate the elements of the work to the cosmology of the Nine Worlds.
        Begin the analysis with an invocation or a traditional storytelling opening.
        """
    },
    "Greco-Roman Myth": {
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
    # Philosophy & Ethics - Core Traditions
    "Absurdism": ["Albert Camus"],
    "Stoicism": ["Marcus Aurelius", "Seneca the Younger", "Epictetus", "Zeno of Citium"],
    "Existentialism": ["Jean-Paul Sartre", "Simone de Beauvoir", "Albert Camus", "Søren Kierkegaard", "Friedrich Nietzsche"],
    "Confucianism": ["Confucius", "Mencius"],
    "Aristotelianism": ["Aristotle"],
    "Transcendentalism": ["Ralph Waldo Emerson", "Henry David Thoreau", "Margaret Fuller"],

    # v10.3: Philosophy & Ethics - Expanded
    "Analytic Philosophy": ["Bertrand Russell", "Ludwig Wittgenstein", "G.E. Moore", "Rudolf Carnap"],
    "Empiricism": ["John Locke", "David Hume", "George Berkeley"],  # Locke also in Classical Liberalism, Social Contract
    "Rationalism": ["René Descartes", "Baruch Spinoza", "Gottfried Wilhelm Leibniz"],
    "Pragmatism": ["William James", "John Dewey", "Charles Sanders Peirce"],  # Dewey also in Democracy
    "Phenomenology": ["Edmund Husserl", "Martin Heidegger", "Maurice Merleau-Ponty"],
    "Hermeneutics": ["Hans-Georg Gadamer", "Paul Ricoeur", "Wilhelm Dilthey"],
    "Nihilism": ["Friedrich Nietzsche", "Arthur Schopenhauer"],  # Nietzsche also in Existentialism, Egoism
    "Epicureanism": ["Epicurus", "Lucretius"],
    "Legalism": ["Han Feizi", "Shang Yang"],
    "Taoism": ["Laozi (Lao Tzu)", "Zhuangzi (Chuang Tzu)", "Liezi"],
    "Virtue Ethics": ["Aristotle", "Alasdair MacIntyre", "Philippa Foot", "Rosalind Hursthouse"],
    "Utilitarianism": ["Jeremy Bentham", "John Stuart Mill", "Henry Sidgwick"],  # Mill also in Democracy
    "Social Contract Theory": ["Thomas Hobbes", "John Locke", "Jean-Jacques Rousseau"],  # Locke in Empiricism, Classical Liberalism; Rousseau in Democracy
    "Dialectical Materialism": ["Karl Marx", "Friedrich Engels", "V.I. Lenin"],

    # Political Philosophy
    "Marxism": ["Karl Marx", "Friedrich Engels", "Walter Benjamin", "Georg Lukács", "Terry Eagleton", "Antonio Gramsci"],
    "Feminism": ["Virginia Woolf", "bell hooks", "Judith Butler", "Mary Wollstonecraft", "Simone de Beauvoir", "Kimberlé Crenshaw"],  # de Beauvoir in Existentialism; Crenshaw in Intersectionality
    "Postcolonialism": ["Edward Said", "Homi K. Bhabha", "Gayatri Chakravorty Spivak", "Frantz Fanon"],  # Said in Orientalism; Spivak in Subaltern Studies
    "Critical Theory": ["Theodor Adorno", "Max Horkheimer", "Herbert Marcuse", "Walter Benjamin"],
    "Bourdieuian Analysis": ["Pierre Bourdieu"],
    "Post-Structuralism": ["Michel Foucault"],

    # v10.3: Political Philosophy - Expanded
    "Classical Liberalism": ["John Locke", "Adam Smith", "John Stuart Mill", "Friedrich Hayek"],  # Locke in Empiricism, Social Contract; Mill in Utilitarianism, Democracy
    "Anarchism": ["Pierre-Joseph Proudhon", "Mikhail Bakunin", "Peter Kropotkin", "Emma Goldman"],
    "Fascism": ["Benito Mussolini", "Giovanni Gentile"],
    "Environmentalism": ["Aldo Leopold", "Rachel Carson", "Arne Naess"],
    "Orientalism": ["Edward Said"],  # Said also in Postcolonialism
    "Subaltern Studies": ["Gayatri Chakravorty Spivak", "Ranajit Guha"],  # Spivak also in Postcolonialism
    "Intersectionality": ["Kimberlé Crenshaw", "Patricia Hill Collins"],  # Crenshaw also in Feminism

    # Consolidated Ideology Pools (v10.1)
    "Deontology": ["Immanuel Kant", "W.D. Ross", "Christine Korsgaard", "Thomas Nagel"],
    "Egoism": ["Ayn Rand", "Max Stirner", "Friedrich Nietzsche"],  # Nietzsche in Existentialism, Nihilism
    "Idealism": ["Plato", "George Berkeley", "G.W.F. Hegel", "Josiah Royce", "F.H. Bradley"],
    "Psychoanalytic Theory": ["Sigmund Freud", "Carl Jung", "Jacques Lacan", "Melanie Klein", "D.W. Winnicott", "Alfred Adler"],
    "Buddhism": ["Nagarjuna", "Dōgen", "14th Dalai Lama (Tenzin Gyatso)", "Ajahn Chah"],
    "Christian Theology": ["Augustine of Hippo", "Thomas Aquinas", "Martin Luther", "John Calvin", "Gustavo Gutiérrez", "Karl Barth"],

    # Era-Spanning Political Ideologies (v10.1)
    "Republicanism": [
        "Cicero",  # Ancient Rome - De Republica
        "Niccolò Machiavelli",  # Renaissance - Discourses on Livy
        "Montesquieu",  # Enlightenment - Spirit of the Laws
        "Thomas Jefferson",  # American Enlightenment
        "James Madison",  # American Enlightenment - Federalist Papers
        "Alexander Hamilton",  # American Enlightenment - Federalist Papers
        "Abraham Lincoln",  # 19th Century - Preservation of Union
        "Theodore Roosevelt",  # Progressive Era
        "Hannah Arendt",  # 20th Century - On Revolution
    ],
    "Democracy": [
        "Pericles",  # Ancient Athens - Funeral Oration
        "Jean-Jacques Rousseau",  # Enlightenment - Social Contract
        "Alexis de Tocqueville",  # 19th Century - Democracy in America
        "John Stuart Mill",  # 19th Century - Representative Government
        "John Dewey",  # 20th Century - Participatory Democracy
        "Robert Dahl",  # 20th Century - Polyarchy
        "John Rawls",  # 20th Century - Theory of Justice
    ],
    "Conservatism": [
        "Edmund Burke",  # 18th Century - Reflections on the Revolution
        "Michael Oakeshott",  # 20th Century - Rationalism in Politics
        "Russell Kirk",  # 20th Century - The Conservative Mind
        "William F. Buckley Jr.",  # 20th Century - National Review
        "Roger Scruton",  # 20th Century - The Meaning of Conservatism
    ],
    "Socialism": [
        "Robert Owen",  # Pre-Marxist Utopian Socialism
        "Charles Fourier",  # Pre-Marxist Utopian Socialism
        "Pierre-Joseph Proudhon",  # Pre-Marxist Anarcho-Socialism
        "Eduard Bernstein",  # Democratic Socialism - Revisionism
        "Eugene V. Debs",  # American Socialism
        "Rosa Luxemburg",  # Revolutionary Socialism
        "Michael Harrington",  # 20th Century Democratic Socialism
        "Bernie Sanders",  # Contemporary Democratic Socialism
    ],

    # v10.3: Psychology & Cognitive Science
    "Attachment Theory": ["John Bowlby", "Mary Ainsworth", "Mary Main"],
    "Behaviorism": ["B.F. Skinner", "John B. Watson", "Ivan Pavlov"],
    "CBT Principles": ["Aaron Beck", "Albert Ellis", "Judith Beck"],
    "Cognitive Dissonance": ["Leon Festinger"],
    "Cognitive Linguistics": ["George Lakoff", "Mark Johnson", "Leonard Talmy"],
    "Evolutionary Psychology": ["Leda Cosmides", "John Tooby", "Steven Pinker", "David Buss"],
    "Gestalt Psychology": ["Max Wertheimer", "Wolfgang Köhler", "Kurt Koffka"],
    "Humanistic Psychology": ["Carl Rogers", "Abraham Maslow", "Rollo May"],
    "Maslow's Hierarchy": ["Abraham Maslow"],
    "Trauma Studies": ["Judith Herman", "Bessel van der Kolk", "Cathy Caruth"],

    # v10.3: Literary Theory & Rhetoric
    "Archetypal Criticism": ["Northrop Frye", "Carl Jung"],  # Jung also in Psychoanalytic
    "Bakhtinian Dialogism": ["Mikhail Bakhtin"],
    "Close Reading": ["I.A. Richards", "William Empson", "Cleanth Brooks"],
    "Deconstruction": ["Jacques Derrida", "Paul de Man", "J. Hillis Miller"],
    "Defamiliarization": ["Viktor Shklovsky", "Roman Jakobson"],
    "Dramatism": ["Kenneth Burke"],
    "Genre Studies": ["Tzvetan Todorov", "Northrop Frye", "Jacques Derrida"],
    "Intertextuality": ["Julia Kristeva", "Roland Barthes", "Gerard Genette"],
    "Narratology": ["Gérard Genette", "Mieke Bal", "Seymour Chatman"],
    "Reader-Response": ["Stanley Fish", "Wolfgang Iser", "Norman Holland"],
    "Reception Theory": ["Hans Robert Jauss", "Wolfgang Iser"],
    "Rhetorical Analysis": ["Aristotle", "Cicero", "Quintilian"],
    "Semiotics": ["Ferdinand de Saussure", "Charles Sanders Peirce", "Roland Barthes", "Umberto Eco"],  # Peirce also in Pragmatism
    "Structuralism": ["Claude Lévi-Strauss", "Roland Barthes", "Roman Jakobson"],
    "Stylistics": ["Roman Jakobson", "M.A.K. Halliday", "Geoffrey Leech"],
    "Intentional Fallacy": ["W.K. Wimsatt", "Monroe Beardsley"],

    # v10.3: Film & Media Studies
    "Auteur Theory": ["François Truffaut", "Andrew Sarris", "Peter Wollen"],
    "Cinema Novo": ["Glauber Rocha", "Nelson Pereira dos Santos"],
    "Dogme 95": ["Lars von Trier", "Thomas Vinterberg"],
    "Film Noir": ["Raymond Chandler", "Billy Wilder", "Fritz Lang"],
    "French New Wave": ["Jean-Luc Godard", "François Truffaut", "Agnès Varda"],
    "Italian Neorealism": ["Vittorio De Sica", "Roberto Rossellini", "Luchino Visconti"],
    "New Hollywood": ["Martin Scorsese", "Francis Ford Coppola", "Robert Altman"],
    "Soviet Montage": ["Sergei Eisenstein", "Dziga Vertov", "Vsevolod Pudovkin"],
    "Third Cinema": ["Fernando Solanas", "Octavio Getino", "Glauber Rocha"],  # Rocha also in Cinema Novo
    "Media Ecology": ["Marshall McLuhan", "Neil Postman", "Walter Ong"],

    # v10.3: Art & Design
    "Surrealism": ["André Breton", "Salvador Dalí", "René Magritte"],
    "Suprematism": ["Kazimir Malevich"],
    "Iconography/Iconology": ["Erwin Panofsky", "Aby Warburg"],

    # v10.3: Sociology & Systems
    "Actor-Network Theory (ANT)": ["Bruno Latour", "Michel Callon", "John Law"],
    "Chaos Theory": ["Edward Lorenz", "Benoit Mandelbrot", "Ilya Prigogine"],
    "Conflict Theory": ["Karl Marx", "C. Wright Mills", "Ralf Dahrendorf"],  # Marx also in Marxism, Dialectical Materialism
    "Cultural Materialism": ["Marvin Harris"],
    "Cybernetics": ["Norbert Wiener", "Gregory Bateson", "Heinz von Foerster"],
    "Ethnomethodology": ["Harold Garfinkel"],
    "Functionalism": ["Émile Durkheim", "Talcott Parsons", "Robert K. Merton"],
    "Game Theory": ["John von Neumann", "John Nash", "Thomas Schelling"],
    "Ludology": ["Jesper Juul", "Gonzalo Frasca", "Ian Bogost"],
    "Network Analysis": ["Stanley Milgram", "Mark Granovetter", "Duncan Watts"],
    "Social Constructionism": ["Peter L. Berger", "Thomas Luckmann", "Kenneth Gergen"],
    "Symbolic Interactionism": ["George Herbert Mead", "Herbert Blumer", "Erving Goffman"],
    "Systems Theory": ["Ludwig von Bertalanffy", "Niklas Luhmann"],

    # v10.3: History & Historical Theory
    "Annales School": ["Marc Bloch", "Fernand Braudel", "Lucien Febvre"],
    "Great Man Theory": ["Thomas Carlyle"],
    "Historiography": ["Leopold von Ranke", "Edward Gibbon", "Fernand Braudel"],  # Braudel also in Annales School
    "New Historicism": ["Stephen Greenblatt", "Louis Montrose"],

    # v10.3: Theology & Religion (Expanded)
    "Comparative Mythology": ["Joseph Campbell", "Mircea Eliade", "Carl Jung"],  # Jung also in Psychoanalytic, Archetypal
    "Hinduism: Advaita Vedanta": ["Adi Shankara (Shankaracharya)", "Swami Vivekananda"],
    "Islam: Sufism": ["Rumi (Jalal ad-Din Muhammad Rumi)", "Hafez", "Al-Ghazali", "Ibn Arabi"],

    # v10.3: Warfare & Strategy
    "Bushido": ["Miyamoto Musashi", "Yamamoto Tsunetomo", "Inazo Nitobe"],
    "Chivalry": ["Geoffroi de Charny", "Christine de Pizan", "Sir Thomas Malory"],
    "Guerrilla Warfare": ["Mao Zedong", "Che Guevara", "T.E. Lawrence"],

    # Archaeological Analysis
    "Archaeological Analysis": [
        "Heinrich Schliemann",  # Troy, Mycenae - pioneering excavator
        "Howard Carter",  # Tutankhamun's tomb - meticulous methodology
        "Sir Mortimer Wheeler",  # Wheeler-Kenyon method - scientific excavation
        "Mary Leakey",  # Olduvai Gorge - paleoanthropology
        "Kathleen Kenyon",  # Jericho - stratigraphic method
    ],

    # v10.3: Art Movements & Aesthetics (Expanded)
    "Abstract Expressionism": ["Jackson Pollock", "Willem de Kooning", "Mark Rothko"],
    "Aestheticism": ["Oscar Wilde", "Walter Pater", "Théophile Gautier"],
    "Art Deco": ["Tamara de Lempicka", "Erté (Romain de Tirtoff)"],
    "Avant-Garde Studies": ["Marcel Duchamp", "John Cage", "Yoko Ono"],
    "Baroque Aesthetics": ["Gian Lorenzo Bernini", "Peter Paul Rubens", "Caravaggio"],
    "Constructivism": ["Vladimir Tatlin", "Alexander Rodchenko", "El Lissitzky"],
    "Cubism": ["Pablo Picasso", "Georges Braque", "Juan Gris"],
    "Dadaism": ["Marcel Duchamp", "Tristan Tzara", "Hugo Ball"],
    "De Stijl": ["Piet Mondrian", "Theo van Doesburg"],
    "Expressionism": ["Edvard Munch", "Ernst Ludwig Kirchner", "Emil Nolde"],
    "German Expressionism": ["Fritz Lang", "F.W. Murnau", "Robert Wiene"],
    "Fauvism": ["Henri Matisse", "André Derain", "Maurice de Vlaminck"],
    "Futurism": ["Filippo Tommaso Marinetti", "Umberto Boccioni"],
    "Impressionism": ["Claude Monet", "Pierre-Auguste Renoir", "Edgar Degas"],
    "Minimalism": ["Donald Judd", "Dan Flavin", "Carl Andre"],
    "Modernism": ["T.S. Eliot", "James Joyce", "Virginia Woolf"],  # Woolf also in Feminism
    "Pop Art": ["Andy Warhol", "Roy Lichtenstein", "Jasper Johns"],
    "Postmodernism": ["Jean-François Lyotard", "Jean Baudrillard", "Fredric Jameson"],
    "Realism": ["Gustave Courbet", "Honoré Daumier", "Ilya Repin"],
    "Renaissance Aesthetics": ["Leon Battista Alberti", "Giorgio Vasari", "Baldassare Castiglione"],
    "Romanticism": ["William Wordsworth", "Lord Byron", "Mary Shelley"],

    # v10.3: Film Criticism & Theory (Additional)
    "Formalism": ["Sergei Eisenstein", "Rudolf Arnheim", "Viktor Shklovsky"],  # Shklovsky also in Defamiliarization
    "Impressionistic Criticism": ["Virginia Woolf", "Walter Pater"],  # Woolf in Feminism, Modernism
    "Mumblecore": ["Joe Swanberg", "Andrew Bujalski", "Lynn Shelton"],
    "Pragmatic Criticism": ["I.A. Richards", "William Empson"],  # Richards also in Close Reading

    # v10.3: Political Philosophy (Additional)
    "Communitarianism": ["Alasdair MacIntyre", "Michael Sandel", "Charles Taylor"],  # MacIntyre also in Virtue Ethics
    "Critical Race Theory (CRT)": ["Derrick Bell", "Kimberlé Crenshaw", "Richard Delgado"],  # Crenshaw in Feminism, Intersectionality
    "Libertarianism": ["Robert Nozick", "Murray Rothbard", "Ayn Rand"],  # Rand in Egoism
    "Neoliberalism": ["Friedrich Hayek", "Milton Friedman", "Margaret Thatcher"],  # Hayek in Classical Liberalism
    "Political Economy": ["Adam Smith", "David Ricardo", "John Maynard Keynes"],  # Smith in Classical Liberalism
    "Realpolitik": ["Otto von Bismarck", "Henry Kissinger", "Niccolò Machiavelli"],  # Machiavelli in Republicanism
    "Secular Humanism": ["Bertrand Russell", "Carl Sagan", "A.C. Grayling"],  # Russell in Analytic Philosophy

    # v10.3: Literary & Cultural Studies (Additional)
    "Affect Theory": ["Eve Kosofsky Sedgwick", "Sara Ahmed", "Lauren Berlant"],
    "Afrofuturism": ["Octavia Butler", "Samuel R. Delany", "N.K. Jemisin"],
    "Biographical Analysis": ["James Boswell", "Lytton Strachey", "Richard Ellmann"],
    "Disability Studies": ["Rosemarie Garland-Thomson", "Tobin Siebers", "Lennard J. Davis"],
    "Ecocriticism": ["Lawrence Buell", "Cheryll Glotfelty", "Timothy Morton"],
    "Gender Studies": ["Judith Butler", "Raewyn Connell", "Michael Kimmel"],  # Butler in Feminism
    "Historical Contextualism": ["Stephen Greenblatt", "Jerome McGann"],  # Greenblatt in New Historicism
    "Indigenous Methodologies": ["Linda Tuhiwai Smith", "Shawn Wilson", "Margaret Kovach"],
    "Mythopoeic Analysis": ["Joseph Campbell", "Northrop Frye"],  # Campbell in Comparative Mythology; Frye in Archetypal Criticism
    "Oral History": ["Studs Terkel", "Alessandro Portelli", "Paul Thompson"],
    "Presentism": ["David Hackett Fischer", "Lynn Hunt"],
    "Queer Theory": ["Judith Butler", "Eve Kosofsky Sedgwick", "Jack Halberstam"],  # Butler in Feminism, Gender Studies; Sedgwick in Affect Theory
    "Whiteness Studies": ["Ruth Frankenberg", "David Roediger", "Cheryl Harris"],

    # v10.3: Economics & Behavioral Science
    "Behavioral Economics": ["Daniel Kahneman", "Amos Tversky", "Richard Thaler"],
    "Geopolitical Analysis": ["Halford Mackinder", "Nicholas Spykman", "Zbigniew Brzezinski"],

    # v10.3: Religion & Theology (Additional)
    "Hinduism: General Philosophy": ["Swami Vivekananda", "Aurobindo Ghose", "Sarvepalli Radhakrishnan"],
    "Islamic Theology (Kalam)": ["Al-Ghazali", "Imam Al-Ash'ari", "Fakhr al-Din al-Razi"],
    "Judaism: Kabbalah": ["Isaac Luria", "Moses de León", "Gershom Scholem"],
    "Judaism: Talmudic/Rabbinic": ["Maimonides (Moses ben Maimon)", "Rashi (Rabbi Shlomo Yitzhaki)", "Rabbi Akiva"],
    "Shinto": ["Motoori Norinaga", "Hirata Atsutane"],

    # Mythological Personas (God's-Eye View)
    "Greco-Roman Myth": ["Zeus", "Athena", "Hades", "Apollo", "Hera", "Odysseus"],
    "Norse Myth": ["Odin (The Allfather)", "Thor", "Loki", "Freyja"],
    "Egyptian Myth": ["Ra", "Osiris", "Isis", "Anubis", "Thoth"],
    "Mesoamerican Myth": ["Quetzalcoatl", "Tezcatlipoca", "Huitzilopochtli"],
}

# -----------------------------------------------------------------------------
# 7. PERSONA METADATA (v10.2: Cascading Filter Integration)
# Reverse-maps personas to their attributes (disciplines, functions, eras, lenses).
# Built dynamically from PERSONA_POOL and lens data.
# -----------------------------------------------------------------------------

def _build_persona_metadata():
    """
    Builds PERSONA_METADATA by iterating through PERSONA_POOL and extracting
    attributes from the associated lenses.

    Returns: dict mapping persona_name -> {disciplines: set, functions: set, eras: set, lenses: list}
    """
    from collections import defaultdict

    metadata = defaultdict(lambda: {
        'disciplines': set(),
        'functions': set(),
        'eras': set(),
        'lenses': []
    })

    for lens_name, personas in PERSONA_POOL.items():
        # Get lens attributes directly from LENS_DEFINITIONS
        lens_data = LENS_DEFINITIONS.get(lens_name)
        if not lens_data:
            continue

        lens_eras = set(lens_data.get('eras', []))

        # Find disciplines containing this lens
        lens_disciplines = set()
        for disc_name, lenses in LENSES_HIERARCHY.items():
            if lens_name in lenses:
                lens_disciplines.add(disc_name)

        # Find functions containing this lens
        lens_functions = set()
        for func_name, lenses in LENSES_FUNCTIONAL.items():
            if lens_name in lenses:
                lens_functions.add(func_name)

        # Add to each persona in this lens's pool
        for persona in personas:
            metadata[persona]['disciplines'].update(lens_disciplines)
            metadata[persona]['functions'].update(lens_functions)
            metadata[persona]['eras'].update(lens_eras)
            metadata[persona]['lenses'].append(lens_name)

    return dict(metadata)

# Build the metadata at module load time
PERSONA_METADATA = _build_persona_metadata()

# Create a sorted list of all personas for UI
SORTED_PERSONA_NAMES = sorted(list(PERSONA_METADATA.keys()))


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