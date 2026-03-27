import React from "react";

const QuestionsModal = ({ isOpen, onClose, children }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 w-full max-w-xl relative">
         
                <button
                    onClick={onClose}
                    className="absolute top-2 right-2 text-white hover:text-blue-400 mr-3 mt-3"
                >
                    X
                </button>
                
                {children}
            </div>
        </div>
    );
};

export default QuestionsModal;
