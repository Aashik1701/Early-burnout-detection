import React, { useState } from 'react';
import { GlassPanel } from '../components/ui/GlassPanel';
import { ArrowDownToLine, Search } from 'lucide-react';

export function ActionQueue({ data, filters }) {
    const [sortConfig, setSortConfig] = useState({ key: 'risk_score', direction: 'desc' });

    const sortedData = [...data].sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) return sortConfig.direction === 'asc' ? -1 : 1;
        if (a[sortConfig.key] > b[sortConfig.key]) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
    });

    const handleSort = (key) => {
        let direction = 'desc';
        if (sortConfig.key === key && sortConfig.direction === 'desc') {
            direction = 'asc';
        }
        setSortConfig({ key, direction });
    };

    const getRiskBadge = (level) => {
        const colors = {
            High: { bg: 'var(--risk-high-mute)', color: 'var(--risk-high)' },
            Medium: { bg: 'var(--risk-medium-mute)', color: 'var(--risk-medium)' },
            Low: { bg: 'var(--risk-low-mute)', color: 'var(--risk-low)' }
        };
        const style = colors[level] || colors.Low;
        return (
            <span style={{
                backgroundColor: style.bg,
                color: style.color,
                padding: '0.25rem 0.5rem',
                borderRadius: 'var(--radius-full)',
                fontSize: '0.75rem',
                fontWeight: 600
            }}>
                {level || 'Unknown'}
            </span>
        );
    };

    const exportCSV = () => {
        const csvHeader = ['Student_ID', 'dropout_probability', 'risk_score', 'burnout_risk_level', 'recommended_intervention_strategy'].join(',');
        const csvBody = sortedData.map(r => [
            r.Student_ID, r.dropout_probability, r.risk_score, r.burnout_risk_level, `"${r.recommended_intervention_strategy || ''}"`
        ].join(',')).join('\n');
        const blob = new Blob([csvHeader + '\n' + csvBody], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'action_queue.csv';
        a.click();
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div>
                    <h3 style={{ marginBottom: '0.5rem' }}>⚡ Action Queue</h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Students sorted by descending risk score.</p>
                </div>
                <button
                    onClick={exportCSV}
                    style={{
                        display: 'flex', alignItems: 'center', gap: '0.5rem',
                        backgroundColor: 'var(--accent-blue)', color: '#fff',
                        padding: '0.5rem 1rem', borderRadius: 'var(--radius-sm)',
                        fontWeight: 500, fontSize: '0.875rem'
                    }}
                >
                    <ArrowDownToLine size={16} />
                    Export CSV
                </button>
            </div>

            <GlassPanel style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
                <div style={{ overflowX: 'auto', overflowY: 'auto', maxHeight: 'calc(100vh - 220px)' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                        <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--bg-card-hover)', zIndex: 10 }}>
                            <tr>
                                {['Student_ID', 'dropout_probability', 'risk_score', 'burnout_risk_level', 'recommended_intervention_strategy'].map(key => (
                                    <th
                                        key={key}
                                        onClick={() => handleSort(key)}
                                        style={{
                                            padding: '1rem',
                                            fontSize: '0.75rem',
                                            textTransform: 'uppercase',
                                            letterSpacing: '0.05em',
                                            color: 'var(--text-secondary)',
                                            cursor: 'pointer',
                                            borderBottom: '1px solid var(--border-light)'
                                        }}
                                    >
                                        {key.replace(/_/g, ' ')}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {sortedData.map((row) => (
                                <tr key={row.Student_ID} style={{ borderBottom: '1px solid var(--border-light)' }}>
                                    <td style={{ padding: '1rem', fontWeight: 500 }}>{row.Student_ID}</td>
                                    <td style={{ padding: '1rem' }}>{row.dropout_probability?.toFixed(4)}</td>
                                    <td style={{ padding: '1rem' }}>{row.risk_score?.toFixed(1)}</td>
                                    <td style={{ padding: '1rem' }}>{getRiskBadge(row.burnout_risk_level)}</td>
                                    <td style={{ padding: '1rem', fontSize: '0.875rem' }}>{row.recommended_intervention_strategy}</td>
                                </tr>
                            ))}
                            {sortedData.length === 0 && (
                                <tr>
                                    <td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                        No students match current filters.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </GlassPanel>
        </div>
    );
}
