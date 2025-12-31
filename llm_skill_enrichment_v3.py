# llm_skill_enrichment_v2.py
# Uses OpenAI GPT-4o-mini to infer additional skills from job descriptions
# Works with v2 tables

import json
import os
import pandas as pd
from sqlalchemy import create_engine
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ===================
# CONFIGURATION
# ===================

DB_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/job_market"
engine = create_engine(DB_URL)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Limit jobs to process (to control API costs)
MAX_JOBS_TO_PROCESS = 500  # Set to None for all jobs

# ===================
# MAIN FUNCTIONS
# ===================

def load_jobs_for_enrichment():
    """Load jobs that need LLM enrichment"""
    
    query = """
        SELECT j.job_id, j.job_title, j.job_description, j.sector
        FROM v2_jobs j
        WHERE j.job_description IS NOT NULL
        AND LENGTH(j.job_description) > 100
    """
    
    if MAX_JOBS_TO_PROCESS:
        query += f" LIMIT {MAX_JOBS_TO_PROCESS}"
    
    return pd.read_sql(query, engine)


def load_existing_skills():
    """Load already extracted skills"""
    
    query = """
        SELECT job_id, skill
        FROM v2_job_skills
    """
    return pd.read_sql(query, engine)


def get_skills_for_job(job_id, skills_df):
    """Get list of skills for a specific job"""
    
    job_skills = skills_df[skills_df['job_id'] == job_id]['skill'].tolist()
    return ", ".join(job_skills) if job_skills else "None extracted yet"


def enrich_with_llm(job_id, job_title, description, sector, existing_skills):
    """Use GPT-4o-mini to infer additional skills"""
    
    prompt = f"""You are an expert HR analyst specializing in {sector} jobs.

Analyze this job posting and identify skills that are IMPLIED but not explicitly mentioned.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{description[:3000]}

ALREADY EXTRACTED SKILLS:
{existing_skills}

YOUR TASK:
Identify 3-8 additional skills that are strongly implied by this job but NOT in the already extracted list.
Include BOTH technical skills AND soft skills.

RULES:
- Only include skills with high confidence (>0.7)
- Don't repeat skills already extracted
- Include skill_type: "technical" or "soft"
- Don't hallucinate - only infer what's clearly implied

Return ONLY a valid JSON array, no other text:
[
  {{"skill": "python", "confidence": 0.9, "skill_type": "technical"}},
  {{"skill": "communication", "confidence": 0.85, "skill_type": "soft"}}
]
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown if present
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        # Parse JSON
        inferred_skills = json.loads(content)
        
        return inferred_skills
        
    except json.JSONDecodeError as e:
        print(f"  ⚠️ JSON parse error: {e}")
        return []
    except Exception as e:
        print(f"  ❌ API error: {e}")
        return []


def save_enriched_skills(enriched_rows):
    """Save LLM-inferred skills to database"""
    
    if not enriched_rows:
        print("No skills to save")
        return
    
    df = pd.DataFrame(enriched_rows)
    df.to_sql("v2_job_skills", engine, if_exists="append", index=False)
    print(f"\n🎉 Saved {len(df)} LLM-enriched skills to v2_job_skills")


# ===================
# MAIN EXECUTION
# ===================

def run_llm_enrichment():
    """Main function to run LLM enrichment"""
    
    print("=" * 60)
    print("🤖 LLM SKILL ENRICHMENT (OpenAI GPT-4o-mini)")
    print(f"   Started: {datetime.now()}")
    print("=" * 60)
    
    # Load data
    print("\n📥 Loading jobs...")
    jobs_df = load_jobs_for_enrichment()
    print(f"   Found {len(jobs_df)} jobs to process")
    
    print("\n📥 Loading existing skills...")
    skills_df = load_existing_skills()
    print(f"   Found {len(skills_df)} existing skill extractions")
    
    # Process jobs
    print("\n🧠 Processing with LLM...")
    enriched_rows = []
    processed = 0
    errors = 0
    
    for idx, row in jobs_df.iterrows():
        job_id = row['job_id']
        job_title = row['job_title']
        description = row['job_description']
        sector = row['sector']
        
        # Get existing skills for this job
        existing_skills = get_skills_for_job(job_id, skills_df)
        
        print(f"\n  [{idx+1}/{len(jobs_df)}] {job_title[:50]}...")
        
        # Call LLM
        inferred = enrich_with_llm(job_id, job_title, description, sector, existing_skills)
        
        if inferred:
            for item in inferred:
                enriched_rows.append({
                    "job_id": job_id,
                    "skill": item.get("skill", "").lower(),
                    "category": "llm_inferred",
                    "skill_type": item.get("skill_type", "technical"),
                    "confidence": item.get("confidence", 0.7),
                    "source": "openai_gpt4o_mini"
                })
            
            print(f"    ✅ Found {len(inferred)} skills: {[s['skill'] for s in inferred]}")
            processed += 1
        else:
            errors += 1
    
    # Save to database
    print("\n💾 Saving to database...")
    save_enriched_skills(enriched_rows)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 LLM ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"   Jobs processed: {processed}")
    print(f"   Errors: {errors}")
    print(f"   Total skills inferred: {len(enriched_rows)}")
    print(f"   Finished: {datetime.now()}")
    
    # Show sample of inferred skills
    if enriched_rows:
        print("\n📈 SAMPLE OF INFERRED SKILLS:")
        sample_df = pd.DataFrame(enriched_rows[:20])
        print(sample_df[['skill', 'skill_type', 'confidence']].to_string(index=False))
    
    return len(enriched_rows)


if __name__ == "__main__":
    run_llm_enrichment()
