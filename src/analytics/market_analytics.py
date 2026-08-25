import pandas as pd
import numpy as np
from collections import Counter

class MarketAnalytics:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        # Parse skills column into lists if string
        if 'skills' in self.df.columns and isinstance(self.df['skills'].iloc[0], str):
            self.df['skills_list'] = self.df['skills'].apply(lambda x: [s.strip() for s in str(x).split(",") if s.strip()])
        elif 'skills_list' not in self.df.columns:
            self.df['skills_list'] = [[] for _ in range(len(self.df))]

    def get_top_skills(self, role=None, top_n=15):
        filtered_df = self.df
        if role and role != "All Roles":
            filtered_df = self.df[self.df['title'] == role]
            
        skill_counts = Counter()
        for skills in filtered_df['skills_list']:
            skill_counts.update(skills)
            
        top_skills = skill_counts.most_common(top_n)
        return pd.DataFrame(top_skills, columns=['Skill', 'Count'])

    def get_salary_by_role(self):
        grouped = self.df.groupby('title').agg(
            Avg_Salary=('avg_salary', 'mean'),
            Min_Salary=('min_salary', 'min'),
            Max_Salary=('max_salary', 'max'),
            Job_Count=('job_id', 'count')
        ).reset_index().sort_values(by='Avg_Salary', ascending=False)
        return grouped

    def get_salary_by_location(self):
        grouped = self.df.groupby('location').agg(
            Avg_Salary=('avg_salary', 'mean'),
            Job_Count=('job_id', 'count')
        ).reset_index().sort_values(by='Avg_Salary', ascending=False)
        return grouped

    def get_salary_by_experience(self):
        grouped = self.df.groupby('experience_level').agg(
            Avg_Salary=('avg_salary', 'mean'),
            Min_Salary=('min_salary', 'min'),
            Max_Salary=('max_salary', 'max')
        ).reset_index()
        return grouped

    def get_skill_co_occurrence(self, target_skill: str, top_n=8):
        co_counts = Counter()
        for skills in self.df['skills_list']:
            if target_skill in skills:
                for s in skills:
                    if s != target_skill:
                        co_counts[s] += 1
        return pd.DataFrame(co_counts.most_common(top_n), columns=['Co_Occurring_Skill', 'Frequency'])
