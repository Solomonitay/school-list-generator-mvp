import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import ApplicantInfo from './components/ApplicantInfo';
import SchoolSelector from './components/SchoolSelector';
import PreliminaryList from './components/PreliminaryList';
import ResourcesPanel from './components/ResourcesPanel';
import './App.css';

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
      setPreliminaryList([...preliminaryList, school]);
    }
  };

  const removeFromPreliminaryList = (schoolName) => {
    setPreliminaryList(preliminaryList.filter(s => s['Medical School Name'] !== schoolName));
  };

  const clearList = () => {
    setPreliminaryList([]);
  };

  const exportToCSV = () => {
    const headers = [
      'Medical School Name', 'Degree Type', 'State', 'Application System',
      'Average GPA', 'Average MCAT', 'Minimum MCAT Notes', 'Public School Status',
      'Website URL', 'Notes'
    ];
    const data = preliminaryList.map(school => ({
      'Medical School Name': school['Medical School Name'],
      'Degree Type': school['Degree Type'],
      'State': school.State,
      'Application System': school['Application System'],
      'Average GPA': school['Average GPA'],
      'Average MCAT': school['Average MCAT'],
      'Minimum MCAT Notes': school['Minimum MCAT Notes'],
      'Public School Status': school['Public School Status'],
      'Website URL': school['Website URL'],
      'Notes': school.notes || ''
    }));

    const csv = Papa.unparse(data, { header: true });
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', 'school_list.csv');
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

          <ResourcesPanel />
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
        </main>
        </div>
      </div>
    </div>
  );
}

export default App;