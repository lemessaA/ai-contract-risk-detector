'use client'

import React, { useState } from 'react'
import { Download, FileText, File, Image, FileCode } from 'lucide-react'

interface ReportFormat {
  name: string
  description: string
  available: boolean
  mime_type: string
}

interface DownloadableReportsProps {
  analysisId: string
}

export default function DownloadableReports({ analysisId }: DownloadableReportsProps) {
  const [availableFormats, setAvailableFormats] = useState<ReportFormat[]>([])
  const [selectedFormats, setSelectedFormats] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedReports, setGeneratedReports] = useState<any>({})

  React.useEffect(() => {
    fetchAvailableFormats()
  }, [])

  const fetchAvailableFormats = async () => {
    try {
      const response = await fetch('/api/reports/available-formats')
      if (response.ok) {
        const data = await response.json()
        setAvailableFormats(data.formats || [])
      }
    } catch (error) {
      console.error('Failed to fetch formats:', error)
    }
  }

  const generateReport = async (format: string) => {
    setIsGenerating(true)
    try {
      const response = await fetch(`/api/reports/generate-${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          analysis_id: analysisId,
          filename: `contract-analysis.${format}`
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setGeneratedReports(prev => ({
            ...prev,
            [format]: data
          }))
        } else {
          alert(`Error generating ${format.toUpperCase()}: ${data.error}`)
        }
      } else {
        throw new Error(`Failed to generate ${format} report`)
      }
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsGenerating(false)
    }
  }

  const generateAllFormats = async () => {
    setIsGenerating(true)
    try {
      const response = await fetch('/api/reports/generate-all-formats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          analysis_id: analysisId,
          base_filename: 'contract-analysis'
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setGeneratedReports(data.reports || {})
        } else {
          alert(`Error generating reports: ${data.error}`)
        }
      } else {
        throw new Error('Failed to generate reports')
      }
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadReport = (format: string) => {
    const report = generatedReports[format]
    if (!report || !report.success) {
      alert(`No ${format} report available for download`)
      return
    }

    try {
      const binaryString = atob(report.content_base64)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }

      const blob = new Blob([bytes], { type: report.mime_type })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = report.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      alert(`Download failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const toggleFormat = (format: string) => {
    setSelectedFormats(prev => 
      prev.includes(format) 
        ? prev.filter(f => f !== format)
        : [...prev, format]
    )
  }

  const getFormatIcon = (format: string) => {
    switch (format.toLowerCase()) {
      case 'pdf':
        return <FileText className="w-4 h-4" />
      case 'html':
        return <FileCode className="w-4 h-4" />
      case 'json':
        return <File className="w-4 h-4" />
      case 'word':
        return <File className="w-4 h-4" />
      default:
        return <File className="w-4 h-4" />
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <Download className="w-5 h-5 text-green-600" />
        <h2 className="text-xl font-semibold text-gray-800">Downloadable Reports</h2>
      </div>

      <div className="flex-1 overflow-y-auto space-y-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Available Formats</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {availableFormats.map((format) => (
              <div
                key={format.name}
                className={`relative rounded-lg border-2 p-3 cursor-pointer transition-colors ${
                  selectedFormats.includes(format.name)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                } ${!format.available ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={() => format.available && toggleFormat(format.name)}
              >
                <div className="flex flex-col items-center space-y-2">
                  <div className={`p-2 rounded-full ${
                    format.available ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
                  }`}>
                    {getFormatIcon(format.name)}
                  </div>
                  
                  <div className="text-center">
                    <div className="font-medium text-sm">{format.name}</div>
                    <div className="text-xs text-gray-500">{format.description}</div>
                  </div>
                  
                  {!format.available && (
                    <div className="text-xs text-red-600 font-medium">Coming Soon</div>
                  )}
                </div>
                
                {selectedFormats.includes(format.name) && (
                  <div className="absolute top-1 right-1 w-4 h-4 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs">✓</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={generateAllFormats}
            disabled={isGenerating || selectedFormats.length === 0}
            className="flex-1 sm:flex-initial items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent animate-spin rounded-full"></div>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Generate Selected
              </>
            )}
          </button>
          
          <div className="text-sm text-gray-600 text-center">
            {selectedFormats.length} format{selectedFormats.length !== 1 ? 's' : ''} selected
          </div>
        </div>

        {Object.keys(generatedReports).length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-green-800 mb-4 flex items-center gap-2">
              <Image className="w-5 h-5" />
              Generated Reports
            </h3>
            
            <div className="space-y-3">
              {Object.entries(generatedReports).map(([format, report]: [string, any]) => (
                <div key={format} className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-full ${
                      report.success ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                    }`}>
                      {getFormatIcon(format)}
                    </div>
                    
                    <div>
                      <div className="font-medium text-sm">{format.toUpperCase()}</div>
                      <div className="text-xs text-gray-500">
                        {report.success ? `${report.size_bytes} bytes` : 'Failed'}
                      </div>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => downloadReport(format)}
                    disabled={!report.success}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      report.success
                        ? 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                        : 'bg-gray-300 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-md font-semibold text-blue-800 mb-2">Format Information</h3>
          <div className="text-sm text-gray-700 space-y-2">
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-1"></div>
              <div>
                <div className="font-medium">PDF</div>
                <div className="text-gray-600">Best for printing and sharing. Maintains formatting across all devices.</div>
              </div>
            </div>
            
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-1"></div>
              <div>
                <div className="font-medium">HTML</div>
                <div className="text-gray-600">Interactive web format. Viewable in any browser with clickable links.</div>
              </div>
            </div>
            
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-1"></div>
              <div>
                <div className="font-medium">JSON</div>
                <div className="text-gray-600">Data format for integration with other systems and analysis.</div>
              </div>
            </div>
            
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-blue-600 rounded-full mt-1"></div>
              <div>
                <div className="font-medium">RTF</div>
                <div className="text-gray-600">Word-compatible format. Basic formatting support.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
