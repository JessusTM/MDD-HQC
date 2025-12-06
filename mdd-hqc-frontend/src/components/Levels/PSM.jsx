import { useState } from "react"
import { Code, CheckCircle, Maximize2, X } from "lucide-react"
import { encode } from "plantuml-encoder"

export const PSM = ({ pumlContent, metrics }) => {
  const hasContent = !!pumlContent
  const [isFullscreen, setIsFullscreen] = useState(false)

  const getPlantUmlUrl = (content) => {
    if (!content) return null
    const encoded = encode(content)
    return `http://www.plantuml.com/plantuml/svg/${encoded}`
  }

  const plantUmlUrl = hasContent ? getPlantUmlUrl(pumlContent) : null

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
            aria-label="Cerrar fullscreen"
          >
            <X className="w-6 h-6 text-ctp-text" />
          </button>
          {plantUmlUrl && (
            <img
              src={plantUmlUrl}
              alt="Diagrama UML Cuántico"
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
      <div className="flex flex-col h-full bg-ctp-surface0 rounded-xl shadow-xl border-2 border-ctp-surface2 transition-all duration-300 hover:border-ctp-surface1">
        <div className="p-5 border-b border-ctp-surface1 bg-ctp-surface0/20 rounded-t-xl flex items-center justify-between shrink-0 h-20">
          <div className="flex items-center gap-4">
            <div className="p-2.5 bg-ctp-surface1 rounded-lg">
              <Code className="w-8 h-8 text-ctp-teal" />
            </div>
            <div>
              <h3 className="font-bold text-ctp-text text-2xl">PSM</h3>
              <p className="text-lg text-ctp-subtext0 font-semibold hidden xl:block">
                Quantum UML / PlantUML
              </p>
            </div>
          </div>

          {hasContent && (
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsFullscreen(true)}
                className="px-3 py-1.5 bg-ctp-blue/20 hover:bg-ctp-blue/30 text-ctp-blue border border-ctp-blue/30 text-sm font-semibold rounded-lg flex items-center gap-1.5 shadow-sm transition-colors"
                title="Ver en pantalla completa"
              >
                <Maximize2 className="w-4 h-4" />
                Fullscreen
              </button>
              <span className="px-3 py-1 bg-ctp-green/20 text-ctp-green border border-ctp-green/30 text-sm font-semibold rounded-full flex items-center gap-1.5 shadow-sm">
                <CheckCircle className="w-4 h-4" /> Listo
              </span>
            </div>
          )}
        </div>

        <div className="flex-1 p-0 overflow-auto flex flex-col relative bg-ctp-crust">
          {hasContent && plantUmlUrl ? (
            <div className="w-full h-full p-6 flex items-center justify-center">
              <img
                src={plantUmlUrl}
                alt="Diagrama UML Cuántico"
                className="max-w-full h-auto"
              />
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center m-6 py-10 rounded-lg bg-ctp-mantle/50">
              <p className="text-ctp-subtext0 text-xl mb-6 text-center px-6 font-semibold">
                Esperando transformación de UVL a UML…
              </p>
            </div>
          )}
        </div>

        <div className="shrink-0 bg-ctp-mantle border-t border-ctp-surface0/50 p-4">
          <div className="min-h-[104px] rounded-lg bg-ctp-mantle/40 p-4 overflow-y-auto max-h-[300px]">
            {metrics ? (
              <div className="space-y-2">
                <h4 className="text-ctp-text font-bold text-sm mb-3">Métricas PSM</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-ctp-surface0/50 p-2 rounded">
                    <span className="text-ctp-subtext0">Total Clases:</span>
                    <span className="text-ctp-text font-semibold ml-2">{metrics.total_classes || 0}</span>
                  </div>
                  <div className="bg-ctp-surface0/50 p-2 rounded">
                    <span className="text-ctp-subtext0">Dependencias:</span>
                    <span className="text-ctp-text font-semibold ml-2">{metrics.total_dependencies || 0}</span>
                  </div>
                  <div className="bg-ctp-surface0/50 p-2 rounded">
                    <span className="text-ctp-subtext0">Atributos:</span>
                    <span className="text-ctp-text font-semibold ml-2">{metrics.attributes || 0}</span>
                  </div>
                  <div className="bg-ctp-surface0/50 p-2 rounded">
                    <span className="text-ctp-subtext0">Métodos:</span>
                    <span className="text-ctp-text font-semibold ml-2">{metrics.methods || 0}</span>
                  </div>
                  {metrics.stereotypes && (
                    <>
                      <div className="bg-ctp-surface0/50 p-2 rounded">
                        <span className="text-ctp-subtext0">Algorithm:</span>
                        <span className="text-ctp-text font-semibold ml-2">{metrics.stereotypes.algorithm_classes || 0}</span>
                      </div>
                      <div className="bg-ctp-surface0/50 p-2 rounded">
                        <span className="text-ctp-subtext0">QuantumDriver:</span>
                        <span className="text-ctp-text font-semibold ml-2">{metrics.stereotypes.quantum_driver_classes || 0}</span>
                      </div>
                    </>
                  )}
                  {metrics.semantic_preservation && (
                    <div className="bg-ctp-surface0/50 p-2 rounded col-span-2">
                      <span className="text-ctp-subtext0 font-semibold">Preservación Semántica:</span>
                      <div className="mt-1 space-y-1 text-xs">
                        <div className="text-ctp-text">
                          Clases con comentarios: <span className="font-semibold">{metrics.semantic_preservation.classes_with_comments || 0}</span>
                        </div>
                        <div className="text-ctp-text">
                          Total comentarios: <span className="font-semibold">{metrics.semantic_preservation.total_comments || 0}</span>
                        </div>
                        <div className="text-ctp-text">
                          Clases con tagged values: <span className="font-semibold">{metrics.semantic_preservation.classes_with_tagged_values || 0}</span>
                        </div>
                        <div className="text-ctp-text">
                          Total tagged values: <span className="font-semibold">{metrics.semantic_preservation.total_tagged_values || 0}</span>
                        </div>
                      </div>
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
      <FullscreenModal />
    </>
  )
}