/**
 * Home page that introduces the product and links back to the editor.
 */

import {
  ArrowRight,
  Code,
  Github,
  GitBranch,
  Layout,
  ShieldCheck,
  Sparkles,
  Target,
  Workflow,
} from "lucide-react"

const featureCards = [
  {
    icon: Target,
    title: "Model the problem",
    description: "Describe stakeholders, goals, tasks, resources, and quality concerns before making technical decisions.",
  },
  {
    icon: Workflow,
    title: "Guide the design",
    description: "Move from requirements to variability and architectural views through structured model transformations.",
  },
  {
    icon: Layout,
    title: "Explore the solution",
    description: "Understand the main components behind the workflow and how they connect from goals to system design.",
  },
]

const workflowStages = [
  {
    label: "Goal Model",
    subtitle: "Computation Independent Model",
    notation: "iStar 2.0",
    accent: "text-ctp-blue border-ctp-blue/20 bg-ctp-blue/10",
  },
  {
    label: "Variability Model",
    subtitle: "Design decisions and variability",
    notation: "Extended Feature Model / UVL",
    accent: "text-ctp-mauve border-ctp-mauve/20 bg-ctp-mauve/10",
  },
  {
    label: "Architecture Model",
    subtitle: "Preliminary system architecture",
    notation: "Quantum-UML",
    accent: "text-ctp-teal border-ctp-teal/20 bg-ctp-teal/10",
  },
]

const languageCards = [
  {
    icon: Target,
    eyebrow: "Intentions",
    eyebrowColor: "text-ctp-blue/50",
    title: "iStar 2.0",
    description: "Models stakeholder goals, actors, dependencies, and system intentions.",
    note: "Captures the problem space before design decisions.",
    noteColor: "text-ctp-blue",
    accent: "text-ctp-blue bg-ctp-blue/10 border-ctp-blue/20",
  },
  {
    icon: Layout,
    eyebrow: "Decisions",
    eyebrowColor: "text-ctp-mauve/50",
    title: "Extended FM / UVL",
    description: "Models design variability, alternatives, and key HQC decision points.",
    note: "Makes the transition from requirements to design choices explicit.",
    noteColor: "text-ctp-mauve",
    accent: "text-ctp-mauve bg-ctp-mauve/10 border-ctp-mauve/20",
  },
  {
    icon: Code,
    eyebrow: "Structure",
    eyebrowColor: "text-ctp-teal/50",
    title: "QuantumUML",
    description: "Models the preliminary architecture of the hybrid system.",
    note: "Translates design decisions into a structural view.",
    noteColor: "text-ctp-teal",
    accent: "text-ctp-teal bg-ctp-teal/10 border-ctp-teal/20",
  },
]

const operationsCards = [
  {
    icon: GitBranch,
    eyebrow: "Traceability",
    eyebrowColor: "text-ctp-blue/50",
    title: "Transformation rules",
    description: "Map elements across levels and keep vertical traceability between models.",
    accent: "text-ctp-blue bg-ctp-blue/10 border-ctp-blue/20",
  },
  {
    icon: Layout,
    eyebrow: "Variability",
    eyebrowColor: "text-ctp-mauve/50",
    title: "Explicit variability",
    description: "Represent decisions, alternatives, and key design points in a dedicated artifact.",
    accent: "text-ctp-mauve bg-ctp-mauve/10 border-ctp-mauve/20",
  },
  {
    icon: ShieldCheck,
    eyebrow: "Semantics",
    eyebrowColor: "text-ctp-teal/50",
    title: "Semantic support",
    description: "Use AI-assisted review when rule-based mappings are not enough.",
    accent: "text-ctp-teal bg-ctp-teal/10 border-ctp-teal/20",
  },
]

const SectionHeading = ({ title, description, centered = false }) => (
  <div className={centered ? "mx-auto max-w-3xl text-center" : "max-w-3xl"}>
    <h2 className="text-4xl md:text-5xl font-black tracking-tight text-ctp-text">{title}</h2>
    <p className="mt-5 text-lg leading-8 text-ctp-subtext0">{description}</p>
  </div>
)

const WorkflowArrow = () => (
  <div className="hidden items-center justify-center lg:flex">
    <div className="flex flex-col items-center gap-3 text-center text-ctp-overlay1">
      <svg width="86" height="42" viewBox="0 0 86 42" fill="none" xmlns="http://www.w3.org/2000/svg" className="overflow-visible">
        <path d="M6 23C24 8 47 8 74 23" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path d="M68 17L75 23L69 29" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <span className="text-[9px] font-bold uppercase tracking-[0.22em]">Transformation Rules</span>
    </div>
  </div>
)

/**
 * Renders the public-facing landing page while keeping the editor one click away.
 */
