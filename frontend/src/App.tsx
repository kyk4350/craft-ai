import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GeneratePage from './pages/GeneratePage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<GeneratePage />} />
        {/* 추가 라우트는 5주차에 구현 (Dashboard, Projects, History 등) */}
      </Routes>
    </Router>
  );
}

export default App;
