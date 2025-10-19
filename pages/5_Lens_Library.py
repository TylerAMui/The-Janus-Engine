import streamlit as st
import pandas as pd
import utils
from lenses import LENS_DEFINITIONS, PERSONA_POOL, SORTED_LENS_NAMES, get_lens_data

# --- PAGE SETUP ---
PAGE_TITLE = "Janus | Lens Library"
utils.initialize_page_config(PAGE_TITLE)
st.title("📚 Lens Library")
st.write("Browse and search all entries in the Janus Engine's knowledge base. Use filters and search to explore lenses, personas, disciplines, functions, and eras.")

# --- SIDEBAR ---
utils.render_sidebar_settings()

# v10.2: Initialize perspective cart for multi-perspective analysis
if 'library_perspectives' not in st.session_state:
    st.session_state.library_perspectives = []

# v10.2: Sidebar perspective status (always visible)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Perspectives")

perspective_count = len(st.session_state.library_perspectives)

if perspective_count > 0:
    st.sidebar.markdown(f"**Total:** {perspective_count}/6")
    for i, persp in enumerate(st.session_state.library_perspectives):
        st.sidebar.caption(f"{i+1}. {persp.get('lens', 'Unknown')}")
else:
    st.sidebar.caption("No perspectives configured")

st.markdown("---")

# v10.2: Build unified entry database (cached to avoid rebuilding on every rerun)
@st.cache_data
def get_cached_entries():
    return utils.get_all_entries()

all_entries = get_cached_entries()

# v10.2: Handle jump-to-entry from 🔍 buttons
# Track all entries that should be temporarily visible in a list (to maintain order)
if 'library_jump_entries' not in st.session_state:
    st.session_state.library_jump_entries = []  # Changed from set to list for ordering
if 'library_most_recent_jump' not in st.session_state:
    st.session_state.library_most_recent_jump = None

if 'library_search_target' in st.session_state:
    target_name = st.session_state.library_search_target

    # Remove from list if already present (to avoid duplicates)
    if target_name in st.session_state.library_jump_entries:
        st.session_state.library_jump_entries.remove(target_name)

    # Add to the BEGINNING of the list (most recent first)
    st.session_state.library_jump_entries.insert(0, target_name)

    # Track the most recent jump for highlighting
    st.session_state.library_most_recent_jump = target_name

    # Auto-expand this entry
    target_entry = next((e for e in all_entries if e['name'] == target_name), None)
    if target_entry:
        entry_key = f"{target_entry['type']}_{target_entry['name']}"
        st.session_state.library_expanded_entries.add(entry_key)
    # Clear the target
    del st.session_state.library_search_target

# v10.2: Show jump-to-entry banner if active
if st.session_state.library_jump_entries:
    col1, col2 = st.columns([5, 1])
    with col1:
        count = len(st.session_state.library_jump_entries)
        if count == 1:
            entry_name = st.session_state.library_jump_entries[0]
            target_entry = next((e for e in all_entries if e['name'] == entry_name), None)
            if target_entry:
                st.info(f"📍 Showing 1 navigation entry: **{target_entry['icon']} {target_entry['name']}**")
        else:
            st.info(f"📍 Showing {count} navigation entries (most recent first)")
    with col2:
        if st.button("✕ Clear All", use_container_width=True, key="clear_jump"):
            st.session_state.library_jump_entries = []
            st.rerun()
    st.markdown("---")

# v10.2: Entry Type Filters (Checkboxes)
st.markdown("**Filter by Entry Type:**")
filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)

# Simple checkboxes - no manipulation, just user's choice
with filter_col1:
    show_lenses = st.checkbox("📖 Lenses", value=True, key="filter_lenses")
with filter_col2:
    show_personas = st.checkbox("🎭 Personas", value=True, key="filter_personas")
with filter_col3:
    show_disciplines = st.checkbox("🏛️ Disciplines", value=True, key="filter_disciplines")
