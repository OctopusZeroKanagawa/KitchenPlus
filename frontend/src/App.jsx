import { useEffect, useState } from 'react'
import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import './App.css'

function CrearPedido() {
  const [mesas, setMesas] = useState([])
  const [platos, setPlatos] = useState([])
  const [mesaId, setMesaId] = useState('')
  const [quantities, setQuantities] = useState({})
  const [loadingData, setLoadingData] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    const loadOptions = async () => {
      try {
        const [mesasRes, platosRes] = await Promise.all([
          fetch('http://localhost:8000/api/mesas/'),
          fetch('http://localhost:8000/api/platos/'),
        ])

        if (!mesasRes.ok || !platosRes.ok) {
          throw new Error('No se pudieron cargar las mesas o los platos.')
        }

        const mesasData = await mesasRes.json()
        const platosData = await platosRes.json()

        setMesas(mesasData)
        setPlatos(platosData)
        if (mesasData.length > 0) {
          setMesaId(String(mesasData[0].id))
        }
      } catch (error) {
        setErrorMessage(error.message)
      } finally {
        setLoadingData(false)
      }
    }

    loadOptions()
  }, [])

  const handleCantidadChange = (platoId, rawValue) => {
    const nextValue = Number(rawValue)
    const safeValue = Number.isFinite(nextValue) && nextValue >= 0 ? nextValue : 0
    setQuantities((prev) => ({ ...prev, [platoId]: safeValue }))
  }

  const itemsToCreate = platos
    .filter((plato) => Number(quantities[plato.id] || 0) > 0)
    .map((plato) => ({
      plato_id: plato.id,
      cantidad: Number(quantities[plato.id]),
    }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSuccessMessage('')
    setErrorMessage('')

    if (!mesaId) {
      setErrorMessage('Debes seleccionar una mesa.')
      return
    }

    if (itemsToCreate.length === 0) {
      setErrorMessage('Debes elegir al menos un plato con cantidad mayor que 0.')
      return
    }

    try {
      setSubmitting(true)
      const response = await fetch('http://localhost:8000/api/pedidos/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mesa: Number(mesaId),
          items_to_create: itemsToCreate,
        }),
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        const message = Array.isArray(data.detail)
          ? data.detail.join(', ')
          : data.detail || 'No se pudo crear el pedido.'
        throw new Error(message)
      }

      setSuccessMessage(`Pedido creado correctamente con ID ${data.id}.`)
      setQuantities({})
      if (mesas.length > 0) {
        setMesaId(String(mesas[0].id))
      }
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="pedido-form-container">
      <h1>Crear pedido</h1>

      {loadingData ? (
        <p>Cargando mesas y platos...</p>
      ) : (
        <form onSubmit={handleSubmit} className="pedido-form">
          <label className="field-group">
            <span>Mesa</span>
            <select value={mesaId} onChange={(event) => setMesaId(event.target.value)}>
              {mesas.map((mesa) => (
                <option key={mesa.id} value={mesa.id}>
                  Mesa {mesa.numero} ({mesa.capacidad} pax)
                </option>
              ))}
            </select>
          </label>

          <div className="field-group">
            <span>Platos</span>
            <div className="platos-list">
              {platos.map((plato) => {
                const selectedQty = Number(quantities[plato.id] || 0)
                const unavailable = !plato.disponible

                return (
                  <label
                    key={plato.id}
                    className={`plato-row ${unavailable ? 'plato-row-disabled' : ''}`}
                  >
                    <div className="plato-row-main">
                      <input
                        type="checkbox"
                        checked={selectedQty > 0}
                        disabled={unavailable}
                        onChange={(event) => {
                          if (event.target.checked) {
                            handleCantidadChange(plato.id, 1)
                          } else {
                            handleCantidadChange(plato.id, 0)
                          }
                        }}
                      />

                      <div>
                        <strong>{plato.nombre}</strong>
                        <small>€{Number(plato.precio).toFixed(2)}</small>
                      </div>
                    </div>

                    <div className="plato-qty-wrapper">
                      <input
                        type="number"
                        min="0"
                        step="1"
                        value={selectedQty}
                        disabled={unavailable}
                        onChange={(event) => handleCantidadChange(plato.id, event.target.value)}
                        aria-label={`Cantidad de ${plato.nombre}`}
                      />
                      {!plato.disponible && <span className="unavailable-tag">No disponible</span>}
                    </div>
                  </label>
                )
              })}
            </div>
          </div>

          {errorMessage && <div className="message error">{errorMessage}</div>}
          {successMessage && <div className="message success">{successMessage}</div>}

          <button type="submit" disabled={submitting}>
            {submitting ? 'Creando pedido...' : 'Crear pedido'}
          </button>
        </form>
      )}
    </div>
  )
}

