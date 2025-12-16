import React, { useCallback, useRef } from 'react'

export default function Dropzone({ onFileSelect, label = "Upload Image" }) {
  // Use ref instead of fixed ID to support multiple Dropzone instances
  const fileInputRef = useRef(null)
  
  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0])
    }
  }, [onFileSelect])

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0])
    }
  }

  const handleClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  return (
    <div 
      className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer"
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      onClick={handleClick}
    >
      <input 
        type="file" 
        ref={fileInputRef}
        className="hidden" 
        accept="image/*" 
        onChange={handleChange} 
      />
      <p className="text-gray-600">{label}</p>
      <p className="text-sm text-gray-400 mt-2">Drag & drop or click to select</p>
    </div>
  )
}
