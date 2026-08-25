import { useState, useEffect } from 'react';
import { PageHeader } from '../components/layout';
import { Card, Button } from '../components/ui';
import { StatusPill } from '../components/feedback';
import { getHealth, API_BASE_URL } from '../services/api';
import { Server, Database, BrainCircuit, RefreshCw, Activity, Network } from 'lucide-react';

export default function SystemStatus() {
  const [loading, setLoading] = useState(true);
  const [health, setHealth] = useState<any>(null);
  const [lastChecked, setLastChecked] = useState<Date>(new Date());

  const checkHealth = async () => {
    setLoading(true);
    try {
      const data = await getHealth();
      setHealth({ ...data, api_status: 'ONLINE' });
    } catch {
      setHealth({ api_status: 'OFFLINE', models_loaded: false });
    } finally {
      setLastChecked(new Date());
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader 
        title="System Status" 
        subtitle="Monitor backend connectivity and ML model availability."
        action={
          <Button onClick={checkHealth} disabled={loading} variant="outline" className="flex items-center space-x-2">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-accent' : ''}`} />
            <span>Refresh Status</span>
          </Button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-6 border-b border-border pb-4">
            <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
              <Server className="w-5 h-5 text-accent" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary">FastAPI Backend</h3>
              <p className="text-xs text-secondary">{API_BASE_URL}</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-secondary">API Status</span>
              <StatusPill status={health?.api_status || 'OFFLINE'} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-secondary">Local Storage (History)</span>
              <StatusPill status="ONLINE" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-secondary">Last Checked</span>
              <span className="text-sm text-primary">{lastChecked.toLocaleTimeString()}</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-6 border-b border-border pb-4">
            <div className="w-10 h-10 bg-ai/10 rounded-lg flex items-center justify-center">
              <Database className="w-5 h-5 text-ai" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary">ML Models</h3>
              <p className="text-xs text-secondary">Memory-resident predictive models</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <BrainCircuit className="w-4 h-4 text-secondary" />
                <span className="text-sm font-medium text-secondary">Claim Fraud Model</span>
              </div>
              <StatusPill status={health?.models?.claim_model === 'loaded' ? 'LOADED' : 'ERROR'} />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Network className="w-4 h-4 text-secondary" />
                <span className="text-sm font-medium text-secondary">Provider Fraud Model</span>
              </div>
              <StatusPill status={health?.models?.provider_model === 'loaded' ? 'LOADED' : 'ERROR'} />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-secondary" />
                <span className="text-sm font-medium text-secondary">CMS Anomaly Model</span>
              </div>
              <StatusPill status={health?.models?.cms_model === 'loaded' ? 'LOADED' : 'ERROR'} />
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
