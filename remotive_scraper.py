import requests
import pandas as pd

URL = "https://remotive.com/api/remote-jobs"

def scrape_remotive():
    response = requests.get(URL, timeout=15)
    response.raise_for_status()

    data = response.json()
    jobs = data.get("jobs", [])

    records = []
    for job in jobs:
        records.append({
            "job_id": job.get("id"),
            "job_title": job.get("title"),
            "company": job.get("company_name"),
            "category": job.get("category"),
            "job_type": job.get("job_type"),
            "candidate_location": job.get("candidate_required_location"),
            "publication_date": job.get("publication_date"),
            "job_url": job.get("url"),
            "tags": ", ".join(job.get("tags", [])),
            "job_description": job.get("description"),
            "source": "remotive"
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    df = scrape_remotive()
    print(df.head())
    print("Total jobs scraped:", len(df))
    df.to_csv("remotive_jobs.csv", index=False)
