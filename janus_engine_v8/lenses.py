# lenses.py
import logging

# --- LENSES HIERARCHY & MAPPINGS ---

# This structure is used for the "Library" view (View by Discipline)
LENSES_HIERARCHY = {
    "Structural & Formalist": ["Formalist", "Structuralism", "Narratology", "Semiotics", "Computational Analysis/Digital Humanities"],
    "Psychological": ["Jungian", "Freudian", "Evolutionary Psychology", "Behaviorism", "Lacanian"],
    "Philosophical": ["Existentialist", "Taoist", "Phenomenological", "Stoicism", "Platonism", "Nietzschean", "Absurdism"],
    "Socio-Political": ["Marxist", "Feminist", "Post-Colonial", "Queer Theory"],
    
    # --- Art History & Aesthetics ---
    "Art History & Aesthetics": [
        "Aestheticism",
        "Cubism",
        "Surrealism",
        "Iconography/Iconology",
        "Formalist Art Criticism",
        "Impressionism"
    ],
    
    # --- Communication & Media Theory ---
    "Communication & Media Theory": [
        "Rhetorical Analysis",
        "Media Ecology (McLuhan)",
        "Agenda-Setting Theory",
        "Uses and Gratifications Theory"
    ],

    "Ethical Frameworks": ["Utilitarianism", "Virtue Ethics", "Deontology (Kantian)", "Bioethics"],
    "Scientific & STEM Perspectives": [
        "Cognitive Science", "Systems Theory (Complexity)", "Ecocriticism",
        "Astrophysics/Cosmology", "Materials Science", "Epidemiology"
    ],
    "Economics & Systems": [
        "Game Theory", "Behavioral Economics", "Supply Chain Analysis"
    ],
    "Law & Governance": [
        "Legal Positivism", "Critical Legal Studies"
    ],
    "Spiritual & Esoteric": [
        "Animism",
        "Bhakti Yoga (Hindu Devotion)",
        "Buddhist Philosophy (General)",
        "Christian Mysticism",
        "Christian Theology",
        "Gnosticism",
        "Hermeticism",
        "Kabbalah (Jewish Mysticism)",
        "Mysticism (General)",
        "Quranic Studies (Islam)",
        "Rabbinic Thought (Judaism)",
        "Shinto",
        "Sufism (Islamic Mysticism)",
        "Tibetan Buddhism",
        "Vedanta (Hindu Philosophy)",
        "Western Esotericism",
        "Zen Buddhism",
    ],
    "Historical & Contextual": ["Biographical", "Historical Context", "Reader-Response"],
}

# --- HELPER FUNCTIONS ---

def flatten_lenses(lenses_hierarchy):
    """Flattens a hierarchical dictionary into a sorted list of lens names."""
    flat_lenses = []
    for category, lens_list in lenses_hierarchy.items():
        flat_lenses.extend(lens_list)
    return sorted(list(set(flat_lenses))) # Use set to ensure uniqueness

# Helper function for the Multi-Stage selection UI
def get_filtered_lenses(hierarchy, selected_categories):
    """Filters lenses based on selected categories from a hierarchy."""
    filtered_lenses = []
    for category in selected_categories:
        if category in hierarchy:
            filtered_lenses.extend(hierarchy[category])
    # Return a sorted list of unique lenses found across the selected categories
    return sorted(list(set(filtered_lenses)))

def create_functional_mapping(lenses_hierarchy):
    """Maps lenses from the hierarchy to the Three Tiers of Inquiry."""
    # This mapping defines the "Workshop" view (View by Function)
    mapping = {
        "Contextual (What, Who, Where, When)": [
            "Biographical", "Historical Context", "Reader-Response",
            "Epidemiology", "Supply Chain Analysis", "Astrophysics/Cosmology",
            "Quranic Studies (Islam)",
            "Rabbinic Thought (Judaism)",
            "Iconography/Iconology",
            "Agenda-Setting Theory",
        ],
        "Mechanical (How)": [
            "Formalist", "Structuralism", "Narratology", "Semiotics",
            "Systems Theory (Complexity)", "Cognitive Science", "Behaviorism",
            "Game Theory", "Behavioral Economics",
            "Computational Analysis/Digital Humanities", "Materials Science",
            "Legal Positivism",
            "Cubism",
            "Formalist Art Criticism",
            "Impressionism",
            "Rhetorical Analysis",
        ],
        "Interpretive (Why)": [
            "Jungian", "Freudian", "Lacanian", "Evolutionary Psychology",
            "Existentialist", "Taoist", "Phenomenological", "Stoicism", "Platonism", "Nietzschean", "Absurdism",
            "Marxist", "Feminist", "Post-Colonial", "Queer Theory",
            "Utilitarianism", "Virtue Ethics", "Deontology (Kantian)", "Bioethics",
            "Ecocriticism",
            "Critical Legal Studies",
            # Spiritual/Esoteric
            "Animism",
            "Bhakti Yoga (Hindu Devotion)",
            "Buddhist Philosophy (General)",
            "Christian Mysticism",
            "Christian Theology",
            "Gnosticism",
            "Hermeticism",
            "Kabbalah (Jewish Mysticism)",
            "Mysticism (General)",
            "Shinto",
            "Sufism (Islamic Mysticism)",
            "Tibetan Buddhism",
            "Vedanta (Hindu Philosophy)",
            "Western Esotericism",
            "Zen Buddhism",
            "Aestheticism",
            "Surrealism",
            "Media Ecology (McLuhan)",
            "Uses and Gratifications Theory",
        ]
    }
    
    # Validation check
    all_hierarchical = set(flatten_lenses(lenses_hierarchy))
    all_functional = set(flatten_lenses(mapping))
    
    missing = all_hierarchical - all_functional
    if missing:
        logging.warning(f"DATA INTEGRITY WARNING: Lenses missing from functional mapping: {missing}")

    # Ensure internal lists are sorted
    for key in mapping:
        mapping[key] = sorted(mapping[key])

    return mapping

# Initialize the functional mapping and the flattened list
LENSES_FUNCTIONAL = create_functional_mapping(LENSES_HIERARCHY)
# SORTED_LENS_NAMES is used for data integrity checks and Smart Selection input
SORTED_LENS_NAMES = flatten_lenses(LENSES_HIERARCHY)