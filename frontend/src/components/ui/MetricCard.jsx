import React from 'react';
import { GlassPanel } from './GlassPanel';
import { motion } from 'framer-motion';

export function MetricCard({ title, value, subtitle, highlightColor = 'var(--accent-blue)', delay = 0 }) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay }}
        >
            <GlassPanel className="metric-card" animate={false}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {title}
                    </span>
                    <span style={{ color: highlightColor, fontSize: '1.875rem', fontWeight: 700, lineHeight: 1 }}>
                        {value}
                    </span>
                    {subtitle && (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                            {subtitle}
                        </span>
                    )}
                </div>
            </GlassPanel>
        </motion.div>
    );
}
