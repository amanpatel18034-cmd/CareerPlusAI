import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import random
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, JobPosting, SkillTaxonomy, JobApplication, init_db

DB_PATH = "sqlite:///data/careerpulse.db"

class DatabaseManager:
    def __init__(self, db_url=DB_PATH):
        self.engine = init_db(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def populate_from_csv(self, csv_path="data/processed/jobs.csv"):
        if not os.path.exists(csv_path):
            print(f"CSV file {csv_path} not found.")
            return False
            
        session = self.Session()
        try:
            count = session.query(JobPosting).count()
            if count > 0:
                print(f"Database already contains {count} records. Skipping population.")
                session.close()
                return True
                
            df = pd.read_csv(csv_path)
            postings = []
            all_skills = set()
            
            for _, row in df.iterrows():
                posting = JobPosting(
                    job_id=str(row["job_id"]),
                    title=str(row["title"]),
                    company=str(row["company"]),
                    location=str(row["location"]),
                    work_model=str(row["work_model"]),
                    experience_level=str(row["experience_level"]),
                    min_salary=int(row["min_salary"]),
                    max_salary=int(row["max_salary"]),
                    avg_salary=int(row["avg_salary"]),
                    currency=str(row.get("currency", "INR")),
                    skills=str(row["skills"]),
                    description=str(row["description"]),
                    posted_date=str(row["posted_date"])
                )
                postings.append(posting)
                
                skills_list = [s.strip() for s in str(row["skills"]).split(",") if s.strip()]
                all_skills.update(skills_list)
                
            session.bulk_save_objects(postings)
            taxonomies = [SkillTaxonomy(skill_name=s, category="Technical Skill") for s in all_skills]
            session.bulk_save_objects(taxonomies)
            
            session.commit()
            print(f"Successfully populated DB with {len(postings)} job listings.")
            return True
        except Exception as e:
            session.rollback()
            print(f"Error populating DB: {e}")
            return False
        finally:
            session.close()
            
    def get_all_jobs_df(self):
        session = self.Session()
        try:
            query = session.query(JobPosting)
            df = pd.read_sql(query.statement, session.bind)
            if 'skills' in df.columns and not df.empty:
                df['skills_list'] = df['skills'].apply(lambda x: [s.strip() for s in str(x).split(",") if s.strip()])
            return df
        finally:
            session.close()
            
    def get_job_by_id(self, job_id):
        session = self.Session()
        try:
            job = session.query(JobPosting).filter(JobPosting.job_id == job_id).first()
            return job.to_dict() if job else None
        finally:
            session.close()

    def submit_job_application(self, job_id, job_title, company, applicant_name, applicant_email, applicant_phone="", experience_years="", skills="", cover_note=""):
        session = self.Session()
        try:
            app_id = f"APP-{random.randint(10000, 99999)}"
            applied_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            application = JobApplication(
                app_id=app_id,
                job_id=job_id,
                job_title=job_title,
                company=company,
                applicant_name=applicant_name,
                applicant_email=applicant_email,
                applicant_phone=applicant_phone,
                experience_years=experience_years,
                skills=skills,
                cover_note=cover_note,
                applied_date=applied_date,
                status="Applied"
            )
            session.add(application)
            session.commit()
            return application.to_dict()
        except Exception as e:
            session.rollback()
            print(f"Error submitting application: {e}")
            return None
        finally:
            session.close()

    def get_all_applications(self, applicant_email=None):
        session = self.Session()
        try:
            query = session.query(JobApplication)
            if applicant_email:
                query = query.filter(JobApplication.applicant_email == applicant_email)
            apps = query.order_by(JobApplication.id.desc()).all()
            return [a.to_dict() for a in apps]
        finally:
            session.close()

if __name__ == "__main__":
    db = DatabaseManager()
    db.populate_from_csv()
