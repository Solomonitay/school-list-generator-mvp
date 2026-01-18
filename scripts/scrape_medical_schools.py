#!/usr/bin/env python3
"""
Medical School Data Scraper
Scrapes medical school admission statistics and organizes them into a structured CSV format.
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
from typing import Dict, List, Optional


def scrape_medical_schools(url: str) -> List[Dict[str, str]]:
    """
    Scrape medical school data from the specified URL.

    Args:
        url: The URL to scrape

    Returns:
        List of dictionaries containing medical school data
    """
    # Fetch the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the data table
    table = soup.find('table')
    if not table:
        raise ValueError("Could not find data table on the page")

    schools_data = []

    # Process each row in the table (skip header row)
    rows = table.find_all('tr')[1:]  # Skip header

    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 5:  # Ensure we have enough columns
            continue

        # Extract raw data and clean up whitespace/newlines
        school_name_raw = ' '.join(cells[0].get_text(strip=True).split())
        state = ' '.join(cells[1].get_text(strip=True).split())
        degree_type = ' '.join(cells[2].get_text(strip=True).split())
        avg_gpa = ' '.join(cells[3].get_text(strip=True).split())
        avg_mcat = ' '.join(cells[4].get_text(strip=True).split())
        min_mcat = ' '.join(cells[5].get_text(strip=True).split()) if len(cells) > 5 else "NR"

        # Parse school name and check for asterisk (public school indicator)
        is_public = False
        school_name = school_name_raw

        if '*' in school_name_raw:
            is_public = True
            school_name = school_name_raw.replace('*', '').strip()

        # Create the data dictionary
        school_dict = {
            'Medical School Name': school_name,
            'State': state,
            'Degree Type': degree_type,
            'Average GPA': avg_gpa,
            'Average MCAT': avg_mcat,
            'Minimum MCAT Notes': min_mcat,
            'Public School Status': 'Public' if is_public else 'Private'
        }

        schools_data.append(school_dict)

    return schools_data


def save_to_csv(data: List[Dict[str, str]], filename: str) -> None:
    """
    Save the scraped data to a CSV file.

    Args:
        data: List of school dictionaries
        filename: Output CSV filename
    """
    if not data:
        print("No data to save")
        return

    fieldnames = [
        'Medical School Name',
        'State',
        'Degree Type',
        'Average GPA',
        'Average MCAT',
        'Minimum MCAT Notes',
        'Public School Status'
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"✓ Successfully saved {len(data)} medical schools to {filename}")


def main():
    """Main execution function."""
    url = "https://www.shemmassianconsulting.com/blog/average-gpa-and-mcat-score-for-every-medical-school"
    output_file = "medical_schools_data.csv"

    print("Starting medical school data scraper...")
    print(f"Fetching data from: {url}")

    try:
        # Scrape the data
        schools_data = scrape_medical_schools(url)

        # Save to CSV
        save_to_csv(schools_data, output_file)

        # Print summary statistics
        print(f"\nSummary:")
        print(f"  Total schools scraped: {len(schools_data)}")
        print(f"  MD programs: {sum(1 for s in schools_data if s['Degree Type'] == 'MD')}")
        print(f"  DO programs: {sum(1 for s in schools_data if s['Degree Type'] == 'DO')}")
        print(f"  Public schools: {sum(1 for s in schools_data if s['Public School Status'] == 'Public')}")
        print(f"  Private schools: {sum(1 for s in schools_data if s['Public School Status'] == 'Private')}")

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
