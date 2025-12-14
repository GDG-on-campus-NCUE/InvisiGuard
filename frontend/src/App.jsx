import { useState, useEffect } from 'react'
import api from './services/api'

function App() {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    api.get('/health')
      .then(res => setHealth(res.data))
      .catch(err => console.error(err))
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold underline mb-4">
        InvisiGuard
      </h1>
      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-xl font-semibold mb-2">System Status</h2>
        {health ? (
          <div className="text-green-600">
            <p>Status: {health.status}</p>
            <p>Service: {health.service}</p>
          </div>
        ) : (
          <p className="text-gray-500">Connecting to backend...</p>
        )}
      </div>
    </div>
  )
}

export default App
