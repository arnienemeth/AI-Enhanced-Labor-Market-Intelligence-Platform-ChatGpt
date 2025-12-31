# unified_job_loader_v2.py
# IMPROVED: Better job roles, complete skills dictionary (tech + soft skills)

import requests
import pandas as pd
from datetime import datetime, date
from sqlalchemy import create_engine, text
import time
import re

# ===================
# CONFIGURATION
# ===================

DB_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/job_market"
ENGINE = create_engine(DB_URL)

ADZUNA_APP_ID = "YOUR_APP_ID"
ADZUNA_APP_KEY = "YOUR_APP_KEY"

# Countries to scrape
COUNTRIES = {
    "gb": "United Kingdom",
    "de": "Germany",
    "us": "United States"
}

# ===================
# JOB SEARCH TERMS (BROADER)
# ===================

IT_SEARCH_TERMS = [
    # General IT
    "software developer",
    "software engineer",
    "programmer",
    "web developer",
    "frontend developer",
    "backend developer",
    "full stack developer",
    
    # Data & Analytics
    "data analyst",
    "data engineer",
    "data scientist",
    "business analyst",
    "business intelligence",
    "analytics",
    "reporting analyst",
    
    # Cloud & Infrastructure
    "cloud engineer",
    "devops",
    "system administrator",
    "network engineer",
    "infrastructure engineer",
    
    # AI/ML
    "machine learning",
    "artificial intelligence",
    "ai engineer",
    
    # Security
    "cyber security",
    "security analyst",
    "information security",
    
    # Management
    "it manager",
    "project manager it",
    "scrum master",
    "product owner",
    "technical lead"
]

FINANCE_SEARCH_TERMS = [
    # General Finance
    "financial analyst",
    "finance manager",
    "accountant",
    "financial controller",
    "treasury",
    
    # Investment & Banking
    "investment analyst",
    "investment banker",
    "portfolio manager",
    "asset management",
    "wealth management",
    "private equity",
    
    # Risk & Compliance
    "risk analyst",
    "risk manager",
    "compliance officer",
    "compliance analyst",
    "audit",
    "internal audit",
    
    # Quantitative
    "quantitative analyst",
    "quant developer",
    "trading",
    "trader",
    
    # Corporate Finance
    "fp&a",
    "financial planning",
    "corporate finance",
    "m&a analyst"
]

ALL_SEARCH_TERMS = IT_SEARCH_TERMS + FINANCE_SEARCH_TERMS

# ===================
# COMPLETE SKILLS DICTIONARY
# ===================

