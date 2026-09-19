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
