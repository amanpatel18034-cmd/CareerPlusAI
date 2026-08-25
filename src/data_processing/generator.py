import random
import os
import pandas as pd
from datetime import datetime, timedelta

ROLES_SKILLS = {
    "AI/ML Engineer": {
        "core": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "SQL", "Docker"],
        "optional": ["MLflow", "CUDA", "FastAPI", "Kubernetes", "Transformers", "ONNX", "Ray", "AWS SageMaker", "LangChain"],
        "min_sal_inr": 1200000, "max_sal_inr": 3500000
    },
    "Data Engineer": {
        "core": ["Python", "SQL", "Spark", "Airflow", "Snowflake", "Docker"],
        "optional": ["Kafka", "dbt", "PostgreSQL", "AWS Redshift", "Databricks", "Kubernetes", "GCP BigQuery", "Scala", "Hive"],
        "min_sal_inr": 1000000, "max_sal_inr": 2800000
    },
    "Full Stack Developer": {
        "core": ["JavaScript", "TypeScript", "React", "Node.js", "Python", "SQL"],
        "optional": ["Next.js", "Express", "Docker", "PostgreSQL", "MongoDB", "GraphQL", "TailwindCSS", "AWS", "Redis"],
        "min_sal_inr": 800000, "max_sal_inr": 2400000
    },
    "DevOps & Cloud Engineer": {
        "core": ["Linux", "Docker", "Kubernetes", "Terraform", "AWS", "CI/CD"],
        "optional": ["Ansible", "Python", "Bash", "Prometheus", "Grafana", "Azure", "GCP", "GitLab CI", "ArgoCD"],
        "min_sal_inr": 1100000, "max_sal_inr": 3000000
    },
    "Data Analyst": {
        "core": ["SQL", "Python", "Tableau", "Excel", "PowerBI"],
        "optional": ["R", "Pandas", "Looker", "Statistics", "Google Analytics", "BigQuery", "Snowflake", "A/B Testing"],
        "min_sal_inr": 600000, "max_sal_inr": 1600000
    },
    "Cloud Architect": {
        "core": ["AWS", "Azure", "Cloud Security", "Terraform", "Kubernetes", "Python"],
        "optional": ["GCP", "Microservices", "System Design", "Docker", "Networking", "IAM", "Serverless", "Enterprise Architecture"],
        "min_sal_inr": 2000000, "max_sal_inr": 4800000
    },
    "Cybersecurity Specialist": {
        "core": ["Network Security", "Python", "Linux", "SIEM", "Penetration Testing"],
        "optional": ["Wireshark", "Firewalls", "CISSP", "Incident Response", "AWS Security", "SOC", "Cryptography", "Compliance"],
        "min_sal_inr": 900000, "max_sal_inr": 2600000
    },
    "Product Manager (Tech)": {
        "core": ["Agile", "Product Strategy", "User Research", "SQL", "Roadmapping"],
        "optional": ["Jira", "A/B Testing", "Data Analytics", "Scrum", "Figma", "Growth Hacking", "System Architecture"],
        "min_sal_inr": 1500000, "max_sal_inr": 3800000
    }
}

COMPANIES = [
    "TechNova India", "CloudScale Labs", "Nexus AI", "DataStream Corp",
    "TCS Innovation Labs", "Infosys Digital", "Wipro Cloud", "HCL Tech Solutions",
    "Apex Systems", "CyberShield Tech", "QuantVantage", "Pulse Analytics",
    "Hyperion Software", "Vanguard AI", "ByteCraft Inc", "OmniCloud Systems",
    "Zomato Tech", "Swiggy Engineering", "Flipkart Labs", "Paytm Digital"
]

