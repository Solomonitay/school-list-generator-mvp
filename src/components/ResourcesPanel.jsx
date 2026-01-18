import React, { useState } from 'react';
import './ResourcesPanel.css';

function ResourcesPanel() {
  const resources = [
    {
      id: 'how-many-schools',
      title: 'How Many Medical Schools Should I Apply To?',
      description: 'Data-driven guide to building your application list',
      href: 'https://www.shemmassianconsulting.com/blog/how-many-medical-schools-should-i-apply-to',
      type: 'guide'
    },
    {
      id: 'school-list-video',
      title: 'Building Your Medical School List',
      description: 'Video guide on strategic school selection',
      href: 'https://www.youtube.com/watch?v=TdXzGQ74EFA',
      type: 'video'
    },
    {
      id: 'medical-schools-list',
      title: 'Complete List of U.S. Medical Schools',
      description: 'Comprehensive database of all accredited MD programs',
      href: 'https://www.shemmassianconsulting.com/medical-schools-in-the-united-states',
      type: 'external'
    }
  ];

  const visibleResources = resources; // Show all resources since we only have 3

  const getIcon = (type) => {
    switch (type) {
      case 'guide':
        return '📄';
      case 'video':
        return '🎥';
      case 'external':
        return '🔗';
      default:
        return '📄';
    }
  };

  return (
    <div className="resources-panel">
      <div className="panel-header">
        <h2 className="panel-title">Resources</h2>
      </div>

      <div className="resources-list">
        {visibleResources.map((resource) => (
          <a
            key={resource.id}
            href={resource.href}
            target="_blank"
            rel="noopener noreferrer"
            className="resource-item"
          >
            <div className="resource-icon">
              {getIcon(resource.type)}
            </div>
            <div className="resource-content">
              <div className="resource-title">{resource.title}</div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

export default ResourcesPanel;