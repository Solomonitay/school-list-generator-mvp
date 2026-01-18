#!/usr/bin/env python3
"""
Script to add website URLs to medical_schools_data.csv
URLs sourced from Shemmassian Consulting
"""

import csv
import re

# MD School URLs
md_school_urls = {
    "University of Alabama School of Medicine": "https://www.uab.edu/medicine/home/",
    "University of South Alabama College of Medicine": "https://www.southalabama.edu/colleges/com/",
    "University of Arkansas for Medical Sciences College of Medicine": "https://medicine.uams.edu/",
    "University of Arizona College of Medicine - Tucson": "https://medicine.arizona.edu/",
    "University of Arizona School of Medicine - Phoenix": "https://phoenixmed.arizona.edu/",
    "Mayo Clinic Alix School of Medicine": "https://college.mayo.edu/academics/mayo-clinic-alix-school-of-medicine/",
    "California Northstate University College of Medicine": "https://medicine.cnsu.edu/",
    "California University of Science and Medicine": "https://www.cusm.org/",
    "Loma Linda University School of Medicine": "https://medicine.llu.edu/",
    "University of California – Davis School of Medicine": "https://health.ucdavis.edu/welcome/",
    "Stanford University School of Medicine": "https://www.med.stanford.edu/",
    "University of California – Irvine School of Medicine": "https://www.meded.uci.edu/",
    "University of California – Los Angeles David Geffen School of Medicine": "https://medschool.ucla.edu/",
    "University of California – Riverside School of Medicine": "https://medschool.ucr.edu/",
    "University of California – San Diego School of Medicine": "https://medschool.ucsd.edu/",
    "University of California – San Francisco School of Medicine": "https://meded.ucsf.edu/",
    "University of Southern California Keck School of Medicine": "https://keck.usc.edu/",
    "Kaiser Permanente School of Medicine": "https://medschool.kp.org/",
    "University of Colorado School of Medicine": "https://medschool.cuanschutz.edu/",
    "Quinnipiac University Frank H. Netter MD School of Medicine": "https://www.qu.edu/schools/medicine/",
    "University of Connecticut School of Medicine": "https://medicine.uconn.edu/",
    "Yale School of Medicine": "https://medicine.yale.edu/",
    "George Washington University School of Medicine and Health Sciences": "https://smhs.gwu.edu/",
    "Georgetown University School of Medicine": "https://som.georgetown.edu/",
    "Howard University College of Medicine": "https://medicine.howard.edu/",
    "Florida Atlantic University Charles E. Schmidt College of Medicine": "https://www.fau.edu/medicine/",
    "Florida International University Herbert Wertheim College of Medicine": "https://medicine.fiu.edu/",
    "Florida State University College of Medicine": "https://med.fsu.edu/",
    "University of Central Florida College of Medicine": "https://med.ucf.edu/",
    "University of Florida College of Medicine": "https://med.ufl.edu/",
    "University of Miami Miller School of Medicine": "https://med.miami.edu/",
    "University of South Florida Health Morsani College of Medicine": "https://health.usf.edu/medicine",
    "Nova Southeastern University Dr. Kiran C. Patel College of Allopathic Medicine": "https://md.nova.edu/",
    "Emory University School of Medicine": "https://www.med.emory.edu/",
    "Medical College of Georgia at Augusta University": "https://www.augusta.edu/mcg/",
    "Mercer University School of Medicine": "https://medicine.mercer.edu/",
    "Morehouse School of Medicine": "https://www.msm.edu/",
    "University of Hawaii John A. Burns School of Medicine": "https://jabsom.hawaii.edu/",
    "University of Iowa Carver College of Medicine": "https://medicine.uiowa.edu/",
    "Carle Illinois College of Medicine": "https://medicine.illinois.edu/",
    "Chicago Medical School at Rosalind Franklin University of Medicine and Science": "https://www.rosalindfranklin.edu/",
    "Loyola University of Chicago Stritch School of Medicine": "https://www.luc.edu/stritch/",
    "Northwestern University The Feinberg School of Medicine": "https://www.feinberg.northwestern.edu/",
    "Rush Medical College of Rush University": "https://www.rushu.rush.edu/rush-medical-college",
    "Southern Illinois University School of Medicine": "https://www.siumed.edu/",
    "University of Chicago Pritzker School of Medicine": "https://pritzker.uchicago.edu/",
    "University of Illinois College of Medicine": "https://medicine.uic.edu/",
    "Indiana University School of Medicine": "https://medicine.iu.edu/",
    "University of Kansas School of Medicine": "https://www.kumc.edu/school-of-medicine.html",
    "University of Kentucky College of Medicine": "https://medicine.uky.edu/",
    "University of Louisville School of Medicine": "https://louisville.edu/medicine",
    "Louisiana State University – New Orleans School of Medicine": "https://www.medschool.lsuhsc.edu/",
    "Louisiana State University – Shreveport School of Medicine": "https://www.lsuhs.edu/our-schools/school-of-medicine",
    "Tulane University School of Medicine": "https://medicine.tulane.edu/",
    "Boston University School of Medicine": "https://www.bumc.bu.edu/camed/",
    "Harvard Medical School": "https://hms.harvard.edu/",
    "Tufts University School of Medicine": "https://medicine.tufts.edu/",
    "University of Massachusetts Medical School": "https://www.umassmed.edu/",
    "Johns Hopkins University School of Medicine": "https://www.hopkinsmedicine.org/som/",
    "Uniformed Services University of the Health Sciences F. Edward Hebert School of Medicine": "https://medschool.usuhs.edu/",
    "University of Maryland School of Medicine": "https://www.medschool.umaryland.edu/",
    "Central Michigan University College of Medicine": "https://www.cmich.edu/academics/colleges/college-of-medicine",
    "Michigan State University College of Human Medicine": "https://humanmedicine.msu.edu/",
    "Oakland University William Beaumont School of Medicine": "https://oakland.edu/medicine/",
    "University of Michigan Medical School": "https://medicine.umich.edu/medschool/home/",
    "Wayne State University School of Medicine": "https://www.med.wayne.edu/",
    "Western Michigan University School of Medicine": "https://med.wmich.edu/",
    "University of Minnesota Medical School - Twin Cities": "https://med.umn.edu/",
    "University of Minnesota Medical School - Duluth": "https://med.umn.edu/about/duluth-campus",
    "University of Missouri – Columbia School of Medicine": "https://medicine.missouri.edu/",
    "Saint Louis University School of Medicine": "https://www.slu.edu/medicine/index.php",
    "University of Missouri – Kansas City School of Medicine": "https://med.umkc.edu/",
    "Washington University School of Medicine": "https://medicine.wustl.edu/",
    "University of Mississippi School of Medicine": "https://www.umc.edu/som/SOM_Home.html",
    "Duke University School of Medicine": "https://medschool.duke.edu/",
    "East Carolina University Brody School of Medicine": "https://medicine.ecu.edu/",
    "University of North Carolina at Chapel Hill School of Medicine": "https://www.med.unc.edu/",
    "Wake Forest School of Medicine": "https://school.wakehealth.edu/",
    "University of North Dakota School of Medicine and Health Sciences": "https://med.und.edu/",
    "Creighton University School of Medicine": "https://www.creighton.edu/medicine",
    "University of Nebraska Medical Center College of Medicine": "https://www.unmc.edu/com/",
    "Geisel School of Medicine at Dartmouth": "https://geiselmed.dartmouth.edu/",
    "Cooper Medical School of Rowan University": "https://cmsru.rowan.edu/",
    "Rutgers New Jersey Medical School": "https://njms.rutgers.edu/",
    "Rutgers Robert Wood Johnson Medical School": "https://rwjms.rutgers.edu/",
    "Hackensack Meridian School of Medicine": "https://www.hmsom.org/",
    "University of New Mexico School of Medicine": "https://som.unm.edu/",
    "University of Nevada Reno School of Medicine": "https://med.unr.edu/",
    "University of Nevada Las Vegas School of Medicine": "https://www.unlv.edu/medicine",
    "Albany Medical College": "https://www.amc.edu/academic/",
    "Albert Einstein College of Medicine": "https://www.einsteinmed.edu/",
    "Columbia University College of Physicians and Surgeons": "https://www.vagelos.columbia.edu/",
    "Hofstra Northwell School of Medicine": "https://medicine.hofstra.edu/",
    "Icahn School of Medicine at Mount Sinai": "https://icahn.mssm.edu/",
    "New York Medical College": "https://www.nymc.edu/",
    "New York University Grossman School of Medicine": "https://med.nyu.edu/",
    "New York University Long Island School of Medicine": "https://medli.nyu.edu/",
    "SUNY – Downstate Medical Center College of Medicine": "https://www.downstate.edu/education-training/college-of-medicine/index.html",
    "University at Buffalo Jacobs School of Medicine and Biomedical Sciences": "https://medicine.buffalo.edu/",
    "SUNY – Upstate Medical University": "https://www.upstate.edu/",
    "Stony Brook University School of Medicine": "https://renaissance.stonybrookmedicine.edu/",
    "University of Rochester School of Medicine and Dentistry": "https://www.urmc.rochester.edu/smd.aspx",
    "Weill Cornell Medical College": "https://weill.cornell.edu/",
    "Case Western Reserve University School of Medicine": "https://case.edu/medicine/",
    "Northeast Ohio Medical University": "https://www.neomed.edu/",
    "The Ohio State University College of Medicine": "https://medicine.osu.edu/",
    "The University of Toledo College of Medicine and Life Sciences": "https://www.utoledo.edu/med",
    "University of Cincinnati College of Medicine": "https://med.uc.edu/",
    "Wright State University Boonshoft School of Medicine": "https://medicine.wright.edu/",
    "University of Oklahoma College of Medicine": "https://medicine.ouhsc.edu/",
    "Oregon Health & Science University School of Medicine": "https://www.ohsu.edu/school-of-medicine",
    "Drexel University College of Medicine": "https://drexel.edu/medicine/",
    "Geisinger Commonwealth School of Medicine": "https://www.geisinger.edu/education",
    "Pennsylvania State University College of Medicine": "https://med.psu.edu/",
    "Perelman School of Medicine University of Pennsylvania": "https://www.med.upenn.edu/",
    "Sidney Kimmel Medical College at Thomas Jefferson University": "https://www.jefferson.edu/academics/colleges-schools-institutes/skmc.html",
    "Temple University Lewis Katz School of Medicine": "https://medicine.temple.edu/",
    "University of Pittsburgh School of Medicine": "https://www.medschool.pitt.edu/",
    "Ponce School of Medicine and Health Sciences": "https://www.psm.edu/",
    "San Juan Bautista School of Medicine": "https://www.sanjuanbautista.edu/",
    "Universidad Central Del Caribe School of Medicine": "https://www.uccaribe.edu/som/",
    "University of Puerto Rico School of Medicine": "https://md.rcm.upr.edu/",
    "Brown University The Warren Alpert Medical School": "https://medical.brown.edu/",
    "Medical University of South Carolina College of Medicine": "https://medicine.musc.edu/",
    "University of South Carolina School of Medicine – Columbia": "https://sc.edu/study/colleges_schools/medicine/index.php",
    "University of South Carolina School of Medicine – Greenville": "https://sc.edu/study/colleges_schools/medicine_greenville/index.php",
    "University of South Dakota Sanford School of Medicine": "https://www.usd.edu/Academics/Colleges-and-Schools/sanford-school-of-medicine",
    "East Tennessee State University Quillen College of Medicine": "https://www.etsu.edu/com/",
    "Meharry Medical College School of Medicine": "https://home.mmc.edu/",
    "University of Tennessee Health Science Center College of Medicine": "https://uthsc.edu/medicine/",
    "Vanderbilt University School of Medicine": "https://medschool.vanderbilt.edu/",
    "Baylor College of Medicine": "https://www.bcm.edu/",
    "TCU and UNTHSC School of Medicine": "https://mdschool.tcu.edu/",
    "Texas A&M Health Science Center College of Medicine": "https://medicine.tamu.edu/",
    "Texas Tech University Health Sciences Center Paul L. Foster School of Medicine": "https://elpaso.ttuhsc.edu/som/",
    "Texas Tech University Health Sciences Center School of Medicine – Lubbock": "https://www.ttuhsc.edu/medicine/default.aspx",
    "University of Houston Tilman J. Fertitta Family College of Medicine": "https://www.uh.edu/medicine/",
    "University of Texas at Austin Dell Medical School": "https://dellmed.utexas.edu/",
    "University of Texas Medical Branch School of Medicine": "https://som.utmb.edu/",
    "University of Texas McGovern Medical School at Houston": "https://med.uth.edu/",
    "University of Texas Rio Grande Valley School of Medicine": "https://www.utrgv.edu/school-of-medicine/",
    "University of Texas School of Medicine at San Antonio": "https://uthscsa.edu/medicine/",
    "University of Texas Southwestern Medical School": "https://utswmed.org/",
    "University of Utah School of Medicine": "https://medicine.utah.edu/",
    "Eastern Virginia Medical School": "https://www.evms.edu/",
    "Virginia Commonwealth University School of Medicine": "https://medschool.vcu.edu/",
    "Virginia Tech Carilion School of Medicine and Research Institute": "https://medicine.vtc.vt.edu/",
    "University of Virginia School of Medicine": "https://med.virginia.edu/",
    "The University of Vermont Larner College of Medicine": "https://www.med.uvm.edu/",
    "University of Washington School of Medicine": "https://www.uwmedicine.org/school-of-medicine",
    "Washington State University Elson S. Floyd College of Medicine": "https://medicine.wsu.edu/",
    "Marshall University Joan C. Edwards School of Medicine": "https://jcesom.marshall.edu/",
    "West Virginia University School of Medicine": "https://medicine.wvu.edu/",
    "Medical College of Wisconsin": "https://www.mcw.edu/",
    "University of Wisconsin School of Medicine and Public Health": "https://www.med.wisc.edu/",
    # Drew/UCLA
    "Drew/UCLA Joint Medical Program Drew University of Medicine and ScienceNote: This joint Program has been discontinued. Drew now has its own MD program.": "https://www.cdrewu.edu/",
}

