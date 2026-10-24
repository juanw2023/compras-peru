# Publicar Compras Perú en los directorios de agentes

Estado al 2026-10-24 sobre la revisión `f9c751f3bffaf338462eb18828de452d5588a47f` (0.4.5). Este documento separa lo que **ya funciona** (instalar desde GitHub) de lo que significa **aparecer en una tienda pública** (directorio de Anthropic, directorio de plugins de ChatGPT/Codex), que exige un envío por portal, una revisión y datos que no están en el código.

## Frontera de este repositorio

Aquí vive solo el **empaquetado** para cada agente: `claude/` (plugin de Claude Code), `codex/` (plugin de Codex), `gemini-extension.json` (Gemini CLI) y los dos catálogos (`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`). Los tres paquetes lanzan el mismo cliente local:

```
uvx --quiet --from https://market.ori-song.com/static/descargas/compras_multicomercio-0.4.5-py3-none-any.whl compras-cliente
```

con `COMPRAS_PERU_URL=https://market.ori-song.com/mcp` y la clave del cliente en `COMPRAS_PERU_TOKEN`. El cliente `compras_multicomercio`, el servidor MCP remoto de `market.ori-song.com/mcp`, la web, los pagos y la autenticación por clave (Bearer) **no están en este repositorio**. Cualquier cambio de autenticación del servidor (por ejemplo OAuth) se hace allí, no aquí.

## Las cuatro vías y qué le corresponde a este producto

| Vía | Qué es | Cómo se entra | Estado para Compras Perú |
|---|---|---|---|
| Marketplace propio de Claude Code | Catálogo `.claude-plugin/marketplace.json` en este repo. Cualquiera lo añade con `claude plugin marketplace add juanw2023/compras-peru`. | Solo publicar el archivo en GitHub; sin formulario. | **Operativo.** `claude plugin validate --strict` pasa en el plugin y en el catálogo. No es una tienda pública ni implica aprobación de Anthropic. |
| Directorio de Anthropic (claude.ai/directory) | Catálogo que la gente ve en claude.ai, Cowork y Claude Code. Se envía un **plugin bundle** desde un repo público de GitHub en el portal claude.ai/directory/manage. | Plan de pago (Pro, Max, Team u Enterprise), GitHub conectado en claude.ai, validación en el portal, preguntas de datos, 4 reconocimientos, escaneo de seguridad y revisión humana de la primera versión. | **Enviable con pendientes.** El paquete `claude/` cumple las comprobaciones automáticas conocidas (README ≥ 40 palabras, `license`, nombre, icono, rutas). Faltan URLs de privacidad, soporte y términos (ver pendientes). El servidor MCP local hará que un revisor lo mire siempre (regla «Runs a pinned npx or uvx package»). En claude.ai chat el MCP local **no se carga**: allí el plugin sería solo la skill. |
| Directorio de conectores de Claude | Listado de un **servidor MCP remoto** (URL https) que la gente conecta desde claude.ai. | Mismo portal, opción «MCP connector». Exige OAuth 2.0 para servidores que actúan sobre la cuenta del usuario, `title` y `readOnlyHint`/`destructiveHint` en cada herramienta, cuenta de prueba para revisores, política de privacidad, documentación, icono. | **Bloqueado fuera de este repo.** El servidor `market.ori-song.com/mcp` autentica con clave Bearer, no con OAuth 2.0. Anthropic recomienda enviar el conector además del plugin, pero eso requiere cambiar el servidor. |
| Plugins de Codex (marketplace propio) | Catálogo `.agents/plugins/marketplace.json` en este repo. `codex plugin marketplace add juanw2023/compras-peru` y `codex plugin add compras-peru@compras-peru-market`. | Solo publicar el archivo en GitHub. | **Operativo.** Codex busca `.agents/plugins/marketplace.json` (también acepta `.claude-plugin/marketplace.json`); `policy.installation=AVAILABLE` y `policy.authentication=ON_USE` son valores válidos; `.codex-plugin/plugin.json` sigue admitido como formato de compatibilidad; `.mcp.json` con `command`/`args`/`env`/`env_vars` es el formato stdio de Codex. |
| Directorio de plugins de ChatGPT y Codex | Catálogo público único de OpenAI (el antiguo directorio de apps de ChatGPT migró a «Plugin directory» el 2026-07-09). Se sube un ZIP en el portal de plugins. | Organización verificada en OpenAI Platform; manifiesto con `interface` completa; servidor MCP **remoto https** con autenticación **none, OAuth o mixta**; cuenta de prueba sin MFA para revisores; política de privacidad y términos; sin hooks. | **Bloqueado por dos motivos independientes**, ambos fuera de este repo (detalle abajo). |

## El bloqueo concreto del directorio de ChatGPT/Codex

