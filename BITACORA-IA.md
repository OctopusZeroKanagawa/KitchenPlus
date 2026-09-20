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

## Sesión 3 — [19 de Septiembre del 2026]

**Herramienta:** GitHub Copilot (Agent Mode, VS Code)
**Contexto dado:** `AGENTS.md` + `ASSUMPTIONS.md`

**Se pidió:**

1. Configurar CORS en el backend para que el frontend en desarrollo
   (Vite) pudiera consumir la API.
2. Crear el proyecto frontend con Vite + React, con dos pantallas
   (`CrearPedido`, `ColaCocina`) y navegación simple.
3. Agregar endpoints de solo lectura `GET /api/mesas/` y
   `GET /api/platos/` para poblar el formulario.
4. Implementar `CrearPedido`: formulario que consume `mesas`/`platos`
   y envía `POST /api/pedidos/`.
5. Implementar `ColaCocina`: polling cada 5s a `GET /api/cocina/cola/`,
   con botón para avanzar el estado de cada ítem vía PATCH.

**Qué propuso el agente y qué se corrigió:**

- **CORS**: primer intento solo permitía `http://localhost:5173`.
  Falló en el navegador real porque Vite abrió en `127.0.0.1:5173`
  en este entorno — se agregó ese segundo origen tras diagnosticarlo
  con Playwright (consola del navegador mostró el error de CORS).
- **`mesas`/`platos`**: en la primera verificación del endpoint de
  platos, el único plato de prueba no tenía receta asociada, así que
  `disponible` salía `true` de forma trivial (lista vacía). Se pidió
  crear un ingrediente con stock 0 y asociarlo, confirmando que
  `disponible` pasaba a `false` y volvía a `true` al reponer stock —
  antes de eso no había evidencia real de que el cálculo funcionara.
- **Código muerto detectado y removido**: `PlatoSerializer.get_disponible`
  tenía una rama `callable(obj.disponible)` que nunca se ejecuta
  porque `disponible` es una `@property`, no un método. Se simplificó
  a `bool(obj.disponible)`.
- **`ItemPedidoSerializer` sin dato útil para cocina**: exponía
  `pedido` (el ID), no el número de mesa. Se agregó el campo
  `mesa_numero` vía `source='pedido.mesa.numero'`, verificado con
  curl mostrando que dos ítems de pedidos distintos con la misma mesa
  reportaban el mismo `mesa_numero` (prueba de que no estaba
  hardcodeado).
- **Discrepancia repetida entre "resumen" y código real**: en más de
  una ocasión, lo que el agente describió como el contenido del
  archivo no coincidía con el diff real generado después (faltaba el
  `<h1>` de `ColaCocina`, y el mensaje de error había dejado de ser
  condicional — se habría mostrado un recuadro de error vacío en todo
  momento). Se detectó pidiendo explícitamente el diff real en vez de
  aceptar el resumen, y se corrigió antes de comitear.
- **Verificación real vs. build**: un "build exitoso" (`npm run build`)
  no demuestra que la funcionalidad funcione en el navegador. Se pidió
  verificación real con Playwright (headless) en varios puntos, lo
  cual sí sacó a la luz el problema de CORS con `127.0.0.1` que un
  build nunca habría detectado.

**Qué se aceptó:**

- Todas las correcciones anteriores, tras confirmar cada una con
  evidencia directa (diff real o prueba en navegador), no con el
  resumen del agente.
- El flujo end-to-end completo (crear pedido → aparece en cola →
  avanza de estado → desaparece al llegar a "listo"), verificado con
  un script de Playwright que crea un pedido real y sigue su ciclo de
  vida completo en la interfaz.
- No usar ramas de git por el tiempo limitado de la prueba (ver nota
  en `ASSUMPTIONS.md`, sección "Decisiones de proceso").

**Qué se corrigió como hábito de trabajo:**

- Se dejó de aceptar resúmenes del agente como evidencia suficiente;
  desde la mitad de esta sesión, cada cambio se confirmó pidiendo el
  diff real (`git diff`) o la salida cruda de comandos/pruebas, nunca
  la descripción que el agente hace de sí mismo.
- Se instaló y desinstaló Playwright dos veces (una por sesión de
  prueba) para no dejarlo como dependencia permanente del proyecto.

**Qué quedó sin verificar:**

- No se revisó si el polling de 5 segundos maneja bien el caso de
  que la pestaña quede en segundo plano por mucho tiempo (los
  navegadores pueden limitar timers en pestañas inactivas). No es
  crítico para la demo pero podría afectar un uso prolongado real.
- La base de datos de desarrollo quedó con datos residuales de varias
  sesiones de prueba; falta limpiarla antes de la demo final.

## Sesión 4 — [19 de Septiembre del 2026]

**Herramienta:** GitHub Copilot (Agent Mode, VS Code)
**Contexto dado:** `AGENTS.md` + `ASSUMPTIONS.md`

**Se pidió:**

1. Implementar la regla de pagos parciales (una de las 4 reglas de
   negocio obligatorias, hasta entonces solo modelada, sin API): pago
   individual por pedido y pago del total de una mesa.
2. Pantalla `PagarMesa` en el frontend para esa funcionalidad.
3. Redactar `README.md` en la raíz con instrucciones de instalación.

**Qué propuso el agente y qué se verificó:**

- **API de pagos**: `POST /api/pagos/` con la lógica exacta pedida
  (pago individual marca `pagado` al cubrir el subtotal; pago total
  rechaza montos insuficientes con mensaje claro y marca todos los
  pedidos no pagados de la mesa al cubrirse). Se agregó
  `Mesa.total_pendiente` y `GET /api/mesas/<id>/cuenta/`. 8 tests
  (3 nuevos de pago) pasando.
