import { Settings2, ArrowRight, Play } from "lucide-react"
import { useState } from "react"
import { transformCimToPim, transformPimToPsm } from "../../services/api"

export const Filter = ({
  uploadedFilePath,
  uvlContent,
  onTransformCimToPim,
  onTransformPimToPsm,
}) => {
  const [source, setSource] = useState("CIM")
  const [target, setTarget] = useState("PIM")
  const [loading, setLoading] = useState(false)

  const sameLevel = source === target

  const handleTransform = async () => {
    if (sameLevel || !uploadedFilePath) return

    setLoading(true)
    try {
      if (source === "CIM" && target === "PIM") {
        const response = await transformCimToPim(uploadedFilePath)
        onTransformCimToPim?.(response)
      } else if (source === "PIM" && target === "PSM") {
        if (!uvlContent) {
          alert("Primero debes completar la transformación CIM → PIM")
          return
        }
        const response = await transformPimToPsm(uploadedFilePath)
        onTransformPimToPsm?.(response)
      }
    } catch (error) {
      console.error("Error en transformación:", error)
      alert(error.response?.data?.detail || "Error al realizar la transformación")
    } finally {
      setLoading(false)
    }
  }

  const canTransform = !sameLevel && uploadedFilePath && 
    !(source === "PIM" && target === "PSM" && !uvlContent)

  return (
    <div className="w-full relative">
      <div className="bg-ctp-mantle border-2 border-ctp-surface1 shadow-xl rounded-xl px-5 py-3 flex flex-wrap items-center justify-between gap-4">

        <div className="flex items-center gap-6 flex-1">
          <div className="flex items-center gap-3 text-ctp-overlay1 mr-4">
            <Settings2 className="w-6 h-6" />
            <span className="text-lg font-semibold uppercase tracking-wider hidden md:inline">
              Transformación
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-base font-bold text-ctp-overlay0 uppercase">De</span>
            <div className="relative">
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="appearance-none bg-ctp-surface0 border border-transparent text-ctp-text text-lg rounded-lg focus:ring-2 focus:ring-ctp-mauve focus:border-ctp-mauve block w-36 md:w-48 p-3 font-semibold cursor-pointer hover:bg-ctp-surface1 transition-colors shadow-sm outline-none"
              >
                <option value="CIM">CIM</option>
                <option value="PIM">PIM</option>
                <option value="PSM">PSM</option>
              </select>
            </div>
          </div>

          <ArrowRight className="text-ctp-surface2 w-6 h-6" />

          <div className="flex items-center gap-3">
            <span className="text-base font-bold text-ctp-overlay0 uppercase">A</span>
            <div className="relative">
              <select
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                className="appearance-none bg-ctp-surface0 border border-transparent text-ctp-text text-lg rounded-lg focus:ring-2 focus:ring-ctp-mauve focus:border-ctp-mauve block w-36 md:w-48 p-3 font-semibold cursor-pointer hover:bg-ctp-surface1 transition-colors shadow-sm outline-none"
              >
                <option value="CIM">CIM</option>
                <option value="PIM">PIM</option>
                <option value="PSM">PSM</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            disabled={!canTransform || loading}
            onClick={handleTransform}
            className={`
              flex items-center gap-3 px-8 py-3 rounded-lg font-bold text-ctp-base shadow-lg transition-all text-base tracking-wide
              ${!canTransform || loading
                ? "bg-ctp-surface0 text-ctp-overlay0 cursor-not-allowed shadow-none border border-ctp-surface1"
                : "bg-ctp-mauve hover:bg-ctp-pink active:bg-ctp-pink text-ctp-base"
              }
            `}
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-ctp-base border-t-transparent rounded-full animate-spin" />
                Transformando...
              </>
            ) : (
              <>
                <Play className="w-5 h-5 fill-current" />
                Ejecutar
              </>
            )}
          </button>
        </div>
      </div>

      {sameLevel && (
        <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 z-50 text-center text-sm text-ctp-red font-semibold bg-ctp-base p-2 rounded-md border border-ctp-red/50 px-6 shadow-sm backdrop-blur-sm pointer-events-none">
          Origen y Destino no pueden ser iguales.
        </div>
      )}
      {source === "PIM" && target === "PSM" && !uvlContent && uploadedFilePath && (
        <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 z-50 text-center text-sm text-ctp-red font-semibold bg-ctp-base p-2 rounded-md border border-ctp-red/50 px-6 shadow-sm backdrop-blur-sm pointer-events-none">
          Primero completa la transformación CIM → PIM.
        </div>
      )}
    </div>
  )
}