1. **Autenticación.** La página oficial «Upload and submit your plugin» (developers.openai.com/plugins/deploy/submission, sección *Authentication limitations*) dice que el formulario de conexión del portal admite «no authentication, OAuth, and mixed unauthenticated/OAuth access», que «the manifest schema accepts API-key declarations, but the portal doesn't provide an API-key connection flow or a bearer-token input» y que «this limitation also applies to Basic and custom-header API-key declarations». El servidor `market.ori-song.com/mcp` usa clave Bearer. **No hay rechazo oficial registrado**: nadie ha enviado nada; el bloqueo es que el portal no ofrece dónde poner esa clave. La solución es que el servidor remoto implemente OAuth 2.1 conforme a la especificación de autorización de MCP (developers.openai.com/plugins/build/auth), o un modo «mixto» en el que las búsquedas sean anónimas y solo carrito/pedido exijan OAuth. Eso se construye en el repositorio del servidor, no aquí. **No se debe quitar la clave ni abrir el servidor para contentar al portal.**
2. **Transporte.** El paquete actual declara un servidor MCP **local (stdio)** lanzado con `uvx`. Según «Submit desktop-only plugins» (developers.openai.com/plugins/deploy/desktop-only), los plugins con servidor MCP local «display a Desktop only badge … and can only be installed from the ChatGPT desktop app», y su envío «is limited to approved partners»: hay que enviar el ID de organización a un representante de OpenAI y esperar la inclusión en la lista permitida antes de enviar. Sin ese contacto, la única vía pública es declarar el servidor remoto `https://market.ori-song.com/mcp` en `mcp.json`, lo que vuelve al punto 1.

Las dos cosas pueden prepararse en paralelo: cuando el servidor tenga OAuth, en este repo bastará con cambiar `codex/.mcp.json` a una entrada remota y rellenar las URLs de `interface`.

Nota de verificación: desde este entorno los dominios `developers.openai.com`, `help.openai.com` y `market.ori-song.com` están bloqueados por la política de red, así que las citas de OpenAI provienen de los fragmentos indexados de sus páginas oficiales y del código fuente público de Codex (`openai/codex`, commit `970111f6`), no de la lectura de la página completa. Conviene abrir esas páginas antes de enviar.

## Ficha de presentación (lista para copiar)

Texto tomado de los manifiestos de esta revisión. Donde una vía impone un límite, se indica.

- **Nombre técnico:** `compras-peru` (cumple las reglas de nombre de Anthropic y de OpenAI: minúsculas, dígitos y guiones, ≤ 64).
- **Nombre visible:** Compras Perú (12 caracteres; límite OpenAI en envío final: 30).
- **Descripción corta (OpenAI, ≤ 30):** Supermercados de Perú con Juan (30).
- **Descripción (Anthropic, `description`, 144 caracteres):** Busca en Tottus, Wong y Metro con foto y ficha exactas, compara, arma el carrito y encarga la compra a Juan, que compra y entrega por ti (Perú).
- **Descripción larga (OpenAI `longDescription`, 252 caracteres; límite 4 000):** Busca en Tottus, Wong y Metro con la foto y la ficha exactas, compara precios, arma el carrito y encarga la compra a Juan, que compra, paga y coordina la entrega. El agente nunca compra ni paga solo. Suscripción S/ 4 por 30 días en market.ori-song.com.
- **Desarrollador / autor:** Compras Perú (`author.name`, `developerName`).
- **Categoría:** Productivity (Codex/OpenAI) · productivity (catálogo de Claude Code; campo libre).
- **Palabras clave:** peru, supermercado, compras, tottus, wong, metro, mcp.
- **Sitio web / homepage:** https://market.ori-song.com
- **Repositorio:** https://github.com/juanw2023/compras-peru (público; responde 200 sin autenticación).
- **Documentación:** https://github.com/juanw2023/compras-peru#readme
- **Icono:** `claude/assets/icon.png` y `codex/assets/icon.png`, el mismo PNG RGB cuadrado de 1080 × 1080 px, 301 560 bytes.
- **Prompts de ejemplo (`defaultPrompt`):** «Compara leche Gloria, arroz Costeño y aceite Primor en Tottus, Wong y Metro» · «Arma mi carrito del súper y encárgaselo a Juan».
- **Licencia:** MIT (`license` en ambos manifiestos y `LICENSE` en la raíz del repo).
- **Componentes:** 1 skill (`skills/compras-peru/SKILL.md`), 1 servidor MCP local (`compras-peru`), sin hooks, agentes ni comandos.
- **Qué ejecuta y a dónde se conecta (para las preguntas de datos y el escaneo de seguridad):** descarga el wheel `compras_multicomercio-0.4.5` desde `market.ori-song.com/static/descargas/` con `uvx`; Tottus se consulta desde la conexión del usuario; Wong, Metro, carritos y pedidos van a `https://market.ori-song.com/mcp` con la clave como Bearer. `pedir_compra` envía contacto y dirección del cliente a ese servicio. Otros destinos del cliente no se pueden verificar desde este repositorio porque su código vive fuera.
- **Autenticación hoy:** clave de suscripción (Bearer). Claude Code la pide con `userConfig.compras_token` (sensible, guardada en el llavero). Codex la lee de `COMPRAS_PERU_TOKEN` (`env_vars`) o del archivo `~/.config/compras-peru/clave`. Gemini CLI la pide como ajuste sensible.
- **Cobros:** suscripción S/ 4 por 30 días (Yape) y tarifa por pedido gestionado de S/ 5 o 5 %, lo que sea mayor. El agente nunca compra ni paga.
- **Público:** no está dirigido a menores de 18 años (compras y pagos los gestiona Juan con el cliente).

