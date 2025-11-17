import { useState } from 'react'
import { MddCard } from "../Commons/MddCard"

export const CIM = ({ onModelReady, onModelCleared }) => {
  const [file, setFile] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [infoMessage, setInfoMessage] = useState('')

  const reset = () => {
    setFile(null)
    setErrorMessage('')
    setInfoMessage('')
    onModelCleared?.()
  }

  const handleFile = async (event) => {
    const selected = event.target.files?.[0]

    if (!selected) {
      reset()
      return
    }

    setFile(selected)
    setInfoMessage('Validando archivo…')
    setErrorMessage('')
    await processFile(selected)
  }

  const processFile = async (file) => {
    try {
      const xmlContent = await file.text()
      setInfoMessage('Modelo válido.')
      onModelReady(xmlContent)
    } catch (error) {
      console.error('XML inválido', error)
      setErrorMessage('El archivo no es un XML válido.')
      setInfoMessage('')
      onModelCleared?.()
    }
  }

  return (
    <MddCard title="i* 2.0">
      <p>Sube tu modelo iStar 2.0 aquí.</p>

      <input
        type="file"
        className="form-control"
        accept=".xml"
        onChange={handleFile}
      />

      <div className="mt-3 small">
        {file && !errorMessage && !infoMessage && (
          <span className="text-secondary">{file.name}</span>
        )}

        {infoMessage && (
          <span className="text-info">{infoMessage}</span>
        )}

        {errorMessage && (
          <span className="text-danger">{errorMessage}</span>
        )}
      </div>
    </MddCard>
  )
}
