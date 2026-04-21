/**
 * Main application shell that maps top-level pages to real browser routes.
 */

import { Navigate, Route, Routes } from "react-router-dom"
import { EditorPage } from "./editor/EditorPage"
import { HomePage } from "./home/HomePage"

/**
 * Renders the top-level application routes.
 */
export const App = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/editor" element={<EditorPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
