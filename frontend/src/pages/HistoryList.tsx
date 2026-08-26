import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/layout';
import { Card, RiskBadge, Input, Select, Button } from '../components/ui';
import { getHistory, clearHistory, type HistoryRecord } from '../services/history';

export default function HistoryList() {
  const navigate = useNavigate();
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getHistory().then(data => {
      setHistory(data);
      setLoading(false);
    });
  }, []);

  const handleClear = async () => {
    if (window.confirm('Are you sure you want to clear all investigation history? This will permanently delete all records.')) {
      await clearHistory();
      setHistory([]);
    }
  };

  const filtered = history.filter(item => {
    if (typeFilter !== 'All' && item.type !== typeFilter) return false;
    
    // Normalize risk level matching
    const itemRisk = item.type === 'Anomaly' ? item.status : item.riskLevel;
    if (riskFilter !== 'All') {
      if (riskFilter === 'High' && !itemRisk.includes('HIGH')) return false;
      if (riskFilter === 'Medium' && !itemRisk.includes('MEDIUM')) return false;
      if (riskFilter === 'Low' && !itemRisk.includes('LOW')) return false;
      if (riskFilter === 'Suspicious' && !itemRisk.includes('SUSPICIOUS')) return false;
    }

    if (search) {
      return item.id.toLowerCase().includes(search.toLowerCase());
    }
    return true;
  });

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Investigation History" 
        subtitle="Review past AI analyses and risk reports."
        action={history.length > 0 && <Button variant="outline" onClick={handleClear}>Clear History</Button>}
      />

      <Card className="p-4 md:p-6">
        <div className="flex flex-col md:flex-row md:items-end gap-4 mb-6">
          <div className="flex-1">
            <Input 
              name="search" 
              label="Search by ID" 
              placeholder="e.g. af5a..." 
              value={search} 
              onChange={e => setSearch(e.target.value)} 
            />
          </div>
          <div className="w-full md:w-48">
            <Select 
              name="type" 
              label="Type" 
              options={['All', 'Claim', 'Provider', 'Anomaly']} 
              value={typeFilter} 
              onChange={e => setTypeFilter(e.target.value)} 
            />
          </div>
          <div className="w-full md:w-48">
            <Select 
              name="risk" 
              label="Risk Level" 
              options={['All', 'High', 'Medium', 'Low', 'Suspicious']} 
              value={riskFilter} 
              onChange={e => setRiskFilter(e.target.value)} 
            />
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-secondary">Loading investigation history...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-border rounded-lg">
            <p className="text-secondary mb-4">No investigations found.</p>
            <Button variant="outline" onClick={() => navigate('/claim-analysis')}>Run New Analysis</Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs text-secondary uppercase bg-surface-alt border-y border-border">
                <tr>
                  <th className="px-4 py-3 font-semibold rounded-tl-lg">ID</th>
                  <th className="px-4 py-3 font-semibold">Type</th>
                  <th className="px-4 py-3 font-semibold">Date</th>
                  <th className="px-4 py-3 font-semibold">Score</th>
                  <th className="px-4 py-3 font-semibold">Risk Level</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map(item => (
                  <tr 
                    key={item.id} 
                    onClick={() => navigate(`/history/${item.id}`)}
                    className="hover:bg-surface-alt transition-colors cursor-pointer group"
                  >
                    <td className="px-4 py-3 font-mono text-xs text-secondary group-hover:text-primary transition-colors">
                      {item.id.split('-')[0]}...
                    </td>
                    <td className="px-4 py-3 font-medium text-primary">{item.type}</td>
                    <td className="px-4 py-3 text-secondary">{new Date(item.timestamp).toLocaleString()}</td>
                    <td className="px-4 py-3 tabular-nums font-medium">
                      {item.type === 'Anomaly' ? item.riskScore?.toFixed(2) : Math.round(item.riskScore)}
                    </td>
                    <td className="px-4 py-3">
                      <RiskBadge level={item.type === 'Anomaly' ? item.status : item.riskLevel} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
