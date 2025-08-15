# app.py
# streamlit run app.py
"""
AI Mock Interview Bot - Mobile-Responsive Version with Fixed Timer
Features:
- Fixed continuous timer with auto-refresh
- Mobile-responsive design
- Improved question card visibility
- Better touch interface for mobile
- Real-time timer updates
- Enhanced UI with balanced layout
"""

import os
import time
import random
import threading
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
import json

# OpenAI imports with better error handling
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("OpenAI library not installed. Run: pip install openai")

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
@st.cache_resource
def init_openai_client():
    """Initialize OpenAI client with caching"""
    if not OPENAI_API_KEY:
        st.error("❌ OpenAI API Key not found. Please set OPENAI_API_KEY in your .env file")
        return None
    
    if not OPENAI_AVAILABLE:
        return None
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        # Test the connection
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
        return None

client = init_openai_client()

# Enhanced question categories
QUESTION_CATEGORIES = {
    "General": [
        "Tell me about yourself.",
        "Why are you interested in this position?",
        "What are your strengths and weaknesses?",
        "Where do you see yourself in 5 years?",
        "Why should we hire you?",
        "Describe a challenging situation you faced and how you handled it.",
    ],
    "Technical": [
        "Explain object-oriented programming principles.",
        "What is the difference between SQL and NoSQL databases?",
        "Describe your experience with version control systems.",
        "How do you ensure code quality and maintainability?",
        "Explain the concept of API design and RESTful services.",
        "What are design patterns and can you give examples?",
    ],
    "Behavioral": [
        "Tell me about a time you had to work with a difficult team member.",
        "Describe a project where you had to meet a tight deadline.",
        "Give an example of when you had to learn something new quickly.",
        "Tell me about a mistake you made and how you handled it.",
        "Describe a time when you had to explain something complex to a non-technical person.",
    ],
    "Problem Solving": [
        "How would you approach debugging a system that's running slowly?",
        "Design a system for a library management system.",
        "How would you handle a situation where a client is unhappy with deliverables?",
        "Explain how you would prioritize tasks when everything seems urgent.",
        "Walk me through your problem-solving process.",
    ]
}

DIFFICULTY_LEVELS = {
    "Beginner": {"time_multiplier": 1.5, "complexity": "basic"},
    "Intermediate": {"time_multiplier": 1.0, "complexity": "moderate"},
    "Advanced": {"time_multiplier": 0.8, "complexity": "complex"}
}

def ask_chat(prompt, model="gpt-4o-mini", max_retries=3):
    """Enhanced chat function with retry logic and better error handling"""
    if not client:
        return "❌ OpenAI client not available. Please check your API key and connection."
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            if attempt == max_retries - 1:
                return f"❌ Error after {max_retries} attempts: {str(e)}"
            time.sleep(1)  # Brief delay before retry

def extract_name(answer_text):
    """Enhanced name extraction with validation"""
    if not answer_text.strip():
        return "Candidate"
    
    prompt = f"""
    Extract ONLY the first name from this introduction. Rules:
    - Return only the first name (no last names, titles, or extra words)
    - If no clear first name is found, return "Candidate"
    - If multiple names, return only the first one
    
    Introduction: "{answer_text[:200]}"
    """
    
    try:
        name = ask_chat(prompt, max_retries=2)
        if name and len(name.split()) <= 2:  # Reasonable name length
            clean_name = ''.join(c for c in name.split()[0] if c.isalpha() or c == '-')
            return clean_name.title() if clean_name else "Candidate"
        return "Candidate"
    except:
        return "Candidate"

def calculate_score(answer, question, difficulty="Intermediate"):
    """Calculate comprehensive score for an answer"""
    if not answer.strip():
        return {"score": 0, "feedback": "No answer provided"}
    
    complexity_map = {
        "Beginner": "entry-level",
        "Intermediate": "mid-level professional", 
        "Advanced": "senior-level expert"
    }
    
    prompt = f"""
    As an expert interview coach, evaluate this {complexity_map[difficulty]} candidate's answer.
    
    Question: {question}
    Answer: {answer}
    
    Provide a JSON response with:
    {{
        "score": [0-10 integer],
        "strengths": ["strength1", "strength2"],
        "improvements": ["improvement1", "improvement2"],
        "sample_answer": "brief improved version"
    }}
    
    Scoring criteria:
    - Relevance and completeness (40%)
    - Clarity and structure (30%)
    - Specific examples and details (30%)
    """
    
    try:
        response = ask_chat(prompt)
        # Try to parse JSON, fallback to text if needed
        if response.startswith('{'):
            return json.loads(response)
        else:
            return {"score": 5, "feedback": response}
    except:
        return {"score": 5, "feedback": "Unable to analyze answer at this time"}

