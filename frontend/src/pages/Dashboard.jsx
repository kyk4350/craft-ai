function Dashboard() {
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">ContentCraft AI</h1>
        <p className="mt-2 text-gray-600">AI-powered Marketing Content Generator</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium">Total Contents</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">0</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium">Avg CTR</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">-</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium">Projects</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">0</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium">This Week</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">0</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Get Started</h2>
        <p className="text-gray-600 mb-4">
          Start creating AI-powered marketing content in minutes.
        </p>
        <button className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition">
          + New Project
        </button>
      </div>
    </div>
  )
}

export default Dashboard
