import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getModelInfo = async () => {
  const response = await api.get('/model-info');
  return response.data;
};

export const fetchDashboardStats = async () => {
  const response = await api.get('/dashboard/stats');
  return response.data;
};

export const analyzeClaim = async (data: any) => {
  const response = await api.post('/analyze-claim', data);
  return response.data;
};

export const analyzeProvider = async (data: any) => {
  const response = await api.post('/analyze-provider', data);
  return response.data;
};

export const analyzeAnomaly = async (data: any) => {
  const response = await api.post('/analyze-anomaly', data);
  return response.data;
};

// ─── Investigation History API ──────────────────────────────────────

export const fetchHistory = async () => {
  const response = await api.get('/history');
  return response.data;
};

export const fetchHistoryById = async (id: string) => {
  const response = await api.get(`/history/${id}`);
  return response.data;
};

export const saveHistoryRecord = async (record: any) => {
  const response = await api.post('/history', record);
  return response.data;
};

export const deleteAllHistory = async () => {
  const response = await api.delete('/history');
  return response.data;
};

// ─── Healthcare & Patient Identity API (Phase 2) ───────────────────

export const fetchPatients = async () => {
  const response = await api.get('/patients');
  return response.data;
};

export const fetchPatientById = async (patientId: string) => {
  const response = await api.get(`/patients/${patientId}`);
  return response.data;
};

export const registerPatient = async (data: {
  full_name: string;
  date_of_birth: string;
  gender: string;
  phone: string;
  address?: string;
}) => {
  const response = await api.post('/patients', data);
  return response.data;
};

export const fetchHospitals = async () => {
  const response = await api.get('/hospitals');
  return response.data;
};

export const fetchHospitalById = async (hospitalId: string) => {
  const response = await api.get(`/hospitals/${hospitalId}`);
  return response.data;
};

export const fetchEncounters = async (params?: { patient_id?: string; hospital_id?: string }) => {
  const response = await api.get('/encounters', { params });
  return response.data;
};

export const fetchEncounterById = async (encounterId: string) => {
  const response = await api.get(`/encounters/${encounterId}`);
  return response.data;
};

export const createEncounter = async (data: any) => {
  const response = await api.post('/encounters', data);
  return response.data;
};

export const fetchIssues = async (encounterId: string) => {
  const response = await api.get(`/issues/${encounterId}`);
  return response.data;
};

export const createIssue = async (data: any) => {
  const response = await api.post('/issues', data);
  return response.data;
};

export const fetchPrescription = async (encounterId: string) => {
  const response = await api.get(`/prescriptions/${encounterId}`);
  return response.data;
};

export const createPrescription = async (data: any) => {
  const response = await api.post('/prescriptions', data);
  return response.data;
};

export const fetchMedicines = async () => {
  const response = await api.get('/medicines');
  return response.data;
};

export const lookupMedicine = async (name: string) => {
  const response = await api.get('/medicines/lookup', { params: { name } });
  return response.data;
};

export const fetchBill = async (encounterId: string) => {
  const response = await api.get(`/bills/${encounterId}`);
  return response.data;
};

export const createBill = async (data: any) => {
  const response = await api.post('/bills', data);
  return response.data;
};

export const fetchClaims = async (patientId?: string) => {
  const response = await api.get('/claims', { params: patientId ? { patient_id: patientId } : {} });
  return response.data;
};

export const fetchClaimById = async (claimId: string) => {
  const response = await api.get(`/claims/${claimId}`);
  return response.data;
};

export const createClaim = async (data: any) => {
  const response = await api.post('/claims', data);
  return response.data;
};

export const verifyClaim = async (claimId: string) => {
  const response = await api.post('/verify-claim', { claim_id: claimId });
  return response.data;
};

export const fetchVerification = async (claimId: string) => {
  const response = await api.get(`/verifications/${claimId}`);
  return response.data;
};

export default api;
