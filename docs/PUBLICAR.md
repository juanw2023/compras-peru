# Publicar Compras Perú en los directorios oficiales

Lista de comprobación, en orden. Todo lo que exige cuenta (claude.ai, GitHub, OpenAI) lo hace el dueño del repo o un agente con su navegador; nada de esto se ejecuta desde CI.

Estado al preparar esta lista (2026-11-05): el repo ya se instala **directamente desde GitHub** en los tres agentes (ver README). Los directorios oficiales son un paso extra para que aparezca en sus catálogos.

## 0. Antes de nada (una vez)

- [ ] Fusionar este PR en `main`.
- [ ] Comprobar en local:
  ```sh
  python scripts/validar.py                    # debe terminar con ✓
  python -m unittest discover -s tests         # debe decir OK
  claude plugin validate . --strict            # marketplace de Claude
  claude plugin validate ./claude --strict     # plugin de Claude
  ```
- [ ] Probar la instalación desde GitHub en una máquina limpia (README → «Instalar») y pedir «compara leche Gloria en Tottus, Wong y Metro».
- [ ] **Publicar la página de privacidad** en `https://market.ori-song.com/privacidad` a partir de [privacidad.md](privacidad.md): completar los plazos de conservación y un contacto de soporte **no personal** (p. ej. un formulario o un correo genérico del servicio). Los directorios la piden.
- [ ] (Recomendado) Página de condiciones de uso en `https://market.ori-song.com/condiciones`.
- [ ] Cuando existan esas páginas, añadir sus URL a los manifiestos (cambio pequeño, mismo número de versión o con la siguiente versión del producto):
  - `claude/.claude-plugin/plugin.json`: `"privacyPolicyUrl": "https://market.ori-song.com/privacidad"` y, si hay, `"termsOfServiceUrl"`, `"supportUrl"`.
  - `codex/.codex-plugin/plugin.json`, dentro de `interface`: `"privacyPolicyURL"` y `"termsOfServiceURL"`.
- [ ] Crear una etiqueta y release en GitHub de la versión actual (`v0.4.5`). Gemini la necesita para su galería y sirve de referencia para las demás.

## 1. Directorio de plugins de Claude (Anthropic)

Fuente: https://claude.com/docs/plugins/submit y https://code.claude.com/docs/en/plugins/publish (consultadas el 2026-11-05).

Requisitos: plan de pago de claude.ai, GitHub conectado en claude.ai con permiso de *push* sobre `juanw2023/compras-peru`, repo público (ya lo es). Límite: 10 envíos por organización cada 24 h. El catálogo `claude-plugins-official` **no** se pide por este portal (va por contacto de socio con Anthropic).

1. [ ] Ir a https://claude.ai/directory/manage → **Submit new** → **Plugin bundle**.
2. [ ] **Source**
   - Repository: `juanw2023/compras-peru`
   - Plugin path: `claude`
   - Branch/tag: `main` (o `v0.4.5` si se creó la etiqueta)
   - Pulsar **Validate** (debe pasar; es lo mismo que `claude plugin validate ./claude`).
3. [ ] **Listing details** (se leen de `plugin.json` y del README; revisar que salgan así):
   - Nombre: `Compras Perú` (identificador `compras-peru`)
   - Descripción corta: `Supermercados de Perú: busca, compara y encarga la compra al operador.`
   - Descripción larga: `Busca en Tottus, Wong y Metro con la foto y la ficha exactas, compara precios, arma el carrito y encarga la compra al operador, que compra, paga y coordina la entrega. El agente nunca compra ni paga solo. Suscripción S/ 4 por 30 días en market.ori-song.com; cada pedido gestionado suma una tarifa de S/ 5 o el 5 % (lo que sea mayor), desglosada antes de aceptar.`
   - Categoría: `Productivity` (productividad)
   - Sitio web: `https://market.ori-song.com`
   - Repositorio: `https://github.com/juanw2023/compras-peru`
   - Icono: `claude/.claude-plugin/icon.png` (PNG 1080×1080, declarado en `plugin.json` como `icon`)
   - Política de privacidad: `https://market.ori-song.com/privacidad` (**falta publicarla**, paso 0)
