import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          {/* 추가 라우트는 나중에 구현 */}
        </Routes>
      </div>
    </Router>
  )
}

export default App
