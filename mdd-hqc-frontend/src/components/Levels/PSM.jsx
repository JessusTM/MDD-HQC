import { MddCard } from "../Commons/MddCard"

export const PSM = ({ plantUml }) => {
  return (
    <MddCard title="PlantUML (PSM)">
      <p>Acá encontrarás una vistta de la arquitectura del modelo generado en UML.</p>
      <pre className="bg-dark text-light p-3 rounded-3 overflow-auto">
        {plantUml}
      </pre>
    </MddCard>
  )
}
