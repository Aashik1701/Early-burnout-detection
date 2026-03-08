import React from 'react';

export function TopBar() {
    return (
        <div style={{
            height: '72px',
            width: '100%',
            backgroundColor: 'rgba(22, 27, 34, 0.65)',
            backdropFilter: 'blur(12px)',
            borderBottom: '1px solid var(--border-light)',
            display: 'flex',
            alignItems: 'center',
            padding: '0 2rem',
            position: 'sticky',
            top: 0,
            zIndex: 50
        }}>
            <div>
                <h1 style={{ fontSize: '1.25rem' }}>🎓 Early Burnout & Dropout Risk</h1>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Model artifacts · Prioritize with human review
                </p>
            </div>
        </div>
    );
}
