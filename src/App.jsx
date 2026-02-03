import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import ApplicantInfo from './components/ApplicantInfo';
import SchoolSelector from './components/SchoolSelector';
import PreliminaryList from './components/PreliminaryList';
import ResourcesPanel from './components/ResourcesPanel';
import {
  classifyGPA,
  classifyMCAT,
  getOverallClassification,
  getSchoolClassification
} from './utils/classification';
import './App.css';

// LocalStorage keys
const STORAGE_KEYS = {
  SCHOOL_LIST: 'medSchoolList_schools',
  APPLICANT_DATA: 'medSchoolList_applicant'
};

function App() {
  const [schools, setSchools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSchoolData, setSelectedSchoolData] = useState(null);

  // Load initial state from localStorage
  const [preliminaryList, setPreliminaryList] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.SCHOOL_LIST);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [applicantData, setApplicantData] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.APPLICANT_DATA);
      return saved ? JSON.parse(saved) : { mcat: '', gpa: '', sgpa: '', state: '' };
    } catch {
      return { mcat: '', gpa: '', sgpa: '', state: '' };
    }
  });

  // Save to localStorage when data changes
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.SCHOOL_LIST, JSON.stringify(preliminaryList));
  }, [preliminaryList]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.APPLICANT_DATA, JSON.stringify(applicantData));
  }, [applicantData]);

  // Load CSV data
  useEffect(() => {
    Papa.parse(`${import.meta.env.BASE_URL}medical_schools_data.csv`, {
      download: true,
      header: true,
      complete: (results) => {
        console.log(`Loaded ${results.data.length} schools from CSV`);
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
      const { gpaClass, mcatClass, overallClassification } = getSchoolClassification(school, applicantData);

      // Add classification data and notes field to the school object
      const schoolWithClassification = {
        ...school,
        gpaClass,
        mcatClass,
        overallClassification,
        notes: '',
        addedAt: Date.now() // For ordering
      };

      setPreliminaryList([...preliminaryList, schoolWithClassification]);
    }
  };

  const removeFromPreliminaryList = (schoolName) => {
    setPreliminaryList(preliminaryList.filter(s => s['Medical School Name'] !== schoolName));
  };

  const updateSchoolNotes = (schoolName, notes) => {
    setPreliminaryList(preliminaryList.map(s =>
      s['Medical School Name'] === schoolName ? { ...s, notes } : s
    ));
  };

  const reorderSchools = (newOrder) => {
    setPreliminaryList(newOrder);
  };

  const clearList = () => {
    setPreliminaryList([]);
  };

  const exportToCSV = () => {
    // Group schools by classification (Reach, Target, Safety/Undershoot)
    const groupedSchools = {
      reach: [],
      target: [],
      safety: []
    };

    preliminaryList.forEach(school => {
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

    // Helper function to format school row
    const formatSchoolRow = (school) => ({
      'School Name': school['Medical School Name'] || '',
      'Average MCAT': school['Average MCAT'] || '',
      'Average GPA': school['Average GPA'] || '',
      'Casper required?': school['Requires Casper'] === 'True' ? 'Yes' : 'No',
      'AAMC PREview required?': school['Requires PREview'] && school['Requires PREview'] !== 'Not Required' ? 'Yes' : 'No',
      'Additional Requirements': '',
      'Notes': school.notes || ''
    });

    // Helper function to create empty row
    const emptyRow = () => ({
      'School Name': '',
      'Average MCAT': '',
      'Average GPA': '',
      'Casper required?': '',
      'AAMC PREview required?': '',
      'Additional Requirements': '',
      'Notes': ''
    });

    // Helper function to create section header
    const sectionHeader = (title) => ({
      'School Name': title,
      'Average MCAT': '',
      'Average GPA': '',
      'Casper required?': '',
      'AAMC PREview required?': '',
      'Additional Requirements': '',
      'Notes': ''
    });

    // Helper function to create column header row
    const columnHeaders = () => ({
      'School Name': 'School Name',
      'Average MCAT': 'Average MCAT',
      'Average GPA': 'Average GPA',
      'Casper required?': 'Casper required?',
      'AAMC PREview required?': 'AAMC PREview required?',
      'Additional Requirements': 'Additional Requirements',
      'Notes': 'Notes'
    });

    const csvData = [];

    // Reach Schools section
    csvData.push(sectionHeader('Reach Schools'));
    csvData.push(columnHeaders());
    groupedSchools.reach.forEach(school => {
      csvData.push(formatSchoolRow(school));
    });
    // Add empty rows to fill to 12 slots
    for (let i = groupedSchools.reach.length; i < 12; i++) {
      csvData.push(emptyRow());
    }

    // Target Schools section
    csvData.push(sectionHeader('Target Schools'));
    csvData.push(columnHeaders());
    groupedSchools.target.forEach(school => {
      csvData.push(formatSchoolRow(school));
    });
    // Add empty rows to fill to 12 slots
    for (let i = groupedSchools.target.length; i < 12; i++) {
      csvData.push(emptyRow());
    }

    // Safety Schools section
    csvData.push(sectionHeader('Safety Schools'));
    csvData.push(columnHeaders());
    groupedSchools.safety.forEach(school => {
      csvData.push(formatSchoolRow(school));
    });
    // Add empty rows to fill to 13 slots
    for (let i = groupedSchools.safety.length; i < 13; i++) {
      csvData.push(emptyRow());
    }

    // Summary section
    csvData.push(emptyRow());
    csvData.push(emptyRow());
    csvData.push({ ...emptyRow(), 'School Name': `TOTAL: ${preliminaryList.length}` });
    csvData.push({ ...emptyRow(), 'School Name': 'SUBMITTED:' });
    csvData.push({ ...emptyRow(), 'School Name': 'INTERVIEWS:' });
    csvData.push({ ...emptyRow(), 'School Name': 'WAITLIST:' });
    csvData.push({ ...emptyRow(), 'School Name': 'REJECTED:' });
    csvData.push({ ...emptyRow(), 'School Name': 'ACCEPTED:' });

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
                      <span className="detail-label">State:</span>
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
                    {(() => {
                      const gpaClass = classifyGPA(applicantData.gpa, selectedSchoolData['Average GPA']);
                      const mcatClass = classifyMCAT(applicantData.mcat, selectedSchoolData['Average MCAT']);
                      const overallClassification = getOverallClassification(gpaClass, mcatClass);

                      if (overallClassification) {
                        return (
                          <div className="detail-row">
                            <span className="detail-label">Classification:</span>
                            <span className={`badge classification-badge ${overallClassification.toLowerCase()}`}>
                              {overallClassification}
                            </span>
                          </div>
                        );
                      } else if (applicantData.gpa && applicantData.mcat) {
                        return (
                          <div className="detail-row">
                            <span className="detail-label">Classification:</span>
                            <span className="badge classification-badge na">Unable to classify</span>
                          </div>
                        );
                      } else {
                        return (
                          <div className="detail-row full-width classification-prompt">
                            <span className="classification-placeholder">Enter GPA & MCAT above to see classification</span>
                          </div>
                        );
                      }
                    })()}

                    {/* Matriculation Information */}
                    <div className="detail-row">
                      <span className="detail-label">In-State %:</span>
                      <span className="detail-value tabular-nums">
                        {selectedSchoolData['In-State Matriculants %']
                          ? `${selectedSchoolData['In-State Matriculants %']}%`
                          : 'N/A'
                        }
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Out-of-State %:</span>
                      <span className="detail-value tabular-nums">
                        {selectedSchoolData['Out-of-State Matriculants %']
                          ? `${selectedSchoolData['Out-of-State Matriculants %']}%`
                          : 'N/A'
                        }
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">In-State Advantage:</span>
                      {(() => {
                        const inState = parseFloat(selectedSchoolData['In-State Matriculants %']);
                        if (isNaN(inState)) return <span className="detail-value">N/A</span>;
                        
                        let advantage, className;
                        if (inState >= 80) {
                          advantage = 'Huge';
                          className = 'huge';
                        } else if (inState >= 60) {
                          advantage = 'Material';
                          className = 'material';
                        } else if (inState >= 40) {
                          advantage = 'Modest';
                          className = 'modest';
                        } else {
                          advantage = 'None';
                          className = 'none';
                        }
                        return (
                          <span className={`badge advantage-badge ${className}`}>
                            {advantage}
                          </span>
                        );
                      })()}
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
              onUpdateNotes={updateSchoolNotes}
              onReorder={reorderSchools}
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