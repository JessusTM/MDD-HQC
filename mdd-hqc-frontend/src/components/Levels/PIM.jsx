import { MddCard } from "../Commons/MddCard"

export const PIM = ({ UVL }) => {
  return (
    <MddCard title="UVL (PIM)">
      <p>Acá encontrarás el modelo UVL generado.</p>
      <pre className="bg-dark text-light p-3 rounded-3 overflow-auto">
        {UVL}
      </pre>
    </MddCard>
  )
}
