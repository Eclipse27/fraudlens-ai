import { useState } from 'react';
import { PageHeader } from '../components/layout';
import { Card, Button, Input, RiskScoreGauge, RiskBadge } from '../components/ui';
import { LoadingState, ErrorState } from '../components/feedback';
import { analyzeProvider } from '../services/api';
import { saveHistory } from '../services/history';
import { ShieldCheck, ShieldAlert } from 'lucide-react';

export default function ProviderAnalysis() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData(e.currentTarget);
    const data: Record<string, any> = {};
    formData.forEach((value, key) => {
      data[key] = Number(value);
    });

    try {
      const res = await analyzeProvider(data);
      setResult(res);
      await saveHistory({
        id: res.provider_id,
        type: 'Provider',
        timestamp: new Date().toISOString(),
        riskScore: res.fraud_risk_score,
        riskLevel: res.risk_level,
        status: res.risk_level,
        result: res
      });
    } catch (err: any) {
      console.error("API Error:", err);
      setError(err.response?.data?.detail || err.message || "Unable to connect to the AI analysis service. Please check that the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Provider Analysis" 
        subtitle="Review aggregate provider risk factors based on historical claims data."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <p className="text-sm text-secondary mb-4 bg-surface-alt p-3 rounded-lg border border-border">
              Enter aggregate metrics for the provider to calculate an overall risk profile.
            </p>
            
            <div>
              <h3 className="text-sm font-semibold text-primary uppercase tracking-wide border-b border-border pb-2 mb-4">Volume & Beneficiaries</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input name="num_unique_beneficiaries" label="Unique Beneficiaries" type="number" required defaultValue={150} />
                <Input name="total_claims" label="Total Claims" type="number" required defaultValue={400} />
                <Input name="total_inpatient_claims" label="Total Inpatient Claims" type="number" required defaultValue={50} />
                <Input name="total_outpatient_claims" label="Total Outpatient Claims" type="number" required defaultValue={350} />
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-primary uppercase tracking-wide border-b border-border pb-2 mb-4">Financial Aggregates</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input name="insc_claim_amt_reimbursed_sum" label="Total Reimbursed ($)" type="number" step="0.01" required defaultValue={50000} />
                <Input name="insc_claim_amt_reimbursed_mean" label="Mean Reimbursed ($)" type="number" step="0.01" required defaultValue={125} />
                <Input name="deductible_amt_paid_sum" label="Total Deductibles ($)" type="number" step="0.01" required defaultValue={5000} />
                <Input name="deductible_amt_paid_max" label="Max Deductible ($)" type="number" step="0.01" required defaultValue={1068} />
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-primary uppercase tracking-wide border-b border-border pb-2 mb-4">Patient Demographics (Averages)</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input name="age_mean" label="Mean Patient Age" type="number" step="0.1" required defaultValue={65.5} />
                <Input name="num_procedures_mean" label="Mean Procedures per Claim" type="number" step="0.1" required defaultValue={1.5} />
                <Input name="claim_duration_mean" label="Mean Claim Duration (Days)" type="number" step="0.1" required defaultValue={2.5} />
                <Input name="num_diagnosis_mean" label="Mean Diagnoses per Claim" type="number" step="0.1" required defaultValue={3.2} />
              </div>
            </div>

            <Button type="submit" className="w-full" isLoading={loading}>Analyze Provider</Button>
          </form>
        </Card>

        <div>
          {loading && <Card><LoadingState message="Calculating provider risk profile..." /></Card>}
          {error && <Card><ErrorState message={error} onRetry={() => setError(null)} /></Card>}
          
          {!loading && !error && result && (
            <Card className="p-6">
              <div className="flex flex-col items-center justify-center border-b border-border pb-6 mb-6">
                <RiskScoreGauge score={result.fraud_risk_score} />
                <RiskBadge level={result.risk_level} className="mt-4" />
                <p className="text-lg font-semibold text-primary mt-2">
                  {result.risk_level === 'HIGH' ? 'ELEVATED RISK - REVIEW REQUIRED' : 'NORMAL RISK PROFILE'}
                </p>
                <p className="text-xs text-secondary mt-1">Provider Ref: {result.provider_id}</p>
              </div>

              <div className="mb-6">
                <h4 className="text-sm font-semibold text-primary uppercase tracking-wide mb-3">Top Risk Indicators</h4>
                {result.top_factors && result.top_factors.length > 0 ? (
                  <div className="space-y-3">
                    {result.top_factors.map((rf: any, idx: number) => (
                      <div key={idx} className="p-3 bg-risk-high-bg/30 rounded-lg border border-red-100 flex items-start space-x-3">
                        <ShieldAlert className="w-5 h-5 text-risk-high shrink-0 mt-0.5" />
                        <div>
                          <span className="font-semibold text-sm text-primary">{rf.factor}</span>
                          <p className="text-xs text-secondary">{rf.explanation}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 bg-risk-low-bg/50 rounded-lg border border-green-100 flex items-center space-x-3">
                    <ShieldCheck className="w-5 h-5 text-risk-low shrink-0" />
                    <p className="text-sm text-secondary">No strong positive risk indicators detected in the provider's aggregate data.</p>
                  </div>
                )}
              </div>

              <div className="mt-6 p-4 bg-surface-alt rounded-lg border border-border">
                <p className="text-xs text-secondary text-center">
                  <strong>Disclaimer:</strong> Provider risk analysis is based on aggregated claim behaviour and historical patterns. High risk scores require manual review and do not definitively confirm fraudulent provider activity.
                </p>
              </div>
            </Card>
          )}

          {!loading && !error && !result && (
            <Card className="p-12 flex flex-col items-center justify-center text-center h-[500px] border-dashed">
              <p className="text-secondary">Enter provider aggregates and run the analysis to view the risk report.</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
