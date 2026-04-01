import { BookOpen, ChevronRight, Lightbulb, X } from "lucide-react"

export const ExamplesSidebar = ({ isOpen, onClose, onSelectExample }) => {
  const handleSelect = () => {
    onSelectExample?.({
      id: "chileespres",
      name: "ChileEsPres",
      url: "/examples/ChileEsPres.xml",
    })
    onClose?.()
  }

  return (
    <>
      <div
        className={[
          "fixed inset-0 z-[60] bg-ctp-base/70 backdrop-blur-sm transition-opacity duration-300",
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none",
        ].join(" ")}
        onClick={onClose}
      />

        <aside
          className={[
          "fixed left-0 top-0 z-[70] h-full w-full max-w-[540px] border-r border-ctp-surface1 bg-ctp-mantle shadow-2xl transition-transform duration-300",
          isOpen ? "translate-x-0" : "-translate-x-full",
        ].join(" ")}
      >
          <div className="flex h-full flex-col">
           <div className="flex items-center justify-between border-b border-ctp-surface1 px-6 py-6">
             <div className="flex items-center gap-4">
               <div className="rounded-xl bg-ctp-surface0 p-3">
                 <BookOpen className="h-6 w-6 text-ctp-mauve" />
               </div>
               <div>
                 <h2 className="text-3xl font-bold leading-none text-ctp-text">Examples</h2>
               </div>
             </div>

             <button
               type="button"
               onClick={onClose}
               className="flex h-12 w-12 items-center justify-center rounded-xl text-[#a0988c] transition-colors hover:bg-ctp-surface0 hover:text-ctp-text"
               aria-label="Close examples"
             >
               <X className="h-6 w-6" />
             </button>
          </div>

          <div className="flex-1 overflow-y-auto px-6 py-6">
            <div className="mb-6 rounded-2xl border border-ctp-blue/20 bg-ctp-blue/10 p-4">
              <div className="flex items-start gap-3">
                <Lightbulb className="mt-0.5 h-5 w-5 shrink-0 text-ctp-blue" />
                <p className="text-xl leading-8 text-[#a0988c]">
                  Use these examples to quickly explore the transformation flow and test the system without uploading your own model.
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={handleSelect}
              className="group w-full rounded-3xl border border-ctp-surface1 bg-ctp-surface0/40 p-6 text-left transition-all duration-300 hover:border-ctp-mauve/50 hover:bg-ctp-surface0"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-3xl font-bold text-ctp-text">ChileEsPres</div>
                  <p className="mt-3 text-xl leading-8 text-[#a0988c]">
                    Enterprise route-planning scenario with a quantum annealing module designed to produce improved routing plans for deliveries.
                  </p>
                </div>
                <ChevronRight className="mt-1 h-6 w-6 shrink-0 text-[#a0988c] transition-transform group-hover:translate-x-1 group-hover:text-ctp-text" />
              </div>

              <div className="mt-5 flex items-center gap-3">
                <span className="rounded-lg border border-ctp-mauve/30 bg-ctp-mauve/10 px-3 py-1 text-base font-bold uppercase tracking-wide text-ctp-mauve">
                  i* 2.0
                </span>
                <span className="rounded-lg border border-ctp-blue/30 bg-ctp-blue/10 px-3 py-1 text-base font-bold uppercase tracking-wide text-ctp-blue">
                  CIM
                </span>
              </div>
            </button>
          </div>
        </div>
      </aside>
    </>
  )
}
