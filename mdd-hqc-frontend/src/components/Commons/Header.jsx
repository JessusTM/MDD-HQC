/**
 * Top-level header components used by the main application shell.
 */

import { Home, Menu } from "lucide-react"

/**
 * Renders the decorative AI toggle icon used by the application header.
 *
 * This helper exists so the header can reuse the custom sparkles icon without mixing
 * the SVG markup directly into the main header structure.
 */
const SparklesIcon = ({ className = "" }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
    <path d="M5 3v4" />
    <path d="M19 17v4" />
    <path d="M3 5h4" />
    <path d="M17 19h4" />
  </svg>
)

/**
 * Displays the sticky application header with examples, AI mode, and repository access.
 *
 * This component is used by the main app shell to keep navigation and global controls
 * visible while the user moves through the transformation workspace.
 */
export const Header = ({ onOpenExamples, onGoHome, isAiEnabled, onToggleAi }) => {
  return (
    <header className="bg-ctp-mantle border-b border-ctp-surface0 shrink-0 z-50 shadow-lg shadow-black/20 h-24 sticky top-0">
      <div className="w-full max-w-[1920px] mx-auto px-6 h-full flex items-center justify-center relative pt-3 pb-3">
        <div className="absolute left-6 flex items-center gap-3">
          <button
            type="button"
            onClick={onOpenExamples}
            className="flex items-center gap-3 rounded-2xl border border-[#45475a] bg-ctp-surface0 px-3.5 py-3 text-sm font-bold uppercase tracking-[0.2em] leading-none text-ctp-mauve transition-all hover:border-[#585b70] hover:bg-ctp-surface1"
          >
            <Menu className="h-6 w-6" />
            Examples
          </button>

          <button
            type="button"
            onClick={onGoHome}
            className="flex items-center gap-3 rounded-2xl border border-[#45475a] bg-ctp-surface0 px-3.5 py-3 text-sm font-bold uppercase tracking-[0.2em] leading-none text-ctp-blue transition-all hover:border-[#585b70] hover:bg-ctp-surface1"
          >
            <Home className="h-6 w-6" />
            Home
          </button>
        </div>

        {/* Project identity */}
        <div className="text-center mt-1">
          <h1 className="text-4xl font-bold text-ctp-text tracking-tight leading-tight">
            MDD-HQC
          </h1>
          <p className="text-xl text-[#a0988c] font-semibold mt-1 mb-1">
            A Goal-Oriented Model-Driven Solution for the Design of Hybrid Quantum-Classical Systems
          </p>
        </div>

        {/* Global actions */}
        <div className="absolute right-3 sm:right-6 flex items-center gap-3">
          <button
            type="button"
            onClick={onToggleAi}
            role="switch"
            aria-checked={isAiEnabled}
            className={`group inline-flex h-12 items-center gap-3 rounded-full border px-3 transition-all duration-200 hover:scale-[1.02] hover:shadow-lg active:scale-[0.99] sm:px-4 ${
              isAiEnabled
                ? "border-[#cba6f7] bg-[#1e1e2e]"
                : "border-[#7f849c] bg-[#313244]"
            }`}
          >
            <span className={`transition-transform duration-200 group-hover:rotate-12 ${
              isAiEnabled ? "text-[#cba6f7]" : "text-[#7f849c]"
            }`}>
              <SparklesIcon className="h-4 w-4 sm:h-5 sm:w-5" />
            </span>
            <span className={`text-left text-xs font-bold uppercase tracking-[0.14em] sm:text-sm ${
              isAiEnabled ? "text-[#f5e0dc]" : "text-[#bac2de]"
            }`}>
              AI Assist
            </span>
            <span
              className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors ${
                isAiEnabled ? "bg-ctp-mauve" : "bg-ctp-surface1"
              }`}
              aria-hidden="true"
            >
              <span
                className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform ${
                  isAiEnabled ? "translate-x-5" : "translate-x-1"
                }`}
              />
            </span>
          </button>

          <a
            href="https://github.com/JessusTM/MDD-HQC"
            target="_blank"
            rel="noreferrer"
            aria-label="Open GitHub repository"
            className="flex h-12 items-center gap-2 rounded-full bg-ctp-surface0 px-3 text-[#a0988c] transition-colors hover:text-ctp-text sm:px-6"
          >
            <svg
              viewBox="0 0 98 96"
              aria-hidden="true"
              className="h-4 w-4 fill-current sm:h-5 sm:w-5"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M41.4395 69.3848C28.8066 67.8535 19.9062 58.7617 19.9062 46.9902C19.9062 42.2051 21.6289 37.0371 24.5 33.5918C23.2559 30.4336 23.4473 23.7344 24.8828 20.959C28.7109 20.4805 33.8789 22.4902 36.9414 25.2656C40.5781 24.1172 44.4062 23.543 49.0957 23.543C53.7852 23.543 57.6133 24.1172 61.0586 25.1699C64.0254 22.4902 69.2891 20.4805 73.1172 20.959C74.457 23.543 74.6484 30.2422 73.4043 33.4961C76.4668 37.1328 78.0937 42.0137 78.0937 46.9902C78.0937 58.7617 69.1934 67.6621 56.3691 69.2891C59.623 71.3945 61.8242 75.9883 61.8242 81.252L61.8242 91.2051C61.8242 94.0762 64.2168 95.7031 67.0879 94.5547C84.4102 87.9512 98 70.6289 98 49.1914C98 22.1074 75.9883 6.69539e-07 48.9043 4.309e-07C21.8203 1.92261e-07 -1.9479e-07 22.1074 -4.3343e-07 49.1914C-6.20631e-07 70.4375 13.4941 88.0469 31.6777 94.6504C34.2617 95.6074 36.75 93.8848 36.75 91.3008L36.75 83.6445C35.4102 84.2188 33.6875 84.6016 32.1562 84.6016C25.8398 84.6016 22.1074 81.1563 19.4277 74.7441C18.375 72.1602 17.2266 70.6289 15.0254 70.3418C13.877 70.2461 13.4941 69.7676 13.4941 69.1934C13.4941 68.0449 15.4082 67.1836 17.3223 67.1836C20.0977 67.1836 22.4902 68.9063 24.9785 72.4473C26.8926 75.2227 28.9023 76.4668 31.2949 76.4668C33.6875 76.4668 35.2187 75.6055 37.4199 73.4043C39.0469 71.7773 40.291 70.3418 41.4395 69.3848Z" />
            </svg>
            <span className="text-sm sm:text-2xl font-bold">
              v1.2.2
            </span>
          </a>
        </div>
      </div>
    </header>
  )
}
