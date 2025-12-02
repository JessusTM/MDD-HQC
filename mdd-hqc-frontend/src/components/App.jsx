import { CIM } from "./Levels/CIM"
import { PIM } from "./Levels/PIM"
import { PSM } from "./Levels/PSM"
import { Filter } from "./Filter/Filter"
import { Header } from "./Commons/Header"

export const App = () => {
  return (
    <div className="min-h-screen w-full bg-ctp-base text-ctp-text font-sans selection:bg-ctp-mauve selection:text-ctp-base flex flex-col">

      <Header />

      <main className="flex-1 flex flex-col w-full max-w-[1920px] mx-auto px-6 py-8">

        <div className="mb-8">
          <Filter />
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
            <CIM />
          </div>

          <div className="relative z-10 h-full">
            <PIM />
          </div>

          <div className="relative z-10 h-full">
            <PSM />
          </div>
        </div>
      </main>
    </div>
  )
}
