# KitchenPlus — Sistema E: Pedidos y cocina de restaurante

Prueba técnica individual del curso de Técnicas de Empleabilidad.
Sistema de gestión de pedidos y cocina para un restaurante: crear
pedidos, seguir la cola de cocina en tiempo (casi) real, y cobrar la
cuenta de una mesa con pagos parciales.

Ver `AGENTS.md` para el contexto completo del proyecto, `ASSUMPTIONS.md`
para los supuestos asumidos, `docs/ADR/` para las decisiones de diseño,
y `BITACORA-IA.md` para el registro de sesiones de trabajo con IA.

## Stack técnico

- **Backend:** Django + Django REST Framework (`backend/`)
- **Frontend:** React + Vite (`frontend/`)
- **Base de datos:** SQLite (desarrollo)

## Estructura del repositorio

```bash
KitchenPlus/
├── backend/          # Proyecto Django (API REST)
│   └── cocina/       # App principal: modelos, vistas, tests
├── frontend/         # Aplicación React (Vite)
├── docs/
│   └── ADR/          # Decisiones de arquitectura documentadas
├── AGENTS.md          # Contexto del proyecto para agentes de IA
├── ASSUMPTIONS.md      # Supuestos asumidos sobre el enunciado
└── BITACORA-IA.md      # Registro de sesiones de trabajo con IA
```

## Cómo correr el proyecto desde cero

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

La API queda disponible en `http://127.0.0.1:8000/api/`.

Para tener datos de prueba (mesas y platos), puedes crearlos desde el
shell de Django:

```bash
python manage.py shell -c "
from cocina.models import Mesa, Plato
Mesa.objects.create(numero=1, capacidad=4)
Plato.objects.create(nombre='Lomo Saltado', precio=24.50)
"
```

### Frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

La app queda disponible en `http://localhost:5173/` (o
`http://127.0.0.1:5173/`, según cómo la abra Vite en tu entorno —
ambos orígenes están permitidos por CORS en el backend).

## Pantallas del frontend

- **`/` — Crear Pedido:** elige una mesa, agrega platos con cantidad
  (solo platos con stock disponible) y crea el pedido.
- **`/cocina` — Cola de Cocina:** lista los ítems pendientes o en
  preparación, ordenados por antigüedad, con auto-refresh cada 5
  segundos. Permite avanzar el estado de cada ítem.
- **`/pagar` — Pagar Mesa:** muestra los pedidos no pagados de una
  mesa y su total pendiente. Permite pagar un pedido individual o el
  total de la mesa de una vez.

## Endpoints de la API

| Método | Endpoint | Descripción |
| --- | --- | --- |
| GET | `/api/mesas/` | Lista todas las mesas |
| GET | `/api/mesas/<id>/cuenta/` | Pedidos no pagados y total pendiente de una mesa |
| GET | `/api/platos/` | Lista todos los platos con su disponibilidad |
| POST | `/api/pedidos/` | Crea un pedido con sus ítems |
| GET | `/api/pedidos/<id>/` | Detalle de un pedido |
| GET | `/api/cocina/cola/` | Ítems pendientes/en preparación, ordenados por antigüedad |
| PATCH | `/api/items/<id>/estado/` | Cambia el estado de un ítem |
| POST | `/api/pagos/` | Registra un pago (de un pedido o del total de una mesa) |

## Reglas de negocio implementadas

1. Cada ítem de pedido avanza por sus propios estados; un ítem solo
   se puede cancelar si aún no se ha empezado a preparar.
2. Un plato sin ingredientes suficientes deja de estar disponible
   automáticamente.
3. La cuenta de una mesa admite pagos parciales: por pedido individual
   o por el total acumulado.
4. La cola de cocina tiene un límite máximo de 100 ítems simultáneos
   (ver `ASSUMPTIONS.md`).

## Tests

```bash
cd backend
python manage.py test cocina
```

Cubren: creación de pedidos, la regla de cancelación, el límite de la
cola de cocina, el orden de la cola, y los tres escenarios de pago
(individual, total insuficiente, total completo).
