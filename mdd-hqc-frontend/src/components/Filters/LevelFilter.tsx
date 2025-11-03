import type { ChangeEvent } from 'react'
import { levelOptions } from '../../types/levels'
import type { LevelKey } from '../../types/levels'
import type { LevelFilterProps } from '../../types/components/filters'

const allowedTransitions: Record<LevelKey, LevelKey[]> = {
  cim: ['pim'],
  pim: ['psm'],
  psm: [],
}

export const LevelFilter = ({
  from,
  to,
  onFromChange,
  onToChange,
  onTransform,
  isTransforming = false,
  isTransformDisabled = false,
}: LevelFilterProps) => {
  const fromOptions = levelOptions.filter((option) => allowedTransitions[option.key].length > 0)
  const toOptions = levelOptions.filter((option) => allowedTransitions[from].includes(option.key))

  const handleFromChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const nextFrom = event.target.value as LevelKey
    onFromChange(nextFrom)

    const nextToOptions = allowedTransitions[nextFrom] ?? []
    if (nextToOptions.length > 0 && !nextToOptions.includes(to)) {
      onToChange(nextToOptions[0])
    }
  }

  const handleToChange = (event: ChangeEvent<HTMLSelectElement>) => {
    onToChange(event.target.value as LevelKey)
  }

  const isTransformEnabled = allowedTransitions[from].includes(to)

  return (
    <div className="bg-primary-subtle border border-primary rounded-4 p-4 mt-4">
      <div className="row g-3 align-items-end">
        <div className="col-md-5">
          <label className="form-label text-uppercase text-primary-emphasis fw-semibold">
            Nivel origen
          </label>
          <select
            className="form-select"
            value={from}
            onChange={handleFromChange}
          >
            {fromOptions.map((option) => (
              <option key={option.key} value={option.key}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-5">
          <label className="form-label text-uppercase text-primary-emphasis fw-semibold">
            Nivel destino
          </label>
          <select
            className="form-select"
            value={to}
            onChange={handleToChange}
          >
            {toOptions.map((option) => (
              <option key={option.key} value={option.key}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-2 d-grid">
          <button
            className="btn btn-danger fw-semibold"
            type="button"
            onClick={onTransform}
            disabled={!isTransformEnabled || isTransformDisabled}
          >
            {isTransforming ? 'Transformando…' : 'Transformar'}
          </button>
        </div>
      </div>
    </div>
  )
}
