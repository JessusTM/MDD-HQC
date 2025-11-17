export const MddCard = ({ title, children }) => {
  return (
    <section className="bg-body-secondary text-dark rounded-4 p-4 h-100 d-flex flex-column">
      <h2 className="h5 text-center mb-3">{title}</h2>

      <div className="flex-grow-1">
        {children}
      </div>
    </section>
  )
}
