#!/usr/bin/env python3
"""
Example Flask API for Medical Schools Data
A simple REST API to serve the medical school data for your web application.

Usage:
    pip install flask flask-cors
    python3 example_api.py

    Then access:
    - http://localhost:5000/api/schools (all schools)
    - http://localhost:5000/api/schools?state=CA (filter by state)
    - http://localhost:5000/api/schools?degree=MD (filter by degree type)
    - http://localhost:5000/api/schools?public=true (filter by public status)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Load data from CSV
def load_medical_schools():
    """Load medical schools data from CSV file."""
    schools = []

    # Try different path locations
    api_dir = os.path.dirname(__file__)
    possible_paths = [
        os.path.join(api_dir, '..', 'data', 'medical_schools_data.csv'),  # From api folder
        os.path.join(api_dir, 'medical_schools_data.csv'),  # Same directory
        'data/medical_schools_data.csv',  # From project root
        'medical_schools_data.csv'  # Current directory
    ]

    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            break

    if not csv_path:
        raise FileNotFoundError("Could not find medical_schools_data.csv in expected locations")

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert to more API-friendly format
            school = {
                'id': len(schools) + 1,
                'name': row['Medical School Name'],
                'state': row['State'],
                'degreeType': row['Degree Type'],
                'avgGPA': row['Average GPA'],
                'avgMCAT': row['Average MCAT'],
                'minMCATNotes': row['Minimum MCAT Notes'],
                'isPublic': row['Public School Status'] == 'Public',
                'applicationSystem': row['Application System'],
                'hasMDPhD': row['MD/PhD Program'] == 'Yes',
                'websiteURL': row['Website URL']
            }
            schools.append(school)

    return schools

# Cache the data in memory
MEDICAL_SCHOOLS = load_medical_schools()


@app.route('/')
def home():
    """API documentation endpoint."""
    return jsonify({
        'message': 'Medical Schools API',
        'version': '1.0',
        'endpoints': {
            '/api/schools': 'Get all schools (supports filtering)',
            '/api/schools/<id>': 'Get specific school by ID',
            '/api/states': 'Get list of all states',
            '/api/stats': 'Get summary statistics'
        },
        'query_parameters': {
            'state': 'Filter by state (e.g., ?state=CA)',
            'degree': 'Filter by degree type (e.g., ?degree=MD)',
            'public': 'Filter by public status (e.g., ?public=true)',
            'min_gpa': 'Filter by minimum GPA (e.g., ?min_gpa=3.5)',
            'max_gpa': 'Filter by maximum GPA (e.g., ?max_gpa=3.8)',
            'min_mcat': 'Filter by minimum MCAT (e.g., ?min_mcat=510)',
            'max_mcat': 'Filter by maximum MCAT (e.g., ?max_mcat=520)',
            'app_system': 'Filter by application system (e.g., ?app_system=TMDSAS)',
            'mdphd': 'Filter by MD/PhD program availability (e.g., ?mdphd=true)'
        }
    })


@app.route('/api/schools', methods=['GET'])
def get_schools():
    """
    Get all medical schools with optional filtering.

    Query Parameters:
        state: Filter by state code (e.g., CA, NY)
        degree: Filter by degree type (MD or DO)
        public: Filter by public status (true/false)
        app_system: Filter by application system (AMCAS, AACOMAS, TMDSAS)
        mdphd: Filter by MD/PhD program availability (true/false)
        min_gpa: Minimum GPA threshold
        max_gpa: Maximum GPA threshold
        min_mcat: Minimum MCAT threshold
        max_mcat: Maximum MCAT threshold
    """
    schools = MEDICAL_SCHOOLS.copy()

    # Apply filters
    state = request.args.get('state', '').upper()
    if state:
        schools = [s for s in schools if s['state'] == state]

    degree = request.args.get('degree', '').upper()
    if degree:
        schools = [s for s in schools if s['degreeType'] == degree]

    public_filter = request.args.get('public', '').lower()
    if public_filter == 'true':
        schools = [s for s in schools if s['isPublic']]
    elif public_filter == 'false':
        schools = [s for s in schools if not s['isPublic']]

    app_system = request.args.get('app_system', '').upper()
    if app_system:
        schools = [s for s in schools if s['applicationSystem'] == app_system]

    mdphd_filter = request.args.get('mdphd', '').lower()
    if mdphd_filter == 'true':
        schools = [s for s in schools if s['hasMDPhD']]
    elif mdphd_filter == 'false':
        schools = [s for s in schools if not s['hasMDPhD']]

    # GPA filtering
    try:
        min_gpa = request.args.get('min_gpa')
        if min_gpa:
            min_gpa = float(min_gpa)
            schools = [s for s in schools if _parse_gpa(s['avgGPA']) >= min_gpa]

        max_gpa = request.args.get('max_gpa')
        if max_gpa:
            max_gpa = float(max_gpa)
            schools = [s for s in schools if _parse_gpa(s['avgGPA']) <= max_gpa]
    except ValueError:
        pass

    # MCAT filtering
    try:
        min_mcat = request.args.get('min_mcat')
        if min_mcat:
            min_mcat = int(min_mcat)
            schools = [s for s in schools if _parse_mcat(s['avgMCAT']) >= min_mcat]

        max_mcat = request.args.get('max_mcat')
        if max_mcat:
            max_mcat = int(max_mcat)
            schools = [s for s in schools if _parse_mcat(s['avgMCAT']) <= max_mcat]
    except ValueError:
        pass

    return jsonify({
        'count': len(schools),
        'data': schools
    })


@app.route('/api/schools/<int:school_id>', methods=['GET'])
def get_school(school_id):
    """Get a specific school by ID."""
    school = next((s for s in MEDICAL_SCHOOLS if s['id'] == school_id), None)

    if school:
        return jsonify(school)
    else:
        return jsonify({'error': 'School not found'}), 404


@app.route('/api/states', methods=['GET'])
def get_states():
    """Get list of all states with school counts."""
    states = {}
    for school in MEDICAL_SCHOOLS:
        state = school['state']
        if state not in states:
            states[state] = {
                'state': state,
                'count': 0,
                'md_count': 0,
                'do_count': 0
            }
        states[state]['count'] += 1
        if school['degreeType'] == 'MD':
            states[state]['md_count'] += 1
        else:
            states[state]['do_count'] += 1

    return jsonify({
        'count': len(states),
        'data': sorted(states.values(), key=lambda x: x['state'])
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get summary statistics."""
    total_schools = len(MEDICAL_SCHOOLS)
    md_schools = sum(1 for s in MEDICAL_SCHOOLS if s['degreeType'] == 'MD')
    do_schools = sum(1 for s in MEDICAL_SCHOOLS if s['degreeType'] == 'DO')
    public_schools = sum(1 for s in MEDICAL_SCHOOLS if s['isPublic'])
    private_schools = total_schools - public_schools

    # Calculate GPA stats
    gpas = [_parse_gpa(s['avgGPA']) for s in MEDICAL_SCHOOLS]
    gpas = [g for g in gpas if g > 0]  # Filter out invalid values

    # Calculate MCAT stats
    mcats = [_parse_mcat(s['avgMCAT']) for s in MEDICAL_SCHOOLS]
    mcats = [m for m in mcats if m > 0]  # Filter out invalid values

    return jsonify({
        'total_schools': total_schools,
        'by_degree': {
            'md': md_schools,
            'do': do_schools
        },
        'by_status': {
            'public': public_schools,
            'private': private_schools
        },
        'gpa_stats': {
            'min': min(gpas) if gpas else None,
            'max': max(gpas) if gpas else None,
            'avg': round(sum(gpas) / len(gpas), 2) if gpas else None
        },
        'mcat_stats': {
            'min': min(mcats) if mcats else None,
            'max': max(mcats) if mcats else None,
            'avg': round(sum(mcats) / len(mcats), 1) if mcats else None
        }
    })


