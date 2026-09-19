# AGENTS.md — Sistema E: Pedidos y cocina de restaurante

> Este archivo es el contexto que se le da al agente de IA (Copilot / Claude) al inicio
> de cada sesión de trabajo. Se actualiza durante la semana a medida que el proyecto
> avanza y se toman nuevas decisiones.

## Qué es este proyecto

Prueba técnica individual del curso de Técnicas de Empleabilidad. Sistema de gestión
de pedidos y cocina para un restaurante. Objetivo: un flujo completo de punta a punta
funcionando, con el proceso de trabajo documentado (ADRs, bitácora IA, assumptions),
no necesariamente el sistema completo.

## Stack técnico

- **Backend:** Django REST Framework
- **Frontend:** React (aplicación separada, consume la API)
- **Estructura del repo:** monorepo
  - `backend/` — proyecto Django
  - `frontend/` — aplicación React

## Entidades mínimas

- **Mesa**
- **Pedido**
- **Ítem de pedido**
- **Plato**
- **Estado de preparación**

## Reglas de negocio (no negociables)

1. Cada ítem del pedido avanza por sus propios estados de preparación de forma
   independiente. El pedido completo solo se considera terminado cuando **todos**
   sus ítems están en estado final.
2. Un plato sin ingredientes disponibles no puede pedirse y debe dejar de
   ofrecerse automáticamente mientras dure esa condición.
3. Un ítem de pedido solo puede cancelarse si la cocina **todavía no lo ha
   empezado a preparar**.
4. La cuenta de una mesa admite **pagos parciales** (varios pagos hasta cubrir
   el total).

## Consulta obligatoria

Cola de cocina: ítems pendientes de preparación, ordenados por antigüedad
(el más viejo primero), agrupados de forma útil para la cocina.

## Fuera de alcance (explícitamente)

- Autenticación avanzada / roles complejos de usuario
- Procesamiento de pagos reales (pasarelas)
- Despliegue en producción
- Integraciones externas (delivery, facturación electrónica, etc.)

## Convenciones de trabajo con el agente

- Los mensajes de commit explican **qué se decidió**, no qué archivo se tocó
  (ej. "Modelo de Pedido con estados por ítem", no "update models.py").
- Toda decisión de diseño no trivial que tome el agente y se acepte debe quedar
  reflejada en un ADR si es arquitectónica, o en `ASSUMPTIONS.md` si es un
  supuesto sobre un vacío del enunciado.
- Cada sesión de trabajo con el agente se registra en `BITACORA-IA.md`: qué se
  pidió, qué propuso, qué se aceptó/rechazó, qué quedó sin verificar.

## Estado actual del proyecto

- [x] Repositorio creado
- [x] Modelo de datos definido
- [x] Backend Django levantado
- [x] API del flujo pedido → cola → estado (probada con curl)
- [x] Frontend React levantado
- [x] ADR (3 hasta ahora: elección de herramienta de IA, estado de preparación, modelo de inventario)
- [x] Flujo end-to-end funcionando (falta conectar el frontend a la API)
