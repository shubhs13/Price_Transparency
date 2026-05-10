# ClearCare Data Initiative
### Hospital Price Transparency Analytics Pipeline
 
A data engineering and analytics project that ingests, normalizes, and analyzes publicly available hospital pricing data across two major U.S. metropolitan areas — enabling consumers to compare procedure costs across hospitals and insurance providers.
 
---
## Project Overview
 
Hospital pricing in the U.S. is notoriously opaque. Federal price transparency regulations require hospitals to publish standard charge files, but these files vary wildly in format, structure, and completeness — making meaningful comparison nearly impossible for the average consumer.
 
The ClearCare Data Initiative solves this by:
- Collecting raw charge files (CSV, JSON, XLSX) from 37 hospitals across two metro areas
- Cleaning, normalizing, and loading them into a structured PostgreSQL database
- Delivering a self-service Power BI / Tableau dashboard enabling non-technical users to compare procedure costs by CPT code, hospital, insurance provider, and plan
**Focus areas:** New York–Newark–Jersey City MSA (NY/NJ/PA) vs. Austin–Round Rock–Georgetown MSA (TX)
 
---
 
## Data Sources
 
**New York MSA — 16 hospitals including:**
- New York-Presbyterian Health System (7 locations)
- Newark Beth Israel Medical Center
- Jersey City Medical Center
- Saint Michael's Medical Center
- University Hospital
- Wayne Memorial Hospital
**Austin MSA — 15+ hospitals including:**
- Ascension Seton Health System (8 locations)
- Baylor Scott & White Medical Center – Round Rock
- St. David's Medical Center (4 locations)
- Heart Hospital of Austin
- Dell Children's Medical Center
All data sourced from official hospital websites in compliance with CMS price transparency regulations.
 
---
 
## Database Schema
 
```
hospitals         → hospital_PK, hospital, metroplex, state, zip_code
procedures        → procedure_id, description, billing_code
billing_codes     → billing_code
payers            → payer_name, plan_name, payer_plan_combo_id
charges           → procedure_id, hospital_PK, payer_plan_combo_id,
                    gross_charge, insurer_price, max_price,
                    discounted_cash, additional_generic_notes
```
 
**Primary key on charges:** `(procedure_id, hospital_PK, payer_plan_combo_id)`
 
Only CPT codes (5-digit) were retained for consistency. Other code types (HCPCS, CDM, MS-DRG) were excluded.
 
---
 
## Tech Stack
 
| Layer | Tools |
|---|---|
| Data Collection | Manual download + Python scripts |
| Data Cleaning & Transformation | Python (Pandas — `json_normalize`, `melt`, custom transforms) |
| Development Environment | VS Code, Google Colab |
| Database | PostgreSQL hosted on Railway (cloud) |
| File Coordination | OneDrive |
| Visualization | Power BI, Tableau |
 
---
 
## Pipeline Architecture
 
```
Raw Hospital Files (CSV / JSON / XLSX)
        ↓
Python Cleaning Scripts (VS Code + Google Colab)
  - Standardize column names
  - Normalize JSON → CSV via json_normalize()
  - Handle missing values (max_price used to impute insurer_price)
  - Filter to CPT codes only
  - Remove dummy values ($999,999) and majority-blank rows
        ↓
Normalized CSV Files (12-column schema)
        ↓
PostgreSQL Database (Railway — cloud hosted)
        ↓
Power BI / Tableau Dashboard (self-service)
```
 
---
 
## Key Findings
 
**Pricing discrepancies (across ~8.7M records):**
- **40%+ of records:** Cash-paying patients charged *less* than insurer negotiated price
- **19%+ of records:** Cash-paying patients charged *more* than insurer price — disproportionately affecting uninsured patients
- **~35% of records:** Minimal discrepancy between cash and insurer pricing
**Extreme price variance for identical CPT codes:**
- CPT `#42100` (biopsy of palate/uvula): prices ranged from negligible to thousands of dollars across hospitals for the same procedure — driven by setting (OR vs. outpatient clinic), cost bundling, hospital type, and market dynamics
**Most expensive procedures (Ascension Seton Austin):**
- `93653` — Cardiac electrophysiology mapping (SVT treatment)
- `93656` — Atrial fibrillation ablation
- `93654` — Ventricular tachycardia ablation
**Market comparison:**
- NY metro ranks in the top 1% nationally for CMS price transparency compliance
- ~75% of Texas hospitals are compliant or mostly compliant; Austin market is less centralized and harder to compare
---
 
## Data Collected
 
| Hospital | CPT Code Records |
|---|---|
| NY-Presbyterian System | 7,583,368 |
| Newark Wayne Community Hospital | 4,374,058 |
| Saint Michael Medical Centre | 2,774,442 |
| Ascension Seton Williamson | 2,248,576 |
| St. David's Round Rock | 1,957,431 |
| Ascension Seton Medical Centre | 1,048,573 |
| Ascension Seton Northwest | 1,048,573 |
| Baylor Scott & White | 1,043,337 |
| Jersey City Medical Centre | 88,791 |
| NY-Presbyterian Queens | 120,144 |
| Newark Beth Medical Centre | 108,533 |
| University Hospital | 101,968 |
| Wayne Memorial Hospital | 52,227 |
| Saint Joseph's Medical Centre | 42,674 |
| Heart Hospital of Austin | 1,048,575 |
| Dell Children's Medical Centre | 1,048,573 |
| St. David's North Austin | 87,941 |
| Ascension Seton Shoal Creek | 2 |
 
**Raw file formats ingested:** 77.8% vertical CSV · 16.7% JSON · 5.6% horizontal CSV
 
---
 
## Challenges & Solutions
 
**1. Format inconsistency (JSON vs. CSV)**
JSON is hierarchical; CSV is flat. Used Pandas `json_normalize()` to convert all JSON source files to a consistent CSV structure before processing.
 
**2. File size**
Several source files exceeded 1GB with majority-blank fields or dummy pricing rows (`$999,999`). Files were split before cleaning; hospitals with insufficient data quality were replaced.
 
**3. Hospital-specific schema variations**
Some hospitals used a separate column per insurance company rather than a payer column. Others used inconsistent billing code naming. Custom Pandas transformation scripts were written per hospital type.
 
**4. Missing insurer prices**
Where `insurer_price` was null, `max_price` was used as an imputation proxy to preserve record completeness.
 
---
 
## Team
 
· Shubham Pathare · Tin Trung Diep · Yingzhe Geng · Raquel Guerra · Samin Khan · Aye Chan Moe · Rohit Narayanan · Xiaowen Shang
 
*BUAN 6390.001 — University of Texas at Dallas, Spring 2025*
