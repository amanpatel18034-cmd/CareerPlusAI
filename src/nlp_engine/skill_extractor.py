import re
import io

KNOWN_SKILLS = [
    # Programming Languages
    "Python", "JavaScript", "TypeScript", "SQL", "R", "Scala", "Java", "C++", "C#", "Go", "Rust", "Bash", "PHP",
    # AI / ML & Data Science
    "PyTorch", "TensorFlow", "Scikit-Learn", "Keras", "OpenCV", "Transformers", "LangChain", "MLflow",
    "Pandas", "NumPy", "CUDA", "ONNX", "Ray", "AWS SageMaker", "Statistics", "A/B Testing",
    # Data Engineering & Cloud Data
    "Spark", "Airflow", "Snowflake", "Databricks", "Kafka", "dbt", "PostgreSQL", "MongoDB",
    "AWS Redshift", "GCP BigQuery", "Hive", "Redis", "Cassandra",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible", "Linux", "CI/CD",
    "Prometheus", "Grafana", "GitLab CI", "ArgoCD", "Cloud Security", "IAM", "Serverless",
    # Web & Frameworks
    "React", "Next.js", "Node.js", "Express", "FastAPI", "Flask", "Django", "GraphQL", "TailwindCSS", "HTML", "CSS",
    # Analytics & Visualization
    "Tableau", "PowerBI", "Looker", "Excel", "Matplotlib", "Seaborn", "Plotly",
    # Cybersecurity & Networks
    "Network Security", "SIEM", "Penetration Testing", "Wireshark", "Firewalls", "CISSP", "Incident Response", "SOC", "Cryptography",
    # Product & Management
    "Agile", "Scrum", "Jira", "Product Strategy", "User Research", "Roadmapping", "Figma", "Growth Hacking", "System Design"
]

SKILL_MAP = {
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "aws": "AWS",
    "amazon web services": "AWS",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "power bi": "PowerBI",
    "powerbi": "PowerBI",
    "js": "JavaScript",
    "ts": "TypeScript",
    "node": "Node.js",
    "nodejs": "Node.js",
    "reactjs": "React",
    "react.js": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "fastapi": "FastAPI"
}

class SkillExtractor:
    def __init__(self):
        self.known_skills = KNOWN_SKILLS
        escaped_skills = [re.escape(s) for s in sorted(self.known_skills, key=len, reverse=True)]
        self.pattern = re.compile(r'\b(' + '|'.join(escaped_skills) + r')\b', re.IGNORECASE)

    def extract_text_from_file(self, uploaded_file) -> str:
        if uploaded_file is None:
            return ""
            
        filename = uploaded_file.name.lower()
        
        # 1. Plain Text files
        if filename.endswith(".txt"):
            try:
                return uploaded_file.read().decode("utf-8", errors="ignore")
            except Exception:
                return ""

        # 2. PDF files using pypdf
        elif filename.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(uploaded_file)
                extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                return "\n".join(extracted_pages)
            except Exception as e:
                # Fallback stream extraction
                try:
                    uploaded_file.seek(0)
                    content = uploaded_file.read().decode("latin-1", errors="ignore")
                    text_blocks = re.findall(r'\((.*?)\)', content)
                    return " ".join([b for b in text_blocks if len(b) > 3])
                except Exception:
                    return ""

        # 3. Word Documents (DOCX / DOC)
        elif filename.endswith(".docx") or filename.endswith(".doc"):
            try:
                import docx
                doc = docx.Document(uploaded_file)
                paragraphs = [p.text for p in doc.paragraphs if p.text]
                return "\n".join(paragraphs)
            except Exception:
                return ""

        return ""
        
    def extract_skills(self, text: str) -> list:
        if not text or not isinstance(text, str):
            return []
            
        found_skills = set()
        
        # 1. Regex search over text
        matches = self.pattern.findall(text)
        for m in matches:
            norm = SKILL_MAP.get(m.lower(), m)
            matched_skill = next((s for s in self.known_skills if s.lower() == norm.lower()), m.capitalize())
            found_skills.add(matched_skill)
            
        # 2. Check for manual comma or slash separated inputs
        words = re.split(r'[,/\n;]', text)
        for word in words:
            clean = word.strip()
            if not clean:
                continue
            clean_lower = clean.lower()
            if clean_lower in SKILL_MAP:
                found_skills.add(SKILL_MAP[clean_lower])
            else:
                for ks in self.known_skills:
                    if ks.lower() == clean_lower:
                        found_skills.add(ks)
                        break
                        
        return sorted(list(found_skills))

    def extract_years_experience(self, text: str) -> float:
        if not text:
            return 0.0
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience\s*of\s*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)'
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    return float(groups[0])
                elif len(groups) == 2:
                    return (float(groups[0]) + float(groups[1])) / 2.0
        return 0.0

if __name__ == "__main__":
    extractor = SkillExtractor()
    sample = "Looking for a Senior AI Engineer with 5+ years of experience in Python, PyTorch, Scikit-learn, Docker, and AWS SageMaker."
    print("Skills:", extractor.extract_skills(sample))
    print("Experience:", extractor.extract_years_experience(sample))
