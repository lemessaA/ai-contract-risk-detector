'use client'

import React, { useState } from 'react'
import { FileText, GitCompare, ArrowRight, Download, Eye } from 'lucide-react'

interface ComparisonResult {
  text_diff?: any
  ai_analysis?: any
  clause_changes?: any
  similarity_score?: number
}

interface VersionComparisonProps {
  analysisId?: string
}

export default function VersionComparison({ analysisId }: VersionComparisonProps) {
  const [originalText, setOriginalText] = useState('')
  const [modifiedText, setModifiedText] = useState('')
  const [originalFile, setOriginalFile] = useState<File | null>(null)
  const [modifiedFile, setModifiedFile] = useState<File | null>(null)
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text')

  const compareTexts = async () => {
    if (!originalText.trim() || !modifiedText.trim()) {
      alert('Please enter both original and modified text')
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch('/api/version-comparison/compare-texts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          original_text: originalText,
          modified_text: modifiedText,
          original_label: 'Original',
          modified_label: 'Modified'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setComparisonResult(data)
      } else {
        throw new Error('Comparison failed')
      }
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsLoading(false)
    }
  }

  const compareFiles = async () => {
    if (!originalFile || !modifiedFile) {
      alert('Please select both original and modified files')
      return
    }

    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('original_file', originalFile)
      formData.append('modified_file', modifiedFile)
      formData.append('original_label', 'Original')
      formData.append('modified_label', 'Modified')

      const response = await fetch('/api/version-comparison/compare-files', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        setComparisonResult(data)
      } else {
        throw new Error('File comparison failed')
      }
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsLoading(false)
    }
  }

  const downloadComparison = () => {
    if (!comparisonResult) return

    const data = JSON.stringify(comparisonResult, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'contract-comparison.json'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <GitCompare className="w-5 h-5 text-green-600" />
        <h2 className="text-xl font-semibold text-gray-800">Version Comparison</h2>
      </div>

      <div className="border-b border-gray-200 mb-4">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('text')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'text'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Text Comparison
          </button>
          <button
            onClick={() => setActiveTab('file')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'file'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            File Comparison
          </button>
        </nav>
      </div>

      <div className="flex-1 overflow-y-auto">
        {activeTab === 'text' ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Original Contract
                </label>
                <textarea
                  value={originalText}
                  onChange={(e) => setOriginalText(e.target.value)}
                  placeholder="Paste original contract text here..."
                  className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Modified Contract
                </label>
                <textarea
                  value={modifiedText}
                  onChange={(e) => setModifiedText(e.target.value)}
                  placeholder="Paste modified contract text here..."
                  className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={compareTexts}
                disabled={isLoading || !originalText.trim() || !modifiedText.trim()}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent animate-spin rounded-full"></div>
                ) : (
                  <>
                    <GitCompare className="w-4 h-4" />
                    Compare Texts
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Original File
                </label>
                <input
                  type="file"
                  accept=".txt,.pdf,.docx"
                  onChange={(e) => setOriginalFile(e.target.files?.[0] || null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {originalFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    Selected: {originalFile.name}
                  </p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Modified File
                </label>
                <input
                  type="file"
                  accept=".txt,.pdf,.docx"
                  onChange={(e) => setModifiedFile(e.target.files?.[0] || null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {modifiedFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    Selected: {modifiedFile.name}
                  </p>
                )}
              </div>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={compareFiles}
                disabled={isLoading || !originalFile || !modifiedFile}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent animate-spin rounded-full"></div>
                ) : (
                  <>
                    <GitCompare className="w-4 h-4" />
                    Compare Files
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {comparisonResult && (
          <div className="mt-6 space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-2 flex items-center gap-2">
                <Eye className="w-5 h-5" />
                Comparison Results
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {comparisonResult.similarity_score ? Math.round(comparisonResult.similarity_score * 100) : 0}%
                  </div>
                  <div className="text-sm text-gray-600">Similarity</div>
                </div>
                
                {comparisonResult.clause_changes && (
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {comparisonResult.clause_changes.total_changes || 0}
                    </div>
                    <div className="text-sm text-gray-600">Total Changes</div>
                  </div>
                )}
                
                {comparisonResult.clause_changes && (
                  <>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {comparisonResult.clause_changes.added_clauses?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Added</div>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">
                        {comparisonResult.clause_changes.removed_clauses?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Removed</div>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-600">
                        {comparisonResult.clause_changes.modified_clauses?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Modified</div>
                    </div>
                  </>
                )}
              </div>
            </div>

            {comparisonResult.ai_analysis && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-md font-semibold text-blue-800 mb-2">AI Analysis</h4>
                <div className="text-sm text-gray-700 whitespace-pre-wrap">
                  {comparisonResult.ai_analysis.ai_analysis}
                </div>
              </div>
            )}

            <div className="flex justify-center mt-4">
              <button
                onClick={downloadComparison}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                <Download className="w-4 h-4" />
                Download Comparison
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
