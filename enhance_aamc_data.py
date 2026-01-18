import pandas as pd
import re

# Additional AAMC matriculation data from the external links
# Format: 'School Name': (in_state_pct, out_state_pct, advantage)
additional_aamc_data = {
    # From external links - adding more schools
    'Yale School of Medicine': (6.7, 93.3, 'none'),
    'Harvard Medical School': (12.3, 87.7, 'none'),
    'Stanford University School of Medicine': (32.6, 67.4, 'none'),
    'Columbia University Vagelos College of Physicians & Surgeons': (17.4, 82.6, 'none'),
    'Cornell University (Weill)': (30.2, 69.8, 'none'),
    'New York Medical College': (49.2, 50.8, 'none'),
    'SUNY Downstate Medical Center College of Medicine': (85.5, 14.5, 'huge'),
    'SUNY Upstate Medical University Alan & Marlene Norton College of Medicine': (77.1, 22.9, 'huge'),
    'SUNY Upstate': (77.1, 22.9, 'huge'),
    'Zucker Hofstra Northwell': (79.6, 20.4, 'huge'),
    'Renaissance Stony Brook': (79.6, 20.4, 'huge'),
    'Stony Brook': (79.6, 20.4, 'huge'),
    'George Washington University School of Medicine & Health Sciences': (2.2, 97.8, 'none'),
    'Georgetown University School of Medicine': (2.5, 97.5, 'none'),
    'Howard University College of Medicine': (2.4, 97.6, 'none'),
    'Eastern Virginia Medical School': (50.3, 49.7, 'none'),
    'Virginia': (46.2, 53.8, 'none'),
    'Virginia Commonwealth University': (53.8, 46.2, 'material'),
    'Virginia Tech Carilion School of Medicine': (16.0, 84.0, 'none'),
    'East Tennessee State U. (Quillen College of Medicine)': (81.8, 18.2, 'huge'),
    'East Tennessee': (81.8, 18.2, 'huge'),
    'Tennessee': (90.2, 9.8, 'huge'),
    'Vanderbilt University School of Medicine': (10.5, 89.5, 'none'),
    'Meharry Medical College': (18.1, 81.9, 'none'),
    'Mercer University School of Medicine': (100.0, 0.0, 'huge'),
    'Morehouse School of Medicine': (68.2, 31.8, 'material'),
    'Emory University School of Medicine': (39.6, 60.4, 'none'),
    'MC Georgia Augusta': (99.6, 0.4, 'huge'),
    'Augusta': (99.6, 0.4, 'huge'),
    'Medical College of Georgia at Augusta University': (99.6, 0.4, 'huge'),
    'Michigan State University College of Human Medicine': (79.4, 20.6, 'huge'),
    'Oakland University William Beaumont School of Medicine': (55.2, 44.8, 'material'),
    'Wayne State University School of Medicine': (62.3, 37.7, 'material'),
    'Western Michigan University Homer Stryker MD School of Medicine': (39.3, 60.7, 'none'),
    'Central Michigan University College of Medicine': (76.9, 23.1, 'huge'),
    'Mississippi': (100.0, 0.0, 'huge'),
    'Missouri Columbia': (83.6, 16.4, 'huge'),
    'Missouri Kansas City': (64.0, 36.0, 'material'),
    'Saint Louis': (33.7, 66.3, 'none'),
    'Washington U St Louis': (5.6, 94.4, 'none'),
    'Creighton University School of Medicine': (4.0, 96.0, 'none'),
    'Nebraska': (79.5, 20.5, 'huge'),
    'Nevada Reno': (82.9, 17.1, 'huge'),
    'UNLV-Kerkorian': (72.7, 27.3, 'huge'),
    'New Mexico': (93.5, 6.5, 'huge'),
    'North Carolina': (88.2, 11.8, 'huge'),
    'East Carolina-Brody': (99.7, 0.3, 'huge'),
    'Wake Forest School of Medicine': (38.6, 61.4, 'none'),
    'North Dakota': (48.6, 51.4, 'none'),
    'Oklahoma': (90.9, 9.1, 'huge'),
    'Oregon': (72.0, 28.0, 'huge'),
    'Pennsylvania-Perelman': (11.5, 88.5, 'none'),
    'Drexel University College of Medicine': (32.6, 67.4, 'none'),
    'Jefferson-Kimmel': (28.7, 71.3, 'none'),
    'Penn State': (31.0, 69.0, 'none'),
    'Pittsburgh': (37.8, 62.2, 'none'),
    'Temple-Katz': (38.3, 61.7, 'huge'),
    'Brown-Alpert': (11.1, 88.9, 'none'),
    'Caribe': (85.7, 14.3, 'huge'),
    'Ponce': (65.0, 35.0, 'material'),
    'Puerto Rico': (98.0, 2.0, 'huge'),
    'San Juan Bautista': (46.9, 53.1, 'none'),
    'MU South Carolina': (91.3, 8.7, 'huge'),
    'South Carolina Columbia': (75.0, 25.0, 'huge'),
    'South Carolina Greenville': (70.0, 30.0, 'huge'),
    'East Tennessee-Quillen': (81.8, 18.2, 'huge'),
    'Meharry': (18.1, 81.9, 'none'),
    'Tennessee': (90.2, 9.8, 'huge'),
    'Texas A&M': (86.4, 13.6, 'material'),
    'Texas Tech': (90.1, 9.9, 'huge'),
    'Texas Tech-Foster': (94.4, 5.6, 'huge'),
    'UT Austin-Dell': (90.0, 10.0, 'huge'),
    'UT Houston-McGovern': (95.0, 5.0, 'huge'),
    'UT Medical Branch-Sealy': (94.3, 5.7, 'huge'),
    'UT Rio Grande Valley': (92.5, 7.5, 'huge'),
    'UT San Antonio-Long': (88.4, 11.6, 'material'),
    'UT Southwestern': (87.1, 12.9, 'material'),
    'UT Tyler': (98.8, 1.2, 'huge'),
    'TCU-Burnett': (50.0, 50.0, 'none'),
    'Houston-Fertitta': (54.0, 46.0, 'material'),
    'U Washington': (53.5, 46.5, 'material'),
    'Washington State-Floyd': (88.8, 11.3, 'huge'),
    'MC Wisconsin': (52.3, 47.7, 'material'),
    'Wisconsin': (68.4, 31.6, 'material'),
    'Marshall-Edwards': (56.9, 43.1, 'material'),
    'West Virginia': (69.6, 30.4, 'material'),
    'Robert Larner': (27.0, 73.0, 'none'),
    'Vermont-Larner': (27.0, 73.0, 'none'),
    'Utah-Eccles': (72.8, 27.2, 'huge'),
}

