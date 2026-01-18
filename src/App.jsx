import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import ApplicantInfo from './components/ApplicantInfo';
import SchoolSelector from './components/SchoolSelector';
import PreliminaryList from './components/PreliminaryList';
import ResourcesPanel from './components/ResourcesPanel';
import './App.css';

// Classification functions
const getResidencyStatus = (schoolState, applicantState) => {
  if (!applicantState) return null;
  return schoolState === applicantState ? 'In-State' : 'Out-of-State';
};

const classifyGPA = (userGPA, schoolAvgGPA) => {
  if (!userGPA || !schoolAvgGPA) return null;
  const diff = parseFloat(userGPA) - parseFloat(schoolAvgGPA);
  if (diff >= 0.2) return 'Undershoot';
  if (Math.abs(diff) <= 0.1) return 'Target';
  if (diff <= -0.2) return 'Reach';
  return null;
};

const classifyMCAT = (userMCAT, schoolAvgMCAT) => {
  if (!userMCAT || !schoolAvgMCAT) return null;
  const diff = parseInt(userMCAT) - parseInt(schoolAvgMCAT);
  if (diff >= 3) return 'Undershoot';
  if (Math.abs(diff) <= 2) return 'Target';
  if (diff <= -3) return 'Reach';
  return null;
};

const getOverallClassification = (gpaClass, mcatClass) => {
  if (!gpaClass || !mcatClass) return null;

  // Rule matrix from Shemmassian methodology
  if (gpaClass === 'Reach' && mcatClass === 'Reach') return 'Reach';
  if (gpaClass === 'Target' && mcatClass === 'Target') return 'Target';
  if (gpaClass === 'Undershoot' && mcatClass === 'Undershoot') return 'Undershoot';
  if (gpaClass === 'Reach' && mcatClass === 'Undershoot') return 'Target';
  if (gpaClass === 'Undershoot' && mcatClass === 'Reach') return 'Target';
  if (gpaClass === 'Target' && mcatClass === 'Reach') return 'Reach';
  if (gpaClass === 'Target' && mcatClass === 'Undershoot') return 'Undershoot';
  if (gpaClass === 'Reach' && mcatClass === 'Target') return 'Reach';
  if (gpaClass === 'Undershoot' && mcatClass === 'Target') return 'Undershoot';

  return null;
};