export const HomePage = ({ onOpenEditor }) => {
  return (
    <div className="min-h-screen bg-ctp-base text-ctp-text selection:bg-ctp-mauve selection:text-ctp-base">
      <header className="sticky top-0 z-40 border-b border-ctp-surface0 bg-ctp-base/85 backdrop-blur">
        <div className="mx-auto flex h-20 w-full max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-ctp-mauve/30 bg-ctp-mauve/10 text-ctp-mauve">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xl font-black tracking-tight">MDD-HQC</div>
            </div>
          </div>

          <nav className="hidden items-center gap-6 text-sm font-semibold text-ctp-subtext0 md:flex">
            <a href="#overview" className="transition-colors hover:text-ctp-text">Overview</a>
            <a href="#workflow" className="transition-colors hover:text-ctp-text">Workflow</a>
            <a href="#languages" className="transition-colors hover:text-ctp-text">Languages</a>
            <a href="#operates" className="transition-colors hover:text-ctp-text">Operates</a>
          </nav>

          <button
            type="button"
            onClick={onOpenEditor}
            className="rounded-2xl bg-ctp-mauve px-5 py-3 text-sm font-bold text-ctp-base shadow-lg shadow-ctp-mauve/20 transition-all hover:scale-[1.02] hover:bg-ctp-pink active:scale-[0.99]"
          >
            Open Editor
          </button>
        </div>
      </header>

      <main>
        <section className="relative overflow-hidden px-6 pb-24 pt-24 md:pb-32 md:pt-32">
          <div className="absolute left-1/2 top-0 -z-10 h-[34rem] w-[70rem] -translate-x-1/2 rounded-full bg-ctp-mauve/10 blur-[120px]" />
          <div className="mx-auto flex max-w-6xl flex-col items-center text-center">
            <img
              src="/images/logo.png"
              alt="MDD-HQC"
              className="mb-10 h-auto w-full max-w-[40rem] drop-shadow-2xl"
            />
            <h1 className="mt-2 max-w-6xl text-4xl font-black tracking-tight text-ctp-mauve md:text-6xl md:leading-[1.1]">
              MDD-HQC: A goal-oriented, model-driven approach to designing hybrid quantum-classical systems.
            </h1>
            <p className="mt-8 max-w-3xl text-lg leading-8 text-ctp-subtext0 md:text-xl">
              Understand requirements, structure design decisions, and move from goals to architectural models through a guided workflow.
            </p>
            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <button
                type="button"
                onClick={onOpenEditor}
                className="flex items-center justify-center gap-3 rounded-2xl bg-ctp-mauve px-8 py-4 text-lg font-black text-ctp-base shadow-xl shadow-ctp-mauve/20 transition-all hover:scale-[1.02] hover:bg-ctp-pink active:scale-[0.99]"
              >
                Open Editor <ArrowRight className="h-5 w-5" />
              </button>
              <a
                href="https://github.com/JessusTM/MDD-HQC"
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-center gap-3 rounded-2xl border border-ctp-surface1 bg-ctp-surface0 px-8 py-4 text-lg font-bold text-ctp-text transition-colors hover:bg-ctp-surface1"
              >
                <Github className="h-5 w-5" />
                Repository
              </a>
            </div>
          </div>
        </section>

        <section id="overview" className="bg-ctp-mantle px-6 py-24">
          <div className="mx-auto max-w-7xl">
            <SectionHeading
              title="What is MDD-HQC?"
              description="MDD-HQC is a design support application that helps users model requirements, guide transformations, and structure hybrid quantum-classical system solutions across multiple abstraction levels."
            />
            <div className="mt-8 h-2 w-16 rounded-full bg-ctp-mauve" />
            <div className="mt-14 grid gap-6 md:grid-cols-3">
              {featureCards.map(({ icon: Icon, title, description }) => (
                <article key={title} className="rounded-3xl border border-ctp-surface0 bg-ctp-base p-8 shadow-xl shadow-black/10">
                  <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-ctp-mauve/20 bg-ctp-mauve/10 text-ctp-mauve">
                    <Icon className="h-7 w-7" />
                  </div>
                  <h3 className="mt-6 text-2xl font-bold text-ctp-text">{title}</h3>
                  <p className="mt-4 text-base leading-7 text-ctp-subtext0">{description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="workflow" className="px-6 py-24">
          <div className="mx-auto max-w-7xl">
            <SectionHeading
              centered
              title="Model-Driven Workflow"
              description="Designing hybrid quantum-classical systems is challenging because requirements, variability, and architecture must remain connected across different abstraction levels. MDD-HQC addresses this through a model-driven workflow."
            />
            <p className="mx-auto mt-6 max-w-3xl text-center text-base italic leading-7 text-ctp-subtext1">
              Instead of jumping directly into implementation, the workflow starts from problem understanding and progressively refines the solution into connected design artifacts.
            </p>
            <div className="mt-16 grid gap-6 lg:grid-cols-[minmax(0,1fr)_110px_minmax(0,1fr)_110px_minmax(0,1fr)] lg:items-center">
              <article className={`rounded-[2rem] border p-8 text-center shadow-xl shadow-black/10 ${workflowStages[0].accent}`}>
                <div className="text-3xl font-black">{workflowStages[0].label}</div>
                <div className="mt-3 text-xs font-bold uppercase tracking-[0.25em] opacity-80">{workflowStages[0].subtitle}</div>
                <div className="mx-auto mt-8 h-px w-16 bg-current opacity-30" />
                <div className="mt-8 text-sm font-semibold text-ctp-subtext0">
                  Notation: <span className="text-ctp-text">{workflowStages[0].notation}</span>
                </div>
              </article>
              <WorkflowArrow />
              <article className={`rounded-[2rem] border p-8 text-center shadow-xl shadow-black/10 ${workflowStages[1].accent}`}>
                <div className="text-3xl font-black">{workflowStages[1].label}</div>
                <div className="mt-3 text-xs font-bold uppercase tracking-[0.25em] opacity-80">{workflowStages[1].subtitle}</div>
                <div className="mx-auto mt-8 h-px w-16 bg-current opacity-30" />
                <div className="mt-8 text-sm font-semibold text-ctp-subtext0">
                  Notation: <span className="text-ctp-text">{workflowStages[1].notation}</span>
                </div>
              </article>
              <WorkflowArrow />
              <article className={`rounded-[2rem] border p-8 text-center shadow-xl shadow-black/10 ${workflowStages[2].accent}`}>
                <div className="text-3xl font-black">{workflowStages[2].label}</div>
                <div className="mt-3 text-xs font-bold uppercase tracking-[0.25em] opacity-80">{workflowStages[2].subtitle}</div>
                <div className="mx-auto mt-8 h-px w-16 bg-current opacity-30" />
                <div className="mt-8 text-sm font-semibold text-ctp-subtext0">
                  Notation: <span className="text-ctp-text">{workflowStages[2].notation}</span>
                </div>
              </article>
            </div>
            <div className="mt-10 text-center text-sm font-bold uppercase tracking-[0.35em] text-ctp-overlay1">
              Goals -> Design Decisions -> Preliminary Architecture
            </div>
          </div>
        </section>

        <section id="languages" className="bg-ctp-mantle px-6 py-24">
          <div className="mx-auto max-w-7xl">
            <SectionHeading
              centered
              title="The role of each language"
              description="Each language in the solution captures a different concern and keeps the transition between levels explicit."
            />
            <div className="mt-16 grid gap-6 lg:grid-cols-3">
              {languageCards.map(({ icon: Icon, eyebrow, eyebrowColor, title, description, note, noteColor, accent }) => (
                <article key={title} className="rounded-[2rem] border border-ctp-surface0 bg-ctp-base p-8 text-center shadow-xl shadow-black/10">
                  <div className={`mx-auto flex h-16 w-16 items-center justify-center rounded-3xl border ${accent}`}>
                    <Icon className="h-8 w-8" />
                  </div>
                  <div className={`mt-8 text-xs font-black uppercase tracking-[0.35em] ${eyebrowColor}`}>{eyebrow}</div>
                  <h3 className="mt-4 text-3xl font-black text-ctp-text">{title}</h3>
                  <p className="mt-5 min-h-[96px] text-lg leading-8 text-ctp-subtext0">{description}</p>
                  <div className={`mt-8 border-t border-ctp-surface0 pt-6 text-sm font-bold ${noteColor}`}>Why: {note}</div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="operates" className="px-6 py-24">
          <div className="mx-auto max-w-7xl">
            <SectionHeading
              centered
              title="How MDD-HQC operates"
              description="The workflow is supported by explicit transformations, variability modeling, and semantic review when rules alone are not enough."
            />
            <div className="mt-16 grid gap-6 lg:grid-cols-3">
              {operationsCards.map(({ icon: Icon, eyebrow, eyebrowColor, title, description, accent }) => (
                <article key={title} className="rounded-[2rem] border border-ctp-surface0 bg-ctp-mantle p-8 text-center shadow-xl shadow-black/10">
                  <div className={`mx-auto flex h-16 w-16 items-center justify-center rounded-3xl border ${accent}`}>
                    <Icon className="h-8 w-8" />
                  </div>
                  <div className={`mt-8 text-xs font-black uppercase tracking-[0.35em] ${eyebrowColor}`}>{eyebrow}</div>
                  <h3 className="mt-4 text-3xl font-black text-ctp-text">{title}</h3>
                  <p className="mt-5 text-lg leading-8 text-ctp-subtext0">{description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-ctp-surface0 px-6 py-10">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 md:flex-row">
          <div className="flex items-center gap-3 text-ctp-text">
            <Sparkles className="h-5 w-5 text-ctp-mauve" />
            <span className="font-bold">MDD-HQC</span>
          </div>
          <p className="text-sm text-ctp-overlay1">© 2026 MDD-HQC. Built for the Quantum Future.</p>
        </div>
      </footer>
    </div>
  )
}
