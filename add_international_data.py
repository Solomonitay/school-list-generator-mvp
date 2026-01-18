import pandas as pd
import re

# List of MD schools that accept international students from Shemmassian Consulting
international_schools = {
    'Boston University School of Medicine',
    'Case Western Reserve School of Medicine',
    'Columbia University Vagelos College of Physicians and Surgeons',
    'Creighton University School of Medicine',
    'Duke University School of Medicine',
    'Emory University School of Medicine',
    'Faculty of Medicine Université Laval',
    'Geisel School of Medicine at Dartmouth',
    'George Washington University School of Medicine and Health Sciences',
    'Harvard Medical School',
    'Howard University College of Medicine',
    'Icahn School of Medicine at Mount Sinai',
    'Johns Hopkins University School of Medicine',
    'Loma Linda University School of Medicine',
    'McGill University Faculty of Medicine',
    'McGovern Medical School',
    'McMaster University Michael G. DeGroote School of Medicine',
    'Medical College of Wisconsin–Milwaukee',
    'Memorial University of Newfoundland Faculty of Medicine',
    'Morehouse School of Medicine',
    'New York Medical College',
    'Northwestern University The Feinberg School of Medicine',
    'NYU Grossman Long Island School of Medicine',
    'NYU Grossman School of Medicine',
    'Perelman School of Medicine at the University of Pennsylvania',
    "Queen's University Faculty of Health Sciences",
    'Renaissance School of Medicine at Stony Brook University',
    'Rutgers New Jersey Medical School',
    'Rutgers Robert Wood Johnson Medical School',
    'Saint Louis University School of Medicine',
    'San Juan Bautista School of Medicine',
    'Sidney Kimmel Medical College at Thomas Jefferson University',
    'Stanford University School of Medicine',
    'State University of New York Upstate Medical University',
    'The Warren Alpert Medical School of Brown University',
    'Tufts University School of Medicine',
    'Tulane University School of Medicine',
    'Universidad Central del Caribe School of Medicine',
    'Universite de Montreal Faculty of Medicine',
    'Universite de Sherbrooke Faculty of Medicine',
    'University of California, Davis, School of Medicine',
    'University of Chicago Division of the Biological Sciences The Pritzker School of Medicine',
    'University of Colorado School of Medicine',
    'University of Connecticut School of Medicine',
    'University of Hawaii, John A. Burns School of Medicine',
    'University of Illinois College of Medicine',
    'University of Kentucky College of Medicine',
    'University of Louisville School of Medicine',
    'University of Maryland School of Medicine',
    'University of Nebraska Medical Center College of Medicine',
    'University of New Mexico School of Medicine',
    'University of North Carolina at Chapel Hill School of Medicine',
    'University of Rochester School of Medicine and Dentistry',
    'University of South Alabama',
    'University of Southern California Keck School of Medicine',
    'University of Toronto Faculty of Medicine',
    'University of Utah School of Medicine',
    'University of Virginia School of Medicine',
    'Vanderbilt University School of Medicine',
    'Virginia Commonwealth University School of Medicine',
    'Washington University in St. Louis School of Medicine',
    'Wayne State University School of Medicine',
    'Weill Cornell Medicine',
    'West Virginia University School of Medicine',
    'Yale School of Medicine'
}

def clean_school_name(name):
    """Clean school names for matching"""
    name = str(name).strip()
    name = re.sub(r'\s+', ' ', name)
    # Remove common variations
    name = re.sub(r'^university of ', '', name, flags=re.IGNORECASE)
    name = re.sub(r' college of medicine$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' school of medicine$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' medical college$', '', name, flags=re.IGNORECASE)
    return name.lower().strip()

def add_international_acceptance():
    """Add international student acceptance data to CSV"""
    # Read current CSV
    df = pd.read_csv('/Users/itaysolomon/medical-school-advisor/public/medical_schools_data.csv')

    # Add new column if it doesn't exist
    if 'Accepts International Students' not in df.columns:
        df['Accepts International Students'] = False

    # Reset all to False first
    df['Accepts International Students'] = False

    # Mark schools that accept international students
    updated_count = 0
    for idx, row in df.iterrows():
        school_name = row['Medical School Name']
        clean_name = clean_school_name(school_name)

        # Check if this school accepts international students
        accepts = False
        for intl_school in international_schools:
            clean_intl = clean_school_name(intl_school)
            # Use multiple matching strategies
            if (clean_name == clean_intl or
                clean_name in clean_intl or
                clean_intl in clean_name or
                len(set(clean_name.split()) & set(clean_intl.split())) >= 2):  # At least 2 words match
                accepts = True
                break

        df.at[idx, 'Accepts International Students'] = accepts
        if accepts:
            updated_count += 1

    # Save updated CSV
    df.to_csv('/Users/itaysolomon/medical-school-advisor/public/medical_schools_data_updated.csv', index=False)

    print(f"Updated {updated_count} schools to indicate they accept international students")
    accepts_count = df['Accepts International Students'].sum()
    print(f"Total schools that accept international students: {accepts_count}/{len(df)} ({accepts_count/len(df)*100:.1f}%)")

    # Show some examples
    accepts_df = df[df['Accepts International Students'] == True]
    print("\nSample schools that accept international students:")
    for i, row in accepts_df.head(5).iterrows():
        print(f"- {row['Medical School Name']}")

if __name__ == "__main__":
    add_international_acceptance()