function App() {
  const [schools, setSchools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [preliminaryList, setPreliminaryList] = useState([]);
  const [selectedSchoolData, setSelectedSchoolData] = useState(null);
  const [applicantData, setApplicantData] = useState({
    mcat: '',
    gpa: '',
    sgpa: '',
    state: ''
  });

  useEffect(() => {
    // Load CSV data
    Papa.parse('/medical_schools_data.csv', {
      download: true,
      header: true,
      complete: (results) => {
        console.log(`Loaded ${results.data.length} schools from CSV`);
        console.log('Sample school:', results.data[0]);
        setSchools(results.data);
        setLoading(false);
      },
      error: (error) => {
        console.error('Error loading CSV:', error);
        setLoading(false);
      }
    });
  }, []);

  const addToPreliminaryList = (school) => {
    if (!preliminaryList.find(s => s['Medical School Name'] === school['Medical School Name'])) {
      // Calculate classifications for the school
      const gpaClass = classifyGPA(applicantData.gpa, school['Average GPA']);
      const mcatClass = classifyMCAT(applicantData.mcat, school['Average MCAT']);
      const overallClassification = getOverallClassification(gpaClass, mcatClass);

      // Add classification data to the school object
      const schoolWithClassification = {
        ...school,
        gpaClass,
        mcatClass,
        overallClassification
      };

      setPreliminaryList([...preliminaryList, schoolWithClassification]);
    }
  };

  const removeFromPreliminaryList = (schoolName) => {
    setPreliminaryList(preliminaryList.filter(s => s['Medical School Name'] !== schoolName));
  };

  const clearList = () => {
    setPreliminaryList([]);
  };

  const exportToCSV = () => {
    // Group schools by classification (Reach, Target, Safety)
    const groupedSchools = {
      reach: [],
      target: [],
      safety: []
    };

    preliminaryList.forEach(school => {
      // Determine classification based on GPA and MCAT (using existing logic)
      const gpaClass = school.gpaClass || 'Unknown';
      const mcatClass = school.mcatClass || 'Unknown';
      const overallClassification = school.overallClassification || 'Unknown';

      if (overallClassification === 'Reach') {
        groupedSchools.reach.push(school);
      } else if (overallClassification === 'Target') {
        groupedSchools.target.push(school);
      } else {
        // Default to safety for undershoot or unknown
        groupedSchools.safety.push(school);
      }
    });

    // Create structured CSV data similar to the Excel template
    const csvData = [];

    // Add Reach Schools section
    if (groupedSchools.reach.length > 0) {
      // Section header
      csvData.push({
        'Reach Schools': 'Reach Schools',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      });

      // Header row
      csvData.push({
        'Reach Schools': '(by order of preference)',
        'School Name': 'School Name',
        'Average MCAT': 'Average MCAT',
        'Average GPA': 'Average GPA',
        'Casper required?': 'Casper required?',
        'AAMC PREview required?': 'AAMC PREview required?',
        'Additional Requirements (Duet, Snapshot, etc).': 'Additional Requirements (Duet, Snapshot, etc).',
        'Notes': 'Notes'
      });

      // Add reach schools with ranking
      groupedSchools.reach.forEach((school, index) => {
        csvData.push({
          'Reach Schools': (index + 1).toString(),
          'School Name': school['Medical School Name'] || '',
          'Average MCAT': school['Average MCAT'] || '',
          'Average GPA': school['Average GPA'] || '',
          'Casper required?': school['Requires Casper'] === 'True' ? 'Yes' : 'No',
          'AAMC PREview required?': school['Requires PREview'] !== 'Not Required' ? school['Requires PREview'] : 'No',
          'Additional Requirements (Duet, Snapshot, etc).': '', // Could be populated based on school data
          'Notes': school.notes || ''
        });
      });

      // Add empty rows to match template (up to 12 slots)
      for (let i = groupedSchools.reach.length; i < 12; i++) {
        csvData.push({
          'Reach Schools': (i + 1).toString(),
          'School Name': '',
          'Average MCAT': '',
          'Average GPA': '',
          'Casper required?': '',
          'AAMC PREview required?': '',
          'Additional Requirements (Duet, Snapshot, etc).': '',
          'Notes': ''
        });
      }
    }

    // Add Target Schools section
    if (groupedSchools.target.length > 0) {
      // Section header
      csvData.push({
        'Reach Schools': 'Target Schools',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      });

      // Header row
      csvData.push({
        'Reach Schools': '(by order of preference)',
        'School Name': 'School Name',
        'Average MCAT': 'Average MCAT',
        'Average GPA': 'Average GPA',
        'Casper required?': 'Casper required?',
        'AAMC PREview required?': 'AAMC PREview required?',
        'Additional Requirements (Duet, Snapshot, etc).': 'Additional Requirements (Duet, Snapshot, etc).',
        'Notes': 'Notes'
      });

      // Add target schools with ranking
      groupedSchools.target.forEach((school, index) => {
        csvData.push({
          'Reach Schools': (index + 1).toString(),
          'School Name': school['Medical School Name'] || '',
          'Average MCAT': school['Average MCAT'] || '',
          'Average GPA': school['Average GPA'] || '',
          'Casper required?': school['Requires Casper'] === 'True' ? 'Yes' : 'No',
          'AAMC PREview required?': school['Requires PREview'] !== 'Not Required' ? school['Requires PREview'] : 'No',
          'Additional Requirements (Duet, Snapshot, etc).': '',
          'Notes': school.notes || ''
        });
      });

      // Add empty rows to match template (up to 12 slots)
      for (let i = groupedSchools.target.length; i < 12; i++) {
        csvData.push({
          'Reach Schools': (i + 1).toString(),
          'School Name': '',
          'Average MCAT': '',
          'Average GPA': '',
          'Casper required?': '',
          'AAMC PREview required?': '',
          'Additional Requirements (Duet, Snapshot, etc).': '',
          'Notes': ''
        });
      }
    }

    // Add Safety Schools section
    if (groupedSchools.safety.length > 0) {
      // Section header
      csvData.push({
        'Reach Schools': 'Safety Schools',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      });

      // Header row
      csvData.push({
        'Reach Schools': '(by order of preference)',
        'School Name': 'School Name',
        'Average MCAT': 'Average MCAT',
        'Average GPA': 'Average GPA',
        'Casper required?': 'Casper required?',
        'AAMC PREview required?': 'AAMC PREview required?',
        'Additional Requirements (Duet, Snapshot, etc).': 'Additional Requirements (Duet, Snapshot, etc).',
        'Notes': 'Notes'
      });

      // Add safety schools with ranking
      groupedSchools.safety.forEach((school, index) => {
        csvData.push({
          'Reach Schools': (index + 1).toString(),
          'School Name': school['Medical School Name'] || '',
          'Average MCAT': school['Average MCAT'] || '',
          'Average GPA': school['Average GPA'] || '',
          'Casper required?': school['Requires Casper'] === 'True' ? 'Yes' : 'No',
          'AAMC PREview required?': school['Requires PREview'] !== 'Not Required' ? school['Requires PREview'] : 'No',
          'Additional Requirements (Duet, Snapshot, etc).': '',
          'Notes': school.notes || ''
        });
      });

      // Add empty rows to match template (up to 13 slots)
      for (let i = groupedSchools.safety.length; i < 13; i++) {
        csvData.push({
          'Reach Schools': (i + 1).toString(),
          'School Name': '',
          'Average MCAT': '',
          'Average GPA': '',
          'Casper required?': '',
          'AAMC PREview required?': '',
          'Additional Requirements (Duet, Snapshot, etc).': '',
          'Notes': ''
        });
      }
    }

    // Add summary section (empty rows followed by totals)
    csvData.push(
      {
        'Reach Schools': '',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      },
      {
        'Reach Schools': '',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      },
      {
        'Reach Schools': '',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      },
      {
        'Reach Schools': '',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      },
      {
        'Reach Schools': 'TOTAL:',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      },
      {
        'Reach Schools': 'SUBMITTED:',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      },
      {
        'Reach Schools': 'INTERVIEWS:',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      },
      {
        'Reach Schools': 'WAITLIST:',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      },
      {
        'Reach Schools': 'REJECTED:',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      },
      {
        'Reach Schools': 'ACCEPTED:',
        'School Name': '',
        'Average MCAT': '',
        'Average GPA': '',
        'Casper required?': '',
        'AAMC PREview required?': '',
        'Additional Requirements (Duet, Snapshot, etc).': '',
        'Notes': ''
      }
    );

    const csv = Papa.unparse(csvData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', 'school_list_export.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSchoolSelection = (schoolData) => {
    setSelectedSchoolData(schoolData);
  };

  if (loading) {
    return <div className="loading">Loading medical school data...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">School List Generator</h1>
          <div className="header-actions">
            <button
              className="btn btn-secondary"
              onClick={clearList}
              disabled={preliminaryList.length === 0}
            >
              Clear List
            </button>
            <button
              className="btn btn-primary"
              onClick={exportToCSV}
              disabled={preliminaryList.length === 0}
            >
              Export List
            </button>
          </div>
        </div>
      </header>

      <div className="main-content-container">
        <div className="dashboard-content">
        <aside className="dashboard-sidebar">
          <div className="sidebar-section">
            <h2 className="section-title">Admissions Profile</h2>
            <ApplicantInfo
              applicantData={applicantData}
              onApplicantDataChange={setApplicantData}
            />
          </div>

          <div className="sidebar-section">
            <h2 className="section-title">Add Schools</h2>
            <SchoolSelector
              schools={schools}
              onAddToList={addToPreliminaryList}
              onSchoolSelect={handleSchoolSelection}
              applicantData={applicantData}
            />
          </div>

          <div className="sidebar-section">
            <h2 className="section-title">School Profile</h2>
            <div className="school-preview">
              {selectedSchoolData ? (
                <>
                  <h4 className="school-name">{selectedSchoolData['Medical School Name']}</h4>
                  <div className="preview-details">
                    <div className="detail-row">
                      <span className="detail-label">State of Residency:</span>
                      <span className="detail-value">{selectedSchoolData.State}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Degree:</span>
                      <span className="detail-value">{selectedSchoolData['Degree Type']}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Application:</span>
                      <span className="detail-value">{selectedSchoolData['Application System']}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Avg GPA:</span>
                      <span className="detail-value tabular-nums">{selectedSchoolData['Average GPA']}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Avg MCAT:</span>
                      <span className="detail-value tabular-nums">{selectedSchoolData['Average MCAT']}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Institution:</span>
                      <span className="detail-value">{selectedSchoolData['Public School Status']}</span>
                    </div>

                    {/* Classification - Always calculated */}
                    <div className="detail-row">
                      <span className="detail-label">Your Classification:</span>
                      <div className="classification-display">
                        {(() => {
                          const gpaClass = classifyGPA(applicantData.gpa, selectedSchoolData['Average GPA']);
                          const mcatClass = classifyMCAT(applicantData.mcat, selectedSchoolData['Average MCAT']);
                          const overallClassification = getOverallClassification(gpaClass, mcatClass);

                          if (overallClassification) {
                            return (
                              <span className={`badge classification-badge ${overallClassification.toLowerCase()}`}>
                                {overallClassification}
                              </span>
                            );
                          } else if (applicantData.gpa && applicantData.mcat) {
                            return <span className="badge classification-badge na">Unable to classify</span>;
                          } else {
                            return <span className="classification-placeholder">Enter GPA & MCAT above</span>;
                          }
                        })()}
                      </div>
                    </div>

                    <div className="detail-row">
                      <span className="detail-label">International Students:</span>
                      <span className="detail-value">
                        {selectedSchoolData['Accepts International Students'] ? 'Accepted' : 'Not Accepted'}
                      </span>
                    </div>

                    {/* Matriculation Information - Always shown */}
                    <div className="detail-row">
                      <span className="detail-label">In-State %:</span>
                      <span className="detail-value">
                        {selectedSchoolData['In-State Matriculants %']
                          ? `${selectedSchoolData['In-State Matriculants %']}%`
                          : 'N/A'
                        }
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Out-of-State %:</span>
                      <span className="detail-value">
                        {selectedSchoolData['Out-of-State Matriculants %']
                          ? `${selectedSchoolData['Out-of-State Matriculants %']}%`
                          : 'N/A'
                        }
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">In-State Advantage:</span>
                      <span className="detail-value">
                        {selectedSchoolData['In-State Advantage'] && selectedSchoolData['In-State Advantage'] !== 'unknown'
                          ? selectedSchoolData['In-State Advantage']
                          : 'N/A'
                        }
                      </span>
                    </div>

                  </div>

                  {/* Action Buttons */}
                  <div className="action-buttons">
                    <button
                      className="btn btn-success"
                      onClick={() => {
                        if (selectedSchoolData['Website URL']) {
                          window.open(selectedSchoolData['Website URL'], '_blank', 'noopener,noreferrer');
                        }
                      }}
                      disabled={!selectedSchoolData || !selectedSchoolData['Website URL']}
                    >
                      Visit Website
                    </button>

                    <button
                      className="btn btn-primary"
                      onClick={() => {
                        if (selectedSchoolData) {
                          addToPreliminaryList(selectedSchoolData);
                          setSelectedSchoolData(null);
                        }
                      }}
                      disabled={!selectedSchoolData}
                    >
                      Add to List
                    </button>
                  </div>
                </>
              ) : (
                <div className="school-preview-empty">
                  <p className="empty-text">Search and select a school above to view its profile</p>
                </div>
              )}
            </div>
          </div>
        </aside>

        <main className="dashboard-main">
          <div className="main-content">
            <h2 className="section-title">School List</h2>
            <PreliminaryList
              schools={preliminaryList}
              onRemove={removeFromPreliminaryList}
              applicantData={applicantData}
            />
          </div>

          <div className="resources-container">
            <ResourcesPanel />
          </div>
        </main>
        </div>
      </div>
    </div>
  );
}

export default App;