INDIAN_LOCATIONS = [
    "Karnataka (Bengaluru)",
    "Maharashtra (Mumbai)",
    "Maharashtra (Pune)",
    "Telangana (Hyderabad)",
    "Tamil Nadu (Chennai)",
    "Delhi NCR (Gurugram)",
    "Delhi NCR (Noida)",
    "Gujarat (Ahmedabad / GIFT City)",
    "West Bengal (Kolkata)",
    "Kerala (Kochi)",
    "Kerala (Thiruvananthapuram)",
    "Punjab (Mohali / Chandigarh)",
    "Rajasthan (Jaipur)",
    "Madhya Pradesh (Indore)",
    "Uttar Pradesh (Lucknow)",
    "Remote (India)",
    "Remote (Global)"
]

WORK_MODELS = ["Remote", "Hybrid", "Onsite"]
EXPERIENCE_LEVELS = ["Entry Level (0-2 yrs)", "Mid Level (2-5 yrs)", "Senior Level (5-8 yrs)", "Lead / Principal (8+ yrs)"]

EXP_MULTIPLIER = {
    "Entry Level (0-2 yrs)": 0.7,
    "Mid Level (2-5 yrs)": 1.0,
    "Senior Level (5-8 yrs)": 1.4,
    "Lead / Principal (8+ yrs)": 1.85
}

DESCRIPTION_TEMPLATES = [
    "We are seeking an experienced {title} at {company} in {location}. You will work closely with engineering teams to implement high-impact systems using {primary_skills}. Expert knowledge of {all_skills} is required.",
    "Join {company} ({location}) as a {title}! In this role, you will lead the architecture, design, and execution of core digital products using {primary_skills} and {secondary_skills}.",
    "{company} is expanding its engineering hub in {location}. We are hiring a {title} with expertise in {primary_skills} and proficiency in {secondary_skills}."
]

def generate_job_postings(count=1200, output_file="data/processed/jobs.csv"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    random.seed(42)
    
    jobs = []
    base_date = datetime.now()
    
    for i in range(1, count + 1):
        role_name, role_info = random.choice(list(ROLES_SKILLS.items()))
        company = random.choice(COMPANIES)
        location = random.choice(INDIAN_LOCATIONS)
        work_model = "Remote" if "Remote" in location else random.choice(WORK_MODELS)
        exp_level = random.choices(EXPERIENCE_LEVELS, weights=[0.2, 0.4, 0.3, 0.1])[0]
        
        # Select skills
        core_s = random.sample(role_info["core"], k=min(len(role_info["core"]), random.randint(3, 5)))
        opt_s = random.sample(role_info["optional"], k=random.randint(2, 4))
        all_skills = list(set(core_s + opt_s))
        
        # Calculate salary in INR (LPA - Lakhs Per Annum & Base numeric)
        mult = EXP_MULTIPLIER[exp_level]
        min_s = int(role_info["min_sal_inr"] * mult * random.uniform(0.9, 1.1))
        max_s = int(role_info["max_sal_inr"] * mult * random.uniform(0.9, 1.1))
        if min_s >= max_s:
            max_s = min_s + 200000
            
        # Description
        template = random.choice(DESCRIPTION_TEMPLATES)
        desc = template.format(
            title=role_name,
            company=company,
            location=location,
            primary_skills=", ".join(core_s),
            secondary_skills=", ".join(opt_s),
            all_skills=", ".join(all_skills)
        )
        
        posted_days_ago = random.randint(0, 60)
        posted_date = (base_date - timedelta(days=posted_days_ago)).strftime("%Y-%m-%d")
        
        job = {
            "job_id": f"JOB-{1000 + i}",
            "title": role_name,
            "company": company,
            "location": location,
            "work_model": work_model,
            "experience_level": exp_level,
            "min_salary": min_s,
            "max_salary": max_s,
            "avg_salary": (min_s + max_s) // 2,
            "currency": "INR",
            "skills": ", ".join(all_skills),
            "description": desc,
            "posted_date": posted_date
        }
        jobs.append(job)
        
    df = pd.DataFrame(jobs)
    df.to_csv(output_file, index=False)
    print(f"Generated {count} job listings with Indian state location preferences saved to {output_file}")
    return df

if __name__ == "__main__":
    generate_job_postings()
