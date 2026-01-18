#!/usr/bin/env python3
"""
Update Medical Schools CSV with Casper Test Requirements
Adds a column indicating which schools require the Casper test based on Shemmassian Consulting data.
"""

import csv

# Schools that require Casper test (from Shemmassian Consulting - Appendix A)
# Updated March 2025 for 2025-2026 application cycle

MD_SCHOOLS_REQUIRING_CASPER = {
    "Baylor College of Medicine",
    "Boston University School of Medicine",
    "California University of Science and Medicine",
    "Central Michigan University College of Medicine",
    "Donald and Barbara Zucker School of Medicine at Hofstra/Northwell",
    "Drexel University College of Medicine",
    "East Tennessee State University Quillen College of Medicine",
    "Indiana University School of Medicine",
    "Medical College of Georgia at Augusta University",
    "Medical College of Wisconsin",
    "Meharry Medical College",
    "Michigan State University College of Human Medicine",
    "Netter School of Medicine Quinnipiac University",
    "New York Medical College",
    "Renaissance School of Medicine at Stony Brook University",
    "Rush University Medical College",
    "Rutgers Robert Wood Johnson Medical School",
    "Temple University Lewis Katz School of Medicine",
    "Texas A&M University College of Medicine",
    "Texas Tech University Health Sciences Center El Paso Paul L. Foster School of Medicine",
    "Texas Tech University Health Sciences Center School of Medicine at Lubbock",
    "Tulane University School of Medicine",
    "University of Colorado School of Medicine",
    "University of Miami Miller School of Medicine",
    "University of Nevada, Reno School of Medicine",
    "University of Texas at Tyler School of Medicine",
    "University of Texas Health Science Center at Houston, McGovern Medical School",
    "University of Texas Health Science Center at San Antonio, Long School of Medicine",
    "University of Texas Medical Branch John Sealy School of Medicine",
    "University of Texas Southwestern Medical School",
    "University of Vermont Larner College of Medicine",
    "Virginia Commonwealth University School of Medicine",
    "Wake Forest School of Medicine",
    "West Virginia University School of Medicine"
}

DO_SCHOOLS_REQUIRING_CASPER = {
    "Arkansas College of Osteopathic Medicine",
    "Kansas Health Science Center – Kansas College of Osteopathic Medicine",
    "Sam Houston State University College of Osteopathic Medicine",
    "Touro University Nevada College of Medicine",
    "Touro College of Osteopathic Medicine (NY)",
    "William Carey University College of Osteopathic Medicine"
}

# Note: Some schools "encourage" but don't require Casper:
# - Tulane University School of Medicine (encourages)
# - West Virginia University School of Medicine (encourages for 2025)
# - Arkansas College of Osteopathic Medicine (highly recommended but not required)


def normalize_school_name(name):
    """
    Normalize school names for better matching.
    Remove extra spaces, handle common variations.
    """
    # Common name variations to standardize
    name = name.strip()
    name = name.replace("  ", " ")  # Remove double spaces

    # Handle specific variations
    replacements = {
        "Texas Tech University Health Sciences Center El Paso Paul L. Foster School of Medicine": "Texas Tech University Health Sciences Center Paul L. Foster School of Medicine",
        "Texas Tech University Health Sciences Center School of Medicine at Lubbock": "Texas Tech University Health Sciences Center School of Medicine – Lubbock",
        "University of Texas Health Science Center at Houston, McGovern Medical School": "University of Texas McGovern Medical School at Houston",
        "University of Texas Health Science Center at San Antonio, Long School of Medicine": "University of Texas School of Medicine at San Antonio",
    }

    return replacements.get(name, name)


def requires_casper(school_name, degree_type):
    """
    Determine if a school requires the Casper test.

    Args:
        school_name: Full name of the medical school
        degree_type: MD or DO

    Returns:
        Boolean: True if school requires Casper, False otherwise
    """
    normalized_name = normalize_school_name(school_name)

    # Check MD schools
    if degree_type == "MD":
        # Direct match
        if normalized_name in MD_SCHOOLS_REQUIRING_CASPER:
            return True

        # Fuzzy matching for common variations
        for casper_school in MD_SCHOOLS_REQUIRING_CASPER:
            if casper_school.lower() in normalized_name.lower():
                return True

    # Check DO schools
    elif degree_type == "DO":
        # Direct match
        if normalized_name in DO_SCHOOLS_REQUIRING_CASPER:
            return True

        # Fuzzy matching for common variations
        for casper_school in DO_SCHOOLS_REQUIRING_CASPER:
            if casper_school.lower() in normalized_name.lower():
                return True

    return False


def update_csv_with_casper_requirements(input_file, output_file):
    """
    Read the existing CSV and add Casper requirement column.

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

            # Determine Casper requirement
            casper_required = requires_casper(school_name, degree_type)
            row['Requires Casper'] = 'True' if casper_required else 'False'

            schools_data.append(row)

    # Write updated CSV
    new_fieldnames = list(fieldnames) + ['Requires Casper']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(schools_data)

    return schools_data


def print_summary(schools_data):
    """Print summary statistics."""
    md_casper = sum(1 for s in schools_data if s['Degree Type'] == 'MD' and s['Requires Casper'] == 'True')
    do_casper = sum(1 for s in schools_data if s['Degree Type'] == 'DO' and s['Requires Casper'] == 'True')
    total_md = sum(1 for s in schools_data if s['Degree Type'] == 'MD')
    total_do = sum(1 for s in schools_data if s['Degree Type'] == 'DO')

    print("\n=== Casper Test Requirements Summary ===")
    print(f"MD schools requiring Casper: {md_casper}/{total_md} ({md_casper/total_md*100:.1f}%)")
    print(f"DO schools requiring Casper: {do_casper}/{total_do} ({do_casper/total_do*100:.1f}%)")
    print(f"Total schools requiring Casper: {md_casper + do_casper}")

    print("\n=== MD Schools Requiring Casper ===")
    for school in schools_data:
        if school['Degree Type'] == 'MD' and school['Requires Casper'] == 'True':
            print(f"  • {school['Medical School Name']}")

    print("\n=== DO Schools Requiring Casper ===")
    for school in schools_data:
        if school['Degree Type'] == 'DO' and school['Requires Casper'] == 'True':
            print(f"  • {school['Medical School Name']}")


def main():
    input_file = "../public/medical_schools_data.csv"
    output_file = "../public/medical_schools_data_with_casper.csv"

    print("Updating medical schools CSV with Casper test requirements...")
    print("Source: Shemmassian Consulting - Appendix A (March 2025 update)")

    schools_data = update_csv_with_casper_requirements(input_file, output_file)

    print(f"\n✓ Successfully updated {len(schools_data)} schools")
    print(f"✓ Saved to: {output_file}")

    print_summary(schools_data)

    print("\n=== Next Steps ===")
    print("1. Review the updated CSV file")
    print("2. If satisfied, replace the original medical_schools_data.csv")
    print("3. Update any React components to display Casper requirements")
    print("4. Test the application to ensure new data displays correctly")


if __name__ == "__main__":
    main()