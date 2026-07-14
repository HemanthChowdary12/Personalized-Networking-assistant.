import streamlit as st
import httpx
import logging
import datetime
from typing import List, Dict, Any

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# --- PAGE SETUP ---
st.set_page_config(page_title="Personalized Networking Assistant | AI-Powered Starter Generator", page_icon="🤝", layout="wide")

# SEO Headers & Google Fonts Styling
st.markdown("""
    <!-- SEO Meta Tags -->
    <meta name="description" content="AI-powered web application that helps users generate smart, tailored conversation starters for professional or social networking events. Uses DistilBERT and GPT-2.">
    <meta name="keywords" content="networking, AI, conversation starters, professional growth, GPT-2, DistilBERT, factchecking">
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Main body customization */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #090d16 0%, #0f172a 50%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    [data-testid="stHeader"] {
        background: transparent;
    }
    
    /* Input fields and selectboxes */
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border-color: #334155 !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="input"] input:focus, div[data-baseweb="textarea"] textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 1px #818cf8 !important;
    }
    
    /* Custom premium card */
    .premium-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
    }
    
    .premium-card:hover {
        transform: translateY(-4px);
        border-color: rgba(129, 140, 248, 0.4);
        box-shadow: 0 20px 30px -5px rgba(0, 0, 0, 0.4), 0 10px 15px -5px rgba(129, 140, 248, 0.05);
    }
    
    .theme-badge {
        display: inline-block;
        background: linear-gradient(90deg, rgba(129, 140, 248, 0.15) 0%, rgba(192, 132, 252, 0.15) 100%);
        border: 1px solid rgba(129, 140, 248, 0.3);
        color: #e0e7ff;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 8px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Title Stylings */
    h1 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        background: linear-gradient(90deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        margin-bottom: 8px !important;
    }
    
    h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        letter-spacing: -0.01em;
        color: #f1f5f9;
    }
    
    /* Tabs customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-bottom: 2px solid transparent;
        color: #94a3b8;
        font-weight: 600;
        font-size: 1.05rem;
        padding: 10px 16px;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #f8fafc;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #818cf8 !important;
        border-bottom-color: #818cf8 !important;
    }
    
    /* Custom buttons */
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4) !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #4f46e5 0%, #4338ca 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.5) !important;
    }

    /* Feedback icon styles */
    .fb-btn-container {
        display: flex;
        gap: 12px;
        margin-top: 12px;
    }
    
    .status-indicator {
        font-size: 0.85rem;
        color: #94a3b8;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND HELPER FUNCTIONS ---
def call_api(method: str, endpoint: str, json_data: Dict[str, Any] = None) -> Dict[str, Any]:
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method.upper() == "POST":
            response = httpx.post(url, json=json_data, timeout=30.0)
        else:
            response = httpx.get(url, timeout=30.0)
            
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API returned status {response.status_code}: {response.text}")
            st.error(f"API Error ({response.status_code}): {response.text}")
            return {}
    except Exception as e:
        logger.error(f"Failed to connect to API endpoint {url}: {e}")
        return {"connection_error": True}

# Fallback Offline Mock Services (in case backend is starting or offline)
def get_mock_themes(desc: str) -> List[str]:
    text = desc.lower()
    themes = []
    if "sustain" in text or "climate" in text or "cities" in text:
        themes.append("Sustainability & Climate Change")
        themes.append("Urban Planning & Smart Cities")
    if "ai" in text or "intelligence" in text or "learning" in text:
        themes.append("Artificial Intelligence")
    if "blockchain" in text or "healthcare" in text:
        themes.append("Blockchain & Cryptography")
        themes.append("Healthcare & Biotech")
    if not themes:
        themes.append("General Networking")
    return themes[:3]

def get_mock_starters(desc: str, themes: List[str], interests: List[str], goals: str) -> List[str]:
    primary_theme = themes[0] if themes else "this event"
    interest_str = ", ".join(interests) if interests else "networking"
    goal_str = goals or "networking"
    return [
        f"Hi! I was reading the event overview on '{primary_theme}'. I'm deeply interested in {interest_str}. What aspect of this field do you focus on?",
        f"With the fast growth of '{primary_theme}', I've been wondering how experts are combining {interest_str} to drive impact. What's your take on this?",
        f"I'm attending this event with the goal to {goal_str} in the {interest_str} space. Do you have any suggestions on whom I should talk to or panels to check out?"
    ]

# --- SIDEBAR & HEADER ---
st.markdown("<h1>Personalized Networking Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:1.15rem; color:#94a3b8; margin-top:-10px; margin-bottom:25px;'>Tailored, AI-powered conversation starters & real-time fact-checking to elevate your networking strategy.</p>", unsafe_allow_html=True)

# Check backend status and toggle offline mode
backend_status = call_api("GET", "/")
backend_online = "connection_error" not in backend_status and backend_status.get("status") == "online"

with st.sidebar:
    st.markdown("### ⚙️ System Status")
    if backend_online:
        st.markdown("🟢 **Backend:** API Online")
    else:
        st.markdown("🔴 **Backend:** Offline/Connecting...")
        st.info("The models will automatically load and fall back gracefully once ready.")

    st.markdown("---")
    st.markdown("### 📘 Tips for Best Results")
    st.markdown("""
    1. **Be Specific**: Write 1-2 detailed sentences about the event.
    2. **Define Interests**: Enter keywords related directly to your technical domain.
    3. **Set a Goal**: Specify if you want to find collaborators, hire talent, or seek mentorship.
    """)

# --- TABS CREATION ---
tab1, tab2, tab3 = st.tabs(["🤝 Generate Starters", "🔍 Fact-Checking Hub", "📊 Strategy & History"])

# --- TAB 1: GENERATE STARTERS ---
with tab1:
    st.markdown("### 🚀 Spark New Conversations")
    st.markdown("Enter event details and your specific interests to generate context-aware icebreakers.")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("#### ✏️ Event & Interest Inputs")
        
        event_desc = st.text_area(
            "Event Description", 
            placeholder="e.g., AI for Sustainable Cities. An interactive session focused on neural network applications for climate mitigation and urban infrastructure grid planning.",
            height=120,
            key="event_desc_input"
        )
        
        interests_input = st.text_input(
            "Your Interests (comma separated)", 
            placeholder="e.g., climate change, urban planning, machine learning",
            key="interests_input"
        )
        
        networking_goal = st.text_input(
            "Networking Goal (optional)", 
            placeholder="e.g., find research collaborators, meet startup founders",
            key="goal_input"
        )
        
        generate_btn = st.button("Generate Smart Starters", use_container_width=True, key="gen_starters_btn")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        if generate_btn:
            if not event_desc:
                st.warning("Please enter an event description to analyze.")
            else:
                interests_list = [i.strip() for i in interests_input.split(",") if i.strip()]
                if not interests_list:
                    interests_list = ["networking"]
                
                with st.spinner("Analyzing event themes and generating custom icebreakers..."):
                    # Call API or use fallback
                    if backend_online:
                        result = call_api("POST", "/generate-conversation", {
                            "event_description": event_desc,
                            "interests": interests_list,
                            "goals": networking_goal
                        })
                    else:
                        # Fallback mode
                        mock_themes = get_mock_themes(event_desc)
                        mock_starters = get_mock_starters(event_desc, mock_themes, interests_list, networking_goal)
                        result = {
                            "id": f"mock_{int(datetime.datetime.now().timestamp())}",
                            "themes": mock_themes,
                            "starters": mock_starters,
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                    
                    if result and "starters" in result:
                        st.session_state.current_generation = result
                        st.success("Analysis complete! Starters generated successfully.")
                    else:
                        st.error("Failed to generate starters. Please check backend log details.")
        
        # Display Results
        if "current_generation" in st.session_state:
            gen = st.session_state.current_generation
            session_id = gen["id"]
            
            st.markdown(f"#### 🏷️ Extracted Event Themes")
            theme_html = ""
            for theme in gen.get("themes", []):
                theme_html += f"<span class='theme-badge'>{theme}</span>"
            if not theme_html:
                theme_html = "<span class='theme-badge'>General Networking</span>"
            st.markdown(theme_html, unsafe_allow_html=True)
            
            st.markdown("#### 💬 Tailored Icebreakers")
            
            for index, starter in enumerate(gen["starters"]):
                starter_id = f"{session_id}_{index}"
                st.markdown(f"""
                <div class="premium-card">
                    <p style="font-size:1.1rem; line-height:1.6; color:#f1f5f9; font-style:italic;">
                        "{starter}"
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Feedback buttons
                fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 4])
                
                # Setup feedback session state to prevent page reload clearing
                fb_key_up = f"fb_up_{starter_id}"
                fb_key_down = f"fb_down_{starter_id}"
                fb_submitted_key = f"fb_submitted_{starter_id}"
                
                if fb_submitted_key not in st.session_state:
                    st.session_state[fb_submitted_key] = None

                with fb_col1:
                    if st.button("👍 Useful", key=fb_key_up):
                        if backend_online:
                            call_api("POST", "/feedback", {"starter_id": starter_id, "rating": "up"})
                        st.session_state[fb_submitted_key] = "up"
                with fb_col2:
                    if st.button("👎 Not Useful", key=fb_key_down):
                        if backend_online:
                            call_api("POST", "/feedback", {"starter_id": starter_id, "rating": "down"})
                        st.session_state[fb_submitted_key] = "down"
                
                with fb_col3:
                    if st.session_state[fb_submitted_key] == "up":
                        st.markdown("<p style='color:#4ade80; margin-top:8px;'>✓ Marked as helpful!</p>", unsafe_allow_html=True)
                    elif st.session_state[fb_submitted_key] == "down":
                        st.markdown("<p style='color:#f87171; margin-top:8px;'>✗ Marked as not helpful</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='color:#64748b; margin-top:8px;'>Rate this starter to improve suggestions</p>", unsafe_allow_html=True)
        else:
            st.info("Your generated results and feedback options will appear here once you click 'Generate Smart Starters'.")

