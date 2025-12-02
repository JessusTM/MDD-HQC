import { useRef, useState } from "react"
import { Upload, FileText, CheckCircle } from "lucide-react"

export const CIM = ({ onModelReady, onModelCleared }) => {
  const [file, setFile] = useState(null)
  const [errorMessage, setErrorMessage] = useState("")
  const [infoMessage, setInfoMessage] = useState("")
  const fileInputRef = useRef(null)

  const reset = () => {
    setFile(null)
    setErrorMessage("")
    setInfoMessage("")
    onModelCleared?.()
  }

  const handleFile = async (event) => {
    const selected = event.target.files?.[0]

    if (!selected) {
      reset()
      return
    }

    setFile(selected)
    setInfoMessage("Validando archivo…")
    setErrorMessage("")
    await processFile(selected)
  }

  const processFile = async (fileToRead) => {
    try {
      const xmlContent = await fileToRead.text()
      setInfoMessage("Modelo válido.")
      onModelReady?.(xmlContent)
    } catch (error) {
      console.error("XML inválido", error)
      setErrorMessage("El archivo no es un XML válido.")
      setInfoMessage("")
      onModelCleared?.()
    }
  }

  return (
    <div className="flex flex-col h-full bg-ctp-surface0 rounded-xl shadow-xl border-2 border-ctp-surface2 transition-all duration-300 hover:border-ctp-surface1">
      <div className="p-5 border-b border-ctp-surface1 bg-ctp-surface0/20 rounded-t-xl flex items-center justify-between shrink-0 h-20">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-ctp-surface1 rounded-lg">
            <FileText className="w-8 h-8 text-ctp-blue" />
          </div>
          <div>
            <h3 className="font-bold text-ctp-text text-2xl">CIM</h3>
            <p className="text-lg text-ctp-subtext0 font-semibold hidden xl:block">
              i* 2.0 (iStar)
            </p>
          </div>
        </div>

        {file && !errorMessage && (
          <span className="px-3 py-1 bg-ctp-green/20 text-ctp-green border border-ctp-green/30 text-sm font-semibold rounded-full flex items-center gap-1.5 shadow-sm">
            <CheckCircle className="w-4 h-4" /> Listo
          </span>
        )}
      </div>

      <div className="flex-1 p-0 overflow-hidden flex flex-col relative bg-ctp-crust">
        <div className="flex-1 flex flex-col items-center justify-center m-6 py-10 rounded-lg bg-ctp-mantle/50">
          <p className="text-ctp-subtext0 text-xl mb-6 text-center px-6 font-semibold">
            Sube tu archivo i* 2.0 (XML) aquí…
          </p>

          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept=".xml,.istar,.txt"
            onChange={handleFile}
          />

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-3 px-6 py-3 bg-ctp-mauve hover:bg-ctp-pink text-ctp-base rounded-lg font-bold transition-all hover:scale-105 active:scale-95 shadow-lg shadow-ctp-mauve/20 text-base"
          >
            <Upload className="w-5 h-5" />
            Subir Archivo
          </button>

          <div className="mt-4 text-sm">
            {file && !errorMessage && !infoMessage && (
              <span className="text-ctp-subtext0">{file.name}</span>
            )}

            {infoMessage && (
              <span className="text-ctp-green">{infoMessage}</span>
            )}

            {errorMessage && (
              <span className="text-ctp-red">{errorMessage}</span>
            )}
          </div>
        </div>
      </div>

      <div className="shrink-0 bg-ctp-mantle border-t border-ctp-surface0/50 p-4">
        <div className="h-[104px] rounded-lg bg-ctp-mantle/40 flex items-center justify-center">
          <span className="text-ctp-subtext0 text-xl font-semibold italic">
            Sin métricas disponibles
          </span>
        </div>
      </div>
    </div>
  )
}
