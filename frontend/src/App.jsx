import { useState, useMemo, useEffect } from 'react';
import { useDashboardData } from './hooks/useDashboardData';
import { Sidebar } from './components/layout/Sidebar';
import { TopBar } from './components/layout/TopBar';
import { Overview, ActionQueue, StudentDetail, InterventionPlanner, ProgramImpact, CohortInsights } from './pages';
import { LandingPage } from './pages/LandingPage';
import { Loader2 } from 'lucide-react';

function App() {
  const { data, metrics, loading, error } = useDashboardData();
  const [isDashboard, setIsDashboard] = useState(false);
  const [currentTab, setCurrentTab] = useState('overview');
  const [filters, setFilters] = useState({
    mode: 'balanced',
    search: '',
  });

  useEffect(() => {
    const handlePopState = () => {
      setIsDashboard(window.location.pathname === '/dashboard');
    };
    window.addEventListener('popstate', handlePopState);
    handlePopState();
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const enterDashboard = () => {
    window.history.pushState({}, '', '/dashboard');
    setIsDashboard(true);
    window.scrollTo(0, 0);
  };

  const availableModes = Object.keys(metrics?.mode_metrics || { balanced: true });

  const filteredData = useMemo(() => {
    if (!data) return [];
    let _data = data;
    if (filters.search) {
      const q = filters.search.trim().toLowerCase();
      _data = _data.filter(d => String(d.Student_ID).toLowerCase().includes(q));
    }
    return _data;
  }, [data, filters.search]);

  if (isDashboard && error) {
    return (
      <div className="app-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: 'var(--risk-high)' }}>Error loading data: {error}</div>
      </div>
    );
  }

  if (isDashboard && (loading || !data.length)) {
    return (
      <div className="app-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <Loader2 className="animate-spin" size={48} color="var(--accent-blue)" />
      </div>
    );
  }

  if (!isDashboard) {
    return <LandingPage enterDashboard={enterDashboard} />;
  }

  return (
    <div className="app-container">
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        filters={filters}
        setFilters={setFilters}
        availableModes={availableModes}
      />
      <main className="main-content">
        <TopBar />
        <div className="page-content">
          {currentTab === 'overview' && <Overview data={filteredData} metrics={metrics} filters={filters} />}
          {currentTab === 'queue' && <ActionQueue data={filteredData} filters={filters} />}
          {currentTab === 'detail' && <StudentDetail data={filteredData} />}
          {currentTab === 'planner' && <InterventionPlanner data={filteredData} />}
          {currentTab === 'impact' && <ProgramImpact data={filteredData} metrics={metrics} filters={filters} />}
          {currentTab === 'cohort' && <CohortInsights data={filteredData} filters={filters} />}
        </div>
      </main>
    </div>
  );
}

export default App;
