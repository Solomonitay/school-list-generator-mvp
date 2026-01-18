import pandas as pd
import requests
import io
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pdfplumber
import tempfile
import os

def clean_school_name(name):
    """Clean school names for better matching"""
    name = str(name).strip()
    # Remove common prefixes/suffixes that might differ
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'^university of ', '', name, flags=re.IGNORECASE)
    name = re.sub(r' college of medicine$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' school of medicine$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' medical college$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+school$', '', name, flags=re.IGNORECASE)
    return name.lower().strip()

def download_aamc_data(url):
    """Download and parse AAMC PDF data using text extraction and regex"""
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Save PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        # Parse PDF with pdfplumber - extract text instead of tables
        all_text = ""

        with pdfplumber.open(temp_file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"

        # Clean up temporary file
        os.unlink(temp_file_path)

        # Parse the text using regex patterns
        aamc_data = []

        # Split text into lines
        lines = all_text.split('\n')

        # Print sample lines for debugging
        print("Sample text lines:")
        data_lines = [line for line in lines if line.strip() and len(line.split()) > 8][:5]
        for i, line in enumerate(data_lines):
            print(f"  Line {i}: {line}")

        # More flexible pattern to match school entries
        # Looking for lines with state codes and matriculant percentages
        pattern = r'^([A-Z]{2})\s+(.+?)\s+\d+(?:,\d+)?\s+\d+(?:\.\d+)?(?:\s+\d+(?:\.\d+)?)*?\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)(?:\s+\d+(?:\.\d+)?)*?$'

        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = re.match(pattern, line)
            if match:
                state, school_name = match.groups()[:2]
                matric_pcts = match.groups()[2:]

                # Skip header-like lines
                if any(header in school_name.lower() for header in ['school', 'state', 'applications', 'matriculants', 'total', 'by in state', 'by gender']):
                    continue

                # Extract the matriculants in-state and out-of-state percentages
                # Table structure: State, School, AppsTotal, AppsIn%, AppsOut%, AppsMen%, AppsWomen%, MatricTotal, MatricIn%, MatricOut%, MatricMen%, MatricWomen%
                try:
                    parts = line.split()
                    if len(parts) >= 12:  # Ensure we have the full row
                        # Matriculants in-state % should be at index 9, out-of-state % at index 10
                        try:
                            matric_in_state_idx = 8  # 0-indexed: State(0), School(1), AppsTotal(2), AppsIn(3), AppsOut(4), AppsMen(5), AppsWomen(6), MatricTotal(7), MatricIn(8), MatricOut(9), MatricMen(10), MatricWomen(11)
                            matric_out_state_idx = 9

                            in_state_matric_pct = float(parts[matric_in_state_idx])
                            out_state_matric_pct = float(parts[matric_out_state_idx])

                            # Validate percentages
                            if 0 <= in_state_matric_pct <= 100 and 0 <= out_state_matric_pct <= 100:
                                # Clean up school name by removing any trailing numbers
                                school_name = re.sub(r'\s+\d+(?:,\d+)?\s*$', '', school_name).strip()

                                aamc_data.append({
                                    'school_name': school_name,
                                    'state': state,
                                    'in_state_matriculants_pct': in_state_matric_pct,
                                    'out_state_matriculants_pct': out_state_matric_pct
                                })
                        except (ValueError, IndexError):
                            # If direct indexing fails, try to find the matriculants section
                            pass
                except Exception as e:
                    print(f"Error parsing line '{line}': {e}")
                    continue

        print(f"Extracted {len(aamc_data)} schools from AAMC PDF text")

        # Show sample data
        if aamc_data:
            print("Sample extracted data:")
            for school in aamc_data[:5]:
                print(f"- {school['school_name']} ({school['state']}): {school['in_state_matriculants_pct']}% in-state, {school['out_state_matriculants_pct']}% out-of-state")

        return pd.DataFrame(aamc_data)

    except Exception as e:
        print(f"Error downloading/parsing AAMC PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def match_schools(existing_df, aamc_df):
    """Match schools between existing data and AAMC data"""
    matched_data = []

    for idx, row in existing_df.iterrows():
        existing_name = row['Medical School Name']
        existing_state = row['State']

        # Clean names for matching
        clean_existing = clean_school_name(existing_name)

        # Find best match in AAMC data
        best_match = None
        best_score = 0

        for aamc_idx, aamc_row in aamc_df.iterrows():
            aamc_name = aamc_row['school_name']
            aamc_state = aamc_row['state']

            # Try exact state match first
            if aamc_state == existing_state:
                clean_aamc = clean_school_name(aamc_name)
                score = fuzz.ratio(clean_existing, clean_aamc)

                if score > best_score:
                    best_score = score
                    best_match = aamc_row

        # Use match if score is high enough (adjust threshold as needed)
        if best_match is not None and best_score > 70:
            matched_row = row.copy()
            matched_row['In-State Matriculants %'] = best_match['in_state_matriculants_pct']
            matched_row['Out-of-State Matriculants %'] = best_match['out_state_matriculants_pct']
            matched_row['Match Score'] = best_score
            matched_data.append(matched_row)
        else:
            # No match found, add with None values
            matched_row = row.copy()
            matched_row['In-State Matriculants %'] = None
            matched_row['Out-of-State Matriculants %'] = None
            matched_row['Match Score'] = None
            matched_data.append(matched_row)

    return pd.DataFrame(matched_data)

def main():
    # URL from AAMC
    aamc_url = "https://www.aamc.org/media/5976/download"

    # Load existing medical schools data
    existing_df = pd.read_csv('/Users/itaysolomon/medical-school-advisor/public/medical_schools_data.csv')

    print(f"Loaded {len(existing_df)} schools from existing database")

    # Download and parse AAMC data
    aamc_df = download_aamc_data(aamc_url)

    if aamc_df is None:
        print("Failed to download AAMC data")
        return

    print(f"Downloaded {len(aamc_df)} schools from AAMC")

    # Match schools and add in-state/out-of-state data
    matched_df = match_schools(existing_df, aamc_df)

    # Save updated data
    output_file = '/Users/itaysolomon/medical-school-advisor/public/medical_schools_data_updated.csv'
    matched_df.to_csv(output_file, index=False)

    # Summary statistics
    matched_count = matched_df['In-State Matriculants %'].notna().sum()
    print(f"\nMatching Results:")
    print(f"- Total schools: {len(matched_df)}")
    print(f"- Schools with in-state data: {matched_count}")
    print(f"- Match rate: {matched_count/len(matched_df)*100:.1f}%")

    # Show sample matches
    print("\nSample matches:")
    sample_matches = matched_df[matched_df['In-State Matriculants %'].notna()].head(5)
    for idx, row in sample_matches.iterrows():
        print(f"- {row['Medical School Name']} ({row['State']}): {row['In-State Matriculants %']}% in-state, {row['Out-of-State Matriculants %']}% out-of-state")

    print(f"\nUpdated data saved to: {output_file}")

if __name__ == "__main__":
    main()