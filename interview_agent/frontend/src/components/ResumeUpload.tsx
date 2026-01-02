import { useCallback } from 'react'

interface ResumeUploadProps {
  onFileSelect: (file: File | null) => void
  selectedFile: File | null
}

export default function ResumeUpload({ onFileSelect, selectedFile }: ResumeUploadProps) {
  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      const file = e.dataTransfer.files[0]
      if (file && file.type === 'application/pdf') {
        onFileSelect(file)
      }
    },
    [onFileSelect]
  )

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onFileSelect(file)
    }
  }

  const handleRemove = () => {
    onFileSelect(null)
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
        selectedFile ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      {selectedFile ? (
        <div className="flex items-center justify-center space-x-4">
          <div>
            <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
            <p className="text-xs text-gray-500">
              {(selectedFile.size / 1024).toFixed(1)} KB
            </p>
          </div>
          <button
            onClick={handleRemove}
            className="text-sm text-red-600 hover:text-red-500"
          >
            Remove
          </button>
        </div>
      ) : (
        <div>
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v24a4 4 0 004 4h24a4 4 0 004-4V20M36 8l-8 8m0-8v8h8"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-600">
            Drag and drop your resume (PDF) or{' '}
            <label className="text-blue-600 hover:text-blue-500 cursor-pointer">
              browse
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileInput}
                className="hidden"
              />
            </label>
          </p>
          <p className="text-xs text-gray-500 mt-1">PDF only, max 10MB</p>
        </div>
      )}
    </div>
  )
}
