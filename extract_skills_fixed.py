# extract_skills_fixed.py
# FIXED: Proper word boundary matching for short skills like R, Go, etc.

import pandas as pd
from sqlalchemy import create_engine
import re

DB_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/job_market"
ENGINE = create_engine(DB_URL)

# ===================
# SKILLS DICTIONARY (with matching rules)
# ===================

# Format: skill_name: (category, sector, skill_type, match_type)
# match_type: 
#   "exact" = needs word boundaries (for short words like R, Go)
#   "contains" = simple substring match (for longer, unique terms)

SKILLS_DICT = {
    # Programming - SHORT (need exact match)
    "r": ("programming", "Both", "technical", "exact"),
    "go": ("programming", "IT", "technical", "exact"),
    "c#": ("programming", "Both", "technical", "exact"),
    "c++": ("programming", "Both", "technical", "contains"),
    "sql": ("database", "Both", "technical", "exact"),
    "php": ("programming", "IT", "technical", "exact"),
    "sas": ("programming", "Both", "technical", "exact"),
    "vba": ("programming", "Finance", "technical", "exact"),
    "css": ("programming", "IT", "technical", "exact"),
    "aws": ("cloud", "Both", "technical", "exact"),
    "gcp": ("cloud", "IT", "technical", "exact"),
    "etl": ("data_engineering", "Both", "technical", "exact"),
    "dbt": ("data_engineering", "IT", "technical", "exact"),
    "nlp": ("ml", "IT", "technical", "exact"),
    "api": ("web", "Both", "technical", "exact"),
    "git": ("devops", "Both", "technical", "exact"),
    "cfa": ("certification", "Finance", "technical", "exact"),
    "cpa": ("certification", "Finance", "technical", "exact"),
    "pmp": ("certification", "Both", "technical", "exact"),
    "aml": ("finance", "Finance", "technical", "exact"),
    "kyc": ("finance", "Finance", "technical", "exact"),
    "sox": ("finance", "Finance", "technical", "exact"),
    "var": ("finance", "Finance", "technical", "exact"),
    "dcf": ("finance", "Finance", "technical", "exact"),
    
    # Programming - LONGER (contains match OK)
    "python": ("programming", "Both", "technical", "contains"),
    "java": ("programming", "Both", "technical", "exact"),  # avoid "javascript"
    "javascript": ("programming", "IT", "technical", "contains"),
    "typescript": ("programming", "IT", "technical", "contains"),
    "scala": ("programming", "IT", "technical", "exact"),  # avoid "scalable"
    "rust": ("programming", "IT", "technical", "exact"),   # avoid "trust", "robust"
    "ruby": ("programming", "IT", "technical", "exact"),
    "swift": ("programming", "IT", "technical", "exact"),
    "kotlin": ("programming", "IT", "technical", "contains"),
    "matlab": ("programming", "Both", "technical", "contains"),
    "bash": ("programming", "IT", "technical", "exact"),
    "powershell": ("programming", "IT", "technical", "contains"),
    "html": ("programming", "IT", "technical", "exact"),
    
    # Databases
    "postgresql": ("database", "Both", "technical", "contains"),
    "mysql": ("database", "Both", "technical", "contains"),
    "sql server": ("database", "Both", "technical", "contains"),
    "oracle": ("database", "Finance", "technical", "exact"),
    "mongodb": ("database", "IT", "technical", "contains"),
    "redis": ("database", "IT", "technical", "exact"),
    "elasticsearch": ("database", "IT", "technical", "contains"),
    "snowflake": ("database", "Both", "technical", "contains"),
    "redshift": ("database", "Both", "technical", "contains"),
    "bigquery": ("database", "Both", "technical", "contains"),
    "databricks": ("database", "Both", "technical", "contains"),
    "teradata": ("database", "Finance", "technical", "contains"),
    
    # Cloud
    "amazon web services": ("cloud", "Both", "technical", "contains"),
    "azure": ("cloud", "Both", "technical", "contains"),
    "microsoft azure": ("cloud", "Both", "technical", "contains"),
    "google cloud": ("cloud", "IT", "technical", "contains"),
    
    # DevOps
    "docker": ("devops", "IT", "technical", "contains"),
    "kubernetes": ("devops", "IT", "technical", "contains"),
    "jenkins": ("devops", "IT", "technical", "contains"),
    "terraform": ("devops", "IT", "technical", "contains"),
    "ansible": ("devops", "IT", "technical", "contains"),
    "github": ("devops", "Both", "technical", "contains"),
    "gitlab": ("devops", "IT", "technical", "contains"),
    "ci/cd": ("devops", "IT", "technical", "contains"),
    "linux": ("devops", "IT", "technical", "exact"),
    "jira": ("tools", "Both", "technical", "exact"),
    "confluence": ("tools", "Both", "technical", "contains"),
    
    # Data Engineering
    "spark": ("data_engineering", "Both", "technical", "exact"),
    "apache spark": ("data_engineering", "Both", "technical", "contains"),
    "hadoop": ("data_engineering", "Both", "technical", "contains"),
    "kafka": ("data_engineering", "IT", "technical", "contains"),
    "airflow": ("data_engineering", "IT", "technical", "contains"),
    "data pipeline": ("data_engineering", "Both", "technical", "contains"),
    "data warehouse": ("data_engineering", "Both", "technical", "contains"),
    
    # BI & Analytics
    "excel": ("bi", "Both", "technical", "exact"),
    "power bi": ("bi", "Both", "technical", "contains"),
    "powerbi": ("bi", "Both", "technical", "contains"),
    "tableau": ("bi", "Both", "technical", "contains"),
    "looker": ("bi", "IT", "technical", "exact"),
    "qlik": ("bi", "Both", "technical", "exact"),
    "data visualization": ("bi", "Both", "technical", "contains"),
    "reporting": ("bi", "Both", "technical", "exact"),
    "dashboards": ("bi", "Both", "technical", "contains"),
    
    # ML/AI
    "machine learning": ("ml", "Both", "technical", "contains"),
    "deep learning": ("ml", "IT", "technical", "contains"),
    "artificial intelligence": ("ml", "Both", "technical", "contains"),
    "tensorflow": ("ml", "IT", "technical", "contains"),
    "pytorch": ("ml", "IT", "technical", "contains"),
    "scikit-learn": ("ml", "Both", "technical", "contains"),
    "pandas": ("ml", "Both", "technical", "exact"),
    "numpy": ("ml", "Both", "technical", "exact"),
    "statistics": ("ml", "Both", "technical", "exact"),
    "statistical analysis": ("ml", "Both", "technical", "contains"),
    "predictive modeling": ("ml", "Both", "technical", "contains"),
    
    # Web frameworks
    "react": ("web", "IT", "technical", "exact"),
    "angular": ("web", "IT", "technical", "exact"),
    "vue": ("web", "IT", "technical", "exact"),
    "node.js": ("web", "IT", "technical", "contains"),
    "nodejs": ("web", "IT", "technical", "contains"),
    "django": ("web", "IT", "technical", "contains"),
    "flask": ("web", "IT", "technical", "exact"),
    "spring": ("web", "IT", "technical", "exact"),
    ".net": ("web", "Both", "technical", "contains"),
    "rest api": ("web", "IT", "technical", "contains"),
    "microservices": ("web", "IT", "technical", "contains"),
    
    # Finance specific
    "bloomberg": ("finance", "Finance", "technical", "contains"),
    "financial modeling": ("finance", "Finance", "technical", "contains"),
    "valuation": ("finance", "Finance", "technical", "exact"),
    "derivatives": ("finance", "Finance", "technical", "contains"),
    "fixed income": ("finance", "Finance", "technical", "contains"),
    "equities": ("finance", "Finance", "technical", "contains"),
    "portfolio management": ("finance", "Finance", "technical", "contains"),
    "risk management": ("finance", "Finance", "technical", "contains"),
    "credit risk": ("finance", "Finance", "technical", "contains"),
    "market risk": ("finance", "Finance", "technical", "contains"),
    "trading": ("finance", "Finance", "technical", "exact"),
    "quantitative analysis": ("finance", "Finance", "technical", "contains"),
    "gaap": ("finance", "Finance", "technical", "exact"),
    "ifrs": ("finance", "Finance", "technical", "exact"),
    "budgeting": ("finance", "Finance", "technical", "contains"),
    "forecasting": ("finance", "Both", "technical", "contains"),
    "fp&a": ("finance", "Finance", "technical", "contains"),
    "audit": ("finance", "Finance", "technical", "exact"),
    "compliance": ("finance", "Finance", "technical", "exact"),
    
    # ERP
    "sap": ("erp", "Both", "technical", "exact"),
    "netsuite": ("erp", "Finance", "technical", "contains"),
    "workday": ("erp", "Finance", "technical", "contains"),
    "salesforce": ("erp", "Both", "technical", "contains"),
    
    # SOFT SKILLS
    "communication skills": ("soft_skill", "Both", "soft", "contains"),
    "written communication": ("soft_skill", "Both", "soft", "contains"),
    "verbal communication": ("soft_skill", "Both", "soft", "contains"),
    "presentation skills": ("soft_skill", "Both", "soft", "contains"),
    "public speaking": ("soft_skill", "Both", "soft", "contains"),
    "leadership": ("soft_skill", "Both", "soft", "exact"),
    "team leadership": ("soft_skill", "Both", "soft", "contains"),
    "people management": ("soft_skill", "Both", "soft", "contains"),
    "mentoring": ("soft_skill", "Both", "soft", "contains"),
    "teamwork": ("soft_skill", "Both", "soft", "contains"),
    "collaboration": ("soft_skill", "Both", "soft", "exact"),
    "cross-functional": ("soft_skill", "Both", "soft", "contains"),
    "stakeholder management": ("soft_skill", "Both", "soft", "contains"),
    "problem solving": ("soft_skill", "Both", "soft", "contains"),
    "problem-solving": ("soft_skill", "Both", "soft", "contains"),
    "analytical thinking": ("soft_skill", "Both", "soft", "contains"),
    "critical thinking": ("soft_skill", "Both", "soft", "contains"),
    "analytical skills": ("soft_skill", "Both", "soft", "contains"),
    "attention to detail": ("soft_skill", "Both", "soft", "contains"),
    "detail-oriented": ("soft_skill", "Both", "soft", "contains"),
    "project management": ("soft_skill", "Both", "soft", "contains"),
    "time management": ("soft_skill", "Both", "soft", "contains"),
    "organizational skills": ("soft_skill", "Both", "soft", "contains"),
    "adaptability": ("soft_skill", "Both", "soft", "contains"),
    "flexibility": ("soft_skill", "Both", "soft", "exact"),
    "self-motivated": ("soft_skill", "Both", "soft", "contains"),
    "proactive": ("soft_skill", "Both", "soft", "contains"),
    "initiative": ("soft_skill", "Both", "soft", "exact"),
    "self-starter": ("soft_skill", "Both", "soft", "contains"),
    "negotiation": ("soft_skill", "Both", "soft", "contains"),
    "relationship building": ("soft_skill", "Both", "soft", "contains"),
    "client facing": ("soft_skill", "Both", "soft", "contains"),
    "customer service": ("soft_skill", "Both", "soft", "contains"),
    "strategic thinking": ("soft_skill", "Both", "soft", "contains"),
    "business acumen": ("soft_skill", "Both", "soft", "contains"),
    
    # Methodologies
    "agile": ("methodology", "Both", "technical", "exact"),
    "scrum": ("methodology", "Both", "technical", "exact"),
    "kanban": ("methodology", "Both", "technical", "exact"),
    "waterfall": ("methodology", "Both", "technical", "exact"),
    "lean": ("methodology", "Both", "technical", "exact"),
    "six sigma": ("methodology", "Both", "technical", "contains"),
}


