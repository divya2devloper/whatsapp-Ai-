import React from 'react'
import { createRoot } from 'react-dom/client'

function App() {
  const [trial, setTrial] = React.useState(null)
  const [lockoutSeconds, setLockoutSeconds] = React.useState(0)

  React.useEffect(() => {
    const firstLoginAt = new Date(Date.now() - 73 * 60 * 60 * 1000).toISOString()
    const query = `first_login_at=${encodeURIComponent(firstLoginAt)}`
    const endpoints = [
      `/api/gym-owner/demo-owner/trial-status?${query}`,
      `http://127.0.0.1:8000/api/gym-owner/demo-owner/trial-status?${query}`
    ]
    ;(async () => {
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(endpoint)
          if (!response.ok) continue
          const data = await response.json()
          setTrial(data)
          if (data.is_expired) {
            setLockoutSeconds((data.lockout_countdown_minutes || 20) * 60)
          }
          return
        } catch (error) {
          // try next endpoint
        }
      }
      setTrial({ is_expired: false, lockout_countdown_minutes: 0 })
    })()
  }, [])

  React.useEffect(() => {
    if (!trial?.is_expired || lockoutSeconds <= 0) return
    const timer = setInterval(() => {
      setLockoutSeconds((prev) => (prev > 0 ? prev - 1 : 0))
    }, 1000)
    return () => clearInterval(timer)
  }, [trial?.is_expired, lockoutSeconds])

  const minutes = String(Math.floor(lockoutSeconds / 60)).padStart(2, '0')
  const seconds = String(lockoutSeconds % 60).padStart(2, '0')

  return (
    <main style={{ fontFamily: 'Inter, system-ui, sans-serif', padding: 24 }}>
      <style>{`@keyframes gymBlink { 50% { opacity: 0.25; } }`}</style>
      <h1>Gym-Brain Fitness Orchestrator</h1>
      <p>The only AI tool built to scale Indian Gyms.</p>
      {trial?.is_expired && (
        <div
          style={{
            marginTop: 16,
            background: '#dc2626',
            color: '#fff',
            padding: 12,
            borderRadius: 8,
            fontWeight: 700,
            animation: 'gymBlink 1s linear infinite'
          }}
        >
          Gym Trial Expired · Lockout Timer: {minutes}:{seconds}
        </div>
      )}
      <section style={{ marginTop: 20 }}>
        <h2>Hiring (Trainers)</h2>
        <p>No MASTER_DEMO trainers are shown for new gym owners.</p>
        <h2>WhatsApp (Member Chats)</h2>
        <p>No MASTER_DEMO member chat data is shown for new gym owners.</p>
      </section>
    </main>
  )
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