## Respuestas de «Data handling» que se pueden dar desde el código (Anthropic)

- ¿Lee o guarda datos personales? Sí: `pedir_compra` recibe contacto y dirección del cliente y los envía al servicio de Compras Perú para que Juan gestione el pedido.
- ¿Envía datos a servicios distintos de sus conectores declarados? Solo a `market.ori-song.com` (MCP y descarga del cliente) y, para Tottus, al propio sitio del comercio desde la conexión del usuario.
- ¿Cuánto tiempo conserva los datos? **No consta en este repo**; lo define el servicio. Dato pendiente de Juan.
- ¿Dirigido a menores de 18? No.

## Pendientes exactos que no están en el código (no inventar)

| Dato | Dónde va | Quién lo aporta |
|---|---|---|
| URL https de la política de privacidad | `privacyPolicyUrl` en `claude/.claude-plugin/plugin.json`; `interface.privacyPolicyURL` en `codex/.codex-plugin/plugin.json`; portal de Anthropic y de OpenAI | Juan (debe publicarla en market.ori-song.com o en el repo) |
| URL https de términos de servicio | `termsOfServiceUrl` / `interface.termsOfServiceURL` | Juan |
| URL o correo de soporte | `supportUrl` (Anthropic); `interface.supportURL` (OpenAI); «support contact» del portal de conectores | Juan |
| Correo de contacto para la revisión | Paso «Compliance» del portal de Anthropic; portal de OpenAI | Juan |
| Cuenta/clave de prueba para revisores, sin MFA | Paso «Test & launch» (conector) y revisión de OpenAI | Juan; nunca en el repo |
| Plan de pago de claude.ai y GitHub conectado | Portal claude.ai/directory/manage | Juan |
| Organización verificada en OpenAI Platform | Portal de plugins de OpenAI | Juan |
| OAuth 2.1 (o modo mixto) en `market.ori-song.com/mcp`; anotaciones `title`, `readOnlyHint`/`destructiveHint` en cada herramienta | Repositorio del servidor | Equipo del servidor |
| Contacto con un representante de OpenAI y alta en la lista permitida, si se quiere la vía «Desktop only» con MCP local | Fuera de línea | Juan |
| Capturas de pantalla (OpenAI, solo si hay UI propia; Anthropic solo para MCP Apps) | `interface.screenshots` / portal | No aplica hoy: el plugin no tiene UI |
| Periodo de retención de datos | Pregunta del portal de Anthropic | Juan |

## Qué queda fuera del alcance de los directorios

- **Gemini CLI**: la galería (geminicli.com/extensions/browse) indexa automáticamente repos públicos con el tema de GitHub `gemini-cli-extension` y `gemini-extension.json` en la raíz del repo; este repo ya cumple lo segundo. Añadir el tema es un ajuste de GitHub, no del código.
- Esta revisión no crea una web nueva ni toca el frontend.

## Fuentes oficiales consultadas (2026-10-24)

Anthropic: https://code.claude.com/docs/en/plugins-reference · https://code.claude.com/docs/en/plugins/publish · https://code.claude.com/docs/en/plugin-marketplaces · https://code.claude.com/docs/en/plugins/marketplace-reference · https://claude.com/docs/plugins/submit · https://claude.com/docs/plugins/pre-submission-checklist · https://claude.com/docs/plugins/platform-support · https://claude.com/docs/directory/publish · https://claude.com/docs/connectors/building/submission

OpenAI (por fragmentos indexados; abrir antes de enviar): https://developers.openai.com/plugins/deploy/submission · https://developers.openai.com/plugins/build/plugins · https://developers.openai.com/plugins/deploy/app-review · https://developers.openai.com/plugins/deploy/desktop-only · https://developers.openai.com/plugins/deploy/submission-errors · https://developers.openai.com/plugins/guides/submit-claude-plugin · https://developers.openai.com/codex/plugins · https://help.openai.com/en/articles/20001256-plugins-in-codex · código fuente https://github.com/openai/codex (`codex-rs/core-plugins/src/marketplace.rs`, `codex-rs/core-plugins/src/manifest.rs`, `codex-rs/codex-mcp/src/plugin_config.rs`)

Gemini CLI: https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/reference.md · https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/releasing.md
