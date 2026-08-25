import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class JobRecommender:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        # Prepare text representation for vectorization
        self.df['search_text'] = self.df['title'] + " " + self.df['skills'] + " " + self.df['description']
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['search_text'])

    def recommend_jobs(self, user_skills: list, target_role=None, location=None, top_n=10):
        query_text = " ".join(user_skills)
        if target_role and target_role != "All Roles":
            query_text = target_role + " " + query_text
            
        query_vec = self.vectorizer.transform([query_text])
        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        results_df = self.df.copy()
        results_df['match_score'] = (sim_scores * 100).round(1)
        
        if location and location != "All Locations":
            results_df = results_df[results_df['location'] == location]
            
        if target_role and target_role != "All Roles":
            # Boost score for exact role match
            results_df.loc[results_df['title'] == target_role, 'match_score'] += 10.0
            results_df['match_score'] = results_df['match_score'].clip(upper=99.9)
            
        recommendations = results_df.sort_values(by='match_score', ascending=False).head(top_n)
        return recommendations
