import { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/layout';
import { Card, Button } from '../components/ui';
import { fetchVerification, verifyClaim, fetchClaimById } from '../services/api';
import {
  ShieldCheck,
  AlertTriangle,
  CheckCircle,
  XCircle,
  FileText,
  Building2,
  UserCheck,
  Pill,
  Receipt,
  CopyCheck,
  ArrowLeft,
  RefreshCw,
  Info
} from 'lucide-react';

interface MedicineDetail {
  medicine_name: string;
  reference_status: string;
  explanation: string;
}

interface VerificationResult {
  verification_id: string;
  claim_id: string;
  verified_at: string;
  patient_id_valid: boolean;
  hospital_match: boolean;
  encounter_exists: boolean;
  encounter_patient_match: boolean;
  encounter_hospital_match: boolean;
  prescription_match: boolean;
  medicine_details: MedicineDetail[];
  medicine_match: boolean;
  bill_match: boolean;
  duplicate_claim: boolean;
  missing_records: string[];
  discrepancies: string[];
  overall_status: 'VERIFIED' | 'REVIEW_REQUIRED' | 'INVALID_REFERENCE' | 'INCOMPLETE';
  investigator_notes: string;
}

export default function ClaimVerificationReport() {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const claimIdFromQuery = searchParams.get('claim_id');
  const claimId = id || claimIdFromQuery || '';
  const navigate = useNavigate();

  const [verification, setVerification] = useState<VerificationResult | null>(null);
  const [claim, setClaim] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async (forceReverify = false) => {
    if (!claimId) {
      setError('No Claim ID provided.');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Load claim info
      const clm = await fetchClaimById(claimId).catch(() => null);
      setClaim(clm);

      if (forceReverify) {
        setVerifying(true);
        const res = await verifyClaim(claimId);
        setVerification(res);
      } else {
        // Try to get existing verification, or run a new one if not found
        try {
          const res = await fetchVerification(claimId);
          setVerification(res);
        } catch {
          const res = await verifyClaim(claimId);
          setVerification(res);
        }
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to complete claim verification.');
    } finally {
      setLoading(false);
      setVerifying(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [claimId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <span className="w-8 h-8 rounded-full border-3 border-accent border-t-transparent animate-spin" />
        <p className="text-secondary text-sm">Evaluating 11-point provenance & clinical consistency...</p>
      </div>
    );
  }

  if (error || !verification) {
    return (
      <Card className="p-8 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-risk-medium mx-auto" />
        <h3 className="text-lg font-bold text-primary">Verification Error</h3>
        <p className="text-sm text-secondary">{error || 'Verification report unavailable.'}</p>
        <Button variant="outline" onClick={() => navigate('/claim-verification')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Verification Hub
        </Button>
      </Card>
    );
  }

  const checks = [
    {
      title: '1. Patient Record Exists',
      status: verification.patient_id_valid,
      desc: 'Patient ID exists in global Master Patient Index.',
      icon: UserCheck
    },
    {
      title: '2. Hospital Record Exists',
      status: verification.hospital_match,
      desc: 'Claimed hospital is an authentic registered facility.',
      icon: Building2
    },
    {
      title: '3. Clinical Encounter Exists',
      status: verification.encounter_exists,
      desc: 'Encounter record found in hospital EHR system.',
      icon: FileText
    },
    {
      title: '4. Patient Matches Encounter',
      status: verification.encounter_patient_match,
      desc: 'Encounter registered to the specified claimant.',
      icon: UserCheck
    },
    {
      title: '5. Hospital Matches Encounter',
      status: verification.encounter_hospital_match,
      desc: 'Encounter performed at the claimed facility.',
      icon: Building2
    },
    {
      title: '6. Prescription Exists',
      status: verification.prescription_match,
      desc: 'Physician prescription record linked to encounter.',
      icon: Pill
    },
    {
      title: '7. WHO EML Medicine Verification',
      status: verification.medicine_match,
      desc: 'Prescribed medicines conform to WHO EML approved indications.',
      icon: Pill
    },
    {
      title: '8. Billing Amount Consistency',
      status: verification.bill_match,
      desc: 'Hospital itemized bill total matches claimed amount (within 10% tolerance).',
      icon: Receipt
    },
    {
      title: '9. Duplicate Claim Check',
      status: !verification.duplicate_claim, // true if NO duplicate
      desc: verification.duplicate_claim ? 'Duplicate submission detected for same encounter!' : 'No prior claim submitted for this encounter.',
      icon: CopyCheck
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'VERIFIED':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-risk-low-bg text-risk-low border border-risk-low/30">
            <CheckCircle className="w-3.5 h-3.5 mr-1.5" />
            VERIFIED AUTHENTIC
          </span>
        );
      case 'REVIEW_REQUIRED':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-risk-medium-bg text-risk-medium border border-risk-medium/30">
            <AlertTriangle className="w-3.5 h-3.5 mr-1.5" />
            CLINICAL REVIEW REQUIRED
          </span>
        );
      case 'INVALID_REFERENCE':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-risk-high-bg text-risk-high border border-risk-high/30">
            <XCircle className="w-3.5 h-3.5 mr-1.5" />
            INVALID REFERENCE DETECTED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-surface-alt text-secondary">
            INCOMPLETE RECORDS
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Button variant="outline" className="p-2" onClick={() => navigate('/claim-verification')}>
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <PageHeader
            title="Claim Authenticity & Provenance Audit"
            subtitle={`Verification ID: ${verification.verification_id}`}
          />
        </div>

        <Button
          variant="outline"
          onClick={() => loadData(true)}
          isLoading={verifying}
          className="flex items-center space-x-2 text-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Re-verify Claim</span>
        </Button>
      </div>

      {/* Summary Card */}
      <Card className="p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-border gap-4">
          <div>
            <span className="text-xs font-semibold text-secondary uppercase tracking-wider">Target Claim</span>
            <div className="text-2xl font-bold font-mono text-accent mt-0.5">{verification.claim_id}</div>
            {claim && (
              <p className="text-xs text-secondary mt-1">
                Amount: <strong className="text-primary">₹{Number(claim.claim_amount).toLocaleString('en-IN')}</strong> ·
                Patient: <strong className="text-primary font-mono">{claim.patient_id}</strong> ·
                Insurer: <strong className="text-primary">{claim.insurer}</strong>
              </p>
            )}
          </div>

          <div className="flex flex-col items-start md:items-end space-y-1.5">
            <span className="text-xs text-secondary font-medium">Audit Outcome:</span>
            {getStatusBadge(verification.overall_status)}
            <span className="text-[11px] text-gray-400">
              Verified: {new Date(verification.verified_at).toLocaleString()}
            </span>
          </div>
        </div>

        {/* Investigator Notes */}
        <div className="mt-6 p-4 rounded-lg bg-surface-alt/50 border border-border flex items-start space-x-3">
          <Info className="w-5 h-5 text-accent shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="text-xs font-bold text-primary uppercase tracking-wider">
              Investigator Guidance & Non-Prescriptive Notice
            </span>
            <p className="text-xs text-secondary leading-relaxed">
              {verification.investigator_notes}
            </p>
          </div>
        </div>
      </Card>

      {/* Discrepancies and Missing Records */}
      {(verification.discrepancies.length > 0 || verification.missing_records.length > 0) && (
        <Card className="p-6 border-l-4 border-l-risk-medium">
          <h3 className="font-bold text-primary text-sm mb-3 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-risk-medium" />
            <span>Audit Findings & Clinical Discrepancies</span>
          </h3>

          {verification.discrepancies.length > 0 && (
            <div className="space-y-1.5 mb-4">
              <span className="text-xs font-semibold text-secondary">Specific Discrepancies:</span>
              <ul className="list-disc list-inside space-y-1 text-xs text-secondary">
                {verification.discrepancies.map((d, i) => (
                  <li key={i} className="text-risk-medium font-medium">{d}</li>
                ))}
              </ul>
            </div>
          )}

          {verification.missing_records.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-secondary">Missing EHR Records:</span>
              <div className="flex flex-wrap gap-2">
                {verification.missing_records.map((m, i) => (
                  <span key={i} className="px-2 py-0.5 rounded text-xs bg-risk-high-bg text-risk-high font-semibold">
                    {m} Missing
                  </span>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* 9-Point Verification Matrix */}
      <div className="space-y-3">
        <h3 className="font-bold text-primary text-base flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-accent" />
          <span>Multi-Point Provenance Verification Matrix</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {checks.map((chk, idx) => (
            <Card key={idx} className="p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <chk.icon className="w-4 h-4 text-accent" />
                    <span className="text-xs font-bold text-primary">{chk.title}</span>
                  </div>
                  {chk.status ? (
                    <CheckCircle className="w-4 h-4 text-risk-low" />
                  ) : (
                    <XCircle className="w-4 h-4 text-risk-high" />
                  )}
                </div>
                <p className="text-xs text-secondary mt-1">{chk.desc}</p>
              </div>

              <div className="mt-3 pt-2 border-t border-border flex items-center justify-between text-[11px]">
                <span className="text-gray-400">Status</span>
                <span className={`font-bold ${chk.status ? 'text-risk-low' : 'text-risk-high'}`}>
                  {chk.status ? 'Passed' : 'Flagged'}
                </span>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Detailed Medicine Indication Breakdown */}
      {verification.medicine_details && verification.medicine_details.length > 0 && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Pill className="w-5 h-5 text-accent" />
              <h3 className="font-bold text-primary text-sm uppercase tracking-wider">
                WHO Model List of Essential Medicines (EML) Indication Audit
              </h3>
            </div>
            <span className="text-xs text-secondary">
              Cross-checked against WHO EML 23rd Edition (2023)
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-surface-alt text-secondary uppercase font-semibold text-[10px] border-b border-border">
                <tr>
                  <th className="px-4 py-3">Medicine Name</th>
                  <th className="px-4 py-3">WHO Indication Status</th>
                  <th className="px-4 py-3">Clinical Explanation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {verification.medicine_details.map((m, idx) => (
                  <tr key={idx} className="hover:bg-surface-alt/40">
                    <td className="px-4 py-3 font-semibold text-primary">{m.medicine_name}</td>
                    <td className="px-4 py-3">
                      {m.reference_status === 'VERIFIED_MATCH' ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-risk-low-bg text-risk-low">
                          VERIFIED MATCH
                        </span>
                      ) : m.reference_status === 'POSSIBLE_MATCH' ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-risk-medium-bg text-risk-medium">
                          POSSIBLE MATCH
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-risk-high-bg text-risk-high">
                          NO VERIFIED MATCH
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-secondary leading-relaxed">{m.explanation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
