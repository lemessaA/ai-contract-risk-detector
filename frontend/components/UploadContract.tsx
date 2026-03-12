import React, { useState, useCallback } from 'react';
import { 
  CloudArrowUpIcon, 
  DocumentIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  ArrowUpTrayIcon
} from '@heroicons/react/24/outline';

interface UploadContractProps {
  onUploadStart: (filename: string) => void;
  onUploadComplete: (analysisId: string, filename: string) => void;
  onUploadError: (error: string) => void;
  isUploading?: boolean;
}

const UploadContract: React.FC<UploadContractProps> = ({
  onUploadStart,
  onUploadComplete,
  onUploadError,
  isUploading = false
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (file: File) => {
    // Validate file type
    const allowedTypes = ['.pdf', '.docx', '.txt'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedTypes.includes(fileExtension)) {
      onUploadError(`File type ${fileExtension} is not supported. Please upload PDF, DOCX, or TXT files.`);
      return;
    }

    setSelectedFile(file);
    setUploadProgress(0);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      onUploadStart(selectedFile.name);
      setUploadProgress(0);
      setIsAnalyzing(true);

      const response = await fetch('/api/analyze-contract', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Upload failed');
      }

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      setUploadProgress(100);
      onUploadComplete(data.analysis_id, selectedFile.name);
      setSelectedFile(null);
      setUploadProgress(0);
      setIsAnalyzing(false);

    } catch (error) {
      console.error('Upload error:', error);
      onUploadError(error instanceof Error ? error.message : 'Upload failed');
      setUploadProgress(0);
      setIsAnalyzing(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* AI Analysis Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-3 mb-4">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full blur-lg opacity-75 animate-pulse"></div>
            <div className="relative bg-gradient-to-r from-purple-600 to-pink-600 p-3 rounded-full">
              <DocumentIcon className="h-8 w-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
            AI Contract Analysis
          </h2>
        </div>
        <p className="text-purple-200 text-lg">
          Upload your contract for comprehensive AI-powered risk analysis
        </p>
        <div className="flex items-center justify-center space-x-4 mt-2">
          <div className="flex items-center space-x-1 text-purple-300 text-sm">
            <DocumentIcon className="h-4 w-4" />
            <span>Multi-Agent Processing</span>
          </div>
          <div className="flex items-center space-x-1 text-purple-300 text-sm">
            <DocumentIcon className="h-4 w-4" />
            <span>Advanced AI Analysis</span>
          </div>
        </div>
      </div>

      {/* File Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
          dragActive
            ? 'border-purple-400 bg-purple-500/10 backdrop-blur-sm'
            : 'border-purple-300/50 hover:border-purple-400 bg-white/5 backdrop-blur-sm'
        } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {/* Animated Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-2xl opacity-50"></div>
        
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".pdf,.docx,.txt"
          onChange={handleFileInputChange}
          disabled={isUploading}
        />
        
        <div className="relative z-10">
          {isUploading ? (
            <div className="space-y-6">
              {/* AI Processing Animation */}
              <div className="flex justify-center">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full blur-lg opacity-75 animate-pulse"></div>
                  <div className="relative bg-gradient-to-r from-purple-600 to-pink-600 p-4 rounded-full">
                    <DocumentIcon className="h-12 w-12 text-white animate-spin" />
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {isAnalyzing ? 'AI Analyzing Contract...' : 'Uploading...'}
                </h3>
                <p className="text-purple-200 mb-4">
                  {isAnalyzing 
                    ? 'Our AI agents are analyzing your contract for risks and compliance issues'
                    : 'Securely uploading your contract to our AI system'
                  }
                </p>
                
                {/* Progress Bar */}
                <div className="w-full bg-purple-900/50 rounded-full h-3 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  >
                    <div className="h-full bg-white/20 rounded-full animate-pulse"></div>
                  </div>
                </div>
                
                <p className="text-purple-200 text-sm mt-2">{uploadProgress}% Complete</p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Upload Icon */}
              <div className="flex justify-center">
                <div className={`relative ${dragActive ? 'animate-bounce' : ''}`}>
                  <div className={`absolute inset-0 bg-gradient-to-r ${dragActive ? 'from-purple-400 to-pink-400' : 'from-purple-500 to-pink-500'} rounded-full blur-lg opacity-75`}></div>
                  <div className={`relative bg-gradient-to-r ${dragActive ? 'from-purple-500 to-pink-500' : 'from-purple-600 to-pink-600'} p-6 rounded-full`}>
                    <CloudArrowUpIcon className="h-16 w-16 text-white" />
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-2xl font-bold text-white mb-2">
                  {dragActive ? 'Drop your contract here' : 'Upload Contract for AI Analysis'}
                </h3>
                <p className="text-purple-200 mb-4">
                  Drag and drop your contract file, or click to browse
                </p>
                <div className="flex items-center justify-center space-x-4 text-purple-300 text-sm">
                  <span>PDF</span>
                  <span>•</span>
                  <span>DOCX</span>
                  <span>•</span>
                  <span>TXT</span>
                </div>
              </div>
              
              <label
                htmlFor="file-upload"
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg cursor-pointer hover:from-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-105"
              >
                <ArrowUpTrayIcon className="h-5 w-5" />
                <span>Choose File</span>
              </label>
            </div>
          )}
        </div>
      </div>

      {/* Selected File Info */}
      {selectedFile && !isUploading && (
        <div className="mt-6 p-4 bg-white/10 backdrop-blur-sm rounded-lg border border-purple-300/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-2 rounded-lg">
                <DocumentIcon className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-white font-medium">{selectedFile.name}</p>
                <p className="text-purple-200 text-sm">{formatFileSize(selectedFile.size)}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setSelectedFile(null)}
                className="text-purple-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-2 rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-300 transform hover:scale-105 flex items-center space-x-2"
              >
                <DocumentIcon className="h-4 w-4" />
                <span>Analyze with AI</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI Features */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-purple-300/30">
          <div className="flex items-center space-x-2 mb-2">
            <DocumentIcon className="h-6 w-6 text-purple-400" />
            <h4 className="text-white font-semibold">Risk Analysis</h4>
          </div>
          <p className="text-purple-200 text-sm">
            AI-powered identification of potential risks and liabilities
          </p>
        </div>
        
        <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-purple-300/30">
          <div className="flex items-center space-x-2 mb-2">
            <DocumentIcon className="h-6 w-6 text-purple-400" />
            <h4 className="text-white font-semibold">Compliance Check</h4>
          </div>
          <p className="text-purple-200 text-sm">
            Automated compliance verification against legal standards
          </p>
        </div>
        
        <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-purple-300/30">
          <div className="flex items-center space-x-2 mb-2">
            <DocumentIcon className="h-6 w-6 text-purple-400" />
            <h4 className="text-white font-semibold">Smart Reports</h4>
          </div>
          <p className="text-purple-200 text-sm">
            Comprehensive before-sign reports with AI insights
          </p>
        </div>
      </div>
    </div>
  );
};

export default UploadContract;
