import { useState } from "react"

import type { PsmLevelProps } from "../../types/components/levels"

export const PsmLevel = ({
  diagramUrl,
  plantUmlSource,
  isTransforming,
  errorMessage,
}: PsmLevelProps) => {
  const hasDiagram = Boolean(diagramUrl);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => {
    if (hasDiagram) {
      setIsModalOpen(true);
    }
  };

  const handleCloseModal = () => setIsModalOpen(false);

  return (
    <section className="bg-body-secondary text-dark rounded-4 p-4 h-100 d-flex flex-column">
      <h2 className="h5 text-center mb-3">Arquitectura</h2>
      <p>
        Visualice la arquitectura Quantum-UML derivada del UVL seleccionado. El diagrama utiliza PlantUML para representar clases y estereotipos.
      </p>

      {errorMessage && (
        <div className="alert alert-danger" role="alert">
          {errorMessage}
        </div>
      )}

      {isTransforming && <p className="text-info">Generando diagrama de arquitectura…</p>}

      {!isTransforming && hasDiagram && (
        <div className="bg-dark rounded-3 p-3 flex-grow-1 d-flex flex-column">
          <div className="bg-white rounded-2 p-2 flex-grow-1 d-flex justify-content-center align-items-center">
            <img
              src={diagramUrl}
              alt="Diagrama de arquitectura Quantum-UML"
              className="img-fluid"
            />
          </div>
          <div className="d-flex justify-content-between align-items-center mt-3 gap-2 flex-wrap">
            <button
              type="button"
              className="btn btn-outline-light"
              onClick={handleOpenModal}
            >
              Ampliar diagrama
            </button>
            {plantUmlSource && (
              <details className="text-white-50 flex-grow-1">
                <summary className="text-white">Ver PlantUML</summary>
                <pre className="mt-2 text-white">{plantUmlSource}</pre>
              </details>
            )}
          </div>
        </div>
      )}

      {!isTransforming && !hasDiagram && !errorMessage && (
        <p className="text-muted mb-0">Genere un modelo UVL para habilitar la transformación a arquitectura.</p>
      )}

      {isModalOpen && diagramUrl && (
        <div className="modal d-block" style={{ backgroundColor: "rgba(0, 0, 0, 0.75)" }}>
          <div className="modal-dialog modal-xl modal-dialog-centered">
            <div className="modal-content bg-dark text-white border-secondary">
              <div className="modal-header border-secondary">
                <h5 className="modal-title">Diagrama de arquitectura</h5>
                <button
                  type="button"
                  className="btn-close btn-close-white"
                  aria-label="Cerrar"
                  onClick={handleCloseModal}
                />
              </div>
              <div className="modal-body">
                <div className="bg-white rounded-2 p-2">
                  <img
                    src={diagramUrl}
                    alt="Diagrama de arquitectura Quantum-UML ampliado"
                    className="img-fluid"
                  />
                </div>
              </div>
              <div className="modal-footer border-secondary">
                <button type="button" className="btn btn-outline-light" onClick={handleCloseModal}>
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