def _parse_gpa(gpa_str):
    """Parse GPA string to float, handling special cases."""
    if not gpa_str or gpa_str == 'NR':
        return 0.0

    # Handle ranges (take the first value)
    if '–' in gpa_str or '-' in gpa_str:
        gpa_str = gpa_str.split('–')[0].split('-')[0]

    # Handle 3.5+ format
    gpa_str = gpa_str.replace('+', '')

    try:
        return float(gpa_str.strip())
    except ValueError:
        return 0.0


def _parse_mcat(mcat_str):
    """Parse MCAT string to int, handling special cases."""
    if not mcat_str or mcat_str == 'NR':
        return 0

    # Handle ranges (take the first value)
    if '–' in mcat_str or '-' in mcat_str:
        mcat_str = mcat_str.split('–')[0].split('-')[0]

    # Handle 500+ format
    mcat_str = mcat_str.replace('+', '')

    try:
        return int(float(mcat_str.strip()))
    except ValueError:
        return 0


@app.route('/api/classify', methods=['GET'])
def classify_schools():
    """
    Classify schools as Reach, Target, or Undershoot for an applicant.

    Query Parameters:
        gpa: User's GPA (required)
        mcat: User's MCAT score (required)
        state: User's state (optional)
        degree: Filter by degree type (optional)
    """
    try:
        user_gpa = float(request.args.get('gpa'))
        user_mcat = int(request.args.get('mcat'))
    except (TypeError, ValueError):
        return jsonify({'error': 'GPA and MCAT parameters are required'}), 400

    user_state = request.args.get('state', '').upper()
    degree_filter = request.args.get('degree', '').upper()

    # Classification thresholds
    GPA_UNDERSHOOT_DIFF = 0.2
    GPA_TARGET_RANGE = 0.1
    MCAT_UNDERSHOOT_DIFF = 3
    MCAT_TARGET_RANGE = 2

    def classify_by_gpa(user_gpa, school_gpa):
        diff = user_gpa - school_gpa
        if diff >= GPA_UNDERSHOOT_DIFF:
            return 'Undershoot'
        elif abs(diff) <= GPA_TARGET_RANGE:
            return 'Target'
        else:
            return 'Reach' if diff < 0 else 'Target'

    def classify_by_mcat(user_mcat, school_mcat):
        diff = user_mcat - school_mcat
        if diff >= MCAT_UNDERSHOOT_DIFF:
            return 'Undershoot'
        elif abs(diff) <= MCAT_TARGET_RANGE:
            return 'Target'
        else:
            return 'Reach' if diff < 0 else 'Target'

    def classify_overall(gpa_class, mcat_class):
        if gpa_class == mcat_class:
            return gpa_class
        if (gpa_class == 'Reach' and mcat_class == 'Undershoot') or \
           (gpa_class == 'Undershoot' and mcat_class == 'Reach'):
            return 'Target'
        if gpa_class == 'Target':
            return mcat_class
        if mcat_class == 'Target':
            return gpa_class
        return 'Target'

    classified_schools = []

    for school in MEDICAL_SCHOOLS:
        # Apply degree filter if specified
        if degree_filter and school['degreeType'] != degree_filter:
            continue

        # Parse school stats
        school_gpa = _parse_gpa(school['avgGPA'])
        school_mcat = _parse_mcat(school['avgMCAT'])

        if school_gpa == 0 or school_mcat == 0:
            continue  # Skip schools with invalid data

        # Classify
        gpa_class = classify_by_gpa(user_gpa, school_gpa)
        mcat_class = classify_by_mcat(user_mcat, school_mcat)
        overall = classify_overall(gpa_class, mcat_class)

        # Check in-state advantage
        in_state_advantage = (user_state and school['state'] == user_state and school['isPublic'])

        classified_schools.append({
            **school,
            'classification': overall,
            'gpaClassification': gpa_class,
            'mcatClassification': mcat_class,
            'gpaDiff': round(user_gpa - school_gpa, 2),
            'mcatDiff': user_mcat - school_mcat,
            'inStateAdvantage': in_state_advantage
        })

    # Sort by classification and then by competitiveness
    reach = [s for s in classified_schools if s['classification'] == 'Reach']
    target = [s for s in classified_schools if s['classification'] == 'Target']
    undershoot = [s for s in classified_schools if s['classification'] == 'Undershoot']

    # Sort each category by school stats (most competitive first)
    reach.sort(key=lambda x: (_parse_gpa(x['avgGPA']), _parse_mcat(x['avgMCAT'])), reverse=True)
    target.sort(key=lambda x: (_parse_gpa(x['avgGPA']), _parse_mcat(x['avgMCAT'])), reverse=True)
    undershoot.sort(key=lambda x: (_parse_gpa(x['avgGPA']), _parse_mcat(x['avgMCAT'])), reverse=True)

    return jsonify({
        'userStats': {
            'gpa': user_gpa,
            'mcat': user_mcat,
            'state': user_state or None
        },
        'summary': {
            'totalSchools': len(classified_schools),
            'reachCount': len(reach),
            'targetCount': len(target),
            'undershootCount': len(undershoot)
        },
        'recommendations': {
            'reach': '3-5 schools',
            'target': '7-10 schools',
            'undershoot': '5-7 schools',
            'totalRecommended': '15-22 schools'
        },
        'schools': {
            'reach': reach,
            'target': target,
            'undershoot': undershoot
        }
    })


if __name__ == '__main__':
    print("="*60)
    print("Medical Schools API Server")
    print("="*60)
    print(f"Total schools loaded: {len(MEDICAL_SCHOOLS)}")
    print("\nAPI Endpoints:")
    print("  http://localhost:5000/")
    print("  http://localhost:5000/api/schools")
    print("  http://localhost:5000/api/schools?state=CA")
    print("  http://localhost:5000/api/schools?degree=MD")
    print("  http://localhost:5000/api/states")
    print("  http://localhost:5000/api/stats")
    print("  http://localhost:5000/api/classify?gpa=3.75&mcat=512")
    print("="*60)
    print("\nStarting server on http://localhost:5000")
    print("Press Ctrl+C to stop\n")

    app.run(debug=True, port=5000)
