import React, { useState, useEffect } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { ArrowRight, Zap, ShieldCheck, Activity, LayoutDashboard, Database, Server, Component, Book, BarChart3 } from 'lucide-react';

// Reusable animated section wrapper
const FadeInSection = ({ children, delay = 0, className = '' }) => (
    <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-50px" }} // Reduced margin to trigger slightly earlier, smoother flow
        transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
        className={className}
    >
        {children}
    </motion.div>
);

export function LandingPage({ enterDashboard }) {
    const { scrollYProgress } = useScroll();
    const heroOpacity = useTransform(scrollYProgress, [0, 0.15], [1, 0]);
    const heroY = useTransform(scrollYProgress, [0, 0.2], [0, 50]);
    const dashboardY = useTransform(scrollYProgress, [0, 0.2], [20, -50]); // Parallax lift

    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        let ticking = false;
        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    setScrolled(window.scrollY > 50);
                    ticking = false;
                });
                ticking = true;
            }
        };
        window.addEventListener('scroll', handleScroll, { passive: true }); // Passive listener for better perf
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <div className="landing-container">
            {/* Global Background Layers */}
            <div className="ambient-orb orb-1" />
            <div className="ambient-orb orb-2" />
            <div className="ambient-orb orb-3" />
            <div className="bg-grid" />
            <div className="bg-noise" />

            {/* Sticky Navigation */}
            <nav className={`landing-nav ${scrolled ? 'scrolled' : ''}`}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Book size={18} color="#fff" />
                    </div>
                    <span style={{ fontSize: '1rem', fontWeight: 600, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>Sentinel AI</span>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button className="btn-secondary" onClick={() => window.open('https://sentinel-ai-analytics.streamlit.app/', '_blank')}>
                        Legacy App
                    </button>
                    <button className="btn-primary" onClick={enterDashboard}>
                        Enter Platform
                    </button>
                </div>
            </nav>

            {/* 1. HERO SECTION */}
            <section style={{ position: 'relative', paddingTop: '14rem', paddingBottom: '6rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', zIndex: 10 }}>
                <motion.div style={{ opacity: heroOpacity, y: heroY, padding: '0 2rem' }}>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '0.35rem 0.75rem', borderRadius: 'var(--radius-full)', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.03)', marginBottom: '2rem', color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 500, backdropFilter: 'blur(10px)' }}
                    >
                        <span style={{ position: 'relative', display: 'flex', width: '6px', height: '6px' }}>
                            <span style={{ animation: 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite', position: 'absolute', height: '100%', width: '100%', borderRadius: '50%', background: 'var(--accent-blue)', opacity: 0.75 }}></span>
                            <span style={{ position: 'relative', borderRadius: '50%', height: '6px', width: '6px', background: 'var(--accent-blue)' }}></span>
                        </span>
                        BehAnalytics v2.0 is now live
                    </motion.div>

                    <motion.h1
                        className="hero-title"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                    >
                        Predict Dropout.<br />
                        <span className="text-gradient">Protect Futures.</span>
                    </motion.h1>

                    <motion.p
                        style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 3rem auto' }}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                    >
                        An intelligent decision-support engine. Leverage behavioral data and Random Forest predictions to identify high-risk students weeks before they fail.
                    </motion.p>

                    <motion.div
                        style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
                    >
                        <button className="btn-primary" onClick={enterDashboard} style={{ padding: '0.75rem 2rem' }}>
                            Launch Dashboard <ArrowRight size={16} />
                        </button>
                    </motion.div>
                </motion.div>

                {/* Floating Dashboard Preview (Parallax) */}
                <motion.div
                    style={{ y: dashboardY, marginTop: '5rem', width: '100%', maxWidth: '1000px', padding: '0 2rem' }}
                    initial={{ opacity: 0, y: 100 }}
                    animate={{ opacity: 1, y: 20 }}
                    transition={{ duration: 1.2, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
                >
                    <div className="glass-panel" style={{ width: '100%', height: '400px', position: 'relative', overflow: 'hidden' }}>
                        {/* Mock Header */}
                        <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-light)', display: 'flex', gap: '8px' }}>
                            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ff5f56' }} />
                            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ffbd2e' }} />
                            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#27c93f' }} />
                        </div>
                        {/* Mock Content */}
                        <div style={{ display: 'flex', height: 'calc(100% - 49px)' }}>
                            <div style={{ width: '200px', borderRight: '1px solid var(--border-light)', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                <div style={{ height: 20, width: '80%', background: 'rgba(255,255,255,0.05)', borderRadius: 4 }} />
                                <div style={{ height: 20, width: '60%', background: 'rgba(255,255,255,0.05)', borderRadius: 4 }} />
                                <div style={{ height: 20, width: '70%', background: 'rgba(255,255,255,0.05)', borderRadius: 4 }} />
                            </div>
                            <div style={{ flex: 1, padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                                <div style={{ display: 'flex', gap: '1rem' }}>
                                    {[1, 2, 3].map(i => (
                                        <div key={i} style={{ flex: 1, height: 100, background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-light)', borderRadius: 8 }} />
                                    ))}
                                </div>
                                <div style={{ flex: 1, background: 'linear-gradient(180deg, rgba(255,255,255,0.02) 0%, transparent 100%)', border: '1px solid var(--border-light)', borderRadius: 8, borderBottom: 'none' }} />
                            </div>
                        </div>
                        {/* Glow Underlay */}
                        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '60%', height: '60%', background: 'var(--accent-blue)', filter: 'blur(100px)', opacity: 0.1, zIndex: -1 }} />
                    </div>
                </motion.div>
            </section>

            <div className="glowing-divider" />

            {/* 2. WHAT IT SOLVES (Minimal Numbers) */}
            <section className="landing-section">
                <FadeInSection>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '4rem' }}>
                        <div className="tech-badge" style={{ marginBottom: '1rem' }}>The Reality</div>
                        <h2 className="section-title">Reactive <span style={{ color: 'var(--text-muted)' }}>vs</span> Proactive</h2>
                        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', maxWidth: '600px' }}>
                            Waiting for students to fail exams is too late. We process behavioral meta-data to flag risk up to 6 weeks before traditional academic indicators trigger.
                        </p>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem' }}>
                        {[
                            { stat: "30%", title: "Attrition Rate", desc: "First-year students drop out before their sophomore year." },
                            { stat: "Weeks", title: "Lag Time", desc: "Average delay in identifying struggling students conventionally." },
                            { stat: "1:400", title: "Ratio", desc: "Counselor to student ratio limits manual tracking capability." }
                        ].map((item, i) => (
                            <motion.div
                                key={i}
                                style={{ borderLeft: '1px solid var(--border-strong)', paddingLeft: '1.5rem' }}
                                whileHover={{ x: 5 }}
                                transition={{ type: "spring", stiffness: 300, damping: 20 }}
                            >
                                <div style={{ fontSize: '3.5rem', fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '-0.05em', lineHeight: 1 }}>{item.stat}</div>
                                <h3 style={{ fontSize: '1rem', marginTop: '1rem', marginBottom: '0.25rem', color: 'var(--text-primary)' }}>{item.title}</h3>
                                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{item.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </FadeInSection>
            </section>

            <div className="glowing-divider" />

            {/* 3. SYNTHESIS (Features Grid) */}
            <section className="landing-section">
                <FadeInSection>
                    <div style={{ marginBottom: '4rem' }}>
                        <div className="tech-badge" style={{ marginBottom: '1rem' }}>capabilities</div>
                        <h2 className="section-title">Engineered for intervention.</h2>
                    </div>

                    <div className="bento-grid">
                        <div className="bento-card" style={{ gridColumn: '1 / -1' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '600px' }}>
                                <Activity size={24} color="var(--text-primary)" />
                                <h3 style={{ fontSize: '1.5rem' }}>Predictive Burnout Modeling</h3>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
                                    Utilizes a trained Scikit-Learn Random Forest classifier deployed via lightweight CSV payloads to the client. Achieves 94% ROC-AUC without server-side compute overhead.
                                </p>
                            </div>
                            <div style={{ position: 'absolute', right: '2rem', top: '2rem', opacity: 0.1 }}>
                                <BarChart3 size={200} strokeWidth={1} />
                            </div>
                        </div>

                        <div className="bento-card">
                            <LayoutDashboard size={20} color="var(--accent-blue)" style={{ marginBottom: '1.5rem' }} />
                            <h3 style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>Action Queue</h3>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                Prioritized, sortable tabular views instantly bubble the most at-risk students to the top for immediate review.
                            </p>
                        </div>

                        <div className="bento-card">
                            <ShieldCheck size={20} color="var(--accent-purple)" style={{ marginBottom: '1.5rem' }} />
                            <h3 style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>Thresholding</h3>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                Adjustable precision/recall controls allow staff to fine-tune the flag rate based on workforce capacity.
                            </p>
                        </div>

                        <div className="bento-card">
                            <Zap size={20} color="#f5a623" style={{ marginBottom: '1.5rem' }} />
                            <h3 style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>Intervention OS</h3>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                Distribute high-risk student cases across available counselors via automated weekly scheduling.
                            </p>
                        </div>
                    </div>
                </FadeInSection>
            </section>

            <div className="glowing-divider" />

            {/* 4. TECHNICAL PIPELINE */}
            <section className="landing-section">
                <FadeInSection>
                    <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
                        <div className="tech-badge" style={{ marginBottom: '1rem' }}>Stack</div>
                        <h2 className="section-title">Zero-latency architecture.</h2>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'center', gap: '3rem', alignItems: 'center', flexWrap: 'wrap' }}>
                        <div className="architecture-node" style={{ width: '220px' }}>
                            <Database color="var(--text-muted)" size={24} style={{ margin: '0 auto 1rem auto' }} />
                            <h4 style={{ fontSize: '0.875rem', marginBottom: '0.25rem' }}>Static Datasets</h4>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>CSV Artifacts</p>
                        </div>

                        <div style={{ height: '1px', width: '30px', background: 'var(--border-strong)' }} />

                        <div className="architecture-node" style={{ width: '220px' }}>
                            <Server color="var(--text-muted)" size={24} style={{ margin: '0 auto 1rem auto' }} />
                            <h4 style={{ fontSize: '0.875rem', marginBottom: '0.25rem' }}>Model Weights</h4>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>Random Forest Output</p>
                        </div>

                        <div style={{ height: '1px', width: '30px', background: 'var(--border-strong)' }} />

                        <div className="architecture-node" style={{ width: '220px', borderColor: 'var(--border-light)', background: 'rgba(255,255,255,0.03)' }}>
                            <Component color="var(--text-primary)" size={24} style={{ margin: '0 auto 1rem auto' }} />
                            <h4 style={{ fontSize: '0.875rem', marginBottom: '0.25rem', color: 'var(--text-primary)' }}>React Edge</h4>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>Vite + PapaParse</p>
                        </div>
                    </div>
                </FadeInSection>
            </section>

            <div className="glowing-divider" />

            {/* 5. USE CASES */}
            <section className="landing-section" style={{ paddingBottom: '12rem' }}>
                <FadeInSection>
                    <h2 className="section-title">Scale your impact.</h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem', marginTop: '3rem' }}>
                        {[
                            { role: "Academic Advisors", focus: "Micro", desc: "Identify which students to contact today and what cognitive intervention strategies to employ based on behavioural triggers." },
                            { role: "Department Heads", focus: "Meso", desc: "Track high-risk rates across specific semesters and majors to identify systemic curriculum issues using Cohort Insights." },
                            { role: "University Leadership", focus: "Macro", desc: "View high-level funnel aggregations and operational loads to justify and scale strategic counseling budgets." }
                        ].map((uc, i) => (
                            <div key={i} style={{ padding: '2rem 2rem 2rem 0', borderTop: '1px solid var(--border-strong)' }}>
                                <div className="tech-badge" style={{ marginBottom: '1rem', background: 'transparent' }}>{uc.focus}</div>
                                <h3 style={{ fontSize: '1.25rem', marginBottom: '0.75rem', color: 'var(--text-primary)' }}>{uc.role}</h3>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{uc.desc}</p>
                            </div>
                        ))}
                    </div>
                </FadeInSection>
            </section>

            {/* FOOTER */}
            <footer style={{ padding: '2rem', display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-light)', color: 'var(--text-muted)', fontSize: '0.75rem', fontFamily: 'JetBrains Mono, monospace' }}>
                <span>&copy; 2026 Sentinel AI.</span>
                <span>SYSTEM STATUS: NORMAL</span>
            </footer>
        </div>
    );
}
