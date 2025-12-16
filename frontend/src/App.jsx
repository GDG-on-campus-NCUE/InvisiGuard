import { useState, useEffect } from 'react'
import api from './services/api'
import Dropzone from './components/Dropzone'
import ConfigPanel from './components/ConfigPanel'
import ComparisonView from './components/ComparisonView'
import AttackSimulator from './components/AttackSimulator'
import VerifyTab from './components/VerifyTab'
import { validateEmbedRequest } from './utils/validation'

function App() {
    const [health, setHealth] = useState(null)
    const [activeTab, setActiveTab] = useState('embed')

    // Embed State
    const [file, setFile] = useState(null)
    const [text, setText] = useState('')
    const [alpha, setAlpha] = useState(1.0)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [originalPreview, setOriginalPreview] = useState(null)

    // Extract State
    const [extractOriginal, setExtractOriginal] = useState(null)
    const [extractSuspect, setExtractSuspect] = useState(null)
    const [extractResult, setExtractResult] = useState(null)
    const [extractOriginalPreview, setExtractOriginalPreview] = useState(null)
    const [extractSuspectPreview, setExtractSuspectPreview] = useState(null)

    const handleExtractOriginalSelect = (selectedFile) => {
        setExtractOriginal(selectedFile)
        setExtractOriginalPreview(URL.createObjectURL(selectedFile))
        console.log('[Extract] Original file selected:', selectedFile.name)
    }

    const handleExtractSuspectSelect = (selectedFile) => {
        setExtractSuspect(selectedFile)
        setExtractSuspectPreview(URL.createObjectURL(selectedFile))
        console.log('[Extract] Suspect file selected:', selectedFile.name)
    }

    useEffect(() => {
        api.get('/health')
            .then(res => setHealth(res.data))
            .catch(err => console.error(err))
    }, [])

    const handleEmbedFileSelect = (selectedFile) => {
        setFile(selectedFile)
        setOriginalPreview(URL.createObjectURL(selectedFile))
        setResult(null)
        // Removed auto-set of extractOriginal to prevent state conflict
    }

    const handleEmbed = async () => {
        // T013-T016: Client-side validation
        const validation = validateEmbedRequest(file, text, alpha)
        if (!validation.valid) {
            // T017: Improved error message display
            const errorMessage = validation.errors.join('\n')
            alert(`❌ Validation Error\n\n${errorMessage}`)
            return
        }

        setLoading(true)
        const formData = new FormData()
        formData.append('file', file)
        formData.append('text', text.trim())
        formData.append('alpha', alpha)

        try {
            // T012: Remove manual Content-Type header - let browser set it automatically
            const res = await api.post('/embed', formData)
            setResult(res.data.data)
        } catch (err) {
            console.error(err)
            // T017: Improved error message display with server error details
            if (err.response?.data?.message) {
                const errorData = err.response.data
                const errorMessage = `❌ ${errorData.message}\n\n${errorData.suggestion || 'Please try again.'}`
                alert(errorMessage)
            } else {
                alert('❌ Error embedding watermark. Please check the console for details.')
            }
        } finally {
            setLoading(false)
        }
    }

    const handleExtract = async () => {
        if (!extractOriginal || !extractSuspect) return

        setLoading(true)
        const formData = new FormData()
        formData.append('original_file', extractOriginal)
        formData.append('suspect_file', extractSuspect)

        try {
            const res = await api.post('/extract', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            setExtractResult(res.data.data)
        } catch (err) {
            console.error(err)
            alert('Extraction failed')
        } finally {
            setLoading(false)
        }
    }

    const handleDownloadResult = async () => {
        if (!result || !result.image_url) return

        setLoading(true)
        try {
            const resp = await fetch(result.image_url)
            if (!resp.ok) throw new Error('Download failed')
            const blob = await resp.blob()
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = 'watermarked_image.png'
            document.body.appendChild(a)
            a.click()
            a.remove()
            URL.revokeObjectURL(url)
        } catch (err) {
            console.error(err)
            alert('Download failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-6xl mx-auto space-y-8">
                <header className="flex justify-between items-center">
                    <h1 className="text-3xl font-bold text-gray-900">InvisiGuard</h1>
                    <div className="flex items-center gap-4">
                        <div className="space-x-2">
                            <button
                                onClick={() => setActiveTab('embed')}
                                className={`px-4 py-2 rounded ${activeTab === 'embed' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                            >
                                Embed Watermark
                            </button>
                            <button
                                onClick={() => setActiveTab('extract')}
                                className={`px-4 py-2 rounded ${activeTab === 'extract' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                            >
                                Extract (With Original)
                            </button>
                            <button
                                onClick={() => setActiveTab('verify')}
                                className={`px-4 py-2 rounded ${activeTab === 'verify' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                            >
                                Verify (Blind)
                            </button>
                        </div>
                        <div className="text-sm">
                            {health ? (
                                <span className="text-green-600 font-medium">● System Online</span>
                            ) : (
                                <span className="text-red-500">● Connecting...</span>
                            )}
                        </div>
                    </div>
                </header>

                {activeTab === 'embed' && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Left Column: Controls */}
                        <div className="space-y-6">
                            <section className="bg-white p-6 rounded-lg shadow-md">
                                <h2 className="text-xl font-semibold mb-4">1. Upload Image</h2>
                                <Dropzone onFileSelect={handleEmbedFileSelect} label={file ? file.name : "Upload Image"} />
                            </section>

                            <section>
                                <ConfigPanel
                                    text={text}
                                    setText={setText}
                                    alpha={alpha}
                                    setAlpha={setAlpha}
                                    onEmbed={handleEmbed}
                                    loading={loading}
                                />
                            </section>
                        </div>

                        {/* Right Column: Preview & Results */}
                        <div className="lg:col-span-2 space-y-6">
                            {originalPreview && !result && (
                                <div className="bg-white p-6 rounded-lg shadow-md">
                                    <h2 className="text-xl font-semibold mb-4">Preview</h2>
                                    <img src={originalPreview} alt="Preview" className="max-h-[500px] mx-auto rounded" />
                                </div>
                            )}

                            {result && (
                                <div className="space-y-6">
                                    {/* PNG Format Warning */}
                                    <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-300">
                                        <h3 className="text-sm font-semibold text-yellow-900 mb-2 flex items-center gap-2">
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                                            </svg>
                                            重要提示：請保持 PNG 格式
                                        </h3>
                                        <p className="text-sm text-yellow-800">
                                            浮水印圖片已保存為 <strong>PNG 格式</strong>（無損壓縮）。<strong className="text-red-600">請勿轉換為 JPG</strong>，否則會因有損壓縮而破壞浮水印，導致無法提取！
                                        </p>
                                    </div>
                                    
                                    <div className="bg-white p-6 rounded-lg shadow-md">
                                        <h2 className="text-xl font-semibold mb-4">Result Analysis</h2>
                                        <ComparisonView
                                            originalUrl={originalPreview}
                                            processedUrl={result.image_url}
                                            signalMapUrl={result.signal_map_url ? result.signal_map_url : null}
                                            metrics={{ psnr: result.psnr, ssim: result.ssim }}
                                        />
                                        <div className="mt-4 flex justify-end">
                                            <button
                                                onClick={handleDownloadResult}
                                                disabled={loading}
                                                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 inline-flex items-center gap-2 disabled:opacity-50"
                                            >
                                                <span>Download PNG Image</span>
                                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
                {activeTab === 'extract' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div className="space-y-6">
                            {/* T022: Helper text explaining Original vs Suspect */}
                            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 text-blue-800 text-sm">
                                <strong>⚠️ Important - Upload Order:</strong>
                                <ul className="mt-2 space-y-1 list-disc list-inside">
                                    <li><strong>Original Image:</strong> The <u>ORIGINAL unwatermarked</u> image (before embedding)</li>
                                    <li><strong>Suspect Image:</strong> The <u>WATERMARKED</u> image (after embedding, downloaded from Embed tab)</li>
                                    <li>We compare both images to extract the hidden watermark</li>
                                </ul>
                                <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-yellow-800 text-xs">
                                    💡 <strong>Tip:</strong> If extraction fails, make sure you didn't swap the images!
                                </div>
                            </div>
                            
                            <section className="bg-white p-6 rounded-lg shadow-md">
                                <h2 className="text-xl font-semibold mb-4 flex items-center justify-between">
                                    <span>1. Original Image</span>
                                    {/* T021: Success checkmark when file uploaded */}
                                    {extractOriginal && <span className="text-green-600 text-sm">✓ Uploaded</span>}
                                </h2>
                                <Dropzone
                                    onFileSelect={handleExtractOriginalSelect}
                                    label={extractOriginal ? extractOriginal.name : "Upload Original"}
                                />
                                {/* T020: Filename display */}
                                {extractOriginal && (
                                    <div className="mt-2 text-sm text-gray-600">
                                        📄 {extractOriginal.name} ({(extractOriginal.size / 1024).toFixed(1)} KB)
                                    </div>
                                )}
                                {/* T018: File preview for extractOriginal */}
                                {extractOriginalPreview && (
                                    <div className="mt-4">
                                        <img 
                                            src={extractOriginalPreview} 
                                            alt="Original preview" 
                                            className="max-h-48 mx-auto rounded border border-gray-200" 
                                        />
                                    </div>
                                )}
                            </section>
                            
                            <section className="bg-white p-6 rounded-lg shadow-md">
                                <h2 className="text-xl font-semibold mb-4 flex items-center justify-between">
                                    <span>2. Suspect Image</span>
                                    {/* T021: Success checkmark when file uploaded */}
                                    {extractSuspect && <span className="text-green-600 text-sm">✓ Uploaded</span>}
                                </h2>
                                <Dropzone
                                    onFileSelect={handleExtractSuspectSelect}
                                    label={extractSuspect ? extractSuspect.name : "Upload Suspect"}
                                />
                                {/* T020: Filename display */}
                                {extractSuspect && (
                                    <div className="mt-2 text-sm text-gray-600">
                                        📄 {extractSuspect.name} ({(extractSuspect.size / 1024).toFixed(1)} KB)
                                    </div>
                                )}
                                {/* T019: File preview for extractSuspect */}
                                {extractSuspectPreview && (
                                    <div className="mt-4">
                                        <img 
                                            src={extractSuspectPreview} 
                                            alt="Suspect preview" 
                                            className="max-h-48 mx-auto rounded border border-gray-200" 
                                        />
                                    </div>
                                )}
                            </section>
                            
                            {/* T023: Disable button when files missing, show validation message */}
                            {(!extractOriginal || !extractSuspect) && (
                                <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200 text-yellow-800 text-sm">
                                    ⚠️ Please upload both images to continue
                                </div>
                            )}
                            
                            <button
                                onClick={handleExtract}
                                disabled={loading || !extractOriginal || !extractSuspect}
                                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? "Extracting..." : "Extract Watermark"}
                            </button>
                        </div>

                        <div className="space-y-6">
                            {extractResult && (
                                <div className="bg-white p-6 rounded-lg shadow-md">
                                    <h2 className="text-xl font-semibold mb-4">Extraction Result</h2>
                                    <div className="space-y-4">
                                        <div className="p-4 bg-gray-50 rounded border">
                                            <div className="text-sm text-gray-500">Decoded Text</div>
                                            <div className="text-2xl font-mono font-bold text-blue-600 break-all">
                                                {extractResult.decoded_text || "<No text found>"}
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="p-3 bg-gray-50 rounded border">
                                                <div className="text-xs text-gray-500">Status</div>
                                                <div className="font-medium">
                                                    {extractResult.debug_info?.status === 'aligned' ? '✅ Aligned' : '⚠️ Alignment Failed'}
                                                </div>
                                            </div>
                                            <div className="p-3 bg-gray-50 rounded border">
                                                <div className="text-xs text-gray-500">Confidence</div>
                                                <div className="font-medium">{(extractResult.confidence * 100).toFixed(0)}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
                {activeTab === 'verify' && <VerifyTab />}
            </div>
        </div>
    )
}

export default App
