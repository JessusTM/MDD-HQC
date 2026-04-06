/**
 * Small shared card container used to display titled content blocks.
 */

/**
 * Wraps content inside a simple titled card layout.
 *
 * This component exists so shared card styling can stay reusable across the frontend
 * without duplicating the same section structure in each consumer.
 */
export const MddCard = ({ title, children }) => {
  return (
    <section className="mdd-card">
      {/* Card header */}
      <header className="mdd-card-header">
        <div className="mdd-card-badge" aria-hidden="true" />
        <div>
          <h2 className="mdd-card-title">{title}</h2>
          <p className="mdd-card-subtitle">
          </p>
        </div>
      </header>

      {/* Card body */}
      <div className="mdd-card-body">
        {children}
      </div>
    </section>
  )
}
