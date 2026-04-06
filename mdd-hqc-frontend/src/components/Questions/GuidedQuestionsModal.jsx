/**
 * Guided questions modal used by the AI-assisted CIM-to-PIM interaction flow.
 */

/**
 * Displays the prepared questions that guide the user before the CIM-to-PIM step.
 *
 * This component is used by the main application when guided interaction is available so
 * the user can review the generated questions in a dedicated modal view.
 */
const GuidedQuestionsModal = ({ isOpen, onClose, questions, onContinue }) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-xl relative">
        {/* Close action */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-2 right-2 text-white hover:text-blue-400 mr-3 mt-3"
        >
          X
        </button>

        {/* Modal header */}
        <div className="flex items-center mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="w-6 h-6 text-purple-400 mr-2"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M7 17h3l2-4V7H7v6h2l-2 4zm7 0h3l2-4V7h-5v6h2l-2 4z" />
          </svg>

          <h2 className="text-xl font-bold text-white">Guided Interaction: CIM to PIM</h2>
        </div>

        {/* Question list */}
        <div className="bg-gray-900 p-4 mb-4 -mx-6 max-h-[420px] overflow-y-auto">
          <p className="text-gray-300">
            Answer the following questions to refine the semi-automatic transformation from <span className="font-bold text-blue-200">CIM to PIM</span>
          </p>

          {questions.map((q, index) => (
            <div key={q.id || index} className="mt-6 bg-gray-700 p-4 rounded-lg">
              <h3 className="text-white font-semibold mb-2">{q.text}</h3>
              <div className="flex flex-wrap gap-2 mt-3">
                {q.options?.map((opt, optionIndex) => (
                  <button
                    type="button"
                    key={optionIndex}
                    className="bg-gray-900 text-white px-3 py-2 rounded hover:bg-blue-600"
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer action */}
        <div className="flex justify-end">
          <button
            type="button"
            onClick={onContinue}
            className="bg-gray-700 text-white px-4 py-2 rounded"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  )
}

export default GuidedQuestionsModal
