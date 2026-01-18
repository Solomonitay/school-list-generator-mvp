#!/usr/bin/env python3
"""
Update Medical Schools CSV with Application System Designations
Adds AMCAS, AACOMAS, or TMDSAS designation to each school.
"""

import csv

# Texas schools that use TMDSAS (updated from Shemmassian Consulting - February 2025)
# Using school names as they appear in our CSV database
TMDSAS_SCHOOLS = {
    "Baylor College of Medicine",
    "University of Texas School of Medicine at San Antonio",  # Long School of Medicine
    "University of Texas McGovern Medical School at Houston",  # McGovern Medical School
    "Sam Houston State University College of Osteopathic Medicine",
    "Texas A&M Health Science Center College of Medicine",
    "Texas Tech University Health Sciences Center Paul L. Foster School of Medicine",
    "Texas Tech University Health Sciences Center School of Medicine – Lubbock",
    "University of Houston Tilman J. Fertitta Family College of Medicine",
    "University of North Texas Health Science Center at Fort Worth Texas College of Osteopathic Medicine",
    "University of Texas at Austin Dell Medical School",
    "University of Texas Medical Branch School of Medicine",
    "University of Texas Rio Grande Valley School of Medicine",
    "University of Texas Southwestern Medical School"
    # Note: University of Texas at Tyler School of Medicine not in our current dataset
}

# Texas schools that don't use TMDSAS (from Shemmassian Consulting)
TEXAS_AMCAS_SCHOOLS = [
    "TCU and UNTHSC School of Medicine"
]
TEXAS_AACOMAS_SCHOOLS = [
    "University of the Incarnate Word School of Osteopathic Medicine"
]


def determine_application_system(school_name, degree_type, state):
    """
    Determine which application system a school uses.

    Args:
        school_name: Full name of the medical school
        degree_type: MD or DO
        state: State abbreviation

    Returns:
        Application system: TMDSAS, AMCAS, or AACOMAS
    """
    # Check if it's a TMDSAS school
    for tmdsas_school in TMDSAS_SCHOOLS:
        if tmdsas_school.lower() in school_name.lower():
            return "TMDSAS"

    # Texas exceptions
    if state == "TX":
        if any(amcas_school.lower() in school_name.lower() for amcas_school in TEXAS_AMCAS_SCHOOLS):
            return "AMCAS"
        if any(aacomas_school.lower() in school_name.lower() for aacomas_school in TEXAS_AACOMAS_SCHOOLS):
            return "AACOMAS"

    # General rules
    if degree_type == "DO":
        return "AACOMAS"
    else:  # MD programs
        return "AMCAS"


def update_csv_with_application_systems(input_file, output_file):
    """
    Read the existing CSV and add application system column.

    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV
    """
    schools_data = []

    # Read existing CSV
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            school_name = row['Medical School Name']
            degree_type = row['Degree Type']
            state = row['State']

            # Determine application system
            app_system = determine_application_system(school_name, degree_type, state)
            row['Application System'] = app_system

            schools_data.append(row)

    # Write updated CSV
    new_fieldnames = list(fieldnames) + ['Application System']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(schools_data)

    return schools_data


def print_summary(schools_data):
    """Print summary statistics."""
    amcas_count = sum(1 for s in schools_data if s['Application System'] == 'AMCAS')
    aacomas_count = sum(1 for s in schools_data if s['Application System'] == 'AACOMAS')
    tmdsas_count = sum(1 for s in schools_data if s['Application System'] == 'TMDSAS')

    print("\n=== Application System Summary ===")
    print(f"AMCAS (MD programs): {amcas_count}")
    print(f"AACOMAS (DO programs): {aacomas_count}")
    print(f"TMDSAS (Texas schools): {tmdsas_count}")
    print(f"Total: {len(schools_data)}")

    print("\n=== TMDSAS Schools Found ===")
    for school in schools_data:
        if school['Application System'] == 'TMDSAS':
            print(f"  • {school['Medical School Name']} ({school['Degree Type']})")


def main():
    input_file = "../public/medical_schools_data.csv"
    output_file = "../public/medical_schools_data.csv"  # Overwrite the original

    print("Updating medical schools CSV with application system designations...")

    schools_data = update_csv_with_application_systems(input_file, output_file)

    print(f"\n✓ Successfully updated {len(schools_data)} schools")
    print(f"✓ Saved to: {output_file}")

    print_summary(schools_data)


if __name__ == "__main__":
    main()
