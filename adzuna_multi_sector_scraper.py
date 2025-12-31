# adzuna_multi_sector_scraper.py
# Scrapes IT + Finance jobs from multiple countries

import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import time

# ===================
# CONFIGURATION
# ===================

APP_ID = "YOUR_APP_ID"
APP_KEY = "YOUR_APP_KEY"

# Database connection
ENGINE = create_engine("postgresql://postgres:YOUR_PASSWORD@localhost:5432/job_market")

# Countries to scrape (Adzuna coverage)
COUNTRIES = {
    "gb": "United Kingdom",
    "de": "Germany",
    "nl": "Netherlands",
    "fr": "France",
    "at": "Austria",
    "ch": "Switzerland",
    "us": "United States",
    "au": "Australia"
}

# ===================
# JOB ROLES TO SCRAPE
# ===================

IT_ROLES = [
    # Data & Analytics
    "data engineer",
    "data analyst",
    "data scientist",
    "business intelligence",
    "analytics engineer",
    
    # Software Development
    "software engineer",
    "backend developer",
    "frontend developer",
    "full stack developer",
    "python developer",
    "java developer",
    "javascript developer",
    
    # Cloud & DevOps
    "cloud engineer",
    "devops engineer",
    "site reliability engineer",
    "platform engineer",
    "aws engineer",
    "azure engineer",
    
    # AI & ML
    "machine learning engineer",
    "ai engineer",
    "mlops engineer",
    "nlp engineer",
    "computer vision engineer",
    
    # Security
    "security engineer",
    "cybersecurity analyst",
    "penetration tester",
    
    # Management & Architecture
    "solution architect",
    "technical lead",
    "engineering manager",
    "cto",
    "product manager tech"
]

FINANCE_ROLES = [
    # Quant & Trading
    "quantitative analyst",
    "quantitative developer",
    "algorithmic trader",
    "trading systems developer",
    
    # Risk & Compliance
    "risk analyst",
    "risk manager",
    "compliance analyst",
    "financial risk",
    
    # Investment & Banking
    "investment analyst",
    "financial analyst",
    "portfolio manager",
    "asset manager",
    "investment banker",
    
    # FinTech specific
    "fintech engineer",
    "blockchain developer",
    "payments engineer",
    
    # Finance + Tech hybrid
    "financial data analyst",
    "finance data engineer",
    "treasury analyst"
]

ALL_ROLES = IT_ROLES + FINANCE_ROLES

# ===================
# SCRAPER FUNCTIONS
# ===================

def scrape_adzuna(country_code, search_term, max_pages=3):
    """Scrape jobs from Adzuna API for a specific country and search term"""
    
    all_jobs = []
    
    for page in range(1, max_pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}"
        
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "what": search_term,
            "results_per_page": 50,
            "content-type": "application/json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("results", [])
                
                if not jobs:
                    break
                    
                all_jobs.extend(jobs)
                print(f"  Page {page}: {len(jobs)} jobs")
                
            else:
                print(f"  ❌ Error {response.status_code}: {response.text[:100]}")
                break
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            break
            
        time.sleep(0.5)  # Rate limiting
    
    return all_jobs


def parse_job(job, country_code, country_name, search_term, sector):
    """Parse raw job data into clean format"""
    
    return {
        "job_id": job.get("id"),
        "job_title": job.get("title"),
        "company": job.get("company", {}).get("display_name"),
        "location": job.get("location", {}).get("display_name"),
        "country_code": country_code,
        "country": country_name,
        "category": job.get("category", {}).get("label"),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "contract_type": job.get("contract_type"),
        "job_description": job.get("description"),
        "job_url": job.get("redirect_url"),
        "created": job.get("created"),
        "search_term": search_term,
        "sector": sector,
        "source": "adzuna",
        "scrape_date": datetime.now().strftime("%Y-%m-%d")
    }


def run_full_scrape(countries=None, roles=None, max_pages=2):
    """Run full scrape across all countries and roles"""
    
    if countries is None:
        countries = COUNTRIES
    if roles is None:
        roles = ALL_ROLES
    
    all_parsed_jobs = []
    
    print("=" * 60)
    print(f"🚀 STARTING MULTI-SECTOR JOB SCRAPE")
    print(f"   Countries: {len(countries)}")
    print(f"   Roles: {len(roles)}")
    print("=" * 60)
    
    for country_code, country_name in countries.items():
        print(f"\n🌍 {country_name} ({country_code.upper()})")
        print("-" * 40)
        
        for role in roles:
            # Determine sector
            sector = "Finance" if role in FINANCE_ROLES else "IT"
            
            print(f"\n  🔍 Searching: {role}")
            
            jobs = scrape_adzuna(country_code, role, max_pages=max_pages)
            
            for job in jobs:
                parsed = parse_job(job, country_code, country_name, role, sector)
                all_parsed_jobs.append(parsed)
            
            print(f"  ✅ Total for '{role}': {len(jobs)} jobs")
            
            time.sleep(1)  # Be nice to API
    
    print("\n" + "=" * 60)
    print(f"🎉 SCRAPE COMPLETE!")
    print(f"   Total jobs collected: {len(all_parsed_jobs)}")
    print("=" * 60)
    
    return all_parsed_jobs


def save_to_database(jobs, table_name="jobs_adzuna"):
    """Save jobs to PostgreSQL"""
    
    if not jobs:
        print("❌ No jobs to save")
        return
    
    df = pd.DataFrame(jobs)
    
    # Remove duplicates by job_id
    df = df.drop_duplicates(subset=["job_id"], keep="first")
    
    # Save to DB
    df.to_sql(table_name, ENGINE, if_exists="append", index=False)
    
    print(f"✅ Saved {len(df)} jobs to '{table_name}'")
    
    return df


def get_scrape_stats():
    """Get statistics from scraped data"""
    
    query = """
    SELECT 
        sector,
        country,
        COUNT(*) as job_count,
        COUNT(DISTINCT search_term) as role_types,
        COUNT(DISTINCT company) as companies,
        scrape_date
    FROM jobs_adzuna
    GROUP BY sector, country, scrape_date
    ORDER BY job_count DESC
    """
    
    df = pd.read_sql(query, ENGINE)
    return df


# ===================
# MAIN EXECUTION
# ===================

if __name__ == "__main__":
    
    # Option 1: Quick test (1 country, few roles)
    # jobs = run_full_scrape(
    #     countries={"gb": "United Kingdom"},
    #     roles=["data engineer", "software engineer", "financial analyst"],
    #     max_pages=1
    # )
    
    # Option 2: Medium scrape (3 countries, all roles)
    jobs = run_full_scrape(
        countries={
            "gb": "United Kingdom",
            "de": "Germany",
            "us": "United States"
        },
        roles=ALL_ROLES,
        max_pages=2
    )
    
    # Option 3: Full scrape (all countries, all roles)
    # jobs = run_full_scrape(max_pages=2)
    
    # Save to database
    if jobs:
        df = save_to_database(jobs)
        
        # Show sample
        print("\n📊 SAMPLE DATA:")
        print(df[["job_title", "company", "country", "sector", "salary_min"]].head(10))
        
        # Show stats by sector
        print("\n📈 JOBS BY SECTOR:")
        print(df.groupby("sector").size())
        
        print("\n📈 JOBS BY COUNTRY:")
        print(df.groupby("country").size())
