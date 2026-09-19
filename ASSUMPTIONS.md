# ASSUMPTIONS.md

Supuestos asumidos para llenar los vacíos que el enunciado no especifica
directamente, para el Sistema E (pedidos y cocina de restaurante).

## Inventario y disponibilidad de platos

- Los ingredientes se pueden reabastecer (restock). Cuando el stock de un
  ingrediente vuelve a estar disponible, los platos que lo requieren
  vuelven a estar disponibles automáticamente.
- Cada plato tiene una receta: una lista de ingredientes con la cantidad
  que requiere de cada uno (ej. 8 g de sal). Al confirmarse un ítem de
  pedido, esa cantidad se descuenta del stock disponible del ingrediente.
- El restock y el consumo de ingredientes quedan registrados como
  movimientos de inventario (una bitácora de entradas/salidas), en vez de
  modelarse como bodegas físicas separadas, ya que el enunciado no
  menciona múltiples bodegas para este caso.

## Mesas, pedidos y pagos

- Una mesa puede tener varios pedidos abiertos al mismo tiempo (por
  ejemplo, pedidos hechos en momentos distintos de la misma visita). Cada
  pedido tiene su propio subtotal.
- El total de la mesa es la suma de los pedidos aún no pagados.
- El pago puede hacerse por pedido individual o como pago total de la
  mesa, lo cual permite los pagos parciales que exige el enunciado.

## Estado de preparación

- El estado de preparación de un ítem de pedido se modela como un campo
  simple de opciones (pendiente, en preparación, listo, entregado,
  cancelado), no como una tabla de historial de cambios, porque el
  enunciado no exige trazabilidad de cada transición, solo el estado
  actual por ítem.

## Límite operativo de la cola

- Se asume un límite máximo de 100 ítems simultáneos en la cola de
  cocina (pendientes + en preparación), como regla propia para evitar
  que el sistema modele una situación irreal de cola infinita. Al llegar
  al límite, el sistema no debería permitir agregar nuevos ítems hasta
  que la cola baje.

## Decisiones de proceso

- Se consideró trabajar con ramas de git (una por funcionalidad) como
  buena práctica de flujo de trabajo en equipo. Se descartó por el
  tiempo limitado de la prueba individual: para esta semana, un
  historial lineal en `main`, con commits pequeños y bien
  documentados, da la misma trazabilidad que exige el enunciado sin
  el costo de gestionar merges. Con más de un desarrollador o más
  tiempo disponible, ramas por feature habría sido la elección
  correcta.