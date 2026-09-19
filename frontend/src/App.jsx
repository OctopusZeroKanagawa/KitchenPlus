import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import './App.css'

function CrearPedido() {
  return <h1>CrearPedido</h1>
}

function ColaCocina() {
  return <h1>ColaCocina</h1>
}

function App() {
  return (
    <BrowserRouter>
      <nav className="top-nav">
        <NavLink to="/" end>
          CrearPedido
        </NavLink>
        <NavLink to="/cocina">ColaCocina</NavLink>
      </nav>

      <main className="page-shell">
        <Routes>
          <Route path="/" element={<CrearPedido />} />
          <Route path="/cocina" element={<ColaCocina />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App
