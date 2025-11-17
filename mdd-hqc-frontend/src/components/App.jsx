import { CIM } from "./Levels/CIM"
import { PIM } from "./Levels/PIM"
import { PSM } from "./Levels/PSM"
import { Filter } from "./Filter/Filter"

export const App = () => {
  return (
    <div className="container py-5">

      <div className="p-4 rounded-4" style={{ background: "#111" }}>
        <section className="row g-4">
          <div className="col-md-4">
            <CIM />
          </div>

          <div className="col-md-4">
            <PIM />
          </div>

          <div className="col-md-4">
            <PSM />
          </div>
        </section>

        <div
          style={{
            height: "120px",
            background: "rgba(255,255,255,0.08)",
            borderRadius: "12px",
            marginTop: "40px",
          }}
        ></div>

        <div className="mt-4">
          <Filter />
        </div>
      </div>
    </div>
  )
}
