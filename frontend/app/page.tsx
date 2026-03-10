'use client';

import { useState } from 'react';
import UploadContract from '@/components/UploadContract';
import RiskDashboard from '@/components/RiskDashboard';
import BeforeSignReport from '@/components/BeforeSignReport';
import AIChat from '@/components/AIChat';
import VersionComparison from '@/components/VersionComparison';
import DownloadableReports from '@/components/DownloadableReports';
import { 
  DocumentTextIcon, 
  ChartBarIcon, 
  ShieldCheckIcon,
  ChatBubbleLeftRightIcon,
  ArrowsRightLeftIcon,
  DocumentArrowDownIcon
} from '@heroicons/react/24/outline';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'upload' | 'dashboard' | 'report' | 'chat' | 'compare' | 'download'>('upload');
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadStart = (fileName: string) => {
    setFilename(fileName);
    setIsUploading(true);
  };

  const handleUploadComplete = (analysisId: string, fileName: string) => {
    setAnalysisId(analysisId);
    setFilename(fileName);
    setIsUploading(false);
    setActiveTab('dashboard');
  };

  const handleUploadError = (error: string) => {
    setIsUploading(false);
    alert(`Upload failed: ${error}`);
  };

  const tabs = [
    {
      id: 'upload' as const,
      name: 'Upload Contract',
      icon: DocumentTextIcon,
      description: 'Upload and analyze your contract'
    },
    {
      id: 'dashboard' as const,
      name: 'Risk Dashboard',
      icon: ChartBarIcon,
      description: 'View detailed risk analysis',
      disabled: !analysisId
    },
    {
      id: 'report' as const,
      name: 'Before Sign Report',
      icon: ShieldCheckIcon,
      description: 'Get recommendations before signing',
      disabled: !analysisId
    },
    {
      id: 'chat' as const,
      name: 'AI Chat',
      icon: ChatBubbleLeftRightIcon,
      description: 'Ask questions about your contract',
      disabled: !analysisId
    },
    {
      id: 'compare' as const,
      name: 'Version Comparison',
      icon: ArrowsRightLeftIcon,
      description: 'Compare contract versions'
    },
    {
      id: 'download' as const,
      name: 'Download Reports',
      icon: DocumentArrowDownIcon,
      description: 'Generate downloadable reports',
      disabled: !analysisId
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Contract Risk Detector</h1>
                <p className="text-sm text-gray-500">Multi-agent contract analysis system</p>
              </div>
            </div>
            
            {filename && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Current file:</span>
                <span className="text-sm font-medium text-gray-900">{filename}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => !tab.disabled && setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : tab.disabled
                      ? 'border-transparent text-gray-400 cursor-not-allowed'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors`}
                  disabled={tab.disabled}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'upload' && (
          <UploadContract
            onUploadStart={handleUploadStart}
            onUploadComplete={handleUploadComplete}
            onUploadError={handleUploadError}
            isUploading={isUploading}
          />
        )}

        {activeTab === 'dashboard' && analysisId && (
          <RiskDashboard
            analysisId={analysisId}
            isActive={activeTab === 'dashboard'}
          />
        )}

        {activeTab === 'report' && analysisId && (
          <BeforeSignReport
            analysisId={analysisId}
            isActive={activeTab === 'report'}
          />
        )}

        {activeTab === 'chat' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AIChat analysisId={analysisId || undefined} />
          </div>
        )}

        {activeTab === 'compare' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <VersionComparison />
          </div>
        )}

        {activeTab === 'download' && analysisId && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DownloadableReports analysisId={analysisId} />
          </div>
        )}

        {activeTab !== 'upload' && activeTab !== 'compare' && !analysisId && (
          <div className="text-center py-12">
            <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Contract Uploaded</h3>
            <p className="text-gray-600 mb-4">Please upload a contract to view the analysis.</p>
            <button
              onClick={() => setActiveTab('upload')}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Upload Contract
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-sm text-gray-600">
              AI Contract Risk Detector - Powered by Multi-Agent Analysis
            </p>
            <p className="text-xs text-gray-500 mt-2">
              This tool provides guidance and is not a substitute for professional legal advice.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
