import { useCallback, useState } from "react"
import { CIM } from "./Levels/CIM"
import { PIM } from "./Levels/PIM"
import { PSM } from "./Levels/PSM"
import { Filter } from "./Filter/Filter"
import { Header } from "./Commons/Header"
import { ExamplesSidebar } from "./Examples/ExamplesSidebar"

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
          />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-stretch min-h-[780px]">
          <div className="xl:col-span-4 h-full">
            <CIM
              onFileUploaded={handleFileUploaded}
              onMetricsLoaded={handleCimMetricsLoaded}
              metrics={cimMetrics}
              selectedExample={selectedExample}
            />
          </div>

          <div className="xl:col-span-4 h-full">
            <PIM
              uvlContent={uvlContent}
              metrics={pimMetrics}
            />
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
