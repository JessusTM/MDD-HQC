/**
 * CIM panel that handles XML upload, example loading, and CIM metric display.
 */

import { useCallback, useEffect, useRef, useState } from "react"
import axios from "axios"
import { Upload, FileText, CheckCircle, Loader2, Trash2 } from "lucide-react"
import { uploadFile } from "../../../services/file"
import { getCimMetrics } from "../../../services/metrics"

/**
 * Displays the CIM stage and manages the source file-processing workflow.
 *
 * This component is responsible for uploading or loading the XML source model and for
 * exposing the resulting CIM metrics to the rest of the application.
 */
export const CIM = ({ onFileUploaded, onMetricsLoaded, metrics, selectedExample, onClear }) => {
  const uploadAbortRef = useRef(null)
  const metricsAbortRef = useRef(null)
  const processRunIdRef = useRef(0)
  const [file, setFile] = useState(null)
  const [errorMessage, setErrorMessage] = useState("")
  const [infoMessage, setInfoMessage] = useState("")
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)
  const processedExampleRequestRef = useRef(null)

  /**
   * Cancels the active upload and metric requests used by the CIM processing flow.
   *
   * This helper is used by the CIM component before a new upload, example load, or clear
   * action so stale responses do not overwrite the latest panel state.
   */
  const abortProcessing = useCallback(() => {
    processRunIdRef.current += 1
    uploadAbortRef.current?.abort()
    uploadAbortRef.current = null
    metricsAbortRef.current?.abort()
    metricsAbortRef.current = null
  }, [])

  /**
   * Resets the local CIM panel state and clears the parent callbacks when needed.
   *
   * This helper is used by the CIM component after failures, clears, or empty file input
   * events so the panel returns to a stable baseline state.
   */
  const reset = useCallback(({ clearError = true } = {}) => {
    setFile(null)
    if (clearError) setErrorMessage("")
    setInfoMessage("")
    setLoading(false)
    onFileUploaded?.(null)
    onMetricsLoaded?.(null)
  }, [onFileUploaded, onMetricsLoaded])

  useEffect(() => () => {
    abortProcessing()
  }, [abortProcessing])

  /**
   * Starts processing when the user selects a file from the upload input.
   *
   * This handler is used by the hidden file input because that control is the entry point
   * for the manual XML upload flow managed by this component.
   */
  const handleFile = async (event) => {
    const selected = event.target.files?.[0]

    if (!selected) {
      reset()
      return
    }

    abortProcessing()
    setFile(selected)
    setInfoMessage("Uploading file...")
    setErrorMessage("")
    setLoading(true)
    await processFile(selected)
  }

  /**
   * Uploads the selected file and then requests the CIM metrics for the saved path.
   *
   * This helper is used by both manual uploads and example loading so the CIM component
   * can reuse one processing pipeline for any source file that enters the panel.
   */
  const processFile = useCallback(async (fileToRead) => {
    const runId = ++processRunIdRef.current
    const uploadController = new AbortController()
    let metricsController = null
    uploadAbortRef.current = uploadController

    try {
      const uploadResponse = await uploadFile(fileToRead, { signal: uploadController.signal })

      if (uploadController.signal.aborted || runId !== processRunIdRef.current) {
        return
      }

      const path = uploadResponse.path
      setInfoMessage("File uploaded successfully")
      onFileUploaded?.(path)
      setInfoMessage("Calculating CIM metrics...")

      metricsController = new AbortController()
      metricsAbortRef.current = metricsController
      const metricsResponse = await getCimMetrics(path, { signal: metricsController.signal })

      if (metricsController.signal.aborted || runId !== processRunIdRef.current) {
        return
      }

      onMetricsLoaded?.(metricsResponse.metrics?.cim)
      setInfoMessage("Metrics calculated")
    } catch (error) {
      if (axios.isCancel(error) || error.code === "ERR_CANCELED") {
        return
      }

      console.error("Error processing file", error)
      setErrorMessage(error.response?.data?.detail || "Error processing file")
      setInfoMessage("")
      reset({ clearError: false })
    } finally {
      if (uploadAbortRef.current === uploadController) {
        uploadAbortRef.current = null
      }
      if (metricsAbortRef.current === metricsController) {
        metricsAbortRef.current = null
      }

      if (runId === processRunIdRef.current) {
        setLoading(false)
      }
    }
  }, [onFileUploaded, onMetricsLoaded, reset])

  /**
   * Loads the selected example file and reuses the normal CIM processing flow for it.
   *
   * This helper is used by the CIM component when the examples sidebar picks a sample,
   * so example loading behaves like a regular upload from the panel perspective.
   */
  useEffect(() => {
    const loadExample = async () => {
      if (!selectedExample?.url || !selectedExample?.requestId) return
      if (processedExampleRequestRef.current === selectedExample.requestId) return

      abortProcessing()
      processedExampleRequestRef.current = selectedExample.requestId

      try {
        setFile(null)
        setErrorMessage("")
        setInfoMessage(`Loading ${selectedExample.name}...`)
        setLoading(true)

        const response = await fetch(selectedExample.url)
        if (!response.ok) {
          throw new Error("Example file could not be loaded")
        }

        const blob = await response.blob()
        const exampleFile = new File([blob], `${selectedExample.name}.xml`, {
          type: "text/xml",
        })

        setFile(exampleFile)
        await processFile(exampleFile)
      } catch (error) {
        if (error.name === "AbortError") {
          return
        }

        console.error("Error loading example", error)
        processedExampleRequestRef.current = null
        setFile(null)
        setErrorMessage("Error loading example")
        setInfoMessage("")
        setLoading(false)
      }
    }

    loadExample()
  }, [abortProcessing, processFile, selectedExample])

  /**
   * Clears the current CIM source, local UI state, and downstream application results.
   *
   * This handler is used by the panel clear button because resetting the source CIM must
   * also invalidate every later transformation stage.
   */
  const handleClear = () => {
    abortProcessing()
    processedExampleRequestRef.current = null
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
    reset()
    onClear?.()
  }

  const hasUploadedResult = file && !errorMessage && !loading && metrics

  return (
    <div className="group flex flex-col h-full bg-ctp-surface0 rounded-xl shadow-xl border-2 border-ctp-surface2 transition-all duration-300 hover:border-ctp-surface1">
      {/* Panel header */}
      <div className="px-4 py-5 border-b border-ctp-surface1 bg-ctp-surface0/20 rounded-t-xl flex items-center justify-between shrink-0 h-20">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="p-2.5 bg-ctp-surface1 rounded-lg">
            <FileText className="w-8 h-8 text-ctp-blue" />
          </div>
          <div className="min-w-0 text-left">
            <h3 className="font-bold text-ctp-text text-2xl">CIM</h3>
            <p className="text-lg text-[#a0988c] font-semibold hidden xl:block">
              i* 2.0 (iStar)
            </p>
          </div>
        </div>

        {file && !errorMessage && (
          <div className="flex items-center gap-2 shrink-0">
            <span className="px-4 py-1.5 border text-base font-semibold rounded-full flex items-center gap-2 shadow-sm shrink-0 bg-[#a6e3a1]/20 border-[#a6e3a1]/30 text-[#a6e3a1]">
              <CheckCircle className="h-4.5 w-4.5" /> Ready
            </span>
            <button
              type="button"
              onClick={handleClear}
              className="rounded-lg border border-ctp-surface0 bg-ctp-crust p-2.5 text-ctp-overlay1 shadow-sm transition-all hover:border-ctp-red/30 hover:bg-ctp-red/20 hover:text-ctp-red"
              title="Clear CIM and downstream results"
              aria-label="Clear CIM and downstream results"
            >
              <Trash2 className="h-4.5 w-4.5" />
            </button>
          </div>
        )}
      </div>

      {/* Upload state */}
      <div className="flex-1 p-0 overflow-hidden flex flex-col relative bg-ctp-crust">
        <div className="flex-1 flex flex-col items-center justify-center m-6 py-10 rounded-lg bg-ctp-mantle/50">
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept=".xml"
            onChange={handleFile}
          />

          {hasUploadedResult ? (
            <>
              {/* Success state */}
              <div className="flex flex-col items-center justify-center px-6 text-center">
              <div className="mb-2 rounded-full bg-ctp-green/10 p-3 text-ctp-green">
                <CheckCircle className="h-14 w-14" />
              </div>
              <h4 className="text-3xl font-bold uppercase tracking-[0.16em] text-ctp-green">
                Archivo Subido
              </h4>
              <p className="mt-2 max-w-[240px] truncate text-center font-mono text-2xl text-ctp-text" title={file.name}>
                {file.name}
              </p>
              <p className="mt-2 text-lg font-semibold text-ctp-green/90">
                Metrics calculated
              </p>
              </div>
            </>
          ) : (
            <>
              {/* Upload prompt */}
              <p className="text-[#a0988c] text-xl mb-6 text-center px-6 font-semibold">
                Upload your i* 2.0 (XML) file here...
              </p>

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-3 px-6 py-3 bg-ctp-mauve hover:bg-ctp-pink text-ctp-base rounded-lg font-bold transition-all hover:scale-105 active:scale-95 shadow-lg shadow-ctp-mauve/20 text-base"
              >
                <Upload className="w-5 h-5" />
                Upload File
              </button>

              <div className="mt-4 text-sm">
                {file && !errorMessage && !infoMessage && (
                  <span className="text-[#a0988c]">{file.name}</span>
                )}

                {infoMessage && (
                  <span className="text-ctp-green">{infoMessage}</span>
                )}

                {errorMessage && (
                  <span className="text-ctp-red">{errorMessage}</span>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Metrics area */}
      <div className="shrink-0 bg-ctp-mantle border-t border-ctp-surface0/50 p-4">
        <div className="min-h-[104px] rounded-lg bg-ctp-mantle/40 p-4 overflow-y-auto max-h-[300px]">
          {loading ? (
            <>
              {/* Loading metrics */}
              <div className="flex items-center justify-center gap-2 text-[#a0988c]">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-sm font-semibold">Calculating metrics...</span>
              </div>
            </>
          ) : metrics ? (
            <>
              {/* Metrics content */}
              <div className="space-y-2">
              <h4 className="text-ctp-text font-bold text-sm mb-3">CIM Metrics</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-[#a0988c]">Goals:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.goals || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-[#a0988c]">Tasks:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.tasks || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-[#a0988c]">Softgoals:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.softgoals || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-[#a0988c]">Resources:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.resources || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-[#a0988c]">Actors:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.actors || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-[#a0988c]">Agents:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.agents || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-[#a0988c]">Roles:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.roles || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-[#a0988c]">Dependencies:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.social_dependencies || 0}</span>
                </div>
                {metrics.internal_links && (
                  <>
                    <div className="bg-ctp-surface0/50 p-2 rounded">
                      <span className="text-[#a0988c]">Needed-by:</span>
                      <span className="text-ctp-text font-semibold ml-2">{metrics.internal_links.needed_by || 0}</span>
                    </div>
                    <div className="bg-ctp-surface0/50 p-2 rounded">
                      <span className="text-[#a0988c]">Qualification:</span>
                      <span className="text-ctp-text font-semibold ml-2">{metrics.internal_links.qualification_links || 0}</span>
                    </div>
                    <div className="bg-ctp-surface0/50 p-2 rounded">
                      <span className="text-[#a0988c]">Contributions:</span>
                      <span className="text-ctp-text font-semibold ml-2">{metrics.internal_links.contributions || 0}</span>
                    </div>
                  </>
                )}
                {metrics.refinements && (
                  <>
                    <div className="bg-ctp-surface0/50 p-2 rounded">
                      <span className="text-[#a0988c]">Refinements AND:</span>
                      <span className="text-ctp-text font-semibold ml-2">{metrics.refinements.and || 0}</span>
                    </div>
                    <div className="bg-ctp-surface0/50 p-2 rounded">
                      <span className="text-[#a0988c]">Refinements OR:</span>
                      <span className="text-ctp-text font-semibold ml-2">{metrics.refinements.or || 0}</span>
                    </div>
                  </>
                )}
                {metrics.total_nodes !== undefined && (
                  <div className="bg-ctp-surface0/50 p-2 rounded col-span-2">
                    <span className="text-[#a0988c]">Total nodes:</span>
                    <span className="text-ctp-text font-semibold ml-2">{metrics.total_nodes}</span>
                  </div>
                )}
              </div>
              </div>
            </>
          ) : (
            <div className="min-h-[72px] border border-dashed border-ctp-overlay0/30 rounded-lg flex items-center justify-center px-4 bg-ctp-mantle/10">
              <span className="text-[#a0988c] text-xl font-semibold italic">
                No metrics available
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
