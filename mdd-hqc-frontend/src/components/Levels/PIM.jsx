/**
 * PIM panel that displays the generated UVL artifact and its metrics.
 */
import { useState } from "react"
import { Layers, CheckCircle, Maximize2, Trash2, X } from "lucide-react"

/**
 * Displays the PIM stage after the CIM-to-PIM transformation finishes.
 *
 * This component renders the generated UVL text, the interaction status, and the PIM
 * metrics that help the user inspect the intermediate transformation result.
 */
export const PIM = ({ uvlContent, metrics, interactionStatus, onClear }) => {
  const hasContent = !!uvlContent
  const [isFullscreen, setIsFullscreen] = useState(false)

  /**
   * Renders the fullscreen viewer used to inspect the generated UVL artifact in detail.
   *
   * This helper stays inside the PIM component because the panel owns the fullscreen
   * state and the current UVL text shown in both the card and the expanded view.
   */
  const FullscreenModal = () => {
    if (!isFullscreen) return null

    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center bg-ctp-base/95 p-8 backdrop-blur-sm"
        onClick={() => setIsFullscreen(false)}
      >
        <div
          className="relative flex h-full w-full max-w-7xl flex-col overflow-hidden rounded-2xl border border-ctp-surface1 bg-ctp-mantle shadow-2xl shadow-black/30"
          onClick={(event) => event.stopPropagation()}
        >
          <button
            type="button"
            onClick={() => setIsFullscreen(false)}
            className="absolute right-4 top-4 z-10 rounded-lg bg-ctp-surface0 p-2 text-ctp-text transition-colors hover:bg-ctp-surface1"
            aria-label="Close fullscreen"
          >
            <X className="h-6 w-6" />
          </button>
          <div className="border-b border-ctp-surface1 px-6 py-5 pr-20">
            <h3 className="text-2xl font-bold text-ctp-text">PIM</h3>
            <p className="text-base font-semibold text-[#a0988c]">UVL (Universal Variability Language)</p>
          </div>
          <textarea
            readOnly
            className="h-full w-full resize-none bg-ctp-crust p-6 font-mono text-sm leading-relaxed text-ctp-text focus:outline-none"
            value={uvlContent}
          />
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="flex flex-col h-full bg-ctp-surface0 rounded-xl shadow-xl border-2 border-ctp-surface2 transition-all duration-300 hover:border-ctp-surface1">
        {/* Panel header */}
        <div className="px-4 py-5 border-b border-ctp-surface1 bg-ctp-surface0/20 rounded-t-xl flex items-center justify-between shrink-0 h-20">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="p-2.5 bg-ctp-surface1 rounded-lg">
              <Layers className="w-8 h-8 text-ctp-mauve" />
            </div>
            <div className="min-w-0 text-left">
              <h3 className="font-bold text-ctp-text text-2xl">PIM</h3>
              <p className="text-lg text-[#a0988c] font-semibold hidden xl:block">
                UVL (Universal Variability Language)
              </p>
            </div>
          </div>

          {interactionStatus === "loading" ? (
            <span className="px-3 py-1 bg-ctp-blue/20 text-ctp-blue border border-ctp-blue/30 text-sm font-semibold rounded-full flex items-center gap-1.5 shadow-sm shrink-0">
              Preparing
            </span>
          ) : hasContent ? (
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => setIsFullscreen(true)}
                className="px-3 py-1.5 bg-ctp-blue/20 hover:bg-ctp-blue/30 text-ctp-blue border border-ctp-blue/30 text-sm font-semibold rounded-lg flex items-center gap-1.5 shadow-sm transition-colors"
                title="View fullscreen"
              >
                <Maximize2 className="w-4 h-4" />
                Fullscreen
              </button>
              <span className="px-4 py-1.5 border text-base font-semibold rounded-full flex items-center gap-2 shadow-sm shrink-0 bg-[#a6e3a1]/20 border-[#a6e3a1]/30 text-[#a6e3a1]">
                <CheckCircle className="h-4.5 w-4.5" /> Ready
              </span>
              <button
                type="button"
                onClick={onClear}
                className="rounded-lg border border-ctp-surface0 bg-ctp-crust p-2.5 text-ctp-overlay1 shadow-sm transition-all hover:border-ctp-red/30 hover:bg-ctp-red/20 hover:text-ctp-red"
                title="Clear PIM and downstream results"
                aria-label="Clear PIM and downstream results"
              >
                <Trash2 className="h-4.5 w-4.5" />
              </button>
            </div>
          ) : null}
        </div>

        {/* UVL content */}
        <div className="flex-1 p-0 overflow-hidden flex flex-col relative bg-ctp-crust">
          {hasContent ? (
            <textarea
              readOnly
              className="w-full h-full p-6 bg-ctp-crust text-ctp-text font-mono text-sm leading-relaxed rounded-none resize-none focus:outline-none scrollbar-thin scrollbar-thumb-ctp-surface1 scrollbar-track-ctp-crust"
              value={uvlContent}
            />
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center m-6 py-10 rounded-lg bg-ctp-mantle/50">
              <p className="text-[#a0988c] text-xl mb-6 text-center px-6 font-semibold">
                Waiting for i* to UVL transformation...
              </p>
            </div>
          )}
        </div>

        {/* Metrics area */}
        <div className="shrink-0 bg-ctp-mantle border-t border-ctp-surface0/50 p-4">
          <div className="min-h-[104px] rounded-lg bg-ctp-mantle/40 p-4 overflow-y-auto max-h-[300px]">
            {metrics ? (
              <div className="space-y-2">
                <h4 className="text-ctp-text font-bold text-sm mb-3">PIM Metrics</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-ctp-surface0/50 p-2 rounded">
                    <span className="text-[#a0988c]">Total Features:</span>
                    <span className="text-ctp-text font-semibold ml-2">
                      {metrics.total_features || 0}
                    </span>
                  </div>

                  {metrics.features_by_category && Object.keys(metrics.features_by_category).length > 0 && (
                    <div className="bg-ctp-surface0/50 p-2 rounded col-span-2">
                      <span className="text-[#a0988c] font-semibold">By Category:</span>
                      <div className="mt-1 space-y-1">
                        {Object.entries(metrics.features_by_category).map(([cat, count]) => (
                          <div key={cat} className="text-ctp-text text-xs">
                            {cat}: <span className="font-semibold">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="bg-ctp-surface0/50 p-2 rounded">
                    <span className="text-[#a0988c]">Constraints:</span>
                    <span className="text-ctp-text font-semibold ml-2">
                      {metrics.constraints || 0}
                    </span>
                  </div>

                </div>
              </div>
            ) : (
              <div className="min-h-[72px] border border-dashed border-ctp-overlay0/30 rounded-lg flex items-center justify-center px-4 bg-ctp-mantle/10">
                <span className="text-[#a0988c] text-xl font-semibold italic">
                  No metrics available
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
      <FullscreenModal />
    </>
  )
}
