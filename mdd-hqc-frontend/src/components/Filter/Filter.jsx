export const Filter = () => {
  return (
    <>
      <div className="bg-primary-subtle border border-primary rounded-4 p-4 mt-4">
        <div className="row g-3 align-items-end">

          <div className="col-md-5">
            <label className="form-label text-uppercase text-primary-emphasis fw-semibold">
              Nivel origen
            </label>
            <select className="form-select">
              <option value="cim">CIM</option>
              <option value="pim">PIM</option>
              <option value="psm">PSM</option>
            </select>
          </div>

          <div className="col-md-5">
            <label className="form-label text-uppercase text-primary-emphasis fw-semibold">
              Nivel destino
            </label>
            <select className="form-select">
              <option value="cim">CIM</option>
              <option value="pim">PIM</option>
              <option value="psm">PSM</option>
            </select>
          </div>

          <div className="col-md-2 d-grid">
            <button className="btn btn-danger fw-semibold" type="button">
              Transformar
            </button>
          </div>

        </div>
      </div>
    </>
  )
}
