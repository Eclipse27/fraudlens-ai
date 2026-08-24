export type HistoryRecord = {
  id: string;
  type: 'Claim' | 'Provider' | 'Anomaly';
  timestamp: string;
  riskScore: number;
  riskLevel: string;
  status: string;
  result: any;
};

const STORAGE_KEY = 'fraud_investigation_history';

export const getHistory = (): HistoryRecord[] => {
  const data = localStorage.getItem(STORAGE_KEY);
  if (!data) return [];
  try {
    return JSON.parse(data) as HistoryRecord[];
  } catch {
    return [];
  }
};

export const getHistoryById = (id: string): HistoryRecord | undefined => {
  return getHistory().find(r => r.id === id);
};

export const saveHistory = (record: HistoryRecord) => {
  const history = getHistory();
  history.unshift(record); // Add to beginning
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
};

export const clearHistory = () => {
  localStorage.removeItem(STORAGE_KEY);
};
