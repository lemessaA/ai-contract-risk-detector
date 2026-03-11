"""
Web Content Analyzer Component
Frontend component for analyzing legal content from websites
"""

"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Globe, 
  Search, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Shield,
  Scale,
  Eye,
  Download,
  Copy,
  ExternalLink
} from 'lucide-react';

interface WebAnalysisRequest {
  url: string;
  analysisOptions?: Record<string, any>;
}

interface WebAnalysisResult {
  analysis_id: string;
  type: string;
  web_metadata: {
    url: string;
    title: string;
    scraped_at: string;
    content_length: number;
    legal_content_detected: boolean;
  };
  contract_analysis: {
    document_parsed: any;
    clauses_extracted: any;
    risks_analyzed: any;
    compliance_checked: any;
    before_sign_report: any;
  };
  guardrail_warnings: string[];
  analysis_completed_at: string;
}

interface ContentTypeDetection {
  success: boolean;
  url: string;
  title: string;
  detected_types: string[];
  confidence_scores: Record<string, number>;
  primary_type: string | null;
  content_length: number;
  legal_content_detected: boolean;
}

export default function WebContentAnalyzer() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<WebAnalysisResult | null>(null);
  const [contentType, setContentType] = useState<ContentTypeDetection | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<string>('');

  const resetForm = () => {
    setUrl('');
    setAnalysisId(null);
    setAnalysisResult(null);
    setContentType(null);
    setError(null);
    setProgress(0);
    setStatus('');
  };

  const detectContentType = async () => {
    if (!url) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/web-content/detect-content-type', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Content type detection failed');
      }

      setContentType(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const analyzeWebContent = async () => {
    if (!url) return;

    setIsLoading(true);
    setError(null);
    setProgress(0);
    setStatus('Initializing analysis...');

    try {
      const request: WebAnalysisRequest = { url };

      const response = await fetch('/api/web-content/analyze-web-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Analysis failed');
      }

      setAnalysisId(result.analysis_id);
      
      // Start polling for results
      pollAnalysisResults(result.analysis_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsLoading(false);
    }
  };

  const pollAnalysisResults = async (id: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const statusResponse = await fetch(`/api/web-content/web-analysis/${id}/status`);
        const statusResult = await statusResponse.json();

        if (!statusResponse.ok) {
          throw new Error('Failed to get status');
        }

        setStatus(statusResult.status || 'Processing...');
        setProgress(statusResult.progress || 0);

        if (statusResult.status === 'completed') {
          clearInterval(pollInterval);
          
          // Get full results
          const resultsResponse = await fetch(`/api/web-content/web-analysis/${id}/results`);
          const results = await resultsResponse.json();

          if (resultsResponse.ok) {
            setAnalysisResult(results);
          }
          
          setIsLoading(false);
        } else if (statusResult.status === 'failed') {
          clearInterval(pollInterval);
          setError(statusResult.error || 'Analysis failed');
          setIsLoading(false);
        }
      } catch (err) {
        clearInterval(pollInterval);
        setError(err instanceof Error ? err.message : 'Analysis monitoring failed');
        setIsLoading(false);
      }
    }, 2000);

    // Stop polling after 5 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      if (isLoading) {
        setError('Analysis timed out');
        setIsLoading(false);
      }
    }, 300000);
  };

  const getRiskLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getContentTypeIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'terms_of_service':
        return <FileText className="h-4 w-4" />;
      case 'privacy_policy':
        return <Shield className="h-4 w-4" />;
      case 'cookie_policy':
        return <Globe className="h-4 w-4" />;
      case 'user_agreement':
        return <Scale className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Globe className="h-8 w-8" />
          Web Content Contract Analyzer
        </h1>
        <p className="text-gray-600">
          Analyze legal content from websites - Terms of Service, Privacy Policies, User Agreements, and more
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Website Analysis
          </CardTitle>
          <CardDescription>
            Enter a URL to analyze legal content and identify potential risks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="url">Website URL</Label>
            <div className="flex gap-2">
              <Input
                id="url"
                type="url"
                placeholder="https://example.com/terms-of-service"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isLoading}
              />
              <Button
                variant="outline"
                onClick={detectContentType}
                disabled={!url || isLoading}
              >
                <Eye className="h-4 w-4 mr-2" />
                Detect Type
              </Button>
              <Button
                onClick={analyzeWebContent}
                disabled={!url || isLoading}
              >
                {isLoading ? (
                  <>
                    <Clock className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Scale className="h-4 w-4 mr-2" />
                    Analyze
                  </>
                )}
              </Button>
            </div>
          </div>

          {contentType && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <strong>Detected Content Type:</strong>
                    <Badge variant="secondary" className="flex items-center gap-1">
                      {getContentTypeIcon(contentType.primary_type || 'unknown')}
                      {contentType.primary_type?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
                    </Badge>
                    <span className="text-sm text-gray-500">
                      ({Math.round((contentType.confidence_scores[contentType.primary_type || ''] || 0) * 100)}% confidence)
                    </span>
                  </div>
                  <div className="text-sm">
                    <strong>Title:</strong> {contentType.title}
                  </div>
                  <div className="text-sm">
                    <strong>Legal Content:</strong>{' '}
                    {contentType.legal_content_detected ? (
                      <Badge variant="default" className="ml-1">Detected</Badge>
                    ) : (
                      <Badge variant="outline" className="ml-1">Not Detected</Badge>
                    )}
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {isLoading && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{status}</span>
                <span className="text-sm text-gray-500">{progress}%</span>
              </div>
              <Progress value={progress} className="w-full" />
            </div>
          )}
        </CardContent>
      </Card>

      {analysisResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Analysis Results
            </CardTitle>
            <CardDescription>
              Contract analysis completed for {analysisResult.web_metadata.title}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="risks">Risks</TabsTrigger>
                <TabsTrigger value="compliance">Compliance</TabsTrigger>
                <TabsTrigger value="clauses">Clauses</TabsTrigger>
                <TabsTrigger value="report">Full Report</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Source Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4" />
                        <a 
                          href={analysisResult.web_metadata.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline flex items-center gap-1"
                        >
                          {analysisResult.web_metadata.url}
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                      <div>
                        <strong>Title:</strong> {analysisResult.web_metadata.title}
                      </div>
                      <div>
                        <strong>Content Length:</strong> {analysisResult.web_metadata.content_length.toLocaleString()} characters
                      </div>
                      <div>
                        <strong>Legal Content:</strong>{' '}
                        {analysisResult.web_metadata.legal_content_detected ? (
                          <Badge variant="default">Detected</Badge>
                        ) : (
                          <Badge variant="outline">Not Detected</Badge>
                        )}
                      </div>
                      <div>
                        <strong>Analyzed:</strong> {new Date(analysisResult.web_metadata.scraped_at).toLocaleString()}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Analysis Summary</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div>
                        <strong>Total Clauses:</strong>{' '}
                        {analysisResult.contract_analysis.clauses_extracted?.clauses?.length || 0}
                      </div>
                      <div>
                        <strong>Risks Found:</strong>{' '}
                        {analysisResult.contract_analysis.risks_analyzed?.risk_analyses?.length || 0}
                      </div>
                      <div>
                        <strong>Compliance Score:</strong>{' '}
                        {analysisResult.contract_analysis.compliance_checked?.compliance_score || 0}%
                      </div>
                      <div>
                        <strong>High Risk Items:</strong>{' '}
                        {
                          analysisResult.contract_analysis.risks_analyzed?.risk_analyses?.filter(
                            (risk: any) => risk.risk_level === 'High'
                          ).length || 0
                        }
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {analysisResult.guardrail_warnings.length > 0 && (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <div className="space-y-1">
                        <strong>Guardrail Warnings:</strong>
                        {analysisResult.guardrail_warnings.map((warning, index) => (
                          <div key={index} className="text-sm">• {warning}</div>
                        ))}
                      </div>
                    </AlertDescription>
                  </Alert>
                )}
              </TabsContent>

              <TabsContent value="risks" className="space-y-4">
                {analysisResult.contract_analysis.risks_analyzed?.risk_analyses?.map((risk: any, index: number) => (
                  <Card key={index}>
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold">Risk #{index + 1}</h4>
                          <Badge className={getRiskLevelColor(risk.risk_level)}>
                            {risk.risk_level}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-600">
                          <strong>Clause:</strong> {risk.clause_text?.substring(0, 200)}...
                        </div>
                        <div>
                          <strong>Explanation:</strong> {risk.risk_explanation}
                        </div>
                        {risk.suggestions && risk.suggestions.length > 0 && (
                          <div>
                            <strong>Suggestions:</strong>
                            <ul className="list-disc list-inside mt-1">
                              {risk.suggestions.map((suggestion: string, idx: number) => (
                                <li key={idx} className="text-sm">{suggestion}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>

              <TabsContent value="compliance" className="space-y-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <div>
                        <strong>Overall Compliance:</strong>{' '}
                        <Badge className={
                          analysisResult.contract_analysis.compliance_checked?.overall_compliance === 'Good'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }>
                          {analysisResult.contract_analysis.compliance_checked?.overall_compliance || 'Unknown'}
                        </Badge>
                      </div>
                      <div>
                        <strong>Compliance Score:</strong> {analysisResult.contract_analysis.compliance_checked?.compliance_score || 0}%
                      </div>
                      {analysisResult.contract_analysis.compliance_checked?.missing_clauses?.length > 0 && (
                        <div>
                          <strong>Missing Essential Clauses:</strong>
                          <ul className="list-disc list-inside mt-1">
                            {analysisResult.contract_analysis.compliance_checked.missing_clauses.map((clause: string, index: number) => (
                              <li key={index} className="text-sm text-red-600">{clause}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="clauses" className="space-y-4">
                {analysisResult.contract_analysis.clauses_extracted?.clauses?.map((clause: any, index: number) => (
                  <Card key={index}>
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold">Clause #{index + 1}</h4>
                          <div className="flex gap-2">
                            <Badge variant="outline">{clause.type}</Badge>
                            <Badge className={
                              clause.importance === 'High' 
                                ? 'bg-red-100 text-red-800' 
                                : clause.importance === 'Medium'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-green-100 text-green-800'
                            }>
                              {clause.importance}
                            </Badge>
                          </div>
                        </div>
                        <div className="text-sm">{clause.text}</div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>

              <TabsContent value="report" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Before You Sign Report</CardTitle>
                    <CardDescription>
                      Executive summary and recommendations
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">Summary</h4>
                      <p className="text-sm text-gray-600">
                        {analysisResult.contract_analysis.before_sign_report?.summary}
                      </p>
                    </div>
                    
                    {analysisResult.contract_analysis.before_sign_report?.top_risks && (
                      <div>
                        <h4 className="font-semibold mb-2">Top Risks</h4>
                        <div className="space-y-2">
                          {analysisResult.contract_analysis.before_sign_report.top_risks.map((risk: any, index: number) => (
                            <div key={index} className="border-l-4 border-red-400 pl-4">
                              <div className="font-medium">#{risk.rank} {risk.clause}</div>
                              <div className="text-sm text-gray-600">{risk.explanation}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Download Report
                      </Button>
                      <Button variant="outline" size="sm">
                        <Copy className="h-4 w-4 mr-2" />
                        Copy Summary
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
