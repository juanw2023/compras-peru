# Historial de cambios

Sacado de `git log`. Las versiones son las del paquete de plugins y de la wheel `compras_multicomercio`.

## Sin publicar

- Validador del paquete (`scripts/validar.py`) y pruebas (`tests/`).
- `icon` declarado en el `plugin.json` de Claude para el directorio de plugins.
- README reescrito para usuarios sin conocimientos técnicos; guía para publicar en los directorios oficiales y borrador de política de privacidad.
- Descripciones de las skills con frases habituales en Perú («compra del súper», «cuánto cuesta», «arma mi carrito»).

## 0.4.5 — 2026-10-22

- Tarifa por pedido gestionado: S/ 5 o el 5 % de la compra, lo que sea mayor, desglosada en la cotización (`cobro`).
- 2026-10-31: los textos públicos hablan de «el operador», sin nombres de personas.

## 0.4.4 — 2026-10-21

- Búsqueda más tolerante: avisa de productos «parecidos» cuando ninguno tiene todas las palabras pedidas.
- Plugin de Codex movido a `codex/.codex-plugin/` con icono, `interface` y frases de ejemplo.

## 0.4.3

- No hay commit propio en este repo (la versión pasó de 0.4.2 a 0.4.4).

## 0.4.2 — 2026-10-21

- Primera versión pública: plugins para Claude Code, Codex y Gemini CLI, con marketplaces para Claude y Codex, skill `compras-peru` y servidor MCP remoto con clave de suscripción.
