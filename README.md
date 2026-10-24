# Compras Perú — plugins para agentes

Tu agente de IA (Claude Code, Codex o Gemini CLI) busca en **Tottus, Wong y Metro**, te muestra la foto y la ficha exactas de cada producto, compara precios entre cadenas, arma el carrito y encarga la compra. **Juan compra, paga y coordina la entrega por ti**: el agente nunca compra ni paga solo, y tú no necesitas cuenta en ningún supermercado.

- Suscripción: **S/ 4 por 30 días** en https://market.ori-song.com (pagas con Yape; la clave aparece al confirmar el pago).
- Por cada pedido que Juan gestiona: tarifa de servicio de **S/ 5 o el 5 % de la compra, lo que sea mayor**, desglosada en la cotización.
- Requiere [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

## Instalar

| Agente | Comandos |
|---|---|
| Claude Code | `claude plugin marketplace add juanw2023/compras-peru` y `claude plugin install compras-peru@compras-peru-market` (te pide la clave y la guarda en el llavero) |
| Codex | `codex plugin marketplace add juanw2023/compras-peru` y `codex plugin add compras-peru@compras-peru-market`; la clave va en `~/.config/compras-peru/clave` o en `COMPRAS_PERU_TOKEN` |
| Gemini CLI | `gemini extensions install https://github.com/juanw2023/compras-peru` (te pide la clave como ajuste sensible) |

Guardar la clave en el archivo, sin que quede en el historial:

```sh
mkdir -p ~/.config/compras-peru && (umask 077; read -rs CLAVE && printf %s "$CLAVE" > ~/.config/compras-peru/clave)
```

## Cómo funciona

1. Pídele a tu agente lo que necesitas («2 leches Gloria azul y 1 kg de arroz Costeño, lo más barato»).
2. El agente compara, te enseña la foto y la ficha y arma el carrito; tú confirmas.
3. Con tu sí, el agente encarga el pedido: Juan lo recibe al instante, lo cotiza (compra + tarifa de servicio) y tú aceptas el total exacto.
4. Juan compra y coordina la entrega; el pedido pasa a «completado».

Tottus se lee desde tu propia conexión; Wong, Metro, carritos y pedidos pasan por el servicio con tu clave. Instalar no crea cuentas, no cobra y no compra nada.

Qué ejecuta y a dónde se conecta: al iniciar, `uvx` descarga el cliente `compras_multicomercio` 0.4.5 (wheel publicado en https://market.ori-song.com/static/descargas/) y lo ejecuta en tu equipo; ese cliente lee Tottus desde tu propia conexión y envía las búsquedas de Wong y Metro, los carritos y los pedidos a https://market.ori-song.com/mcp con tu clave como Bearer. El servidor MCP y el cliente no viven en este repositorio: aquí solo está el empaquetado para cada agente.
