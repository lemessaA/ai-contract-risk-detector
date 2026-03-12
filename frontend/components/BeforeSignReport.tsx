import React, { useState, useEffect } from 'react';
import {
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  ShieldCheckIcon,
  LightBulbIcon,
  DocumentTextIcon,
  ArrowDownIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

interface BeforeSignReportProps {
  analysisId: string;
  isActive: boolean;
}

const BeforeSignReport: React.FC<BeforeSignReportProps> = ({ analysisId, isActive }) => {
  const [reportData, setReportData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  useEffect(() => {
    if (isActive && analysisId) {
      fetchReportData();
    }
  }, [isActive, analysisId]);

  const fetchReportData = async () => {
    setLoading(true);
    setError(null);

    try {
      // First, try to get the report from analysis results
      const response = await fetch(`/api/analysis-results/${analysisId}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch report data');
      }

      if (data.success && data.results?.report_generated?.before_sign_report) {
        setReportData(data.results.report_generated.before_sign_report);
      } else {
        // If no report exists, try to generate it
        await generateReport();
      }
    } catch (err) {
      console.error('Error fetching report data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load report data');
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    try {
      const response = await fetch('/api/reports/generate-all-formats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          'analysis_id': analysisId,
          'base_filename': `contract-report-${analysisId}`,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate report');
      }

      // After generation, try to fetch the report again
      setTimeout(() => {
        fetchReportData();
      }, 2000);
    } catch (err) {
      console.error('Error generating report:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate report');
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

  const getActionColor = (action: string) => {
    switch (action) {
      case 'Sign':
        return 'text-green-600 bg-green-100';
      case 'Negotiate':
        return 'text-yellow-600 bg-yellow-100';
      case 'Legal Review':
        return 'text-orange-600 bg-orange-100';
      case "Don't Sign":
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getUrgencyIcon = (urgency: string) => {
    switch (urgency) {
      case 'Immediate Attention':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      case 'Recommended':
        return <LightBulbIcon className="h-5 w-5 text-yellow-600" />;
      case 'Consider':
        return <ClockIcon className="h-5 w-5 text-blue-600" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Generating your Before You Sign report...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
          <div>
            <h3 className="text-red-800 font-medium">Error Loading Report</h3>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!reportData) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 mb-6">No report data available</p>
        <button
          onClick={generateReport}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center space-x-2"
        >
          <DocumentTextIcon className="h-5 w-5" />
          <span>Generate Before-Sign Report</span>
        </button>
      </div>
    );
  }

  const executiveSummary = reportData.executive_summary || {};
  const topRisks = reportData.top_risky_clauses || [];
  const overallRecommendation = reportData.overall_recommendation || {};
  const redFlags = reportData.red_flags || [];
  const greenFlags = reportData.green_flags || [];

  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
          <h2 className="text-2xl font-bold text-white mb-2">Before You Sign Report</h2>
          <p className="text-blue-100">Critical analysis of your contract before signing</p>
        </div>

        <div className="p-6">
          {/* Overall Assessment */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(executiveSummary.overall_risk_level)}`}>
                {executiveSummary.overall_risk_level} Risk
              </div>
              <p className="text-sm text-gray-600 mt-2">Overall Risk Level</p>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{executiveSummary.risk_score}/100</div>
              <p className="text-sm text-gray-600 mt-2">Risk Score</p>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getActionColor(overallRecommendation.action)}`}>
                {overallRecommendation.action}
              </div>
              <p className="text-sm text-gray-600 mt-2">Recommended Action</p>
            </div>
          </div>

          {/* Key Takeaway */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start space-x-3">
              <LightBulbIcon className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-blue-900">Key Takeaway</h3>
                <p className="text-blue-800 text-sm mt-1">{executiveSummary.key_takeaway}</p>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <ClockIcon className="h-4 w-4" />
            <span>Recommended timeline: {overallRecommendation.timeline}</span>
          </div>
        </div>
      </div>

      {/* Top 3 Risky Clauses */}
      {topRisks.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Top Risky Clauses Requiring Attention</h3>
            <p className="text-sm text-gray-600 mt-1">The most critical issues in your contract</p>
          </div>
          
          <div className="divide-y divide-gray-200">
            {topRisks.map((risk: any, index: number) => (
              <div key={index} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center justify-center w-8 h-8 bg-red-100 text-red-600 rounded-full font-bold text-sm">
                      {risk.rank}
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{risk.clause_name}</h4>
                      <div className="flex items-center space-x-2 mt-1">
                        {getUrgencyIcon(risk.urgency)}
                        <span className="text-sm text-gray-600">{risk.urgency}</span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getRiskColor(risk.risk_level)}`}>
                          {risk.risk_level} Risk
                        </span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => setExpandedSection(expandedSection === `risk-${index}` ? null : `risk-${index}`)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    {expandedSection === `risk-${index}` ? <XMarkIcon className="h-5 w-5" /> : <ArrowDownIcon className="h-5 w-5" />}
                  </button>
                </div>

                <div className="space-y-3">
                  <div>
                    <h5 className="font-medium text-gray-900 text-sm">Problem Explained</h5>
                    <p className="text-sm text-gray-700 mt-1">{risk.problem_explained}</p>
                  </div>

                  <div>
                    <h5 className="font-medium text-gray-900 text-sm">Business Impact</h5>
                    <p className="text-sm text-gray-700 mt-1">{risk.business_impact}</p>
                  </div>

                  {expandedSection === `risk-${index}` && (
                    <div className="space-y-3 pt-3 border-t border-gray-200">
                      <div>
                        <h5 className="font-medium text-gray-900 text-sm">Suggested Fix</h5>
                        <div className="bg-green-50 border border-green-200 rounded-lg p-3 mt-1">
                          <p className="text-sm text-green-800">{risk.suggested_fix}</p>
                        </div>
                      </div>

                      <div>
                        <h5 className="font-medium text-gray-900 text-sm">Negotiation Tips</h5>
                        <p className="text-sm text-gray-700 mt-1">{risk.negotiation_tips}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Recommendations */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Quick Recommendations</h3>
          <p className="text-sm text-gray-600 mt-1">Immediate actions to consider</p>
        </div>
        
        <div className="p-6">
          <ul className="space-y-3">
            {reportData.quick_recommendations?.map((recommendation: string, index: number) => (
              <li key={index} className="flex items-start space-x-3">
                <CheckCircleIcon className="h-5 w-5 text-green-600 mt-0.5" />
                <span className="text-sm text-gray-700">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Overall Recommendation */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Overall Recommendation</h3>
        </div>
        
        <div className="p-6">
          <div className="flex items-center space-x-4 mb-4">
            <div className={`inline-flex items-center px-4 py-2 rounded-lg font-medium ${getActionColor(overallRecommendation.action)}`}>
              {overallRecommendation.action}
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <ClockIcon className="h-4 w-4" />
              <span>{overallRecommendation.timeline}</span>
            </div>
          </div>

          <p className="text-gray-700">{overallRecommendation.reasoning}</p>
        </div>
      </div>

      {/* Flags */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Red Flags */}
        {redFlags.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-red-900 flex items-center space-x-2">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
                <span>Red Flags</span>
              </h3>
            </div>
            
            <div className="p-6">
              <ul className="space-y-2">
                {redFlags.map((flag: string, index: number) => (
                  <li key={index} className="flex items-start space-x-3">
                    <ExclamationTriangleIcon className="h-4 w-4 text-red-600 mt-0.5" />
                    <span className="text-sm text-red-800">{flag}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Green Flags */}
        {greenFlags.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-green-900 flex items-center space-x-2">
                <CheckCircleIcon className="h-5 w-5 text-green-600" />
                <span>Green Flags</span>
              </h3>
            </div>
            
            <div className="p-6">
              <ul className="space-y-2">
                {greenFlags.map((flag: string, index: number) => (
                  <li key={index} className="flex items-start space-x-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-600 mt-0.5" />
                    <span className="text-sm text-green-800">{flag}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <ShieldCheckIcon className="h-5 w-5 text-yellow-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-yellow-800">Important Disclaimer</h4>
            <p className="text-yellow-700 text-sm mt-2">
              This report provides AI-powered guidance based on common contract patterns and risk factors. 
              It is not legal advice and should not replace consultation with qualified legal professionals. 
              Always consult with an attorney before signing legally binding documents.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BeforeSignReport;
