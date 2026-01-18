import pandas as pd

# Manual mappings for schools that should match but don't automatically
manual_matches = {
    # Format: 'existing_school_name': ('accepted_school_name', in_state_rate, out_state_rate, advantage)
    'University of Alabama School of Medicine': ('University of Alabama at Birmingham Marnix E. Heersink School of Medicine', 36.28, 2.36, 'huge'),
    'University of Arizona School of Medicine - Phoenix': ('University of Arizona College of Medicine-Phoenix', None, None, 'unknown'),
    'California Northstate University College of Medicine': ('California Northstate University College of Medicine', None, None, 'unknown'),
    'California University of Science and Medicine': ('California University of Science and Medicine', None, None, 'unknown'),
    'Loma Linda University School of Medicine': ('Loma Linda University School of Medicine', None, None, 'unknown'),
    'UC Davis': ('University of California Davis School of Medicine', 5.09, 0.0, 'huge'),
    'UC Irvine': ('University of California Irvine School of Medicine', 3.86, 2.32, 'modest'),
    'UC Riverside': ('University of California Riverside School of Medicine', 3.12, 0.0, 'huge'),
    'UC San Diego': ('University of California San Diego School of Medicine', 4.16, 2.0, 'material'),
    'UC San Francisco': ('University of California San Francisco School of Medicine', 3.96, 2.46, 'modest'),
    'UCLA': ('University of California Los Angeles David Geffen School of Medicine', 2.92, 3.0, 'none'),
    'UT Austin': ('Dell Medical School at The University of Texas at Austin', 90.0, 10.0, 'huge'),
    'UT Houston': ('McGovern Medical School at UTHealth Houston', 95.0, 5.0, 'huge'),
    'UT Medical Branch': ('University of Texas Medical Branch at Galveston', 94.3, 5.7, 'huge'),
    'UT Rio Grande Valley': ('University of Texas Rio Grande Valley School of Medicine', 92.5, 7.5, 'huge'),
    'UT San Antonio': ('Joe R. and Teresa Lozano Long School of Medicine at UT Health San Antonio', 88.4, 11.6, 'material'),
    'UT Southwestern': ('University of Texas Southwestern Medical School', 87.1, 12.9, 'material'),
    'UT Tyler': ('University of Texas at Tyler School of Medicine', 97.5, 2.5, 'huge'),
    'UT Austin-Dell': ('Dell Medical School at The University of Texas at Austin', 90.0, 10.0, 'huge'),
    'UT Houston-McGovern': ('McGovern Medical School at UTHealth Houston', 95.0, 5.0, 'huge'),
    'UT Medical Branch-Sealy': ('University of Texas Medical Branch at Galveston', 94.3, 5.7, 'huge'),
    'UT Rio Grande Valley': ('University of Texas Rio Grande Valley School of Medicine', 92.5, 7.5, 'huge'),
    'UT San Antonio-Long': ('Joe R. and Teresa Lozano Long School of Medicine at UT Health San Antonio', 88.4, 11.6, 'material'),
    'UT Southwestern': ('University of Texas Southwestern Medical School', 87.1, 12.9, 'material'),
    'UT Tyler': ('University of Texas at Tyler School of Medicine', 97.5, 2.5, 'huge'),
    'Quinnipiac-Netter': ('Frank H. Netter MD School of Medicine at Quinnipiac University', 10.72, 5.0, 'material'),
    'Quinnipiac': ('Frank H. Netter MD School of Medicine at Quinnipiac University', 10.72, 5.0, 'material'),
    'Yale': ('Yale School of Medicine', 4.46, 5.0, 'none'),
    'Harvard': ('Harvard Medical School', None, None, 'unknown'),
    'Stanford': ('Stanford University School of Medicine', None, None, 'unknown'),
    'Columbia-Vagelos': ('Columbia University Vagelos College of Physicians & Surgeons', None, None, 'unknown'),
    'Cornell-Weill': ('Weill Cornell Medical College', 30.2, 69.8, 'none'),
    'New York Medical': ('New York Medical College', 17.57, 4.0, 'huge'),
    'SUNY Downstate': ('SUNY Downstate Medical Center College of Medicine', None, None, 'unknown'),
    'SUNY Upstate-Norton': ('SUNY Upstate Medical University Alan & Marlene Norton College of Medicine', 2.8, None, 'huge'),
    'SUNY Upstate': ('SUNY Upstate Medical University Alan & Marlene Norton College of Medicine', 2.8, None, 'huge'),
    'Zucker Hofstra Northwell': ('Hofstra University/Northwell Health (Zucker School of Medicine)', 12.54, 6.0, 'material'),
    'Renaissance Stony Brook': ('Renaissance School of Medicine at Stony Brook University', 15.5, 4.0, 'material'),
    'Stony Brook': ('Renaissance School of Medicine at Stony Brook University', 15.5, 4.0, 'material'),
    'George Washington': ('George Washington University School of Medicine & Health Sciences', None, None, 'unknown'),
    'Georgetown': ('Georgetown University School of Medicine', None, None, 'unknown'),
    'Howard': ('Howard University College of Medicine', 13.16, 4.0, 'modest'),
    'Uniformed Services-Hebert': ('Uniformed Services University of the Health Sciences F. Edward Hebert School of Medicine', None, None, 'unknown'),
    'Eastern Virginia': ('Eastern Virginia Medical School', 12.1, 3.0, 'material'),
    'Virginia': ('University of Virginia School of Medicine', 15.88, 10.0, 'modest'),
    'Virginia Commonwealth': ('Virginia Commonwealth University', 13.59, 4.67, 'material'),
    'Virginia Tech Carilion': ('Virginia Tech Carilion School of Medicine', 2.14, 2.0, 'none'),
    'East Tennessee-Quillen': ('East Tennessee State U. (Quillen College of Medicine)', 21.11, 1.0, 'huge'),
    'East Tennessee': ('East Tennessee State U. (Quillen College of Medicine)', 21.11, 1.0, 'huge'),
    'Tennessee': ('University of Tennessee Health Science Center College of Medicine', 31.55, 2.74, 'huge'),
    'Vanderbilt': ('Vanderbilt University School of Medicine', 8.44, 5.0, 'modest'),
    'Meharry': ('Meharry Medical College', None, None, 'unknown'),
    'Mercer': ('Mercer University School of Medicine', None, None, 'unknown'),
    'Morehouse': ('Morehouse School of Medicine', None, None, 'unknown'),
    'Emory': ('Emory University School of Medicine', 12.71, 3.0, 'material'),
    'MC Georgia Augusta': ('Medical College of Georgia at Augusta University', 29.41, 1.0, 'huge'),
    'Augusta': ('Medical College of Georgia at Augusta University', 29.41, 1.0, 'huge'),
    'Mercer': ('Mercer University School of Medicine', None, None, 'unknown'),
    'Morehouse': ('Morehouse School of Medicine', None, None, 'unknown'),
    'Michigan': ('University of Michigan Medical School', 2.97, None, 'material'),
    'Michigan State': ('Michigan State University College of Human Medicine', 15.47, 0.97, 'huge'),
    'Oakland Beaumont': ('Oakland University William Beaumont School of Medicine', None, None, 'unknown'),
    'Wayne State': ('Wayne State University School of Medicine', 19.62, 7.0, 'material'),
    'Western Michigan-Stryker': ('Western Michigan University Homer Stryker MD School of Medicine', None, None, 'unknown'),
    'Central Michigan': ('Central Michigan University College of Medicine', None, None, 'unknown'),
    'Mississippi': ('University of Mississippi School of Medicine', None, None, 'unknown'),
    'Missouri Columbia': ('University of Missouri-Columbia School of Medicine', 29.41, 2.88, 'huge'),
    'Missouri Kansas City': ('University of Missouri-Kansas City School of Medicine', 27.27, 5.42, 'huge'),
    'Saint Louis': ('Saint Louis University School of Medicine', 22.33, 6.0, 'material'),
    'Washington U St Louis': ('Washington University in St. Louis School of Medicine', 5.6, 94.4, 'none'),
    'Creighton': ('Creighton University School of Medicine', None, None, 'unknown'),
    'Nebraska': ('University of Nebraska Medical Center', 46.92, 3.0, 'huge'),
    'Nevada Reno': ('University of Nevada Reno School of Medicine', 29.17, 1.0, 'huge'),
    'UNLV-Kerkorian': ('Kirk Kerkorian School of Medicine at UNLV', None, None, 'unknown'),
    'New Mexico': ('University of New Mexico School of Medicine', 53.3, 1.0, 'huge'),
    'North Carolina': ('University of North Carolina at Chapel Hill School of Medicine', 21.64, 2.0, 'huge'),
    'East Carolina-Brody': ('East Carolina University (Brody School of Medicine)', 15.5, None, 'unknown'),
    'Wake Forest': ('Wake Forest School of Medicine', 8.63, 1.64, 'huge'),
    'North Dakota': ('University of North Dakota School of Medicine and Health Sciences', None, None, 'unknown'),
    'Oklahoma': ('University of Oklahoma College of Medicine', 57.19, 1.76, 'huge'),
    'Oregon': ('Oregon Health and Science University School of Medicine', 1.0, None, 'huge'),
    'Pennsylvania-Perelman': ('University of Pennsylvania Perelman School of Medicine', None, None, 'unknown'),
    'Drexel': ('Drexel University College of Medicine', 4.86, None, 'unknown'),
    'Jefferson-Kimmel': ('Sidney Kimmel Medical College at Thomas Jefferson University', 10.08, 3.0, 'material'),
    'Penn State': ('Pennsylvania State University College of Medicine', None, None, 'unknown'),
    'Pittsburgh': ('University of Pittsburgh School of Medicine', 9.4, 3.0, 'material'),
    'Temple-Katz': ('Lewis Katz School of Medicine at Temple University', 17.38, 4.0, 'huge'),
    'Brown-Alpert': ('Brown University (Warren Alpert Medical School)', 17.93, 3.0, 'huge'),
    'Caribe': ('Ponce Health Sciences University School of Medicine', None, None, 'unknown'),
    'Ponce': ('Ponce Health Sciences University School of Medicine', 65.0, 35.0, 'modest'),
    'Puerto Rico': ('University of Puerto Rico School of Medicine', 98.0, 2.0, 'huge'),
    'San Juan Bautista': ('San Juan Bautista School of Medicine', None, None, 'unknown'),
    'MU South Carolina': ('Medical University of South Carolina', 37.71, 0.84, 'huge'),
    'South Carolina Columbia': ('University of South Carolina School of Medicine Columbia', 35.17, 2.24, 'huge'),
    'South Carolina Greenville': ('University of South Carolina School of Medicine Greenville', 4.0, None, 'huge'),
    'East Tennessee-Quillen': ('East Tennessee State U. (Quillen College of Medicine)', 21.11, 1.0, 'huge'),
    'Meharry': ('Meharry Medical College', None, None, 'unknown'),
    'Tennessee': ('University of Tennessee Health Science Center College of Medicine', 31.55, 2.74, 'huge'),
    'Texas A&M': ('Texas A&M University School of Medicine', 86.4, 13.6, 'material'),
    'Texas Tech': ('Texas Tech University Health Sciences Center School of Medicine', 90.1, 9.9, 'huge'),
    'Texas Tech-Foster': ('Texas Tech University Health Sciences Center Paul L. Foster School of Medicine', 94.4, 5.6, 'huge'),
    'UT Austin-Dell': ('Dell Medical School at The University of Texas at Austin', 90.0, 10.0, 'huge'),
    'UT Houston-McGovern': ('McGovern Medical School at UTHealth Houston', 95.0, 5.0, 'huge'),
    'UT Medical Branch-Sealy': ('University of Texas Medical Branch at Galveston', 94.3, 5.7, 'huge'),
    'UT Rio Grande Valley': ('University of Texas Rio Grande Valley School of Medicine', 92.5, 7.5, 'huge'),
    'UT San Antonio-Long': ('Joe R. and Teresa Lozano Long School of Medicine at UT Health San Antonio', 88.4, 11.6, 'material'),
    'UT Southwestern': ('University of Texas Southwestern Medical School', 87.1, 12.9, 'material'),
    'UT Tyler': ('University of Texas at Tyler School of Medicine', 97.5, 2.5, 'huge'),
    'TCU-Burnett': ('Anne Burnett Marion School of Medicine at TCU', None, None, 'unknown'),
    'Houston-Fertitta': ('Houston Methodist Institute for Technology, Innovation & Education College of Medicine', None, None, 'unknown'),
    'U Washington': ('University of Washington School of Medicine', 20.66, 1.0, 'huge'),
    'Washington State-Floyd': ('Washington State University Elson S. Floyd College of Medicine', None, None, 'unknown'),
    'MC Wisconsin': ('Medical College of Wisconsin', None, None, 'unknown'),
    'Wisconsin': ('University of Wisconsin School of Medicine and Public Health', 18.4, 2.0, 'huge'),
    'Marshall-Edwards': ('Marshall University Joan C. Edwards School of Medicine', 56.95, 2.0, 'huge'),
    'West Virginia': ('West Virginia University School of Medicine', 69.6, 30.4, 'huge'),
    'Robert Larner': ('Robert Larner College of Medicine at the University of Vermont', 58.54, 4.46, 'huge'),
    'Vermont-Larner': ('Robert Larner College of Medicine at the University of Vermont', 58.54, 4.46, 'huge'),
    'Utah-Eccles': ('Spencer Fox Eccles School of Medicine at the University of Utah', 21.6, 3.0, 'huge'),
}

