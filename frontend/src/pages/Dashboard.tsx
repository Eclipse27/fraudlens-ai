import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/layout';
import { Card, Button, RiskBadge } from '../components/ui';
import { getHistory, type HistoryRecord } from '../services/history';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Activity, FileSearch, Building2, BrainCircuit } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const [history, setHistory] = useState<HistoryRecord[]>([]);

  useEffect(() => {
    setHistory(getHistory());
  }, []);

  const highRiskCount = history.filter(h => h.riskLevel === 'HIGH').length;
  // A record is suspicious pattern if its type is Anomaly and status is SUSPICIOUS PATTERN or MODERATE ANOMALY (or just SUSPICIOUS PATTERN). 
  // Wait, if I changed the possible labels to "SUSPICIOUS PATTERN", "MODERATE ANOMALY", "NORMAL PATTERN", I'll count SUSPICIOUS PATTERN.
  const suspiciousCount = history.filter(h => h.status === 'SUSPICIOUS PATTERN' && h.type === 'Anomaly').length;

  const riskData = [
    { name: 'Low Risk', value: history.filter(h => h.riskLevel === 'LOW').length, color: 'var(--color-risk-low)' },
    { name: 'Medium Risk', value: history.filter(h => h.riskLevel === 'MEDIUM').length, color: 'var(--color-risk-medium)' },
    { name: 'High Risk', value: highRiskCount, color: 'var(--color-risk-high)' },
    { name: 'Suspicious Anomaly', value: suspiciousCount, color: 'var(--color-risk-suspicious)' },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Good evening, Investigator" 
        subtitle="Monitor fraud risks, suspicious claims, and investigation intelligence."
      />

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <p className="text-sm font-medium text-secondary mb-1">Analyses Run</p>
          <p className="text-3xl font-bold tabular-nums text-primary">{history.length}</p>
        </Card>
        <Card className="p-6">
          <p className="text-sm font-medium text-secondary mb-1">High Risk Cases</p>
          <p className="text-3xl font-bold tabular-nums text-risk-high">{highRiskCount}</p>
        </Card>
        <Card className="p-6">
          <p className="text-sm font-medium text-secondary mb-1">Suspicious Patterns</p>
          <p className="text-3xl font-bold tabular-nums text-risk-suspicious">{suspiciousCount}</p>
        </Card>
        <Card className="p-6">
          <p className="text-sm font-medium text-secondary mb-1">Models Active</p>
          <p className="text-3xl font-bold tabular-nums text-primary flex items-center">
            3 <span className="ml-2 w-2 h-2 rounded-full bg-risk-low animate-pulse" />
          </p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-primary">Quick Actions</h3>
          <Card className="p-4 flex items-center space-x-4 hover:-translate-y-0.5 hover:shadow-md transition-all cursor-pointer" onClick={() => navigate('/claim-analysis')}>
            <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
              <FileSearch className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="font-semibold text-primary">Analyze New Claim</p>
              <p className="text-xs text-secondary">Check a single claim against the XGBoost model.</p>
            </div>
          </Card>
          <Card className="p-4 flex items-center space-x-4 hover:-translate-y-0.5 hover:shadow-md transition-all cursor-pointer" onClick={() => navigate('/provider-analysis')}>
            <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
              <Building2 className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="font-semibold text-primary">Analyze Provider</p>
              <p className="text-xs text-secondary">Review aggregate provider risk factors.</p>
            </div>
          </Card>
          <Card className="p-4 flex items-center space-x-4 hover:-translate-y-0.5 hover:shadow-md transition-all cursor-pointer" onClick={() => navigate('/anomaly-detection')}>
            <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
              <Activity className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="font-semibold text-primary">Check CMS Pattern</p>
              <p className="text-xs text-secondary">Unsupervised anomaly detection on utilization.</p>
            </div>
          </Card>

          <Card className="p-4 mt-6 border-l-4 border-l-ai bg-ai/5">
            <div className="flex items-center space-x-2 mb-2">
              <BrainCircuit className="w-5 h-5 text-ai" />
              <h4 className="font-semibold text-ai">AI Investigation Insights</h4>
            </div>
            <p className="text-sm text-secondary leading-relaxed">
              Based on recent trends, specialist office procedures and high provider-patient distances are strongly correlating with elevated risk. Consider prioritizing manual review for these combinations.
            </p>
          </Card>
        </div>

        {/* Center: Chart */}
        <Card className="p-6 flex flex-col">
          <h3 className="text-lg font-semibold text-primary mb-4">Risk Distribution</h3>
          {riskData.length > 0 ? (
            <div className="flex-1 min-h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={riskData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center space-x-4 mt-4">
                {riskData.map(d => (
                  <div key={d.name} className="flex items-center text-xs text-secondary">
                    <span className="w-3 h-3 rounded-full mr-1.5" style={{ backgroundColor: d.color }} />
                    {d.name} ({d.value})
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-secondary text-sm">
              No data yet. Run an analysis.
            </div>
          )}
        </Card>

        {/* Right: Recent History */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-primary">Recent Activity</h3>
            <Button variant="outline" className="text-xs px-2 py-1 h-auto" onClick={() => navigate('/history')}>View All</Button>
          </div>
          <div className="space-y-4">
            {history.length > 0 ? history.slice(0, 5).map(item => (
              <div key={item.id} className="flex items-start justify-between border-b border-border pb-3 last:border-0 last:pb-0">
                <div>
                  <p className="text-sm font-medium text-primary">{item.type} Analysis</p>
                  <p className="text-xs text-secondary">{new Date(item.timestamp).toLocaleString()}</p>
                </div>
                <RiskBadge level={item.type === 'Anomaly' ? item.status : item.riskLevel} />
              </div>
            )) : (
              <p className="text-sm text-secondary text-center py-8">No investigations recorded yet.</p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