def clean_school_name(name):
    """Clean school names for matching"""
    name = str(name).strip()
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'^university of ', '', name, flags=re.IGNORECASE)
    name = re.sub(r' college of medicine$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' school of medicine$', '', name, flags=re.IGNORECASE)
    name = re.sub(r' medical college$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+school$', '', name, flags=re.IGNORECASE)
    return name.lower().strip()

def enhance_with_additional_data():
    """Add more AAMC matriculation data to the CSV"""
    # Load current data
    df = pd.read_csv('/Users/itaysolomon/medical-school-advisor/public/medical_schools_data.csv')

    added_count = 0

    for idx, row in df.iterrows():
        school_name = row['Medical School Name']

        # Check if school already has matriculation data
        if pd.isna(row['In-State Matriculants %']):
            # Try exact match first
            if school_name in additional_aamc_data:
                in_state, out_state, advantage = additional_aamc_data[school_name]
                df.at[idx, 'In-State Matriculants %'] = in_state
                df.at[idx, 'Out-of-State Matriculants %'] = out_state
                df.at[idx, 'In-State Advantage'] = advantage
                added_count += 1
                continue

            # Try fuzzy matching
            clean_target = clean_school_name(school_name)
            for aamc_school, (in_state, out_state, advantage) in additional_aamc_data.items():
                clean_aamc = clean_school_name(aamc_school)
                if clean_target == clean_aamc or clean_target in clean_aamc or clean_aamc in clean_target:
                    df.at[idx, 'In-State Matriculants %'] = in_state
                    df.at[idx, 'Out-of-State Matriculants %'] = out_state
                    df.at[idx, 'In-State Advantage'] = advantage
                    added_count += 1
                    break

    # Save enhanced data
    df.to_csv('/Users/itaysolomon/medical-school-advisor/public/medical_schools_data_enhanced.csv', index=False)

    print(f"Added matriculation data for {added_count} additional schools")

    # Summary
    with_data = df.dropna(subset=['In-State Matriculants %'])
    print(f"Total schools with matriculation data: {len(with_data)}/{len(df)} ({len(with_data)/len(df)*100:.1f}%)")

    # Check Yale
    yale = df[df['Medical School Name'].str.contains('Yale', case=False)]
    if not yale.empty:
        yale_row = yale.iloc[0]
        in_rate = yale_row['In-State Matriculants %']
        out_rate = yale_row['Out-of-State Matriculants %']
        print(f"Yale: In: {in_rate}% Out: {out_rate}%")

if __name__ == "__main__":
    enhance_with_additional_data()