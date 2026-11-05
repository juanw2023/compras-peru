# Compras Perú

Tu asistente de IA hace la compra del súper contigo: busca en **Tottus, Wong y Metro**, te enseña la foto y la ficha de cada producto, compara precios, arma el carrito y se lo encarga al **operador**, una persona que compra, paga y coordina la entrega por ti.

**El asistente nunca compra ni paga solo.** Solo encarga el pedido cuando tú dices que sí, y solo se paga cuando aceptas el total exacto que te cotiza el operador.

Funciona con **Claude Code**, **Codex** y **Gemini CLI**.

## Cuánto cuesta

- **S/ 4 por 30 días** de suscripción.
- Por cada pedido que el operador gestiona, una tarifa de **S/ 5 o el 5 % de la compra, lo que sea mayor**. Siempre la ves desglosada antes de aceptar.
- Instalar el plugin es gratis y no compra nada.

## Antes de empezar

1. **Consigue tu clave** en https://market.ori-song.com: activas la suscripción, pagas con Yape y la clave aparece al confirmarse el pago.
2. **Instala uv**, el programa que pone en marcha el plugin. Pega esto en la terminal (Mac o Linux):

   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   En Windows y otros casos: https://docs.astral.sh/uv/

## Instalar

### Claude Code

Dentro de Claude Code escribe, uno por uno:

```
/plugin marketplace add juanw2023/compras-peru
/plugin install compras-peru@compras-peru-market
```

Te pedirá la clave y la guardará de forma segura. (Desde la terminal también vale: `claude plugin marketplace add juanw2023/compras-peru` y luego `claude plugin install compras-peru@compras-peru-market`.)

### Codex

En la terminal:

```sh
codex plugin marketplace add juanw2023/compras-peru
```

Después abre Codex, escribe `/plugins` y activa **Compras Perú** (por verificar: el nombre exacto del comando de instalación puede variar según tu versión de Codex).

Codex no pide la clave al instalar: guárdala en un archivo con este comando (te la pide sin mostrarla en pantalla):

```sh
mkdir -p ~/.config/compras-peru && (umask 077; read -rs CLAVE && printf %s "$CLAVE" > ~/.config/compras-peru/clave)
```

o, si lo prefieres, ponla en la variable de entorno `COMPRAS_PERU_TOKEN`.

### Gemini CLI

En la terminal:

```sh
gemini extensions install https://github.com/juanw2023/compras-peru
```

Te pedirá la clave y la guardará de forma segura.

## Cómo comprobar que funciona

Abre tu asistente y pídele:

> compara leche Gloria en Tottus, Wong y Metro

Debe responder con los productos de cada cadena, su precio y su foto. Si dice que la clave no es válida, revisa que la copiaste completa y que tu suscripción está activa en https://market.ori-song.com.

## Cómo se hace un pedido

1. Pide lo que necesitas: «2 leches Gloria azul y 1 kg de arroz Costeño, lo más barato».
2. El asistente compara, te muestra foto y ficha y arma el carrito. Tú confirmas.
3. Con tu sí, encarga el pedido. El operador lo recibe y te cotiza: compra + tarifa = total.
4. Si aceptas ese total, el operador compra y coordina la entrega. El pedido termina como «completado».

## Qué NO hace

- **No compra ni paga por su cuenta.** Siempre decide una persona: tú das el sí y el operador hace la compra.
- No te pide tarjetas, contraseñas de supermercados ni datos bancarios.
- No necesita que tengas cuenta en ningún supermercado.
- No salta bloqueos ni CAPTCHA de las tiendas: si una tienda no responde, te lo dice y se detiene.

## Privacidad

Al servicio solo llegan tu clave, las búsquedas en Wong y Metro, tu carrito y, si encargas un pedido, el contacto y la dirección de entrega que tú indiques. Las búsquedas en Tottus salen desde tu propia conexión. Borrador de la política: [docs/privacidad.md](docs/privacidad.md).

---

Para quien mantiene el repo: `python scripts/validar.py` comprueba el paquete y `python -m unittest discover -s tests` ejecuta las pruebas. Cómo enviarlo a los directorios oficiales: [docs/PUBLICAR.md](docs/PUBLICAR.md). Historial: [CHANGELOG.md](CHANGELOG.md). Licencia MIT.
