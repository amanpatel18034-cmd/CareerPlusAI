import pandas as pd
from collections import Counter

LEARNING_RESOURCES = {
    "PyTorch": "Fast.ai Deep Learning for Coders / PyTorch Official Tutorials",
    "TensorFlow": "DeepLearning.AI TensorFlow Developer Professional Certificate",
    "Python": "Fluent Python / 100 Days of Code: Python",
    "SQL": "Mode Analytics SQL Tutorial / Complete SQL Bootcamp",
    "Spark": "Apache Spark UI & Architecture / Databricks Learning",
    "Docker": "Docker Mastery on Udemy / Official Docker Docs",
    "Kubernetes": "Mumshad Mannambeth CKA / Kubernetes Up & Running",
    "AWS": "AWS Certified Solutions Architect Associate Course",
    "Snowflake": "Snowflake Complete Masterclass / SnowPro Core Certification",
    "Airflow": "Data Engineering with Apache Airflow (Astronomer)",
    "React": "Epic React by Kent C. Dodds / React Official Docs",
    "TypeScript": "TypeScript Handbook / Execute Program TypeScript",
    "Scikit-Learn": "Hands-On Machine Learning with Scikit-Learn & TensorFlow (Aurélien Géron)",
    "Tableau": "Tableau Desktop Specialist Certification Prep",
    "PowerBI": "Microsoft Power BI Data Analyst (PL-300)",
    "Kafka": "Apache Kafka Series by Stephane Maarek",
    "FastAPI": "FastAPI Web Development & Microservices Mastery"
}

class SkillGapAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        if 'skills' in self.df.columns and ('skills_list' not in self.df.columns or isinstance(self.df['skills'].iloc[0], str)):
            self.df['skills_list'] = self.df['skills'].apply(lambda x: [s.strip() for s in str(x).split(",") if s.strip()])
        elif 'skills_list' not in self.df.columns:
            self.df['skills_list'] = [[] for _ in range(len(self.df))]

    def analyze_gap(self, candidate_skills: list, target_role: str):
        # Filter jobs matching target role
        role_jobs = self.df[self.df['title'] == target_role]
        if role_jobs.empty:
            role_jobs = self.df
            
        # Extract all skills required for target role
        role_skill_counts = Counter()
        for skills in role_jobs['skills_list']:
            role_skill_counts.update(skills)
            
        # Top 10 required skills for role
        top_required = dict(role_skill_counts.most_common(12))
        total_postings = len(role_jobs)
        
        user_skills_set = set(s.strip().lower() for s in candidate_skills)
        
        matching_skills = []
        missing_skills = []
        
        for skill, count in top_required.items():
            importance_pct = round((count / total_postings) * 100, 1)
            if skill.lower() in user_skills_set:
                matching_skills.append({
                    "skill": skill,
                    "demand_pct": importance_pct
                })
            else:
                missing_skills.append({
                    "skill": skill,
                    "demand_pct": importance_pct,
                    "recommended_resource": LEARNING_RESOURCES.get(skill, f"Learn {skill} via official documentation and hands-on projects.")
                })
                
        # Calculate fit score
        fit_score = 0.0
        if top_required:
            matched_weight = sum(top_required[s['skill']] for s in matching_skills)
            total_weight = sum(top_required.values())
            fit_score = round((matched_weight / total_weight) * 100, 1)
            
        return {
            "target_role": target_role,
            "fit_score": fit_score,
            "matching_skills": matching_skills,
            "missing_skills": sorted(missing_skills, key=lambda x: x["demand_pct"], reverse=True),
            "total_jobs_analyzed": total_postings
        }
