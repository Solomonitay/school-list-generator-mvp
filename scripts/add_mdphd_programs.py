#!/usr/bin/env python3
"""
Add MD/PhD Program Information to Medical Schools Database
Updates the CSV to indicate which schools offer MD/PhD programs.
"""

import csv
import re

# U.S. Schools with MD/PhD programs (from Shemmassian Consulting)
# These are partial names/keywords to match against our database
MDPHD_SCHOOLS = {
    # Alabama
    "University of Alabama School of Medicine",
    "University of South Alabama College of Medicine",

    # Arizona
    "Mayo Clinic Alix School of Medicine",
    "University of Arizona College of Medicine - Tucson",
    "University of Arizona School of Medicine - Phoenix",

    # Arkansas
    "University of Arkansas",

    # California
    "Loma Linda University School of Medicine",
    "Stanford University School of Medicine",
    "University of California – Davis",
    "University of California – Irvine",
    "University of California – San Diego",
    "University of California – San Francisco",
    "University of Southern California Keck School of Medicine",

    # Colorado
    "University of Colorado School of Medicine",

    # Connecticut
    "University of Connecticut School of Medicine",
    "Yale School of Medicine",

    # DC
    "Georgetown University School of Medicine",
    "Howard University College of Medicine",

    # Florida
    "University of Florida College of Medicine",
    "University of Miami Miller School of Medicine",
    "University of South Florida",

    # Georgia
    "Emory University School of Medicine",
    "Medical College of Georgia at Augusta University",
    "Morehouse School of Medicine",

    # Illinois
    "Loyola University of Chicago Stritch School of Medicine",
    "Northwestern University",
    "Chicago Medical School at Rosalind Franklin University",
    "University of Chicago Pritzker School of Medicine",
    "University of Illinois College of Medicine",

    # Indiana
    "Indiana University School of Medicine",

    # Iowa
    "University of Iowa",

    # Kansas
    "University of Kansas School of Medicine",

    # Kentucky
    "University of Kentucky College of Medicine",
    "University of Louisville School of Medicine",

    # Louisiana
    "Louisiana State University – New Orleans",
    "Louisiana State University – Shreveport",
    "Tulane University School of Medicine",

    # Maryland
    "Johns Hopkins University School of Medicine",
    "Uniformed Services University",
    "University of Maryland School of Medicine",

    # Massachusetts
    "Boston University School of Medicine",
    "Tufts University School of Medicine",
    "University of Massachusetts Medical School",
    "Harvard Medical School",  # Not in list but likely has it

    # Michigan
    "Michigan State University College of",
    "University of Michigan Medical School",
    "Wayne State University School of Medicine",

    # Minnesota
    "Mayo",  # Both Mayo campuses
    "University of Minnesota",

    # Mississippi
    "University of Mississippi School of Medicine",

    # Missouri
    "Saint Louis University School of Medicine",
    "University of Missouri – Columbia",
    "University of Missouri – Kansas City",
    "Washington University School of Medicine",

    # Nebraska
    "Creighton University School of Medicine",
    "University of Nebraska Medical Center",

    # Nevada
    "University of Nevada Reno",

    # New Hampshire
    "Geisel School of Medicine at Dartmouth",

    # New Jersey
    "Rutgers New Jersey Medical School",
    "Rutgers Robert Wood Johnson",

    # New Mexico
    "University of New Mexico School of Medicine",

    # New York
    "Albany Medical College",
    "Albert Einstein College of Medicine",
    "Columbia University College of Physicians and Surgeons",
    "Hofstra Northwell School of Medicine",
    "Weill Cornell Medical College",
    "Icahn School of Medicine at Mount Sinai",
    "New York Medical College",
    "New York University",
    "University at Buffalo",
    "Stony Brook University School of Medicine",
    "SUNY – Downstate Medical Center",
    "SUNY – Upstate Medical University",
    "University of Rochester School of Medicine",

    # North Carolina
    "Wake Forest School of Medicine",
    "Duke University School of Medicine",
    "East Carolina University Brody School of Medicine",
    "University of North Carolina at Chapel Hill",

    # North Dakota
    "University of North Dakota",

    # Ohio
    "Case Western Reserve University School of Medicine",
    "The Ohio State University College of Medicine",
    "University of Cincinnati College of Medicine",
    "The University of Toledo College of Medicine",
    "Wright State University",

    # Oklahoma
    "University of Oklahoma College of Medicine",

    # Oregon
    "Oregon Health & Science University",

    # Pennsylvania
    "Drexel University College of Medicine",
    "Sidney Kimmel Medical College at Thomas Jefferson",
    "Pennsylvania State University College of Medicine",
    "Perelman School of Medicine University of Pennsylvania",
    "University of Pittsburgh School of Medicine",
    "Temple University Lewis Katz School of Medicine",

    # Rhode Island
    "Brown University The Warren Alpert Medical School",

    # South Carolina
    "Medical University of South Carolina",
    "University of South Carolina School of Medicine",

    # South Dakota
    "University of South Dakota",

    # Tennessee
    "East Tennessee State University Quillen",
    "Meharry Medical College",
    "University of Tennessee Health Science Center",
    "Vanderbilt University School of Medicine",

    # Texas
    "Baylor College of Medicine",
    "Texas A&M Health Science Center",
    "Texas Tech University",
    "University of Texas Medical Branch",
    "University of Texas School of Medicine at San Antonio",
    "University of Texas Southwestern",

    # Utah
    "University of Utah School of Medicine",

    # Virginia
    "Virginia Commonwealth University School of Medicine",
    "University of Virginia School of Medicine",

    # Washington
    "University of Washington School of Medicine",

    # West Virginia
    "Marshall University",
    "West Virginia University School of Medicine",

    # Wisconsin
    "Medical College of Wisconsin",
    "University of Wisconsin",
}


