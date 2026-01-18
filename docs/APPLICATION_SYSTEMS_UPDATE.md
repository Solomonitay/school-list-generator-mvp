# Application Systems Update - Summary

## What Was Updated

Successfully added **Application System** designations (AMCAS, AACOMAS, TMDSAS) to all 202 medical schools in your database.

## Files Modified

### 1. `/Users/itaysolomon/medical_schools_data.csv`
- Added new column: **Application System**
- Values: AMCAS, AACOMAS, or TMDSAS

### 2. `/Users/itaysolomon/update_application_systems.py`
- New script to automatically assign application systems based on school type and location
- Can be re-run if needed to update data

### 3. `/Users/itaysolomon/example_api.py`
- Added `applicationSystem` field to API responses
- Added filtering by application system: `?app_system=TMDSAS`
- Updated API documentation

### 4. `/Users/itaysolomon/example_frontend.html`
- Added Application System filter dropdown
- Added color-coded badges for AMCAS, AACOMAS, TMDSAS
- Updated JavaScript to handle app system filtering

## Application System Distribution

```
AMCAS (MD programs):     145 schools (72%)
AACOMAS (DO programs):    44 schools (22%)
TMDSAS (Texas schools):   13 schools (6%)
─────────────────────────────────────────
Total:                   202 schools
```

## Application System Rules

### AMCAS (American Medical College Application Service)
- Used by: Most MD programs nationwide
- **Total: 145 schools**
- Includes: All non-Texas MD programs + TCU and UNTHSC in Texas

### AACOMAS (American Association of Colleges of Osteopathic Medicine)
- Used by: Most DO programs nationwide
- **Total: 44 schools**
- Includes: All DO programs except Sam Houston State and UNT in Texas
- Exception: University of the Incarnate Word (TX) uses AACOMAS

### TMDSAS (Texas Medical and Dental Schools Application Service)
- Used by: 13 Texas medical schools (both MD and DO)
- **Total: 13 schools**
- **Covers 87% of Texas medical schools**

## TMDSAS Schools List

### MD Programs (11 schools):
1. Baylor College of Medicine
2. Texas A&M Health Science Center College of Medicine
3. Texas Tech University Health Sciences Center Paul L. Foster School of Medicine
4. Texas Tech University Health Sciences Center School of Medicine – Lubbock
5. University of Houston Tilman J. Fertitta Family College of Medicine
6. University of Texas at Austin Dell Medical School
7. University of Texas Medical Branch School of Medicine
8. University of Texas McGovern Medical School at Houston
9. University of Texas Rio Grande Valley School of Medicine
10. University of Texas School of Medicine at San Antonio
11. University of Texas Southwestern Medical School

### DO Programs (2 schools):
1. Sam Houston State University College of Osteopathic Medicine
2. University of North Texas Health Science Center at Fort Worth Texas College of Osteopathic Medicine

### Texas Exceptions (NOT using TMDSAS):
- **TCU and UNTHSC School of Medicine** - Uses AMCAS (MD program)
- **University of the Incarnate Word School of Osteopathic Medicine** - Uses AACOMAS (DO program)

## Updated CSV Structure

```csv
Medical School Name,State,Degree Type,Average GPA,Average MCAT,Minimum MCAT Notes,Public School Status,Application System
Baylor College of Medicine,TX,MD,3.91,518,NR,Private,TMDSAS
University of Alabama School of Medicine,AL,MD,3.83,509,494,Public,AMCAS
Alabama College of Osteopathic Medicine,AL,DO,3.45,503,NR,Private,AACOMAS
```

## API Usage Examples

### Filter by TMDSAS schools
```bash
curl "http://localhost:5000/api/schools?app_system=TMDSAS"
```

### Filter by AACOMAS (DO programs)
```bash
curl "http://localhost:5000/api/schools?app_system=AACOMAS"
```

### Filter by AMCAS schools in California with high GPA
```bash
curl "http://localhost:5000/api/schools?app_system=AMCAS&state=CA&min_gpa=3.8"
```

### Get all Texas schools (mix of TMDSAS, AMCAS, AACOMAS)
```bash
curl "http://localhost:5000/api/schools?state=TX"
```

## Frontend Features

The updated frontend now includes:

1. **Application System Filter Dropdown**
   - Filter by AMCAS, AACOMAS, or TMDSAS
   - Color-coded badges on each school card

2. **Badge Colors**
   - **AMCAS**: Blue (most MD programs)
   - **AACOMAS**: Purple (DO programs)
   - **TMDSAS**: Gold/Yellow (Texas schools)

3. **Combined Filtering**
   - Filter by multiple criteria simultaneously
   - Example: "Show me all TMDSAS schools with GPA > 3.8"

## Why This Matters for Medical School Applicants

### Application Strategy
- **AMCAS**: Single application for multiple MD programs (most common)
- **AACOMAS**: Separate application for DO programs
- **TMDSAS**: Texas residents can apply to 13 schools with one application

### Cost Savings
- TMDSAS schools may have lower application fees for Texas residents
- Understanding which system to use helps plan application budget

### Timeline Differences
- Each system has different deadlines and processing times
- TMDSAS opens earlier (May) vs AMCAS (June)

### Texas Applicants
- Can use TMDSAS for 13 schools + AMCAS/AACOMAS for others
- Most Texas public schools strongly prefer in-state applicants

## Re-running the Update Script

If you need to update the application systems in the future:

```bash
cd /Users/itaysolomon
python3 update_application_systems.py
```

The script will:
1. Read the existing CSV
2. Apply application system logic
3. Overwrite the CSV with updated data
4. Display a summary

## Database Schema Update

If importing to a database, update your schema:

```sql
ALTER TABLE medical_schools
ADD COLUMN application_system VARCHAR(10);

CREATE INDEX idx_application_system
ON medical_schools(application_system);
```

## Next Steps

Your database now includes:
- ✓ School names
- ✓ State locations
- ✓ Degree types (MD/DO)
- ✓ GPA/MCAT statistics
- ✓ Public/Private status
- ✓ Application systems

**Coming next:** MD/PhD program information

---

**Data Source:** https://www.shemmassianconsulting.com/blog/tmdsas
**Last Updated:** January 10, 2026
