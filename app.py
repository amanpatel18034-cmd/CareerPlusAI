import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

from src.database.db_manager import DatabaseManager
from src.nlp_engine.skill_extractor import SkillExtractor, KNOWN_SKILLS
from src.analytics.market_analytics import MarketAnalytics
from src.analytics.skill_gap import SkillGapAnalyzer
from src.recommendation.job_recommender import JobRecommender

# --- Page Configuration ---
st.set_page_config(
    page_title="CareerPulse AI — Job Intelligence & Application Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---
def format_inr(val):
    if val >= 100000:
        lakhs = val / 100000
        return f"₹{lakhs:.1f} LPA"
    return f"₹{val:,.0f}"

def normalize_job_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    if raw_df is None or raw_df.empty:
        return raw_df
        
    df_norm = raw_df.copy()
    col_map = {col: str(col).lower().strip().replace(' ', '_').replace('-', '_') for col in df_norm.columns}
    df_norm.rename(columns=col_map, inplace=True)
    
    alias_map = {
        "job_title": "title", "role": "title", "job": "title", "position": "title",
        "loc": "location", "city": "location", "state": "location", "place": "location",
        "organization": "company", "employer": "company", "firm": "company",
        "sal": "avg_salary", "salary": "avg_salary", "compensation": "avg_salary", "pay": "avg_salary",
        "exp": "experience_level", "experience": "experience_level", "exp_level": "experience_level",
        "work_type": "work_model", "type": "work_model", "mode": "work_model",
        "skill_set": "skills", "skill": "skills", "technologies": "skills", "tech_stack": "skills",
        "desc": "description", "details": "description", "summary": "description"
    }
    for old_c, new_c in alias_map.items():
        if old_c in df_norm.columns and new_c not in df_norm.columns:
            df_norm.rename(columns={old_c: new_c}, inplace=True)

    defaults = {
        "job_id": [f"JOB-{i+1000}" for i in range(len(df_norm))],
        "title": "Software Engineer",
        "company": "Tech Company",
        "location": "Remote (India)",
        "work_model": "Remote",
        "experience_level": "Mid Level (2-5 yrs)",
        "min_salary": 600000,
        "max_salary": 1800000,
        "avg_salary": 1200000,
        "currency": "INR",
        "skills": "Python, SQL, Problem Solving",
        "description": "Software engineering role.",
        "posted_date": "2026-08-01"
    }
    for req_col, default_val in defaults.items():
        if req_col not in df_norm.columns:
            df_norm[req_col] = default_val

    df_norm['title'] = df_norm['title'].fillna("Software Engineer")
    df_norm['company'] = df_norm['company'].fillna("Tech Company")
    df_norm['location'] = df_norm['location'].fillna("Remote (India)")
    df_norm['experience_level'] = df_norm['experience_level'].fillna("Mid Level (2-5 yrs)")
    df_norm['work_model'] = df_norm['work_model'].fillna("Remote")
    df_norm['skills'] = df_norm['skills'].fillna("Python, SQL")
    df_norm['avg_salary'] = pd.to_numeric(df_norm['avg_salary'], errors='coerce').fillna(1200000)
    df_norm['skills_list'] = df_norm['skills'].apply(lambda x: [s.strip() for s in str(x).split(",") if s.strip()])
    return df_norm

# --- Custom Styling & CSS Design System ---
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #1E1B4B 0%, #0F172A 50%, #030712 100%);
        color: #F8FAFC;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        border-radius: 24px;
        padding: 32px 40px;
        margin-bottom: 28px;
    }

    .live-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34D399;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 5px 14px;
        border-radius: 20px;
        margin-bottom: 12px;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10B981;
    }

    /* Glassmorphic Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow: 0 12px 30px -10px rgba(0,0,0,0.5);
        backdrop-filter: blur(12px);
        transition: all 0.25s ease;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 20px 40px -15px rgba(99, 102, 241, 0.3);
    }

    .metric-title {
        font-size: 0.82rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 6px;
    }

    .metric-sub {
        font-size: 0.82rem;
        color: #38BDF8;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Badges */
    .skill-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 5px 13px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 3px;
    }
    .missing-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.15);
        color: #FCA5A5;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 5px 13px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 3px;
    }
    .location-badge {
        display: inline-block;
        background: rgba(168, 85, 247, 0.15);
        color: #C084FC;
        border: 1px solid rgba(168, 85, 247, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .status-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
    }

    /* Premium Job Card */
    .job-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 18px;
        backdrop-filter: blur(12px);
        transition: all 0.25s ease;
    }
    .job-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }

    /* Streamlit Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        color: #94A3B8;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%) !important;
        color: #FFFFFF !important;
        border-color: #6366F1 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Initialize DB Manager ---
db_manager = DatabaseManager()

# --- Data Loading Cache ---
@st.cache_data
def load_data():
    db_manager.populate_from_csv()
    raw_df = db_manager.get_all_jobs_df()
    return normalize_job_dataframe(raw_df)

df = load_data()

# --- Sidebar Controls & Custom CSV Uploader ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/lightning-bolt.png", width=64)
    st.markdown("## **CareerPulse AI**")
    st.markdown("<p style='color: #94A3B8; font-size: 0.85rem;'>Real-Time Career Intelligence & Application Portal</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("⚙️ Data Source & Filters")
    uploaded_file = st.file_uploader("Upload Custom Jobs Dataset (CSV):", type=["csv"])
    if uploaded_file is not None:
        try:
            custom_df = pd.read_csv(uploaded_file)
            df = normalize_job_dataframe(custom_df)
            st.success("Successfully loaded and normalized custom job dataset!")
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            
    st.markdown("---")
    st.write("**Filter Dashboard Context:**")
    selected_state_filter = st.selectbox("State / Location Focus:", ["All Locations"] + sorted(list(df['location'].unique())), index=0)
    min_exp_filter = st.selectbox("Experience Level:", ["All Levels"] + sorted(list(df['experience_level'].unique())), index=0)
    
    st.markdown("---")
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); font-size: 0.82rem; color: #94A3B8;">
        💡 <b>Pro Tip:</b> Apply for open roles directly in the <i>AI Job Matcher</i> tab and track status in <i>My Applications</i>.
    </div>
    """, unsafe_allow_html=True)

# Filter dataset based on sidebar
filtered_df = df.copy()
if selected_state_filter != "All Locations":
    filtered_df = filtered_df[filtered_df['location'] == selected_state_filter]
if min_exp_filter != "All Levels":
    filtered_df = filtered_df[filtered_df['experience_level'] == min_exp_filter]

analytics = MarketAnalytics(filtered_df)
extractor = SkillExtractor()
gap_analyzer = SkillGapAnalyzer(filtered_df)
recommender = JobRecommender(filtered_df)

# --- Hero Header Banner ---
st.markdown(f"""
<div class="hero-banner">
    <div class="live-pill">
        <div class="pulse-dot"></div> SYSTEM ONLINE • {len(filtered_df):,} ACTIVE LISTINGS
    </div>
    <h1 style="font-size: 2.5rem; font-weight: 800; margin: 0; background: linear-gradient(90deg, #6366F1, #3B82F6, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        CareerPulse AI Job Portal
    </h1>
    <p style="color: #94A3B8; margin-top: 8px; font-size: 1.05rem; max-width: 800px; line-height: 1.6;">
        Explore tech market analytics, evaluate resume fit, and apply directly to open engineering job roles across Indian tech hubs.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Top Key Metrics Row ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Active Market Postings</div>
        <div class="metric-value">{len(filtered_df):,}</div>
        <div class="metric-sub">▲ 18% month-on-month</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    avg_sal_inr = format_inr(filtered_df['avg_salary'].mean()) if not filtered_df.empty else "₹0 LPA"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Average Package (LPA)</div>
        <div class="metric-value">{avg_sal_inr}</div>
        <div class="metric-sub">Lakhs Per Annum</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    top_role = filtered_df['title'].mode()[0] if not filtered_df.empty else "N/A"
    count_top = len(filtered_df[filtered_df['title']==top_role]) if not filtered_df.empty else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Top Demand Role</div>
        <div class="metric-value" style="font-size: 1.35rem;">{top_role}</div>
        <div class="metric-sub">{count_top} job openings</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    apps_count = len(db_manager.get_all_applications())
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Applications</div>
        <div class="metric-value">{apps_count}</div>
        <div class="metric-sub">Submitted Candidates</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# --- Navigation Tabs ---
tab_market, tab_salary, tab_gap, tab_jobs, tab_my_apps = st.tabs([
    "📊 Market Intelligence",
    "💰 Salary Analytics",
    "🎯 Skill-Gap Analyzer",
    "💼 AI Job Matcher & Apply",
    "📑 My Applications"
])

# ==============================================================================
# TAB 1: MARKET INTELLIGENCE
# ==============================================================================
with tab_market:
    st.markdown("### 📊 Skill Demand Rankings & Tech Stack Dynamics")
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        roles_list = ["All Roles"] + sorted(list(filtered_df['title'].unique()))
        selected_role = st.selectbox("Select Target Job Role:", roles_list, key="market_role")
    with col_filter2:
        top_n_skills = st.slider("Number of top skills to display:", min_value=5, max_value=25, value=15)
        
    top_skills_df = analytics.get_top_skills(role=selected_role, top_n=top_n_skills)
    
    c1, c2 = st.columns([1.6, 1])
    with c1:
        fig_skills = px.bar(
            top_skills_df,
            x='Count',
            y='Skill',
            orientation='h',
            title=f"Top {top_n_skills} Requested Tech Skills ({selected_role})",
            color='Count',
            color_continuous_scale='Sunsetdark',
            text='Count'
        )
        fig_skills.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_skills, use_container_width=True)
        
    with c2:
        st.write("#### **Skill Co-Occurrence Analyzer**")
        selected_skill = st.selectbox("Explore tech paired with:", top_skills_df['Skill'].tolist() if not top_skills_df.empty else ["Python"])
        co_df = analytics.get_skill_co_occurrence(target_skill=selected_skill)
        
        fig_co = px.pie(
            co_df,
            values='Frequency',
            names='Co_Occurring_Skill',
            title=f"Tech Stack Frequently Paired with '{selected_skill}'",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Electric
        )
        fig_co.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_co, use_container_width=True)

# ==============================================================================
# TAB 2: SALARY & STATE ANALYTICS
# ==============================================================================
with tab_salary:
    st.markdown("### 💰 Compensation Benchmarks & State Comparisons")
    c1, c2 = st.columns(2)
    with c1:
        loc_sal_df = analytics.get_salary_by_location()
        loc_sal_df['Avg_LPA'] = (loc_sal_df['Avg_Salary'] / 100000).round(1)
        fig_sal_loc = px.bar(
            loc_sal_df,
            x='Avg_LPA',
            y='location',
            orientation='h',
            title="Average Compensation by Location / Hub (LPA ₹)",
            color='Avg_LPA',
            color_continuous_scale='Purples',
            text_auto='.1f'
        )
        fig_sal_loc.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_sal_loc, use_container_width=True)
        
    with c2:
        df_copy = filtered_df.copy()
        df_copy['avg_lpa'] = df_copy['avg_salary'] / 100000
        fig_exp = px.box(
            df_copy,
            x='experience_level',
            y='avg_lpa',
            color='experience_level',
            title="Compensation Range across Experience Tiers (LPA)",
            labels={'avg_lpa': 'Package in Lakhs (LPA)'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_exp.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig_exp, use_container_width=True)

# ==============================================================================
# TAB 3: SKILL-GAP ANALYZER
# ==============================================================================
with tab_gap:
    st.markdown("### 🎯 Resume & Skill Gap Readiness Analyzer")
    st.write("Compare candidate skills against target engineering role requirements.")
    
    st.write("**Quick Demo Presets:**")
    demo_c1, demo_c2, demo_c3 = st.columns(3)
    preset_skills = ["Python", "SQL", "Docker"]
    if demo_c1.button("📋 Load AI/ML Engineer Profile"):
        preset_skills = ["Python", "PyTorch", "SQL", "Scikit-Learn", "Docker", "FastAPI"]
    if demo_c2.button("📋 Load Data Engineer Profile"):
        preset_skills = ["Python", "SQL", "Spark", "Airflow", "Snowflake", "Docker", "PostgreSQL"]
    if demo_c3.button("📋 Load Full Stack Profile"):
        preset_skills = ["JavaScript", "TypeScript", "React", "Node.js", "Python", "SQL", "TailwindCSS"]
        
    input_method = st.radio("Input Mode:", ["Upload Resume / CV File (PDF, DOCX, TXT)", "Paste Resume / Bio Text", "Select Skill Tags"], horizontal=True)
    
    user_skills = []
    if input_method == "Upload Resume / CV File (PDF, DOCX, TXT)":
        resume_file = st.file_uploader("Upload Candidate Resume / CV Document:", type=["pdf", "docx", "doc", "txt"], help="Upload PDF, Word (DOCX/DOC), or Plain Text resume files")
        if resume_file is not None:
            resume_text = extractor.extract_text_from_file(resume_file)
            if resume_text.strip():
                word_count = len(resume_text.split())
                st.success(f"✅ Successfully parsed '{resume_file.name}' ({word_count} words extracted)")
                user_skills = extractor.extract_skills(resume_text)
                detected_exp = extractor.extract_years_experience(resume_text)
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write("**Extracted Skills:**", ", ".join([f"`{s}`" for s in user_skills]) if user_skills else "No known skills detected.")
                with col_info2:
                    if detected_exp > 0:
                        st.info(f"⏳ **Detected Experience:** {detected_exp} Years")
            else:
                st.error("Could not extract text from uploaded resume.")
        else:
            st.info("Please upload a PDF, DOCX, or TXT candidate resume file above.")
            
    elif input_method == "Select Skill Tags":
        user_skills = st.multiselect("Select candidate technical skills:", KNOWN_SKILLS, default=preset_skills)
    else:
        resume_text = st.text_area("Paste Resume Text:", height=150, value="Software engineer with 4 years experience in Python, PyTorch, SQL, Spark, Docker, and AWS SageMaker.")
        user_skills = extractor.extract_skills(resume_text)
        st.write("**Extracted Skills:**", ", ".join([f"`{s}`" for s in user_skills]) if user_skills else "No technical skills detected.")
        
    gap_c1, gap_c2 = st.columns(2)
    with gap_c1:
        target_gap_role = st.selectbox("Target Desired Role:", sorted(list(df['title'].unique())), key="gap_target_role")
        
    if st.button("Evaluate Skill Fit Score 🚀", type="primary"):
        gap_results = gap_analyzer.analyze_gap(candidate_skills=user_skills, target_role=target_gap_role)
        st.markdown("<br>", unsafe_allow_html=True)
        fit_score = gap_results["fit_score"]
        score_color = "#10B981" if fit_score >= 70 else "#F59E0B" if fit_score >= 45 else "#EF4444"
        
        g1, g2 = st.columns([1, 2])
        with g1:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.9); border: 2px solid {score_color}; border-radius: 20px; padding: 28px; text-align: center;">
                <div style="color: #94A3B8; font-weight: 600; font-size: 0.85rem;">ROLE MATCH SCORE</div>
                <div style="font-size: 4rem; font-weight: 800; font-family: 'Outfit', sans-serif; color: {score_color};">{fit_score}%</div>
                <div style="color: #F8FAFC; font-weight: 600;">Target: {target_gap_role}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with g2:
            st.write("#### **Skill Alignment Breakdown**")
            st.write("**✅ Skills You Possess:**")
            if gap_results["matching_skills"]:
                skills_html = "".join([f'<span class="skill-badge">{s["skill"]} ({s["demand_pct"]}% demand)</span>' for s in gap_results["matching_skills"]])
                st.markdown(skills_html, unsafe_allow_html=True)
            st.write("<br>**❌ Recommended Skills to Learn:**", unsafe_allow_html=True)
            if gap_results["missing_skills"]:
                missing_html = "".join([f'<span class="missing-badge">{s["skill"]} ({s["demand_pct"]}% demand)</span>' for s in gap_results["missing_skills"]])
                st.markdown(missing_html, unsafe_allow_html=True)

# ==============================================================================
# TAB 4: AI JOB MATCHER & APPLY
# ==============================================================================
with tab_jobs:
    st.markdown("### 💼 Active Engineering Roles & One-Click Application")
    st.write("Explore AI-matched job opportunities and submit candidate applications directly.")
    
    rec_c1, rec_c2, rec_c3 = st.columns(3)
    with rec_c1:
        rec_role = st.selectbox("Role Filter:", ["All Roles"] + sorted(list(df['title'].unique())), key="rec_role")
    with rec_c2:
        rec_loc = st.selectbox("State / Location Filter:", ["All Locations"] + sorted(list(df['location'].unique())), key="rec_loc")
    with rec_c3:
        rec_skills_input = st.multiselect("Candidate Skills:", KNOWN_SKILLS, default=user_skills if user_skills else ["Python", "PyTorch", "SQL", "Docker"])
        
    loc_filter = None if rec_loc == "All Locations" else rec_loc
    
    recommendations = recommender.recommend_jobs(
        user_skills=rec_skills_input,
        target_role=rec_role,
        location=loc_filter,
        top_n=10
    )
    
    st.write(f"Displaying top **{len(recommendations)}** matched job opportunities:")
    st.write("")
    
    for idx, row in recommendations.iterrows():
        match_val = row['match_score']
        badge_bg = "linear-gradient(135deg, #10B981 0%, #059669 100%)" if match_val >= 70 else "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)"
        
        min_inr = format_inr(row['min_salary'])
        max_inr = format_inr(row['max_salary'])
        job_id = str(row['job_id'])
        
        st.markdown(f"""
        <div class="job-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h3 style="margin: 0; color: #F8FAFC; font-size: 1.3rem; font-family: 'Outfit', sans-serif;">{row['title']}</h3>
                    <div style="color: #818CF8; font-weight: 600; margin-top: 4px;">
                        {row['company']} • <span class="location-badge">📍 {row['location']} ({row['work_model']})</span>
                    </div>
                </div>
                <div>
                    <span style="background: {badge_bg}; color: #FFF; padding: 6px 18px; border-radius: 20px; font-weight: 700; font-size: 0.92rem;">
                        {match_val}% Match
                    </span>
                </div>
            </div>
            <div style="margin-top: 14px; display: flex; gap: 24px; font-size: 0.9rem; color: #CBD5E1;">
                <div>💼 <b>Experience:</b> {row['experience_level']}</div>
                <div>💰 <b>Package:</b> {min_inr} - {max_inr}</div>
                <div>🆔 <b>Job ID:</b> {job_id}</div>
            </div>
            <div style="margin-top: 14px;">
                {' '.join([f'<span class="skill-badge">{s.strip()}</span>' for s in str(row["skills"]).split(",")])}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_act1, col_act2 = st.columns([1, 4])
        with col_act1:
            show_apply = st.checkbox(f"⚡ Apply Now", key=f"apply_chk_{job_id}")
            
        with col_act2:
            with st.expander(f"View Full Role Description"):
                st.write(row['description'])
                
        # --- Interactive Application Form Modal ---
        if show_apply:
            st.markdown(f"""
            <div style="background: rgba(30, 27, 75, 0.7); border: 1px solid #6366F1; border-radius: 16px; padding: 24px; margin-bottom: 20px;">
                <h4 style="color: #60A5FA; margin-top: 0;">⚡ Application Form for {row['title']} at {row['company']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form(key=f"app_form_{job_id}"):
                af_col1, af_col2 = st.columns(2)
                with af_col1:
                    app_name = st.text_input("Applicant Full Name *", value="Aman Patel")
                    app_email = st.text_input("Email Address *", value="aman.patel@example.com")
                with af_col2:
                    app_phone = st.text_input("Phone Number", value="+91 9876543210")
                    app_exp = st.selectbox("Experience Tier", ["0-2 Years", "2-5 Years", "5-8 Years", "8+ Years"], index=1)
                    
                app_skills = st.text_area("Key Skills & Technologies", value=", ".join(rec_skills_input) if rec_skills_input else "Python, SQL, PyTorch, Docker")
                app_note = st.text_area("Cover Note / Brief Pitch", value="I am an experienced engineer enthusiastic about this role. My skills align closely with your tech stack.")
                
                submit_app = st.form_submit_button("🚀 Submit Job Application", type="primary")
                
                if submit_app:
                    import re
                    is_valid = True
                    
                    # 1. Validate Full Name (Alphabets and spaces only)
                    clean_name = app_name.strip()
                    if not clean_name:
                        st.error("❌ Applicant Full Name is required.")
                        is_valid = False
                    elif not re.match(r'^[a-zA-Z\s]+$', clean_name):
                        st.error("❌ Full Name can contain only alphabetic characters and spaces (no numbers or special symbols allowed).")
                        is_valid = False

                    # 2. Validate Email Address
                    clean_email = app_email.strip()
                    if not clean_email:
                        st.error("❌ Email Address is required.")
                        is_valid = False
                    elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', clean_email):
                        st.error("❌ Please enter a valid Email Address (e.g. candidate@example.com).")
                        is_valid = False

                    # 3. Validate Phone Number (Numeric digits / integers only)
                    clean_phone_raw = app_phone.strip()
                    clean_phone_digits = clean_phone_raw.replace(" ", "").replace("-", "").replace("+", "")
                    if not clean_phone_digits:
                        st.error("❌ Phone Number is required.")
                        is_valid = False
                    elif not clean_phone_digits.isdigit():
                        st.error("❌ Phone Number can contain only numeric integer digits (no letters or special symbols allowed).")
                        is_valid = False

                    if is_valid:
                        app_res = db_manager.submit_job_application(
                            job_id=job_id,
                            job_title=row['title'],
                            company=row['company'],
                            applicant_name=clean_name,
                            applicant_email=clean_email,
                            applicant_phone=clean_phone_raw,
                            experience_years=app_exp,
                            skills=app_skills,
                            cover_note=app_note
                        )
                        if app_res:
                            st.success(f"🎉 Application Submitted Successfully! Reference ID: **{app_res['app_id']}**")
                            st.balloons()
                        else:
                            st.error("Failed to submit application. Please try again.")

# ==============================================================================
# TAB 5: MY APPLICATIONS DASHBOARD
# ==============================================================================
with tab_my_apps:
    st.markdown("### 📑 Submitted Job Applications Tracker")
    st.write("View and track all candidate job applications submitted through CareerPulse AI.")
    
    filter_email = st.text_input("Filter by Candidate Email Address:", value="", placeholder="Enter email to filter (leave blank to view all)")
    
    apps_list = db_manager.get_all_applications(applicant_email=filter_email if filter_email else None)
    
    if apps_list:
        st.write(f"Found **{len(apps_list)}** submitted applications:")
        st.write("")
        
        for app in apps_list:
            st.markdown(f"""
            <div class="job-card" style="border-left: 4px solid #10B981;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin: 0; color: #F8FAFC; font-size: 1.25rem;">{app['job_title']}</h3>
                        <div style="color: #60A5FA; font-weight: 600; margin-top: 2px;">
                            {app['company']} • <span style="color: #CBD5E1;">Applied by: <b>{app['applicant_name']}</b> ({app['applicant_email']})</span>
                        </div>
                    </div>
                    <div>
                        <span class="status-badge">✅ {app['status']}</span>
                    </div>
                </div>
                <div style="margin-top: 12px; display: flex; gap: 24px; font-size: 0.88rem; color: #94A3B8;">
                    <div>🆔 <b>App Ref:</b> <code style="color:#818CF8;">{app['app_id']}</code></div>
                    <div>📅 <b>Applied Date:</b> {app['applied_date']}</div>
                    <div>📞 <b>Phone:</b> {app['applicant_phone']}</div>
                    <div>💼 <b>Experience:</b> {app['experience_years']}</div>
                </div>
                <div style="margin-top: 10px; font-size: 0.88rem; color: #CBD5E1;">
                    <b>Technical Skills:</b> {app['skills']}
                </div>
                <div style="margin-top: 6px; font-size: 0.85rem; color: #94A3B8; italic;">
                    "{app['cover_note']}"
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No submitted job applications found. Explore open roles in the **AI Job Matcher & Apply** tab to submit an application!")
