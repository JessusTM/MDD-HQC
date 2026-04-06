/**
 * Main application container that coordinates the CIM, PIM, and PSM frontend flow.
 */

import { useCallback, useEffect, useRef, useState } from "react"
import axios from "axios"
import { Loader2, TriangleAlert } from "lucide-react"
import { CIM } from "./Levels/CIM"
import { PIM } from "./Levels/PIM"
import { PSM } from "./Levels/PSM"
import { Filter } from "./Filter/Filter"
import { Header } from "./Commons/Header"
import { ExamplesSidebar } from "./Examples/ExamplesSidebar"
import QuestionsModal from "./Questions/Questions_modal"
import GuidedQuestionsModal from "./Questions/GuidedQuestionsModal"
import { transformCimToPim } from "../services/transformations"
import { fetchQuestions } from "../services/questions"

/**
 * Orchestrates uploads, guided interaction, and transformation results across the app.
 *
 * This component owns the shared state used by the level panels, the filter controls,
 * and the interaction modals so the full frontend flow stays synchronized.
 */
export const App = () => {
  const questionsAbortRef = useRef(null)
  const transformAbortRef = useRef(null)
  const interactionRunIdRef = useRef(0)
  const [isAiEnabled, setIsAiEnabled] = useState(true)
  const [uploadedFilePath, setUploadedFilePath] = useState(null)
  const [cimMetrics, setCimMetrics] = useState(null)
  const [pimMetrics, setPimMetrics] = useState(null)
  const [psmMetrics, setPsmMetrics] = useState(null)
  const [uvlContent, setUvlContent] = useState(null)
  const [pumlContent, setPumlContent] = useState(null)
  const [isExamplesOpen, setIsExamplesOpen] = useState(false)
  const [selectedExample, setSelectedExample] = useState(null)
  const [isQuestionsModalOpen, setIsQuestionsModalOpen] = useState(false)
  const [questions, setQuestions] = useState([])
  const [questionsStatus, setQuestionsStatus] = useState("idle")
  const [questionsError, setQuestionsError] = useState("")

  /**
   * Resets the guided-interaction state used by the application and modal flow.
   *
   * This helper is used by the main app whenever a new upload, example selection, or
   * mode change should discard stale questions, errors, and modal visibility.
   */
  const resetInteractionState = useCallback(() => {
    setQuestions([])
    setQuestionsStatus("idle")
    setQuestionsError("")
    setIsQuestionsModalOpen(false)
  }, [])

  /**
   * Cancels the active interaction-related requests tracked by the application.
   *
   * This helper is used by the main app before starting a new interaction or
   * transformation run so older responses cannot overwrite the latest shared state.
   */
  const abortInteractionRequests = useCallback(() => {
    interactionRunIdRef.current += 1
    questionsAbortRef.current?.abort()
    questionsAbortRef.current = null
    transformAbortRef.current?.abort()
    transformAbortRef.current = null
  }, [])

  useEffect(() => {
    const handlePageHide = () => {
      abortInteractionRequests()
    }

    window.addEventListener("pagehide", handlePageHide)

    return () => {
      window.removeEventListener("pagehide", handlePageHide)
      abortInteractionRequests()
    }
  }, [abortInteractionRequests])

  /**
   * Stores the uploaded file path and clears downstream results tied to the previous run.
   *
   * This handler is used by the CIM panel after a successful upload so the rest of the
   * application can start a fresh transformation flow from the new source file.
   */
  const handleFileUploaded = useCallback((path) => {
    abortInteractionRequests()
    setUploadedFilePath(path)
    setUvlContent(null)
    setPumlContent(null)
    setPimMetrics(null)
    setPsmMetrics(null)
    resetInteractionState()
  }, [abortInteractionRequests, resetInteractionState])

  /**
   * Stores the CIM metrics returned by the upload-processing flow.
   *
   * This handler is used by the CIM panel so the application can expose the loaded CIM
   * summary to the rest of the transformation flow.
   */
  const handleCimMetricsLoaded = useCallback((metrics) => {
    setCimMetrics(metrics)
  }, [])

  /**
   * Stores the PIM result produced by the CIM-to-PIM transformation.
   *
   * This handler is used by the app after the first transformation step so the PIM panel
   * and downstream actions can reuse the generated UVL content and metrics.
   */
  const handlePimTransformed = useCallback((data) => {
    setUvlContent(data.uvl_content)
    setCimMetrics(data.metrics?.cim || cimMetrics)
    setPimMetrics(data.metrics?.pim || null)
  }, [cimMetrics])

  /**
   * Stores the PSM result produced by the PIM-to-PSM transformation.
   *
   * This handler is used by the app after the second transformation step so the PSM
   * panel can display the generated diagram and the latest metrics snapshot.
   */
  const handlePsmTransformed = useCallback((data) => {
    setPumlContent(data.puml_content)
    setUvlContent(data.uvl_content || uvlContent)
    setCimMetrics(data.metrics?.cim || cimMetrics)
    setPimMetrics(data.metrics?.pim || pimMetrics)
    setPsmMetrics(data.metrics?.psm || null)
  }, [cimMetrics, pimMetrics, uvlContent])

  /**
   * Clears only the PSM output while keeping the earlier CIM and PIM state available.
   *
   * This handler is used by the PSM panel when the user wants to discard the final UML
   * result without restarting the whole frontend flow.
   */
  const handleClearPsm = useCallback(() => {
    setPumlContent(null)
    setPsmMetrics(null)
  }, [])

  /**
   * Clears the current PIM result and every state that depends on it.
   *
   * This handler is used by the PIM panel so the application can remove the generated UVL,
   * reset guided interaction, and also discard the downstream PSM output.
   */
  const handleClearPim = useCallback(() => {
    abortInteractionRequests()
    setUvlContent(null)
    setPimMetrics(null)
    setPumlContent(null)
    setPsmMetrics(null)
    resetInteractionState()
  }, [abortInteractionRequests, resetInteractionState])

  /**
   * Clears the source CIM state and all downstream transformation results.
   *
   * This handler is used by the CIM panel when the user wants to restart the complete
   * frontend flow from a clean state.
   */
  const handleClearCim = useCallback(() => {
    abortInteractionRequests()
    setUploadedFilePath(null)
    setSelectedExample(null)
    setCimMetrics(null)
    setUvlContent(null)
    setPimMetrics(null)
    setPumlContent(null)
    setPsmMetrics(null)
    resetInteractionState()
  }, [abortInteractionRequests, resetInteractionState])

  /**
   * Loads one predefined example into the application as the current CIM source.
   *
   * This handler is used by the examples sidebar so the app can switch to a sample model
   * while clearing every result derived from a previous upload or example.
   */
  const handleExampleSelected = useCallback((example) => {
    abortInteractionRequests()
    setSelectedExample({
      ...example,
      requestId: `${example.id}-${Date.now()}`,
    })
    setUploadedFilePath(null)
    setCimMetrics(null)
    setPimMetrics(null)
    setPsmMetrics(null)
    setUvlContent(null)
    setPumlContent(null)
    resetInteractionState()
  }, [abortInteractionRequests, resetInteractionState])

  /**
   * Toggles AI-assisted interaction mode and resets stale interaction state when disabled.
   *
   * This handler is used by the header toggle because guided questions only make sense
   * while the application is operating in the AI-assisted interaction mode.
   */
  const handleToggleAi = useCallback(() => {
    setIsAiEnabled((currentValue) => {
      const nextValue = !currentValue

      if (!nextValue) {
        abortInteractionRequests()
        resetInteractionState()
      }

      return nextValue
    })
  }, [abortInteractionRequests, resetInteractionState])

  /**
   * Runs the CIM-to-PIM transformation for the current uploaded source file.
   *
   * This helper is used by the main application after guided interaction or direct
   * execution so the PIM result is always produced from the latest active file path.
   */
  const runCimToPimTransformation = useCallback(async () => {
    if (!uploadedFilePath) return

    transformAbortRef.current?.abort()
    const controller = new AbortController()
    const runId = ++interactionRunIdRef.current
    transformAbortRef.current = controller

    try {
      const response = await transformCimToPim(uploadedFilePath, { signal: controller.signal })

      if (controller.signal.aborted || runId !== interactionRunIdRef.current) {
        return
      }

      handlePimTransformed(response)
    } finally {
      if (transformAbortRef.current === controller) {
        transformAbortRef.current = null
      }
    }
  }, [handlePimTransformed, uploadedFilePath])

  /**
   * Opens the guided-question flow or falls back to direct transformation when AI is off.
   *
   * This helper is used by the central interaction button because that action decides
   * whether the app should fetch questions first or run the CIM-to-PIM step immediately.
   */
  const openQuestionsModal = async () => {
    if (!uploadedFilePath) return

    if (!isAiEnabled) {
      resetInteractionState()
      await runCimToPimTransformation()
      return
    }

    if (questionsStatus === "loading") {
      setIsQuestionsModalOpen(true)
      return
    }

    if (questionsStatus === "ready" && questions.length > 0) {
      setIsQuestionsModalOpen(true)
      return
    }

    setQuestions([])
    setQuestionsError("")
    setQuestionsStatus("loading")
    setIsQuestionsModalOpen(true)
    let controller = null

    try {
      questionsAbortRef.current?.abort()
      controller = new AbortController()
      const runId = ++interactionRunIdRef.current
      questionsAbortRef.current = controller

      const qs = await fetchQuestions(uploadedFilePath, { signal: controller.signal })

      if (controller.signal.aborted || runId !== interactionRunIdRef.current) {
        return
      }

      setQuestions(qs)
      setQuestionsStatus("ready")
      setIsQuestionsModalOpen(true)
    } catch (error) {
      if (axios.isCancel(error) || error.code === "ERR_CANCELED") {
        return
      }

      setQuestions([])
      setQuestionsError(error.response?.data?.detail || "Unable to load guided questions. Please try again.")
      setQuestionsStatus("error")
      setIsQuestionsModalOpen(true)
      console.error("Error fetching questions:", error)
    } finally {
      if (questionsAbortRef.current === controller) {
        questionsAbortRef.current = null
      }
    }
  }

  /**
   * Closes the questions modal without mutating the stored question state.
   *
   * This handler is used by both modal variants so the shared modal visibility stays
   * controlled from the main application state.
   */
  const handleQuestionsModalClose = () => {
    setIsQuestionsModalOpen(false)
  }

  /**
   * Continues from the guided-question step into the CIM-to-PIM transformation.
   *
   * This handler is used by the guided questions modal so the app can resume the main
   * transformation flow after the user is done reviewing the prepared questions.
   */
  const handleContinueWithQuestions = async () => {
    setIsQuestionsModalOpen(false)
    try {
      await runCimToPimTransformation()
    } catch (error) {
      if (axios.isCancel(error) || error.code === "ERR_CANCELED") {
        return
      }

      throw error
    }
  }

  /**
   * Renders one interaction button variant for the center action columns.
   *
   * This helper is used twice by the main layout so both action columns share the same
   * button structure while keeping the interactive and disabled behaviors consistent.
   */
  const renderInteractionButton = ({ interactive = false }) => {
    const isLoadingQuestions = interactive && questionsStatus === "loading"
    const isDisabled = interactive ? !uploadedFilePath || isLoadingQuestions : true
    const handleClick = interactive ? openQuestionsModal : undefined

    return (
      <button
        type="button"
        onClick={handleClick}
        disabled={isDisabled}
        className={`min-w-[76px] rounded-lg border px-3 py-2 transition-all ${
          !interactive
            ? "cursor-not-allowed border-ctp-surface1 bg-ctp-surface0 text-[#a0988c] opacity-60"
            : !uploadedFilePath
            ? "cursor-not-allowed border-ctp-surface1 bg-ctp-surface0 text-[#a0988c]"
            : isLoadingQuestions
              ? "border-ctp-blue/40 bg-ctp-blue/20 text-ctp-blue shadow-lg shadow-ctp-blue/10"
              : "border-gray-600 bg-gray-700 text-white hover:bg-gray-600"
        }`}
      >
        <span className="mb-2 flex items-center justify-center">
          {isLoadingQuestions ? (
            <Loader2 className="h-6 w-6 animate-spin" />
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-6 w-6"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              <path d="M8 12a2 2 0 0 0 2-2V8H8" />
              <path d="M14 12a2 2 0 0 0 2-2V8h-2" />
            </svg>
          )}
        </span>
        <div className="text-sm tracking-wide">{isLoadingQuestions ? "PREPARING" : "INTERACT"}</div>
      </button>
    )
  }

  return (
    <div className="min-h-screen w-full bg-ctp-base text-[#a0988c] font-sans selection:bg-ctp-mauve selection:text-ctp-base flex flex-col">
      {/* Examples sidebar */}
      <ExamplesSidebar
        isOpen={isExamplesOpen}
        onClose={() => setIsExamplesOpen(false)}
        onSelectExample={handleExampleSelected}
      />

      {/* Top navigation */}
      <Header
        onOpenExamples={() => setIsExamplesOpen(true)}
        isAiEnabled={isAiEnabled}
        onToggleAi={handleToggleAi}
      />

      {/* Main workspace */}
      <main className="flex-1 flex flex-col w-full max-w-[1920px] mx-auto px-6 py-8">
        {/* Transformation controls */}
        <div className="mb-8">
          <Filter
            uploadedFilePath={uploadedFilePath}
            uvlContent={uvlContent}
            onTransformCimToPim={handlePimTransformed}
            onTransformPimToPsm={handlePsmTransformed}
            onOpenQuestionsModal={openQuestionsModal}
          />
        </div>

        {/* Three-level transformation layout */}
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_88px_minmax(0,1fr)_88px_minmax(0,1fr)] gap-4 items-stretch min-h-[780px]">
          {/* CIM panel */}
          <div className="h-full">
            <CIM
              onFileUploaded={handleFileUploaded}
              onMetricsLoaded={handleCimMetricsLoaded}
              metrics={cimMetrics}
              selectedExample={selectedExample}
              onClear={handleClearCim}
            />
          </div>

          {/* CIM to PIM action */}
          <div className="flex flex-col items-center justify-center">
            {renderInteractionButton({ interactive: true })}
          </div>

          {/* Interaction modals */}
          {questionsStatus === "ready" ? (
            <GuidedQuestionsModal
              isOpen={isQuestionsModalOpen}
              onClose={handleQuestionsModalClose}
              questions={questions}
              onContinue={handleContinueWithQuestions}
            />
          ) : (
            <QuestionsModal isOpen={isQuestionsModalOpen} onClose={handleQuestionsModalClose}>
              {questionsStatus === "loading" ? (
                <>
                  {/* Loading state */}
                  <div className="flex min-h-[280px] flex-col items-center justify-center text-center">
                <div className="mb-5 rounded-full border border-ctp-blue/30 bg-ctp-blue/10 p-4 text-ctp-blue">
                  <Loader2 className="h-10 w-10 animate-spin" />
                </div>
                <h2 className="text-2xl font-bold text-ctp-text">Preparing guided questions</h2>
                <p className="mt-3 max-w-md text-base text-[#a0988c]">
                  You can close this window while we prepare them. It will reopen automatically when the questions are ready.
                </p>
                  </div>
                </>
              ) : questionsStatus === "error" ? (
                <>
                  {/* Error state */}
                  <div className="flex min-h-[280px] flex-col items-center justify-center text-center">
                <div className="mb-5 rounded-full border border-ctp-red/30 bg-ctp-red/10 p-4 text-ctp-red">
                  <TriangleAlert className="h-10 w-10" />
                </div>
                <h2 className="text-2xl font-bold text-ctp-text">Unable to load guided questions</h2>
                <p className="mt-3 max-w-md text-base text-[#a0988c]">{questionsError}</p>
                <div className="mt-6 flex gap-3">
                  <button
                    type="button"
                    onClick={handleQuestionsModalClose}
                    className="rounded-lg border border-ctp-surface1 bg-ctp-surface0 px-4 py-2 font-semibold text-ctp-text transition-colors hover:bg-ctp-surface1"
                  >
                    Close
                  </button>
                  <button
                    type="button"
                    onClick={openQuestionsModal}
                    className="rounded-lg bg-ctp-mauve px-4 py-2 font-semibold text-ctp-base transition-colors hover:bg-ctp-pink"
                  >
                    Try again
                  </button>
                </div>
                  </div>
                </>
              ) : null}
            </QuestionsModal>
          )}

          {/* PIM panel */}
          <div className="h-full">
            <PIM
              uvlContent={uvlContent}
              metrics={pimMetrics}
              interactionStatus={questionsStatus}
              onClear={handleClearPim}
            />
          </div>

          {/* PIM to PSM action */}
          <div className="flex flex-col items-center justify-center">
            {renderInteractionButton({ interactive: false })}
          </div>

          {/* PSM panel */}
          <div className="h-full">
            <PSM
              pumlContent={pumlContent}
              metrics={psmMetrics}
              onClear={handleClearPsm}
            />
          </div>
        </div>
      </main>
    </div>
  )
}
