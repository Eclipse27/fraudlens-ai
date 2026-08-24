import { useState } from 'react';
import { PageHeader } from '../components/layout';
import { Card, Button, Input, Select, RiskScoreGauge, RiskBadge, cn } from '../components/ui';
import { LoadingState, ErrorState } from '../components/feedback';
import { analyzeClaim } from '../services/api';
import { saveHistory } from '../services/history';

export default function ClaimAnalysis() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData(e.currentTarget);
    const data = {
      claim_amount: Number(formData.get('claim_amount')),
      patient_age: Number(formData.get('patient_age')),
      number_of_procedures: Number(formData.get('number_of_procedures')),
      length_of_stay_days: Number(formData.get('length_of_stay_days')),
      deductible_amount: Number(formData.get('deductible_amount')),
      copay_amount: Number(formData.get('copay_amount')),
      number_of_previous_claims_patient: Number(formData.get('number_of_previous_claims_patient')),
      number_of_previous_claims_provider: Number(formData.get('number_of_previous_claims_provider')),
      provider_patient_distance_miles: Number(formData.get('provider_patient_distance_miles')),
      claim_submitted_late: Number(formData.get('claim_submitted_late')),
      service_to_claim_days: Number(formData.get('service_to_claim_days')),
      policy_days_left: Number(formData.get('policy_days_left')),
      patient_gender: formData.get('patient_gender'),
      provider_type: formData.get('provider_type'),
      provider_specialty: formData.get('provider_specialty'),
      admission_type: formData.get('admission_type'),
      discharge_type: formData.get('discharge_type'),
      service_type: formData.get('service_type'),
    };

    try {
      const res = await analyzeClaim(data);
      setResult(res);
      saveHistory({
        id: res.claim_id,
        type: 'Claim',
        timestamp: new Date().toISOString(),
        riskScore: res.fraud_risk_score,
        riskLevel: res.risk_level,
        status: res.risk_level,
        result: res
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Unable to connect to the AI analysis service. Please check that the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Claim Analysis" 
        subtitle="Evaluate individual health insurance claims for fraud risk using Regularized XGBoost."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h3 className="text-sm font-semibold text-primary uppercase tracking-wide border-b border-border pb-2 mb-4">Claim Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input name="claim_amount" label="Claim Amount ($)" type="number" step="0.01" required defaultValue={1500} />
                <Input name="number_of_procedures" label="Number of Procedures" type="number" required defaultValue={2} />
                <Input name="length_of_stay_days" label="Length of Stay (Days)" type="number" required defaultValue={0} />
                <Input name="deductible_amount" label="Deductible ($)" type="number" step="0.01" required defaultValue={0} />
                <Input name="copay_amount" label="Copay ($)" type="number" step="0.01" required defaultValue={20} />
                <Select name="service_type" label="Service Type" options={['Inpatient', 'Outpatient', 'Emergency Room', 'Laboratory', 'Pharmacy']} defaultValue="Outpatient" />
                <Select name="admission_type" label="Admission Type" options={['Elective', 'Emergency', 'Newborn', 'Trauma', 'Urgent']} defaultValue="Elective" />
                <Select name="discharge_type" label="Discharge Type" options={['Home', 'Deceased', 'Rehab/Skilled Nursing', 'Transfer to another facility']} defaultValue="Home" />
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-primary uppercase tracking-wide border-b border-border pb-2 mb-4">Provider Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select name="provider_type" label="Provider Type" options={['Hospital', 'Laboratory', 'Pharmacy', 'Specialist Office', 'Urgent Care']} defaultValue="Specialist Office" />
                <Select name="provider_specialty" label="Provider Specialty" options={['General Practice', 'Cardiology', 'Dermatology', 'Neurology', 'Oncology', 'Orthopedics', 'Pediatrics', 'Physical Therapy', 'Psychiatry', 'Radiology']} defaultValue="General Practice" />
                <Input name="provider_patient_distance_miles" label="Patient-Provider Distance (Miles)" type="number" step="0.1" required defaultValue={15.5} />
                <Input name="number_of_previous_claims_provider" label="Provider Prev. Claims" type="number" required defaultValue={150} />
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-primary uppercase tracking-wide border-b border-border pb-2 mb-4">Patient & Policy</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input name="patient_age" label="Patient Age" type="number" required defaultValue={45} />
                <Select name="patient_gender" label="Patient Gender" options={['Male', 'Female', 'Other']} defaultValue="Female" />
                <Input name="number_of_previous_claims_patient" label="Patient Prev. Claims" type="number" required defaultValue={3} />
                <Input name="policy_days_left" label="Policy Days Left" type="number" required defaultValue={200} />
                <Input name="claim_submitted_late" label="Submitted Late (0 or 1)" type="number" min="0" max="1" required defaultValue={0} />
                <Input name="service_to_claim_days" label="Service to Claim Days" type="number" required defaultValue={5} />
              </div>
            </div>

            <Button type="submit" className="w-full" isLoading={loading}>Analyze Claim</Button>
          </form>
        </Card>

        <div>
          {loading && <Card><LoadingState message="AI is analyzing claim risk..." /></Card>}
          {error && <Card><ErrorState message={error} onRetry={() => setError(null)} /></Card>}
          
          {!loading && !error && result && (
            <Card className="p-6">
              <div className="flex flex-col items-center justify-center border-b border-border pb-6 mb-6">
                <RiskScoreGauge score={result.fraud_risk_score} />
                <RiskBadge level={result.risk_level} className="mt-4" />
                <p className="text-lg font-semibold text-primary mt-2">{result.prediction}</p>
                <p className="text-xs text-secondary mt-1">ID: {result.claim_id}</p>
              </div>

              <div className="mb-6">
                <h4 className="text-sm font-semibold text-primary uppercase tracking-wide mb-3">AI Risk Factors</h4>
                <div className="space-y-3">
                  {result.risk_factors.map((rf: any, idx: number) => (
                    <div key={idx} className="p-3 bg-surface-alt rounded-lg border border-border">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className={cn('text-[10px] font-bold px-2 py-0.5 rounded', rf.impact === 'HIGH' ? 'bg-risk-high-bg text-risk-high' : 'bg-risk-medium-bg text-risk-medium')}>{rf.impact}</span>
                        <span className="font-semibold text-sm text-primary">{rf.factor}</span>
                      </div>
                      <p className="text-xs text-secondary">{rf.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mb-6">
                <h4 className="text-sm font-semibold text-primary uppercase tracking-wide mb-3">Recommendations</h4>
                <ul className="space-y-2">
                  {result.recommendation.map((r: string, idx: number) => (
                    <li key={idx} className="text-sm text-secondary flex items-start">
                      <span className="mr-2 text-accent">•</span> {r}
                    </li>
                  ))}
                </ul>
              </div>

              <Button variant="outline" className="w-full" onClick={() => setResult(null)}>Analyze Another Claim</Button>
            </Card>
          )}

          {!loading && !error && !result && (
            <Card className="p-12 flex flex-col items-center justify-center text-center h-[500px] border-dashed">
              <p className="text-secondary">Fill out the claim details and run the analysis to view the AI risk report.</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
