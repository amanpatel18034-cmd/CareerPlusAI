import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from src.database.db_manager import DatabaseManager
from src.nlp_engine.skill_extractor import SkillExtractor
from src.analytics.market_analytics import MarketAnalytics
from src.analytics.skill_gap import SkillGapAnalyzer
from src.recommendation.job_recommender import JobRecommender

def test_full_pipeline():
    print("--- 1. Testing Database & Data Loader ---")
    db = DatabaseManager()
    success = db.populate_from_csv()
    assert success, "Failed to populate database"
    
    df = db.get_all_jobs_df()
    assert not df.empty, "Database returned empty dataframe"
    assert len(df) >= 1000, f"Expected 1000+ jobs, got {len(df)}"
    print(f"[OK] DB Loaded successfully with {len(df)} job records.")

    print("\n--- 2. Testing NLP Skill Extractor ---")
    extractor = SkillExtractor()
    sample_text = "Senior Data Engineer needed with 4+ years of experience in Python, PyTorch, SQL, Spark, Docker, and AWS SageMaker."
    skills = extractor.extract_skills(sample_text)
    exp = extractor.extract_years_experience(sample_text)
    assert "Python" in skills, "Failed to extract Python"
    assert "Spark" in skills, "Failed to extract Spark"
    assert exp == 4.0, f"Expected 4.0 years experience, got {exp}"
    print(f"[OK] NLP Extracted skills: {skills}")
    print(f"[OK] NLP Extracted experience: {exp} years")

    print("\n--- 3. Testing Market Analytics ---")
    analytics = MarketAnalytics(df)
    top_skills = analytics.get_top_skills(top_n=5)
    sal_by_role = analytics.get_salary_by_role()
    assert not top_skills.empty, "Top skills dataframe is empty"
    assert not sal_by_role.empty, "Salary by role dataframe is empty"
    print("[OK] Market Analytics Top Skills:")
    print(top_skills)

    print("\n--- 4. Testing Skill Gap Analyzer ---")
    gap_analyzer = SkillGapAnalyzer(df)
    gap_res = gap_analyzer.analyze_gap(candidate_skills=["Python", "SQL", "Docker"], target_role="AI/ML Engineer")
    assert "fit_score" in gap_res, "Fit score missing from gap analysis"
    print(f"[OK] Skill Gap Target: {gap_res['target_role']} | Fit Score: {gap_res['fit_score']}%")
    print(f"[OK] Missing skills to learn: {[s['skill'] for s in gap_res['missing_skills'][:3]]}")

    print("\n--- 5. Testing AI Job Recommender ---")
    recommender = JobRecommender(df)
    recs = recommender.recommend_jobs(user_skills=["Python", "PyTorch", "Docker"], target_role="AI/ML Engineer", top_n=3)
    assert not recs.empty, "Job recommendations returned empty dataframe"
    assert "match_score" in recs.columns, "Match score column missing"
    print("[OK] Top Recommended Jobs:")
    for _, r in recs.iterrows():
        print(f"  - {r['title']} at {r['company']} ({r['match_score']}% match)")

    print("\n[SUCCESS] ALL PIPELINE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_pipeline()
