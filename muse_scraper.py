import requests
import pandas as pd
import time

BASE_URL = "https://www.themuse.com/api/public/jobs"

def scrape_muse_jobs(pages=5):
    all_jobs = []

    for page in range(0, pages):  # 🔥 page starts at 0
        params = {
            "page": page,
            "category": "Engineering"  # 🔥 THIS WORKS
        }

        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        print(f"Page {page}: {len(data.get('results', []))} jobs")

        for job in data.get("results", []):
            all_jobs.append({
                "job_id": job.get("id"),
                "job_title": job.get("name"),
                "company": job.get("company", {}).get("name"),
                "locations": ", ".join([loc["name"] for loc in job.get("locations", [])]),
                "levels": ", ".join([lvl["name"] for lvl in job.get("levels", [])]),
                "publication_date": job.get("publication_date"),
                "job_url": job.get("refs", {}).get("landing_page"),
                "job_description": job.get("contents"),
                "source": "the_muse"
            })

        time.sleep(1)

    return pd.DataFrame(all_jobs)


if __name__ == "__main__":
    df = scrape_muse_jobs(pages=5)

    print(df.head())
    print("Total jobs scraped:", len(df))

    df.to_csv("muse_jobs.csv", index=False)