# DO School URLs
do_school_urls = {
    "Alabama College of Osteopathic Medicine": "https://www.acom.edu/",
    "Edward Via College of Osteopathic Medicine – Auburn Campus": "https://www.vcom.edu/locations/auburn",
    "Arkansas College of Osteopathic Medicine": "https://arcom.achehealth.edu/",
    "A.T. Still University School of Osteopathic Medicine Arizona (SOMA)": "https://www.atsu.edu/",
    "Arizona College of Osteopathic Medicine of Midwestern University": "https://www.midwestern.edu/academics/our-colleges/arizona-college-of-osteopathic-medicine",
    "Touro University California College of Osteopathic Medicine": "https://tu.edu/",
    "Western University of Health Sciences College of Osteopathic Medicine of the Pacific": "https://www.westernu.edu/osteopathic/",
    "California Health Sciences University College of Osteopathic Medicine": "https://osteopathic.chsu.edu/",
    "Rocky Vista University College of Osteopathic Medicine": "https://www.rvu.edu/",
    "Des Moines University College of Osteopathic Medicine": "https://www.dmu.edu/com/",
    "Idaho College of Osteopathic Medicine": "https://www.idahocom.org/",
    "Chicago College of Osteopathic Medicine of Midwestern University": "https://www.midwestern.edu/",
    "Marian University College of Osteopathic Medicine": "https://www.marian.edu/osteopathic-medical-school/index.php",
    "Kansas College of Osteopathic Medicine": "https://kansascom.kansashsc.org/",
    "University of Pikeville Kentucky College of Osteopathic Medicine": "https://www.upike.edu/osteopathic-medicine/",
    "Edward Via College of Osteopathic Medicine – Louisiana Campus": "https://www.vcom.edu/locations/louisiana",
    "University of New England College of Osteopathic Medicine": "https://www.une.edu/com",
    "Michigan State University College of Osteopathic Medicine": "https://com.msu.edu/",
    "A.T. Still University of Health Sciences Kirksville College of Osteopathic Medicine": "https://www.atsu.edu/kirksville-college-of-osteopathic-medicine",
    "Kansas City University of Medicine and Biosciences College of Osteopathic Medicine": "https://www.kansascity.edu/programs/college-of-osteopathic-medicine",
    "William Carey University College of Osteopathic Medicine": "https://www.wmcarey.edu/College/Osteopathic-Medicine",
    "Campbell University Jerry M. Wallace School of Osteopathic Medicine": "https://medicine.campbell.edu/",
    "Rowan University School of Osteopathic Medicine": "https://som.rowan.edu/",
    "Lake Erie College of Osteopathic Medicine": "https://lecom.edu/",
    "Lake Erie College of Osteopathic Medicine Bradenton Campus": "https://lecom.edu/communities/bradenton/",
    "Nova Southeastern University Dr. Kiran C. Patel College of Osteopathic Medicine": "https://osteopathic.nova.edu/",
    "Georgia Campus Philadelphia College of Osteopathic Medicine": "https://www.pcom.edu/campuses/georgia-campus/",
    "Philadelphia College of Osteopathic Medicine": "https://www.pcom.edu/",
    "Edward Via College of Osteopathic Medicine – Carolinas Campus": "https://www.vcom.edu/locations/carolinas",
    "Ohio University Heritage College of Osteopathic Medicine": "https://www.ohio.edu/medicine/",
    "Oklahoma State University Center for Health Sciences College of Osteopathic Medicine": "https://medicine.okstate.edu/com/",
    "Sam Houston State University College of Osteopathic Medicine": "https://www.shsu.edu/academics/osteopathic-medicine/",
    "University of the Incarnate Word School of Osteopathic Medicine": "https://osteopathic-medicine.uiw.edu/",
    "University of North Texas Health Science Center at Fort Worth Texas College of Osteopathic Medicine": "https://www.unthsc.edu/",
    "Noorda College of Osteopathic Medicine": "https://www.noordacom.org/",
    "Edward Via College of Osteopathic Medicine – Virginia Campus": "https://www.vcom.edu/locations/virginia",
    "Liberty University College of Osteopathic Medicine": "https://www.liberty.edu/lucom/",
    "Pacific Northwestern University of Health Sciences College of Osteopathic Medicine": "https://www.pnwu.edu/",
    "West Virginia School of Osteopathic Medicine": "https://www.wvsom.edu/",
    "Western University of Health Sciences College of Osteopathic Medicine of the Pacific Northwest": "https://www.westernu.edu/osteopathic/",
    "Touro University – Nevada College of Osteopathic Medicine": "https://tun.touro.edu/",
    "New York Institute of Technology College of Osteopathic Medicine": "https://www.nyit.edu/medicine",
    "Touro College of Osteopathic Medicine - Middletown Campus": "https://tourocom.touro.edu/about-us/facilities/middletown-campus/",
    "Touro College of Osteopathic Medicine - Harlem Campus": "https://tourocom.touro.edu/about-us/facilities/harlem-campus/",
    "Burrell College of Osteopathic Medicine at New Mexico State University": "https://bfrcom.org/",
    "Lincoln Memorial University DeBusk College of Osteopathic Medicine": "https://www.lmunet.edu/debusk-college-of-osteopathic-medicine/",
}

