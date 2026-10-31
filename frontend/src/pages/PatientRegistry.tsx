import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/layout';
import { Card, Button, Input, Select } from '../components/ui';
import { fetchPatients, registerPatient, fetchHospitals } from '../services/api';
import { Users, UserPlus, Search, Building2, AlertTriangle, CheckCircle, ExternalLink, ShieldCheck } from 'lucide-react';

interface Patient {
  patient_id: string;
  full_name: string;
  date_of_birth: string;
  gender: string;
  phone: string;
  address: string;
  created_at: string;
  potential_duplicate_flag?: boolean;
}

interface Hospital {
  hospital_id: string;
  name: string;
  type: string;
  address: string;
  city: string;
}

export default function PatientRegistry() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showRegModal, setShowRegModal] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [regMessage, setRegMessage] = useState<{ type: 'success' | 'warning' | 'error'; text: string } | null>(null);

  // Form State
  const [fullName, setFullName] = useState('');
  const [dob, setDob] = useState('');
  const [gender, setGender] = useState('Male');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [pts, hsps] = await Promise.all([
        fetchPatients().catch(() => []),
        fetchHospitals().catch(() => [])
      ]);
      setPatients(pts || []);
      setHospitals(hsps || []);
    } catch (err) {
      console.error('Failed to load patient data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();
    setRegMessage(null);

    if (!fullName.trim() || !dob || !phone.trim()) {
      setRegMessage({ type: 'error', text: 'Full Name, Date of Birth, and Phone are required.' });
      return;
    }

    try {
      setRegistering(true);
      const res = await registerPatient({
        full_name: fullName.trim(),
        date_of_birth: dob,
        gender,
        phone: phone.trim(),
        address: address.trim(),
      });

      if (res.is_new) {
        setRegMessage({
          type: 'success',
          text: `Success: New patient registered with ID ${res.patient.patient_id}.`
        });
      } else {
        setRegMessage({
          type: 'warning',
          text: `Duplicate Match: Patient already registered across shared network with ID ${res.patient.patient_id}. Returning existing identity record.`
        });
      }

      // Refresh list
      const pts = await fetchPatients().catch(() => []);
      setPatients(pts || []);

      // Reset form fields
      setFullName('');
      setDob('');
      setPhone('');
      setAddress('');
    } catch (err: any) {
      setRegMessage({
        type: 'error',
        text: err?.response?.data?.detail || 'Registration failed. Check network or server connection.'
      });
    } finally {
      setRegistering(false);
    }
  };

  const filteredPatients = patients.filter(p =>
    p.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.patient_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.phone?.includes(searchTerm)
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Patient Identity Registry"
        subtitle="Global cross-hospital master patient index (MPI) covering Prayagraj healthcare network."
        action={
          <Button onClick={() => setShowRegModal(true)} className="flex items-center space-x-2">
            <UserPlus className="w-4 h-4" />
            <span>Register New Patient</span>
          </Button>
        }
      />

      {/* Network Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {hospitals.map((h) => (
          <Card key={h.hospital_id} className="p-4 border-l-4 border-l-accent flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-surface-alt text-secondary">
                  {h.hospital_id}
                </span>
                <span className="text-xs text-accent font-medium">{h.city}</span>
              </div>
              <h4 className="font-semibold text-primary text-sm mt-1">{h.name}</h4>
              <p className="text-xs text-secondary mt-1">{h.type}</p>
            </div>
            <div className="mt-3 pt-2 border-t border-border flex items-center text-xs text-gray-400">
              <Building2 className="w-3.5 h-3.5 mr-1 text-accent" />
              <span>{h.address}</span>
            </div>
          </Card>
        ))}
      </div>

      {/* Search and Filters */}
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="relative w-full sm:w-96">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-secondary" />
            <input
              type="text"
              placeholder="Search by name, Patient ID (FL-PAT-...), or phone..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-lg border border-border bg-transparent text-sm focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div className="text-xs text-secondary font-medium">
            Showing <span className="text-primary font-bold">{filteredPatients.length}</span> of {patients.length} registered patients
          </div>
        </div>
      </Card>

      {/* Patients Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface-alt border-b border-border text-xs uppercase text-secondary font-semibold">
              <tr>
                <th className="px-6 py-3">Patient ID</th>
                <th className="px-6 py-3">Full Name</th>
                <th className="px-6 py-3">Date of Birth</th>
                <th className="px-6 py-3">Gender</th>
                <th className="px-6 py-3">Phone</th>
                <th className="px-6 py-3">City / Address</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-secondary">
                    <div className="flex items-center justify-center space-x-2">
                      <span className="w-4 h-4 rounded-full border-2 border-accent border-t-transparent animate-spin" />
                      <span>Loading patient records...</span>
                    </div>
                  </td>
                </tr>
              ) : filteredPatients.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-secondary">
                    No patient records found matching your criteria.
                  </td>
                </tr>
              ) : (
                filteredPatients.map((p) => (
                  <tr key={p.patient_id} className="hover:bg-surface-alt/50 transition-colors">
                    <td className="px-6 py-4 font-mono font-medium text-accent">
                      {p.patient_id}
                    </td>
                    <td className="px-6 py-4 font-semibold text-primary">
                      {p.full_name}
                      {p.potential_duplicate_flag && (
                        <span className="ml-2 inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-risk-medium-bg text-risk-medium font-bold">
                          Review Flagged
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-secondary">{p.date_of_birth}</td>
                    <td className="px-6 py-4 text-secondary">{p.gender}</td>
                    <td className="px-6 py-4 text-secondary font-mono text-xs">{p.phone}</td>
                    <td className="px-6 py-4 text-secondary">{p.address || '—'}</td>
                    <td className="px-6 py-4 text-right">
                      <Button
                        variant="outline"
                        className="py-1 px-3 text-xs"
                        onClick={() => navigate(`/patients/${p.patient_id}`)}
                      >
                        <span>View EHR Record</span>
                        <ExternalLink className="w-3.5 h-3.5 ml-1.5" />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Registration Modal */}
      {showRegModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy-900/60 backdrop-blur-sm p-4">
          <div className="bg-surface border border-border rounded-xl shadow-xl max-w-lg w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="px-6 py-4 border-b border-border flex items-center justify-between bg-surface-alt/50">
              <div className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-accent" />
                <h3 className="font-bold text-primary">Register Patient in Global Registry</h3>
              </div>
              <button
                onClick={() => { setShowRegModal(false); setRegMessage(null); }}
                className="text-secondary hover:text-primary text-xl font-bold"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleRegister} className="p-6 space-y-4">
              <div className="p-3 bg-surface-alt rounded-lg text-xs text-secondary flex items-start space-x-2">
                <ShieldCheck className="w-4 h-4 text-accent shrink-0 mt-0.5" />
                <span>
                  <strong>Safe 4-Field Identity Matching:</strong> Patient records are deduplicated globally across all Prayagraj hospitals using Name + Date of Birth + Gender + Phone.
                </span>
              </div>

              {regMessage && (
                <div className={`p-3 rounded-lg text-xs flex items-start space-x-2 ${
                  regMessage.type === 'success'
                    ? 'bg-risk-low-bg text-risk-low'
                    : regMessage.type === 'warning'
                    ? 'bg-risk-medium-bg text-risk-medium'
                    : 'bg-risk-high-bg text-risk-high'
                }`}>
                  {regMessage.type === 'success' ? (
                    <CheckCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  )}
                  <span>{regMessage.text}</span>
                </div>
              )}

              <Input
                label="Full Legal Name"
                placeholder="e.g. Ramesh Kumar Verma"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Date of Birth"
                  type="date"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                  required
                />
                <Select
                  label="Gender"
                  options={['Male', 'Female', 'Other']}
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                />
              </div>

              <Input
                label="10-Digit Phone Number"
                placeholder="9876543210"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
              />

              <Input
                label="Residential Address / City"
                placeholder="Civil Lines, Prayagraj"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
              />

              <div className="pt-4 border-t border-border flex items-center justify-end space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => { setShowRegModal(false); setRegMessage(null); }}
                >
                  Close
                </Button>
                <Button type="submit" isLoading={registering}>
                  Verify & Register
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
