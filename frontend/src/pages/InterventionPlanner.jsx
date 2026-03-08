import React, { useState, useMemo } from 'react';
import { GlassPanel } from '../components/ui/GlassPanel';
import { MetricCard } from '../components/ui/MetricCard';

export function InterventionPlanner({ data }) {
    const [counselors, setCounselors] = useState(5);
    const [slots, setSlots] = useState(10);

    const plannerData = useMemo(() => {
        const totalCapacity = counselors * slots;
        const sorted = [...data].sort((a, b) => b.risk_score - a.risk_score);

        return sorted.map((row, index) => {
            const isUrgent = (row.recommended_intervention_strategy || '').toUpperCase().includes('URGENT');
            return {
                ...row,
                urgency: isUrgent ? '🚨 URGENT' : 'Standard',
                assigned_counselor: `Counselor ${(index % counselors) + 1}`,
                week_slot: `Week ${Math.floor(index / totalCapacity) + 1}`
            };
        });
    }, [data, counselors, slots]);

    const totalCapacity = counselors * slots;
    const weeksNeeded = Math.ceil(plannerData.length / (totalCapacity || 1));
    const urgentCount = plannerData.filter(d => d.urgency === '🚨 URGENT').length;

    const weekOptions = Array.from(new Set(plannerData.map(d => d.week_slot))).sort();
    const [selectedWeek, setSelectedWeek] = useState(weekOptions[0] || 'Week 1');

    const weekData = plannerData.filter(d => d.week_slot === selectedWeek);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div>
                <h3 style={{ marginBottom: '0.5rem' }}>📅 Intervention Planner</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Convert risk into a concrete outreach plan with counselor assignments.</p>
            </div>

            <div style={{ display: 'flex', gap: '1.5rem' }}>
                <GlassPanel style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Available counselors</label>
                    <input
                        type="number" min="1" max="100" value={counselors} onChange={e => setCounselors(Number(e.target.value) || 1)}
                        style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', color: 'white', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-sm)' }}
                    />
                </GlassPanel>
                <GlassPanel style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Weekly contact slots per counselor</label>
                    <input
                        type="number" min="1" max="50" value={slots} onChange={e => setSlots(Number(e.target.value) || 1)}
                        style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', color: 'white', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-sm)' }}
                    />
                </GlassPanel>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                <MetricCard title="Total Weekly Capacity" value={totalCapacity} />
                <MetricCard title="Students to Contact" value={plannerData.length.toLocaleString()} />
                <MetricCard title="Weeks Needed" value={weeksNeeded} />
                <MetricCard title="Urgent Cases" value={urgentCount.toLocaleString()} highlightColor="var(--risk-high)" />
            </div>

            <GlassPanel style={{ display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
                <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h4 style={{ margin: 0 }}>Prioritized Contact List</h4>
                    <select
                        value={selectedWeek}
                        onChange={e => setSelectedWeek(e.target.value)}
                        style={{ padding: '0.4rem', backgroundColor: 'var(--bg-main)', color: 'white', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-sm)' }}
                    >
                        {weekOptions.map(w => <option key={w} value={w}>{w}</option>)}
                    </select>
                </div>
                <div style={{ overflowX: 'auto', maxHeight: '400px' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                        <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--bg-card)', zIndex: 10 }}>
                            <tr>
                                {['Student_ID', 'Urgency', 'Assigned Counselor', 'Risk Score', 'Strategy'].map(h => (
                                    <th key={h} style={{ padding: '0.75rem 1.5rem', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)', borderBottom: '1px solid var(--border-light)' }}>{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {weekData.map(row => (
                                <tr key={row.Student_ID} style={{ borderBottom: '1px solid var(--border-light)' }}>
                                    <td style={{ padding: '0.75rem 1.5rem', fontWeight: 500 }}>{row.Student_ID}</td>
                                    <td style={{ padding: '0.75rem 1.5rem', color: row.urgency.includes('URGENT') ? 'var(--risk-high)' : 'inherit', fontWeight: row.urgency.includes('URGENT') ? 600 : 400 }}>{row.urgency}</td>
                                    <td style={{ padding: '0.75rem 1.5rem' }}>{row.assigned_counselor}</td>
                                    <td style={{ padding: '0.75rem 1.5rem' }}>{row.risk_score?.toFixed(1)}</td>
                                    <td style={{ padding: '0.75rem 1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{row.recommended_intervention_strategy}</td>
                                </tr>
                            ))}
                            {weekData.length === 0 && <tr><td colSpan={5} style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No data for selected week</td></tr>}
                        </tbody>
                    </table>
                </div>
            </GlassPanel>
        </div>
    );
}
