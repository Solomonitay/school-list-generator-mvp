# Medical School Classification System

## Overview

A comprehensive system to categorize medical schools as **Reach**, **Target**, or **Undershoot** based on applicant statistics, following Shemmassian Consulting's proven methodology.

---

## Classification Rules

### GPA-Based Classification

Compare your GPA against the school's entering class average:

| Your GPA vs School Average | Classification | Example |
|---------------------------|----------------|---------|
| **+0.2 or higher** | Undershoot | You: 3.9, School: 3.7 |
| **Within ±0.1** | Target | You: 3.75, School: 3.8 |
| **-0.2 or lower** | Reach | You: 3.6, School: 3.8 |

**Formula:**
```python
diff = your_gpa - school_avg_gpa

if diff >= 0.2:
    return 'Undershoot'
elif abs(diff) <= 0.1:
    return 'Target'
elif diff <= -0.2:
    return 'Reach'
```

### MCAT-Based Classification

Compare your MCAT against the school's entering class average:

| Your MCAT vs School Average | Classification | Example |
|----------------------------|----------------|---------|
| **+3 or higher** | Undershoot | You: 516, School: 512 |
| **Within ±2** | Target | You: 510, School: 512 |
| **-3 or lower** | Reach | You: 507, School: 512 |

**Formula:**
```python
diff = your_mcat - school_avg_mcat

if diff >= 3:
    return 'Undershoot'
elif abs(diff) <= 2:
    return 'Target'
elif diff <= -3:
    return 'Reach'
```

---

## Overall School Classification

Combine GPA and MCAT classifications using these rules:

### Rule Matrix

| GPA Class | MCAT Class | Overall Result | Logic |
|-----------|------------|----------------|-------|
| Reach | Reach | **Reach** | Both metrics indicate reach |
| Target | Target | **Target** | Both metrics indicate target |
| Undershoot | Undershoot | **Undershoot** | Both metrics indicate undershoot |
| Reach | Undershoot | **Target** | Mixed signals balance out |
| Undershoot | Reach | **Target** | Mixed signals balance out |
| Target | Reach | **Reach** | Conservative (take the weaker) |
| Target | Undershoot | **Undershoot** | Take the stronger position |
| Reach | Target | **Reach** | Conservative (take the weaker) |
| Undershoot | Target | **Undershoot** | Take the stronger position |

### Special Override Rule

**Critical Exception:** If your GPA or MCAT falls below a school's 10th percentile (or stated minimum), classify that school as **Reach** regardless of your other strengths.

```python
if user_mcat < school_minimum_mcat:
    return 'Reach'  # Override all other classifications
```

---

## Example Classifications

### Example 1: Strong Applicant
**Stats:** GPA 3.9, MCAT 518

| School | School Avg | Your Diff | GPA Class | MCAT Class | Overall |
|--------|-----------|-----------|-----------|------------|---------|
| Stanford (3.89, 519) | 3.89/519 | +0.01/-1 | Target | Target | **Target** |
| UCLA (3.81, 516) | 3.81/516 | +0.09/+2 | Target | Target | **Target** |
| Michigan State (3.7, 507) | 3.7/507 | +0.20/+11 | Undershoot | Undershoot | **Undershoot** |

### Example 2: Average Applicant
**Stats:** GPA 3.6, MCAT 508

| School | School Avg | Your Diff | GPA Class | MCAT Class | Overall |
|--------|-----------|-----------|-----------|------------|---------|
| Harvard (3.9, 520) | 3.9/520 | -0.30/-12 | Reach | Reach | **Reach** |
| Cincinnati (3.78, 512) | 3.78/512 | -0.18/-4 | Reach | Reach | **Reach** |
| Mississippi (3.77, 505) | 3.77/505 | -0.17/+3 | Reach | Undershoot | **Target** |
| Meharry (3.46, 503) | 3.46/503 | +0.14/+5 | Target | Undershoot | **Undershoot** |

### Example 3: DO Program Applicant
**Stats:** GPA 3.4, MCAT 502

| School | School Avg | Your Diff | GPA Class | MCAT Class | Overall |
|--------|-----------|-----------|-----------|------------|---------|
| PCOM (3.5, 505) | 3.5/505 | -0.10/-3 | Target | Reach | **Reach** |
| LECOM (3.41, 503) | 3.41/503 | -0.01/-1 | Target | Target | **Target** |
| ACOM (3.45, 503) | 3.45/503 | -0.05/-1 | Target | Target | **Target** |