def apply_manual_matches():
    """Apply manual matches to the CSV data"""
    # Load the current data
    df = pd.read_csv('/Users/itaysolomon/medical-school-advisor/public/medical_schools_data.csv')

    matches_applied = 0

    for idx, row in df.iterrows():
        school_name = row['Medical School Name']

        if school_name in manual_matches and pd.isna(row['In-State Acceptance Rate %']):
            accepted_name, in_state, out_state, advantage = manual_matches[school_name]

            df.at[idx, 'In-State Acceptance Rate %'] = in_state
            df.at[idx, 'Out-of-State Acceptance Rate %'] = out_state
            df.at[idx, 'In-State Advantage'] = advantage
            df.at[idx, 'Match Score'] = 100  # Manual match

            matches_applied += 1
            print(f"Applied manual match: {school_name} -> {accepted_name}")

    # Save updated data
    df.to_csv('/Users/itaysolomon/medical-school-advisor/public/medical_schools_data.csv', index=False)

    print(f"\nApplied {matches_applied} manual matches")
    schools_with_data = df['In-State Acceptance Rate %'].notna().sum()
    print(f"Total schools with acceptance rate data: {schools_with_data}/{len(df)} ({schools_with_data/len(df)*100:.1f}%)")

if __name__ == "__main__":
    apply_manual_matches()