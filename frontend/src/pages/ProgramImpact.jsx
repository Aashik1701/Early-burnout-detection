import React, { useMemo } from 'react';
import { GlassPanel } from '../components/ui/GlassPanel';
import { MetricCard } from '../components/ui/MetricCard';

export function ProgramImpact({ data, metrics, filters }) {
    const activeThreshold = metrics.mode_metrics[filters.mode]?.threshold || metrics.threshold || 0.5;

    const { flagged, totalFlagged, highInFlagged, totalHigh, fpCount } = useMemo(() => {
        const _flagged = data.filter(d => d.dropout_probability >= activeThreshold);
        const _highInFlagged = _flagged.filter(d => d.burnout_risk_level === 'High').length;
        const _totalHigh = data.filter(d => d.burnout_risk_level === 'High').length;
        return {
            flagged: _flagged,
            totalFlagged: _flagged.length,
            highInFlagged: _highInFlagged,
            totalHigh: _totalHigh,
            fpCount: _flagged.length - _highInFlagged
        };
    }, [data, activeThreshold]);

    const highCapture = totalHigh ? (highInFlagged / totalHigh) * 100 : 0;
    const fpRate = totalFlagged ? (fpCount / totalFlagged) * 100 : 0;
    const totalNotFlagged = data.length - totalFlagged;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div>
                <h3 style={{ marginBottom: '0.5rem' }}>🎯 Program Impact</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Leadership-level view: projected outreach impact before acting.</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                <MetricCard title="Students Contacted" value={totalFlagged.toLocaleString()} />
                <MetricCard title="High-Risk Captured" value={`${highInFlagged} / ${totalHigh}`} highlightColor="var(--risk-low)" />
                <MetricCard title="High-Risk Capture %" value={`${highCapture.toFixed(1)}%`} highlightColor="var(--risk-low)" />
                <MetricCard title="False-Positive Load" value={`${fpCount} (${fpRate.toFixed(1)}%)`} highlightColor="var(--risk-high)" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <MetricCard title="Active Threshold" value={activeThreshold.toFixed(4)} />
                <MetricCard title="Flagged Rate" value={`${(data.length ? (totalFlagged / data.length) * 100 : 0).toFixed(1)}%`} />
                <MetricCard title="Students NOT Flagged" value={totalNotFlagged.toLocaleString()} />
            </div>

            <GlassPanel style={{ background: 'var(--accent-blue-mute)', borderColor: 'var(--accent-blue)' }}>
                <p style={{ margin: 0, color: 'var(--text-primary)', lineHeight: 1.6 }}>
                    At threshold <b style={{ color: 'var(--accent-blue)' }}>{activeThreshold.toFixed(4)}</b> ({filters.mode} mode), contacting <b style={{ color: 'var(--accent-blue)' }}>{totalFlagged.toLocaleString()}</b> students ({(data.length ? (totalFlagged / data.length) * 100 : 0).toFixed(1)}% of cohort) captures <b style={{ color: 'var(--risk-low)' }}>{highCapture.toFixed(1)}%</b> of high-risk students. Approximately <b style={{ color: 'var(--risk-high)' }}>{fpCount.toLocaleString()}</b> contacts ({fpRate.toFixed(1)}%) are false positives.
                </p>
            </GlassPanel>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
                <GlassPanel>
                    <h4 style={{ marginBottom: '1.5rem' }}>Intervention Funnel (Data View)</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {/* Simple CSS Funnel Representation */}
                        {[
                            { label: 'All Students', val: data.length, max: data.length, color: 'var(--accent-blue)' },
                            { label: 'Flagged by Model', val: totalFlagged, max: data.length, color: 'var(--risk-medium)' },
                            { label: 'High-Risk Captured', val: highInFlagged, max: data.length, color: 'var(--risk-high)' }
                        ].map(item => (
                            <div key={item.label}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                                    <span>{item.label}</span>
                                    <span style={{ fontWeight: 600 }}>{item.val.toLocaleString()} ({(item.max ? (item.val / item.max) * 100 : 0).toFixed(1)}%)</span>
                                </div>
                                <div style={{ width: '100%', backgroundColor: 'var(--bg-main)', height: '16px', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{ width: `${item.max ? (item.val / item.max) * 100 : 0}%`, height: '100%', backgroundColor: item.color, margin: '0 auto', transition: 'width 0.5s' }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </GlassPanel>
            </div>
        </div>
    );
}
