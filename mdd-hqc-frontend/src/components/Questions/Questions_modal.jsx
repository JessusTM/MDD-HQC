import { X } from "lucide-react"

const QuestionsModal = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ctp-base/70 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-2xl rounded-2xl border border-ctp-surface1 bg-ctp-mantle shadow-2xl shadow-black/30">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 rounded-lg border border-ctp-surface1 bg-ctp-surface0/80 p-2 text-ctp-text transition-colors hover:bg-ctp-surface1"
          aria-label="Close modal"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="p-6 pr-16">{children}</div>
      </div>
    </div>
  )
}

export default QuestionsModal
