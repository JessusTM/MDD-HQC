import { useState } from "react"
import { CIM } from "./Levels/CIM"
import { PIM } from "./Levels/PIM"
import { PSM } from "./Levels/PSM"
import { Filter } from "./Filter/Filter"
import { Header } from "./Commons/Header"

export const App = () => {
  const [uploadedFilePath, setUploadedFilePath] = useState(null)
  const [cimMetrics, setCimMetrics] = useState(null)
  const [pimMetrics, setPimMetrics] = useState(null)
  const [psmMetrics, setPsmMetrics] = useState(null)
  const [uvlContent, setUvlContent] = useState(null)
  const [pumlContent, setPumlContent] = useState(null)

  const handleFileUploaded = (path) => {
    setUploadedFilePath(path)
    setUvlContent(null)
    setPumlContent(null)
    setPimMetrics(null)
    setPsmMetrics(null)
  }

  const handleCimMetricsLoaded = (metrics) => {
    setCimMetrics(metrics)
  }

  const handlePimTransformed = (data) => {
    setUvlContent(data.uvl_content)
    setCimMetrics(data.metrics?.cim || cimMetrics)
    setPimMetrics(data.metrics?.pim || null)
  }

  const handlePsmTransformed = (data) => {
    setPumlContent(data.puml_content)
    setUvlContent(data.uvl_content || uvlContent)
    setCimMetrics(data.metrics?.cim || cimMetrics)
    setPimMetrics(data.metrics?.pim || pimMetrics)
    setPsmMetrics(data.metrics?.psm || null)
  }

  return (
    <div className="min-h-screen w-full bg-ctp-base text-ctp-text font-sans selection:bg-ctp-mauve selection:text-ctp-base flex flex-col">

      <Header />

      <main className="flex-1 flex flex-col w-full max-w-[1920px] mx-auto px-6 py-8">

        <div className="mb-8">
          <Filter
            uploadedFilePath={uploadedFilePath}
            uvlContent={uvlContent}
            onTransformCimToPim={handlePimTransformed}
            onTransformPimToPsm={handlePsmTransformed}
          />
        </div>

        <div className="grid grid-cols-8 gap-0 items-stretch h-[780px]">

          <div className="col-span-2 h-full">
            <CIM
              onFileUploaded={handleFileUploaded}
              onMetricsLoaded={handleCimMetricsLoaded}
              metrics={cimMetrics}
            />
          </div>

          <div className="col-span-1 flex items-center justify-center px-1" />


          <div className="col-span-2 h-full">
            <PIM
              uvlContent={uvlContent}
              metrics={pimMetrics}
            />
          </div>

          <div className="col-span-1 flex items-center justify-center px-1" />

          <div className="col-span-2 h-full">
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
