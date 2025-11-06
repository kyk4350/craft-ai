import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import GeneratePageNew from './pages/GeneratePageNew';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuthStore } from './stores/authStore';

function Navigation() {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav className="bg-blue-600 shadow-md">
      <div className="max-w-full px-6">
        <div className="flex justify-between items-center h-14">
          <div className="flex items-center space-x-2">
            <span className="text-white text-xl font-bold">ContentCraft AI</span>
            <span className="text-blue-200 text-sm">마케팅 콘텐츠 자동 생성</span>
          </div>

          <div className="flex items-center space-x-6">
            <Link
              to="/"
              className="text-white hover:text-blue-100 text-sm font-medium transition-colors"
            >
              콘텐츠 생성
            </Link>
            <Link
              to="/history"
              className="text-white hover:text-blue-100 text-sm font-medium transition-colors"
            >
              히스토리
            </Link>
            <Link
              to="/dashboard"
              className="text-white hover:text-blue-100 text-sm font-medium transition-colors"
            >
              성과 대시보드
            </Link>

            <div className="flex items-center space-x-3 ml-4 pl-4 border-l border-blue-400">
              <span className="text-blue-100 text-sm">
                {user?.name || user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="text-white hover:text-blue-100 text-sm font-medium transition-colors"
              >
                로그아웃
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="h-screen flex flex-col">
        <Navigation />

        <div className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <GeneratePageNew />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <History />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
