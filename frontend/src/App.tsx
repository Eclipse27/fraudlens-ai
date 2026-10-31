import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout';
import Dashboard from './pages/Dashboard';
import ClaimAnalysis from './pages/ClaimAnalysis';
import ProviderAnalysis from './pages/ProviderAnalysis';
import AnomalyDetection from './pages/AnomalyDetection';
import HistoryList from './pages/HistoryList';
import HistoryDetail from './pages/HistoryDetail';
import ModelIntelligence from './pages/ModelIntelligence';
import SystemStatus from './pages/SystemStatus';
// Phase 2 Pages
import PatientRegistry from './pages/PatientRegistry';
import PatientDetail from './pages/PatientDetail';
import ClaimVerification from './pages/ClaimVerification';
import ClaimVerificationReport from './pages/ClaimVerificationReport';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          {/* Core ML Detection Routes */}
          <Route path="claim-analysis" element={<ClaimAnalysis />} />
          <Route path="provider-analysis" element={<ProviderAnalysis />} />
          <Route path="anomaly-detection" element={<AnomalyDetection />} />
          {/* Phase 2: Patient Identity & Claim Verification Routes */}
          <Route path="patients" element={<PatientRegistry />} />
          <Route path="patients/:id" element={<PatientDetail />} />
          <Route path="claim-verification" element={<ClaimVerification />} />
          <Route path="claim-verification/:id" element={<ClaimVerificationReport />} />
          {/* Operations & Auditing Routes */}
          <Route path="history" element={<HistoryList />} />
          <Route path="history/:id" element={<HistoryDetail />} />
          <Route path="models" element={<ModelIntelligence />} />
          <Route path="system-status" element={<SystemStatus />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
