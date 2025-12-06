import { useState } from "react"
import { CIM } from "./Levels/CIM"
import { PIM } from "./Levels/PIM"
import { PSM } from "./Levels/PSM"
import { Filter } from "./Filter/Filter"
import { Header } from "./Commons/Header"

export const App = () => {
  const [uploadedFilePath, setUploadedFilePath] = useState(null)
  const [cimMetrics, setCimMetrics]             = useState(null)
  const [pimMetrics, setPimMetrics]             = useState(null)
  const [psmMetrics, setPsmMetrics]             = useState(null)
  const [uvlContent, setUvlContent]             = useState(null)
  const [pumlContent, setPumlContent]           = useState(null)

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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch relative h-[780px]">

          <div className="hidden lg:flex absolute top-1/2 -translate-y-1/2 left-0 w-full justify-between px-[16%] pointer-events-none z-0">
            <svg className="w-20 h-20 text-ctp-surface1/50 animate-pulse" viewBox="0 0 24 24" fill="none">
              <path d="M5 4l7 8-7 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <div className="w-10" />
            <svg className="w-20 h-20 text-ctp-surface1/50 animate-pulse" viewBox="0 0 24 24" fill="none">
              <path d="M5 4l7 8-7 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>

          <div className="relative z-10 h-full">
            <CIM
              onFileUploaded={handleFileUploaded}
              onMetricsLoaded={handleCimMetricsLoaded}
              metrics={cimMetrics}
            />
          </div>

          <div className="relative z-10 h-full">
            <PIM
              uvlContent={uvlContent}
              metrics={pimMetrics}
            />
          </div>

          <div className="relative z-10 h-full">
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