---

## Additional Considerations

### In-State vs Out-of-State

**Public Schools:**
- Heavily favor in-state applicants (often 75%+ of class)
- Out-of-state applicants face much higher bars
- **Recommendation:** Treat out-of-state public schools one tier higher (Target → Reach)

**Private Schools:**
- More geographic diversity
- Less in-state preference
- Classification stays the same

### Cost Considerations

| School Type | In-State | Out-of-State | Private |
|------------|----------|--------------|---------|
| **Annual Cost** | ~$51,000 | ~$64,000 | ~$73,000 |
| **4-Year Total** | ~$204,000 | ~$256,000 | ~$292,000 |

### MD/PhD Programs

MD/PhD programs are typically:
- More competitive than MD-only
- Fully funded (tuition + stipend)
- Require strong research background

**Recommendation:** Treat MD/PhD programs one tier higher (Target → Reach)

---

## Application Strategy

### Recommended School Distribution

Based on Shemmassian Consulting guidance:

| Category | Number of Schools | Purpose |
|----------|------------------|---------|
| **Reach** | 3-5 schools | Ambitious targets, competitive |
| **Target** | 7-10 schools | Best fit, realistic chances |
| **Undershoot** | 5-7 schools | Safety net, high acceptance probability |
| **Total** | 15-22 schools | Balanced application list |

### Building Your List

#### Step 1: Calculate Your Baseline
```python
# Example
your_gpa = 3.75
your_mcat = 512
your_state = 'CA'
```

#### Step 2: Classify All Schools
Run the classifier:
```bash
python3 school_classifier.py 3.75 512 CA
```

#### Step 3: Select Schools

**From Reach Category:**
- Choose 3-5 schools you'd be thrilled to attend
- Include top-tier programs in your specialty interest
- Consider geographic preferences

**From Target Category:**
- Choose 7-10 schools where you have realistic chances
- Prioritize in-state public schools (if applicable)
- Consider mission fit and location

**From Undershoot Category:**
- Choose 5-7 schools where you're above average
- Include at least 2 in-state public options (if available)
- Ensure you'd be happy attending

#### Step 4: Adjust for Special Factors
- **Mission fit:** Some schools prefer specific backgrounds
- **Research focus:** If you want research, prioritize MD/PhD programs
- **Location:** Consider where you want to practice
- **Curriculum:** Traditional vs problem-based learning
- **Cost:** Factor in tuition and living expenses

---

## Using the Classifier

### Command Line Usage

```bash
# Basic usage
python3 school_classifier.py [GPA] [MCAT] [STATE]

# Examples
python3 school_classifier.py 3.8 515 NY
python3 school_classifier.py 3.6 508 TX
python3 school_classifier.py 3.9 520 CA
```

### Python Integration

```python
from school_classifier import SchoolClassifier, generate_application_list

# Create classifier
classifier = SchoolClassifier()

# Generate application list
results = generate_application_list(
    user_gpa=3.75,
    user_mcat=512,
    csv_path='medical_schools_data.csv',
    user_state='CA'
)

# Access results
print(f"Reach schools: {results['summary']['reach_count']}")
print(f"Target schools: {results['summary']['target_count']}")
print(f"Undershoot schools: {results['summary']['undershoot_count']}")

# Get specific schools
reach_schools = results['schools']['reach']
for school in reach_schools[:5]:
    print(school['school_name'])
```

### API Integration (Coming Soon)

```bash
# Get classifications for your stats
curl "http://localhost:5000/api/classify?gpa=3.75&mcat=512&state=CA"

# Response
{
  "user_stats": { "gpa": 3.75, "mcat": 512, "state": "CA" },
  "summary": {
    "reach_count": 44,
    "target_count": 65,
    "undershoot_count": 86
  },
  "schools": { ... }
}
```

---

## Classification Examples by Percentile

### Top 10% Applicant (GPA 3.9+, MCAT 520+)

**Realistic Targets:**
- Harvard Medical School
- Johns Hopkins
- Stanford
- UCSF
- Penn

**Even These Can Be Reach:**
- Competition is extremely fierce
- Holistic review matters
- Research, leadership, clinical experience crucial

### 75th Percentile (GPA 3.8, MCAT 515)

**Reach:** Top 20 schools
**Target:** Top 50 schools, strong state schools
**Undershoot:** Mid-tier MD, top DO programs

### 50th Percentile (GPA 3.7, MCAT 510)

**Reach:** Top 50 schools
**Target:** Mid-tier MD, state schools
**Undershoot:** Regional MD, many DO programs

### 25th Percentile (GPA 3.5, MCAT 505)

**Reach:** Most MD programs
**Target:** Some MD programs, strong DO programs
**Undershoot:** Many DO programs, Caribbean (not recommended)

---

## Red Flags & Automatic Reaches

Classify as **Reach** regardless of overall stats if:

1. **Below minimum threshold**
   - GPA or MCAT below school's 10th percentile
   - Below stated minimum requirements

2. **Out-of-state at highly competitive public schools**
   - Example: UC schools for non-CA residents
   - State schools with <5% OOS acceptance

3. **Mission mismatch**
   - Primary care focus schools vs research focus
   - Service-oriented schools vs academic goals

4. **Special program requirements**
   - MD/PhD without research experience
   - HBCU without demonstrated commitment to underserved

---

## Success Tips

### 1. Apply Broadly
- Don't just apply to reaches
- Balanced list is key to acceptance

### 2. Know Your Numbers
- Calculate your classifications early
- Adjust expectations realistically

### 3. Consider Holistic Factors
- Stats aren't everything
- Strong essays, experiences, letters matter

### 4. Apply Early
- Complete primary applications in June/July
- Submit secondaries within 2 weeks
- Early applicants have higher acceptance rates

### 5. Stay Flexible
- Be willing to move for medical school
- Consider DO programs seriously
- Geography shouldn't limit your education

---

## Common Mistakes to Avoid

### ❌ Only Applying to Reaches
**Problem:** Low acceptance probability
**Solution:** Include 7-10 targets and 5-7 undershoots

### ❌ Overestimating Out-of-State Chances
**Problem:** Public schools heavily favor in-state
**Solution:** Treat OOS public schools as one tier higher

### ❌ Underestimating DO Programs
**Problem:** Missing good opportunities
**Solution:** DO = MD in terms of practice, consider both

### ❌ Not Applying Broadly Enough
**Problem:** Zero acceptances
**Solution:** Apply to 15-22 schools minimum

### ❌ Ignoring In-State Advantages
**Problem:** Missing highest probability schools
**Solution:** Apply to ALL in-state public schools

---

## Output Format

The classifier generates a JSON file with complete results:

```json
{
  "user_stats": {
    "gpa": 3.75,
    "mcat": 512,
    "state": "CA"
  },
  "summary": {
    "total_schools": 202,
    "reach_count": 44,
    "target_count": 65,
    "undershoot_count": 86
  },
  "schools": {
    "reach": [ ... ],
    "target": [ ... ],
    "undershoot": [ ... ]
  },
  "recommendations": {
    "reach": "3-5 schools",
    "target": "7-10 schools",
    "undershoot": "5-7 schools"
  }
}
```

---

## File Location

```
Classifier Script:
school-list-generator/scripts/school_classifier.py

Database:
school-list-generator/public/medical_schools_data.csv
school-list-generator/public/medical_schools_data_enhanced.csv

Output Files:
school-list-generator/output/school_classifications_GPA[X]_MCAT[Y].json
```

---

## References

- **Shemmassian Consulting:** "How Many Medical Schools Should I Apply To"
  - https://www.shemmassianconsulting.com/blog/how-many-medical-schools-should-i-apply-to
- **AAMC MSAR:** Medical School Admission Requirements
- **AACOMAS:** Osteopathic Medical College Information Book

---

## Summary

The classification system provides:

✅ **Objective categorization** based on proven methodology
✅ **Realistic expectations** for acceptance chances
✅ **Strategic guidance** for building application lists
✅ **Data-driven decisions** using comprehensive database
✅ **Personalized results** based on your specific stats

**Use this system to build a balanced, strategic medical school application list that maximizes your chances of acceptance!** 🎓🏥

---

**Last Updated:** January 10, 2026
**Based on:** 2025 admission cycle data
**Total Schools:** 202 U.S. medical schools