const estadoLabels = {
  pendiente: 'Pendiente',
  en_preparacion: 'En preparación',
  listo: 'Listo',
  entregado: 'Entregado',
  cancelado: 'Cancelado',
}

const estadoOrden = ['pendiente', 'en_preparacion', 'listo']

const getSiguienteEstado = (estadoActual) => {
  const indexActual = estadoOrden.indexOf(estadoActual)
  if (indexActual === -1 || indexActual === estadoOrden.length - 1) {
    return null
  }
  return estadoOrden[indexActual + 1]
}

const formatearTiempo = (isoDate) => {
  const diffMs = Date.now() - new Date(isoDate).getTime()
  const segundos = Math.max(0, Math.floor(diffMs / 1000))

  if (segundos < 60) {
    return `hace ${segundos} s`
  }

  const minutos = Math.floor(segundos / 60)
  if (minutos < 60) {
    return `hace ${minutos} min`
  }

  const horas = Math.floor(minutos / 60)
  return `hace ${horas} h`
}

function ColaCocina() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [updatingId, setUpdatingId] = useState(null)

  const refreshQueue = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/cocina/cola/')
      if (!response.ok) {
        throw new Error('No se pudo cargar la cola de cocina.')
      }

      const data = await response.json()
      setItems(Array.isArray(data) ? data : [])
      setErrorMessage('')
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refreshQueue()

    const intervalId = setInterval(() => {
      refreshQueue()
    }, 5000)

    return () => {
      clearInterval(intervalId)
    }
  }, [])

  const handleAdvance = async (item) => {
    const siguienteEstado = getSiguienteEstado(item.estado)
    if (!siguienteEstado) {
      return
    }

    setUpdatingId(item.id)
    setErrorMessage('')

    try {
      const response = await fetch(`http://localhost:8000/api/items/${item.id}/estado/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ estado: siguienteEstado }),
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.join(', ')
          : data.detail || 'No se pudo actualizar el estado.'
        throw new Error(detail)
      }

      await refreshQueue()
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setUpdatingId(null)
    }
  }

  return (
    <div className="cocina-container">
      <h1>Cola de cocina</h1>

      {errorMessage && <div className="message error">{errorMessage}</div>}

      {loading ? (
        <p>Cargando cola...</p>
      ) : items.length === 0 ? (
        <p>No hay ítems pendientes.</p>
      ) : (
        <ul className="cola-list">
          {items.map((item) => {
            const siguienteEstado = getSiguienteEstado(item.estado)

            return (
              <li key={item.id} className="cola-item">
                <div className="cola-item-header">
                  <strong>{item.plato_nombre}</strong>
                  <span className="cantidad-badge">{item.cantidad}x</span>
                </div>

                <div className="cola-item-meta">
                  <span>Mesa {item.mesa_numero}</span>
                  <span>{estadoLabels[item.estado] || item.estado}</span>
                  <span>{formatearTiempo(item.creado)}</span>
                </div>

                {siguienteEstado && (
                  <button
                    type="button"
                    className="advance-button"
                    onClick={() => handleAdvance(item)}
                    disabled={updatingId === item.id}
                  >
                    {updatingId === item.id
                      ? 'Actualizando...'
                      : `Avanzar a ${estadoLabels[siguienteEstado]}`}
                  </button>
                )}
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
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
