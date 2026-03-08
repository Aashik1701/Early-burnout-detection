import React from 'react';
import { LayoutDashboard, ListTodo, UserCircle, Calendar, Target, Users } from 'lucide-react';
import { motion } from 'framer-motion';

const NAV_ITEMS = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'queue', label: 'Action Queue', icon: ListTodo },
    { id: 'detail', label: 'Student Detail', icon: UserCircle },
    { id: 'planner', label: 'Intervention Planner', icon: Calendar },
    { id: 'impact', label: 'Program Impact', icon: Target },
    { id: 'cohort', label: 'Cohort Insights', icon: Users },
];

export function Sidebar({ currentTab, setCurrentTab, filters, setFilters, availableModes }) {

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    return (
        <div style={{
            width: '280px',
            height: '100%',
            backgroundColor: 'var(--bg-sidebar)',
            borderRight: '1px solid var(--border-light)',
            display: 'flex',
            flexDirection: 'column',
            padding: '1.5rem 1rem'
        }}>
            <div style={{ padding: '0 0.5rem 2rem 0.5rem' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }} className="text-gradient">
                    Sentinal AI Analytics
                </h2>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    Decision-support dashboard
                </p>
            </div>

            <nav style={{ flex: 1 }}>
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {NAV_ITEMS.map((item) => {
                        const Icon = item.icon;
                        const isActive = currentTab === item.id;
                        return (
                            <li key={item.id}>
                                <button
                                    onClick={() => setCurrentTab(item.id)}
                                    style={{
                                        width: '100%',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.75rem',
                                        padding: '0.75rem 1rem',
                                        borderRadius: 'var(--radius-sm)',
                                        color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
                                        backgroundColor: isActive ? 'var(--bg-card-hover)' : 'transparent',
                                        border: isActive ? '1px solid var(--border-strong)' : '1px solid transparent',
                                        transition: 'all 0.2s',
                                        fontWeight: isActive ? 600 : 500,
                                    }}
                                    onMouseEnter={(e) => {
                                        if (!isActive) {
                                            e.currentTarget.style.backgroundColor = 'var(--bg-card)';
                                            e.currentTarget.style.color = 'var(--text-primary)';
                                        }
                                    }}
                                    onMouseLeave={(e) => {
                                        if (!isActive) {
                                            e.currentTarget.style.backgroundColor = 'transparent';
                                            e.currentTarget.style.color = 'var(--text-muted)';
                                        }
                                    }}
                                >
                                    <Icon size={18} color={isActive ? 'var(--accent-blue)' : 'currentColor'} />
                                    {item.label}
                                    {isActive && (
                                        <motion.div layoutId="sidebar-active-indicator" style={{
                                            position: 'absolute',
                                            left: 0,
                                            width: '3px',
                                            height: '24px',
                                            backgroundColor: 'var(--accent-blue)',
                                            borderRadius: '0 4px 4px 0'
                                        }} />
                                    )}
                                </button>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* Basic Filters Area */}
            <div style={{ marginTop: 'auto', padding: '1rem 0.5rem', borderTop: '1px solid var(--border-light)' }}>
                <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                        Evaluation Mode
                    </label>
                    <select
                        value={filters.mode}
                        onChange={(e) => handleFilterChange('mode', e.target.value)}
                        style={{
                            width: '100%',
                            padding: '0.5rem',
                            backgroundColor: 'var(--bg-main)',
                            color: 'var(--text-primary)',
                            border: '1px solid var(--border-light)',
                            borderRadius: 'var(--radius-sm)'
                        }}
                    >
                        {availableModes.map(m => <option key={m} value={m}>{m === 'balanced' ? 'Balanced' : 'High Recall'}</option>)}
                    </select>
                </div>

                <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                        Search Student ID
                    </label>
                    <input
                        type="text"
                        placeholder="e.g. 1042"
                        value={filters.search}
                        onChange={(e) => handleFilterChange('search', e.target.value)}
                        style={{
                            width: '100%',
                            padding: '0.5rem',
                            backgroundColor: 'var(--bg-main)',
                            color: 'var(--text-primary)',
                            border: '1px solid var(--border-light)',
                            borderRadius: 'var(--radius-sm)'
                        }}
                    />
                </div>
            </div>
        </div>
    );
}