SKILLS_DICT = {
    # =====================
    # PROGRAMMING LANGUAGES
    # =====================
    "python": ("programming", "Both", "technical"),
    "java": ("programming", "Both", "technical"),
    "javascript": ("programming", "IT", "technical"),
    "typescript": ("programming", "IT", "technical"),
    "c#": ("programming", "Both", "technical"),
    "c++": ("programming", "Both", "technical"),
    "sql": ("programming", "Both", "technical"),
    "r": ("programming", "Both", "technical"),
    "scala": ("programming", "IT", "technical"),
    "go": ("programming", "IT", "technical"),
    "golang": ("programming", "IT", "technical"),
    "rust": ("programming", "IT", "technical"),
    "php": ("programming", "IT", "technical"),
    "ruby": ("programming", "IT", "technical"),
    "swift": ("programming", "IT", "technical"),
    "kotlin": ("programming", "IT", "technical"),
    "vba": ("programming", "Finance", "technical"),
    "matlab": ("programming", "Both", "technical"),
    "sas": ("programming", "Both", "technical"),
    "html": ("programming", "IT", "technical"),
    "css": ("programming", "IT", "technical"),
    "bash": ("programming", "IT", "technical"),
    "powershell": ("programming", "IT", "technical"),
    
    # =====================
    # DATABASES
    # =====================
    "postgresql": ("database", "Both", "technical"),
    "mysql": ("database", "Both", "technical"),
    "sql server": ("database", "Both", "technical"),
    "oracle": ("database", "Finance", "technical"),
    "mongodb": ("database", "IT", "technical"),
    "redis": ("database", "IT", "technical"),
    "elasticsearch": ("database", "IT", "technical"),
    "cassandra": ("database", "IT", "technical"),
    "dynamodb": ("database", "IT", "technical"),
    "snowflake": ("database", "Both", "technical"),
    "redshift": ("database", "Both", "technical"),
    "bigquery": ("database", "Both", "technical"),
    "databricks": ("database", "Both", "technical"),
    "teradata": ("database", "Finance", "technical"),
    
    # =====================
    # CLOUD PLATFORMS
    # =====================
    "aws": ("cloud", "Both", "technical"),
    "amazon web services": ("cloud", "Both", "technical"),
    "azure": ("cloud", "Both", "technical"),
    "microsoft azure": ("cloud", "Both", "technical"),
    "gcp": ("cloud", "IT", "technical"),
    "google cloud": ("cloud", "IT", "technical"),
    
    # =====================
    # DEVOPS & TOOLS
    # =====================
    "docker": ("devops", "IT", "technical"),
    "kubernetes": ("devops", "IT", "technical"),
    "jenkins": ("devops", "IT", "technical"),
    "terraform": ("devops", "IT", "technical"),
    "ansible": ("devops", "IT", "technical"),
    "git": ("devops", "Both", "technical"),
    "github": ("devops", "Both", "technical"),
    "gitlab": ("devops", "IT", "technical"),
    "ci/cd": ("devops", "IT", "technical"),
    "linux": ("devops", "IT", "technical"),
    "jira": ("tools", "Both", "technical"),
    "confluence": ("tools", "Both", "technical"),
    
    # =====================
    # DATA ENGINEERING
    # =====================
    "spark": ("data_engineering", "Both", "technical"),
    "apache spark": ("data_engineering", "Both", "technical"),
    "hadoop": ("data_engineering", "Both", "technical"),
    "kafka": ("data_engineering", "IT", "technical"),
    "airflow": ("data_engineering", "IT", "technical"),
    "dbt": ("data_engineering", "IT", "technical"),
    "etl": ("data_engineering", "Both", "technical"),
    "data pipeline": ("data_engineering", "Both", "technical"),
    "data warehouse": ("data_engineering", "Both", "technical"),
    
    # =====================
    # DATA ANALYSIS & BI
    # =====================
    "excel": ("bi", "Both", "technical"),
    "microsoft excel": ("bi", "Both", "technical"),
    "power bi": ("bi", "Both", "technical"),
    "powerbi": ("bi", "Both", "technical"),
    "tableau": ("bi", "Both", "technical"),
    "looker": ("bi", "IT", "technical"),
    "qlik": ("bi", "Both", "technical"),
    "qlikview": ("bi", "Both", "technical"),
    "qliksense": ("bi", "Both", "technical"),
    "ssrs": ("bi", "Both", "technical"),
    "ssis": ("bi", "Both", "technical"),
    "ssas": ("bi", "Both", "technical"),
    "data visualization": ("bi", "Both", "technical"),
    "reporting": ("bi", "Both", "technical"),
    "dashboards": ("bi", "Both", "technical"),
    
    # =====================
    # DATA SCIENCE & ML
    # =====================
    "machine learning": ("ml", "Both", "technical"),
    "deep learning": ("ml", "IT", "technical"),
    "artificial intelligence": ("ml", "Both", "technical"),
    "neural network": ("ml", "IT", "technical"),
    "nlp": ("ml", "IT", "technical"),
    "natural language processing": ("ml", "IT", "technical"),
    "computer vision": ("ml", "IT", "technical"),
    "tensorflow": ("ml", "IT", "technical"),
    "pytorch": ("ml", "IT", "technical"),
    "scikit-learn": ("ml", "Both", "technical"),
    "pandas": ("ml", "Both", "technical"),
    "numpy": ("ml", "Both", "technical"),
    "statistics": ("ml", "Both", "technical"),
    "statistical analysis": ("ml", "Both", "technical"),
    "predictive modeling": ("ml", "Both", "technical"),
    "regression": ("ml", "Both", "technical"),
    "classification": ("ml", "Both", "technical"),
    
    # =====================
    # WEB & FRAMEWORKS
    # =====================
    "react": ("web", "IT", "technical"),
    "angular": ("web", "IT", "technical"),
    "vue": ("web", "IT", "technical"),
    "node.js": ("web", "IT", "technical"),
    "nodejs": ("web", "IT", "technical"),
    "django": ("web", "IT", "technical"),
    "flask": ("web", "IT", "technical"),
    "spring": ("web", "IT", "technical"),
    ".net": ("web", "Both", "technical"),
    "rest api": ("web", "IT", "technical"),
    "api": ("web", "Both", "technical"),
    "microservices": ("web", "IT", "technical"),
    
    # =====================
    # FINANCE SPECIFIC
    # =====================
    "bloomberg": ("finance", "Finance", "technical"),
    "bloomberg terminal": ("finance", "Finance", "technical"),
    "reuters": ("finance", "Finance", "technical"),
    "financial modeling": ("finance", "Finance", "technical"),
    "dcf": ("finance", "Finance", "technical"),
    "valuation": ("finance", "Finance", "technical"),
    "derivatives": ("finance", "Finance", "technical"),
    "fixed income": ("finance", "Finance", "technical"),
    "equities": ("finance", "Finance", "technical"),
    "portfolio management": ("finance", "Finance", "technical"),
    "risk management": ("finance", "Finance", "technical"),
    "credit risk": ("finance", "Finance", "technical"),
    "market risk": ("finance", "Finance", "technical"),
    "var": ("finance", "Finance", "technical"),
    "value at risk": ("finance", "Finance", "technical"),
    "monte carlo": ("finance", "Finance", "technical"),
    "black-scholes": ("finance", "Finance", "technical"),
    "trading": ("finance", "Finance", "technical"),
    "algorithmic trading": ("finance", "Finance", "technical"),
    "quantitative analysis": ("finance", "Finance", "technical"),
    "gaap": ("finance", "Finance", "technical"),
    "ifrs": ("finance", "Finance", "technical"),
    "budgeting": ("finance", "Finance", "technical"),
    "forecasting": ("finance", "Both", "technical"),
    "fp&a": ("finance", "Finance", "technical"),
    "consolidation": ("finance", "Finance", "technical"),
    "reconciliation": ("finance", "Finance", "technical"),
    "audit": ("finance", "Finance", "technical"),
    "sox": ("finance", "Finance", "technical"),
    "regulatory": ("finance", "Finance", "technical"),
    "compliance": ("finance", "Finance", "technical"),
    "aml": ("finance", "Finance", "technical"),
    "kyc": ("finance", "Finance", "technical"),
    
    # =====================
    # ERP & BUSINESS SYSTEMS
    # =====================
    "sap": ("erp", "Both", "technical"),
    "oracle erp": ("erp", "Finance", "technical"),
    "netsuite": ("erp", "Finance", "technical"),
    "workday": ("erp", "Finance", "technical"),
    "salesforce": ("erp", "Both", "technical"),
    "dynamics": ("erp", "Both", "technical"),
    
    # =====================
    # SOFT SKILLS
    # =====================
    "communication": ("soft_skill", "Both", "soft"),
    "communication skills": ("soft_skill", "Both", "soft"),
    "written communication": ("soft_skill", "Both", "soft"),
    "verbal communication": ("soft_skill", "Both", "soft"),
    "presentation": ("soft_skill", "Both", "soft"),
    "presentation skills": ("soft_skill", "Both", "soft"),
    "public speaking": ("soft_skill", "Both", "soft"),
    
    "leadership": ("soft_skill", "Both", "soft"),
    "team leadership": ("soft_skill", "Both", "soft"),
    "people management": ("soft_skill", "Both", "soft"),
    "mentoring": ("soft_skill", "Both", "soft"),
    "coaching": ("soft_skill", "Both", "soft"),
    
    "teamwork": ("soft_skill", "Both", "soft"),
    "collaboration": ("soft_skill", "Both", "soft"),
    "cross-functional": ("soft_skill", "Both", "soft"),
    "stakeholder management": ("soft_skill", "Both", "soft"),
    "stakeholder engagement": ("soft_skill", "Both", "soft"),
    
    "problem solving": ("soft_skill", "Both", "soft"),
    "problem-solving": ("soft_skill", "Both", "soft"),
    "analytical thinking": ("soft_skill", "Both", "soft"),
    "critical thinking": ("soft_skill", "Both", "soft"),
    "analytical skills": ("soft_skill", "Both", "soft"),
    "attention to detail": ("soft_skill", "Both", "soft"),
    "detail-oriented": ("soft_skill", "Both", "soft"),
    
    "project management": ("soft_skill", "Both", "soft"),
    "time management": ("soft_skill", "Both", "soft"),
    "organizational skills": ("soft_skill", "Both", "soft"),
    "multitasking": ("soft_skill", "Both", "soft"),
    "prioritization": ("soft_skill", "Both", "soft"),
    "deadline": ("soft_skill", "Both", "soft"),
    
    "adaptability": ("soft_skill", "Both", "soft"),
    "flexibility": ("soft_skill", "Both", "soft"),
    "fast-paced": ("soft_skill", "Both", "soft"),
    "self-motivated": ("soft_skill", "Both", "soft"),
    "proactive": ("soft_skill", "Both", "soft"),
    "initiative": ("soft_skill", "Both", "soft"),
    "self-starter": ("soft_skill", "Both", "soft"),
    
    "negotiation": ("soft_skill", "Both", "soft"),
    "influencing": ("soft_skill", "Both", "soft"),
    "relationship building": ("soft_skill", "Both", "soft"),
    "client facing": ("soft_skill", "Both", "soft"),
    "customer service": ("soft_skill", "Both", "soft"),
    
    "creativity": ("soft_skill", "Both", "soft"),
    "innovation": ("soft_skill", "Both", "soft"),
    "strategic thinking": ("soft_skill", "Both", "soft"),
    "business acumen": ("soft_skill", "Both", "soft"),
    "commercial awareness": ("soft_skill", "Both", "soft"),
    
    # =====================
    # METHODOLOGIES
    # =====================
    "agile": ("methodology", "Both", "technical"),
    "scrum": ("methodology", "Both", "technical"),
    "kanban": ("methodology", "Both", "technical"),
    "waterfall": ("methodology", "Both", "technical"),
    "lean": ("methodology", "Both", "technical"),
    "six sigma": ("methodology", "Both", "technical"),
    "prince2": ("methodology", "Both", "technical"),
    "pmp": ("methodology", "Both", "technical"),
    
    # =====================
    # CERTIFICATIONS (as skills)
    # =====================
    "cfa": ("certification", "Finance", "technical"),
    "cpa": ("certification", "Finance", "technical"),
    "acca": ("certification", "Finance", "technical"),
    "frm": ("certification", "Finance", "technical"),
    "aws certified": ("certification", "IT", "technical"),
    "azure certified": ("certification", "IT", "technical"),
    "cissp": ("certification", "IT", "technical"),
    "pmp certified": ("certification", "Both", "technical"),
}

