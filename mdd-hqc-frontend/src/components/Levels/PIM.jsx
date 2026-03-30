import { Layers, CheckCircle } from "lucide-react"

export const PIM = ({ uvlContent, metrics }) => {
  const hasContent = !!uvlContent

  return (
    <div className="flex flex-col h-full bg-ctp-surface0 rounded-xl shadow-xl border-2 border-ctp-surface2 transition-all duration-300 hover:border-ctp-surface1">
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

        {hasContent && (
          <span className="px-3 py-1 bg-ctp-green/20 text-ctp-green border border-ctp-green/30 text-sm font-semibold rounded-full flex items-center gap-1.5 shadow-sm shrink-0">
            <CheckCircle className="w-4 h-4" /> Ready
          </span>
        )}
      </div>

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
  )
}