4. [ ] **Data handling** (respuestas sugeridas, coherentes con [privacidad.md](privacidad.md)):
   - ¿Trata datos personales? **Sí, mínimos**: clave de suscripción; búsquedas y carrito; y, solo al encargar un pedido, nombre de contacto, medio de contacto y dirección de entrega que da el cliente.
   - ¿Envía datos a terceros? **Solo al servicio propio** (`market.ori-song.com`); el supermercado recibe lo necesario para la compra que hace el operador. Las búsquedas en Tottus salen desde el equipo del usuario.
   - Conservación: los plazos que se fijen en la página de privacidad.
   - ¿Uso por menores de 18? **No está dirigido a menores** (requiere suscripción de pago).
5. [ ] **Compliance**: correo de contacto **del servicio** (no uno personal) y aceptar las cuatro declaraciones.
6. [ ] **Review and submit**: elegir **GitHub push webhook** (cada push a `main` dispara la revisión de la nueva versión) o comprobación programada. Enviar.
7. [ ] Al aprobarse, añadir al README el enlace a la ficha del directorio.

## 2. Directorio de plugins de Codex (OpenAI)

Fuentes: especificación en el repo oficial `openai/skills` (`skills/.system/plugin-creator/references/plugin-json-spec.md`) y resultados de búsqueda de https://developers.openai.com/plugins/deploy/submission. **Esa página no se pudo abrir desde la sesión en la nube** (red bloqueada): los pasos de esta sección son **por verificar**.

1. [ ] Abrir https://developers.openai.com/plugins/deploy/submission con la cuenta de OpenAI y confirmar si el envío al directorio público ya está abierto (a mediados de 2026 se anunciaba como «próximamente»).
2. [ ] Requisito conocido: los plugins con *hooks* de ciclo de vida no entran en el directorio público. **Compras Perú no usa hooks** (solo un servidor MCP y una skill), así que cumple.
3. [ ] Datos ya preparados en `codex/.codex-plugin/plugin.json` → `interface`:
   - displayName: `Compras Perú`
   - shortDescription: `Supermercados de Perú: busca, compara y encarga al operador`
   - longDescription: la de arriba (sección 1).
   - developerName: `Compras Perú` · category: `Productivity` · websiteURL: `https://market.ori-song.com`
   - logo: `./assets/icon.png` · defaultPrompt: 2 frases (máximo 3, de hasta 128 caracteres)
   - Falta: `privacyPolicyURL` (y opcional `termsOfServiceURL`, `screenshots`, `brandColor`) cuando exista la página.
4. [ ] Mientras no haya directorio público, la vía oficial ya funciona: `codex plugin marketplace add juanw2023/compras-peru`.

## 3. Galería de extensiones de Gemini CLI

Fuente: `google-gemini/gemini-cli` → `docs/extensions/releasing.md` (consultada el 2026-11-05). No hay formulario: la galería se llena sola.

1. [ ] En GitHub → repo → **About** (rueda dentada) → *Topics*: añadir `gemini-cli-extension`.
2. [ ] Confirmar que `gemini-extension.json` está en la raíz (ya lo está).
3. [ ] Crear la release `v0.4.5` (paso 0).
4. [ ] Esperar al rastreo diario (depende de que la búsqueda de código de GitHub haya indexado el manifiesto) y comprobar que aparece en la galería.

## 4. Después de cada versión nueva

1. Subir la versión en los 4 manifiestos y en el nombre de la wheel de los 3 archivos que la usan (el validador falla si queda alguna distinta).
2. `python scripts/validar.py` y las pruebas en verde.
3. Añadir la entrada en `CHANGELOG.md`, etiquetar `vX.Y.Z` y crear la release.
4. El directorio de Claude revisa la versión nueva solo si se eligió el webhook; si no, reenviar desde el portal.
