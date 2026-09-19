# ADR-003: Modelo de inventario como bitácora de movimientos

## Contexto

El enunciado exige que un plato sin ingredientes disponibles deje de
ofrecerse, y se asumió que los platos tienen una receta de ingredientes
que se descuentan del stock. Había que decidir cómo modelar el
inventario (¿el stock vive directo en `Ingrediente`, o se maneja como
una bodega/almacén aparte?) y en qué momento del flujo del pedido se
descuenta ese stock.

## Decisión

**Modelo de inventario:** el stock actual vive en
`Ingrediente.cantidad_disponible`, y cada cambio (restock o consumo)
queda registrado como una fila en `MovimientoInventario` (tipo entrada
o salida). Al guardarse un movimiento, este ajusta automáticamente la
cantidad disponible del ingrediente — así nunca se modifica el stock
directamente, siempre pasa por un movimiento trazable.

**Momento del descuento:** el stock se descuenta cuando el ítem de
pedido pasa al estado `en_preparacion`, no al crearse el pedido ni al
confirmarlo.

## Alternativas descartadas

- **Bodegas/almacenes separados** (una entidad `Almacen` con su propio
  stock independiente): se descartó porque el caso no menciona más de
  una bodega o punto de despacho — un restaurante tiene un solo
  inventario de cocina. Esa complejidad aplicaría a un caso con varias
  bodegas, no a este.
- **Descontar el stock al crear el pedido**: se descartó porque un
  ítem puede cancelarse mientras está en estado `pendiente` (regla de
  negocio del enunciado). Si el stock se descontara al crear el ítem,
  cancelarlo obligaría a "devolver" el stock, complicando la lógica sin
  necesidad — es más simple descontar solo cuando la cocina realmente
  empieza a usar los ingredientes, momento en el que cancelar deja de
  ser una opción válida.

## Consecuencias

- El stock de un ingrediente siempre puede reconstruirse sumando sus
  movimientos, lo que facilita auditar y depurar inconsistencias.
- Mientras un ítem está `pendiente`, el sistema no reserva ingredientes
  para él — dos pedidos pendientes que compiten por el mismo
  ingrediente escaso podrían, en teoría, ambos parecer "disponibles"
  hasta que uno de los dos entra a preparación. Esto no se resuelve en
  el alcance actual; queda como limitación conocida.
- `Plato.disponible` se calcula en el momento (comparando la receta
  contra el stock actual), por lo que siempre refleja el inventario
  real sin necesidad de un job o señal adicional que lo recalcule.
