export const MddCard = ({ title, children }) => {
  return (
    <section className="mdd-card">
      <header className="mdd-card-header">
        <div className="mdd-card-badge" aria-hidden="true" />
        <div>
          <h2 className="mdd-card-title">{title}</h2>
          <p className="mdd-card-subtitle">
          </p>
        </div>
      </header>

      <div className="mdd-card-body">
        {children}
      </div>
    </section>
  )
}