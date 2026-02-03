import React, { useState, useMemo, useCallback } from 'react';
import {
  classifyGPA,
  classifyMCAT,
  getOverallClassification,
  getResidencyStatus
} from '../utils/classification';
import './PreliminaryList.css';

function PreliminaryList({ schools, onRemove, onUpdateNotes, onReorder, applicantData }) {
  const [filterType, setFilterType] = useState('All'); // All, MD, DO
  const [filterClassification, setFilterClassification] = useState('All'); // All, Reach, Target, Safety
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('name'); // name, avgMcat, avgGpa, classification
  const [sortOrder, setSortOrder] = useState('asc');
  const [draggedIndex, setDraggedIndex] = useState(null);
  const [dragOverIndex, setDragOverIndex] = useState(null);

  // Calculate degree type counts
  const degreeCounts = useMemo(() => {
    const counts = {
      all: schools.length,
      md: schools.filter(s => s['Degree Type'] === 'MD').length,
      do: schools.filter(s => s['Degree Type'] === 'DO').length
    };
    return counts;
  }, [schools]);

  // Calculate classification counts based on current filter
  const classificationCounts = useMemo(() => {
    // First filter by degree type
    let filtered = schools;
    if (filterType !== 'All') {
      filtered = filtered.filter(school => school['Degree Type'] === filterType);
    }

    // Calculate classifications for filtered schools
    const counts = {
      reach: 0,
      target: 0,
      safety: 0,
      unclassified: 0
    };

    filtered.forEach(school => {
      const gpaClass = classifyGPA(applicantData.gpa, school['Average GPA']);
      const mcatClass = classifyMCAT(applicantData.mcat, school['Average MCAT']);
      const overallClassification = getOverallClassification(gpaClass, mcatClass);

      if (overallClassification === 'Reach') {
        counts.reach++;
      } else if (overallClassification === 'Target') {
        counts.target++;
      } else if (overallClassification === 'Undershoot') {
        counts.safety++;
      } else {
        counts.unclassified++;
      }
    });

    return counts;
  }, [schools, filterType, applicantData.gpa, applicantData.mcat]);

  // Filter and sort schools
  const filteredAndSortedSchools = useMemo(() => {
    let filtered = schools;

    // Filter by degree type
    if (filterType !== 'All') {
      filtered = filtered.filter(school => school['Degree Type'] === filterType);
    }

    // Filter by classification
    if (filterClassification !== 'All') {
      filtered = filtered.filter(school => {
        const gpaClass = classifyGPA(applicantData.gpa, school['Average GPA']);
        const mcatClass = classifyMCAT(applicantData.mcat, school['Average MCAT']);
        const classification = getOverallClassification(gpaClass, mcatClass);
        
        if (filterClassification === 'Safety') {
          return classification === 'Undershoot';
        }
        return classification === filterClassification;
      });
    }

    // Filter by search
    if (searchQuery) {
      filtered = filtered.filter(school =>
        school['Medical School Name'].toLowerCase().includes(searchQuery.toLowerCase()) ||
        school.State.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Sort
    filtered = [...filtered].sort((a, b) => {
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
        case 'classification':
          const classOrder = { 'Reach': 0, 'Target': 1, 'Undershoot': 2, null: 3 };
          const aClass = getOverallClassification(
            classifyGPA(applicantData.gpa, a['Average GPA']),
            classifyMCAT(applicantData.mcat, a['Average MCAT'])
          );
          const bClass = getOverallClassification(
            classifyGPA(applicantData.gpa, b['Average GPA']),
            classifyMCAT(applicantData.mcat, b['Average MCAT'])
          );
          aVal = classOrder[aClass] ?? 3;
          bVal = classOrder[bClass] ?? 3;
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
  }, [schools, filterType, filterClassification, searchQuery, sortBy, sortOrder, applicantData]);

  // Drag and drop handlers
  const handleDragStart = useCallback((e, index) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.target.outerHTML);
    e.target.style.opacity = '0.5';
  }, []);

  const handleDragEnd = useCallback((e) => {
    e.target.style.opacity = '1';
    setDraggedIndex(null);
    setDragOverIndex(null);
  }, []);

  const handleDragOver = useCallback((e, index) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverIndex(index);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOverIndex(null);
  }, []);

  const handleDrop = useCallback((e, dropIndex) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === dropIndex) {
      setDraggedIndex(null);
      setDragOverIndex(null);
      return;
    }

    const newSchools = [...schools];
    const [draggedSchool] = newSchools.splice(draggedIndex, 1);
    newSchools.splice(dropIndex, 0, draggedSchool);
    
    onReorder(newSchools);
    setDraggedIndex(null);
    setDragOverIndex(null);
  }, [draggedIndex, schools, onReorder]);

  // Notes handler with debounce
  const handleNotesChange = useCallback((schoolName, value) => {
    onUpdateNotes(schoolName, value);
  }, [onUpdateNotes]);

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
        <div className="filter-row">
          <div className="filter-chips">
            <button
              className={`chip ${filterType === 'All' ? 'active' : ''}`}
              onClick={() => setFilterType('All')}
            >
              All ({degreeCounts.all})
            </button>
            <button
              className={`chip ${filterType === 'MD' ? 'active' : ''}`}
              onClick={() => setFilterType('MD')}
            >
              MD ({degreeCounts.md})
            </button>
            <button
              className={`chip ${filterType === 'DO' ? 'active' : ''}`}
              onClick={() => setFilterType('DO')}
            >
              DO ({degreeCounts.do})
            </button>
          </div>

          {/* Classification Filter */}
          <div className="classification-filter">
            <button
              className={`chip classification-chip ${filterClassification === 'All' ? 'active' : ''}`}
              onClick={() => setFilterClassification('All')}
            >
              All
            </button>
            <button
              className={`chip classification-chip reach ${filterClassification === 'Reach' ? 'active' : ''}`}
              onClick={() => setFilterClassification('Reach')}
            >
              Reach ({classificationCounts.reach})
            </button>
            <button
              className={`chip classification-chip target ${filterClassification === 'Target' ? 'active' : ''}`}
              onClick={() => setFilterClassification('Target')}
            >
              Target ({classificationCounts.target})
            </button>
            <button
              className={`chip classification-chip safety ${filterClassification === 'Safety' ? 'active' : ''}`}
              onClick={() => setFilterClassification('Safety')}
            >
              Safety ({classificationCounts.safety})
            </button>
          </div>
        </div>

        {/* Classification Summary */}
        <div className="classification-summary">
          <div className="summary-item reach">
            <span className="summary-label">Reach</span>
            <span className="summary-count">({classificationCounts.reach})</span>
          </div>
          <div className="summary-item target">
            <span className="summary-label">Target</span>
            <span className="summary-count">({classificationCounts.target})</span>
          </div>
          <div className="summary-item safety">
            <span className="summary-label">Safety</span>
            <span className="summary-count">({classificationCounts.safety})</span>
          </div>
          {classificationCounts.unclassified > 0 && (
            <div className="summary-item unclassified">
              <span className="summary-label">Unclassified</span>
              <span className="summary-count">({classificationCounts.unclassified})</span>
            </div>
          )}
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
            <option value="classification-asc">Classification (Reach→Safety)</option>
            <option value="classification-desc">Classification (Safety→Reach)</option>
          </select>
        </div>
      </div>

      {/* Drag hint */}
      <div className="drag-hint">
        <span>💡 Drag rows to reorder your list</span>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="schools-table">
          <thead>
            <tr>
              <th className="drag-handle-header"></th>
              <th className="school-cell">School</th>
              <th>Degree</th>
              <th>Application</th>
              <th>State</th>
              <th>Avg GPA</th>
              <th>Avg MCAT</th>
              {applicantData.state && <th>Residency</th>}
              <th>In-State %</th>
              <th>OOS %</th>
              <th>Advantage</th>
              <th>Casper</th>
              <th>PREview</th>
              <th>Classification</th>
              <th>Notes</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSortedSchools.map((school, index) => {
              const residencyStatus = getResidencyStatus(school.State, applicantData.state);
              const gpaClass = classifyGPA(applicantData.gpa, school['Average GPA']);
              const mcatClass = classifyMCAT(applicantData.mcat, school['Average MCAT']);
              const overallClassification = getOverallClassification(gpaClass, mcatClass);
              const isDragOver = dragOverIndex === index;

              return (
                <tr
                  key={school['Medical School Name']}
                  draggable
                  onDragStart={(e) => handleDragStart(e, index)}
                  onDragEnd={handleDragEnd}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, index)}
                  className={`${isDragOver ? 'drag-over' : ''} ${draggedIndex === index ? 'dragging' : ''}`}
                >
                  <td className="drag-handle">
                    <span className="drag-icon">⋮⋮</span>
                  </td>
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
                  <td>
                    <span className="badge app-system-badge">{school['Application System']}</span>
                  </td>
                  <td className="text-cell">{school.State}</td>
                  <td className="text-cell tabular-nums">{school['Average GPA']}</td>
                  <td className="text-cell tabular-nums">{school['Average MCAT']}</td>
                  {applicantData.state && (
                    <td>
                      {residencyStatus && (
                        <span className={`badge residency-badge ${residencyStatus.toLowerCase().replace('-', '')}`}>
                          {residencyStatus === 'In-State' ? 'In-State' : 'OOS'}
                        </span>
                      )}
                    </td>
                  )}
                  <td className="text-cell tabular-nums">
                    {school['In-State Matriculants %'] ? `${school['In-State Matriculants %']}%` : 'N/A'}
                  </td>
                  <td className="text-cell tabular-nums">
                    {school['Out-of-State Matriculants %'] ? `${school['Out-of-State Matriculants %']}%` : 'N/A'}
                  </td>
                  <td>
                    {(() => {
                      const inState = parseFloat(school['In-State Matriculants %']);
                      if (isNaN(inState)) return <span className="na-text">N/A</span>;
                      
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
                  </td>
                  <td>
                    {school['Requires Casper'] === 'True' ? (
                      <span className="badge casper-badge required">Required</span>
                    ) : (
                      <span className="badge casper-badge not-required">No</span>
                    )}
                  </td>
                  <td>
                    {school['Requires PREview'] && school['Requires PREview'] !== 'Not Required' ? (
                      <span className="badge preview-badge required">Required</span>
                    ) : (
                      <span className="badge preview-badge not-required">No</span>
                    )}
                  </td>
                  <td>
                    {overallClassification ? (
                      <span className={`badge classification-badge ${overallClassification.toLowerCase()}`}>
                        {overallClassification}
                      </span>
                    ) : applicantData.gpa && applicantData.mcat ? (
                      <span className="badge classification-badge na">N/A</span>
                    ) : (
                      <span className="classification-placeholder">-</span>
                    )}
                  </td>
                  <td className="notes-cell">
                    <input
                      type="text"
                      placeholder="Add note..."
                      className="notes-input"
                      value={school.notes || ''}
                      onChange={(e) => handleNotesChange(school['Medical School Name'], e.target.value)}
                    />
                  </td>
                  <td className="action-cell">
                    <button
                      className="remove-btn"
                      onClick={() => onRemove(school['Medical School Name'])}
                      title="Remove from list"
                    >
                      ✕
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
