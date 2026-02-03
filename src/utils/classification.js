/**
 * Classification utilities for medical school list generator
 * Based on Shemmassian methodology
 */

/**
 * Determine residency status based on school and applicant state
 */
export const getResidencyStatus = (schoolState, applicantState) => {
  if (!applicantState) return null;
  return schoolState === applicantState ? 'In-State' : 'Out-of-State';
};

/**
 * Classify GPA relative to school average
 * @param {string|number} userGPA - Applicant's GPA
 * @param {string|number} schoolAvgGPA - School's average GPA
 * @returns {'Undershoot'|'Target'|'Reach'|null}
 */
export const classifyGPA = (userGPA, schoolAvgGPA) => {
  if (!userGPA || !schoolAvgGPA) return null;
  const diff = parseFloat(userGPA) - parseFloat(schoolAvgGPA);
  // Continuous thresholds with no gaps
  if (diff >= 0.1) return 'Undershoot';
  if (diff <= -0.1) return 'Reach';
  return 'Target'; // diff between -0.1 and 0.1
};

/**
 * Classify MCAT relative to school average
 * @param {string|number} userMCAT - Applicant's MCAT score
 * @param {string|number} schoolAvgMCAT - School's average MCAT
 * @returns {'Undershoot'|'Target'|'Reach'|null}
 */
export const classifyMCAT = (userMCAT, schoolAvgMCAT) => {
  if (!userMCAT || !schoolAvgMCAT) return null;
  const diff = parseInt(userMCAT) - parseInt(schoolAvgMCAT);
  // Continuous thresholds with no gaps
  if (diff >= 2) return 'Undershoot';
  if (diff <= -2) return 'Reach';
  return 'Target'; // diff between -2 and 2
};

/**
 * Get overall classification based on GPA and MCAT classifications
 * Uses Shemmassian methodology rule matrix
 * @param {string} gpaClass - GPA classification
 * @param {string} mcatClass - MCAT classification
 * @returns {'Reach'|'Target'|'Undershoot'|null}
 */
export const getOverallClassification = (gpaClass, mcatClass) => {
  if (!gpaClass || !mcatClass) return null;

  // Rule matrix from Shemmassian methodology
  const matrix = {
    'Reach-Reach': 'Reach',
    'Target-Target': 'Target',
    'Undershoot-Undershoot': 'Undershoot',
    'Reach-Undershoot': 'Target',
    'Undershoot-Reach': 'Target',
    'Target-Reach': 'Reach',
    'Target-Undershoot': 'Undershoot',
    'Reach-Target': 'Reach',
    'Undershoot-Target': 'Undershoot'
  };

  return matrix[`${gpaClass}-${mcatClass}`] || null;
};

/**
 * Get classification for a school given applicant data
 * @param {Object} school - School data object
 * @param {Object} applicantData - Applicant data with gpa and mcat
 * @returns {Object} Classification details
 */
export const getSchoolClassification = (school, applicantData) => {
  const gpaClass = classifyGPA(applicantData.gpa, school['Average GPA']);
  const mcatClass = classifyMCAT(applicantData.mcat, school['Average MCAT']);
  const overallClassification = getOverallClassification(gpaClass, mcatClass);
  const residencyStatus = getResidencyStatus(school.State, applicantData.state);

  return {
    gpaClass,
    mcatClass,
    overallClassification,
    residencyStatus
  };
};
