import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { predictions, reports, health } from '../services/api';
import type { SuccessPrediction, GrowthPrediction, RiskPrediction } from '../types';

function Dashboard() {
  const navigate = useNavigate();
  const [successProb, setSuccessProb] = useState<SuccessPrediction | null>(null);
  const [growth, setGrowth] = useState<GrowthPrediction | null>(null);
  const [risk, setRisk] = useState<RiskPrediction | null>(null);
  const [reportUrl, setReportUrl] = useState('');
  const [serverStatus, setServerStatus] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    health()
      .then((res) => setServerStatus(res.data.status))
      .catch(() => setServerStatus('unreachable'));
  }, []);

  const handlePredict = async () => {
    setLoading(true);
    try {
      const [s, g, r] = await Promise.all([
        predictions.success({
          industry: 'Tech', revenue: 5000000, employees: 100,
          founder_experience: 10, funding_raised: 10000000,
          market_size: 500000000, customer_growth: 0.3,
        }),
        predictions.growth({
          revenue: 5000000, employees: 100, funding_raised: 10000000,
          market_size: 500000000, growth_rate: 0.3,
        }),
        predictions.risk({
          industry: 'Tech', revenue: 5000000, employees: 100,
          founder_experience: 10, funding_raised: 10000000,
          market_size: 500000000, growth_rate: 0.3, burn_rate: 200000,
        }),
      ]);
      setSuccessProb(s.data);
      setGrowth(g.data);
      setRisk(r.data);
    } catch {
      // handled by interceptor
    } finally {
      setLoading(false);
    }
  };

  const handleReport = async () => {
    try {
      const res = await reports.generate(1);
      setReportUrl(res.data.pdf_url);
    } catch {
      // handled by interceptor
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-semibold text-gray-900">Startup Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              Server: <span className={`font-medium ${serverStatus === 'ok' ? 'text-green-600' : 'text-red-600'}`}>
                {serverStatus || 'checking...'}
              </span>
            </span>
            <button onClick={handleLogout} className="text-sm text-red-600 hover:underline">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-sm font-medium text-gray-500">Success Probability</h3>
            <p className="text-3xl font-bold mt-2">
              {successProb ? `${successProb.success_probability.toFixed(1)}%` : '--'}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-sm font-medium text-gray-500">Risk Score</h3>
            <p className="text-3xl font-bold mt-2">
              {risk ? `${risk.risk_score.toFixed(1)}` : '--'}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-sm font-medium text-gray-500">1Y Growth</h3>
            <p className="text-3xl font-bold mt-2">
              {growth ? `$${(growth.growth_1y / 1000).toFixed(0)}K` : '--'}
            </p>
          </div>
        </div>

        {risk && (
          <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
            <h3 className="text-sm font-medium text-gray-500 mb-4">Risk Breakdown</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {(['financial_risk', 'operational_risk', 'market_risk', 'team_risk'] as const).map((key) => (
                <div key={key} className="text-center">
                  <div className="text-lg font-bold">{risk[key].toFixed(0)}</div>
                  <div className="text-xs text-gray-500 capitalize">{key.replace('_', ' ')}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-4 mb-8">
          <button
            onClick={handlePredict}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Run Predictions'}
          </button>
          <button
            onClick={handleReport}
            className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700"
          >
            Generate Report
          </button>
        </div>

        {reportUrl && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Report Generated</h3>
            <a
              href={`/api${reportUrl}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Download PDF Report
            </a>
          </div>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
