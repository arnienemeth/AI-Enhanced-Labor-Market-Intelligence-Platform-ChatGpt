# 🗺️ Project Workflow & Architecture

## Pipeline Flow Diagram

```mermaid
flowchart TB
    subgraph Sources["📥 Data Sources"]
        A1[🌐 Adzuna API<br/>17,000+ jobs]
        A2[🏠 Remotive API<br/>25+ remote jobs]
        A3[📊 Future APIs<br/>LinkedIn, Indeed]
    end

    subgraph Ingestion["🐍 Data Ingestion"]
        B1[unified_job_loader_v2.py]
        B2[Rate Limiting]
        B3[Deduplication]
        B4[Sector Classification]
    end

    subgraph Extraction["🧠 Skill Extraction"]
        C1[📋 Rule-Based NLP<br/>150+ patterns<br/>27K skills]
        C2[🤖 GPT-4o-mini<br/>Context inference<br/>3.5K skills]
    end

    subgraph Storage["🗄️ Data Storage"]
        D1[(PostgreSQL<br/>v2_jobs<br/>18K records)]
        D2[(PostgreSQL<br/>v2_job_skills<br/>31K records)]
        D3[(PostgreSQL<br/>v2_skills_dictionary<br/>437 skills)]
    end

    subgraph Visualization["📊 Visualization"]
        E1[Power BI Dashboard]
        E2[Page 1: Executive Summary]
        E3[Page 2: Skills Analysis]
        E4[Page 3: Salary Insights]
        E5[Page 4: AI Insights]
    end

    subgraph Automation["☁️ Cloud Automation"]
        F1[AWS Lambda]
        F2[EventBridge<br/>Weekly Schedule]
        F3[S3 Data Lake]
        F4[CloudWatch Logs]
    end

    A1 --> B1
    A2 --> B1
    A3 -.-> B1
    
    B1 --> B2
    B2 --> B3
    B3 --> B4
    
    B4 --> D1
    D1 --> C1
    D1 --> C2
    
    C1 --> D2
    C2 --> D2
    
    D1 --> E1
    D2 --> E1
    D3 --> E1
    
    E1 --> E2
    E1 --> E3
    E1 --> E4
    E1 --> E5
    
    F2 --> F1
    F1 --> B1
    F1 --> F3
    F1 --> F4

    style Sources fill:#e1f5fe
    style Ingestion fill:#fff3e0
    style Extraction fill:#f3e5f5
    style Storage fill:#e8f5e9
    style Visualization fill:#fff8e1
    style Automation fill:#fce4ec
```

## Technology Stack Diagram

```mermaid
graph LR
    subgraph Frontend["📊 Frontend"]
        PBI[Power BI]
    end

    subgraph Backend["⚙️ Backend"]
        PY[Python 3.11]
        PD[Pandas]
        SA[SQLAlchemy]
        RQ[Requests]
    end

    subgraph AI["🤖 AI/ML"]
        OAI[OpenAI API]
        GPT[GPT-4o-mini]
        NLP[Rule-Based NLP]
    end

    subgraph Database["🗄️ Database"]
        PG[(PostgreSQL)]
    end

    subgraph Cloud["☁️ Cloud"]
        LAM[AWS Lambda]
        EB[EventBridge]
        S3[S3]
    end

    PY --> PD
    PY --> SA
    PY --> RQ
    PY --> OAI
    OAI --> GPT
    PY --> NLP
    SA --> PG
    PG --> PBI
    LAM --> PY
    EB --> LAM
    LAM --> S3

    style Frontend fill:#fff8e1
    style Backend fill:#e3f2fd
    style AI fill:#f3e5f5
    style Database fill:#e8f5e9
    style Cloud fill:#fce4ec
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant API as 🌐 Job APIs
    participant PY as 🐍 Python
    participant NLP as 📋 Rule-Based
    participant LLM as 🤖 GPT-4
    participant DB as 🗄️ PostgreSQL
    participant PBI as 📊 Power BI

    Note over API,PBI: Weekly Pipeline Execution
    
    PY->>API: Request jobs (Adzuna, Remotive)
    API-->>PY: Return 18,000+ jobs
    
    PY->>PY: Deduplicate & classify sectors
    PY->>DB: Store raw jobs (v2_jobs)
    
    PY->>NLP: Extract explicit skills
    NLP-->>PY: Return 27,000 skills
    PY->>DB: Store skills (v2_job_skills)
    
    PY->>LLM: Enrich with context
    LLM-->>PY: Return 3,500 inferred skills
    PY->>DB: Store LLM skills (v2_job_skills)
    
    PBI->>DB: Query all tables
    DB-->>PBI: Return data
    PBI->>PBI: Render 4-page dashboard
```

## Project Timeline

```mermaid
gantt
    title Project Development Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1: Foundation
    Database Setup           :done, p1a, 2024-12-28, 1d
    API Integration          :done, p1b, 2024-12-28, 1d
    Data Pipeline            :done, p1c, 2024-12-29, 1d
    
    section Phase 2: AI
    Rule-Based NLP           :done, p2a, 2024-12-29, 1d
    LLM Integration          :done, p2b, 2024-12-30, 1d
    Skill Extraction         :done, p2c, 2024-12-30, 1d
    
    section Phase 3: Visualization
    Power BI Setup           :done, p3a, 2024-12-30, 1d
    Dashboard Design         :done, p3b, 2024-12-30, 1d
    
    section Phase 4: Cloud
    AWS Lambda               :active, p4a, 2024-12-31, 3d
    Automation               :p4b, 2025-01-02, 2d
```

## Skills Extraction Comparison

```mermaid
pie title Skill Extraction Methods
    "Rule-Based (27K)" : 88
    "LLM Inferred (3.5K)" : 12
```

## Jobs by Sector

```mermaid
pie title Jobs Distribution by Sector
    "IT (62%)" : 62
    "Finance (38%)" : 38
```

## Salary Distribution

```mermaid
pie title Jobs by Salary Band
    "Mid (50-80K)" : 33
    "Senior (80-120K)" : 25
    "Junior (30-50K)" : 18
    "Lead (120-180K)" : 16
    "Executive (180K+)" : 8
```
