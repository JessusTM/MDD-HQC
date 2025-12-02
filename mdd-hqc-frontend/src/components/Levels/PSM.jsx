import { Code, CheckCircle } from "lucide-react"

export const PSM = ({ plantUml }) => {
  const hasContent = !!plantUml

  return (
    <div className="flex flex-col h-full bg-ctp-surface0 rounded-xl shadow-xl border-2 border-ctp-surface2 transition-all duration-300 hover:border-ctp-surface1">
      <div className="p-5 border-b border-ctp-surface1 bg-ctp-surface0/20 rounded-t-xl flex items-center justify-between shrink-0 h-20">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-ctp-surface1 rounded-lg">
            <Code className="w-8 h-8 text-ctp-teal" />
          </div>
          <div>
            <h3 className="font-bold text-ctp-text text-2xl">PSM</h3>
            <p className="text-lg text-ctp-subtext0 font-semibold hidden xl:block">
              UML Cuántico / Qiskit
            </p>
          </div>
        </div>

        {hasContent && (
          <span className="px-3 py-1 bg-ctp-green/20 text-ctp-green border border-ctp-green/30 text-sm font-semibold rounded-full flex items-center gap-1.5 shadow-sm">
            <CheckCircle className="w-4 h-4" /> Listo
          </span>
        )}
      </div>

      <div className="flex-1 p-0 overflow-hidden flex flex-col relative bg-ctp-crust">
        {hasContent ? (
          <textarea
            readOnly
            className="w-full h-full p-6 bg-ctp-crust text-ctp-text font-mono text-base leading-relaxed rounded-none resize-none focus:outline-none scrollbar-thin scrollbar-thumb-ctp-surface1 scrollbar-track-ctp-crust"
            value={plantUml}
          />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center m-6 py-10 rounded-lg bg-ctp-mantle/50">
            <p className="text-ctp-subtext0 text-xl mb-6 text-center px-6 font-semibold">
              Esperando transformación de UVL a Código…
            </p>
          </div>
        )}
      </div>

      <div className="shrink-0 bg-ctp-mantle border-t border-ctp-surface0/50 p-4">
        <div className="h-[104px] rounded-lg bg-ctp-mantle/40 flex items-center justify-center">
          <span className="text-ctp-subtext0 text-xl font-semibold italic">
            Sin métricas disponibles
          </span>
        </div>
      </div>
    </div>
  )
}
