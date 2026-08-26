import { fetchHistory, fetchHistoryById, saveHistoryRecord, deleteAllHistory } from './api';

export type HistoryRecord = {
  id: string;
  type: 'Claim' | 'Provider' | 'Anomaly';
  timestamp: string;
  riskScore: number;
  riskLevel: string;
  status: string;
  result: any;
};

/**
 * Fetch all investigation history records from the backend API (DynamoDB).
 * Returns an empty array if the backend is unavailable.
 */
export const getHistory = async (): Promise<HistoryRecord[]> => {
  try {
    const data = await fetchHistory();
    return data as HistoryRecord[];
  } catch (error) {
    console.warn('Could not fetch history from backend:', error);
    return [];
  }
};

/**
 * Fetch a single investigation history record by ID from the backend API.
 * Returns undefined if the record is not found or the backend is unavailable.
 */
export const getHistoryById = async (id: string): Promise<HistoryRecord | undefined> => {
  try {
    const data = await fetchHistoryById(id);
    return data as HistoryRecord;
  } catch (error) {
    console.warn(`Could not fetch history record ${id} from backend:`, error);
    return undefined;
  }
};

/**
 * Save an investigation history record via the backend API (DynamoDB).
 * Logs a warning if the backend is unavailable but does not throw.
 */
export const saveHistory = async (record: HistoryRecord): Promise<void> => {
  try {
    await saveHistoryRecord(record);
  } catch (error) {
    console.warn('Could not save history to backend:', error);
  }
};

/**
 * Clear all investigation history via the backend API (DynamoDB).
 * Returns the number of records deleted, or 0 if the backend is unavailable.
 */
export const clearHistory = async (): Promise<number> => {
  try {
    const result = await deleteAllHistory();
    return result.deleted || 0;
  } catch (error) {
    console.warn('Could not clear history from backend:', error);
    return 0;
  }
};
