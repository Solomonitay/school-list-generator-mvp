import React, { useState } from 'react';
import './ApplicantInfo.css';

function ApplicantInfo({ applicantData, onApplicantDataChange }) {
  const [stateSearchQuery, setStateSearchQuery] = useState('');
  const [showStateDropdown, setShowStateDropdown] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    onApplicantDataChange({
      ...applicantData,
      [name]: value
    });
  };

  const usStates = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
    'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
    'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
    'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
    'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
    'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
    'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
  ];

  const filteredStates = usStates.filter(state =>
    state.toLowerCase().includes(stateSearchQuery.toLowerCase())
  );

  const handleStateSearchChange = (e) => {
    setStateSearchQuery(e.target.value);
    setShowStateDropdown(true);
  };

  const handleStateSelect = (state) => {
    onApplicantDataChange({
      ...applicantData,
      state: state
    });
    setStateSearchQuery('');
    setShowStateDropdown(false);
  };

  const handleStateSearchFocus = () => {
    setShowStateDropdown(true);
  };

  const handleStateSearchBlur = () => {
    // Delay to allow click on dropdown item
    setTimeout(() => {
      setShowStateDropdown(false);
      setStateSearchQuery('');
    }, 200);
  };

  return (
    <div className="applicant-info">
      <div className="profile-grid">
        <div className="profile-field">
          <label htmlFor="mcat">MCAT Score</label>
          <input
            type="number"
            id="mcat"
            name="mcat"
            value={applicantData.mcat}
            onChange={handleInputChange}
            min="472"
            max="528"
            placeholder="e.g., 510"
          />
        </div>
        <div className="profile-field">
          <label htmlFor="gpa">Overall GPA</label>
          <input
            type="number"
            id="gpa"
            name="gpa"
            value={applicantData.gpa}
            onChange={handleInputChange}
            min="0.00"
            max="4.00"
            step="0.01"
            placeholder="e.g., 3.75"
          />
        </div>
        <div className="profile-field">
          <label htmlFor="sgpa">Science GPA</label>
          <input
            type="number"
            id="sgpa"
            name="sgpa"
            value={applicantData.sgpa}
            onChange={handleInputChange}
            min="0.00"
            max="4.00"
            step="0.01"
            placeholder="e.g., 3.60"
          />
        </div>
        <div className="profile-field">
          <label htmlFor="state">State of Residency</label>
          <div className="state-dropdown-container">
            <input
              type="text"
              id="state"
              placeholder={applicantData.state || "Search state..."}
              value={stateSearchQuery}
              onChange={handleStateSearchChange}
              onFocus={handleStateSearchFocus}
              onBlur={handleStateSearchBlur}
              className="state-search-input"
            />
            {showStateDropdown && (
              <div className="state-dropdown-menu">
                {filteredStates.length === 0 ? (
                  <div className="state-dropdown-item no-results">
                    No states found
                  </div>
                ) : (
                  filteredStates.map((state) => (
                    <div
                      key={state}
                      className="state-dropdown-item"
                      onClick={() => handleStateSelect(state)}
                    >
                      {state}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ApplicantInfo;