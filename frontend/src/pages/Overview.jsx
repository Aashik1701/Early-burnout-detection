import React, { useMemo } from 'react';
import { MetricCard } from '../components/ui/MetricCard';
import { GlassPanel } from '../components/ui/GlassPanel';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';

export function Overview({ data, metrics, filters }) {
    const highRiskCount = data.filter(d => d.burnout_risk_level === 'High').length;
    const avgRiskScore = data.length ? data.reduce((acc, curr) => acc + curr.risk_score, 0) / data.length : 0;

    const modeMetrics = metrics.mode_metrics[filters.mode] || {};
    const highRiskRate = data.length ? (highRiskCount / data.length) * 100 : 0;

    // Risk Distribution Data
    const riskDist = useMemo(() => {
        const counts = { High: 0, Medium: 0, Low: 0 };
        data.forEach(d => { if (d.burnout_risk_level) counts[d.burnout_risk_level]++; });
        return [
            { name: 'Low', value: counts.Low, color: 'var(--risk-low)' },
            { name: 'Medium', value: counts.Medium, color: 'var(--risk-medium)' },
            { name: 'High', value: counts.High, color: 'var(--risk-high)' },
        ];
    }, [data]);

    // Strategy Mix Data
    const strategyMix = useMemo(() => {
        const counts = {};
        data.forEach(d => {
            const s = d.recommended_intervention_strategy || 'Unknown';
            counts[s] = (counts[s] || 0) + 1;
        });
        return Object.keys(counts).map((k, i) => ({
            name: k,
            value: counts[k],
            fill: `hsl(${220 + (i * 40)}, 80%, 60%)`
        })).sort((a, b) => b.value - a.value).slice(0, 8);
    }, [data]);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

            {/* Top KPIs */}
            <div>
                <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>📊 Key Metrics</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                    <MetricCard title="Students (filtered)" value={data.length.toLocaleString()} delay={0.1} />
                    <MetricCard title="High Risk" value={highRiskCount.toLocaleString()} highlightColor="var(--risk-high)" delay={0.2} />
                    <MetricCard title="Avg Risk Score" value={avgRiskScore.toFixed(1)} delay={0.3} />
                    <MetricCard title={`Recall (${filters.mode})`} value={modeMetrics.recall?.toFixed(4) || "—"} delay={0.4} />
                    <MetricCard title="ROC-AUC" value={metrics.roc_auc.toFixed(4)} delay={0.5} />
                </div>
            </div>

            <div style={{ width: '100%', height: '1px', backgroundColor: 'var(--border-light)' }} />

            {/* Charts Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>

                {/* Risk Level Distribution */}
                <GlassPanel>
                    <h4 style={{ marginBottom: '1.5rem' }}>🔴 Risk Level Distribution</h4>
                    <div style={{ height: '300px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={riskDist} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <XAxis dataKey="name" stroke="var(--text-secondary)" tickLine={false} axisLine={false} />
                                <YAxis stroke="var(--text-secondary)" tickLine={false} axisLine={false} />
                                <Tooltip
                                    cursor={{ fill: 'var(--bg-card-hover)' }}
                                    contentStyle={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: '8px' }}
                                />
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                    {riskDist.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </GlassPanel>

                {/* Intervention Strategy */}
                <GlassPanel>
                    <h4 style={{ marginBottom: '1.5rem' }}>💡 Intervention Strategy Mix</h4>
                    <div style={{ height: '300px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={strategyMix}
                                    dataKey="value"
                                    nameKey="name"
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={2}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: '8px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </GlassPanel>

            </div>
        </div>
    );
}
