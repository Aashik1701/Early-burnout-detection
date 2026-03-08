import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { ArrowRight, Brain, Zap, ShieldCheck, Activity, Users, LayoutDashboard, Database, Server, Component, GlassesIcon, Book } from 'lucide-react';

// Reusable animated section wrapper
const FadeInSection = ({ children, delay = 0, className = '' }) => (
    <motion.div
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8, delay, ease: [0.21, 0.47, 0.32, 0.98] }}
        className={className}
    >
        {children}
    </motion.div>
);

export function LandingPage({ enterDashboard }) {
    const { scrollYProgress } = useScroll();
    const heroOpacity = useTransform(scrollYProgress, [0, 0.1], [1, 0]);
    const heroY = useTransform(scrollYProgress, [0, 0.1], [0, 100]);

    return (
        <div className="landing-container">
            {/* Ambient Background Orbs */}
            <div className="ambient-orb orb-1" />
            <div className="ambient-orb orb-2" />
            <div className="ambient-orb orb-3" />

            {/* Sticky Navigation */}
            <nav className="landing-nav">
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Book size={28} color="var(--accent-blue)" />
                    <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em' }}>Sentinal Ai</span>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button
                        onClick={() => window.open('https://sentinel-ai-analytics.streamlit.app/', '_blank')}
                        style={{
                            color: 'var(--text-secondary)',
                            fontWeight: 600,
                            padding: '0.5rem 1rem',
                            borderRadius: 'var(--radius-full)',
                            border: '1px solid var(--border-light)',
                            backdropFilter: 'blur(10px)',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
                        onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
                    >
                        Streamlit
                    </button>
                    <button
                        onClick={enterDashboard}
                        style={{
                            color: 'var(--text-primary)',
                            fontWeight: 600,
                            padding: '0.5rem 1rem',
                            borderRadius: 'var(--radius-full)',
                            border: '1px solid var(--border-light)',
                            backdropFilter: 'blur(10px)',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'; }}
                        onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
                    >
                        Open App
                    </button>
                </div>
            </nav>

            {/* 1. HERO SECTION */}
            <motion.section
                className="landing-section"
                style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', opacity: heroOpacity, y: heroY }}
            >
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                >
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '0.5rem 1rem', borderRadius: 'var(--radius-full)', border: '1px solid var(--accent-purple)', backgroundColor: 'var(--accent-purple-mute)', marginBottom: '2rem', color: 'var(--accent-purple)', fontWeight: 600, fontSize: '0.875rem' }}>
                        <span style={{ position: 'relative', display: 'flex', width: '8px', height: '8px' }}>
                            <span style={{ animation: 'ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite', position: 'absolute', display: 'inline-flex', height: '100%', width: '100%', borderRadius: '50%', backgroundColor: 'var(--accent-purple)', opacity: 0.75 }}></span>
                            <span style={{ position: 'relative', display: 'inline-flex', borderRadius: '50%', height: '8px', width: '8px', backgroundColor: 'var(--accent-purple)' }}></span>
                        </span>
                        Student Burnout Detection v2.0
                    </div>

                    <h1 className="hero-title">
                        Predict Dropout Risk.<br />
                        <span className="text-gradient">Before It Happens.</span>
                    </h1>

                    <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 3rem auto', lineHeight: 1.8 }}>
                        An AI decision-support platform for universities. Leverage behavioral data and Random Forest predictions to drastically increase student retention through targeted human intervention.
                    </p>

                    <button className="btn-primary" onClick={enterDashboard}>
                        Launch Dashboard <ArrowRight size={20} />
                    </button>
                </motion.div>
            </motion.section>

            {/* 2. WHAT IT SOLVES (Problem) */}
            <section className="landing-section" style={{ borderTop: '1px solid var(--border-strong)', background: 'linear-gradient(180deg, rgba(10,12,16,0) 0%, rgba(59,130,246,0.03) 100%)' }}>
                <FadeInSection>
                    <h2 className="section-title">The <span className="text-gradient-accent">Crisis</span></h2>
                    <p style={{ textAlign: 'center', fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '800px', margin: '0 auto 4rem auto' }}>
                        Nearly 30% of first-year college students drop out before their sophomore year. The standard approach of waiting for students to fail exams is reactive and often too late. We need a proactive paradigm.
                    </p>

                    <div className="bento-grid">
                        {[
                            { stat: "30%", title: "First-Year Attrition", desc: "National average dropout rate before sophomore year." },
                            { stat: "Reactive", title: "Current Stigma", desc: "Institutions only act after irreparable academic damage is done." },
                            { stat: "< 5%", title: "Resource Constraint", desc: "Counselors can only engage with a fraction of the student body." }
                        ].map((item, i) => (
                            <motion.div
                                key={i} className="bento-card" style={{ textAlign: 'center' }}
                                whileHover={{ y: -10 }}
                            >
                                <div style={{ fontSize: '3rem', fontWeight: 900, color: 'var(--accent-blue)', marginBottom: '1rem' }}>{item.stat}</div>
                                <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{item.title}</h3>
                                <p style={{ color: 'var(--text-secondary)' }}>{item.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </FadeInSection>
            </section>

            {/* 3. FEATURES & SOLUTIONS */}
            <section className="landing-section">
                <FadeInSection>
                    <h2 className="section-title">A Symphony of <span className="text-gradient">Intelligence</span></h2>
                    <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '4rem', fontSize: '1.25rem' }}>
                        Turn behavioral metadata into actionable counselor interventions.
                    </p>

                    <div className="bento-grid">
                        <div className="bento-card" style={{ gridColumn: '1 / -1', background: 'linear-gradient(135deg, rgba(24,29,38,0.8), rgba(59,130,246,0.1))' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                                <div style={{ flex: 1 }}>
                                    <div className="bento-icon-wrapper"><Activity color="var(--accent-blue)" size={28} /></div>
                                    <h3 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Predictive Burnout Modeling</h3>
                                    <p style={{ color: 'var(--text-secondary)', fontSize: '1.125rem', lineHeight: 1.6 }}>
                                        Our Random Forest classifier analyzes LMS engagement, demographic markers, and academic disengagement indicators to generate a highly calibrated probability score of dropout risk, achieving 94% ROC-AUC.
                                    </p>
                                </div>
                                <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
                                    {/* Mock Diagram */}
                                    <div style={{ width: '100%', maxWidth: '400px', height: '200px', background: 'rgba(0,0,0,0.5)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-strong)', position: 'relative', overflow: 'hidden' }}>
                                        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '60%', background: 'linear-gradient(0deg, var(--accent-blue) 0%, transparent 100%)', opacity: 0.2 }} />
                                        <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: '100%', height: '100%', position: 'absolute' }}>
                                            <path d="M0,80 Q25,20 50,60 T100,20 L100,100 L0,100 Z" fill="rgba(59,130,246,0.2)" stroke="var(--accent-blue)" strokeWidth="2" />
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bento-card">
                            <div className="bento-icon-wrapper"><LayoutDashboard color="var(--accent-purple)" size={28} /></div>
                            <h3>Action Queue Tracking</h3>
                            <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                                A prioritized, sortable tabular interface that instantly bubbles the most at-risk students to the top for immediate review.
                            </p>
                        </div>

                        <div className="bento-card">
                            <div className="bento-icon-wrapper"><ShieldCheck color="var(--accent-teal)" size={28} /></div>
                            <h3>Automated Thresholding</h3>
                            <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                                Adjustable precision/recall evaluation modes allow administrative staff to fine-tune the flag rate based on current workforce capacity.
                            </p>
                        </div>

                        <div className="bento-card">
                            <div className="bento-icon-wrapper"><Zap color="#f59e0b" size={28} /></div>
                            <h3>Intervention Planner</h3>
                            <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                                Automatically distribute highest-risk student cases across available counselors in weekly scheduling slots.
                            </p>
                        </div>
                    </div>
                </FadeInSection>
            </section>

            {/* 4. TECHNICAL ARCHITECTURE & PIPELINE */}
            <section className="landing-section" style={{ position: 'relative' }}>
                <div style={{ position: 'absolute', top: 0, left: '50%', width: '100vw', transform: 'translateX(-50%)', height: '1px', background: 'linear-gradient(90deg, transparent, var(--border-strong), transparent)' }} />
                <FadeInSection>
                    <h2 className="section-title">Technical <span className="text-gradient">Architecture</span></h2>
                    <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '4rem' }}>
                        A meticulously engineered pipeline from raw data to proactive intervention.
                    </p>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem', maxWidth: '900px', margin: '0 auto' }}>

                        <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', alignItems: 'center' }}>
                            <div className="architecture-node" style={{ width: '200px' }}>
                                <Database color="var(--text-muted)" size={32} style={{ margin: '0 auto 1rem auto' }} />
                                <h4>LMS Datasets</h4>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>student_dropout_v3.csv</p>
                            </div>

                            <div style={{ height: '2px', width: '50px', background: 'var(--border-strong)' }} />

                            <div className="architecture-node" style={{ width: '200px', borderColor: 'var(--accent-purple)', boxShadow: '0 0 20px rgba(139,92,246,0.2)' }}>
                                <Server color="var(--accent-purple)" size={32} style={{ margin: '0 auto 1rem auto' }} />
                                <h4>Python Backend</h4>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Scikit-Learn Random Forest</p>
                            </div>

                            <div style={{ height: '2px', width: '50px', background: 'var(--border-strong)' }} />

                            <div className="architecture-node" style={{ width: '200px', borderColor: 'var(--accent-blue)', boxShadow: '0 0 20px rgba(59,130,246,0.2)' }}>
                                <Component color="var(--accent-blue)" size={32} style={{ margin: '0 auto 1rem auto' }} />
                                <h4>React Frontend</h4>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Vite + Framer Motion</p>
                            </div>
                        </div>

                        {/* Pipeline Flow */}
                        <div style={{ background: 'rgba(24,29,38,0.5)', borderRadius: 'var(--radius-lg)', padding: '3rem', border: '1px solid var(--border-light)' }}>
                            <h3 style={{ marginBottom: '2rem', textAlign: 'center' }}>Inference Pipeline</h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', position: 'relative' }}>
                                <div style={{ position: 'absolute', top: '10px', bottom: '10px', left: '24px', width: '2px', background: 'var(--border-strong)' }} />

                                {[
                                    { title: '1. Data Ingestion', desc: 'Client-side ingestion of static CSV artifacts using PapaParse.' },
                                    { title: '2. Probability Mapping', desc: 'Merging real-time cohort metadata with pre-computed calibration scores.' },
                                    { title: '3. Threshold Evaluation', desc: 'Applying operating thresholds (e.g. 0.52) to flag High-Risk students.' },
                                    { title: '4. Action Generation', desc: 'Rendering tailored UI cards and automated counseling schedules.' }
                                ].map((step, i) => (
                                    <motion.div
                                        key={i}
                                        initial={{ opacity: 0, x: -20 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        viewport={{ once: true }}
                                        transition={{ delay: i * 0.2 }}
                                        style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start', position: 'relative', zIndex: 2 }}
                                    >
                                        <div style={{ width: '50px', height: '50px', borderRadius: '50%', background: 'var(--bg-card)', border: '2px solid var(--accent-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>{i + 1}</div>
                                        <div style={{ paddingTop: '10px' }}>
                                            <h4 style={{ fontSize: '1.125rem', marginBottom: '0.25rem' }}>{step.title}</h4>
                                            <p style={{ color: 'var(--text-secondary)' }}>{step.desc}</p>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                    </div>
                </FadeInSection>
            </section>


            {/* 5. USE CASES */}
            <section className="landing-section" style={{ paddingBottom: '12rem' }}>
                <FadeInSection>
                    <h2 className="section-title">Designed for <span className="text-gradient">Impact</span></h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem', marginTop: '4rem' }}>
                        {[
                            { role: "Academic Advisors", focus: "Micro", desc: "Instantly know which students to contact today and what intervention strategies to employ based on specific behavioural triggers." },
                            { role: "Department Heads", focus: "Meso", desc: "Track high-risk rates across specific semesters and majors to identify systemic curriculum issues using Cohort Insights." },
                            { role: "University Leadership", focus: "Macro", desc: "View high-level funnel aggregations and false-positive loads to justify and scale counseling resource budgets." }
                        ].map((uc, i) => (
                            <div key={i} style={{ padding: '2rem', borderTop: '2px solid var(--accent-blue)', background: 'rgba(255,255,255,0.02)' }}>
                                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--accent-blue)', marginBottom: '1rem' }}>{uc.focus} Scale</div>
                                <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>{uc.role}</h3>
                                <p style={{ color: 'var(--text-secondary)' }}>{uc.desc}</p>
                            </div>
                        ))}
                    </div>
                </FadeInSection>
            </section>

            {/* FOOTER */}
            <footer style={{ padding: '2rem', textAlign: 'center', borderTop: '1px solid var(--border-strong)', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                &copy; 2026 BehAnalytics. Developed for the Early Burnout Detection Initiative.
            </footer>
        </div>
    );
}
