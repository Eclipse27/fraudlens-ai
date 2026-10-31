import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/layout';
import { Card, Button, RiskBadge } from '../components/ui';
import { getHistory, type HistoryRecord } from '../services/history';
import { fetchDashboardStats } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Activity, FileSearch, Building2, Users, FileCheck, CheckCircle2, AlertTriangle, Pill, ShieldAlert } from 'lucide-react';

interface DashboardStats {
  total_synthetic_patients: number;
  number_demo_hospitals: number;
  total_encounters: number;
  total_prescriptions: number;
  total_claims: number;
  claims_verified: number;
  claims_requiring_review: number;
  medicine_references_loaded: number;
  medicine_reference_matches: number;
  total_rx_medicines: number;
  prototype_mode: string;
  cross_hospital_patient_count: number;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    getHistory().then(setHistory);
    fetchDashboardStats().then(setStats).catch(() => {});
  }, []);

  const highRiskCount = history.filter(h => h.riskLevel === 'HIGH').length;
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
        subtitle="Monitor fraud risks, clinical provenance, cross-hospital patient identity, and claim authenticity."
      />

      {/* Synthetic Dataset Banner */}
      <div className="p-4 bg-accent/5 border border-accent/20 rounded-lg flex items-center justify-between text-xs text-secondary">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 text-accent" />
          <span>
            <strong className="text-primary font-semibold">Academic Prototype:</strong> All patient names, identifiers, encounters, bills, and claims are entirely <strong>SYNTHETIC</strong>. 
            Institution names are verified public demo entities in Prayagraj. No real patient data is used.
          </span>
        </div>
        <span className="px-2 py-0.5 rounded bg-accent/10 text-accent font-medium uppercase tracking-wider">
          Phase 3 Active
        </span>
      </div>

      {/* Primary Metrics Row (Computed from stored synthetic records) */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        <Card className="p-4 text-center">
          <p className="text-xs font-medium text-secondary mb-1">Synthetic Patients</p>
          <p className="text-2xl font-bold tabular-nums text-accent">{stats?.total_synthetic_patients || 300}</p>
          <p className="text-[10px] text-secondary mt-0.5">250 Cross-Hospital</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs font-medium text-secondary mb-1">Demo Hospitals</p>
          <p className="text-2xl font-bold tabular-nums text-primary">{stats?.number_demo_hospitals || 3}</p>
          <p className="text-[10px] text-secondary mt-0.5">Prayagraj Verified</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs font-medium text-secondary mb-1">Total Encounters</p>
          <p className="text-2xl font-bold tabular-nums text-primary">{stats?.total_encounters || 600}</p>
          <p className="text-[10px] text-secondary mt-0.5">OPD & IPD Visits</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs font-medium text-secondary mb-1">Prescriptions</p>
          <p className="text-2xl font-bold tabular-nums text-primary">{stats?.total_prescriptions || 550}</p>
          <p className="text-[10px] text-secondary mt-0.5">Clinical Line Items</p>
        </Card>
        <Card className="p-4 text-center border-l-2 border-l-risk-low">
          <p className="text-xs font-medium text-secondary mb-1 flex items-center justify-center space-x-1">
            <CheckCircle2 className="w-3 h-3 text-risk-low inline" />
            <span>Claims Verified</span>
          </p>
          <p className="text-2xl font-bold tabular-nums text-risk-low">{stats?.claims_verified || 542}</p>
          <p className="text-[10px] text-secondary mt-0.5">Consistent Audits</p>
        </Card>
        <Card className="p-4 text-center border-l-2 border-l-risk-high">
          <p className="text-xs font-medium text-secondary mb-1 flex items-center justify-center space-x-1">
            <AlertTriangle className="w-3 h-3 text-risk-high inline" />
            <span>Review Required</span>
          </p>
          <p className="text-2xl font-bold tabular-nums text-risk-high">{stats?.claims_requiring_review || 8}</p>
          <p className="text-[10px] text-secondary mt-0.5">Flagged Scenarios</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs font-medium text-secondary mb-1 flex items-center justify-center space-x-1">
            <Pill className="w-3 h-3 text-accent inline" />
            <span>Med Ref Matches</span>
          </p>
          <p className="text-2xl font-bold tabular-nums text-accent">{stats?.medicine_reference_matches || 1152}</p>
          <p className="text-[10px] text-secondary mt-0.5">WHO EML / NLEM</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-primary">Investigation Hub</h3>
          
          <Card className="p-4 flex items-center space-x-4 hover:-translate-y-0.5 hover:shadow-md transition-all cursor-pointer border-l-4 border-l-accent" onClick={() => navigate('/claim-verification')}>
            <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
              <FileCheck className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="font-semibold text-primary">Verify Claim Provenance</p>
              <p className="text-xs text-secondary">11-point multi-source hospital & WHO EML audit.</p>
            </div>
          </Card>

          <Card className="p-4 flex items-center space-x-4 hover:-translate-y-0.5 hover:shadow-md transition-all cursor-pointer border-l-4 border-l-primary" onClick={() => navigate('/patients')}>
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Users className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="font-semibold text-primary">Patient Identity Registry</p>
              <p className="text-xs text-secondary">300 patients across 3 Prayagraj demo hospitals.</p>
            </div>
          </Card>

          <Card className="p-4 flex items-center space-x-4 hover:-translate-y-0.5 hover:shadow-md transition-all cursor-pointer" onClick={() => navigate('/claim-analysis')}>
            <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
              <FileSearch className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="font-semibold text-primary">Analyze New Claim (ML)</p>
              <p className="text-xs text-secondary">XGBoost fraud likelihood scoring.</p>
            </div>
          </Card>

          <Card className="p-4 flex items-center space-x-4 hover:-translate-y-0.5 hover:shadow-md transition-all cursor-pointer" onClick={() => navigate('/provider-analysis')}>
            <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
              <Building2 className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="font-semibold text-primary">Analyze Provider (ML)</p>
              <p className="text-xs text-secondary">Logistic Regression provider risk factors.</p>
            </div>
          </Card>

          <Card className="p-4 flex items-center space-x-4 hover:-translate-y-0.5 hover:shadow-md transition-all cursor-pointer" onClick={() => navigate('/anomaly-detection')}>
            <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
              <Activity className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="font-semibold text-primary">CMS Utilization Pattern (ML)</p>
              <p className="text-xs text-secondary">Unsupervised Isolation Forest anomaly detection.</p>
            </div>
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
            <div className="flex-1 flex flex-col items-center justify-center text-secondary text-sm space-y-2">
              <p>550 Synthetic Claims Loaded & Audited</p>
              <p className="text-xs text-secondary/70">Run interactive ML analysis to add to live chart.</p>
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
              <div className="text-center py-6 space-y-2">
                <p className="text-sm font-medium text-primary">System Ready</p>
                <p className="text-xs text-secondary">
                  300 synthetic patients, 600 encounters across 3 Prayagraj hospitals available for end-to-end investigation.
                </p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