with filter_col4:
    show_functions = st.checkbox("⚙️ Functions", value=True, key="filter_functions")
with filter_col5:
    show_eras = st.checkbox("📅 Eras", value=True, key="filter_eras")

# Build selected types list
selected_types = []
if show_lenses:
    selected_types.append('lens')
if show_personas:
    selected_types.append('persona')
if show_disciplines:
    selected_types.append('discipline')
if show_functions:
    selected_types.append('function')
if show_eras:
    selected_types.append('era')

# v10.2: Search Bar
search_query = st.text_input(
    "🔍 Search across all entries:",
    placeholder="e.g., 'philosophy', 'Marx', 'power', '20th century'...",
    help="Search finds matches in entry names, descriptions, and all related tags"
)

st.markdown("---")

# v10.2: Apply filtering logic
# Always apply normal search and checkbox filters
filtered_entries = utils.search_library_entries(all_entries, search_query, selected_types)

# v10.2: Build final list with jump entries at the top in reverse chronological order
jump_entries_list = []
non_jump_entries = []

if st.session_state.library_jump_entries:
    # Separate jump entries from regular entries
    for entry in filtered_entries:
        if entry['name'] in st.session_state.library_jump_entries:
            jump_entries_list.append(entry)
        else:
            non_jump_entries.append(entry)

    # Add jump entries that aren't already in filtered results
    for jump_entry_name in st.session_state.library_jump_entries:
        if not any(e['name'] == jump_entry_name for e in jump_entries_list):
            target_entry = next((e for e in all_entries if e['name'] == jump_entry_name), None)
            if target_entry:
                jump_entries_list.append(target_entry)

    # Sort jump entries by their position in the jump list (maintains chronological order)
    jump_entries_list = sorted(jump_entries_list,
                                key=lambda e: st.session_state.library_jump_entries.index(e['name']))

    # Sort non-jump entries normally
    type_order = {'lens': 1, 'persona': 2, 'discipline': 3, 'function': 4, 'era': 5}
    non_jump_entries = sorted(non_jump_entries, key=lambda e: (type_order.get(e['type'], 99), e['name']))

    # Combine: jump entries first, then regular entries
    filtered_entries = jump_entries_list + non_jump_entries
else:
    # No jump entries - just sort normally
    type_order = {'lens': 1, 'persona': 2, 'discipline': 3, 'function': 4, 'era': 5}
    filtered_entries = sorted(filtered_entries, key=lambda e: (type_order.get(e['type'], 99), e['name']))

# v10.2: Display results count
total_count = len(all_entries)
filtered_count = len(filtered_entries)
st.markdown(f"**Showing {filtered_count} of {total_count} entries**")

# v10.2: Initialize expanded state tracking
if 'library_expanded_entries' not in st.session_state:
    st.session_state.library_expanded_entries = set()

# v10.2: Helper function to sanitize entry names for HTML IDs
def sanitize_for_html_id(text):
    """Convert text to valid HTML ID (no spaces, special chars)"""
    import re
    # Replace spaces and special chars with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', text)
    return sanitized