# ===================
# SCRAPING FUNCTIONS
# ===================

def scrape_adzuna(country_code, search_term, max_pages=2):
    """Scrape from Adzuna API"""
    jobs = []
    
    for page in range(1, max_pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}"
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "what": search_term,
            "results_per_page": 50
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if not results:
                    break
                jobs.extend(results)
            else:
                break
        except Exception as e:
            print(f"    ❌ Error: {e}")
            break
            
        time.sleep(0.3)
    
    return jobs


def scrape_remotive():
    """Scrape from Remotive API"""
    try:
        response = requests.get("https://remotive.com/api/remote-jobs", timeout=15)
        if response.status_code == 200:
            return response.json().get("jobs", [])
    except Exception as e:
        print(f"❌ Remotive error: {e}")
    return []


# ===================
# PARSING FUNCTIONS
# ===================

def determine_sector(search_term, category=""):
    """Determine if job is IT or Finance"""
    finance_keywords = ["financ", "account", "audit", "risk", "compliance", 
                       "invest", "trading", "treasury", "tax", "banking",
                       "quant", "portfolio", "asset", "wealth", "m&a", "fp&a"]
    
    search_lower = search_term.lower()
    category_lower = category.lower() if category else ""
    
    for keyword in finance_keywords:
        if keyword in search_lower or keyword in category_lower:
            return "Finance"
    
    return "IT"


