import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PageHeader } from '../components/layout';
import { Card, Button } from '../components/ui';
import { fetchClaims } from '../services/api';
import {
  FileCheck,
  Search,
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
  Layers
} from 'lucide-react';

interface Claim {
  claim_id: string;
  patient_id: string;
  hospital_id: string;
  encounter_id: string;
  claim_amount: number;
  submission_date: string;
  policy_number: string;
  insurer: string;
  status: string;
}

export default function ClaimVerification() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialClaimId = searchParams.get('claim_id') || '';

  const [claimIdInput, setClaimIdInput] = useState(initialClaimId);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadClaims = async () => {
      try {
        setLoading(true);
        const data = await fetchClaims().catch(() => []);
        setClaims(data || []);
      } catch (err) {
        console.error('Failed to load claims:', err);
      } finally {
        setLoading(false);
      }
    };
    loadClaims();
  }, []);

  const handleVerify = async (claimId: string) => {
    if (!claimId.trim()) {
      setError('Please enter or select a valid Claim ID.');
      return;
    }
    setError(null);
    try {
      setVerifying(true);
      navigate(`/claim-verification/${claimId.trim()}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Verification request failed.');
      setVerifying(false);
    }
  };

  const demoScenarios = [
    {
      claim_id: 'FL-CLM-000001',
      scenario: 'Clean Standard Claim',
      desc: 'All records exist and match; WHO EML indications verified. Expected: VERIFIED.',
      expected: 'VERIFIED',
      badgeColor: 'text-risk-low bg-risk-low-bg'
    },
    {
      claim_id: 'FL-CLM-000002',
      scenario: 'Duplicate Submission',
      desc: 'Second claim submitted for encounter FL-ENC-000001. Expected: INVALID_REFERENCE (duplicate).',
      expected: 'DUPLICATE',
      badgeColor: 'text-risk-high bg-risk-high-bg'
    },
    {
      claim_id: 'FL-CLM-000003',
      scenario: 'Hypertension Treatment',
      desc: 'Essential hypertension with verified Amlodipine & Losartan. Expected: VERIFIED.',
      expected: 'VERIFIED',
      badgeColor: 'text-risk-low bg-risk-low-bg'
    },
    {
      claim_id: 'FL-CLM-000004',
      scenario: 'Billing Amount Mismatch',
      desc: 'Hospital bill is ₹3,200 but claimed ₹5,500 (>10% discrepancy). Expected: REVIEW_REQUIRED.',
      expected: 'MISMATCH',
      badgeColor: 'text-risk-medium bg-risk-medium-bg'
    },
    {
      claim_id: 'FL-CLM-000005',
      scenario: 'Medicine Review Needed',
      desc: 'Dengue inpatient care with Ondansetron adjunct requiring review. Expected: REVIEW_REQUIRED.',
      expected: 'REVIEW',
      badgeColor: 'text-risk-medium bg-risk-medium-bg'
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Insurance Claim Verification"
        subtitle="Perform 11-point multi-source provenance and clinical authenticity checks."
      />

      {/* Manual Search & Launch Card */}
      <Card className="p-6 bg-surface border border-border">
        <h3 className="font-bold text-primary text-base mb-2 flex items-center space-x-2">
          <Search className="w-5 h-5 text-accent" />
          <span>Verify Any Claim ID</span>
        </h3>
        <p className="text-xs text-secondary mb-4">
          Enter an insurance claim identifier (e.g., FL-CLM-000001) to audit against hospital EHRs, doctor prescriptions, and WHO EML databases.
        </p>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleVerify(claimIdInput);
          }}
          className="flex flex-col sm:flex-row gap-3"
        >
          <div className="flex-1">
            <input
              type="text"
              placeholder="e.g. FL-CLM-000001"
              value={claimIdInput}
              onChange={(e) => setClaimIdInput(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg border border-border bg-transparent text-sm focus:outline-none focus:ring-2 focus:ring-accent font-mono"
            />
          </div>
          <Button type="submit" isLoading={verifying} className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4" />
            <span>Audit Authenticity</span>
          </Button>
        </form>

        {error && (
          <div className="mt-3 p-3 rounded-lg text-xs bg-risk-high-bg text-risk-high flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </Card>

      {/* Preset Demo Scenarios */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Layers className="w-5 h-5 text-accent" />
            <h3 className="font-bold text-primary text-base">Benchmark Verification Scenarios</h3>
          </div>
          <span className="text-xs text-secondary">Pre-configured test fixtures for demonstrative audit</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {demoScenarios.map((demo) => (
            <div
              key={demo.claim_id}
              className="p-4 rounded-lg border border-border bg-surface-alt/40 flex flex-col justify-between hover:border-accent/50 transition-colors"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-mono font-bold text-accent text-sm">{demo.claim_id}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${demo.badgeColor}`}>
                    {demo.expected}
                  </span>
                </div>
                <h4 className="font-semibold text-primary text-xs">{demo.scenario}</h4>
                <p className="text-[11px] text-secondary mt-1 leading-relaxed">{demo.desc}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-border">
                <Button
                  variant="outline"
                  className="w-full text-xs py-1.5 flex items-center justify-center space-x-1.5"
                  onClick={() => handleVerify(demo.claim_id)}
                >
                  <span>Run Provenance Audit</span>
                  <ExternalLink className="w-3 h-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Submitted Claims Table */}
      <Card className="overflow-hidden">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileCheck className="w-4 h-4 text-accent" />
            <h3 className="font-bold text-primary text-sm">All Registered Claims ({claims.length})</h3>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-alt border-b border-border uppercase font-semibold text-secondary text-[10px]">
              <tr>
                <th className="px-4 py-3">Claim ID</th>
                <th className="px-4 py-3">Patient ID</th>
                <th className="px-4 py-3">Hospital ID</th>
                <th className="px-4 py-3">Encounter ID</th>
                <th className="px-4 py-3">Amount</th>
                <th className="px-4 py-3">Insurer</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-secondary">
                    Loading claims list...
                  </td>
                </tr>
              ) : claims.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-secondary">
                    No insurance claims found in database.
                  </td>
                </tr>
              ) : (
                claims.map((c) => (
                  <tr key={c.claim_id} className="hover:bg-surface-alt/40 transition-colors">
                    <td className="px-4 py-3 font-mono font-bold text-accent">{c.claim_id}</td>
                    <td className="px-4 py-3 font-mono text-secondary">{c.patient_id}</td>
                    <td className="px-4 py-3 font-mono text-secondary">{c.hospital_id}</td>
                    <td className="px-4 py-3 font-mono text-secondary">{c.encounter_id}</td>
                    <td className="px-4 py-3 font-semibold text-primary">
                      ₹{Number(c.claim_amount).toLocaleString('en-IN')}
                    </td>
                    <td className="px-4 py-3 text-secondary">{c.insurer}</td>
                    <td className="px-4 py-3 text-right">
                      <Button
                        variant="outline"
                        className="py-1 px-2.5 text-xs"
                        onClick={() => handleVerify(c.claim_id)}
                      >
                        Verify
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
