# ADR-002: Estado de preparación como campo simple, no como historial

## Contexto

Cada ítem de pedido necesita un estado de preparación (pendiente, en
preparación, listo, entregado, cancelado) que la cocina y el mesero
puedan consultar y actualizar. Había que decidir si ese estado se
modela como un campo simple sobre `ItemPedido`, o como una tabla de
historial que registre cada transición con su fecha.

## Decisión

Se modela como un campo `estado` con `choices` directamente en
`ItemPedido`. El estado actual siempre está disponible con una sola
consulta, sin necesidad de joins ni de calcular "el último estado" de
una lista de eventos.

## Alternativas descartadas

- **Tabla de historial de estados** (una fila por cada cambio, con
  fecha): se descartó porque el enunciado no exige trazabilidad de
  cuándo ocurrió cada transición, solo el estado actual de cada ítem y
  la cola ordenada por antigüedad de creación del ítem, no de sus
  cambios de estado. Agregar esa tabla habría sumado complejidad
  (consultas más lentas, más migraciones) sin un requisito que la
  justifique dentro del alcance de esta prueba.

## Consecuencias

- Consultar la cola de cocina o el estado de un ítem es una operación
  directa y rápida.
- Se pierde la capacidad de auditar cuánto tiempo estuvo un ítem en
  cada estado (por ejemplo, cuánto tardó la cocina en empezar a
  prepararlo). Si en el futuro se necesitara esa métrica, habría que
  migrar a una tabla de historial o agregar campos de timestamp por
  transición (`en_preparacion_desde`, `listo_desde`, etc.).
- La validación de que "un ítem solo se cancela si aún no se ha
  empezado a preparar" se resuelve comparando el estado guardado en
  base de datos contra el estado nuevo antes de guardar (en
  `ItemPedido.clean()`), en vez de consultar el último registro de una
  tabla de historial.