# v10.2: Render entry content with anchors
if filtered_entries:
    for idx, entry in enumerate(filtered_entries):
        entry_type = entry['type']
        entry_name = entry['name']
        entry_icon = entry['icon']
        entry_description = entry['description']
        entry_related = entry['related']

        # Create unique key for this entry
        entry_key = f"{entry_type}_{entry_name}"
        is_expanded = entry_key in st.session_state.library_expanded_entries
        is_most_recent_jump = (entry_name == st.session_state.library_most_recent_jump)

        # Render anchor IMMEDIATELY before this entry's container for accurate scroll positioning
        sanitized_key = f"{entry_type}_{sanitize_for_html_id(entry_name)}"
        st.markdown(f'<div id="anchor_{sanitized_key}"></div>', unsafe_allow_html=True)

        # Check if this is a temporarily shown jump entry
        is_jump_entry = entry_name in st.session_state.library_jump_entries

        # Create collapsible button with container (highlight if most recent jump)
        with st.container(border=True):
            # Show visual indicator and dismiss button for jump entries
            if is_jump_entry:
                ind_col1, ind_col2 = st.columns([5, 1])
                with ind_col1:
                    if is_most_recent_jump:
                        st.markdown("🔵 **← Just navigated here**")
                    else:
                        # Show position in navigation history
                        position = st.session_state.library_jump_entries.index(entry_name) + 1
                        st.markdown(f"📍 **Navigation #{position}**")
                with ind_col2:
                    if st.button("✕", key=f"dismiss_{entry_key}", help=f"Remove {entry_name} from navigation"):
                        st.session_state.library_jump_entries.remove(entry_name)
                        # Clear most recent jump if this was it
                        if st.session_state.library_most_recent_jump == entry_name:
                            st.session_state.library_most_recent_jump = None
                        st.rerun()

            # Toggle button
            arrow = "▲" if is_expanded else "▼"
            button_type = "primary" if is_most_recent_jump else "secondary"
            if st.button(f"{entry_icon} **{entry_name}** ({entry_type.capitalize()}) {arrow}",
                        key=f"toggle_{entry_key}",
                        use_container_width=True,
                        type=button_type):
                # Toggle expanded state
                if is_expanded:
                    st.session_state.library_expanded_entries.remove(entry_key)
                else:
                    st.session_state.library_expanded_entries.add(entry_key)
                st.rerun()

            # Show details if expanded
            if is_expanded:
                st.markdown(f"**Description:** {entry_description}")

                # Show related entries with wiki-style links
                st.markdown("---")
                st.markdown("**Related Entries:**")

                # Helper function to render related items with search buttons
                def render_related_items(items, icon, label):
                    if not items:
                        return

                    # Display items with label inline with first item, subsequent items aligned
                    for idx, item in enumerate(items):
                        cols = st.columns([1, 4, 0.5])
                        with cols[0]:
                            if idx == 0:
                                st.markdown(f"**{label}:**")
                        with cols[1]:
                            st.markdown(f"{icon} {item}")
                        with cols[2]:
                            if st.button("🔍", key=f"search_{entry_name}_{item}", help=f"Jump to {item}"):
                                # Set search query and trigger rerun
                                st.session_state.library_search_target = item
                                st.rerun()

                # Related lenses
                render_related_items(entry_related['lenses'], '📖', 'Lenses')

                # Related personas
                render_related_items(entry_related['personas'], '🎭', 'Personas')

                # Related disciplines
                render_related_items(entry_related['disciplines'], '🏛️', 'Disciplines')

                # Related functions
                render_related_items(entry_related['functions'], '⚙️', 'Functions')

                # Related eras
                render_related_items(entry_related['eras'], '📅', 'Eras')

                # v10.2: Perspective Cart Actions (only for lenses)
                if entry_type == 'lens':
                    st.markdown("---")
                    # Check if lens already in perspectives
                    is_in_cart = any(p.get('lens') == entry_name for p in st.session_state.library_perspectives)
                    cart_full = len(st.session_state.library_perspectives) >= 6

                    if is_in_cart:
                        st.button("✓ Already in Perspectives", key=f"cart_{entry_name}", disabled=True, use_container_width=True)
                    elif cart_full:
                        st.button("Cart Full (6/6)", key=f"cart_{entry_name}", disabled=True, use_container_width=True)
                    else:
                        if st.button(f"+ Add to Perspectives ({perspective_count}/6)", key=f"cart_{entry_name}", use_container_width=True):
                            # Add minimal perspective structure (will be enhanced in Phase 3)
                            st.session_state.library_perspectives.append({
                                'lens': entry_name,
                                'persona': None,
                                'discipline': None,
                                'function': None,
                                'era': None
                            })
                            st.toast(f"✅ Added {entry_name} to perspectives!", icon="📖")
                            st.rerun()

