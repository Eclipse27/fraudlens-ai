import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/layout';
import { Card, Button, RiskBadge, RiskScoreGauge, cn } from '../components/ui';
import { getHistoryById, type HistoryRecord } from '../services/history';
import { ShieldCheck, ShieldAlert, ArrowLeft } from 'lucide-react';

export default function HistoryDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [record, setRecord] = useState<HistoryRecord | null>(null);

  useEffect(() => {
    if (id) {
      const rec = getHistoryById(id);
      setRecord(rec || null);
    }
  }, [id]);

  if (!record) {
    return (
      <div className="space-y-6">
        <Button variant="outline" onClick={() => navigate('/history')} className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to History
        </Button>
        <Card className="p-12 text-center">
          <p className="text-secondary">Investigation record not found.</p>
        </Card>
      </div>
    );
  }

  const { result, type } = record;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4 mb-2">
        <Button variant="outline" onClick={() => navigate('/history')} className="h-8 px-2 py-1 text-xs">
          <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back
        </Button>
        <span className="text-sm text-secondary font-medium">Record ID: <span className="font-mono">{record.id}</span></span>
      </div>
      
      <PageHeader 
        title={`${type} Investigation Report`}
        subtitle={`Analysis run on ${new Date(record.timestamp).toLocaleString()}`}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Results Panel */}
        <Card className="p-6">
          <div className="flex flex-col items-center justify-center border-b border-border pb-6 mb-6">
            {type !== 'Anomaly' ? (
              <RiskScoreGauge score={record.riskScore} />
            ) : (
              <div className="text-center">
                <span className="text-secondary text-sm font-medium">Anomaly Risk</span>
                <div className="text-4xl font-bold tabular-nums text-primary mt-2">
                  {record.riskScore?.toFixed(2)}%
                </div>
              </div>
            )}
            <RiskBadge level={record.status || record.riskLevel} className="mt-4" />
            {result.prediction && <p className="text-lg font-semibold text-primary mt-2">{result.prediction}</p>}
          </div>

          <div className="mb-6">
            <h4 className="text-sm font-semibold text-primary uppercase tracking-wide mb-3">
              {type === 'Claim' ? 'AI Risk Factors' : type === 'Provider' ? 'Top Risk Indicators' : 'Analysis Result'}
            </h4>
            
            {type === 'Anomaly' && (
              <p className="text-sm text-primary mb-4 bg-surface-alt p-3 rounded-lg border border-border">
                {result.recommendation}
              </p>
            )}

            {(type === 'Claim' || type === 'Provider') && result.risk_factors && (
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
            )}

            {type === 'Provider' && result.top_factors && (
              <div className="space-y-3">
                {result.top_factors.length > 0 ? result.top_factors.map((rf: any, idx: number) => (
                  <div key={idx} className="p-3 bg-risk-high-bg/30 rounded-lg border border-red-100 flex items-start space-x-3">
                    <ShieldAlert className="w-5 h-5 text-risk-high shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold text-sm text-primary">{rf.factor}</span>
                      <p className="text-xs text-secondary">{rf.explanation}</p>
                    </div>
                  </div>
                )) : (
                  <div className="p-4 bg-risk-low-bg/50 rounded-lg border border-green-100 flex items-center space-x-3">
                    <ShieldCheck className="w-5 h-5 text-risk-low shrink-0" />
                    <p className="text-sm text-secondary">No strong positive risk indicators detected.</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {type === 'Claim' && result.recommendation && (
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
          )}
        </Card>

        {/* Input Data Panel */}
        <Card className="p-6">
          <h3 className="text-sm font-semibold text-primary uppercase tracking-wide border-b border-border pb-2 mb-4">Input Data Snapshot</h3>
          <div className="grid grid-cols-2 gap-y-4 gap-x-2 text-sm">
            {Object.entries(result).filter(([k]) => !['claim_id', 'provider_id', 'fraud_risk_score', 'risk_level', 'risk_factors', 'recommendation', 'prediction', 'top_factors', 'anomaly_score', 'anomaly_status'].includes(k)).map(([k, v]) => (
              <div key={k} className="break-all">
                <span className="block text-xs text-secondary font-medium uppercase tracking-wider mb-0.5">{k.replace(/_/g, ' ')}</span>
                <span className="text-primary font-medium">{String(v)}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
