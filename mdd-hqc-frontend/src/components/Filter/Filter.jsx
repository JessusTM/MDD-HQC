import { Settings2, ArrowRight, Play } from "lucide-react"
import { useState } from "react"
import { transformCimToPim } from "../../services/transformations"
import { transformPimToPsm } from "../../services/transformations"

export const Filter = ({
  uploadedFilePath,
  uvlContent,
  onTransformCimToPim,
  onTransformPimToPsm,
  onOpenQuestionsModal,
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
        onOpenQuestionsModal?.();
        return
      }
      
      if (source === "PIM" && target === "PSM") {
        if (!uvlContent) {
          alert("You must complete the CIM -> PIM transformation first")
          return
        }
        const response = await transformPimToPsm(uploadedFilePath)
        onTransformPimToPsm?.(response)
      }
    } catch (error) {
      console.error("Transformation error:", error)
      alert(error.response?.data?.detail || "Error running the transformation")
    } finally {
      setLoading(false)
    }
  }

  const canTransform = !sameLevel && uploadedFilePath &&
    !(source === "PIM" && target === "PSM" && !uvlContent)

  return (
    <div className="w-full relative">
      <div className="bg-ctp-mantle border-2 border-ctp-surface1 shadow-xl rounded-xl px-5 py-3 flex flex-wrap items-center justify-between gap-4">

          <div className="flex items-center gap-4 flex-1">
          <div className="flex items-center gap-3 text-[#7F849C] mr-3">
            <Settings2 className="w-6 h-6" />
            <span className="text-lg font-semibold uppercase tracking-wider hidden md:inline">
              Transformation
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-lg font-bold text-[#7F849C] uppercase tracking-wide">From</span>
            <div className="relative">
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="appearance-none bg-ctp-surface0 border border-[#45475a] text-ctp-text text-lg rounded-lg focus:ring-2 focus:ring-ctp-mauve focus:border-ctp-mauve block w-36 md:w-48 p-3 font-semibold cursor-pointer hover:border-[#585b70] hover:bg-ctp-surface1 transition-colors shadow-sm outline-none"
              >
                <option value="CIM">CIM</option>
                <option value="PIM">PIM</option>
                <option value="PSM">PSM</option>
              </select>
            </div>
          </div>

          <ArrowRight className="text-ctp-surface2 w-8 h-8" />

          <div className="flex items-center gap-3">
            <span className="text-lg font-bold text-[#7F849C] uppercase tracking-wide">To</span>
            <div className="relative">
              <select
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                className="appearance-none bg-ctp-surface0 border border-[#45475a] text-ctp-text text-lg rounded-lg focus:ring-2 focus:ring-ctp-mauve focus:border-ctp-mauve block w-36 md:w-48 p-3 font-semibold cursor-pointer hover:border-[#585b70] hover:bg-ctp-surface1 transition-colors shadow-sm outline-none"
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
              flex items-center gap-2.5 min-w-[138px] justify-center px-6 py-3 rounded-lg font-semibold border transition-all text-base
              ${!canTransform || loading
                ? "bg-ctp-surface0 text-[#a0988c] cursor-not-allowed border-[#45475a]"
                : "bg-ctp-mauve text-ctp-base border-ctp-mauve shadow-lg shadow-ctp-mauve/20 hover:bg-ctp-pink hover:border-ctp-pink active:scale-95"
              }
            `}
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-ctp-base border-t-transparent rounded-full animate-spin" />
                Transforming...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current opacity-80" />
                Execute
              </>
            )}
          </button>
        </div>
      </div>

      {sameLevel && (
        <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 z-50 text-center text-sm text-ctp-red font-semibold bg-ctp-base p-2 rounded-md border border-ctp-red/50 px-6 shadow-sm backdrop-blur-sm pointer-events-none">
          Source and target cannot be the same.
        </div>
      )}
      {source === "PIM" && target === "PSM" && !uvlContent && uploadedFilePath && (
        <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 z-50 text-center text-sm text-ctp-red font-semibold bg-ctp-base p-2 rounded-md border border-ctp-red/50 px-6 shadow-sm backdrop-blur-sm pointer-events-none">
          Complete the CIM -> PIM transformation first.
        </div>
      )}
    </div>
  )
}
