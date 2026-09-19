# BITACORA-IA.md

Registro de sesiones de trabajo con agentes de IA. Cada entrada indica
qué se pidió, qué propuso el agente, qué se aceptó/rechazó, y qué
quedó sin verificar.

---

## Sesión 1 — [18 de Septiembre del 2026]

**Herramienta:** GitHub Copilot (Agent Mode, VS Code)
**Contexto dado:** `AGENTS.md` + `ASSUMPTIONS.md`

**Se pidió:**

1. Crear el modelo de datos de la app `cocina` (Mesa, Pedido,
   ItemPedido, Plato, Ingrediente, RecetaPlato, MovimientoInventario,
   Pago) con las reglas de negocio y assumptions ya definidos.
2. Inicializar el proyecto Django base (nunca se había levantado
   `manage.py`/`config/`).
3. Instalar dependencias en un entorno virtual, generar
   `requirements.txt` y ajustar `.gitignore`.
4. Correr `makemigrations`/`migrate` y hacer los commits.

**Qué propuso el agente:**

- El modelo completo con los 8 modelos pedidos, incluyendo validación
  en `ItemPedido.clean()` para la regla de cancelación y el límite de
  cola (100 ítems), y `MovimientoInventario.save()`/`delete()` para
  mantener el stock sincronizado.
- Una decisión de diseño **no especificada previamente**: descontar el
  stock del ítem al pasar a estado `en_preparacion` (no al crear el
  pedido). Se evaluó y se aceptó — ver ADR-003.
- Estructura base del proyecto Django (`manage.py`, `config/`) que no
  existía todavía.

**Qué se aceptó:**

- Todo el modelo de datos, tras revisar el diff campo por campo contra
  el diseño acordado previamente.
- La decisión del momento de descuento de stock (en `en_preparacion`),
  justificada porque antes de ese estado el ítem aún puede cancelarse.
- Los mensajes de commit, después de pedir que separara el commit de
  "inicializar proyecto" del de "modelo de datos", y que acortara el
  título del segundo commit dejando el detalle en el cuerpo.

**Qué se corrigió / se le pidió ajustar:**

- El primer intento de mensaje de commit tenía el detalle completo
  pegado al título; se pidió separarlo en título corto + cuerpo.
- Quedaron `apps.py` y `db.sqlite3` fuera del primer intento de commit;
  se corrigió con `git commit --amend` para `apps.py`, y se agregó
  `*.sqlite3` al `.gitignore` en vez de comitearlo.

**Qué quedó sin verificar:**

- No se revisó línea por línea el contenido de la migración
  `0002_alter_...` generada automáticamente por una diferencia de
  versión de Django; se asumió que es un cambio cosmético sin impacto
  en las reglas de negocio, pero no se confirmó con un diff detallado.
- No se corrieron tests automatizados todavía — solo se verificó que
  las migraciones aplicaran sin error.

## Sesión 2 — [19 de Septiembre del 2026]

**Herramienta:** GitHub Copilot (Agent Mode, VS Code)
**Contexto dado:** `AGENTS.md` + `ASSUMPTIONS.md`

**Se pidió:**
Construir la capa de API (serializers + vistas con APIView/generics,
sin ViewSets ni routers) para el flujo priorizado: crear pedido → ver
cola de cocina → cambiar estado de un ítem.

**Qué propuso el agente (primer intento):**

- `PedidoSerializer`, `ItemPedidoSerializer`, vistas para los 4
  endpoints y las urls correspondientes.

**Qué se detectó al revisar antes de comitear:**

1. **Bug que rompe en tiempo de ejecución:** `PedidoSerializer` tenía
   un campo `items` con `source='items'` — nombre y source idénticos,
   lo cual DRF rechaza con `AssertionError` apenas se use el
   serializer. No se detectó leyendo el código en abstracto, sino
   pidiendo explícitamente una prueba real con `curl` contra el
   servidor corriendo.
2. **Regla de negocio no aplicada:** al crear los ítems de un pedido
   nuevo, se usaba `.save()` en vez de `.full_clean()` + `.save()`,
   por lo que el límite de 100 ítems en cola (definido en
   `ItemPedido.clean()`) no se validaba al crear pedidos, solo al
   cambiar el estado de un ítem existente.
3. **Valor de estado corrupto:** en una corrección posterior, un ítem
   quedó guardado con `estado="pending"` (inglés) en vez de
   `"pendiente"`. Django no valida `choices` a nivel de base de
   datos, así que el registro se guardó sin error pero quedaba
   invisible para cualquier filtro que comparara contra `"pendiente"`.
   Se investigó con `git log --all -- views.py`, confirmando que el
   bug nunca llegó a comitearse — ocurrió solo en memoria durante la
   edición. Se resolvió recreando la base de datos de desarrollo
   desde cero (sin datos reales que perder) y repitiendo las pruebas.
4. **Intento de commit sin autorización:** durante el diagnóstico del
   punto 3, el agente ejecutó `git commit` con `|| true` antes de
   preguntar si debía comitear — la pregunta posterior era sobre algo
   que ya había intentado hacer. Se le indicó explícitamente no
   volver a comitear sin confirmación, incluso durante diagnósticos.

**Qué se aceptó:**

- Las correcciones de los 3 bugs, una vez verificadas con peticiones
  `curl` reales (no solo con la palabra del agente) contra una base de
  datos limpia.
- Un solo commit para toda la capa de API (en vez de 3 por endpoint),
  porque los archivos son interdependientes y un commit intermedio
  habría dejado código roto en el historial.

**Qué quedó sin verificar:**

- No se identificó la causa exacta de por qué apareció `"pending"` en
  inglés (el agente no la explicó, solo confirmó que nunca se comiteó
  y que la corrección funciona). Si vuelve a aparecer, investigar más
  a fondo.
- No hay tests automatizados para estos endpoints todavía — la
  verificación fue manual con `curl`.