else:
    st.info("No entries found matching your search and filter criteria.")

# v10.2: Perspective Management (if any perspectives exist)
if perspective_count > 0:
    st.markdown("---")
    st.subheader("🎯 Your Perspectives")

    # Show each perspective with remove button
    for i, persp in enumerate(st.session_state.library_perspectives):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{i+1}.** 📖 {persp['lens']}")
        with col2:
            if st.button("✕", key=f"remove_persp_{i}", help=f"Remove {persp['lens']}"):
                st.session_state.library_perspectives.pop(i)
                st.rerun()

    st.markdown("---")

    # Navigation buttons based on perspective count
    nav_col1, nav_col2, nav_col3 = st.columns(3)

    with nav_col1:
        if perspective_count >= 1:
            if st.button("→ Single Lens Analysis", type="primary", use_container_width=True):
                # Transfer first perspective
                st.session_state.library_selected_lens = st.session_state.library_perspectives[0]['lens']
                st.switch_page("pages/1_Single_Lens.py")

    with nav_col2:
        if perspective_count >= 2:
            if st.button("→ Dialectical Analysis", type="primary", use_container_width=True):
                # Transfer first two perspectives
                st.session_state.library_dialectical_cart = [p['lens'] for p in st.session_state.library_perspectives[:2]]
                st.switch_page("pages/2_Dialectical.py")
        else:
            st.caption(f"Need {2 - perspective_count} more for Dialectical")

    with nav_col3:
        if perspective_count >= 3:
            if st.button("→ Symposium Analysis", type="primary", use_container_width=True):
                # Transfer all perspectives
                st.session_state.library_symposium_cart = [p['lens'] for p in st.session_state.library_perspectives]
                st.switch_page("pages/3_Symposium.py")
        else:
            st.caption(f"Need {3 - perspective_count} more for Symposium")

st.markdown("---")
st.caption("💡 **Tip:** Click on any entry to see its description and related entries. Add lenses to your perspectives to configure multi-lens analyses.")

# v10.2: Scroll to most recent jump target if it exists
if st.session_state.library_most_recent_jump:
    # Find the entry to get its key
    target_entry = next((e for e in all_entries if e['name'] == st.session_state.library_most_recent_jump), None)
    if target_entry:
        entry_key = f"{target_entry['type']}_{sanitize_for_html_id(target_entry['name'])}"
        anchor_id = f"anchor_{entry_key}"

        # JavaScript to scroll to the element
        # Try multiple ways to access the parent document
        scroll_js = f"""
        <script>
            (function() {{
                console.log("Scroll script executing for: {anchor_id}");

                function attemptScroll() {{
                    var doc = null;

                    // Try different ways to access the parent document
                    if (window.parent && window.parent.document) {{
                        doc = window.parent.document;
                        console.log("Using window.parent.document");
                    }} else if (window.top && window.top.document) {{
                        doc = window.top.document;
                        console.log("Using window.top.document");
                    }} else if (parent && parent.document) {{
                        doc = parent.document;
                        console.log("Using parent.document");
                    }} else {{
                        console.error("Cannot access parent document!");
                        return;
                    }}

                    var element = doc.getElementById("{anchor_id}");
                    if (element) {{
                        console.log("Element found! Scrolling...");
                        element.scrollIntoView({{behavior: 'smooth', block: 'start'}});
                    }} else {{
                        console.log("Element not found: {anchor_id}");
                        // List all anchor IDs for debugging
                        var anchors = doc.querySelectorAll('[id^="anchor_"]');
                        console.log("Found " + anchors.length + " anchor elements");
                        if (anchors.length > 0) {{
                            console.log("First few anchors:", Array.from(anchors).slice(0, 5).map(a => a.id));
                        }}
                    }}
                }}

                // Wait for DOM to be ready
                setTimeout(attemptScroll, 150);
            }})();
        </script>
        """

        import streamlit.components.v1 as components
        components.html(scroll_js, height=0)
