/**
 * PSM panel that displays the generated UML diagram and its metrics.
 */

import { useState } from "react"
import { Code, CheckCircle, Maximize2, Trash2, X } from "lucide-react"
import { encode } from "plantuml-encoder"

/**
 * Displays the PSM stage after the backend generates the PlantUML artifact.
 *
 * This component renders the UML preview, the fullscreen viewer, and the PSM metrics
 * used to inspect the final transformation result.
 */
export const PSM = ({ pumlContent, metrics, onClear }) => {
  const hasContent = !!pumlContent
  const [isFullscreen, setIsFullscreen] = useState(false)

  /**
   * Builds the PlantUML server URL for the generated diagram content.
   *
   * This helper is used by the PSM component and its fullscreen modal because both views
   * need the same encoded diagram URL derived from the current PlantUML text.
   */
  const getPlantUmlUrl = (content) => {
    if (!content) return null
    const encoded = encode(content)
    return `http://www.plantuml.com/plantuml/svg/${encoded}`
  }

  const plantUmlUrl = hasContent ? getPlantUmlUrl(pumlContent) : null

  /**
   * Renders the fullscreen viewer used to inspect the generated UML diagram in detail.
   *
   * This helper exists inside the PSM component because only this panel owns the modal
   * state and the PlantUML URL required by the fullscreen preview.
   */
  const FullscreenModal = () => {
    if (!isFullscreen) return null

    return (
      <div
        className="fixed inset-0 z-50 bg-ctp-base/95 backdrop-blur-sm flex items-center justify-center p-8"
        onClick={() => setIsFullscreen(false)}
      >
        <div className="relative w-full h-full flex items-center justify-center">
          <button
            onClick={() => setIsFullscreen(false)}
            className="absolute top-4 right-4 p-2 bg-ctp-surface0 hover:bg-ctp-surface1 rounded-lg transition-colors z-10"
            aria-label="Close fullscreen"
          >
            <X className="w-6 h-6 text-ctp-text" />
          </button>
          {plantUmlUrl && (
            <img
              src={plantUmlUrl}
              alt="Quantum UML diagram"
              className="max-w-full max-h-full object-contain"
              onClick={(e) => e.stopPropagation()}
            />
          )}
        </div>
      </div>
    )
  }

  return (
    <>
      {/* PSM panel */}
      <div className="flex flex-col h-full bg-ctp-surface0 rounded-xl shadow-xl border-2 border-ctp-surface2 transition-all duration-300 hover:border-ctp-surface1">
        {/* Panel header */}
        <div className="px-4 py-5 border-b border-ctp-surface1 bg-ctp-surface0/20 rounded-t-xl flex items-center justify-between shrink-0 h-20">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="p-2.5 bg-ctp-surface1 rounded-lg">
              <Code className="w-8 h-8 text-ctp-teal" />
            </div>
            <div className="min-w-0 text-left">
              <h3 className="font-bold text-ctp-text text-2xl">PSM</h3>
              <p className="text-lg text-[#a0988c] font-semibold hidden xl:block">
                UML with Quantum UML
              </p>
            </div>
          </div>

          {hasContent && (
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
              <span className="px-4 py-1.5 border text-base font-semibold rounded-full flex items-center gap-2 shadow-sm bg-[#a6e3a1]/20 border-[#a6e3a1]/30 text-[#a6e3a1]">
                <CheckCircle className="h-4.5 w-4.5" /> Ready
              </span>
              <button
                type="button"
                onClick={onClear}
                className="rounded-lg border border-ctp-surface0 bg-ctp-crust p-2.5 text-ctp-overlay1 shadow-sm transition-all hover:border-ctp-red/30 hover:bg-ctp-red/20 hover:text-ctp-red"
                title="Clear PSM result"
                aria-label="Clear PSM result"
              >
                <Trash2 className="h-4.5 w-4.5" />
              </button>
            </div>
          )}
        </div>

        {/* Diagram preview */}
        <div className="flex-1 p-0 overflow-auto flex flex-col relative bg-ctp-crust">
          {hasContent && plantUmlUrl ? (
            <div className="w-full h-full p-6 flex items-center justify-center">
              <img
                src={plantUmlUrl}
                alt="Quantum UML diagram"
                className="max-w-full h-auto"
              />
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center m-6 py-10 rounded-lg bg-ctp-mantle/50">
              <p className="text-[#a0988c] text-xl mb-6 text-center px-6 font-semibold">
                Waiting for UVL to UML transformation...
              </p>
            </div>
          )}
        </div>

        {/* Metrics area */}
        <div className="shrink-0 bg-ctp-mantle border-t border-ctp-surface0/50 p-4">
          <div className="min-h-[104px] rounded-lg bg-ctp-mantle/40 p-4 overflow-y-auto max-h-[300px]">
            {metrics ? (
              <div className="space-y-2">
                <h4 className="text-ctp-text font-bold text-sm mb-3">PSM Metrics</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-ctp-surface0/50 p-2 rounded">
                    <span className="text-[#a0988c]">Total classes:</span>
                    <span className="text-ctp-text font-semibold ml-2">{metrics.total_classes || 0}</span>
                  </div>
                  <div className="bg-ctp-surface0/50 p-2 rounded">
                    <span className="text-[#a0988c]">Dependencies:</span>
                    <span className="text-ctp-text font-semibold ml-2">{metrics.total_dependencies || 0}</span>
                  </div>
                  <div className="bg-ctp-surface0/50 p-2 rounded">
                    <span className="text-[#a0988c]">Attributes:</span>
                    <span className="text-ctp-text font-semibold ml-2">{metrics.attributes || 0}</span>
                  </div>
                  <div className="bg-ctp-surface0/50 p-2 rounded">
                    <span className="text-[#a0988c]">Methods:</span>
                    <span className="text-ctp-text font-semibold ml-2">{metrics.methods || 0}</span>
                  </div>
                  {metrics.stereotypes && (
                    <>
                      <div className="bg-ctp-surface0/50 p-2 rounded">
                        <span className="text-[#a0988c]">Algorithm:</span>
                        <span className="text-ctp-text font-semibold ml-2">{metrics.stereotypes.algorithm_classes || 0}</span>
                      </div>
                      <div className="bg-ctp-surface0/50 p-2 rounded">
                        <span className="text-[#a0988c]">QuantumDriver:</span>
                        <span className="text-ctp-text font-semibold ml-2">{metrics.stereotypes.quantum_driver_classes || 0}</span>
                      </div>
                    </>
                  )}
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
      {/* Fullscreen preview */}
      <FullscreenModal />
    </>
  )
}