# Combine all URLs
all_urls = {**md_school_urls, **do_school_urls}

def normalize_name(name):
    """Normalize school name for matching"""
    # Remove extra whitespace
    name = ' '.join(name.split())
    return name.strip()

def find_url(school_name, urls_dict):
    """Find URL for a school, trying various matching strategies"""
    normalized = normalize_name(school_name)

    # Direct match
    if normalized in urls_dict:
        return urls_dict[normalized]

    # Try matching by key
    for key, url in urls_dict.items():
        if normalize_name(key) == normalized:
            return url

    # Try partial matching (school name contains key or vice versa)
    for key, url in urls_dict.items():
        key_normalized = normalize_name(key)
        if key_normalized in normalized or normalized in key_normalized:
            return url

    # Try matching without common suffixes
    name_parts = normalized.lower()
    for key, url in urls_dict.items():
        key_lower = normalize_name(key).lower()
        # Check if core names match
        if (name_parts.replace('school of medicine', '').strip() ==
            key_lower.replace('school of medicine', '').strip()):
            return url

    return None

def main():
    input_file = 'public/medical_schools_data.csv'
    output_file = 'public/medical_schools_data.csv'

    # Read existing data
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Add Website URL column if not present
    if 'Website URL' not in fieldnames:
        fieldnames = list(fieldnames) + ['Website URL']

    # Update each row with website URL
    matched = 0
    unmatched = []

    for row in rows:
        school_name = row.get('Medical School Name', '')
        if not school_name:
            continue

        url = find_url(school_name, all_urls)
        if url:
            row['Website URL'] = url
            matched += 1
        else:
            row['Website URL'] = ''
            unmatched.append(school_name)

    # Write updated data
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {output_file}")
    print(f"Matched: {matched} schools")
    print(f"Unmatched: {len(unmatched)} schools")

    if unmatched:
        print("\nUnmatched schools:")
        for name in unmatched:
            print(f"  - {name}")

if __name__ == '__main__':
    main()
