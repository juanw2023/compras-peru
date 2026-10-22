# Compras Perú para Codex

Tu agente busca en **Tottus, Wong y Metro**, ve la foto y la ficha exactas de cada producto, compara precios, arma el carrito y encarga la compra. **Juan compra, paga y coordina la entrega por ti**; el agente nunca compra ni paga solo. Suscripción: S/ 4 por 30 días en https://market.ori-song.com (Yape; la clave aparece al confirmar el pago). Requiere [uv](https://docs.astral.sh/uv/) instalado.

```sh
codex plugin marketplace add juanw2023/compras-peru
codex plugin add compras-peru@compras-peru-market
# la clave: en el archivo (recomendado) o en COMPRAS_PERU_TOKEN del entorno
mkdir -p ~/.config/compras-peru && (umask 077; read -rs CLAVE && printf %s "$CLAVE" > ~/.config/compras-peru/clave)
```

Tottus se lee desde tu propia conexión; Wong, Metro, carritos y pedidos pasan por el servicio con tu clave. Más información: https://github.com/juanw2023/compras-peru
