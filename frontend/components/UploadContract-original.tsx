import React, { useState, useCallback } from 'react';
import { CloudArrowUpIcon, DocumentIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

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

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024; // 10MB in bytes
    if (file.size > maxSize) {
      onUploadError('File size exceeds 10MB limit. Please upload a smaller file.');
      return;
    }

    setSelectedFile(file);
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

      const response = await fetch('/api/analyze-contract', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Upload failed');
      }

      setUploadProgress(100);
      onUploadComplete(data.analysis_id, selectedFile.name);
      setSelectedFile(null);
      setUploadProgress(0);

    } catch (error) {
      console.error('Upload error:', error);
      onUploadError(error instanceof Error ? error.message : 'Upload failed');
      setUploadProgress(0);
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
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Upload Contract for Analysis
        </h2>

        {/* File Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-upload"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            onChange={handleFileInputChange}
            accept=".pdf,.docx,.txt"
            disabled={isUploading}
          />

          <div className="flex flex-col items-center space-y-4">
            <CloudArrowUpIcon className="h-12 w-12 text-gray-400" />
            
            <div>
              <p className="text-lg font-medium text-gray-900">
                {dragActive ? 'Drop your file here' : 'Drag and drop your contract here'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                or click to browse
              </p>
            </div>

            <div className="text-xs text-gray-400">
              Supported formats: PDF, DOCX, TXT (Max 10MB)
            </div>
          </div>
        </div>

        {/* Selected File Info */}
        {selectedFile && !isUploading && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <DocumentIcon className="h-8 w-8 text-blue-500" />
                <div>
                  <p className="font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-red-500 hover:text-red-700 text-sm font-medium"
              >
                Remove
              </button>
            </div>

            <button
              onClick={handleUpload}
              className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors font-medium"
            >
              Start Analysis
            </button>
          </div>
        )}

        {/* Upload Progress */}
        {isUploading && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Uploading and analyzing...</span>
              <span className="text-sm text-gray-500">{uploadProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2 text-center">
              This may take 5-10 minutes. We'll notify you when it's complete.
            </p>
          </div>
        )}

        {/* Features */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <CheckCircleIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <h3 className="font-medium text-gray-900">Multi-Agent Analysis</h3>
            <p className="text-sm text-gray-600 mt-1">
              5 AI agents analyze your contract comprehensively
            </p>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <CheckCircleIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <h3 className="font-medium text-gray-900">Risk Detection</h3>
            <p className="text-sm text-gray-600 mt-1">
              Identify legal risks before you sign
            </p>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <CheckCircleIcon className="h-8 w-8 text-purple-600 mx-auto mb-2" />
            <h3 className="font-medium text-gray-900">Compliance Check</h3>
            <p className="text-sm text-gray-600 mt-1">
              Ensure essential clauses are included
            </p>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-yellow-800">Before You Upload</h4>
              <ul className="text-sm text-yellow-700 mt-2 space-y-1">
                <li>• Ensure your contract is complete and readable</li>
                <li>• Remove any sensitive personal information</li>
                <li>• This tool provides guidance, not legal advice</li>
                <li>• Always consult with a qualified attorney for legal matters</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadContract;
