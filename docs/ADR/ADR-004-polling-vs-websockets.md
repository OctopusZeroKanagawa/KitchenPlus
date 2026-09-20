# ADR-004: Polling en vez de WebSockets para la cola de cocina

## Contexto

La pantalla de cocina necesita reflejar cambios en la cola (nuevos
ítems, cambios de estado hechos por otros usuarios) sin que el
usuario tenga que recargar la página manualmente. Había que decidir
el mecanismo: actualización push en tiempo real (WebSockets/SSE) o
polling periódico desde el cliente.

## Decisión

Se implementó polling: el frontend hace `GET /api/cocina/cola/` cada
5 segundos con `setInterval`, sin mantener una conexión persistente
con el servidor.

## Alternativas descartadas

- **WebSockets (Django Channels)**: se descartó por el costo de
  configuración adicional (requiere un servidor ASGI, un backend de
  canales como Redis para producción, y una capa nueva de código en
  el backend) que no se justifica para el alcance y tiempo de esta
  prueba. Habría dado actualizaciones instantáneas, pero el objetivo
  aquí es demostrar el flujo funcionando, no optimizar latencia.
- **Server-Sent Events (SSE)**: más simple que WebSockets al ser
  unidireccional, pero igual requiere infraestructura de streaming
  en el backend que Django REST no ofrece de forma nativa sin
  paquetes adicionales. Se descartó por la misma razón de tiempo.

## Consecuencias

- Hay un retraso de hasta 5 segundos entre que algo cambia (un nuevo
  pedido, un cambio de estado desde otra sesión) y que se refleje en
  pantalla — aceptable para una cocina real, donde no se necesita
  precisión de milisegundos.
- Cada cliente conectado genera una petición HTTP completa cada 5
  segundos, incluso si nada cambió. Con pocos clientes (el caso de
  un restaurante pequeño) esto no es un problema; con muchos
  clientes simultáneos, esta estrategia no escalaría bien y
  requeriría revisar el enfoque.
- La implementación quedó simple: un `useEffect` con `setInterval` y
  su `cleanup`, sin dependencias nuevas ni cambios en el backend.
