# lenses.py
import logging

# --- LENSES HIERARCHY & MAPPINGS ---

# This structure is used for the "Library" view (View by Discipline)
# v8.1: Alphabetized both categories and lenses within them.
LENSES_HIERARCHY = {
    "Art History & Aesthetics": [
        "Aestheticism",
        "Cubism",
        "Formalist Art Criticism",
        "Iconography/Iconology",
        "Impressionism",
        "Surrealism"
    ],
    "Communication & Media Theory": [
        "Agenda-Setting Theory",
        "Media Ecology (McLuhan)",
        "Rhetorical Analysis",
        "Uses and Gratifications Theory"
    ],
    "Economics & Systems": [
        "Behavioral Economics", 
        "Game Theory", 
        "Supply Chain Analysis"
    ],
    "Ethical Frameworks": [
        "Bioethics",
        "Bushido",
        "Chivalry",
        "Confucianism",
        "Deontology (Kantian)",
        "Utilitarianism",
        "Virtue Ethics"
    ],
    "Historical & Contextual": [
        "Biographical", 
        "Historical Context", 
        "Reader-Response"
    ],
    "Law & Governance": [
        "Critical Legal Studies",
        "Legal Positivism"
    ],
    "Philosophical": [
        "Absurdism",
        "Existentialist",
        "Nietzschean",
        "Phenomenological",
        "Platonism",
        "Stoicism",
        "Taoist"
    ],
    "Psychological": [
        "Behaviorism", 
        "Evolutionary Psychology", 
        "Freudian", 
        "Jungian", 
        "Lacanian"
    ],
    "Scientific & STEM Perspectives": [
        "Astrophysics/Cosmology",
        "Cognitive Science",
        "Ecocriticism",
        "Epidemiology",
        "Materials Science",
        "Systems Theory (Complexity)"
    ],
    "Socio-Political": [
        "Feminist", 
        "Marxist", 
        "Post-Colonial", 
        "Queer Theory"
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
        "Zen Buddhism"
    ],
    "Structural & Formalist": [
        "Computational Analysis/Digital Humanities",
        "Formalist", 
        "Narratology", 
        "Semiotics", 
        "Structuralism"
    ],
}

# --- HELPER FUNCTIONS ---

def flatten_lenses(lenses_hierarchy):
    """Flattens a hierarchical dictionary into a sorted list of lens names."""
    flat_lenses = []
    for category, lens_list in lenses_hierarchy.items():
        flat_lenses.extend(lens_list)
    return sorted(list(set(flat_lenses)))

def get_filtered_lenses(hierarchy, selected_categories):
    """Filters lenses based on selected categories from a hierarchy."""
    filtered_lenses = []
    for category in selected_categories:
        if category in hierarchy:
            filtered_lenses.extend(hierarchy[category])
    return sorted(list(set(filtered_lenses)))

def create_functional_mapping(lenses_hierarchy):
    """Maps lenses from the hierarchy to the Three Tiers of Inquiry."""
    mapping = {
        "Contextual (What, Who, Where, When)": [
            "Agenda-Setting Theory",
            "Astrophysics/Cosmology",
            "Biographical",
            "Epidemiology",
            "Historical Context",
            "Iconography/Iconology",
            "Quranic Studies (Islam)",
            "Rabbinic Thought (Judaism)",
            "Reader-Response",
            "Supply Chain Analysis"
        ],
        "Mechanical (How)": [
            "Behavioral Economics",
            "Behaviorism",
            "Cognitive Science",
            "Computational Analysis/Digital Humanities",
            "Cubism",
            "Formalist",
            "Formalist Art Criticism",
            "Game Theory",
            "Impressionism",
            "Legal Positivism",
            "Materials Science",
            "Narratology",
            "Rhetorical Analysis",
            "Semiotics",
            "Structuralism",
            "Systems Theory (Complexity)"
        ],
        "Interpretive (Why)": [
            "Absurdism",
            "Aestheticism",
            "Animism",
            "Bhakti Yoga (Hindu Devotion)",
            "Bioethics",
            "Buddhist Philosophy (General)",
            "Bushido",
            "Chivalry",
            "Christian Mysticism",
            "Christian Theology",
            "Confucianism",
            "Critical Legal Studies",
            "Deontology (Kantian)",
            "Ecocriticism",
            "Evolutionary Psychology",
            "Existentialist",
            "Feminist",
            "Freudian",
            "Gnosticism",
            "Hermeticism",
            "Jungian",
            "Kabbalah (Jewish Mysticism)",
            "Lacanian",
            "Marxist",
            "Media Ecology (McLuhan)",
            "Mysticism (General)",
            "Nietzschean",
            "Phenomenological",
            "Platonism",
            "Post-Colonial",
            "Queer Theory",
            "Shinto",
            "Stoicism",
            "Sufism (Islamic Mysticism)",
            "Surrealism",
            "Taoist",
            "Tibetan Buddhism",
            "Uses and Gratifications Theory",
            "Utilitarianism",
            "Vedanta (Hindu Philosophy)",
            "Virtue Ethics",
            "Western Esotericism",
            "Zen Buddhism"
        ]
    }
    
    # Validation check
    all_hierarchical = set(flatten_lenses(lenses_hierarchy))
    all_functional = set(flatten_lenses(mapping))
    
    missing = all_hierarchical - all_functional
    if missing:
        logging.warning(f"DATA INTEGRITY WARNING: Lenses missing from functional mapping: {missing}")

    # The original script already had a sort here, but this ensures it.
    for key in mapping:
        mapping[key] = sorted(mapping[key])

    return mapping

# Initialize the functional mapping and the flattened list
LENSES_FUNCTIONAL = create_functional_mapping(LENSES_HIERARCHY)
SORTED_LENS_NAMES = flatten_lenses(LENSES_HIERARCHY)
