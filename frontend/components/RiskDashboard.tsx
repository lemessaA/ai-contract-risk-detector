import React, { useState, useEffect } from 'react';
import {
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  ScaleIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';

interface RiskAnalysis {
  clause_id: string;
  clause_name: string;
  risk_level: 'High' | 'Medium' | 'Low';
  risk_score: number;
  explanation: string;
  suggested_alternative: string;
  key_concerns: string[];
}

interface ComplianceAnalysis {
  overall_score: number;
  compliance_grade: string;
  essential_clauses: {
    present: Array<{
      clause_type: string;
      adequacy: string;
      assessment: string;
    }>;
    missing: Array<{
      clause_type: string;
      importance: string;
      recommendation: string;
    }>;
  };
  compliance_issues: Array<{
    issue_type: string;
    severity: string;
    description: string;
    recommendation: string;
  }>;
}

interface RiskDashboardProps {
  analysisId: string;
  isActive: boolean;
}

const RiskDashboard: React.FC<RiskDashboardProps> = ({ analysisId, isActive }) => {
  const [analysisData, setAnalysisData] = useState<{
    risks: RiskAnalysis[];
    compliance: ComplianceAnalysis;
    documentInfo: any;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRisk, setSelectedRisk] = useState<RiskAnalysis | null>(null);

  useEffect(() => {
    if (isActive && analysisId) {
      fetchAnalysisData();
    }
  }, [isActive, analysisId]);

  const fetchAnalysisData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/analysis-results/${analysisId}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch analysis data');
      }

      if (data.success && data.results) {
        const risks = data.results.risks_analyzed?.analyses || [];
        const compliance = data.results.compliance_checked?.compliance_analysis || {};
        const documentInfo = data.results.document_parsed || {};

        setAnalysisData({
          risks,
          compliance,
          documentInfo
        });
      } else {
        throw new Error(data.message || 'No analysis results available');
      }
    } catch (err) {
      console.error('Error fetching analysis data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load analysis data');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'High':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'Medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'Low':
        return 'text-green-600 bg-green-50 border-green-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'High':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      case 'Medium':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />;
      case 'Low':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  const getComplianceGradeColor = (grade: string) => {
    switch (grade) {
      case 'A':
        return 'text-green-600 bg-green-100';
      case 'B':
        return 'text-blue-600 bg-blue-100';
      case 'C':
        return 'text-yellow-600 bg-yellow-100';
      case 'D':
        return 'text-orange-600 bg-orange-100';
      case 'F':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const highRiskCount = analysisData?.risks.filter(r => r.risk_level === 'High').length || 0;
  const mediumRiskCount = analysisData?.risks.filter(r => r.risk_level === 'Medium').length || 0;
  const lowRiskCount = analysisData?.risks.filter(r => r.risk_level === 'Low').length || 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading analysis results...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
          <div>
            <h3 className="text-red-800 font-medium">Error Loading Analysis</h3>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No analysis data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Clauses</p>
              <p className="text-2xl font-bold text-gray-900">{analysisData.risks.length}</p>
            </div>
            <DocumentTextIcon className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Risk</p>
              <p className="text-2xl font-bold text-red-600">{highRiskCount}</p>
            </div>
            <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Compliance Score</p>
              <p className="text-2xl font-bold text-gray-900">{analysisData.compliance.overall_score}/100</p>
            </div>
            <ScaleIcon className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Grade</p>
              <p className={`text-2xl font-bold ${getComplianceGradeColor(analysisData.compliance.compliance_grade)}`}>
                {analysisData.compliance.compliance_grade}
              </p>
            </div>
            <ShieldCheckIcon className="h-8 w-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Risk Distribution Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">High Risk</span>
              <span className="text-sm text-gray-500">{highRiskCount} clauses</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-red-600 h-3 rounded-full"
                style={{ width: `${(highRiskCount / analysisData.risks.length) * 100}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Medium Risk</span>
              <span className="text-sm text-gray-500">{mediumRiskCount} clauses</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-yellow-600 h-3 rounded-full"
                style={{ width: `${(mediumRiskCount / analysisData.risks.length) * 100}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Low Risk</span>
              <span className="text-sm text-gray-500">{lowRiskCount} clauses</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-green-600 h-3 rounded-full"
                style={{ width: `${(lowRiskCount / analysisData.risks.length) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Clauses List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Clause Analysis</h3>
        </div>
        <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
          {analysisData.risks.map((risk, index) => (
            <div
              key={risk.clause_id}
              className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => setSelectedRisk(risk)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    {getRiskIcon(risk.risk_level)}
                    <h4 className="font-medium text-gray-900">{risk.clause_name}</h4>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getRiskColor(risk.risk_level)}`}>
                      {risk.risk_level}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2 line-clamp-2">{risk.explanation}</p>
                  <div className="flex items-center space-x-4 mt-2">
                    <span className="text-xs text-gray-500">Risk Score: {risk.risk_score}/100</span>
                    {risk.key_concerns.length > 0 && (
                      <span className="text-xs text-gray-500">
                        {risk.key_concerns.length} concern(s) identified
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Detail Modal */}
      {selectedRisk && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {getRiskIcon(selectedRisk.risk_level)}
                  <h3 className="text-lg font-semibold text-gray-900">{selectedRisk.clause_name}</h3>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getRiskColor(selectedRisk.risk_level)}`}>
                    {selectedRisk.risk_level} Risk
                  </span>
                </div>
                <button
                  onClick={() => setSelectedRisk(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Risk Assessment</h4>
                  <p className="text-gray-700">{selectedRisk.explanation}</p>
                  <div className="mt-2 flex items-center space-x-4">
                    <span className="text-sm font-medium text-gray-600">Risk Score:</span>
                    <span className="text-sm font-bold text-gray-900">{selectedRisk.risk_score}/100</span>
                  </div>
                </div>

                {selectedRisk.key_concerns.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Key Concerns</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {selectedRisk.key_concerns.map((concern, index) => (
                        <li key={index} className="text-sm text-gray-700">{concern}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Suggested Alternative</h4>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-800">{selectedRisk.suggested_alternative}</p>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setSelectedRisk(null)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Compliance Summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Summary</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Essential Clauses Present</h4>
            <div className="space-y-2">
              {analysisData.compliance.essential_clauses.present.map((clause, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-600" />
                  <span className="text-sm text-gray-700">{clause.clause_type}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    clause.adequacy === 'Adequate' ? 'bg-green-100 text-green-800' :
                    clause.adequacy === 'Partial' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {clause.adequacy}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-3">Missing Essential Clauses</h4>
            <div className="space-y-2">
              {analysisData.compliance.essential_clauses.missing.map((clause, index) => (
                <div key={index} className="flex items-start space-x-2">
                  <ExclamationTriangleIcon className="h-4 w-4 text-red-600 mt-0.5" />
                  <div>
                    <span className="text-sm text-gray-700">{clause.clause_type}</span>
                    <span className={`text-xs px-2 py-1 rounded ml-2 ${
                      clause.importance === 'Critical' ? 'bg-red-100 text-red-800' :
                      clause.importance === 'Important' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {clause.importance}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskDashboard;
