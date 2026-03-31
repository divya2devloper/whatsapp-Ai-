import React from 'react'
import { createRoot } from 'react-dom/client'

function App() {
  return (
    <main style={{ fontFamily: 'Inter, system-ui, sans-serif', padding: 24 }}>
      <h1>Brain 2.0 Orchestrator</h1>
      <p>Industrial-grade, ROI-focused AI CRM orchestration for Indian SMEs.</p>
    </main>
  )
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
