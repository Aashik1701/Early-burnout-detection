import React, { useState, useMemo } from 'react';
import { GlassPanel } from '../components/ui/GlassPanel';

export function CohortInsights({ data }) {
    const dimensions = ['Department', 'Semester', 'Gender', 'Part_Time_Job'];
    const [selectedDim, setSelectedDim] = useState('Department');

    const summary = useMemo(() => {
        const map = new Map();
        data.forEach(d => {
            const key = d[selectedDim] || 'Unknown';
            if (!map.has(key)) map.set(key, { total: 0, high: 0, sumRisk: 0 });
            const stats = map.get(key);
            stats.total += 1;
            if (d.burnout_risk_level === 'High') stats.high += 1;
            stats.sumRisk += d.risk_score || 0;
        });

        return Array.from(map.entries()).map(([key, stats]) => ({
            name: key,
            total: stats.total,
            highRate: stats.total ? (stats.high / stats.total) * 100 : 0,
            avgRisk: stats.total ? (stats.sumRisk / stats.total) : 0
        })).sort((a, b) => b.highRate - a.highRate);
    }, [data, selectedDim]);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h3 style={{ marginBottom: '0.5rem' }}>🔬 Cohort Insights</h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Identify where risk concentrates across cohort dimensions.</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>🔎 Cohort dimension</label>
                    <select
                        value={selectedDim}
                        onChange={e => setSelectedDim(e.target.value)}
                        style={{ padding: '0.5rem', backgroundColor: 'var(--bg-card)', color: 'white', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-sm)' }}
                    >
                        {dimensions.map(dim => <option key={dim} value={dim}>{dim.replace(/_/g, ' ')}</option>)}
                    </select>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1.5rem' }}>
                <GlassPanel>
                    <h4 style={{ marginBottom: '1.5rem', fontSize: '1rem' }}>High-risk Rate by {selectedDim.replace(/_/g, ' ')}</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {summary.map(item => (
                            <div key={item.name}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                                    <span>{item.name}</span>
                                    <span style={{ fontWeight: 600 }}>{item.highRate.toFixed(1)}%</span>
                                </div>
                                <div style={{ width: '100%', backgroundColor: 'var(--bg-main)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{ width: `${item.highRate}%`, height: '100%', backgroundColor: 'var(--risk-high)', transition: 'width 0.5s' }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </GlassPanel>

                <GlassPanel>
                    <h4 style={{ marginBottom: '1.5rem', fontSize: '1rem' }}>Average Risk Score</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {[...summary].sort((a, b) => b.avgRisk - a.avgRisk).map(item => (
                            <div key={item.name}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                                    <span>{item.name}</span>
                                    <span style={{ fontWeight: 600 }}>{item.avgRisk.toFixed(1)}</span>
                                </div>
                                <div style={{ width: '100%', backgroundColor: 'var(--bg-main)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{ width: `${item.avgRisk}%`, height: '100%', backgroundColor: 'var(--risk-medium)', transition: 'width 0.5s' }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </GlassPanel>
            </div>
        </div>
    );
}
