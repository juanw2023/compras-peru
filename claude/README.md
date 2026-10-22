# Compras Perú para Claude Code

Tu agente busca en **Tottus, Wong y Metro**, ve la foto y la ficha exactas de cada producto, compara precios, arma el carrito y encarga la compra. **Juan compra, paga y coordina la entrega por ti**; el agente nunca compra ni paga solo. Suscripción: S/ 4 por 30 días en https://market.ori-song.com (Yape; la clave aparece al confirmar el pago), más una tarifa por pedido gestionado de S/ 5 o el 5 % de la compra, lo que sea mayor. Requiere [uv](https://docs.astral.sh/uv/) instalado.

```sh
claude plugin marketplace add juanw2023/compras-peru
claude plugin install compras-peru@compras-peru-market   # pide tu clave y la guarda en el llavero
```

Tottus se lee desde tu propia conexión; Wong, Metro, carritos y pedidos pasan por el servicio con tu clave. Más información: https://github.com/juanw2023/compras-peru
