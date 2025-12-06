import { useRef, useState } from "react"
import { Upload, FileText, CheckCircle, Loader2 } from "lucide-react"
import { uploadFile, getCimMetrics } from "../../services/api"

export const CIM = ({ onFileUploaded, onMetricsLoaded, metrics }) => {
  const [file, setFile]                 = useState(null)
  const [filePath, setFilePath]         = useState(null)
  const [errorMessage, setErrorMessage] = useState("")
  const [infoMessage, setInfoMessage]   = useState("")
  const [loading, setLoading]           = useState(false)
  const fileInputRef                    = useRef(null)

  const reset = () => {
    setFile(null)
    setFilePath(null)
    setErrorMessage("")
    setInfoMessage("")
    onMetricsLoaded?.(null)
  }

  const handleFile = async (event) => {
    const selected = event.target.files?.[0]

    if (!selected) {
      reset()
      return
    }

    setFile(selected)
    setInfoMessage("Subiendo archivo…")
    setErrorMessage("")
    setLoading(true)
    await processFile(selected)
  }

  const processFile = async (fileToRead) => {
    try {
      const uploadResponse  = await uploadFile(fileToRead)
      const path            = uploadResponse.path
      setFilePath(path)
      setInfoMessage("Archivo subido correctamente")
      onFileUploaded?.(path)
      setInfoMessage("Calculando métricas CIM…")
      const metricsResponse = await getCimMetrics(path)
      onMetricsLoaded?.(metricsResponse.metrics?.cim)
      setInfoMessage("Métricas calculadas")
    } catch (error) {
      console.error("Error procesando archivo", error)
      setErrorMessage(error.response?.data?.detail || "Error al procesar el archivo")
      setInfoMessage("")
      reset()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-ctp-surface0 rounded-xl shadow-xl border-2 border-ctp-surface2 transition-all duration-300 hover:border-ctp-surface1">
      <div className="p-5 border-b border-ctp-surface1 bg-ctp-surface0/20 rounded-t-xl flex items-center justify-between shrink-0 h-20">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-ctp-surface1 rounded-lg">
            <FileText className="w-8 h-8 text-ctp-blue" />
          </div>
          <div>
            <h3 className="font-bold text-ctp-text text-2xl">CIM</h3>
            <p className="text-lg text-ctp-subtext0 font-semibold hidden xl:block">
              i* 2.0 (iStar)
            </p>
          </div>
        </div>

        {file && !errorMessage && (
          <span className="px-3 py-1 bg-ctp-green/20 text-ctp-green border border-ctp-green/30 text-sm font-semibold rounded-full flex items-center gap-1.5 shadow-sm">
            <CheckCircle className="w-4 h-4" /> Listo
          </span>
        )}
      </div>

      <div className="flex-1 p-0 overflow-hidden flex flex-col relative bg-ctp-crust">
        <div className="flex-1 flex flex-col items-center justify-center m-6 py-10 rounded-lg bg-ctp-mantle/50">
          <p className="text-ctp-subtext0 text-xl mb-6 text-center px-6 font-semibold">
            Sube tu archivo i* 2.0 (XML) aquí…
          </p>

          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept=".xml,.istar,.txt"
            onChange={handleFile}
          />

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-3 px-6 py-3 bg-ctp-mauve hover:bg-ctp-pink text-ctp-base rounded-lg font-bold transition-all hover:scale-105 active:scale-95 shadow-lg shadow-ctp-mauve/20 text-base"
          >
            <Upload className="w-5 h-5" />
            Subir Archivo
          </button>

          <div className="mt-4 text-sm">
            {file && !errorMessage && !infoMessage && (
              <span className="text-ctp-subtext0">{file.name}</span>
            )}

            {infoMessage && (
              <span className="text-ctp-green">{infoMessage}</span>
            )}

            {errorMessage && (
              <span className="text-ctp-red">{errorMessage}</span>
            )}
          </div>
        </div>
      </div>

      <div className="shrink-0 bg-ctp-mantle border-t border-ctp-surface0/50 p-4">
        <div className="min-h-[104px] rounded-lg bg-ctp-mantle/40 p-4 overflow-y-auto max-h-[300px]">
          {loading ? (
            <div className="flex items-center justify-center gap-2 text-ctp-subtext0">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-sm font-semibold">Calculando métricas...</span>
            </div>
          ) : metrics ? (
            <div className="space-y-2">
              <h4 className="text-ctp-text font-bold text-sm mb-3">Métricas CIM</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-ctp-subtext0">Goals:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.goals || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-ctp-subtext0">Tasks:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.tasks || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-ctp-subtext0">Softgoals:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.softgoals || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-ctp-subtext0">Resources:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.resources || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-ctp-subtext0">Actors:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.actors || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-ctp-subtext0">Agents:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.agents || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-ctp-subtext0">Roles:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.roles || 0}</span>
                </div>
                <div className="bg-ctp-surface0/50 p-2 rounded">
                  <span className="text-ctp-subtext0">Dependencias:</span>
                  <span className="text-ctp-text font-semibold ml-2">{metrics.social_dependencies || 0}</span>
                </div>
                {metrics.internal_links && (
                  <>
                    <div className="bg-ctp-surface0/50 p-2 rounded">
                      <span className="text-ctp-subtext0">Needed-by:</span>
                      <span className="text-ctp-text font-semibold ml-2">{metrics.internal_links.needed_by || 0}</span>
                    </div>
                    <div className="bg-ctp-surface0/50 p-2 rounded">
                      <span className="text-ctp-subtext0">Qualification:</span>
                      <span className="text-ctp-text font-semibold ml-2">{metrics.internal_links.qualification_links || 0}</span>
                    </div>
                    <div className="bg-ctp-surface0/50 p-2 rounded">
                      <span className="text-ctp-subtext0">Contributions:</span>
                      <span className="text-ctp-text font-semibold ml-2">{metrics.internal_links.contributions || 0}</span>
                    </div>
                  </>
                )}
                {metrics.refinements && (
                  <>
                    <div className="bg-ctp-surface0/50 p-2 rounded">
                      <span className="text-ctp-subtext0">Refinements AND:</span>
                      <span className="text-ctp-text font-semibold ml-2">{metrics.refinements.and || 0}</span>
                    </div>
                    <div className="bg-ctp-surface0/50 p-2 rounded">
                      <span className="text-ctp-subtext0">Refinements OR:</span>
                      <span className="text-ctp-text font-semibold ml-2">{metrics.refinements.or || 0}</span>
                    </div>
                  </>
                )}
                {metrics.total_nodes !== undefined && (
                  <div className="bg-ctp-surface0/50 p-2 rounded col-span-2">
                    <span className="text-ctp-subtext0">Total nodos:</span>
                    <span className="text-ctp-text font-semibold ml-2">{metrics.total_nodes}</span>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <span className="text-ctp-subtext0 text-xl font-semibold italic">
              Sin métricas disponibles
            </span>
          )}
        </div>
      </div>
    </div>
  )
}