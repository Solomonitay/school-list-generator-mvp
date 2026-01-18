import React, { useState, useMemo } from 'react';
import './SchoolSelector.css';

function SchoolSelector({ schools, onAddToList, onSchoolSelect, applicantData }) {
  const [selectedProgramType, setSelectedProgramType] = useState('MD');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSchool, setSelectedSchool] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);

  // Filter schools by degree type and search
  const filteredSchools = useMemo(() => {
    // Ensure schools is an array and handle edge cases
    if (!schools || !Array.isArray(schools)) {
      console.warn('Schools data is not an array:', schools);
      return [];
    }

    try {
      const filtered = schools.filter(school => {
        // Ensure school object exists and has required properties
        if (!school || typeof school !== 'object') {
          return false;
        }

        const matchesType = school['Degree Type'] === selectedProgramType;

        // Handle search query safely
        const matchesSearch = searchQuery === '' ||
          (school['Medical School Name'] && school['Medical School Name'].toLowerCase().includes(searchQuery.toLowerCase())) ||
          (school.State && school.State.toLowerCase().includes(searchQuery.toLowerCase()));

        return matchesType && matchesSearch;
      });

      console.log(`Filtered ${filtered.length} schools for type: ${selectedProgramType}, search: "${searchQuery}"`);
      return filtered;
    } catch (error) {
      console.error('Error filtering schools:', error);
      return [];
    }
  }, [schools, selectedProgramType, searchQuery]);

  const handleProgramTypeChange = (programType) => {
    setSelectedProgramType(programType);
    setSelectedSchool(null);
    setSearchQuery('');
    setShowDropdown(false);
  };

  const handleSearchChange = (e) => {
    try {
      const value = e.target.value || '';
      setSearchQuery(value);
      // Always show dropdown when typing
      setShowDropdown(true);
    } catch (error) {
      console.error('Error handling search change:', error);
      setSearchQuery('');
      setShowDropdown(false);
    }
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
              filteredSchools.slice(0, 50).map((school) => {
                // Safety check for school data
                if (!school || !school['Medical School Name']) {
                  return null;
                }

                return (
                  <div
                    key={school['Medical School Name']}
                    className="dropdown-item"
                    onClick={() => handleSchoolSelect(school)}
                  >
                    <div className="school-name">
                      {school['Medical School Name'] || 'Unknown School'}
                    </div>
                    <div className="school-details">
                      <div className="school-state">
                        {school.State || 'Unknown State'}
                      </div>
                      <div className="international-indicator">
                        {school['Accepts International Students'] ? (
                          <span className="intl-badge accepted">Intl</span>
                        ) : (
                          <span className="intl-badge not-accepted">US Only</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              }).filter(Boolean) // Remove any null items
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default SchoolSelector;