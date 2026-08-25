import { useState, useEffect } from 'react';
import { PageHeader } from '../components/layout';
import { Card } from '../components/ui';
import { StatusPill, LoadingState, ErrorState } from '../components/feedback';
import { getModelInfo } from '../services/api';
import { BrainCircuit, Activity, Network } from 'lucide-react';

export default function ModelIntelligence() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<any>(null);

  useEffect(() => {
    fetchModelInfo();
  }, []);

  const fetchModelInfo = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getModelInfo();
      setInfo(data);
    } catch (err) {
      setError("Unable to connect to the backend to retrieve model status.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Fetching model intelligence..." />;
  if (error) return <ErrorState message={error} onRetry={fetchModelInfo} />;

  const valMetrics = info?.validation_metrics || {};

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Model Intelligence" 
        subtitle="Review active machine learning models and their validation metrics."
      />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Claim Fraud Model */}
        <Card className="flex flex-col">
          <div className="p-6 border-b border-border">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-ai/10 rounded-xl flex items-center justify-center">
                <BrainCircuit className="w-6 h-6 text-ai" />
              </div>
              <StatusPill status={info.claim_model === 'Loaded' ? 'LOADED' : 'ERROR'} />
            </div>
            <h3 className="text-xl font-bold text-primary mb-1">Claim Fraud Model</h3>
            <p className="text-sm font-medium text-accent">Regularized XGBoost</p>
            <p className="text-sm text-secondary mt-3 leading-relaxed">
              Supervised classification model evaluating 41 structured features to predict the probability of a fraudulent claim.
            </p>
          </div>
          <div className="p-6 bg-surface-alt flex-1">
            <h4 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-4">Test Set Metrics</h4>
            {valMetrics.Claim ? (
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-primary font-medium">Test F1 Score</span>
                    <span className="text-primary font-bold">{valMetrics.Claim.Test_F1.toFixed(4)}</span>
                  </div>
                  <div className="w-full bg-border rounded-full h-1.5"><div className="bg-accent h-1.5 rounded-full" style={{width: `${valMetrics.Claim.Test_F1 * 100}%`}}></div></div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-primary font-medium">Test PR-AUC</span>
                    <span className="text-primary font-bold">{valMetrics.Claim.Test_PR_AUC.toFixed(4)}</span>
                  </div>
                  <div className="w-full bg-border rounded-full h-1.5"><div className="bg-accent h-1.5 rounded-full" style={{width: `${valMetrics.Claim.Test_PR_AUC * 100}%`}}></div></div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-primary font-medium">Test Recall</span>
                    <span className="text-primary font-bold">{valMetrics.Claim.Test_Recall.toFixed(4)}</span>
                  </div>
                  <div className="w-full bg-border rounded-full h-1.5"><div className="bg-accent h-1.5 rounded-full" style={{width: `${valMetrics.Claim.Test_Recall * 100}%`}}></div></div>
                </div>
                <div className="pt-4 border-t border-border/50">
                  <div className="flex justify-between text-sm">
                    <span className="text-secondary">Generalization Gap</span>
                    <span className="text-primary font-medium tabular-nums">{Math.abs(valMetrics.Claim.Train_F1 - valMetrics.Claim.Test_F1).toFixed(4)}</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-secondary">Metrics unavailable.</p>
            )}
          </div>
        </Card>

        {/* Provider Fraud Model */}
        <Card className="flex flex-col">
          <div className="p-6 border-b border-border">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-ai/10 rounded-xl flex items-center justify-center">
                <Network className="w-6 h-6 text-ai" />
              </div>
              <StatusPill status={info.provider_model === 'Loaded' ? 'LOADED' : 'ERROR'} />
            </div>
            <h3 className="text-xl font-bold text-primary mb-1">Provider Fraud Model</h3>
            <p className="text-sm font-medium text-accent">Logistic Regression</p>
            <p className="text-sm text-secondary mt-3 leading-relaxed">
              Supervised model assessing aggregate provider behavior (financials, patient volume, demographics) over 31 features.
            </p>
          </div>
          <div className="p-6 bg-surface-alt flex-1">
            <h4 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-4">Test Set Metrics</h4>
            {valMetrics.Provider ? (
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-primary font-medium">Test PR-AUC</span>
                    <span className="text-primary font-bold">{valMetrics.Provider.Test_PR_AUC.toFixed(4)}</span>
                  </div>
                  <div className="w-full bg-border rounded-full h-1.5"><div className="bg-accent h-1.5 rounded-full" style={{width: `${valMetrics.Provider.Test_PR_AUC * 100}%`}}></div></div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-primary font-medium">Test F1 Score</span>
                    <span className="text-primary font-bold">{valMetrics.Provider.Test_F1.toFixed(4)}</span>
                  </div>
                  <div className="w-full bg-border rounded-full h-1.5"><div className="bg-accent h-1.5 rounded-full" style={{width: `${valMetrics.Provider.Test_F1 * 100}%`}}></div></div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-primary font-medium">Test Recall</span>
                    <span className="text-primary font-bold">{valMetrics.Provider.Test_Recall.toFixed(4)}</span>
                  </div>
                  <div className="w-full bg-border rounded-full h-1.5"><div className="bg-accent h-1.5 rounded-full" style={{width: `${valMetrics.Provider.Test_Recall * 100}%`}}></div></div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-secondary">Metrics unavailable.</p>
            )}
          </div>
        </Card>

        {/* CMS Pattern Model */}
        <Card className="flex flex-col">
          <div className="p-6 border-b border-border">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-ai/10 rounded-xl flex items-center justify-center">
                <Activity className="w-6 h-6 text-ai" />
              </div>
              <StatusPill status={info.anomaly_model === 'Loaded' ? 'LOADED' : 'ERROR'} />
            </div>
            <h3 className="text-xl font-bold text-primary mb-1">CMS Pattern Model</h3>
            <p className="text-sm font-medium text-accent">Isolation Forest</p>
            <p className="text-sm text-secondary mt-3 leading-relaxed">
              Unsupervised anomaly detection trained on CMS records to identify utilization outliers.
            </p>
          </div>
          <div className="p-6 bg-surface-alt flex-1">
            <h4 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-4">Configuration</h4>
            {valMetrics.CMS ? (
              <div className="space-y-4">
                <div className="flex flex-col">
                  <span className="text-xs text-secondary font-medium uppercase tracking-wide mb-1">Records Trained</span>
                  <span className="text-primary font-bold">{valMetrics.CMS.Records.toLocaleString()}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-secondary font-medium uppercase tracking-wide mb-1">Anomalies Detected</span>
                  <span className="text-primary font-bold">{valMetrics.CMS.Anomalies.toLocaleString()} ({(valMetrics.CMS.Anomaly_Pct).toFixed(2)}%)</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-secondary font-medium uppercase tracking-wide mb-1">Anomaly Labeling</span>
                  <span className="text-primary font-bold">Unsupervised</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-secondary">Metrics unavailable.</p>
            )}
          </div>
        </Card>
      </div>

      <p className="text-xs text-secondary text-center max-w-2xl mx-auto mt-8">
        <strong>Disclaimer:</strong> Fraud predictions represent risk estimates, not proof of fraudulent activity. 
        Thresholds and model parameters should be periodically reviewed against operational outcomes.
      </p>
    </div>
  );
}