def parse_adzuna_job(job, country_code, country_name, search_term):
    """Parse Adzuna job to unified format"""
    category = job.get("category", {}).get("label", "")
    sector = determine_sector(search_term, category)
    
    return {
        "job_id": f"adzuna_{job.get('id')}",
        "job_title": job.get("title"),
        "company": job.get("company", {}).get("display_name"),
        "location": job.get("location", {}).get("display_name"),
        "country_code": country_code,
        "country": country_name,
        "category": category,
        "sector": sector,
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "contract_type": job.get("contract_type"),
        "job_description": job.get("description"),
        "job_url": job.get("redirect_url"),
        "source": "adzuna",
        "search_term": search_term,
        "created_at": job.get("created"),
        "scrape_date": date.today()
    }


def parse_remotive_job(job):
    """Parse Remotive job to unified format"""
    category = job.get("category", "")
    sector = determine_sector(category, category)
    
    return {
        "job_id": f"remotive_{job.get('id')}",
        "job_title": job.get("title"),
        "company": job.get("company_name"),
        "location": job.get("candidate_required_location"),
        "country_code": "remote",
        "country": "Remote",
        "category": category,
        "sector": sector,
        "salary_min": None,
        "salary_max": None,
        "contract_type": job.get("job_type"),
        "job_description": job.get("description"),
        "job_url": job.get("url"),
        "source": "remotive",
        "search_term": category,
        "created_at": job.get("publication_date"),
        "scrape_date": date.today()
    }


