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

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="claim-analysis" element={<ClaimAnalysis />} />
          <Route path="provider-analysis" element={<ProviderAnalysis />} />
          <Route path="anomaly-detection" element={<AnomalyDetection />} />
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
