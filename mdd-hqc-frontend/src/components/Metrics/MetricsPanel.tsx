import type {
  ArchitectureMetrics,
  IStarMetrics,
  MetricRowProps,
  MetricsPanelProps,
  UVLMetrics,
} from "../../types/metrics"

const formatDuration = (value?: number | null) => {
  if (value == null) return "—"
  if (value >= 1000) {
    return `${(value / 1000).toFixed(2)} s`
  }
  return `${Math.round(value)} ms`
}

const formatNumber = (value?: number | null) => {
  if (value == null) return "—"
  return value.toLocaleString("es-ES")
}

const formatPercentage = (value?: number | null) => {
  if (value == null) return "—"
  return `${value.toFixed(1)} %`
}

const StageDefinitions = [
  { key: "istar", label: "i* 2.0" },
  { key: "uvl", label: "UVL" },
  { key: "architecture", label: "Arquitectura" },
] as const satisfies ReadonlyArray<{ key: keyof MetricsPanelProps["metrics"]; label: string }>

const renderRows = (
  key: keyof MetricsPanelProps["metrics"],
  data: MetricsPanelProps["metrics"][keyof MetricsPanelProps["metrics"]],
) => {
  switch (key) {
    case "istar": {
      const metrics = data as IStarMetrics
      return (
        <>
          <MetricRow label="Tiempo de transformación" value={formatDuration(metrics.transformationTimeMs)} />
          <MetricRow label="# Goals" value={formatNumber(metrics.goalsCount)} />
          <MetricRow label="# Softgoals" value={formatNumber(metrics.softgoalsCount)} />
          <MetricRow label="# Recursos" value={formatNumber(metrics.resourcesCount)} />
          <MetricRow label="# Tareas" value={formatNumber(metrics.tasksCount)} isLast />
        </>
      )
    }
    case "uvl": {
      const metrics = data as UVLMetrics
      return (
        <>
          <MetricRow label="Tiempo de transformación" value={formatDuration(metrics.transformationTimeMs)} />
          <MetricRow label="# Features" value={formatNumber(metrics.featuresCount)} />
          <MetricRow label="# Constraints" value={formatNumber(metrics.constraintsCount)} />
          <MetricRow label="% Goals → Features" value={formatPercentage(metrics.goalsConvertedPercent)} />
          <MetricRow label="Pérdida semántica" value={formatPercentage(metrics.semanticLossPercent)} isLast />
        </>
      )
    }
    case "architecture": {
      const metrics = data as ArchitectureMetrics
      return (
        <>
          <MetricRow label="Tiempo de transformación" value={formatDuration(metrics.transformationTimeMs)} />
          <MetricRow label="# Clases" value={formatNumber(metrics.classesCount)} />
          <MetricRow label="# Atributos" value={formatNumber(metrics.attributesCount)} />
          <MetricRow label="# Métodos" value={formatNumber(metrics.methodsCount)} />
          <MetricRow label="% Features → Clases" value={formatPercentage(metrics.featuresToClassesPercent)} />
          <MetricRow label="% Tareas → Métodos" value={formatPercentage(metrics.tasksToMethodsPercent)} />
          <MetricRow
            label="% Recursos → Atributos"
            value={formatPercentage(metrics.resourcesToAttributesPercent)}
          />
          <MetricRow label="Pérdida semántica" value={formatPercentage(metrics.semanticLossPercent)} isLast />
        </>
      )
    }
    default:
      return null
  }
}

const MetricRow = ({ label, value, isLast = false }: MetricRowProps) => {
  const rowStateClass = isLast ? "pt-2" : "border-bottom py-2"
  return (
    <div className={`d-flex justify-content-between ${rowStateClass}`}>
      <dt className="mb-0 text-secondary-emphasis">{label}</dt>
      <dd className="mb-0 fw-semibold text-dark">{value}</dd>
    </div>
  )
}

export const MetricsPanel = ({ metrics }: MetricsPanelProps) => (
  <section className="bg-secondary-subtle border border-secondary rounded-4 p-4 mt-4">
    <h2 className="h5 text-center text-secondary-emphasis mb-4">Métricas</h2>
    <div className="row gy-4">
      {StageDefinitions.map(({ key, label }) => (
        <div className="col-12 col-md-4" key={key}>
          <div className="h-100 bg-white rounded-4 shadow-sm p-3 text-dark">
            <h3 className="h6 text-center text-secondary">{label}</h3>
            <dl className="mb-0 small">{renderRows(key, metrics[key])}</dl>
          </div>
        </div>
      ))}
    </div>
  </section>
)
