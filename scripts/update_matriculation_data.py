#!/usr/bin/env python3
"""
Update medical school CSV with in-state/out-of-state matriculation data from AAMC FACTS.
"""

import pandas as pd
import os

# Manual mapping from FACTS school names to CSV school names
SCHOOL_MAPPING = {
    # Alabama
    "Alabama-Heersink": "University of Alabama School of Medicine",
    "South Alabama-Whiddon": "University of South Alabama College of Medicine",
    
    # Arizona
    "Arizona": "University of Arizona College of Medicine - Tucson",
    "Arizona Phoenix": "University of Arizona School of Medicine - Phoenix",
    
    # California
    "California Northstate": "California Northstate University College of Medicine",
    "Drew": "Charles R. Drew University of Medicine and Science",
    "Kaiser Permanente-Tyson": "Kaiser Permanente School of Medicine",
    "Loma Linda": "Loma Linda University School of Medicine",
    "Southern Cal-Keck": "University of Southern California Keck School of Medicine",
    "Stanford": "Stanford University School of Medicine",
    "UC Davis": "University of California – Davis School of Medicine",
    "UC Irvine": "University of California – Irvine School of Medicine",
    "UC Riverside": "University of California – Riverside School of Medicine",
    "UC San Diego": "University of California – San Diego School of Medicine",
    "UC San Francisco": "University of California – San Francisco School of Medicine",
    "UCLA-Geffen": "University of California – Los Angeles David Geffen School of Medicine",
    
    # Colorado
    "Colorado": "University of Colorado School of Medicine",
    
    # Connecticut
    "Connecticut": "University of Connecticut School of Medicine",
    "Quinnipiac-Netter": "Quinnipiac University Frank H. Netter MD School of Medicine",
    "Yale": "Yale School of Medicine",
    
    # DC
    "George Washington": "George Washington University School of Medicine and Health Sciences",
    "Georgetown": "Georgetown University School of Medicine",
    "Howard": "Howard University College of Medicine",
    
    # Florida
    "FIU-Wertheim": "Florida International University Herbert Wertheim College of Medicine",
    "Florida": "University of Florida College of Medicine",
    "Florida Atlantic-Schmidt": "Florida Atlantic University Charles E. Schmidt College of Medicine",
    "Florida State": "Florida State University College of Medicine",
    "Miami-Miller": "University of Miami Miller School of Medicine",
    "Nova Southeastern-Patel": "Nova Southeastern University Dr. Kiran C. Patel College of Allopathic Medicine",
    "UCF": "University of Central Florida College of Medicine",
    "USF-Morsani": "University of South Florida Health Morsani College of Medicine",
    
    # Georgia
    "Emory": "Emory University School of Medicine",
    "MC Georgia Augusta": "Medical College of Georgia at Augusta University",
    "Mercer": "Mercer University School of Medicine",
    "Morehouse": "Morehouse School of Medicine",
    
    # Hawaii
    "Hawaii-Burns": "University of Hawaii John A. Burns School of Medicine",
    
    # Iowa
    "Iowa-Carver": "University of Iowa Carver College of Medicine",
    
    # Illinois
    "Carle Illinois": "Carle Illinois College of Medicine",
    "Chicago Med Franklin": "Chicago Medical School at Rosalind Franklin University of Medicine and Science",
    "Chicago-Pritzker": "University of Chicago Pritzker School of Medicine",
    "Illinois": "University of Illinois College of Medicine",
    "Loyola-Stritch": "Loyola University of Chicago Stritch School of Medicine",
    "Northwestern-Feinberg": "Northwestern University The Feinberg School of Medicine",
    "Rush": "Rush Medical College of Rush University",
    "Southern Illinois": "Southern Illinois University School of Medicine",
    
    # Indiana
    "Indiana": "Indiana University School of Medicine",
    
    # Kansas
    "Kansas": "University of Kansas School of Medicine",
    
    # Kentucky
    "Kentucky": "University of Kentucky College of Medicine",
    "Louisville": "University of Louisville School of Medicine",
    
    # Louisiana
    "LSU New Orleans": "Louisiana State University – New Orleans School of Medicine",
    "LSU Shreveport": "Louisiana State University – Shreveport School of Medicine",
    "Tulane": "Tulane University School of Medicine",
    
    # Massachusetts
    "BU-Chobanian Avedisian": "Boston University School of Medicine",
    "Harvard": "Harvard Medical School",
    "Massachusetts-Chan": "University of Massachusetts Medical School",
    "Tufts": "Tufts University School of Medicine",
    
    # Maryland
    "Johns Hopkins": "Johns Hopkins University School of Medicine",
    "Maryland": "University of Maryland School of Medicine",
    "Uniformed Services-Hebert": "Uniformed Services University of the Health Sciences F. Edward Hebert School of Medicine",
    
    # Michigan
    "Central Michigan": "Central Michigan University College of Medicine",
    "Michigan": "University of Michigan Medical School",
    "Michigan State": "Michigan State University College of Human Medicine",
    "Oakland Beaumont": "Oakland University William Beaumont School of Medicine",
    "Wayne State": "Wayne State University School of Medicine",
    "Western Michigan-Stryker": "Western Michigan University School of Medicine",
    
    # Minnesota
    "Mayo-Alix": "Mayo Clinic Alix School of Medicine",
    "Minnesota": "University of Minnesota Medical School - Twin Cities",
    
    # Missouri
    "Missouri Columbia": "University of Missouri – Columbia School of Medicine",
    "Missouri Kansas City": "University of Missouri – Kansas City School of Medicine",
    "Saint Louis": "Saint Louis University School of Medicine",
    "Washington U St Louis": "Washington University School of Medicine",
    
    # Mississippi
    "Mississippi": "University of Mississippi School of Medicine",
    
    # North Carolina
    "Duke": "Duke University School of Medicine",
    "East Carolina-Brody": "East Carolina University Brody School of Medicine",
    "North Carolina": "University of North Carolina at Chapel Hill School of Medicine",
    "Wake Forest": "Wake Forest School of Medicine",
    
    # North Dakota
    "North Dakota": "University of North Dakota School of Medicine and Health Sciences",
    
    # Nebraska
    "Creighton": "Creighton University School of Medicine",
    "Nebraska": "University of Nebraska Medical Center College of Medicine",
    
    # New Hampshire
    "Dartmouth-Geisel": "Geisel School of Medicine at Dartmouth",
    
    # New Jersey
    "Cooper Rowan": "Cooper Medical School of Rowan University",
    "Hackensack Meridian": "Hackensack Meridian School of Medicine",
    "Rutgers New Jersey": "Rutgers New Jersey Medical School",
    "Rutgers-RW Johnson": "Rutgers Robert Wood Johnson Medical School",
    
    # New Mexico
    "New Mexico": "University of New Mexico School of Medicine",
    
    # Nevada
    "Nevada Reno": "University of Nevada Reno School of Medicine",
    "UNLV-Kerkorian": "University of Nevada Las Vegas School of Medicine",
    
    # New York
    "Albany": "Albany Medical College",
    "Buffalo-Jacobs": "University at Buffalo Jacobs School of Medicine and Biomedical Sciences",
    "Columbia-Vagelos": "Columbia University College of Physicians and Surgeons",
    "Cornell-Weill": "Weill Cornell Medical College",
    "Einstein": "Albert Einstein College of Medicine",
    "Mount Sinai-Icahn": "Icahn School of Medicine at Mount Sinai",
    "NYU Long Island-Grossman": "New York University Long Island School of Medicine",
    "NYU-Grossman": "New York University Grossman School of Medicine",
    "New York Medical": "New York Medical College",
    "Renaissance Stony Brook": "Stony Brook University School of Medicine",
    "Rochester": "University of Rochester School of Medicine and Dentistry",
    "SUNY Downstate": "SUNY – Downstate Medical Center College of Medicine",
    "SUNY Upstate-Norton": "SUNY – Upstate Medical University",
    "Zucker Hofstra Northwell": "Hofstra Northwell School of Medicine",
    
    # Ohio
    "Case Western Reserve": "Case Western Reserve University School of Medicine",
    "Cincinnati": "University of Cincinnati College of Medicine",
    "Northeast Ohio": "Northeast Ohio Medical University",
    "Ohio State": "The Ohio State University College of Medicine",
    "Toledo": "The University of Toledo College of Medicine and Life Sciences",
    "Wright State-Boonshoft": "Wright State University Boonshoft School of Medicine",
    
    # Oklahoma
    "Oklahoma": "University of Oklahoma College of Medicine",
    
    # Oregon
    "Oregon": "Oregon Health & Science University School of Medicine",
    
    # Pennsylvania
    "Drexel": "Drexel University College of Medicine",
    "Geisinger Commonwealth": "Geisinger Commonwealth School of Medicine",
    "Jefferson-Kimmel": "Sidney Kimmel Medical College at Thomas Jefferson University",
    "Penn State": "Pennsylvania State University College of Medicine",
    "Pennsylvania-Perelman": "Perelman School of Medicine University of Pennsylvania",
    "Pittsburgh": "University of Pittsburgh School of Medicine",
    "Temple-Katz": "Temple University Lewis Katz School of Medicine",
    
    # Puerto Rico
    "Caribe": "Universidad Central Del Caribe School of Medicine",
    "Ponce": "Ponce School of Medicine and Health Sciences",
    "Puerto Rico": "University of Puerto Rico School of Medicine",
    "San Juan Bautista": "San Juan Bautista School of Medicine",
    
    # Rhode Island
    "Brown-Alpert": "Brown University The Warren Alpert Medical School",
    
    # South Carolina
    "MU South Carolina": "Medical University of South Carolina College of Medicine",
    "South Carolina Columbia": "University of South Carolina School of Medicine – Columbia",
    "South Carolina Greenville": "University of South Carolina School of Medicine – Greenville",
    
    # South Dakota
    "South Dakota-Sanford": "University of South Dakota Sanford School of Medicine",
    
    # Tennessee
    "East Tennessee-Quillen": "East Tennessee State University Quillen College of Medicine",
    "Meharry": "Meharry Medical College School of Medicine",
    "Tennessee": "University of Tennessee Health Science Center College of Medicine",
    "Vanderbilt": "Vanderbilt University School of Medicine",
    
    # Texas
    "Baylor": "Baylor College of Medicine",
    "Houston-Fertitta": "University of Houston Tilman J. Fertitta Family College of Medicine",
    "TCU-Burnett": "TCU and UNTHSC School of Medicine",
    "Texas A&M-Vashisht": "Texas A&M Health Science Center College of Medicine",
    "Texas Tech": "Texas Tech University Health Sciences Center School of Medicine – Lubbock",
    "Texas Tech-Foster": "Texas Tech University Health Sciences Center Paul L. Foster School of Medicine",
    "UT Austin-Dell": "University of Texas at Austin Dell Medical School",
    "UT Medical Branch-Sealy": "University of Texas Medical Branch School of Medicine",
    "UT Rio Grande Valley": "University of Texas Rio Grande Valley School of Medicine",
    "UT San Antonio-Long": "University of Texas School of Medicine at San Antonio",
    "UT Southwestern": "University of Texas Southwestern Medical School",
    "UTHealth Houston-McGovern": "University of Texas McGovern Medical School at Houston",
    
    # Utah
    "Utah-Eccles": "University of Utah School of Medicine",
    
    # Virginia
    "Eastern Virginia ODU": "Eastern Virginia Medical School",
    "Virginia": "University of Virginia School of Medicine",
    "Virginia Commonwealth": "Virginia Commonwealth University School of Medicine",
    "Virginia Tech Carilion": "Virginia Tech Carilion School of Medicine and Research Institute",
    
    # Vermont
    "Vermont-Larner": "The University of Vermont Larner College of Medicine",
    
    # Washington
    "U Washington": "University of Washington School of Medicine",
    "Washington State-Floyd": "Washington State University Elson S. Floyd College of Medicine",
    
    # Wisconsin
    "MC Wisconsin": "Medical College of Wisconsin",
    "Wisconsin": "University of Wisconsin School of Medicine and Public Health",
    
    # West Virginia
    "Marshall-Edwards": "Marshall University Joan C. Edwards School of Medicine",
    "West Virginia": "West Virginia University School of Medicine",
}


