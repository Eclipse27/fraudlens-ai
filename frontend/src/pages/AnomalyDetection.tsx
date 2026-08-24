import { useState } from 'react';
import { PageHeader } from '../components/layout';
import { Card, Button, Input, Select, RiskBadge } from '../components/ui';
import { LoadingState, ErrorState } from '../components/feedback';
import { analyzeAnomaly } from '../services/api';
import { saveHistory } from '../services/history';

export default function AnomalyDetection() {
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
      procedure_category: formData.get('procedure_category'),
      count: Number(formData.get('count')),
      profile_display_indicator: formData.get('profile_display_indicator'),
    };

    try {
      const res = await analyzeAnomaly(data);
      setResult({ ...res, ...data }); // store inputs with result for history
      saveHistory({
        id: crypto.randomUUID(),
        type: 'Anomaly',
        timestamp: new Date().toISOString(),
        riskScore: res.anomaly_score, // Not out of 100, just negative/positive decision function
        riskLevel: res.anomaly_status,
        status: res.anomaly_status,
        result: res
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Unable to connect to the AI analysis service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="CMS Anomaly Detection" 
        subtitle="Unsupervised pattern recognition for healthcare utilization anomalies."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="bg-ai/5 border border-ai/20 rounded-lg p-4 mb-6">
              <h4 className="font-semibold text-ai text-sm mb-1">How anomaly detection works</h4>
              <p className="text-xs text-secondary leading-relaxed">
                The AI compares the submitted utilization pattern against patterns observed across real CMS utilization records. It uses an Isolation Forest to flag instances that deviate significantly from the norm.
              </p>
            </div>

            <div className="space-y-4">
              <Input name="procedure_category" label="Procedure Category" type="text" required defaultValue="Cardiology Services" />
              <Input name="count" label="Procedure Count (Volume)" type="number" required defaultValue={1500} />
              <Select name="profile_display_indicator" label="Profile Display Indicator" options={['Y', 'N']} defaultValue="Y" />
            </div>

            <Button type="submit" className="w-full" isLoading={loading}>Check Pattern</Button>
          </form>
        </Card>

        <div>
          {loading && <Card><LoadingState message="Analyzing utilization pattern..." /></Card>}
          {error && <Card><ErrorState message={error} onRetry={() => setError(null)} /></Card>}
          
          {!loading && !error && result && (
            <Card className="p-6">
              <div className="flex flex-col items-center justify-center border-b border-border pb-6 mb-6">
                <RiskBadge level={result.anomaly_status} className="mb-4 px-3 py-1.5 text-sm" />
                
                <div className="text-center mt-2">
                  <span className="text-secondary text-sm font-medium">Anomaly Score</span>
                  <div className="text-3xl font-bold tabular-nums text-primary mt-1">
                    {result.anomaly_score?.toFixed(4)}
                  </div>
                  <p className="text-xs text-secondary mt-1">Negative scores indicate anomalies</p>
                </div>
              </div>

              <div className="mb-6 p-4 bg-surface-alt rounded-lg border border-border">
                <h4 className="text-sm font-semibold text-primary mb-2">Analysis Result</h4>
                <p className="text-sm text-primary mb-4">{result.recommendation}</p>
                <div className="text-xs text-secondary border-t border-border pt-4">
                  <strong>Disclaimer:</strong> An anomaly indicates an unusual utilization pattern and does not confirm fraudulent activity. It simply highlights volume or category deviations that may warrant further review.
                </div>
              </div>

              <Button variant="outline" className="w-full" onClick={() => setResult(null)}>Check Another Pattern</Button>
            </Card>
          )}

          {!loading && !error && !result && (
            <Card className="p-12 flex flex-col items-center justify-center text-center h-[400px] border-dashed">
              <p className="text-secondary">Enter utilization details to detect anomalous patterns.</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
