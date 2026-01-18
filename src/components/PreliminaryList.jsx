import React, { useState, useMemo } from 'react';
import './PreliminaryList.css';

function PreliminaryList({ schools, onRemove, applicantData }) {
  const [filterType, setFilterType] = useState('All'); // All, MD, DO
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('name'); // name, avgMcat, avgGpa
  const [sortOrder, setSortOrder] = useState('asc');

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

  // Filter and sort schools
  const filteredAndSortedSchools = useMemo(() => {
    let filtered = schools;

    // Filter by type
    if (filterType !== 'All') {
      filtered = filtered.filter(school => school['Degree Type'] === filterType);
    }

    // Filter by search
    if (searchQuery) {
      filtered = filtered.filter(school =>
        school['Medical School Name'].toLowerCase().includes(searchQuery.toLowerCase()) ||
        school.State.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Sort
    filtered.sort((a, b) => {
      let aVal, bVal;
      switch (sortBy) {
        case 'avgMcat':
          aVal = parseFloat(a['Average MCAT']) || 0;
          bVal = parseFloat(b['Average MCAT']) || 0;
          break;
        case 'avgGpa':
          aVal = parseFloat(a['Average GPA']) || 0;
          bVal = parseFloat(b['Average GPA']) || 0;
          break;
        default: // name
          aVal = a['Medical School Name'].toLowerCase();
          bVal = b['Medical School Name'].toLowerCase();
      }

      if (sortBy === 'name') {
        return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      } else {
        return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
      }
    });

    return filtered;
  }, [schools, filterType, searchQuery, sortBy, sortOrder]);

  const handleSort = (newSortBy) => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
  };

  if (schools.length === 0) {
    return (
      <div className="school-list-container">
        <div className="empty-state">
          <p>Your school list is empty. Search and add schools above to get started.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="school-list-container">
      {/* Controls */}
      <div className="list-controls">
        <div className="filter-chips">
          <button
            className={`chip ${filterType === 'All' ? 'active' : ''}`}
            onClick={() => setFilterType('All')}
          >
            All
          </button>
          <button
            className={`chip ${filterType === 'MD' ? 'active' : ''}`}
            onClick={() => setFilterType('MD')}
          >
            MD
          </button>
          <button
            className={`chip ${filterType === 'DO' ? 'active' : ''}`}
            onClick={() => setFilterType('DO')}
          >
            DO
          </button>
        </div>

        <div className="search-sort-row">
          <input
            type="text"
            placeholder="Search schools..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />

          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [newSortBy, newSortOrder] = e.target.value.split('-');
              setSortBy(newSortBy);
              setSortOrder(newSortOrder);
            }}
            className="sort-select"
          >
            <option value="name-asc">Name ↑</option>
            <option value="name-desc">Name ↓</option>
            <option value="avgMcat-asc">MCAT ↑</option>
            <option value="avgMcat-desc">MCAT ↓</option>
            <option value="avgGpa-asc">GPA ↑</option>
            <option value="avgGpa-desc">GPA ↓</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="schools-table">
          <thead>
            <tr>
              <th className="school-cell">School</th>
              <th>Degree</th>
              <th>State</th>
              <th>Avg GPA</th>
              <th>Avg MCAT</th>
              <th>Min MCAT</th>
              {applicantData.state && <th>Residency</th>}
              <th>In-State %</th>
              <th>Out-State %</th>
              <th>In-State Advantage</th>
              <th>Classification</th>
              <th>Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSortedSchools.map((school, index) => {
              const residencyStatus = getResidencyStatus(school.State, applicantData.state);
              const gpaClass = classifyGPA(applicantData.gpa, school['Average GPA']);
              const mcatClass = classifyMCAT(applicantData.mcat, school['Average MCAT']);
              const overallClassification = getOverallClassification(gpaClass, mcatClass);

              return (
                <tr key={index}>
                  <td className="school-cell">
                    <a
                      href={school['Website URL']}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="school-link"
                    >
                      {school['Medical School Name']}
                    </a>
                  </td>
                  <td>
                    <span className="badge degree-badge">{school['Degree Type']}</span>
                  </td>
                  <td className="text-cell">{school.State}</td>
                  <td className="numeric tabular-nums">{school['Average GPA']}</td>
                  <td className="numeric tabular-nums">{school['Average MCAT']}</td>
                  <td className="text-cell">{school['Minimum MCAT Notes']}</td>
                  {applicantData.state && (
                    <td>
                      {residencyStatus && (
                        <span className={`badge residency-badge ${residencyStatus.toLowerCase().replace('-', '')}`}>
                          {residencyStatus === 'In-State' ? 'In-State' : 'OOS'}
                        </span>
                      )}
                    </td>
                  )}
                  <td className="numeric tabular-nums">
                    {school['In-State Matriculants %'] ? `${school['In-State Matriculants %']}%` : 'N/A'}
                  </td>
                  <td className="numeric tabular-nums">
                    {school['Out-of-State Matriculants %'] ? `${school['Out-of-State Matriculants %']}%` : 'N/A'}
                  </td>
                  <td>
                    {school['In-State Advantage'] && school['In-State Advantage'] !== 'unknown' ? (
                      <span className={`badge advantage-badge ${school['In-State Advantage'].toLowerCase()}`}>
                        {school['In-State Advantage']}
                      </span>
                    ) : (
                      <span className="badge advantage-badge na">N/A</span>
                    )}
                  </td>
                  <td>
                    {overallClassification ? (
                      <span className={`badge classification-badge ${overallClassification.toLowerCase()}`}>
                        {overallClassification}
                      </span>
                    ) : (
                      <span className="badge classification-badge na">N/A</span>
                    )}
                  </td>
                  <td className="notes-cell">
                    <input
                      type="text"
                      placeholder="Add note..."
                      className="notes-input"
                      defaultValue={school.notes || ''}
                    />
                  </td>
                  <td>
                    <button
                      className="remove-btn"
                      onClick={() => onRemove(school['Medical School Name'])}
                      title="Remove from list"
                    >
                      ×
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PreliminaryList;