import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from fuzzywuzzy import fuzz

def clean_school_name(name):
    """Clean school names for better matching"""
    name = str(name).strip()

    # Normalize common variations
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[^\w\s]', ' ', name)  # Replace punctuation with spaces
    name = re.sub(r'\s+', ' ', name)  # Normalize spaces again

    # Remove common prefixes/suffixes
    name = re.sub(r'^the\s+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^university of ', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^college of ', '', name, flags=re.IGNORECASE)
    name = re.sub(r' college of medicine$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' school of medicine$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' medical college$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' medical school$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' school of medicine and science$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' of medicine$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+school$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+college$', '', name, flags=re.IGNORECASE)

    # Handle common abbreviations
    name = re.sub(r'\bmed\b', 'medicine', name, flags=re.IGNORECASE)
    name = re.sub(r'\buniv\b', 'university', name, flags=re.IGNORECASE)

    return name.lower().strip()

def scrape_accepted_data():
    """Scrape in-state/out-of-state acceptance rates from Accepted.com"""
    url = 'https://www.accepted.com/resources/selectivity-index/medical-school/'

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the main table
        table = soup.find('table')
        if not table:
            print("No table found on the page")
            return None

        accepted_data = []

        # Skip header row and process data rows
        rows = table.find_all('tr')[1:]  # Skip the header row

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 9:  # Ensure we have all columns
                try:
                    school_name = cells[0].text.strip()
                    state = cells[1].text.strip()
                    total_enrollment = cells[2].text.strip()
                    median_mcat = cells[3].text.strip()
                    median_gpa = cells[4].text.strip()
                    acceptance_rate = cells[5].text.strip()
                    in_state_rate = cells[6].text.strip()
                    out_state_rate = cells[7].text.strip()
                    in_state_advantage = cells[8].text.strip()

                    # Skip rows with no data or "unknown"
                    if not school_name or school_name.lower() in ['name', ''] or acceptance_rate.lower() == 'unknown':
                        continue

                    # Parse percentages, handling empty strings
                    def parse_percentage(text):
                        if not text or text.lower() == 'unknown':
                            return None
                        # Remove % and convert to float
                        text = text.strip('%').strip()
                        try:
                            return float(text)
                        except ValueError:
                            return None

                    in_state_pct = parse_percentage(in_state_rate)
                    out_state_pct = parse_percentage(out_state_rate)

                    accepted_data.append({
                        'school_name': school_name,
                        'state': state,
                        'total_enrollment': total_enrollment,
                        'median_mcat': median_mcat,
                        'median_gpa': median_gpa,
                        'overall_acceptance_rate': acceptance_rate,
                        'in_state_acceptance_rate': in_state_pct,
                        'out_state_acceptance_rate': out_state_pct,
                        'in_state_advantage': in_state_advantage
                    })

                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue

        print(f"Scraped {len(accepted_data)} schools from Accepted.com")

        # Show sample data
        if accepted_data:
            print("Sample scraped data:")
            for school in accepted_data[:3]:
                print(f"- {school['school_name']} ({school['state']}): In-state: {school['in_state_acceptance_rate']}%, Out-of-state: {school['out_state_acceptance_rate']}%")

        return pd.DataFrame(accepted_data)

    except Exception as e:
        print(f"Error scraping Accepted.com: {e}")
        return None

def match_schools(existing_df, accepted_df):
    """Match schools between existing data and Accepted.com data with improved matching"""
    matched_data = []
    used_matches = set()  # Track which Accepted.com entries have been used

    for idx, row in existing_df.iterrows():
        existing_name = row['Medical School Name']
        existing_state = row['State']

        # Clean names for matching
        clean_existing = clean_school_name(existing_name)

        # Find best match in Accepted data
        best_match = None
        best_score = 0
        best_match_idx = -1

        for aamc_idx, aamc_row in accepted_df.iterrows():
            if aamc_idx in used_matches:
                continue

            aamc_name = aamc_row['school_name']
            aamc_state = aamc_row['state']

            clean_aamc = clean_school_name(aamc_name)

            # Calculate different matching scores
            name_score = fuzz.ratio(clean_existing, clean_aamc)
            partial_score = fuzz.partial_ratio(clean_existing, clean_aamc)
            token_score = fuzz.token_sort_ratio(clean_existing, clean_aamc)

            # Use the highest of the three scores
            score = max(name_score, partial_score, token_score)

            # Bonus for state match
            if aamc_state == existing_state:
                score += 15

            # Bonus for high partial match (good for long names)
            if partial_score > 85:
                score += 10

            if score > best_score:
                best_score = score
                best_match = aamc_row
                best_match_idx = aamc_idx

        # Very lenient matching criteria to maximize coverage
        partial_ratio = fuzz.partial_ratio(clean_existing, clean_school_name(best_match['school_name']))
        should_match = (
            best_score > 60 or  # Good overall match
            (best_score > 45 and existing_state == best_match['state']) or  # Decent match with state confirmation
            partial_ratio > 85 or  # Very strong partial match
            (partial_ratio > 75 and len(clean_existing) > 10 and len(clean_school_name(best_match['school_name'])) > 10)  # Strong partial for longer names
        )

        if best_match is not None and should_match:
            matched_row = row.copy()
            matched_row['In-State Acceptance Rate %'] = best_match['in_state_acceptance_rate']
            matched_row['Out-of-State Acceptance Rate %'] = best_match['out_state_acceptance_rate']
            matched_row['In-State Advantage'] = best_match['in_state_advantage']
            matched_row['Match Score'] = best_score
            matched_data.append(matched_row)
            used_matches.add(best_match_idx)  # Mark this match as used
        else:
            # No match found, add with None values
            matched_row = row.copy()
            matched_row['In-State Acceptance Rate %'] = None
            matched_row['Out-of-State Acceptance Rate %'] = None
            matched_row['In-State Advantage'] = None
            matched_row['Match Score'] = None
            matched_data.append(matched_row)

    return pd.DataFrame(matched_data)

def main():
    # Load existing medical schools data
    existing_df = pd.read_csv('/Users/itaysolomon/medical-school-advisor/public/medical_schools_data.csv')

    print(f"Loaded {len(existing_df)} schools from existing database")

    # Scrape Accepted.com data
    accepted_df = scrape_accepted_data()

    if accepted_df is None:
        print("Failed to scrape Accepted.com data")
        return

    print(f"Scraped {len(accepted_df)} schools from Accepted.com")

    # Match schools and add in-state/out-of-state data
    matched_df = match_schools(existing_df, accepted_df)

    # Save updated data
    output_file = '/Users/itaysolomon/medical-school-advisor/public/medical_schools_data_with_rates.csv'
    matched_df.to_csv(output_file, index=False)

    # Summary statistics
    matched_count = matched_df['In-State Acceptance Rate %'].notna().sum()
    print(f"\nMatching Results:")
    print(f"- Total schools: {len(matched_df)}")
    print(f"- Schools with acceptance rate data: {matched_count}")
    print(f"- Match rate: {matched_count/len(matched_df)*100:.1f}%")

    # Show sample matches
    print("\nSample matches with acceptance rates:")
    sample_matches = matched_df[matched_df['In-State Acceptance Rate %'].notna()].head(5)
    for idx, row in sample_matches.iterrows():
        print(f"- {row['Medical School Name']} ({row['State']}): In-state: {row['In-State Acceptance Rate %']}%, Out-of-state: {row['Out-of-State Acceptance Rate %']}%, Advantage: {row['In-State Advantage']}")

    print(f"\nUpdated data saved to: {output_file}")

if __name__ == "__main__":
    main()