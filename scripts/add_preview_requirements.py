#!/usr/bin/env python3
"""
Update Medical Schools CSV with AAMC PREview Exam Requirements
Adds a column indicating AAMC PREview requirements based on Shemmassian Consulting data.
"""

import csv

# Schools with AAMC PREview requirements (from Shemmassian Consulting - March 2025)
# Only MD schools are listed as requiring/recommending PREview

MD_SCHOOLS_PREVIEW_REQUIREMENTS = {
    "Alice L. Walton School of Medicine": "Highly Recommended",
    "Cooper Medical School of Rowan University": "Recommended",
    "Geisinger Commonwealth School of Medicine": "Highly Recommended",
    "George Washington University School of Medicine and Health Sciences": "Recommended",
    "Howard University College of Medicine": "Recommended (research only)",
    "Kaiser Permanente School of Medicine": "Required",
    "Mercer University School of Medicine": "Required",
    "Michigan State University College of Human Medicine": "Required (either PREview or Casper)",
    "Morehouse School of Medicine": "Highly Recommended",
    "Oakland University William Beaumont School of Medicine": "Highly Recommended",
    "Rutgers - Robert Wood Johnson Medical School": "Required (either PREview or Casper)",
    "Saint Louis University School of Medicine": "Required",
    "Southern Illinois University School of Medicine": "Recommended",
    "Thomas F. Frist, Jr. College of Medicine at Belmont University": "Required",
    "Uniformed Services University of the Health Sciences F. Edward Hebert School of Medicine": "Recommended",
    "University of Alabama at Birmingham Marnix E. Heersink School of Medicine": "Highly Recommended",
    "University of California at Davis School of Medicine": "Required",
    "University of California Los Angeles David Geffen School of Medicine": "Required for traditional MD program",
    "University of Hawaii John A. Burns School of Medicine": "Required",
    "University of Louisville School of Medicine": "Recommended (research only)",
    "University of Massachusetts Medical School": "Required",
    "University of Utah School of Medicine": "Required",
    "University of Wisconsin School of Medicine and Public Health": "Highly Recommended"
}

# DO schools that recommend PREview (mentioned separately)
DO_SCHOOLS_PREVIEW_RECOMMENDED = {
    "Des Moines University Doctor of Osteopathic Medicine": "Recommended",
    "Oklahoma State University Center for Health Sciences College of Osteopathic Medicine": "Recommended",
    "Rowan-Virtua School of Osteopathic Medicine": "Recommended"
}


def normalize_school_name(name):
    """
    Normalize school names for better matching.
    Remove extra spaces, handle common variations.
    """
    name = name.strip()
    name = name.replace("  ", " ")  # Remove double spaces

    # Common name variations to standardize
    replacements = {
        "Rutgers - Robert Wood Johnson Medical School": "Rutgers Robert Wood Johnson Medical School",
        "University of Alabama at Birmingham Marnix E. Heersink School of Medicine": "University of Alabama at Birmingham Heersink School of Medicine",
        "University of California at Davis School of Medicine": "University of California Davis School of Medicine",
        "University of California Los Angeles David Geffen School of Medicine": "University of California Los Angeles David Geffen School of Medicine",
        "University of Hawaii John A. Burns School of Medicine": "University of Hawaii John A. Burns School of Medicine",
        "University of Louisville School of Medicine": "University of Louisville School of Medicine",
        "University of Massachusetts Medical School": "University of Massachusetts Medical School",
        "University of Utah School of Medicine": "University of Utah School of Medicine",
        "University of Wisconsin School of Medicine and Public Health": "University of Wisconsin School of Medicine and Public Health",
    }

    return replacements.get(name, name)


def get_preview_requirement(school_name, degree_type):
    """
    Determine the AAMC PREview requirement for a school.

    Args:
        school_name: Full name of the medical school
        degree_type: MD or DO

    Returns:
        String: PREview requirement status or "Not Required"
    """
    normalized_name = normalize_school_name(school_name)

    # Check MD schools first
    if degree_type == "MD":
        # Direct match
        if normalized_name in MD_SCHOOLS_PREVIEW_REQUIREMENTS:
            return MD_SCHOOLS_PREVIEW_REQUIREMENTS[normalized_name]

        # Fuzzy matching for common variations
        for preview_school, requirement in MD_SCHOOLS_PREVIEW_REQUIREMENTS.items():
            if preview_school.lower() in normalized_name.lower():
                return requirement

    # Check DO schools
    elif degree_type == "DO":
        # Direct match
        if normalized_name in DO_SCHOOLS_PREVIEW_RECOMMENDED:
            return DO_SCHOOLS_PREVIEW_RECOMMENDED[normalized_name]

        # Fuzzy matching for common variations
        for preview_school, requirement in DO_SCHOOLS_PREVIEW_RECOMMENDED.items():
            if preview_school.lower() in normalized_name.lower():
                return requirement

    return "Not Required"


def update_csv_with_preview_requirements(input_file, output_file):
    """
    Read the existing CSV and add PREview requirement column.

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

            # Determine PREview requirement
            preview_requirement = get_preview_requirement(school_name, degree_type)
            row['Requires PREview'] = preview_requirement

            schools_data.append(row)

    # Write updated CSV
    new_fieldnames = list(fieldnames) + ['Requires PREview']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(schools_data)

    return schools_data


def print_summary(schools_data):
    """Print summary statistics."""
    md_preview_required = sum(1 for s in schools_data if s['Degree Type'] == 'MD' and s['Requires PREview'] != 'Not Required')
    do_preview_recommended = sum(1 for s in schools_data if s['Degree Type'] == 'DO' and s['Requires PREview'] != 'Not Required')
    total_md = sum(1 for s in schools_data if s['Degree Type'] == 'MD')
    total_do = sum(1 for s in schools_data if s['Degree Type'] == 'DO')

    print("\n=== AAMC PREview Requirements Summary ===")
    print(f"MD schools with PREview requirements: {md_preview_required}/{total_md} ({md_preview_required/total_md*100:.1f}%)")
    print(f"DO schools with PREview recommendations: {do_preview_recommended}/{total_do} ({do_preview_recommended/total_do*100:.1f}%)")

    print("\n=== MD Schools with PREview Requirements ===")
    for school in schools_data:
        if school['Degree Type'] == 'MD' and school['Requires PREview'] != 'Not Required':
            print(f"  • {school['Medical School Name']}: {school['Requires PREview']}")

    print("\n=== DO Schools with PREview Recommendations ===")
    for school in schools_data:
        if school['Degree Type'] == 'DO' and school['Requires PREview'] != 'Not Required':
            print(f"  • {school['Medical School Name']}: {school['Requires PREview']}")


def main():
    input_file = "../public/medical_schools_data.csv"
    output_file = "../public/medical_schools_data_with_preview.csv"

    print("Updating medical schools CSV with AAMC PREview requirements...")
    print("Source: Shemmassian Consulting - AAMC PREview guide (March 2025)")

    schools_data = update_csv_with_preview_requirements(input_file, output_file)

    print(f"\n✓ Successfully updated {len(schools_data)} schools")
    print(f"✓ Saved to: {output_file}")

    print_summary(schools_data)

    print("\n=== Next Steps ===")
    print("1. Review the updated CSV file")
    print("2. If satisfied, replace the original medical_schools_data.csv")
    print("3. Update React components to display PREview requirements")
    print("4. Test the application to ensure new data displays correctly")


if __name__ == "__main__":
    main()