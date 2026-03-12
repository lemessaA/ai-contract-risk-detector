'use client';

import { useState, useEffect } from 'react';
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
  const [isAIProcessing, setIsAIProcessing] = useState(false);
  const [glowEffect, setGlowEffect] = useState(true);

  useEffect(() => {
    // Create pulsing glow effect
    const interval = setInterval(() => {
      setGlowEffect(prev => !prev);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleUploadStart = (fileName: string) => {
    setFilename(fileName);
    setIsUploading(true);
    setIsAIProcessing(true);
  };

  const handleUploadComplete = (analysisId: string, fileName: string) => {
    setAnalysisId(analysisId);
    setFilename(fileName);
    setIsUploading(false);
    setIsAIProcessing(false);
    setActiveTab('dashboard');
  };

  const handleUploadError = (error: string) => {
    setIsUploading(false);
    setIsAIProcessing(false);
    alert(`Upload failed: ${error}`);
  };

  const tabs = [
    {
      id: 'upload' as const,
      name: 'AI Analysis',
      icon: DocumentTextIcon,
      description: 'Upload for AI-powered contract analysis',
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      id: 'dashboard' as const,
      name: 'Risk Dashboard',
      icon: ChartBarIcon,
      description: 'View comprehensive risk analysis results',
      gradient: 'from-blue-500 to-cyan-500',
      disabled: !analysisId
    },
    {
      id: 'report' as const,
      name: 'AI Report',
      icon: DocumentTextIcon,
      description: 'Generate AI-powered before-sign report',
      gradient: 'from-green-500 to-emerald-500',
      disabled: !analysisId
    },
    {
      id: 'chat' as const,
      name: 'AI Assistant',
      icon: ChatBubbleLeftRightIcon,
      description: 'Chat with AI about your contract',
      gradient: 'from-orange-500 to-red-500'
    },
    {
      id: 'compare' as const,
      name: 'Version Compare',
      icon: ArrowsRightLeftIcon,
      description: 'Compare contract versions with AI',
      gradient: 'from-indigo-500 to-purple-500'
    },
    {
      id: 'download' as const,
      name: 'Export',
      icon: DocumentArrowDownIcon,
      description: 'Download AI-generated reports',
      gradient: 'from-gray-600 to-gray-800',
      disabled: !analysisId
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse animation-delay-4000"></div>
      </div>

      {/* Header */}
      <header className="relative border-b border-white/10 backdrop-blur-lg bg-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className={`relative ${glowEffect ? 'animate-pulse' : ''}`}>
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg blur-lg opacity-75"></div>
                <div className="relative bg-gradient-to-r from-purple-600 to-pink-600 p-2 rounded-lg">
                  <ShieldCheckIcon className="h-8 w-8 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
                  AI Contract Risk Detector
                </h1>
                <p className="text-sm text-purple-200 flex items-center space-x-1">
                  <DocumentTextIcon className="h-4 w-4" />
                  <span>Advanced multi-agent contract analysis system</span>
                </p>
              </div>
            </div>
            
            {isAIProcessing && (
              <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-purple-300 border-t-transparent"></div>
                <span className="text-sm text-purple-200">AI Processing...</span>
              </div>
            )}
            
            {filename && !isAIProcessing && (
              <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">
                <DocumentTextIcon className="h-4 w-4 text-yellow-400" />
                <span className="text-sm text-purple-200">{filename}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="relative border-b border-white/10 backdrop-blur-lg bg-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-1 overflow-x-auto" aria-label="Tabs">
            {tabs.map((tab, index) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              const isDisabled = tab.disabled;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => !isDisabled && setActiveTab(tab.id)}
                  className={`
                    relative group whitespace-nowrap py-4 px-4 font-medium text-sm
                    flex items-center space-x-2 transition-all duration-300
                    ${isActive 
                      ? 'text-white' 
                      : isDisabled
                      ? 'text-gray-500 cursor-not-allowed'
                      : 'text-purple-200 hover:text-white hover:bg-white/10'
                    }
                  `}
                  disabled={isDisabled}
                >
                  {/* Active Tab Indicator */}
                  {isActive && (
                    <div className={`absolute inset-0 bg-gradient-to-r ${tab.gradient} opacity-20 rounded-lg`}></div>
                  )}
                  
                  {/* Hover Glow Effect */}
                  {!isDisabled && !isActive && (
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  )}
                  
                  <div className="relative flex items-center space-x-2">
                    <div className={`relative ${isActive ? 'animate-pulse' : ''}`}>
                      {isActive && (
                        <div className={`absolute inset-0 bg-gradient-to-r ${tab.gradient} rounded-lg blur-md opacity-75`}></div>
                      )}
                      <Icon className={`h-5 w-5 relative ${isActive ? 'text-white' : ''}`} />
                    </div>
                    <span className="relative">{tab.name}</span>
                    {isActive && (
                      <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse"></div>
                    )}
                  </div>
                  
                  {/* Tooltip */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                    {tab.description}
                  </div>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="relative backdrop-blur-lg bg-white/5 rounded-2xl border border-white/10 shadow-2xl overflow-hidden">
          {/* Content Header */}
          <div className="relative border-b border-white/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
                  {(() => {
                    const currentTab = tabs.find(t => t.id === activeTab);
                    const Icon = currentTab?.icon;
                    return (
                      <>
                        {Icon && <Icon className="h-8 w-8 text-purple-400" />}
                        <span>{currentTab?.name}</span>
                      </>
                    );
                  })()}
                </h2>
                <p className="text-purple-200 mt-1">
                  {(() => {
                    const currentTab = tabs.find(t => t.id === activeTab);
                    return currentTab?.description;
                  })()}
                </p>
              </div>
              
              {isAIProcessing && (
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce animation-delay-200"></div>
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce animation-delay-400"></div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Content Area */}
          <div className="relative p-6">
            <div className="transform transition-all duration-500">
              {activeTab === 'upload' && (
                <div className="animate-fadeIn">
                  <UploadContract 
                    onUploadStart={handleUploadStart}
                    onUploadComplete={handleUploadComplete}
                    onUploadError={handleUploadError}
                    isUploading={isUploading}
                  />
                </div>
              )}
              
              {activeTab === 'dashboard' && (
                <div className="animate-fadeIn">
                  <RiskDashboard analysisId={analysisId!} isActive={true} />
                </div>
              )}
              
              {activeTab === 'report' && (
                <div className="animate-fadeIn">
                  <BeforeSignReport analysisId={analysisId!} />
                </div>
              )}
              
              {activeTab === 'chat' && (
                <div className="animate-fadeIn">
                  <AIChat />
                </div>
              )}
              
              {activeTab === 'compare' && (
                <div className="animate-fadeIn">
                  <VersionComparison />
                </div>
              )}
              
              {activeTab === 'download' && (
                <div className="animate-fadeIn">
                  <DownloadableReports analysisId={analysisId!} />
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative border-t border-white/10 backdrop-blur-lg bg-white/5 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <p className="text-purple-200 text-sm flex items-center justify-center space-x-2">
              <ShieldCheckIcon className="h-4 w-4" />
              <span>Powered by Advanced AI Multi-Agent System</span>
              <DocumentTextIcon className="h-4 w-4" />
            </p>
          </div>
        </div>
      </footer>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
        
        .animation-delay-200 {
          animation-delay: 200ms;
        }
        
        .animation-delay-400 {
          animation-delay: 400ms;
        }
        
        .animation-delay-2000 {
          animation-delay: 2000ms;
        }
        
        .animation-delay-4000 {
          animation-delay: 4000ms;
        }
      `}</style>
    </div>
  );
}
