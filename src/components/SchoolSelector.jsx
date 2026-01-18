import React, { useState, useMemo } from 'react';
import './SchoolSelector.css';

function SchoolSelector({ schools, onAddToList, onSchoolSelect, applicantData }) {
  const [selectedProgramType, setSelectedProgramType] = useState('MD');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSchool, setSelectedSchool] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);

  // Filter schools by degree type and search
  const filteredSchools = useMemo(() => {
    return schools.filter(school => {
      const matchesType = school['Degree Type'] === selectedProgramType;
      const matchesSearch = searchQuery === '' ||
        school['Medical School Name'].toLowerCase().includes(searchQuery.toLowerCase()) ||
        school.State.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesType && matchesSearch;
    });
  }, [schools, selectedProgramType, searchQuery]);

  const handleProgramTypeChange = (programType) => {
    setSelectedProgramType(programType);
    setSelectedSchool(null);
    setSearchQuery('');
    setShowDropdown(false);
  };

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    // Always show dropdown when typing
    setShowDropdown(true);
  };

  const handleSearchFocus = () => {
    // Always show dropdown on focus
    setShowDropdown(true);
  };

  const handleSearchBlur = () => {
    // Delay hiding dropdown to allow for clicks
    setTimeout(() => setShowDropdown(false), 200);
  };

  const handleSchoolSelect = (school) => {
    setSelectedSchool(school);
    setShowDropdown(false);
    if (onSchoolSelect) {
      onSchoolSelect(school);
    }
  };

  return (
    <div className="school-selector">
      {/* Segmented Controls for MD/DO */}
      <div className="segmented-controls">
        <button
          className={`segment-btn ${selectedProgramType === 'MD' ? 'active' : ''}`}
          onClick={() => handleProgramTypeChange('MD')}
        >
          MD
        </button>
        <button
          className={`segment-btn ${selectedProgramType === 'DO' ? 'active' : ''}`}
          onClick={() => handleProgramTypeChange('DO')}
        >
          DO
        </button>
      </div>

      {/* Search Input with Dropdown */}
      <div className="dropdown-container">
        <input
          type="text"
          placeholder="Search schools..."
          value={searchQuery}
          onChange={handleSearchChange}
          onFocus={handleSearchFocus}
          onBlur={handleSearchBlur}
          className="search-input"
        />

        {showDropdown && (
          <div className="dropdown-menu">
            {filteredSchools.length === 0 ? (
              <div className="dropdown-item no-results">
                No schools found
              </div>
            ) : (
              filteredSchools.map((school) => (
                <div
                  key={school['Medical School Name']}
                  className="dropdown-item"
                  onClick={() => handleSchoolSelect(school)}
                >
                  <div className="school-name">{school['Medical School Name']}</div>
                  <div className="school-state">{school.State}</div>
                  {/* Show acceptance rates if available */}
                  {(school['In-State Acceptance Rate %'] || school['Out-of-State Acceptance Rate %']) && (
                    <div className="school-rates">
                      {school['In-State Acceptance Rate %'] && (
                        <span className="rate-badge in-state">
                          In: {school['In-State Acceptance Rate %']}%
                        </span>
                      )}
                      {school['Out-of-State Acceptance Rate %'] && (
                        <span className="rate-badge out-state">
                          Out: {school['Out-of-State Acceptance Rate %']}%
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default SchoolSelector;