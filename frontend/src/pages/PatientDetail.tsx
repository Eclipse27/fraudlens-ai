import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/layout';
import { Card, Button } from '../components/ui';
import {
  fetchPatientById,
  fetchEncounters,
  fetchHospitals,
  fetchIssues,
  fetchPrescription,
  fetchBill,
  fetchClaims
} from '../services/api';
import {
  ArrowLeft,
  Calendar,
  Phone,
  MapPin,
  Building2,
  Stethoscope,
  Pill,
  Receipt,
  FileCheck,
  AlertCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

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

interface Encounter {
  encounter_id: string;
  patient_id: string;
  hospital_id: string;
  admission_date: string;
  discharge_date: string | null;
  encounter_type: string;
  attending_doctor: string;
  department: string;
  notes: string;
}

interface Hospital {
  hospital_id: string;
  name: string;
  city: string;
  type: string;
}

export default function PatientDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [patient, setPatient] = useState<Patient | null>(null);
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [hospitals, setHospitals] = useState<Record<string, Hospital>>({});
  const [encounterDetails, setEncounterDetails] = useState<Record<string, {
    issues: any[];
    prescription: any | null;
    bill: any | null;
  }>>({});
  const [claims, setClaims] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedEncounters, setExpandedEncounters] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (!id) return;

    const loadPatientEhr = async () => {
      try {
        setLoading(true);
        const [pt, encs, hsps, clms] = await Promise.all([
          fetchPatientById(id),
          fetchEncounters({ patient_id: id }),
          fetchHospitals().catch(() => []),
          fetchClaims(id).catch(() => [])
        ]);

        setPatient(pt);
        setEncounters(encs || []);
        setClaims(clms || []);

        const hMap: Record<string, Hospital> = {};
        (hsps || []).forEach((h: Hospital) => {
          hMap[h.hospital_id] = h;
        });
        setHospitals(hMap);

        // Fetch details for each encounter
        const detailsMap: Record<string, any> = {};
        const expandMap: Record<string, boolean> = {};

        await Promise.all(
          (encs || []).map(async (enc: Encounter) => {
            expandMap[enc.encounter_id] = true; // expanded by default
            const [issues, prx, bill] = await Promise.all([
              fetchIssues(enc.encounter_id).catch(() => []),
              fetchPrescription(enc.encounter_id).catch(() => null),
              fetchBill(enc.encounter_id).catch(() => null)
            ]);
            detailsMap[enc.encounter_id] = {
              issues: issues || [],
              prescription: prx,
              bill: bill
            };
          })
        );

        setEncounterDetails(detailsMap);
        setExpandedEncounters(expandMap);
      } catch (err) {
        console.error('Failed to load patient EHR record:', err);
      } finally {
        setLoading(false);
      }
    };

    loadPatientEhr();
  }, [id]);

  const toggleExpand = (encId: string) => {
    setExpandedEncounters(prev => ({
      ...prev,
      [encId]: !prev[encId]
    }));
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <span className="w-8 h-8 rounded-full border-3 border-accent border-t-transparent animate-spin" />
        <p className="text-secondary text-sm">Loading Unified Electronic Health Record (EHR)...</p>
      </div>
    );
  }

  if (!patient) {
    return (
      <Card className="p-8 text-center space-y-4">
        <AlertCircle className="w-12 h-12 text-risk-high mx-auto" />
        <h3 className="text-lg font-bold text-primary">Patient Record Not Found</h3>
        <p className="text-sm text-secondary">The requested patient identifier '{id}' does not exist in the registry.</p>
        <Button variant="outline" onClick={() => navigate('/patients')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Registry
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Button variant="outline" className="p-2" onClick={() => navigate('/patients')}>
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <PageHeader
          title={patient.full_name}
          subtitle={`Master Patient Index (MPI): ${patient.patient_id}`}
        />
      </div>

      {/* Patient Header Card */}
      <Card className="p-6 bg-surface border border-border">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-secondary uppercase tracking-wider">Demographics</span>
            <div className="font-semibold text-primary text-base">{patient.full_name}</div>
            <div className="text-xs text-secondary flex items-center space-x-2 pt-1">
              <Calendar className="w-3.5 h-3.5 text-accent" />
              <span>DOB: {patient.date_of_birth} ({patient.gender})</span>
            </div>
          </div>

          <div className="space-y-1">
            <span className="text-xs font-semibold text-secondary uppercase tracking-wider">Contact & Location</span>
            <div className="text-xs text-primary flex items-center space-x-2 font-mono">
              <Phone className="w-3.5 h-3.5 text-accent" />
              <span>{patient.phone}</span>
            </div>
            <div className="text-xs text-secondary flex items-center space-x-2 pt-1">
              <MapPin className="w-3.5 h-3.5 text-accent" />
              <span>{patient.address || 'Prayagraj, UP'}</span>
            </div>
          </div>

          <div className="space-y-1">
            <span className="text-xs font-semibold text-secondary uppercase tracking-wider">Network Identity</span>
            <div className="font-mono text-xs font-bold text-accent">{patient.patient_id}</div>
            <div className="text-xs text-secondary pt-1">
              Registered: {new Date(patient.created_at).toLocaleDateString()}
            </div>
          </div>

          <div className="space-y-1 flex flex-col justify-between">
            <span className="text-xs font-semibold text-secondary uppercase tracking-wider">Status & Integrity</span>
            <div>
              {patient.potential_duplicate_flag ? (
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-risk-medium-bg text-risk-medium">
                  Duplicate Review Required
                </span>
              ) : (
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-risk-low-bg text-risk-low">
                  Identity Verified (Unique)
                </span>
              )}
            </div>
            <span className="text-[11px] text-gray-400">
              Shared across 3 Prayagraj hospitals
            </span>
          </div>
        </div>
      </Card>

      {/* Associated Insurance Claims */}
      {claims.length > 0 && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <FileCheck className="w-5 h-5 text-accent" />
              <h3 className="font-bold text-primary">Insurance Claims on Record ({claims.length})</h3>
            </div>
            <span className="text-xs text-secondary">Click 'Verify' to test authentic claim provenance</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {claims.map((clm) => (
              <div
                key={clm.claim_id}
                className="p-4 rounded-lg border border-border bg-surface-alt/40 flex items-center justify-between"
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-accent text-sm">{clm.claim_id}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-surface text-secondary font-medium">
                      {clm.policy_number}
                    </span>
                  </div>
                  <div className="text-xs text-primary font-semibold mt-1">
                    Amount: ₹{Number(clm.claim_amount).toLocaleString('en-IN')}
                  </div>
                  <div className="text-[11px] text-secondary mt-0.5">
                    Insurer: {clm.insurer} · Encounter: {clm.encounter_id}
                  </div>
                </div>
                <Button
                  className="text-xs py-1.5 px-3"
                  onClick={() => navigate(`/claim-verification?claim_id=${clm.claim_id}`)}
                >
                  <span>Verify Claim</span>
                  <ExternalLink className="w-3 h-3 ml-1.5" />
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Cross-Hospital Encounters */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Building2 className="w-5 h-5 text-accent" />
            <h3 className="font-bold text-primary text-lg">
              Cross-Hospital Clinical Encounters ({encounters.length})
            </h3>
          </div>
          <span className="text-xs text-secondary">
            Shared health record consolidated across Prayagraj hospital network
          </span>
        </div>

        {encounters.length === 0 ? (
          <Card className="p-8 text-center text-secondary">
            No clinical encounters recorded for this patient.
          </Card>
        ) : (
          encounters.map((enc) => {
            const hsp = hospitals[enc.hospital_id];
            const details = encounterDetails[enc.encounter_id] || { issues: [], prescription: null, bill: null };
            const isExpanded = expandedEncounters[enc.encounter_id];

            return (
              <Card key={enc.encounter_id} className="border border-border overflow-hidden">
                {/* Encounter Accordion Header */}
                <div
                  onClick={() => toggleExpand(enc.encounter_id)}
                  className="p-4 bg-surface-alt/60 hover:bg-surface-alt cursor-pointer transition-colors flex items-center justify-between border-b border-border"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4">
                    <span className="font-mono font-bold text-accent text-sm">
                      {enc.encounter_id}
                    </span>
                    <span className="font-semibold text-primary text-sm flex items-center space-x-1.5">
                      <Building2 className="w-4 h-4 text-accent" />
                      <span>{hsp?.name || enc.hospital_id}</span>
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded bg-surface text-secondary font-medium">
                      {enc.encounter_type}
                    </span>
                  </div>

                  <div className="flex items-center space-x-4">
                    <span className="text-xs text-secondary font-medium">
                      {enc.admission_date} {enc.discharge_date ? `to ${enc.discharge_date}` : '(Ongoing)'}
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-secondary" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-secondary" />
                    )}
                  </div>
                </div>

                {/* Encounter Expanded Body */}
                {isExpanded && (
                  <div className="p-6 space-y-6">
                    {/* Clinical Details */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-3 bg-surface-alt/30 rounded-lg text-xs">
                      <div>
                        <span className="text-secondary font-medium">Attending Doctor:</span>
                        <p className="font-semibold text-primary">{enc.attending_doctor || 'Not specified'}</p>
                      </div>
                      <div>
                        <span className="text-secondary font-medium">Department:</span>
                        <p className="font-semibold text-primary">{enc.department || 'General Medicine'}</p>
                      </div>
                      <div>
                        <span className="text-secondary font-medium">Clinical Notes:</span>
                        <p className="font-semibold text-primary">{enc.notes || 'None recorded'}</p>
                      </div>
                    </div>

                    {/* Diagnoses / Medical Issues */}
                    <div>
                      <div className="flex items-center space-x-2 mb-2">
                        <Stethoscope className="w-4 h-4 text-accent" />
                        <h4 className="text-xs font-bold text-primary uppercase tracking-wider">
                          Diagnosed Medical Issues ({details.issues.length})
                        </h4>
                      </div>
                      {details.issues.length === 0 ? (
                        <p className="text-xs text-secondary italic">No diagnoses recorded for this encounter.</p>
                      ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {details.issues.map((iss: any) => (
                            <div
                              key={iss.issue_id}
                              className="p-3 rounded-lg border border-border bg-surface flex items-center justify-between"
                            >
                              <div>
                                <p className="font-semibold text-primary text-xs">{iss.diagnosis_name}</p>
                                <p className="text-[11px] text-secondary font-mono">ICD-10: {iss.icd_code || 'Unspecified'}</p>
                              </div>
                              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-surface-alt text-secondary">
                                {iss.severity}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Prescriptions & WHO EML Reference Status */}
                    <div>
                      <div className="flex items-center space-x-2 mb-2">
                        <Pill className="w-4 h-4 text-accent" />
                        <h4 className="text-xs font-bold text-primary uppercase tracking-wider">
                          Prescription & Medicine Verification
                        </h4>
                      </div>
                      {!details.prescription ? (
                        <p className="text-xs text-secondary italic">No prescription issued for this encounter.</p>
                      ) : (
                        <div className="space-y-2">
                          <div className="text-xs text-secondary">
                            Prescribed by: <span className="font-semibold text-primary">{details.prescription.prescribed_by}</span> (Rx: {details.prescription.prescription_id})
                          </div>
                          <div className="overflow-x-auto">
                            <table className="w-full text-left text-xs border border-border rounded-lg overflow-hidden">
                              <thead className="bg-surface-alt text-secondary uppercase font-semibold text-[10px]">
                                <tr>
                                  <th className="px-3 py-2">Medicine Name</th>
                                  <th className="px-3 py-2">Dosage</th>
                                  <th className="px-3 py-2">Frequency</th>
                                  <th className="px-3 py-2">Duration</th>
                                  <th className="px-3 py-2">WHO EML Status</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-border">
                                {(details.prescription.medicines || []).map((m: any) => (
                                  <tr key={m.pm_id} className="hover:bg-surface-alt/40">
                                    <td className="px-3 py-2 font-semibold text-primary">
                                      {m.medicine_name}
                                      {m.generic_name && (
                                        <span className="block text-[10px] text-secondary font-normal">{m.generic_name}</span>
                                      )}
                                    </td>
                                    <td className="px-3 py-2 text-secondary">{m.dosage}</td>
                                    <td className="px-3 py-2 text-secondary">{m.frequency}</td>
                                    <td className="px-3 py-2 text-secondary">{m.duration_days} days</td>
                                    <td className="px-3 py-2">
                                      {m.reference_status === 'VERIFIED_MATCH' ? (
                                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-risk-low-bg text-risk-low">
                                          Verified Indication
                                        </span>
                                      ) : m.reference_status === 'POSSIBLE_MATCH' ? (
                                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-risk-medium-bg text-risk-medium">
                                          Class/Alias Match
                                        </span>
                                      ) : (
                                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-risk-high-bg text-risk-high">
                                          Unverified Reference
                                        </span>
                                      )}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Hospital Bill */}
                    <div>
                      <div className="flex items-center space-x-2 mb-2">
                        <Receipt className="w-4 h-4 text-accent" />
                        <h4 className="text-xs font-bold text-primary uppercase tracking-wider">
                          Hospital Billing Breakdown
                        </h4>
                      </div>
                      {!details.bill ? (
                        <p className="text-xs text-secondary italic">No billing records found for this encounter.</p>
                      ) : (
                        <div className="p-3 bg-surface border border-border rounded-lg space-y-2">
                          <div className="flex items-center justify-between border-b border-border pb-2 text-xs">
                            <span className="font-mono text-secondary">Bill ID: {details.bill.bill_id}</span>
                            <span className="font-bold text-primary text-sm">
                              Total: ₹{Number(details.bill.total_amount).toLocaleString('en-IN')}
                            </span>
                          </div>
                          <div className="space-y-1">
                            {(details.bill.itemized || []).map((item: any, idx: number) => (
                              <div key={idx} className="flex justify-between text-xs text-secondary">
                                <span>{item.description}</span>
                                <span className="font-mono">₹{Number(item.amount).toLocaleString('en-IN')}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
