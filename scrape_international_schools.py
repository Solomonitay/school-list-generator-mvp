import requests
from bs4 import BeautifulSoup
import re

def scrape_international_schools():
    """Scrape list of MD schools that accept international students from Shemmassian Consulting"""
    url = 'https://www.shemmassianconsulting.com/blog/medical-schools-that-accept-international-students'

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the section with MD schools that accept international students
        # Look for the heading that contains "Allopathic (MD) medical schools that accept international students"
        md_section = None
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            if 'Allopathic (MD) medical schools that accept international students' in heading.text:
                md_section = heading
                break

        if not md_section:
            print("Could not find MD schools section")
            return set()

        # Extract all schools from the list that follows
        international_schools = set()

        # Find the next element after the heading
        current = md_section.find_next()

        while current and current.name not in ['h2', 'h3', 'h4']:
            # Look for list items or paragraphs containing school names
            for li in current.find_all('li'):
                text = li.text.strip()
                # Extract school name (remove asterisks and footnotes)
                school_name = re.sub(r'[*^§†]', '', text).strip()
                if school_name and len(school_name) > 10:  # Filter out very short entries
                    international_schools.add(school_name)

            current = current.find_next()

        print(f"Found {len(international_schools)} MD schools that accept international students")

        # Show sample
        sample = list(international_schools)[:10]
        print("Sample schools:")
        for school in sample:
            print(f"- {school}")

        return international_schools

    except Exception as e:
        print(f"Error scraping international schools: {e}")
        return set()

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

def update_csv_with_international_data():
    """Update CSV to include international student acceptance info"""
    international_schools = scrape_international_schools()

    if not international_schools:
        print("No international schools data scraped")
        return

    # Read current CSV
    import pandas as pd
    df = pd.read_csv('/Users/itaysolomon/medical-school-advisor/public/medical_schools_data.csv')

    # Add new column
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
            # Use fuzzy matching
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
    print(f"Total schools that accept international students: {accepts_count}")

if __name__ == "__main__":
    update_csv_with_international_data()