def extract_skills(text):
    """Extract skills with proper word boundary matching"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_skills = []
    found_set = set()
    
    for skill, (category, sector, skill_type, match_type) in SKILLS_DICT.items():
        if skill in found_set:
            continue
        
        if match_type == "exact":
            # Word boundary matching for short/ambiguous terms
            # \b = word boundary, handles: space, punctuation, start/end
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append({
                    "job_id": None,
                    "skill": skill,
                    "category": category,
                    "skill_type": skill_type,
                    "confidence": 1.0,
                    "source": "rule_based"
                })
                found_set.add(skill)
        else:
            # Simple contains for longer, unique terms
            if skill in text_lower:
                found_skills.append({
                    "job_id": None,
                    "skill": skill,
                    "category": category,
                    "skill_type": skill_type,
                    "confidence": 1.0,
                    "source": "rule_based"
                })
                found_set.add(skill)
    
    return found_skills


def run_extraction():
    """Main function to extract skills from all jobs"""
    
    print("=" * 60)
    print("🎯 SKILL EXTRACTION (FIXED)")
    print("=" * 60)
    
    # Load jobs
    print("\n📥 Loading jobs...")
    jobs_df = pd.read_sql("""
        SELECT job_id, job_description 
        FROM v2_jobs 
        WHERE job_description IS NOT NULL
    """, ENGINE)
    print(f"   Found {len(jobs_df)} jobs")
    
    # Extract skills
    print("\n🔍 Extracting skills...")
    all_skills = []
    
    for idx, row in jobs_df.iterrows():
        skills = extract_skills(row["job_description"])
        
        for skill in skills:
            skill["job_id"] = row["job_id"]
            all_skills.append(skill)
        
        if idx % 2000 == 0 and idx > 0:
            print(f"   Processed {idx}/{len(jobs_df)} jobs...")
    
    print(f"\n   Total skills found: {len(all_skills)}")
    
    # Save to database
    print("\n💾 Saving to database...")
    df = pd.DataFrame(all_skills)
    df.to_sql("v2_job_skills", ENGINE, if_exists="append", index=False)
    
    # Show top skills
    print("\n📊 TOP 15 SKILLS:")
    top_skills = df.groupby("skill").size().sort_values(ascending=False).head(15)
    for skill, count in top_skills.items():
        print(f"   {skill}: {count}")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    run_extraction()
