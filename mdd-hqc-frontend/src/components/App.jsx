/**
 * Main application shell that switches between the editor and home views.
 */

import { useState } from "react"
import { EditorPage } from "./pages/EditorPage"
import { HomePage } from "./pages/HomePage"

/**
 * Renders the top-level application view and keeps navigation intentionally simple.
 */
export const App = () => {
  const [currentView, setCurrentView] = useState("editor")

  return currentView === "home" ? (
    <HomePage onOpenEditor={() => setCurrentView("editor")} />
  ) : (
    <EditorPage onGoHome={() => setCurrentView("home")} />
  )
}
