# ADR-001: Elección de herramienta de IA para el desarrollo

## Contexto

La prueba técnica exige trabajar con agentes de IA durante toda la semana y
poder defender cada decisión tomada con su ayuda. Se necesitaba desde el
primer día una herramienta ágentica principal, capaz de leer el contexto del
proyecto (`AGENTS.md`) y generar código directamente sobre el repositorio, y
una segunda vía de respaldo por si la principal falla, se queda sin cuota, o
da una respuesta que conviene contrastar antes de aceptarla. Además, el curso
exige que la herramienta principal permita verificación académica del
trabajo realizado.

## Decisión

Se usará **GitHub Copilot (Agent Mode en VS Code)** como herramienta
agéntica principal para escribir y modificar el código del proyecto, apoyada
en el archivo `AGENTS.md` como contexto persistente. Como vía de respaldo se
usará **Claude (chat)**, para resolver dudas puntuales, revisar decisiones de
diseño antes de aplicarlas, y como alternativa si Copilot no está disponible
o su respuesta necesita una segunda opinión.

## Alternativas descartadas

- **Antigravity**: se descartó por no ser la herramienta con la que se tiene
  mayor familiaridad de uso dentro del flujo de trabajo en VS Code, lo que
  habría restado tiempo de la semana a aprender la herramienta en vez de
  avanzar en el sistema.
- **Codex**: se descartó por la misma razón — Copilot ya está integrado de
  forma nativa en el editor que se usa a diario, mientras que sumar otra
  herramienta agéntica distinta habría duplicado el aprendizaje sin un
  beneficio claro para el alcance de esta prueba.

## Consecuencias

- El trabajo queda sujeto a los **límites de cuota** de Copilot; si se agota
  antes de terminar la semana, hay que recurrir a Claude para sostener el
  ritmo mientras se restablece.
- Al ser Copilot la vía requerida para verificación académica, todo el
  código generado con su ayuda debe quedar trazable en los commits y
  reflejado en `BITACORA-IA.md`.
- Usar dos herramientas distintas implica mantener el contexto sincronizado
  entre ambas (Copilot lee `AGENTS.md` automáticamente; a Claude hay que
  pasarle el contexto relevante manualmente en cada conversación).
