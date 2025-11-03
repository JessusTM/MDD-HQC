import type { PimLevelProps } from '../../types/components/levels'

export const PimLevel = ({ content, isTransforming, errorMessage }: PimLevelProps) => {
  const hasContent = content.trim().length > 0

  return (
    <section className="bg-body-secondary text-dark rounded-4 p-4 h-100 d-flex flex-column">
      <h2 className="h5 text-center mb-3">UVL</h2>
      <p className="mb-3">
        Aquí se mostrará la vista del modelo de variabilidad del modelo i*.
      </p>

      {errorMessage && (
        <div className="alert alert-danger" role="alert">
          {errorMessage}
        </div>
      )}

      {isTransforming && (
        <p className="text-info mb-0">Generando modelo UVL…</p>
      )}

      {!isTransforming && hasContent && (
        <pre className="bg-dark text-white rounded-3 p-3 flex-grow-1">{content}</pre>
      )}
    </section>
  )
}
