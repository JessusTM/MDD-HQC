export const Header = () => {
  return (
    <header className="bg-ctp-mantle border-b border-ctp-surface0 shrink-0 z-50 shadow-lg shadow-black/20 h-20 sticky top-0">
      <div className="w-full max-w-[1920px] mx-auto px-6 h-full flex items-center justify-center relative pt-3 pb-2">
        <div className="text-center mt-1">
          <h1 className="text-4xl font-bold text-ctp-text tracking-tight leading-tight">
            MDD-HQC
          </h1>
          <p className="text-xl text-ctp-subtext0 font-semibold mt-1">
            Prototipo orientado a agentes para sistemas híbridos
          </p>
        </div>

        <div className="absolute right-6 hidden md:flex items-center gap-2 text-base text-ctp-subtext1 bg-ctp-surface0 px-6 py-2 rounded-full">
          <span className="text-2xl font-bold">
            v1.0.1
          </span>
        </div>
      </div>
    </header>
  )
}