import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";
import { Orchestrator } from "./components/Orchestrator/Orchestrator";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Orchestrator />
  </StrictMode>,
);
