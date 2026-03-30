import { Menu } from "lucide-react"

export const Header = ({ onOpenExamples }) => {
  return (
    <header className="bg-ctp-mantle border-b border-ctp-surface0 shrink-0 z-50 shadow-lg shadow-black/20 h-24 sticky top-0">
      <div className="w-full max-w-[1920px] mx-auto px-6 h-full flex items-center justify-center relative pt-3 pb-3">
        <button
          type="button"
          onClick={onOpenExamples}
          className="absolute left-6 flex items-center gap-2 rounded-2xl border border-[#FAB387] bg-ctp-surface0 px-3.5 py-3 text-sm font-bold uppercase tracking-[0.2em] text-ctp-mauve transition-all hover:bg-ctp-surface1"
        >
          <Menu className="h-5 w-5" />
          Examples
        </button>

        <div className="text-center mt-1">
          <h1 className="text-4xl font-bold text-ctp-text tracking-tight leading-tight">
            MDD-HQC
          </h1>
          <p className="text-xl text-[#a0988c] font-semibold mt-1 mb-1">
            A Goal-Oriented Model-Driven Solution for the Design of Hybrid Quantum-Classical Systems
          </p>
        </div>

        <div className="absolute right-6 hidden md:flex items-center gap-2 text-base text-[#a0988c] bg-ctp-surface0 px-6 py-2 rounded-full">
          <span className="text-2xl font-bold">
            v1.0.1
          </span>
        </div>
      </div>
    </header>
  )
}
