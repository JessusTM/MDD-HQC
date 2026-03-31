import { useCallback, useState } from "react"
import { CIM } from "./Levels/CIM"
import { PIM } from "./Levels/PIM"
import { PSM } from "./Levels/PSM"
import { Filter } from "./Filter/Filter"
import { Header } from "./Commons/Header"
import { ExamplesSidebar } from "./Examples/ExamplesSidebar"
import QuestionsModal from "./Questions/Questions_modal"
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

  const handleFileUploaded = useCallback((path) => {
    setUploadedFilePath(path)
    setUvlContent(null)
    setPumlContent(null)
    setPimMetrics(null)
    setPsmMetrics(null)
  }, [])

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
  }, [])

  const [isQuestionsModalOpen, setIsQuestionsModalOpen] = useState(false)
  const [questions, setQuestions] = useState([]);

  const openQuestionsModal = async () => {
    if (!uploadedFilePath) return;

    alert("Espere un momento, cargando preguntas...");

    try {

      const qs = await fetchQuestions(uploadedFilePath);
      setQuestions(qs);
      setIsQuestionsModalOpen(true);

    } catch (error) {
      alert("Error al cargar preguntas. Intente nuevamente.");
      console.error("Error fetching questions:", error);
    }

  };

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

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-stretch min-h-[780px]">
          <div className="xl:col-span-3 h-full">
            <CIM
              onFileUploaded={handleFileUploaded}
              onMetricsLoaded={handleCimMetricsLoaded}
              metrics={cimMetrics}
              selectedExample={selectedExample}
            />
          </div>

          <div className="col-span-1 flex flex-col items-center justify-center"> 

            <button className="bg-gray-700 text-white px-3 py-1 rounded-lg flex flex-col items-center mb-10">
              <span className="text-white px-3 py-1 rounded-md mb-2">
                “ ”
              </span>
              <div className="text-sm tracking-wide text-blue-300">DEBUG</div>
          </button>

            <button onClick={() => setIsQuestionsModalOpen(true)} className="bg-gray-700 text-white px-3 py-1 rounded-lg flex flex-col items-center">
              <span className="text-white px-3 py-1 rounded-md mb-2">
                “ ”
              </span>
              <div className="text-sm tracking-wide text-blue-300">INTERACC.</div>
          </button>

          </div>

          <QuestionsModal isOpen={isQuestionsModalOpen} onClose={() => setIsQuestionsModalOpen(false)}>
            <div className="flex items-center mb-4">
            
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="w-6 h-6 text-purple-400 mr-2"
              viewBox="0 0 24 24"
              fill="currentColor"
              >
              <path d="M7 17h3l2-4V7H7v6h2l-2 4zm7 0h3l2-4V7h-5v6h2l-2 4z" />
            </svg>
   
              <h2 className="text-xl font-bold text-white">Interacción Guiada: CIM a PIM</h2>
              </div>

            <div className="bg-gray-900 p-4 mb-4 -mx-6">
              <p className="text-gray-300">Responde a las siguientes preguntas para refinar la transformación semiautomática de <span className="font-bold text-blue-200">CIM a PIM</span></p>

              {questions.map((q) => (
              <div key={q.id} className="mt-6 bg-gray-700 p-4 rounded-lg">
                <h3 className="text-white font-semibold mb-2">{q.text}</h3>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {q.options?.map((opt, i) => (
                      <button 
                      key={i} 
                      className="bg-gray-900 text-white px-3 py-2 rounded hover:bg-blue-600"
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
              </div>
              ))}

            </div>


            <div className="flex justify-end">
            <button
            onClick={async () => {
              setIsQuestionsModalOpen(false)
              const response = await transformCimToPim(uploadedFilePath)
              handlePimTransformed(response)
            }}
            className="bg-gray-700 text-white px-4 py-2 rounded"
          >
            Cerrar
          </button>
          </div>
          </QuestionsModal>

          <div className="xl:col-span-3 h-full">
            <PIM
              uvlContent={uvlContent}
              metrics={pimMetrics}
            />
          </div>

          <div className="col-span-1 flex flex-col items-center justify-center"> 

            <button className="bg-gray-700 text-white px-3 py-1 rounded-lg flex flex-col items-center mb-10">
              <span className="text-white px-3 py-1 rounded-md mb-2">
                “ ”
              </span>
              <div className="text-sm tracking-wide text-blue-300">DEBUG</div>
          </button>

            <button onClick={() => setIsQuestionsModalOpen(true)} className="bg-gray-700 text-white px-3 py-1 rounded-lg flex flex-col items-center">
              <span className="text-white px-3 py-1 rounded-md mb-2">
                “ ”
              </span>
              <div className="text-sm tracking-wide text-blue-300">INTERACC.</div>
          </button>

          </div>

          <div className="xl:col-span-4 h-full">
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
