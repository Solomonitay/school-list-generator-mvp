# Medical School Data Scraper - Project Summary

## Overview
Successfully scraped and organized medical school admission statistics from Shemmassian Consulting into a structured CSV database.

## Files Generated

### 1. `medical_schools_data.csv`
- **Format**: CSV (Comma-Separated Values)
- **Size**: 16 KB
- **Records**: 202 medical schools (+ 1 header row)
- **Encoding**: UTF-8

### 2. `scrape_medical_schools.py`
- Python script to scrape and process the data
- Can be re-run to fetch updated data from the website
- Uses BeautifulSoup for HTML parsing

## CSV Structure

The CSV contains 7 columns:

| Column Name | Description | Example Values |
|------------|-------------|----------------|
| **Medical School Name** | Full name of the institution (asterisks removed) | "University of Alabama School of Medicine" |
| **State** | Two-letter state abbreviation | AL, CA, TX, NY |
| **Degree Type** | Type of medical degree offered | MD, DO |
| **Average GPA** | Average GPA of accepted students | 3.83, 3.5+, 3.0 |
| **Average MCAT** | Average MCAT score of accepted students | 509, 521, NR |
| **Minimum MCAT Notes** | Minimum MCAT requirements with context | "494", "NR", "For out-of-state applicants only: 70th percentile (~507.5)" |
| **Public School Status** | Whether the school is public or private | Public, Private |

## Data Summary

### Statistics
- **Total Schools**: 202
- **MD Programs**: 156 (77%)
- **DO Programs**: 46 (23%)
- **Public Schools**: 99 (49%)
- **Private Schools**: 103 (51%)

### States Covered
All 50 U.S. states plus Puerto Rico

### GPA Range
- Highest: 3.98 (NYU Grossman School of Medicine)
- Lowest: 3.0 (Kansas College of Osteopathic Medicine)

### MCAT Range
- Highest: 523 (NYU Grossman School of Medicine)
- Lowest: 499 (several schools)

## Key Features

### ✓ Asterisk Parsing
- Schools marked with asterisks (*) on the original website are identified as public schools
- Asterisks are removed from school names and recorded in the "Public School Status" column

### ✓ Special Notation Handling
The scraper correctly handles:
- **NR**: Not Reported
- **OOS**: Out-of-state requirements
- **IS**: In-state requirements
- **^**: Out-of-state indicators
- **Ranges**: e.g., "3.5+", "500+", "3.0–3.7"
- **Complex notes**: Percentile requirements, conditional minimums

## Using the Data

### For Database Import
The CSV can be directly imported into:
- **PostgreSQL**: `COPY medical_schools FROM '/path/to/file.csv' WITH CSV HEADER;`
- **MySQL**: `LOAD DATA INFILE '/path/to/file.csv' INTO TABLE medical_schools FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;`
- **SQLite**: `.mode csv` then `.import medical_schools_data.csv medical_schools`
- **MongoDB**: Use mongoimport with `--type csv --headerline`

### For Web Applications
The structured format is ready for:
- RESTful APIs
- GraphQL endpoints
- React/Vue/Angular data tables
- Search and filter functionality
- Data visualization dashboards

### Sample SQL Schema
```sql
CREATE TABLE medical_schools (
    id SERIAL PRIMARY KEY,
    school_name VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL,
    degree_type VARCHAR(2) NOT NULL,
    avg_gpa VARCHAR(20),
    avg_mcat VARCHAR(20),
    min_mcat_notes TEXT,
    public_school_status VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_state ON medical_schools(state);
CREATE INDEX idx_degree_type ON medical_schools(degree_type);
CREATE INDEX idx_public_status ON medical_schools(public_school_status);
```

## Re-running the Scraper

To fetch fresh data from the website:

```bash
# Activate the virtual environment
source medical_scraper_env/bin/activate

# Run the scraper
python3 scrape_medical_schools.py

# The CSV will be overwritten with updated data
```

## Data Considerations

### Important Notes
1. **"NR" Values**: "Not Reported" means the school didn't provide this information
2. **Range Values**: Some schools report ranges (e.g., "3.5+", "509–528")
3. **Conditional Requirements**: Some minimum MCAT notes include conditions (OOS vs IS)
4. **Data Source**: Data is from the 2025 admission cycle per Shemmassian Consulting
5. **Accuracy**: The website notes discrepancies may exist between school websites and MSAR databases

### Data Quality
- All 202 schools successfully scraped
- No duplicate entries
- Clean formatting (whitespace/newlines removed)
- Consistent column structure

## Next Steps for Your Web App

### Recommended Features
1. **Search & Filter**
   - By state, degree type, GPA range, MCAT range
   - Public vs private schools

2. **Comparison Tool**
   - Side-by-side comparison of multiple schools
   - Calculate admission chances based on user's stats

3. **Sorting**
   - By GPA, MCAT, alphabetically, by state

4. **Data Visualization**
   - Charts showing GPA/MCAT distributions
   - Maps showing schools by state
   - MD vs DO program comparisons

5. **Additional Data Fields** (you may want to add)
   - Tuition costs
   - Acceptance rates
   - Class size
   - Location (city)
   - Website URLs
   - Application deadlines

## Technical Requirements

### Python Dependencies
- `requests >= 2.32.5`
- `beautifulsoup4 >= 4.14.3`

### Installation
```bash
pip install requests beautifulsoup4
```

## Source
Data scraped from: https://www.shemmassianconsulting.com/blog/average-gpa-and-mcat-score-for-every-medical-school

---

**Last Updated**: January 10, 2026
**Data Cycle**: 2025 Admissions