def has_mdphd_program(school_name, degree_type):
    """
    Check if a school offers an MD/PhD program.

    Args:
        school_name: Full name of the school
        degree_type: MD or DO

    Returns:
        Boolean indicating if school has MD/PhD program
    """
    # DO schools don't typically have MD/PhD programs
    if degree_type == "DO":
        return False

    # Check if any MD/PhD school keyword matches
    school_name_lower = school_name.lower()

    for mdphd_school in MDPHD_SCHOOLS:
        mdphd_school_lower = mdphd_school.lower()

        # Check for substring match
        if mdphd_school_lower in school_name_lower or school_name_lower in mdphd_school_lower:
            return True

    return False


def update_csv_with_mdphd(input_file, output_file):
    """
    Add MD/PhD program column to CSV.

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

            # Check if school has MD/PhD program
            has_program = has_mdphd_program(school_name, degree_type)
            row['MD/PhD Program'] = 'Yes' if has_program else 'No'

            schools_data.append(row)

    # Write updated CSV
    new_fieldnames = list(fieldnames) + ['MD/PhD Program']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(schools_data)

    return schools_data


def print_summary(schools_data):
    """Print summary statistics."""
    mdphd_count = sum(1 for s in schools_data if s['MD/PhD Program'] == 'Yes')
    md_schools = sum(1 for s in schools_data if s['Degree Type'] == 'MD')

    print("\n=== MD/PhD Program Summary ===")
    print(f"Schools with MD/PhD programs: {mdphd_count}")
    print(f"Total MD programs: {md_schools}")
    print(f"Percentage of MD schools with MD/PhD: {(mdphd_count/md_schools*100):.1f}%")

    print("\n=== Schools with MD/PhD Programs ===")
    for school in schools_data:
        if school['MD/PhD Program'] == 'Yes':
            print(f"  • {school['Medical School Name']} ({school['State']})")


def main():
    input_file = "medical_schools_data.csv"
    output_file = "medical_schools_data.csv"  # Overwrite

    print("Adding MD/PhD program information to medical schools database...")

    schools_data = update_csv_with_mdphd(input_file, output_file)

    print(f"\n✓ Successfully updated {len(schools_data)} schools")
    print(f"✓ Saved to: {output_file}")

    print_summary(schools_data)

    print("\n=== Note ===")
    print("This data is based on schools listed in the Shemmassian MD/PhD guide.")
    print("If you notice any missing schools, you can manually update the CSV.")


if __name__ == "__main__":
    main()
