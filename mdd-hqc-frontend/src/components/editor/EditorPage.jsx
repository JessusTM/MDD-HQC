/**
 * Editor page that coordinates the CIM, PIM, and PSM frontend flow.
 */

import { useCallback, useEffect, useRef, useState } from "react"
import axios from "axios"
import { Loader2, TriangleAlert } from "lucide-react"
import { EditorHeader } from "./EditorHeader"
import { ExamplesSidebar } from "./ExamplesSidebar"
import { Filter } from "./Filter"
import { CIM } from "./levels/CIM"
import { PIM } from "./levels/PIM"
import { PSM } from "./levels/PSM"
import GuidedQuestionsModal from "./questions/GuidedQuestionsModal"
import QuestionsModal from "./questions/QuestionsModal"
import { transformCimToPim } from "../../services/transformations"
import { fetchQuestions } from "../../services/questions"

/**
 * Keeps the full editor workflow synchronized across uploads, transformations, and modals.
 */
export const EditorPage = ({ onGoHome }) => {
  const questionsAbortRef = useRef(null)
  const transformAbortRef = useRef(null)
  const interactionRunIdRef = useRef(0)
  const [isAiEnabled, setIsAiEnabled] = useState(true)
  const [uploadedFilePath, setUploadedFilePath] = useState(null)
  const [generatedUvlPath, setGeneratedUvlPath] = useState(null)
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
   * Clears the guided-interaction state kept after UVL generation.
   */
  const resetInteractionState = useCallback(() => {
    setQuestions([])
    setQuestionsStatus("idle")
    setQuestionsError("")
    setIsQuestionsModalOpen(false)
  }, [])

  /**
   * Cancels in-flight interaction requests and invalidates the current run.
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
   * Stores the uploaded CIM path and clears downstream editor results.
   */
  const handleFileUploaded = useCallback((path) => {
    abortInteractionRequests()
    setUploadedFilePath(path)
    setGeneratedUvlPath(null)
    setUvlContent(null)
    setPumlContent(null)
    setPimMetrics(null)
    setPsmMetrics(null)
    resetInteractionState()
  }, [abortInteractionRequests, resetInteractionState])

  /**
   * Stores the latest CIM metrics returned after upload processing.
   */
  const handleCimMetricsLoaded = useCallback((metrics) => {
    setCimMetrics(metrics)
  }, [])

  /**
   * Applies the CIM-to-PIM response to the editor state.
   */
  const handlePimTransformed = useCallback((data) => {
    setGeneratedUvlPath(data.output_uvl || null)
    setUvlContent(data.uvl_content)
    setCimMetrics(data.metrics?.cim || cimMetrics)
    setPimMetrics(data.metrics?.pim || null)
  }, [cimMetrics])

  /**
   * Applies the PIM-to-PSM response to the editor state.
   */
  const handlePsmTransformed = useCallback((data) => {
    setPumlContent(data.puml_content)
    setUvlContent(data.uvl_content || uvlContent)
    setCimMetrics(data.metrics?.cim || cimMetrics)
    setPimMetrics(data.metrics?.pim || pimMetrics)
    setPsmMetrics(data.metrics?.psm || null)
  }, [cimMetrics, pimMetrics, uvlContent])

  /**
   * Clears only the generated PSM artifact and its metrics.
   */
  const handleClearPsm = useCallback(() => {
    setPumlContent(null)
    setPsmMetrics(null)
  }, [])

  /**
   * Clears the PIM result and every dependent editor state.
   */
  const handleClearPim = useCallback(() => {
    abortInteractionRequests()
    setGeneratedUvlPath(null)
    setUvlContent(null)
    setPimMetrics(null)
    setPumlContent(null)
    setPsmMetrics(null)
    resetInteractionState()
  }, [abortInteractionRequests, resetInteractionState])

  /**
   * Clears the CIM source and resets every later stage.
   */
  const handleClearCim = useCallback(() => {
    abortInteractionRequests()
    setUploadedFilePath(null)
    setGeneratedUvlPath(null)
    setSelectedExample(null)
    setCimMetrics(null)
    setUvlContent(null)
    setPimMetrics(null)
    setPumlContent(null)
    setPsmMetrics(null)
    resetInteractionState()
  }, [abortInteractionRequests, resetInteractionState])

  /**
   * Applies a predefined example as the new CIM source.
   */
  const handleExampleSelected = useCallback((example) => {
    abortInteractionRequests()
    setSelectedExample({
      ...example,
      requestId: `${example.id}-${Date.now()}`,
    })
    setUploadedFilePath(null)
    setGeneratedUvlPath(null)
    setCimMetrics(null)
    setPimMetrics(null)
    setPsmMetrics(null)
    setUvlContent(null)
    setPumlContent(null)
    resetInteractionState()
  }, [abortInteractionRequests, resetInteractionState])

  /**
   * Loads guided questions for the current UVL artifact.
   */
  const loadQuestionsForUvl = useCallback(async (uvlPath, { openModal = false } = {}) => {
    if (!uvlPath || !isAiEnabled) return

    if (questionsStatus === "loading") {
      if (openModal) {
        setIsQuestionsModalOpen(true)
      }
      return
    }

    setQuestions([])
    setQuestionsError("")
    setQuestionsStatus("loading")
    setIsQuestionsModalOpen(openModal)
    let controller = null

    try {
      questionsAbortRef.current?.abort()
      controller = new AbortController()
      const runId = ++interactionRunIdRef.current
      questionsAbortRef.current = controller

      const qs = await fetchQuestions(uvlPath, { signal: controller.signal })

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
  }, [isAiEnabled, questionsStatus])

  /**
   * Toggles AI assistance and clears guided-interaction state when disabling it.
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
   * Runs the CIM-to-PIM transformation for the active uploaded file.
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

      if (isAiEnabled && response.output_uvl) {
        void loadQuestionsForUvl(response.output_uvl, { openModal: true })
      }
    } finally {
      if (transformAbortRef.current === controller) {
        transformAbortRef.current = null
      }
    }
  }, [handlePimTransformed, isAiEnabled, loadQuestionsForUvl, uploadedFilePath])

  /**
   * Opens the guided-questions modal with the latest available state.
   */
  const openQuestionsModal = async () => {
    if (!generatedUvlPath || !isAiEnabled) return

    if (questionsStatus === "loading" || questionsStatus === "error") {
      setIsQuestionsModalOpen(true)
      return
    }

    if (questionsStatus === "ready" && questions.length > 0) {
      setIsQuestionsModalOpen(true)
      return
    }

    await loadQuestionsForUvl(generatedUvlPath, { openModal: true })
  }

  /**
   * Closes the guided-questions modal.
   */
  const handleQuestionsModalClose = () => {
    setIsQuestionsModalOpen(false)
  }

  /**
   * Closes the guided-questions modal after the user continues.
   */
  const handleContinueWithQuestions = () => {
    setIsQuestionsModalOpen(false)
  }

  /**
   * Renders the interaction button displayed between editor stages.
   */
  const renderInteractionButton = ({ interactive = false }) => {
    const isLoadingQuestions = interactive && questionsStatus === "loading"
    const isDisabled = interactive ? !generatedUvlPath || !isAiEnabled : true
    const handleClick = interactive ? openQuestionsModal : undefined

    return (
      <button
        type="button"
        onClick={handleClick}
        disabled={isDisabled}
        className={`min-w-[76px] rounded-lg border px-3 py-2 transition-all ${
          !interactive
            ? "cursor-not-allowed border-ctp-surface1 bg-ctp-surface0 text-[#a0988c] opacity-60"
            : !generatedUvlPath || !isAiEnabled
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
      <ExamplesSidebar
        isOpen={isExamplesOpen}
        onClose={() => setIsExamplesOpen(false)}
        onSelectExample={handleExampleSelected}
      />

      <EditorHeader
        onOpenExamples={() => setIsExamplesOpen(true)}
        onGoHome={onGoHome}
        isAiEnabled={isAiEnabled}
        onToggleAi={handleToggleAi}
      />

      <main className="flex-1 flex flex-col w-full max-w-[1920px] mx-auto px-6 py-8">
        <div className="mb-8">
          <Filter
            uploadedFilePath={uploadedFilePath}
            uvlContent={uvlContent}
            onTransformCimToPim={runCimToPimTransformation}
            onTransformPimToPsm={handlePsmTransformed}
          />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_88px_minmax(0,1fr)_88px_minmax(0,1fr)] gap-4 items-stretch min-h-[780px]">
          <div className="h-full">
            <CIM
              onFileUploaded={handleFileUploaded}
              onMetricsLoaded={handleCimMetricsLoaded}
              metrics={cimMetrics}
              selectedExample={selectedExample}
              onClear={handleClearCim}
            />
          </div>

          <div className="flex flex-col items-center justify-center">
            {renderInteractionButton({ interactive: true })}
          </div>

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
                <div className="flex min-h-[280px] flex-col items-center justify-center text-center">
                  <div className="mb-5 rounded-full border border-ctp-blue/30 bg-ctp-blue/10 p-4 text-ctp-blue">
                    <Loader2 className="h-10 w-10 animate-spin" />
                  </div>
                  <h2 className="text-2xl font-bold text-ctp-text">Preparing guided questions</h2>
                  <p className="mt-3 max-w-md text-base text-[#a0988c]">
                    You can close this window while we prepare them. It will reopen automatically when the questions are ready.
                  </p>
                </div>
              ) : questionsStatus === "error" ? (
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
              ) : null}
            </QuestionsModal>
          )}

          <div className="h-full">
            <PIM
              uvlContent={uvlContent}
              metrics={pimMetrics}
              interactionStatus={questionsStatus}
              onClear={handleClearPim}
            />
          </div>

          <div className="flex flex-col items-center justify-center">
            {renderInteractionButton({ interactive: false })}
          </div>

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
