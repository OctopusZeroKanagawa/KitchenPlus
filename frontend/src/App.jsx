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

function PagarMesa() {
  const [mesas, setMesas] = useState([])
  const [selectedMesaId, setSelectedMesaId] = useState('')
  const [cuenta, setCuenta] = useState(null)
  const [loadingMesas, setLoadingMesas] = useState(true)
  const [loadingCuenta, setLoadingCuenta] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  useEffect(() => {
    const fetchMesas = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/mesas/')
        if (!response.ok) {
          throw new Error('No se pudieron cargar las mesas.')
        }

        const data = await response.json()
        setMesas(Array.isArray(data) ? data : [])
        if (data.length > 0) {
          setSelectedMesaId(String(data[0].id))
        }
      } catch (error) {
        setErrorMessage(error.message)
      } finally {
        setLoadingMesas(false)
      }
    }

    fetchMesas()
  }, [])

  useEffect(() => {
    if (!selectedMesaId) {
      setCuenta(null)
      return
    }

    const fetchCuenta = async () => {
      setLoadingCuenta(true)
      setErrorMessage('')
      setSuccessMessage('')

      try {
        const response = await fetch(`http://localhost:8000/api/mesas/${selectedMesaId}/cuenta/`)
        if (!response.ok) {
          throw new Error('No se pudo cargar la cuenta de la mesa.')
        }

        const data = await response.json()
        setCuenta(data)
      } catch (error) {
        setErrorMessage(error.message)
      } finally {
        setLoadingCuenta(false)
      }
    }

    fetchCuenta()
  }, [selectedMesaId])

  const pagarPedido = async (pedido) => {
    if (!selectedMesaId) {
      return
    }

    setProcessing(true)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const response = await fetch('http://localhost:8000/api/pagos/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mesa: Number(selectedMesaId),
          pedido: pedido.id,
          monto: Number(pedido.subtotal),
        }),
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        const message = Array.isArray(data.detail)
          ? data.detail.join(', ')
          : data.detail || 'No se pudo pagar este pedido.'
        throw new Error(message)
      }

      const updated = await fetch(`http://localhost:8000/api/mesas/${selectedMesaId}/cuenta/`)
      if (!updated.ok) {
        throw new Error('No se pudo recargar la cuenta de la mesa.')
      }

      const cuentaData = await updated.json()
      setCuenta(cuentaData)
      setSuccessMessage(`Pedido ${pedido.id} pagado correctamente.`)
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setProcessing(false)
    }
  }

  const pagarTotalMesa = async () => {
    if (!selectedMesaId || !cuenta || Number(cuenta.total_pendiente) <= 0) {
      return
    }

    setProcessing(true)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const response = await fetch('http://localhost:8000/api/pagos/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mesa: Number(selectedMesaId),
          monto: Number(cuenta.total_pendiente),
        }),
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        const message = Array.isArray(data.detail)
          ? data.detail.join(', ')
          : data.detail || 'No se pudo pagar el total de la mesa.'
        throw new Error(message)
      }

      const updated = await fetch(`http://localhost:8000/api/mesas/${selectedMesaId}/cuenta/`)
      if (!updated.ok) {
        throw new Error('No se pudo recargar la cuenta de la mesa.')
      }

      const cuentaData = await updated.json()
      setCuenta(cuentaData)
      setSuccessMessage('Pago total de la mesa realizado correctamente.')
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setProcessing(false)
    }
  }

  const pedidosPendientes = cuenta?.pedidos || []

  return (
    <div className="cocina-container">
      <h1>Pagar mesa</h1>

      {loadingMesas ? (
        <p>Cargando mesas...</p>
      ) : (
        <label className="field-group">
          <span>Mesa</span>
          <select value={selectedMesaId} onChange={(event) => setSelectedMesaId(event.target.value)}>
            {mesas.map((mesa) => (
              <option key={mesa.id} value={mesa.id}>
                Mesa {mesa.numero}
              </option>
            ))}
          </select>
        </label>
      )}

      {errorMessage && <div className="message error">{errorMessage}</div>}
      {successMessage && <div className="message success">{successMessage}</div>}

      {loadingCuenta ? (
        <p>Cargando cuenta...</p>
      ) : !cuenta ? (
        <p>No hay mesa seleccionada.</p>
      ) : pedidosPendientes.length === 0 ? (
        <p>Esta mesa no tiene cuenta pendiente.</p>
      ) : (
        <div className="cuenta-container">
          <h2>Cuenta pendiente</h2>

          <ul className="cola-list">
            {pedidosPendientes.map((pedido) => (
              <li key={pedido.id} className="cola-item">
                <div className="cola-item-header">
                  <strong>Pedido #{pedido.id}</strong>
                  <span className="cantidad-badge">€{Number(pedido.subtotal).toFixed(2)}</span>
                </div>

                <div className="cola-item-meta">
                  <span>Subtotal: €{Number(pedido.subtotal).toFixed(2)}</span>
                </div>

                <button
                  type="button"
                  className="advance-button"
                  onClick={() => pagarPedido(pedido)}
                  disabled={processing}
                >
                  Pagar este pedido
                </button>
              </li>
            ))}
          </ul>

          <div className="cuenta-resumen">
            <strong>Total pendiente: €{Number(cuenta.total_pendiente).toFixed(2)}</strong>
            {/* El monto se calcula automáticamente desde cuenta.total_pendiente; el error de 'monto insuficiente' del backend solo puede ocurrir si se llama a la API directamente con un monto distinto, no desde este botón. */}
            <button
              type="button"
              className="advance-button"
              onClick={pagarTotalMesa}
              disabled={processing}
            >
              Pagar total de la mesa
            </button>
          </div>
        </div>
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
        <NavLink to="/pagar">PagarMesa</NavLink>
      </nav>

      <main className="page-shell">
        <Routes>
          <Route path="/" element={<CrearPedido />} />
          <Route path="/cocina" element={<ColaCocina />} />
          <Route path="/pagar" element={<PagarMesa />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App
