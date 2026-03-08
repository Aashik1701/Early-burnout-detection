import React, { useState } from 'react';
import { GlassPanel } from '../components/ui/GlassPanel';
import { MetricCard } from '../components/ui/MetricCard';

export function StudentDetail({ data }) {
    const [selectedId, setSelectedId] = useState(data.length > 0 ? data[0].Student_ID : '');

    const selectedRow = data.find(d => String(d.Student_ID) === String(selectedId)) || data[0];

    if (!selectedRow) return <div style={{ color: 'var(--text-muted)' }}>No student data available</div>;

    const riskLvl = selectedRow.burnout_risk_level || 'Low';
    const riskColor = riskLvl === 'High' ? 'var(--risk-high)' : riskLvl === 'Medium' ? 'var(--risk-medium)' : 'var(--risk-low)';

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0 }}>👤 Student Detail</h3>
                <select
                    value={selectedId}
                    onChange={e => setSelectedId(e.target.value)}
                    style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: 'var(--bg-card-hover)',
                        color: 'white',
                        border: '1px solid var(--border-light)',
                        borderRadius: 'var(--radius-sm)',
                        minWidth: '200px'
                    }}
                >
                    {data.map(d => (
                        <option key={d.Student_ID} value={d.Student_ID}>Student #{d.Student_ID}</option>
                    ))}
                </select>
            </div>

            <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}><MetricCard title="Dropout Probability" value={selectedRow.dropout_probability?.toFixed(4)} /></div>
                <div style={{ flex: 1 }}><MetricCard title="Risk Score" value={selectedRow.risk_score?.toFixed(1)} /></div>
                <div style={{ flex: 1 }}><MetricCard title="Risk Level" value={riskLvl} highlightColor={riskColor} /></div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1.5rem' }}>
                <GlassPanel>
                    <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '0.5rem', letterSpacing: '0.05em' }}>
                        🎓 Academic Disengagement Indicators
                    </div>
                    <div style={{ fontSize: '1rem', lineHeight: 1.5 }}>
                        {selectedRow.academic_disengagement_indicators || 'None identified'}
                    </div>
                </GlassPanel>

                <GlassPanel>
                    <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '0.5rem', letterSpacing: '0.05em' }}>
                        ⚠️ Key Behavioural Triggers
                    </div>
                    <div style={{ fontSize: '1rem', lineHeight: 1.5 }}>
                        {selectedRow.key_behavioural_triggers || 'None identified'}
                    </div>
                </GlassPanel>
            </div>

            <GlassPanel style={{ background: 'linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1))', borderColor: 'var(--accent-blue)' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--accent-blue)', marginBottom: '0.5rem', letterSpacing: '0.05em', fontWeight: 600 }}>
                    💊 Recommended Intervention Strategy
                </div>
                <div style={{ fontSize: '1.125rem', lineHeight: 1.5, fontWeight: 500 }}>
                    {selectedRow.recommended_intervention_strategy || 'Standard monitoring'}
                </div>
            </GlassPanel>

            {/* Basic text fallback for the Gauge Chart. Plotting a gauge from scratch in pure Recharts is arduous. We will use a styling bar instead. */}
            <GlassPanel>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Dropout Probability Meter</span>
                    <span style={{ fontWeight: 700, color: riskColor }}>{(selectedRow.dropout_probability * 100).toFixed(1)}%</span>
                </div>
                <div style={{ width: '100%', height: '24px', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                    <div style={{
                        width: `${Math.min(100, selectedRow.dropout_probability * 100)}%`,
                        height: '100%',
                        backgroundColor: riskColor,
                        transition: 'width 0.5s ease-in-out'
                    }} />
                </div>
            </GlassPanel>
        </div>
    );
}