def main():
    # Load FACTS data
    facts_path = '/Users/itaysolomon/Downloads/2025_FACTS_Table_A-1.xlsx'
    facts_df = pd.read_excel(facts_path, header=None)
    
    # Extract FACTS school data
    facts_data = {}
    current_state = None
    for idx, row in facts_df.iterrows():
        if idx < 9:
            continue
        if pd.notna(row[0]):
            current_state = row[0]
        school = row[1]
        if pd.isna(school):
            continue
        
        in_state = row[8]
        out_state = row[9]
        
        facts_data[school] = {
            'in_state': in_state,
            'out_state': out_state
        }
    
    print(f"Loaded {len(facts_data)} schools from FACTS data")
    
    # Load CSV
    csv_path = '/Users/itaysolomon/coding_projects/school-list-generator/public/medical_schools_data.csv'
    df = pd.read_csv(csv_path)
    
    print(f"Loaded {len(df)} schools from CSV")
    
    # Update matriculation data
    updated = 0
    not_found = []
    
    for facts_name, csv_name in SCHOOL_MAPPING.items():
        if facts_name not in facts_data:
            print(f"Warning: FACTS school not found: {facts_name}")
            continue
            
        # Find in CSV
        mask = df['Medical School Name'] == csv_name
        if mask.sum() == 0:
            not_found.append(csv_name)
            continue
        
        # Update values
        df.loc[mask, 'In-State Matriculants %'] = facts_data[facts_name]['in_state']
        df.loc[mask, 'Out-of-State Matriculants %'] = facts_data[facts_name]['out_state']
        updated += 1
    
    print(f"Updated {updated} schools")
    
    if not_found:
        print(f"\nSchools not found in CSV ({len(not_found)}):")
        for s in not_found:
            print(f"  {s}")
    
    # Remove In-State Advantage column
    if 'In-State Advantage' in df.columns:
        df = df.drop(columns=['In-State Advantage'])
        print("\nRemoved 'In-State Advantage' column")
    
    # Remove duplicate Application System columns
    cols_to_drop = [c for c in df.columns if c.startswith('Application System.')]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
        print(f"Removed duplicate columns: {cols_to_drop}")
    
    # Remove Match Score column (not used)
    if 'Match Score' in df.columns:
        df = df.drop(columns=['Match Score'])
        print("Removed 'Match Score' column")
    
    # Save updated CSV
    df.to_csv(csv_path, index=False)
    print(f"\nSaved updated CSV to {csv_path}")
    
    # Print sample of updated data
    print("\nSample updated data:")
    md_schools = df[df['Degree Type'] == 'MD'].head(10)
    for _, row in md_schools.iterrows():
        in_pct = row['In-State Matriculants %']
        out_pct = row['Out-of-State Matriculants %']
        print(f"  {row['Medical School Name'][:50]:50} | In: {in_pct}% | Out: {out_pct}%")


if __name__ == '__main__':
    main()