- **Discrepancia diff vs. salida pegada**: al revisar el diff de los
  tests, una línea de `test_pago_total_completo` parecía tener un
  `self.client.post()` sin la URL como primer argumento — lo cual
  habría hecho fallar el test, contradiciendo el "ok" reportado. Se
  pidió el contenido exacto del archivo con `cat -A` y la ejecución
  aislada de ese test: el archivo real sí tenía la URL correcta: fue
  un error de transcripción en el mensaje anterior, no un bug real.
- **Pruebas de frontend con "trampas" ocultas (dos veces)**: al pedir
  verificar en navegador el caso de "pago total insuficiente":
  1. Primer intento: interceptó `window.fetch` para devolver una
     respuesta 400 fabricada por el propio script, sin que la
     petición llegara al backend real.
  2. Segundo intento (tras señalar el problema): inyectó un `<div>`
     con el mensaje de error directamente en el DOM con
     `document.createElement`, en vez de hacer clic en el botón real
     y dejar que el componente React lo procesara — la petición al
     backend sí fue real esta vez, pero la parte de "así se ve en
     pantalla" seguía siendo simulada.
  3. Al pedir la versión sin ningún atajo (clic real en el botón
     `pagarTotalMesa`), el agente identificó correctamente que **el
     escenario no es alcanzable desde la UI actual**: el botón
     siempre envía `cuenta.total_pendiente` exacto, calculado por el
     propio backend, por lo que nunca puede generar un monto
     insuficiente por diseño. Se documentó esto con un comentario en
     el código en vez de forzar una prueba artificial.
- **Verificación del README ("correr desde cero")**: se pidió clonar
  el repo en una carpeta temporal y seguir las instrucciones al pie
  de la letra. Un primer intento devolvió una mesa existente en un
  clon supuestamente vacío — se sospechó que `db.sqlite3` estaba
  mal trackeado en git a pesar del `.gitignore` (`git log --all` lo
  descartó: el archivo nunca se comiteó) y luego que había una
  colisión de puerto con el servidor de desarrollo real (`lsof`/`ss`
  también lo descartaron: no había nada escuchando en 8000/5173 en
  ese momento). Repitiendo la verificación en puertos alternativos
  (8001/5174) desde un clon nuevo, la API sí devolvió `[]` real. La
  causa exacta de la primera "mesa fantasma" quedó sin explicación
  definitiva, pero la verificación final es sólida.

**Qué se aceptó:**

- La API y los tests de pagos, sin cambios adicionales.
- La pantalla `PagarMesa`, con la nota en el código explicando por
  qué el caso de error de monto insuficiente no es alcanzable desde
  ese botón.
- El `README.md`, tras confirmar con una verificación limpia y sin
  ambigüedad que sus instrucciones funcionan de punta a punta.

**Qué se corrigió como hábito de trabajo:**

- Se reforzó la lección de la sesión anterior: una "prueba en
  navegador" solo cuenta como evidencia real si el clic ocurre sobre
  el elemento real de la UI y la petición llega sin interceptar al
  backend real. Se rechazaron dos intentos que no cumplían esto antes
  de aceptar el tercero.
- Ante una discrepancia entre lo reportado y la evidencia, se
  verificó con la fuente más directa posible en cada caso (`cat -A`
  del archivo, `git log --all`, `lsof`/`ss`) en vez de asumir cuál de
  las dos versiones era la correcta.

**Qué quedó pendiente para la próxima sesión:**

- Revisar/mejorar la parte visual del frontend (hasta ahora
  priorizada la funcionalidad sobre el diseño).
- Confirmar si falta algo más del enunciado antes de la entrega
  final del domingo.
- Limpiar los datos residuales de pruebas en la base de datos de
  desarrollo antes de la demo.

## Sesión 5 — [20 de Septiembre del 2026]

**Herramienta:** GitHub Copilot (Agent Mode, VS Code)

**Se pidió:** limpiar la base de datos de desarrollo y crear un
management command de seed con datos realistas para la demo,
incluyendo deliberadamente un ingrediente sin stock para poder
demostrar en vivo la regla de disponibilidad de platos.

**Qué se encontró:** al sembrar ese caso de prueba, el plato
correspondiente seguía apareciendo como `disponible: true`. Se
descubrió que `Plato.disponible` en el modelo había perdido el
decorador `@property` en algún punto entre sesiones anteriores (no
se identificó en cuál exactamente), haciendo que `bool(obj.disponible)`
evaluara siempre un objeto método, que en Python siempre es "verdadero".
Este bug llevaba tiempo sin detectarse porque ninguna sesión anterior
volvió a probar explícitamente el caso de un plato sin stock después
de las primeras verificaciones.

**Qué se corrigió:** se restauró el `@property`, y se simplificó
`PlatoSerializer.disponible` a un `BooleanField` plano. Se verificó
contra la suite completa de tests (8/8 pasando) y con curl, antes de
comitear el fix por separado del seed de demo.

**Lección:** un caso de prueba "no crítico" (un plato sin stock) que
no se revisita periódicamente puede ocultar una regresión silenciosa
durante varias sesiones. Vale la pena, de cara a la defensa, volver a
probar manualmente cada regla de negocio una vez más antes de la
entrega final, no asumir que "ya se verificó una vez" sigue siendo
cierto después de ediciones posteriores al mismo código.
