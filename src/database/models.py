from sqlalchemy import Column, Integer, String, Float, Text, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class JobPosting(Base):
    __tablename__ = 'job_postings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    work_model = Column(String(50), nullable=False)
    experience_level = Column(String(50), nullable=False)
    min_salary = Column(Integer, nullable=False)
    max_salary = Column(Integer, nullable=False)
    avg_salary = Column(Integer, nullable=False)
    currency = Column(String(10), default="INR")
    skills = Column(Text, nullable=False) # comma-separated
    description = Column(Text, nullable=False)
    posted_date = Column(String(20), nullable=False)

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "work_model": self.work_model,
            "experience_level": self.experience_level,
            "min_salary": self.min_salary,
            "max_salary": self.max_salary,
            "avg_salary": self.avg_salary,
            "currency": self.currency,
            "skills": [s.strip() for s in self.skills.split(",") if s.strip()],
            "description": self.description,
            "posted_date": self.posted_date
        }

class SkillTaxonomy(Base):
    __tablename__ = 'skill_taxonomy'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=False)
    demand_score = Column(Float, default=1.0)

class JobApplication(Base):
    __tablename__ = 'job_applications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(50), unique=True, nullable=False)
    job_id = Column(String(50), nullable=False)
    job_title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    applicant_name = Column(String(100), nullable=False)
    applicant_email = Column(String(100), nullable=False)
    applicant_phone = Column(String(50), nullable=True)
    experience_years = Column(String(50), nullable=True)
    skills = Column(Text, nullable=True)
    cover_note = Column(Text, nullable=True)
    applied_date = Column(String(30), nullable=False)
    status = Column(String(50), default="Applied")

    def to_dict(self):
        return {
            "app_id": self.app_id,
            "job_id": self.job_id,
            "job_title": self.job_title,
            "company": self.company,
            "applicant_name": self.applicant_name,
            "applicant_email": self.applicant_email,
            "applicant_phone": self.applicant_phone,
            "experience_years": self.experience_years,
            "skills": self.skills,
            "cover_note": self.cover_note,
            "applied_date": self.applied_date,
            "status": self.status
        }

def init_db(db_url="sqlite:///data/careerpulse.db"):
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine
