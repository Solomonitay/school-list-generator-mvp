# Getting Started with Medical School Database

## Quick Start Guide

### Files Created

```
/Users/itaysolomon/
├── medical_schools_data.csv          # The scraped data (202 schools)
├── scrape_medical_schools.py         # Web scraper script
├── example_api.py                    # Flask REST API example
├── example_frontend.html             # HTML/JavaScript frontend example
├── MEDICAL_SCHOOLS_README.md         # Detailed documentation
├── GETTING_STARTED.md                # This file
└── medical_scraper_env/              # Python virtual environment
```

## Step 1: View the Data

The CSV file is ready to use! You can:

### Open in Excel/Google Sheets
```bash
open medical_schools_data.csv
```

### View in Terminal
```bash
# View first 10 rows
head medical_schools_data.csv

# View last 10 rows
tail medical_schools_data.csv

# Search for specific schools
grep "California" medical_schools_data.csv
```

### Import into a Database

#### SQLite (Easiest)
```bash
sqlite3 medical_schools.db
.mode csv
.import medical_schools_data.csv medical_schools
.headers on
.mode column
SELECT * FROM medical_schools LIMIT 5;
```

#### PostgreSQL
```sql
CREATE TABLE medical_schools (
    id SERIAL PRIMARY KEY,
    school_name VARCHAR(255),
    state VARCHAR(2),
    degree_type VARCHAR(2),
    avg_gpa VARCHAR(20),
    avg_mcat VARCHAR(20),
    min_mcat_notes TEXT,
    public_school_status VARCHAR(10)
);

COPY medical_schools(school_name, state, degree_type, avg_gpa, avg_mcat, min_mcat_notes, public_school_status)
FROM '/path/to/medical_schools_data.csv'
DELIMITER ','
CSV HEADER;
```

## Step 2: Try the Example API

### Install Dependencies
```bash
# Activate virtual environment
source medical_scraper_env/bin/activate

# Install Flask
pip install flask flask-cors
```

### Run the API Server
```bash
python3 example_api.py
```

You should see:
```
Medical Schools API Server
============================================================
Total schools loaded: 202

API Endpoints:
  http://localhost:5000/
  http://localhost:5000/api/schools
  http://localhost:5000/api/schools?state=CA
  http://localhost:5000/api/schools?degree=MD
  http://localhost:5000/api/states
  http://localhost:5000/api/stats
============================================================

Starting server on http://localhost:5000
```

### Test the API

Open a new terminal and try these commands:

```bash
# Get all schools
curl http://localhost:5000/api/schools

# Get schools in California
curl http://localhost:5000/api/schools?state=CA

# Get MD programs only
curl http://localhost:5000/api/schools?degree=MD

# Get public schools with GPA >= 3.8
curl "http://localhost:5000/api/schools?public=true&min_gpa=3.8"

# Get statistics
curl http://localhost:5000/api/stats

# Get list of states
curl http://localhost:5000/api/states
```

## Step 3: Try the Example Frontend

With the API still running, open the frontend:

```bash
open example_frontend.html
```

Or if you're on Linux:
```bash
xdg-open example_frontend.html
```

The frontend provides:
- ✓ Search and filter by state, degree type, public/private
- ✓ Filter by minimum GPA and MCAT scores
- ✓ Beautiful, responsive design
- ✓ Real-time statistics
- ✓ Interactive school cards

## Step 4: Update the Data

To fetch fresh data from the website:

```bash
# Activate virtual environment
source medical_scraper_env/bin/activate

# Run the scraper
python3 scrape_medical_schools.py
```

This will overwrite `medical_schools_data.csv` with updated data.

## Building Your Web App

### Recommended Tech Stacks

#### Option 1: React + Node.js
```bash
# Frontend
npx create-react-app medical-schools-app
cd medical-schools-app

# Install axios for API calls
npm install axios

# Use the example_api.py as your backend
# or create a Node.js/Express backend
```

#### Option 2: Next.js (Full-stack)
```bash
npx create-next-app@latest medical-schools-app
cd medical-schools-app

# Import CSV directly or use the Flask API
```

#### Option 3: Python Full-stack (Flask + Jinja2)
```bash
# Use Flask for both backend and frontend
# Extend example_api.py to serve HTML templates
```

#### Option 4: Django
```bash
django-admin startproject medical_schools
cd medical_schools
python manage.py startapp schools

# Import CSV data using Django ORM
```

### Key Features to Implement

1. **Search & Filter**
   - By state, degree type, GPA range, MCAT range
   - Public vs private schools
   - Full-text search on school names

2. **School Comparison**
   - Side-by-side comparison tool
   - Compare up to 4 schools at once

3. **Admission Chances Calculator**
   - User inputs their GPA and MCAT
   - Calculate probability of admission
   - Categorize schools as "Reach", "Target", "Safety"

4. **Data Visualization**
   - Charts showing GPA/MCAT distributions
   - Interactive map of schools by state
   - MD vs DO comparisons

5. **User Accounts** (Future)
   - Save favorite schools
   - Track application status
   - Set reminders for deadlines

6. **Additional Data** (Expand the database)
   - Tuition costs
   - Acceptance rates
   - Class size
   - Location details
   - Application deadlines
   - School websites
   - Contact information

### Database Schema Suggestions

```sql
-- Main schools table (already have this data)
CREATE TABLE schools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL,
    degree_type VARCHAR(2) NOT NULL,
    avg_gpa DECIMAL(3,2),
    avg_mcat INT,
    min_mcat_notes TEXT,
    is_public BOOLEAN
);

-- Additional tables you might add
CREATE TABLE school_details (
    school_id INT REFERENCES schools(id),
    city VARCHAR(100),
    tuition_in_state DECIMAL(10,2),
    tuition_out_state DECIMAL(10,2),
    acceptance_rate DECIMAL(5,2),
    class_size INT,
    website VARCHAR(255),
    application_deadline DATE
);

CREATE TABLE user_favorites (
    user_id INT,
    school_id INT REFERENCES schools(id),
    notes TEXT,
    created_at TIMESTAMP
);

CREATE TABLE applications (
    user_id INT,
    school_id INT REFERENCES schools(id),
    status VARCHAR(50),
    applied_date DATE,
    interview_date DATE,
    decision_date DATE
);
```

## API Endpoints Reference

### GET /api/schools
Returns all schools with optional filtering.

**Query Parameters:**
- `state` - Filter by state code (e.g., CA, NY)
- `degree` - Filter by degree type (MD or DO)
- `public` - Filter by public status (true/false)
- `min_gpa` - Minimum GPA threshold
- `max_gpa` - Maximum GPA threshold
- `min_mcat` - Minimum MCAT threshold
- `max_mcat` - Maximum MCAT threshold

**Example Response:**
```json
{
  "count": 10,
  "data": [
    {
      "id": 1,
      "name": "University of Alabama School of Medicine",
      "state": "AL",
      "degreeType": "MD",
      "avgGPA": "3.83",
      "avgMCAT": "509",
      "minMCATNotes": "494",
      "isPublic": true
    }
  ]
}
```

### GET /api/schools/:id
Returns a specific school by ID.

### GET /api/states
Returns list of all states with school counts.

### GET /api/stats
Returns summary statistics across all schools.

## Common Issues & Solutions

### Issue: "Failed to load data" in frontend
**Solution:** Make sure the Flask API is running on http://localhost:5000

### Issue: CORS errors in browser
**Solution:** The example_api.py includes flask-cors. Make sure it's installed:
```bash
pip install flask-cors
```

### Issue: Port 5000 already in use
**Solution:** Change the port in example_api.py:
```python
app.run(debug=True, port=5001)  # Use port 5001 instead
```
And update the API_BASE_URL in example_frontend.html

### Issue: CSV encoding errors
**Solution:** The scraper uses UTF-8 encoding. If you see weird characters, make sure your editor/viewer supports UTF-8.

## Next Steps

1. **Enhance the Scraper**
   - Add error handling for network issues
   - Schedule automatic updates (cron job)
   - Email notifications when data changes

2. **Improve the API**
   - Add pagination for large result sets
   - Implement caching for better performance
   - Add authentication if needed
   - Create more complex search queries

3. **Build the Frontend**
   - Use React, Vue, or Angular for a modern SPA
   - Add charts using Chart.js or D3.js
   - Implement responsive design for mobile
   - Add dark mode

4. **Deploy to Production**
   - **Backend:** Heroku, AWS, DigitalOcean, Render
   - **Database:** PostgreSQL, MongoDB Atlas
   - **Frontend:** Vercel, Netlify, GitHub Pages

## Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **React Documentation:** https://react.dev/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **Chart.js:** https://www.chartjs.org/
- **Tailwind CSS:** https://tailwindcss.com/ (for styling)

## Support

If you need to re-scrape the data or make changes:

1. Modify `scrape_medical_schools.py` as needed
2. Run the scraper again to regenerate the CSV
3. Restart the API server to load new data

## License & Attribution

Data source: https://www.shemmassianconsulting.com/blog/average-gpa-and-mcat-score-for-every-medical-school

Please respect the original data source and comply with their terms of use when building your application.

---

**Happy coding!** 🚀

If you have questions or need help with specific features, feel free to ask!
