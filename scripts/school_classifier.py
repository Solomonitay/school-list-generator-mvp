#!/usr/bin/env python3
"""
Medical School Classification System
Categorizes schools as Reach, Target, or Undershoot based on applicant stats.

Based on Shemmassian Consulting guidance:
https://www.shemmassianconsulting.com/blog/how-many-medical-schools-should-i-apply-to
"""

import csv
import json
from typing import Dict, List, Tuple, Optional


class SchoolClassifier:
    """
    Classifies medical schools as Reach, Target, or Undershoot
    based on applicant's GPA and MCAT scores.
    """

    # Classification thresholds
    GPA_UNDERSHOOT_DIFF = 0.2   # User GPA is 0.2+ higher than school avg
    GPA_TARGET_RANGE = 0.1      # User GPA within ±0.1 of school avg
    GPA_REACH_DIFF = 0.2        # User GPA is 0.2+ lower than school avg

    MCAT_UNDERSHOOT_DIFF = 3    # User MCAT is 3+ higher than school avg
    MCAT_TARGET_RANGE = 2       # User MCAT within ±2 of school avg
    MCAT_REACH_DIFF = 3         # User MCAT is 3+ lower than school avg

    def __init__(self):
        """Initialize the classifier."""
        pass

    def classify_by_gpa(self, user_gpa: float, school_avg_gpa: float) -> str:
        """
        Classify school based on GPA comparison.

        Args:
            user_gpa: Applicant's GPA
            school_avg_gpa: School's average accepted GPA

        Returns:
            'Undershoot', 'Target', or 'Reach'
        """
        diff = user_gpa - school_avg_gpa

        if diff >= self.GPA_UNDERSHOOT_DIFF:
            return 'Undershoot'
        elif abs(diff) <= self.GPA_TARGET_RANGE:
            return 'Target'
        elif diff <= -self.GPA_REACH_DIFF:
            return 'Reach'
        else:
            # Edge cases between target and reach/undershoot
            if diff > 0:
                return 'Target'  # Slightly above but not quite undershoot
            else:
                return 'Target'  # Slightly below but not quite reach

    def classify_by_mcat(self, user_mcat: int, school_avg_mcat: int) -> str:
        """
        Classify school based on MCAT comparison.

        Args:
            user_mcat: Applicant's MCAT score
            school_avg_mcat: School's average accepted MCAT

        Returns:
            'Undershoot', 'Target', or 'Reach'
        """
        diff = user_mcat - school_avg_mcat

        if diff >= self.MCAT_UNDERSHOOT_DIFF:
            return 'Undershoot'
        elif abs(diff) <= self.MCAT_TARGET_RANGE:
            return 'Target'
        elif diff <= -self.MCAT_REACH_DIFF:
            return 'Reach'
        else:
            # Edge cases between target and reach/undershoot
            if diff > 0:
                return 'Target'  # Slightly above but not quite undershoot
            else:
                return 'Target'  # Slightly below but not quite reach

    def classify_overall(
        self,
        gpa_classification: str,
        mcat_classification: str
    ) -> str:
        """
        Determine overall school classification based on GPA and MCAT classifications.

        Rules:
        - Both Reach = Reach
        - Both Undershoot = Undershoot
        - Both Target = Target
        - Mixed (one Reach, one Undershoot) = Target
        - One Target + one Reach = Reach (conservative)
        - One Target + one Undershoot = Undershoot

        Args:
            gpa_classification: GPA-based classification
            mcat_classification: MCAT-based classification

        Returns:
            Overall classification
        """
        # Both same category
        if gpa_classification == mcat_classification:
            return gpa_classification

        # Mixed: one reach, one undershoot
        if (gpa_classification == 'Reach' and mcat_classification == 'Undershoot') or \
           (gpa_classification == 'Undershoot' and mcat_classification == 'Reach'):
            return 'Target'

        # One target, one something else - take the more conservative
        if gpa_classification == 'Target':
            return mcat_classification
        if mcat_classification == 'Target':
            return gpa_classification

        # Should not reach here, but default to target
        return 'Target'

    def check_minimum_threshold(
        self,
        user_mcat: int,
        min_mcat_notes: str
    ) -> bool:
        """
        Check if user's MCAT meets the school's minimum threshold.

        Args:
            user_mcat: Applicant's MCAT score
            min_mcat_notes: School's minimum MCAT notes

        Returns:
            True if meets threshold, False if below minimum
        """
        if not min_mcat_notes or min_mcat_notes == 'NR':
            return True  # No minimum specified

        # Try to extract numeric minimum from notes
        import re
        numbers = re.findall(r'\d+', min_mcat_notes)

        if numbers:
            min_mcat = int(numbers[0])
            if user_mcat < min_mcat:
                return False

        return True

    def classify_school(
        self,
        user_gpa: float,
        user_mcat: int,
        school: Dict,
        user_state: Optional[str] = None
    ) -> Dict:
        """
        Classify a single school for an applicant.

        Args:
            user_gpa: Applicant's GPA
            user_mcat: Applicant's MCAT score
            school: School data dictionary
            user_state: Applicant's state (for in-state considerations)

        Returns:
            Dictionary with classification details
        """
        # Parse school stats
        try:
            school_gpa = float(school['Average GPA'].replace('+', '').split('–')[0].split('-')[0])
        except (ValueError, AttributeError):
            school_gpa = None

        try:
            school_mcat_str = school['Average MCAT'].replace('+', '').split('–')[0].split('-')[0]
            school_mcat = int(float(school_mcat_str))
        except (ValueError, AttributeError):
            school_mcat = None

        # Cannot classify without data
        if school_gpa is None or school_mcat is None:
            return {
                'classification': 'Unknown',
                'gpa_classification': 'Unknown',
                'mcat_classification': 'Unknown',
                'reason': 'Insufficient school data',
                'in_state_advantage': False
            }

        # Check minimum threshold
        meets_minimum = self.check_minimum_threshold(user_mcat, school.get('Minimum MCAT Notes', ''))

        # Classify by GPA and MCAT
        gpa_class = self.classify_by_gpa(user_gpa, school_gpa)
        mcat_class = self.classify_by_mcat(user_mcat, school_mcat)

        # Overall classification
        overall_class = self.classify_overall(gpa_class, mcat_class)

        # If below minimum, override to Reach
        if not meets_minimum:
            overall_class = 'Reach'
            reason = 'Below minimum MCAT threshold'
        else:
            reason = f'GPA: {gpa_class}, MCAT: {mcat_class}'

        # Check in-state advantage
        in_state_advantage = False
        if user_state and school.get('State') == user_state and school.get('Public School Status') == 'Public':
            in_state_advantage = True

        return {
            'school_name': school['Medical School Name'],
            'classification': overall_class,
            'gpa_classification': gpa_class,
            'mcat_classification': mcat_class,
            'reason': reason,
            'in_state_advantage': in_state_advantage,
            'school_avg_gpa': school_gpa,
            'school_avg_mcat': school_mcat,
            'user_gpa': user_gpa,
            'user_mcat': user_mcat,
            'gpa_diff': round(user_gpa - school_gpa, 2),
            'mcat_diff': user_mcat - school_mcat
        }

    def classify_all_schools(
        self,
        user_gpa: float,
        user_mcat: int,
        csv_path: str,
        user_state: Optional[str] = None,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Classify all schools in the database for an applicant.

        Args:
            user_gpa: Applicant's GPA
            user_mcat: Applicant's MCAT score
            csv_path: Path to medical schools CSV
            user_state: Applicant's state (optional)
            filters: Additional filters (degree type, etc.)

        Returns:
            Dictionary with categorized schools
        """
        schools = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for school in reader:
                # Apply filters if provided
                if filters:
                    if filters.get('degree_type') and school['Degree Type'] != filters['degree_type']:
                        continue
                    if filters.get('state') and school['State'] != filters['state']:
                        continue
                    if filters.get('app_system') and school['Application System'] != filters['app_system']:
                        continue

                classification = self.classify_school(user_gpa, user_mcat, school, user_state)
                schools.append(classification)

        # Categorize results
        reach_schools = [s for s in schools if s['classification'] == 'Reach']
        target_schools = [s for s in schools if s['classification'] == 'Target']
        undershoot_schools = [s for s in schools if s['classification'] == 'Undershoot']
        unknown_schools = [s for s in schools if s['classification'] == 'Unknown']

        # Sort each category by competitiveness
        reach_schools.sort(key=lambda x: (x['school_avg_gpa'], x['school_avg_mcat']), reverse=True)
        target_schools.sort(key=lambda x: (x['school_avg_gpa'], x['school_avg_mcat']), reverse=True)
        undershoot_schools.sort(key=lambda x: (x['school_avg_gpa'], x['school_avg_mcat']), reverse=True)

        return {
            'user_stats': {
                'gpa': user_gpa,
                'mcat': user_mcat,
                'state': user_state
            },
            'summary': {
                'total_schools': len(schools),
                'reach_count': len(reach_schools),
                'target_count': len(target_schools),
                'undershoot_count': len(undershoot_schools),
                'unknown_count': len(unknown_schools)
            },
            'schools': {
                'reach': reach_schools,
                'target': target_schools,
                'undershoot': undershoot_schools,
                'unknown': unknown_schools
            }
        }


def generate_application_list(
    user_gpa: float,
    user_mcat: int,
    csv_path: str,
    user_state: Optional[str] = None,
    filters: Optional[Dict] = None
) -> Dict:
    """
    Generate a recommended application list for a pre-med student.

    Based on Shemmassian guidance:
    - 3-5 reach schools
    - 7-10 target schools
    - 5-7 undershoot schools

    Args:
        user_gpa: Applicant's GPA
        user_mcat: Applicant's MCAT score
        csv_path: Path to medical schools CSV
        user_state: Applicant's state (optional)
        filters: Additional filters

    Returns:
        Dictionary with recommended application list
    """
    classifier = SchoolClassifier()
    results = classifier.classify_all_schools(user_gpa, user_mcat, csv_path, user_state, filters)

    # Recommended numbers per Shemmassian
    recommended_reach = (3, 5)
    recommended_target = (7, 10)
    recommended_undershoot = (5, 7)

    return {
        'user_stats': results['user_stats'],
        'summary': results['summary'],
        'schools': results['schools'],
        'recommendations': {
            'reach': f"{recommended_reach[0]}-{recommended_reach[1]} schools",
            'target': f"{recommended_target[0]}-{recommended_target[1]} schools",
            'undershoot': f"{recommended_undershoot[0]}-{recommended_undershoot[1]} schools",
            'total_recommended': f"{sum([recommended_reach[0], recommended_target[0], recommended_undershoot[0]])}-"
                                f"{sum([recommended_reach[1], recommended_target[1], recommended_undershoot[1]])} schools"
        }
    }


def main():
    """Example usage of the school classifier."""
    import sys
    import os

    # Example applicant stats
    user_gpa = 3.75
    user_mcat = 512
    user_state = 'CA'

    # Allow command line arguments
    if len(sys.argv) >= 3:
        user_gpa = float(sys.argv[1])
        user_mcat = int(sys.argv[2])
        if len(sys.argv) >= 4:
            user_state = sys.argv[3]

    # Try different path locations
    possible_paths = [
        '../public/medical_schools_data.csv',   # From scripts folder
        'public/medical_schools_data.csv',      # From project root
        '../public/medical_schools_data_enhanced.csv',  # Enhanced version from scripts
        'public/medical_schools_data_enhanced.csv',     # Enhanced version from root
        'medical_schools_data.csv'              # Current directory
    ]

    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            break

    if not csv_path:
        print("Error: Could not find medical_schools_data.csv")
        print("Please run from project root or scripts directory")
        sys.exit(1)

    print("=" * 70)
    print("MEDICAL SCHOOL CLASSIFICATION SYSTEM")
    print("=" * 70)
    print(f"\nApplicant Stats:")
    print(f"  GPA: {user_gpa}")
    print(f"  MCAT: {user_mcat}")
    print(f"  State: {user_state or 'Not specified'}")

    # Classify all schools
    results = generate_application_list(user_gpa, user_mcat, csv_path, user_state)

    # Print summary
    print(f"\n" + "=" * 70)
    print("CLASSIFICATION SUMMARY")
    print("=" * 70)
    print(f"Total Schools Analyzed: {results['summary']['total_schools']}")
    print(f"  Reach Schools:        {results['summary']['reach_count']}")
    print(f"  Target Schools:       {results['summary']['target_count']}")
    print(f"  Undershoot Schools:   {results['summary']['undershoot_count']}")

    # Recommendations
    print(f"\n" + "=" * 70)
    print("RECOMMENDED APPLICATION STRATEGY")
    print("=" * 70)
    print(f"Based on Shemmassian Consulting guidance:")
    print(f"  Apply to {results['recommendations']['reach']} reach schools")
    print(f"  Apply to {results['recommendations']['target']} target schools")
    print(f"  Apply to {results['recommendations']['undershoot']} undershoot (safety) schools")
    print(f"  Total: {results['recommendations']['total_recommended']} schools")

    # Sample schools from each category
    print(f"\n" + "=" * 70)
    print("SAMPLE REACH SCHOOLS (Top 5)")
    print("=" * 70)
    for i, school in enumerate(results['schools']['reach'][:5], 1):
        print(f"{i}. {school['school_name']}")
        print(f"   School Avg: GPA {school['school_avg_gpa']}, MCAT {school['school_avg_mcat']}")
        print(f"   Your Diff: GPA {school['gpa_diff']:+.2f}, MCAT {school['mcat_diff']:+d}")

    print(f"\n" + "=" * 70)
    print("SAMPLE TARGET SCHOOLS (Top 5)")
    print("=" * 70)
    for i, school in enumerate(results['schools']['target'][:5], 1):
        print(f"{i}. {school['school_name']}")
        print(f"   School Avg: GPA {school['school_avg_gpa']}, MCAT {school['school_avg_mcat']}")
        print(f"   Your Diff: GPA {school['gpa_diff']:+.2f}, MCAT {school['mcat_diff']:+d}")
        if school['in_state_advantage']:
            print(f"   ✓ In-state public school advantage!")

    print(f"\n" + "=" * 70)
    print("SAMPLE UNDERSHOOT SCHOOLS (Top 5)")
    print("=" * 70)
    for i, school in enumerate(results['schools']['undershoot'][:5], 1):
        print(f"{i}. {school['school_name']}")
        print(f"   School Avg: GPA {school['school_avg_gpa']}, MCAT {school['school_avg_mcat']}")
        print(f"   Your Diff: GPA {school['gpa_diff']:+.2f}, MCAT {school['mcat_diff']:+d}")
        if school['in_state_advantage']:
            print(f"   ✓ In-state public school advantage!")

    print(f"\n" + "=" * 70)

    # Option to export to JSON
    # Determine output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.dirname(script_dir), 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    export_path = os.path.join(output_dir, f'school_classifications_GPA{user_gpa}_MCAT{user_mcat}.json')
    with open(export_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nFull results exported to: {export_path}")


if __name__ == "__main__":
    main()
