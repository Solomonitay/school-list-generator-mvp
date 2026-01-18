#!/usr/bin/env python3
"""
Scrape Medical School URLs and Update Database
Extracts website URLs for each medical school from the Shemmassian Consulting page.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time


def scrape_school_urls(url):
    """
    Scrape school names and their URLs from the webpage.

    Args:
        url: The URL to scrape

    Returns:
        Dictionary mapping school names to URLs
    """
    print("Fetching webpage...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the data table
    table = soup.find('table')
    if not table:
        raise ValueError("Could not find data table on the page")

    school_urls = {}
    rows = table.find_all('tr')[1:]  # Skip header row

    print(f"Processing {len(rows)} schools...")

    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue

        # First cell contains the school name (and possibly a link)
        school_cell = cells[0]

        # Try to find a link
        link = school_cell.find('a')

        if link and link.get('href'):
            # School name from link text
            school_name = ' '.join(link.get_text(strip=True).split())
            url = link.get('href')

            # Remove asterisks from school name
            school_name = school_name.replace('*', '').strip()

            school_urls[school_name] = url
        else:
            # No link, just get the text
            school_name = ' '.join(school_cell.get_text(strip=True).split())
            school_name = school_name.replace('*', '').strip()
            school_urls[school_name] = ''  # Empty URL for schools without links

    return school_urls


def match_school_name(db_name, url_names):
    """
    Try to match a database school name to a URL dictionary key.
    Uses fuzzy matching for better results.

    Args:
        db_name: School name from database
        url_names: Dictionary of school names to URLs

    Returns:
        URL if found, empty string otherwise
    """
    # Exact match first
    if db_name in url_names:
        return url_names[db_name]

    # Try matching with different variations
    db_name_lower = db_name.lower()

    for url_name, url in url_names.items():
        url_name_lower = url_name.lower()

        # Check if names contain each other
        if db_name_lower in url_name_lower or url_name_lower in db_name_lower:
            return url

        # Check for key institution name matches
        # Extract main institution name (before "School of Medicine")
        db_institution = db_name_lower.split('school of')[0].strip()
        url_institution = url_name_lower.split('school of')[0].strip()

        if len(db_institution) > 10 and db_institution in url_name_lower:
            return url
        if len(url_institution) > 10 and url_institution in db_name_lower:
            return url

    return ''


def update_csv_with_urls(input_file, output_file, school_urls):
    """
    Add URL column to the CSV.

    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV
        school_urls: Dictionary of school names to URLs
    """
    schools_data = []
    matched_count = 0
    unmatched_schools = []

    # Read existing CSV
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            school_name = row['Medical School Name']

            # Try to find matching URL
            url = match_school_name(school_name, school_urls)

            if url:
                matched_count += 1
            else:
                unmatched_schools.append(school_name)

            row['Website URL'] = url
            schools_data.append(row)

    # Write updated CSV
    new_fieldnames = list(fieldnames) + ['Website URL']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(schools_data)

    return schools_data, matched_count, unmatched_schools


def print_summary(schools_data, matched_count, unmatched_schools):
    """Print summary statistics."""
    print("\n=== URL Scraping Summary ===")
    print(f"Total schools: {len(schools_data)}")
    print(f"Schools with URLs: {matched_count} ({matched_count/len(schools_data)*100:.1f}%)")
    print(f"Schools without URLs: {len(unmatched_schools)}")

    if unmatched_schools:
        print("\n=== Schools Without URLs (First 10) ===")
        for school in unmatched_schools[:10]:
            print(f"  • {school}")

        if len(unmatched_schools) > 10:
            print(f"  ... and {len(unmatched_schools) - 10} more")

    print("\n=== Sample Schools with URLs ===")
    count = 0
    for school in schools_data:
        if school['Website URL'] and count < 5:
            print(f"  • {school['Medical School Name']}")
            print(f"    → {school['Website URL']}")
            count += 1


def main():
    scrape_url = "https://www.shemmassianconsulting.com/blog/average-gpa-and-mcat-score-for-every-medical-school"
    input_file = "medical_schools_data.csv"
    output_file = "medical_schools_data.csv"  # Overwrite

    print("=" * 70)
    print("Medical School URL Scraper")
    print("=" * 70)

    try:
        # Scrape URLs from webpage
        school_urls = scrape_school_urls(scrape_url)
        print(f"\n✓ Found {len(school_urls)} schools on webpage")

        # Update CSV with URLs
        schools_data, matched_count, unmatched_schools = update_csv_with_urls(
            input_file, output_file, school_urls
        )

        print(f"\n✓ Successfully updated {len(schools_data)} schools")
        print(f"✓ Saved to: {output_file}")

        print_summary(schools_data, matched_count, unmatched_schools)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