# --- TAB 2: FACT-CHECKING HUB ---
with tab2:
    st.markdown("### 🔍 Fact-Checking & Knowledge Hub")
    st.markdown("Verify buzzwords, tech trends, or company facts quickly via Wikipedia before you speak with peers.")
    
    check_col1, check_col2 = st.columns([2, 3])
    
    with check_col1:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("#### 🌐 Query Wikipedia")
        fact_query = st.text_input(
            "Enter buzzword or topic", 
            placeholder="e.g., blockchain in healthcare, transformers NLP, smart city",
            key="fact_query_input"
        )
        verify_btn = st.button("Verify Fact", use_container_width=True, key="verify_fact_btn")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with check_col2:
        if verify_btn:
            if not fact_query:
                st.warning("Please enter a search query.")
            else:
                with st.spinner(f"Verifying '{fact_query}' via Wikipedia API..."):
                    if backend_online:
                        result = call_api("POST", "/fact-check", {"query": fact_query})
                    else:
                        # Offline fallback mocks
                        mock_facts = {
                            "blockchain in healthcare": {
                                "query": "blockchain in healthcare",
                                "found": True,
                                "summary": "Blockchain technology in healthcare offers security, interoperability, and data integrity. It provides a decentralized ledger to track medical records, secure clinical trials data, and manage pharmaceutical supply chains.",
                                "url": "https://en.wikipedia.org/wiki/Blockchain"
                            },
                            "transformers nlp": {
                                "query": "transformers nlp",
                                "found": True,
                                "summary": "A transformer is a deep learning model that adopts the mechanism of self-attention, differentially weighting the significance of each part of the input data. It is used primarily in natural language processing (NLP) and computer vision.",
                                "url": "https://en.wikipedia.org/wiki/Transformer_(deep_learning_model)"
                            }
                        }
                        
                        query_lower = fact_query.lower()
                        match = None
                        for k, v in mock_facts.items():
                            if k in query_lower:
                                match = v
                                break
                        
                        if match:
                            result = match
                        else:
                            result = {
                                "query": fact_query,
                                "found": False,
                                "summary": f"Could not connect to online Wikipedia API for '{fact_query}', and no offline mock matches. Run backend to test full Wikipedia connection.",
                                "url": ""
                            }
                    
                    if result:
                        if result.get("found"):
                            st.markdown(f"#### 🟢 Verified Reference: *{result.get('query')}*")
                            st.markdown(f"""
                            <div class="premium-card" style="border-left: 4px solid #4ade80;">
                                <p style="font-size:1.05rem; line-height:1.6; color:#e2e8f0;">
                                    {result.get('summary')}
                                </p>
                                <hr style="border-color: rgba(255,255,255,0.05); margin: 15px 0;"/>
                                <a href="{result.get('url')}" target="_blank" style="color:#818cf8; text-decoration:none; font-weight:600;">
                                    📖 Read complete article on Wikipedia →
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"#### ⚠️ Topic Unverified: *{result.get('query')}*")
                            st.markdown(f"""
                            <div class="premium-card" style="border-left: 4px solid #fbbf24;">
                                <p style="color:#e2e8f0;">
                                    {result.get('summary')}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("Fact verification summary, definition, and reference links will show here.")

# --- TAB 3: STRATEGY & HISTORY ---
with tab3:
    st.markdown("### 📊 Performance & Strategy History")
    st.markdown("Analyze your generated networking strategies, useful ratios, and historical feedback log.")
    
    # Retrieve history from backend
    history_list = []
    if backend_online:
        history_list = call_api("GET", "/history")
    
    if not history_list:
        st.info("No active history available. Once you run generations through the backend API, history and performance feedback will load here.")
    else:
        # Calculate stats
        total_batches = len(history_list)
        total_starters = total_batches * 3
        thumbs_up = 0
        thumbs_down = 0
        
        for item in history_list:
            feedbacks = item.get("starters_feedback", {})
            for sf_id, sf_val in feedbacks.items():
                if sf_val.get("rating") == "up":
                    thumbs_up += 1
                elif sf_val.get("rating") == "down":
                    thumbs_down += 1
                    
        total_rated = thumbs_up + thumbs_down
        success_ratio = int((thumbs_up / total_rated) * 100) if total_rated > 0 else 0
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.markdown(f"""
            <div class="premium-card" style="text-align:center;">
                <p style="font-size:0.9rem; color:#94a3b8; margin-bottom:4px;">Total Strategy Batches</p>
                <h2 style="margin:0; font-size:2rem; color:#818cf8;">{total_batches}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with stat_col2:
            st.markdown(f"""
            <div class="premium-card" style="text-align:center;">
                <p style="font-size:0.9rem; color:#94a3b8; margin-bottom:4px;">Useful Starters (👍)</p>
                <h2 style="margin:0; font-size:2rem; color:#4ade80;">{thumbs_up}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with stat_col3:
            st.markdown(f"""
            <div class="premium-card" style="text-align:center;">
                <p style="font-size:0.9rem; color:#94a3b8; margin-bottom:4px;">Not Useful (👎)</p>
                <h2 style="margin:0; font-size:2rem; color:#f87171;">{thumbs_down}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with stat_col4:
            st.markdown(f"""
            <div class="premium-card" style="text-align:center;">
                <p style="font-size:0.9rem; color:#94a3b8; margin-bottom:4px;">Engagement Ratio</p>
                <h2 style="margin:0; font-size:2rem; color:#c084fc;">{success_ratio}%</h2>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 📜 Historical Logs")
        
        for index, item in enumerate(history_list):
            item_id = item["id"]
            timestamp = item["timestamp"][:16].replace("T", " ")
            themes_str = ", ".join(item["themes"])
            
            with st.expander(f"📅 Session: {timestamp} | Event: {item['event_description'][:40]}..."):
                st.markdown(f"**Extracted Themes:** {themes_str}")
                st.markdown(f"**Interests:** {', '.join(item['interests'])}")
                if item.get("goals"):
                    st.markdown(f"**Networking Goal:** {item['goals']}")
                    
                st.markdown("---")
                st.markdown("**Conversation Starters & Recorded Feedback:**")
                
                feedbacks = item.get("starters_feedback", {})
                for idx, starter in enumerate(item["starters"]):
                    starter_id = f"{item_id}_{idx}"
                    fb = feedbacks.get(starter_id, {})
                    rating = fb.get("rating")
                    
                    rating_symbol = "⚪ Unrated"
                    if rating == "up":
                        rating_symbol = "👍 Useful"
                    elif rating == "down":
                        rating_symbol = "👎 Not Useful"
                        
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding:12px; border-radius:8px; margin-bottom:8px;">
                        <p style="margin:0; color:#cbd5e1; font-style:italic;">"{starter}"</p>
                        <p style="margin:4px 0 0 0; font-size:0.8rem; color:#94a3b8; font-weight:600;">Status: {rating_symbol}</p>
                    </div>
                    """, unsafe_allow_html=True)
