import { useCallback, useState } from "react"
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

export const App = () => {
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

  const resetInteractionState = useCallback(() => {
    setQuestions([])
    setQuestionsStatus("idle")
    setQuestionsError("")
    setIsQuestionsModalOpen(false)
  }, [])

  const handleFileUploaded = useCallback((path) => {
    setUploadedFilePath(path)
    setUvlContent(null)
    setPumlContent(null)
    setPimMetrics(null)
    setPsmMetrics(null)
    resetInteractionState()
  }, [resetInteractionState])

  const handleCimMetricsLoaded = useCallback((metrics) => {
    setCimMetrics(metrics)
  }, [])

  const handlePimTransformed = useCallback((data) => {
    setUvlContent(data.uvl_content)
    setCimMetrics(data.metrics?.cim || cimMetrics)
    setPimMetrics(data.metrics?.pim || null)
  }, [cimMetrics])

  const handlePsmTransformed = useCallback((data) => {
    setPumlContent(data.puml_content)
    setUvlContent(data.uvl_content || uvlContent)
    setCimMetrics(data.metrics?.cim || cimMetrics)
    setPimMetrics(data.metrics?.pim || pimMetrics)
    setPsmMetrics(data.metrics?.psm || null)
  }, [cimMetrics, pimMetrics, uvlContent])

  const handleExampleSelected = useCallback((example) => {
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
  }, [resetInteractionState])

  const openQuestionsModal = async () => {
    if (!uploadedFilePath) return

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

    try {
      const qs = await fetchQuestions(uploadedFilePath)
      setQuestions(qs)
      setQuestionsStatus("ready")
      setIsQuestionsModalOpen(true)
    } catch (error) {
      setQuestions([])
      setQuestionsError(error.response?.data?.detail || "Unable to load guided questions. Please try again.")
      setQuestionsStatus("error")
      setIsQuestionsModalOpen(true)
      console.error("Error fetching questions:", error)
    }
  }

  const handleQuestionsModalClose = () => {
    setIsQuestionsModalOpen(false)
  }

  const handleContinueWithQuestions = async () => {
    setIsQuestionsModalOpen(false)
    const response = await transformCimToPim(uploadedFilePath)
    handlePimTransformed(response)
  }

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
      <ExamplesSidebar
        isOpen={isExamplesOpen}
        onClose={() => setIsExamplesOpen(false)}
        onSelectExample={handleExampleSelected}
      />

      <Header onOpenExamples={() => setIsExamplesOpen(true)} />

      <main className="flex-1 flex flex-col w-full max-w-[1920px] mx-auto px-6 py-8">
        <div className="mb-8">
          <Filter
            uploadedFilePath={uploadedFilePath}
            uvlContent={uvlContent}
            onTransformCimToPim={handlePimTransformed}
            onTransformPimToPsm={handlePsmTransformed}
            onOpenQuestionsModal={openQuestionsModal}
          />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_88px_minmax(0,1fr)_88px_minmax(0,1fr)] gap-4 items-stretch min-h-[780px]">
          <div className="h-full">
            <CIM
              onFileUploaded={handleFileUploaded}
              onMetricsLoaded={handleCimMetricsLoaded}
              metrics={cimMetrics}
              selectedExample={selectedExample}
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
            />
          </div>

          <div className="flex flex-col items-center justify-center">
            {renderInteractionButton({ interactive: false })}
          </div>

          <div className="h-full">
            <PSM
              pumlContent={pumlContent}
              metrics={psmMetrics}
            />
          </div>
        </div>
      </main>
    </div>
  )
}