# ===================
# SKILL EXTRACTION (IMPROVED)
# ===================

def extract_skills(text):
    """Extract skills from job description - improved matching"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_skills = []
    found_skill_names = set()  # Avoid duplicates
    
    for skill, (category, sector, skill_type) in SKILLS_DICT.items():
        # Skip if already found (handles aliases)
        if skill in found_skill_names:
            continue
            
        # Word boundary matching for short skills
        if len(skill) <= 3:
            # For short skills like "r", "go", "sql" - need word boundaries
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append({
                    "skill": skill,
                    "category": category,
                    "skill_type": skill_type,
                    "confidence": 1.0,
                    "source": "rule_based"
                })
                found_skill_names.add(skill)
        else:
            # For longer skills - simple contains check
            if skill in text_lower:
                found_skills.append({
                    "skill": skill,
                    "category": category,
                    "skill_type": skill_type,
                    "confidence": 1.0,
                    "source": "rule_based"
                })
                found_skill_names.add(skill)
    
    return found_skills


# ===================
# DATABASE FUNCTIONS
# ===================

def init_skills_dictionary():
    """Initialize skills dictionary table"""
    records = []
    for skill, (category, sector, skill_type) in SKILLS_DICT.items():
        records.append({
            "skill": skill,
            "category": category,
            "sector": sector,
            "skill_type": skill_type
        })
    
    df = pd.DataFrame(records)
    df.to_sql("v2_skills_dictionary", ENGINE, if_exists="replace", index=False)
    print(f"✅ Loaded {len(df)} skills into v2_skills_dictionary")


def save_jobs(jobs_list):
    """Save jobs to database"""
    if not jobs_list:
        return 0
    
    df = pd.DataFrame(jobs_list)
    df = df.drop_duplicates(subset=["job_id"], keep="first")
    
    try:
        existing = pd.read_sql("SELECT job_id FROM v2_jobs", ENGINE)
        df = df[~df["job_id"].isin(existing["job_id"])]
    except:
        pass
    
    if len(df) > 0:
        df.to_sql("v2_jobs", ENGINE, if_exists="append", index=False)
    
    return len(df)


def save_skills(job_id, skills):
    """Save extracted skills to database"""
    if not skills:
        return
    
    records = []
    for skill in skills:
        records.append({
            "job_id": job_id,
            "skill": skill["skill"],
            "category": skill["category"],
            "skill_type": skill["skill_type"],
            "confidence": skill["confidence"],
            "source": skill["source"]
        })
    
    df = pd.DataFrame(records)
    df.to_sql("v2_job_skills", ENGINE, if_exists="append", index=False)


# ===================
# MAIN PIPELINE
# ===================

def run_full_pipeline():
    """Run complete scraping and loading pipeline"""
    
    print("=" * 60)
    print("🚀 JOB MARKET INTELLIGENCE - DATA PIPELINE v2")
    print(f"   Started: {datetime.now()}")
    print("=" * 60)
    
    all_jobs = []
    
    # 1. Initialize skills dictionary
    print("\n📚 Initializing skills dictionary...")
    init_skills_dictionary()
    
    # 2. Scrape Adzuna
    print("\n🔍 SCRAPING ADZUNA...")
    
    for country_code, country_name in COUNTRIES.items():
        print(f"\n  🌍 {country_name}")
        
        for search_term in ALL_SEARCH_TERMS:
            print(f"    → {search_term}", end=" ")
            jobs = scrape_adzuna(country_code, search_term, max_pages=2)
            
            for job in jobs:
                parsed = parse_adzuna_job(job, country_code, country_name, search_term)
                all_jobs.append(parsed)
            
            print(f"({len(jobs)} jobs)")
            time.sleep(0.3)
    
    # 3. Scrape Remotive
    print("\n🔍 SCRAPING REMOTIVE...")
    remotive_jobs = scrape_remotive()
    for job in remotive_jobs:
        parsed = parse_remotive_job(job)
        all_jobs.append(parsed)
    print(f"  ✅ {len(remotive_jobs)} jobs from Remotive")
    
    # 4. Save jobs
    print("\n💾 SAVING JOBS TO DATABASE...")
    new_jobs = save_jobs(all_jobs)
    print(f"  ✅ {new_jobs} new jobs saved")
    
    # 5. Extract skills
    print("\n🧠 EXTRACTING SKILLS (this may take a few minutes)...")
    jobs_df = pd.read_sql("""
        SELECT job_id, job_description 
        FROM v2_jobs 
        WHERE job_description IS NOT NULL
    """, ENGINE)
    
    skill_count = 0
    for idx, row in jobs_df.iterrows():
        skills = extract_skills(row["job_description"])
        if skills:
            save_skills(row["job_id"], skills)
            skill_count += len(skills)
        
        if idx % 500 == 0 and idx > 0:
            print(f"    Processed {idx} jobs...")
    
    print(f"  ✅ {skill_count} skills extracted")
    
    # 6. Summary
    print("\n" + "=" * 60)
    print("📊 PIPELINE COMPLETE - SUMMARY")
    print("=" * 60)
    
    with ENGINE.connect() as conn:
        jobs_count = conn.execute(text("SELECT COUNT(*) FROM v2_jobs")).scalar()
        skills_count = conn.execute(text("SELECT COUNT(*) FROM v2_job_skills")).scalar()
        countries = conn.execute(text("SELECT COUNT(DISTINCT country) FROM v2_jobs")).scalar()
        companies = conn.execute(text("SELECT COUNT(DISTINCT company) FROM v2_jobs")).scalar()
        
        # Top skills
        top_skills = pd.read_sql("""
            SELECT skill, skill_type, COUNT(*) as count 
            FROM v2_job_skills 
            GROUP BY skill, skill_type 
            ORDER BY count DESC 
            LIMIT 15
        """, conn)
    
    print(f"\n  📁 Total Jobs: {jobs_count}")
    print(f"  🏢 Companies: {companies}")
    print(f"  🌍 Countries: {countries}")
    print(f"  🎯 Skills extracted: {skills_count}")
    
    print(f"\n  📈 TOP 15 SKILLS:")
    print(top_skills.to_string(index=False))
    
    print(f"\n  ⏱️  Finished: {datetime.now()}")
    
    return jobs_count, skills_count


if __name__ == "__main__":
    run_full_pipeline()