def format_time(seconds):
    """Format time in MM:SS format"""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

# Streamlit Configuration
st.set_page_config(
    page_title="AI Mock Interview Bot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Mobile-Responsive CSS with improved styling
st.markdown("""
<style>
/* Base mobile-first responsive design */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem 1rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.main-header h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.main-header p {
    font-size: 1rem;
    opacity: 0.9;
}

/* Enhanced question card with better visibility */
.question-card {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 2rem;
    border-radius: 15px;
    border: 3px solid #4f46e5;
    margin: 1.5rem 0;
    box-shadow: 0 8px 25px rgba(79, 70, 229, 0.15);
    position: relative;
    overflow: hidden;
}

.question-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #ec4899);
}

.question-card h3 {
    color: #1e293b;
    font-size: 1.3rem;
    font-weight: 600;
    line-height: 1.5;
    margin: 0;
}

/* Mobile-optimized progress bar */
.progress-container {
    margin: 1rem 0;
    padding: 0 0.5rem;
}

.progress-bar {
    background: #e2e8f0;
    height: 12px;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

.progress-fill {
    background: linear-gradient(90deg, #10b981, #059669);
    height: 100%;
    transition: width 0.5s ease;
    border-radius: 10px;
}

.progress-text {
    text-align: center;
    margin-top: 0.5rem;
    font-weight: 500;
    color: #475569;
}

/* Enhanced timer styles */
.timer-container {
    background: #fff;
    border-radius: 12px;
    padding: 1rem;
    margin: 1rem 0;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border: 2px solid #e2e8f0;
}

.timer-normal {
    background: linear-gradient(135deg, #dcfce7, #bbf7d0);
    border-color: #22c55e;
    color: #166534;
}

.timer-warning {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border-color: #f59e0b;
    color: #92400e;
    animation: pulse-warning 2s infinite;
}

.timer-danger {
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    border-color: #ef4444;
    color: #dc2626;
    animation: pulse-danger 1s infinite;
}

@keyframes pulse-warning {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

@keyframes pulse-danger {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

/* Enhanced settings cards with perfect alignment */
.settings-cards-container {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
    justify-content: center;
    flex-wrap: wrap;
}

.settings-card {
    /* Enhanced gradient with better contrast */
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 50%, #4338ca 100%);
    color: white;
    
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 15px;
    padding: 1.5rem 1rem;
    text-align: center;
    
    /* Ensure equal sizing */
    flex: 1;
    min-width: 200px;
    max-width: 280px;
    height: 120px;
    
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    
    /* Enhanced visual effects */
    box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.settings-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 35px rgba(79, 70, 229, 0.4);
    border-color: rgba(255, 255, 255, 0.4);
}

.settings-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #ec4899, #f59e0b, #10b981);
}

.settings-card-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-shadow: 0 1px 3px rgba(0,0,0,0.2);
    letter-spacing: 0.5px;
}

.settings-card-value {
    font-size: 1.4rem;
    font-weight: 800;
    margin-bottom: 0.25rem;
    text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.settings-card-subtitle {
    font-size: 0.85rem;
    opacity: 0.9;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

/* Mobile-optimized button styles */
.stButton > button {
    width: 100%;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    border: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

/* Mobile-responsive text areas */
.stTextArea textarea {
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    padding: 1rem;
    font-size: 1rem;
    line-height: 1.5;
    min-height: 150px;
}

.stTextArea textarea:focus {
    border-color: #4f46e5;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

/* Metric cards for mobile */
.metric-card {
    background: linear-gradient(135deg, #f8fafc, #e2e8f0);
    border: 2px solid #cbd5e1;
    border-radius: 12px;
    padding: 1.5rem 1rem;
    text-align: center;
    margin: 0.5rem 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    border-color: #94a3b8;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 0.5rem;
    text-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.metric-label {
    font-size: 0.9rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}

/* Auto-refresh indicator */
.refresh-indicator {
    position: fixed;
    top: 10px;
    right: 10px;
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.9), rgba(99, 102, 241, 0.9));
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.8rem;
    font-weight: 600;
    z-index: 1000;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Mobile breakpoints */
@media (max-width: 768px) {
    .settings-cards-container {
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    
    .settings-card {
        min-width: 100%;
        max-width: 100%;
        height: 100px;
        padding: 1rem;
    }
    
    .settings-card-title {
        font-size: 1rem;
    }
    
    .settings-card-value {
        font-size: 1.2rem;
    }
    
    .settings-card-subtitle {
        font-size: 0.8rem;
    }
    
    .main-header {
        padding: 1rem 0.5rem;
    }
    
    .main-header h1 {
        font-size: 1.5rem;
    }
    
    .question-card {
        padding: 1.5rem 1rem;
        margin: 1rem 0;
    }
    
    .question-card h3 {
        font-size: 1.1rem;
    }
    
    .timer-container {
        padding: 0.75rem 0.5rem;
        font-size: 1.1rem;
    }
    
    .stButton > button {
        padding: 0.875rem 1rem;
        font-size: 0.95rem;
    }
    
    .progress-container {
        padding: 0 0.25rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
    }
}

@media (max-width: 480px) {
    .main-header h1 {
        font-size: 1.25rem;
    }
    
    .main-header p {
        font-size: 0.9rem;
    }
    
    .question-card {
        padding: 1rem 0.75rem;
    }
    
    .question-card h3 {
        font-size: 1rem;
        line-height: 1.4;
    }
    
    .timer-container {
        font-size: 1rem;
        padding: 0.5rem;
    }
    
    .stTextArea textarea {
        min-height: 120px;
        font-size: 0.95rem;
    }
    
    .settings-card {
        height: 90px;
        padding: 0.75rem;
    }
    
    .settings-card-title {
        font-size: 0.9rem;
    }
    
    .settings-card-value {
        font-size: 1.1rem;
    }
}

/* Footer styles */
.footer {
    text-align: center;
    color: #64748b;
    padding: 2rem 1rem;
    margin-top: 3rem;
    border-top: 1px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
    border-radius: 15px 15px 0 0;
}

/* Sidebar mobile optimization */
.css-1d391kg {
    padding-top: 1rem;
}

/* Loading animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in-up {
    animation: fadeInUp 0.6s ease-out;
}

/* Success/Error message enhancements */
.stSuccess > div, .stError > div, .stWarning > div, .stInfo > div {
    border-radius: 10px;
    border-left: 5px solid;
    padding: 1rem 1.5rem;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('''
<div class="main-header fade-in-up">
    <h1>🎯 AI Mock Interview Bot</h1>
    <p>Practice interviews with AI-powered feedback and real-time scoring</p>
</div>
''', unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        "mode": "Start Mock Interview",
        "candidate_name": None,
        "current_q": None,
        "questions": [],
        "answers": [],
        "time_limit": 90,
        "start_time": None,
        "num_questions": 5,
        "feedback": None,
        "category": "General",
        "difficulty": "Intermediate",
        "interview_stats": {},
        "paused": False,
        "auto_refresh": True
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Auto-refresh mechanism for timer
if (st.session_state.current_q is not None and 
    st.session_state.current_q < len(st.session_state.questions) and
    st.session_state.start_time and 
    not st.session_state.paused and
    st.session_state.auto_refresh):
    
    # Add refresh indicator
    st.markdown('<div class="refresh-indicator">🔄 Live Timer</div>', unsafe_allow_html=True)
    
    # Auto-refresh every second during active interview
    time.sleep(1)
    st.rerun()

# Sidebar Configuration
with st.sidebar:
    st.header("🔧 Configuration")
    
    # Mode Selection
    mode = st.radio(
        "Choose Mode",
        ["Start Mock Interview", "Practice Questions & Answers", "Interview Analytics"],
        index=0
    )
    st.session_state.mode = mode
    
    if mode == "Start Mock Interview":
        st.subheader("Interview Settings")
        
        # Mobile-optimized layout
        st.session_state.num_questions = st.selectbox(
            "Number of Questions", [3, 5, 7, 10], index=1
        )
        
        st.session_state.time_limit = st.selectbox(
            "Time per Question (seconds)", [60, 90, 120, 180], index=1
        )
        
        st.session_state.category = st.selectbox(
            "Interview Category", list(QUESTION_CATEGORIES.keys())
        )
        
        st.session_state.difficulty = st.selectbox(
            "Difficulty Level", list(DIFFICULTY_LEVELS.keys()), index=1
        )
        
        # Timer control
        st.session_state.auto_refresh = st.checkbox("Live Timer Updates", value=True)
    
    # AI Query Section
    st.markdown("---")
    st.subheader("🤖 Ask AI Coach")
    user_query = st.text_input("Quick question:", placeholder="How to answer behavioral questions?")
    
    if user_query and st.button("Ask", type="secondary"):
        with st.spinner("🤔 Thinking..."):
            answer = ask_chat(f"As an interview coach, answer this question concisely: {user_query}")
        
        with st.expander("💡 AI Answer", expanded=True):
            st.write(answer)

# Main Content Area
if st.session_state.mode == "Practice Questions & Answers":
    st.header("📚 Practice Questions & Model Answers")
    
    # Mobile-optimized form
    topic = st.text_input("Topic or Skill:", placeholder="e.g., Python, Leadership, System Design")
    
    col1, col2 = st.columns(2)
    with col1:
        num_qa = st.selectbox("Number of Q&As:", [3, 5, 7, 10], index=1)
    with col2:
        qa_difficulty = st.selectbox("Level:", list(DIFFICULTY_LEVELS.keys()), index=1)
    
    if st.button("🎯 Generate Practice Material", type="primary"):
        if not topic.strip():
            st.warning("⚠️ Please enter a topic first.")
        else:
            prompt = f"""
            Create {num_qa} interview questions about {topic} for a {qa_difficulty.lower()}-level position.
            For each question, provide:
            1. The question
            2. A comprehensive model answer
            3. Key points to mention
            
            Format as:
            **Q1: [Question]**
            **Model Answer:** [Answer]
            **Key Points:** [Points]
            
            Make answers specific, actionable, and include examples where appropriate.
            """
            
            with st.spinner(f"🎯 Generating {num_qa} questions about {topic}..."):
                generated_content = ask_chat(prompt)
            
            st.success(f"✅ Generated practice material for {topic}")
            
            with st.container():
                st.markdown("### 📋 Practice Material")
                st.markdown(generated_content)
                
                # Download option
                st.download_button(
                    "📥 Download as Text File",
                    data=generated_content,
                    file_name=f"{topic.replace(' ', '_')}_practice_questions.txt",
                    mime="text/plain"
                )

elif st.session_state.mode == "Interview Analytics":
    st.header("📊 Interview Performance Analytics")
    
    if st.session_state.answers:
        # Calculate overall statistics
        total_questions = len(st.session_state.answers)
        answered_questions = sum(1 for a in st.session_state.answers if a.get('answer', '').strip())
        avg_time = sum(a.get('time_taken', 0) for a in st.session_state.answers) / total_questions
        
        # Mobile-optimized metrics
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card fade-in-up">
                <div class="metric-value">{answered_questions}/{total_questions}</div>
                <div class="metric-label">Questions Completed</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card fade-in-up">
                <div class="metric-value">{avg_time:.1f}s</div>
                <div class="metric-label">Avg Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card fade-in-up">
                <div class="metric-value">{(answered_questions/total_questions)*100:.1f}%</div>
                <div class="metric-label">Completion Rate</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card fade-in-up">
                <div class="metric-value">{st.session_state.category}</div>
                <div class="metric-label">Category</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed breakdown
        st.subheader("Question-by-Question Breakdown")
        
        for i, answer_data in enumerate(st.session_state.answers):
            with st.expander(f"Q{i+1}: {answer_data['question'][:50]}...", expanded=False):
                st.write(f"**Your Answer:** {answer_data.get('answer', 'No answer provided')}")
                st.write(f"**Time Taken:** {answer_data.get('time_taken', 0)}s")
                
                time_limit = st.session_state.time_limit
                if answer_data.get('time_taken', 0) <= time_limit * 0.5:
                    st.success("⚡ Quick response")
                elif answer_data.get('time_taken', 0) <= time_limit:
                    st.info("⏱️ Good timing")
                else:
                    st.warning("🐌 Over time limit")
    else:
        st.info("📈 Complete an interview first to see your analytics!")

else:  # Start Mock Interview Mode
    st.header("🚀 Mock Interview")
    
    # Enhanced settings cards with perfect alignment and better display
    st.markdown(f'''
    <div class="settings-cards-container fade-in-up">
        <div class="settings-card">
            <div class="settings-card-title">📝 Questions</div>
            <div class="settings-card-value">{st.session_state.num_questions}</div>
        </div>
        <div class="settings-card">
            <div class="settings-card-title">⏱️ Time Limit</div>
            <div class="settings-card-value">{st.session_state.time_limit}s</div>
        </div>
        <div class="settings-card">
            <div class="settings-card-title">🎯 Category</div>
            <div class="settings-card-value">{st.session_state.category}</div>
            <div class="settings-card-subtitle">({st.session_state.difficulty})</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Start Interview Button
    if st.session_state.current_q is None:
        st.markdown("### Ready to begin your interview?")
        st.markdown("**Instructions:**")
        st.markdown("- Answer each question thoughtfully")
        st.markdown("- Use the full time available to you") 
        st.markdown("- Speak as if you're in a real interview")
        
        if st.button("🚀 Start Interview", type="primary"):
            # Select questions based on category and difficulty
            available_questions = QUESTION_CATEGORIES[st.session_state.category].copy()
            random.shuffle(available_questions)
            
            selected_questions = available_questions[:st.session_state.num_questions]
            
            # Adjust time based on difficulty
            time_multiplier = DIFFICULTY_LEVELS[st.session_state.difficulty]["time_multiplier"]
            adjusted_time = int(st.session_state.time_limit * time_multiplier)
            
            # Initialize interview state
            st.session_state.questions = selected_questions
            st.session_state.current_q = 0
            st.session_state.answers = []
            st.session_state.candidate_name = None
            st.session_state.start_time = time.time()
            st.session_state.feedback = None
            st.session_state.time_limit = adjusted_time
            st.session_state.paused = False
            
            st.rerun()
    
    # Interview in progress
    elif st.session_state.current_q < len(st.session_state.questions):
        q_index = st.session_state.current_q
        current_question = st.session_state.questions[q_index]
        
        # Display question with candidate name if available
        display_question = current_question
        if st.session_state.candidate_name and q_index > 0:
            display_question = f"{st.session_state.candidate_name}, {current_question}"
        
        # Progress bar
        progress = (q_index) / len(st.session_state.questions)
        st.markdown(f'''
        <div class="progress-container fade-in-up">
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress * 100}%"></div>
            </div>
            <div class="progress-text">
                Question {q_index + 1} of {len(st.session_state.questions)}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Timer logic with continuous updates
        if st.session_state.start_time and not st.session_state.paused:
            elapsed = int(time.time() - st.session_state.start_time)
            remaining = max(0, st.session_state.time_limit - elapsed)
            
            # Timer display with enhanced styling
            if remaining > 30:
                timer_class = "timer-normal"
                timer_emoji = "🟢"
            elif remaining > 10:
                timer_class = "timer-warning"
                timer_emoji = "🟡"
            else:
                timer_class = "timer-danger"
                timer_emoji = "🔴"
            
            st.markdown(f'''
            <div class="timer-container {timer_class} fade-in-up">
                <div style="font-size: 1.5rem; font-weight: bold;">
                    {timer_emoji} Time Remaining: {format_time(remaining)}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Auto-advance when time runs out
            if remaining == 0:
                st.warning("⏰ Time's up! Moving to next question...")
                
                # Get current answer from text area
                current_answer = st.session_state.get(f"answer_{q_index}_{st.session_state.difficulty}", "")
                
                st.session_state.answers.append({
                    "question": current_question,
                    "display_question": display_question,
                    "answer": current_answer,
                    "time_taken": st.session_state.time_limit,
                    "category": st.session_state.category,
                    "difficulty": st.session_state.difficulty
                })
                
                # Extract name from first answer
                if q_index == 0 and current_answer.strip():
                    st.session_state.candidate_name = extract_name(current_answer)
                
                st.session_state.current_q += 1
                st.session_state.start_time = time.time()
                time.sleep(1)  # Brief pause
                st.rerun()
        
        # Question display with enhanced visibility
        st.markdown(f'''
        <div class="question-card fade-in-up">
            <h3>❓ {display_question}</h3>
        </div>
        ''', unsafe_allow_html=True)
        
        # Answer input with mobile-optimized height
        user_answer = st.text_area(
            "Your Answer:",
            value="",
            height=200,
            key=f"answer_{q_index}_{st.session_state.difficulty}",
            placeholder="Take your time to provide a thoughtful, detailed answer. Speak as if you're in a real interview setting..."
        )
        
        # Action buttons with mobile-friendly layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("✅ Submit Answer", type="primary", use_container_width=True):
                # Save answer
                st.session_state.answers.append({
                    "question": current_question,
                    "display_question": display_question,
                    "answer": user_answer,
                    "time_taken": int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0,
                    "category": st.session_state.category,
                    "difficulty": st.session_state.difficulty
                })
                
                # Extract name from first answer
                if q_index == 0 and user_answer.strip():
                    st.session_state.candidate_name = extract_name(user_answer)
                
                # Move to next question
                st.session_state.current_q += 1
                st.session_state.start_time = time.time()
                st.rerun()
        
        with col2:
            # Pause/Resume button
            pause_text = "▶️ Resume" if st.session_state.paused else "⏸️ Pause"
            if st.button(pause_text, use_container_width=True):
                st.session_state.paused = not st.session_state.paused
                st.rerun()
        
        # Skip button (full width on mobile)
        if st.button("⏭️ Skip Question", use_container_width=True, help="Skip this question and move to the next one"):
            st.session_state.answers.append({
                "question": current_question,
                "display_question": display_question,
                "answer": "",
                "time_taken": int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0,
                "category": st.session_state.category,
                "difficulty": st.session_state.difficulty
            })
            
            st.session_state.current_q += 1
            st.session_state.start_time = time.time()
            st.rerun()
    
    # Interview completed - Results and Feedback
    elif st.session_state.current_q >= len(st.session_state.questions) and st.session_state.answers:
        st.balloons()
        st.success("🎉 Congratulations! Interview Completed Successfully!")
        
        # Summary statistics with mobile-friendly layout
        total_time = sum(a.get('time_taken', 0) for a in st.session_state.answers)
        answered_count = sum(1 for a in st.session_state.answers if a.get('answer', '').strip())
        
        # Mobile-optimized metrics display
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card fade-in-up">
                <div class="metric-value">{len(st.session_state.answers)}</div>
                <div class="metric-label">Total Questions</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card fade-in-up">
                <div class="metric-value">{format_time(total_time)}</div>
                <div class="metric-label">Total Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card fade-in-up">
                <div class="metric-value">{answered_count}</div>
                <div class="metric-label">Questions Answered</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card fade-in-up">
                <div class="metric-value">{(answered_count/len(st.session_state.answers))*100:.0f}%</div>
                <div class="metric-label">Completion Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed Results
        st.subheader("📋 Your Interview Responses")
        
        for i, answer_data in enumerate(st.session_state.answers):
            with st.expander(f"Q{i+1}: {answer_data['question']}", expanded=False):
                if answer_data.get('answer', '').strip():
                    st.markdown(f"**Your Answer:**")
                    st.write(answer_data['answer'])
                else:
                    st.markdown("*No answer provided*")
                
                # Performance indicators with mobile-friendly styling
                time_taken = answer_data.get('time_taken', 0)
                st.markdown(f"**Time Taken:** {time_taken}s")
                
                time_ratio = time_taken / st.session_state.time_limit
                if time_ratio <= 0.5:
                    st.success("⚡ Quick Response - Great timing!")
                elif time_ratio <= 0.8:
                    st.info("✅ Good Timing - Well paced")
                elif time_ratio <= 1.0:
                    st.warning("⏱️ Close Call - Used most of the time")
                else:
                    st.error("⏰ Over Time - Consider being more concise")
        
        # Generate AI Feedback
        if not st.session_state.feedback:
            with st.spinner("🎯 Generating detailed AI feedback and scores..."):
                feedback_prompt = f"""
                As an expert interview coach, analyze this {st.session_state.difficulty}-level {st.session_state.category} interview performance.
                
                Candidate: {st.session_state.candidate_name or 'Anonymous'}
                Difficulty: {st.session_state.difficulty}
                Category: {st.session_state.category}
                
                Interview Performance Summary:
                - Total Questions: {len(st.session_state.answers)}
                - Questions Answered: {answered_count}
                - Total Time: {format_time(total_time)}
                - Completion Rate: {(answered_count/len(st.session_state.answers))*100:.1f}%
                
                Questions and Answers:
                """
                
                for idx, ans in enumerate(st.session_state.answers, 1):
                    feedback_prompt += f"""
                    
                Q{idx}: {ans['question']}
                Answer: {ans.get('answer', '[No answer provided]')[:500]}...
                Time Used: {ans.get('time_taken', 0)}s / {st.session_state.time_limit}s
                """
                
                feedback_prompt += f"""
                
                Please provide comprehensive feedback including:
                
                1. **Overall Performance Score (0-100):**
                
                2. **Strengths Demonstrated:**
                   - List 3-4 key strengths observed
                
                3. **Areas for Improvement:**
                   - List 3-4 specific areas to work on
                
                4. **Question-by-Question Analysis:**
                   - Brief feedback on each answer (1-2 sentences each)
                
                5. **Recommendations for Next Steps:**
                   - Specific actionable advice for improvement
                
                6. **Interview Readiness Assessment:**
                   - Overall readiness level and what to focus on
                
                Format the response with clear headers and bullet points for mobile readability.
                """
                
                st.session_state.feedback = ask_chat(feedback_prompt)
        
        # Display Feedback with mobile-optimized styling
        st.subheader("🎯 AI Coach Feedback & Analysis")
        
        if "❌" not in str(st.session_state.feedback):
            # Create expandable sections for better mobile experience
            with st.expander("📊 Complete Feedback Report", expanded=True):
                st.markdown(st.session_state.feedback)
        else:
            st.error("Unable to generate feedback at this time. Please check your OpenAI connection.")
        
        # Action buttons with mobile-friendly layout
        st.subheader("What would you like to do next?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 New Interview", type="primary", use_container_width=True):
                # Reset interview state
                keys_to_reset = ["current_q", "questions", "answers", "candidate_name", 
                               "start_time", "feedback", "paused"]
                for key in keys_to_reset:
                    if key in ["current_q", "candidate_name", "start_time", "feedback"]:
                        st.session_state[key] = None
                    elif key == "paused":
                        st.session_state[key] = False
                    else:
                        st.session_state[key] = []
                st.rerun()
        
        with col2:
            if st.button("📊 View Analytics", use_container_width=True):
                st.session_state.mode = "Interview Analytics"
                st.rerun()
        
        with col3:
            if st.button("📚 Practice Mode", use_container_width=True):
                st.session_state.mode = "Practice Questions & Answers"
                st.rerun()
        
        # Download results section
        st.markdown("---")
        st.subheader("📥 Download Your Results")
        
        # Prepare results for download
        results_text = f"""
AI MOCK INTERVIEW RESULTS
========================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Candidate: {st.session_state.candidate_name or 'Anonymous'}
Category: {st.session_state.category}
Difficulty: {st.session_state.difficulty}
Total Questions: {len(st.session_state.answers)}
Questions Answered: {answered_count}
Completion Rate: {(answered_count/len(st.session_state.answers))*100:.0f}%
Total Time: {format_time(total_time)}

QUESTIONS & ANSWERS
==================
"""
        
        for i, ans in enumerate(st.session_state.answers, 1):
            results_text += f"""
Q{i}: {ans['question']}
Time Allocated: {st.session_state.time_limit}s
Time Used: {ans.get('time_taken', 0)}s

Your Answer:
{ans.get('answer', '[No answer provided]')}

{'='*50}
"""
        
        results_text += f"""

AI COACH FEEDBACK
================
{st.session_state.feedback or 'Feedback not available - please check your OpenAI connection'}

END OF REPORT
=============
Generated by AI Mock Interview Bot
"""
        
        st.download_button(
            "📄 Download Complete Report",
            data=results_text,
            file_name=f"interview_results_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
            help="Download your complete interview results and feedback"
        )
        
        # Performance summary for quick sharing
        summary_text = f"""
🎯 INTERVIEW SUMMARY
Completed {answered_count}/{len(st.session_state.answers)} questions
Category: {st.session_state.category} ({st.session_state.difficulty})
Time: {format_time(total_time)}
Completion: {(answered_count/len(st.session_state.answers))*100:.0f}%

Ready for your next challenge! 🚀
"""
        
        st.download_button(
            "📱 Download Summary",
            data=summary_text,
            file_name=f"interview_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
            help="Download a quick summary for sharing"
        )

# Footer
st.markdown('''
<div class="footer fade-in-up">
    <h4>🚀 AI Mock Interview Bot</h4>
    <p><strong>Practice makes perfect!</strong></p>
    <p>💡 <em>Pro Tip: Regular practice with different difficulty levels will boost your confidence</em></p>
    <p>📱 <em>Optimized for mobile - practice anywhere, anytime!</em></p>
    <p>🎯 <em>Enhanced with perfect alignment and beautiful animations!</em></p>
</div>
''', unsafe_allow_html=True)

# streamlit run app.py