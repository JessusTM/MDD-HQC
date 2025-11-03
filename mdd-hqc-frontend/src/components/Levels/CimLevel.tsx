import type { ChangeEvent } from 'react'
import { useState } from 'react'

import { cleanIStarXml } from '../../services/CimService'
import type {
  CimLevelProps,
  CimLevelStatus,
} from '../../types/components/levels'

export const CimLevel = ({ onModelReady, onModelCleared }: CimLevelProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [status, setStatus] = useState<CimLevelStatus>('idle')
  const [message, setMessage] = useState<string>('')

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null

    if (!file) {
      setSelectedFile(null)
      setStatus('idle')
      setMessage('')
      onModelCleared?.()
      return
    }

    setSelectedFile(file)
    setStatus('processing')
    setMessage('Validando modelo…')

    try {
      const xmlContent = await file.text()
      await cleanIStarXml(xmlContent)
      setStatus('success')
      setMessage('Modelo validado correctamente.')
      onModelReady(xmlContent)
    } catch (error) {
      console.error('No se pudo limpiar el XML recibido', error)
      setStatus('error')
      setMessage('Seleccione un archivo XML válido e intente nuevamente…')
      onModelCleared?.()
    }
  }

  const renderStatusMessage = () => {
    if (!message) {
      return selectedFile ? (
        <span className="text-secondary">Archivo seleccionado: {selectedFile.name}</span>
      ) : undefined
    }

    if (status === 'success') {
      return <span className="text-success">{message}</span>
    }

    if (status === 'error') {
      return <span className="text-danger">{message}</span>
    }

    if (status === 'processing') {
      return <span className="text-info">{message}</span>
    }

    return <span className="text-secondary">{message}</span>
  }

  return (
    <section className="bg-body-secondary text-dark rounded-4 p-4 h-100 d-flex flex-column">
      <h2 className="h5 text-center mb-3">i* 2.0</h2>
      <p className="flex-grow-1">
        Aquí debe subir su modelo i* para su sistema híbrido.
      </p>
      <div className="mb-3">
        <input
          className="form-control"
          type="file"
          accept=".xml"
          onChange={handleFileChange}
        />
      </div>
      <div className="mt-3 small">{renderStatusMessage()}</div>
    </section>
  )
}
