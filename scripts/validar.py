#!/usr/bin/env python3
"""Valida el paquete de plugins de Compras Perú (Claude Code, Codex y Gemini CLI).

Solo usa la biblioteca estándar. Uso:

    python scripts/validar.py            # valida el repo donde vive este script
    python scripts/validar.py RUTA       # valida otra copia del repo

Sale con 0 si todo está bien y con 1 si hay algún error (cada uno con un
mensaje claro). Las advertencias no cambian el código de salida.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# --- Archivos que forman el paquete -------------------------------------------

MARKETPLACE_CLAUDE = ".claude-plugin/marketplace.json"
MARKETPLACE_CODEX = ".agents/plugins/marketplace.json"
PLUGIN_CLAUDE = "claude/.claude-plugin/plugin.json"
PLUGIN_CODEX = "codex/.codex-plugin/plugin.json"
GEMINI = "gemini-extension.json"
MCP_CLAUDE = "claude/.mcp.json"
MCP_CODEX = "codex/.mcp.json"
SKILLS = ("claude/skills/compras-peru/SKILL.md", "codex/skills/compras-peru/SKILL.md")
ICONOS = ("claude/.claude-plugin/icon.png", "codex/assets/icon.png")
CONTEXTO_GEMINI = "GEMINI.md"

# Manifiesto que debe existir dentro de la carpeta a la que apunta cada marketplace.
MANIFIESTO_POR_MARKETPLACE = {
    MARKETPLACE_CLAUDE: ".claude-plugin/plugin.json",
    MARKETPLACE_CODEX: ".codex-plugin/plugin.json",
}

# Únicas formas permitidas de pasar la clave al servidor MCP.
MARCADORES_CLAVE = {"${user_config.compras_token}", "${COMPRAS_PERU_TOKEN}"}

# Lo esencial que los dos SKILL.md (y GEMINI.md) deben decir igual.
REGLAS_ESENCIALES = (
    ("nunca compras ni pagas", "el agente nunca compra ni paga solo"),
    ("el operador compra, paga y coordina la entrega", "quien compra es el operador"),
    ("pedir_compra", "encargar con pedir_compra"),
    ("consentimiento explícito", "pedir_compra solo con consentimiento explícito"),
    ("aceptar_cotizacion", "aceptar la cotización solo con el sí del cliente"),
    ("solo «completado» significa compra hecha", "estado real del pedido"),
    ("nunca pidas tarjeta", "nunca pedir tarjeta ni contraseñas"),
)

WHEEL_RE = re.compile(r"compras_multicomercio-(\d+\.\d+\.\d+)-py3-none-any\.whl")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Nombres de marketplace reservados por Claude Code (docs: plugins/marketplace-reference).
NOMBRES_RESERVADOS = {
    "claude-code-marketplace", "claude-code-plugins", "claude-plugins-official", "anthropic-marketplace",
    "anthropic-plugins", "agent-skills", "anthropic-agent-skills", "knowledge-work-plugins", "claude-community",
    "claude-plugins-community", "anthropic-plugin-directory", "claude-plugin-directory", "inline", "builtin",
    "skills-dir", "synced", "npm", "github", "gh",
}
# Claves admitidas en cada opción de userConfig (Claude Code las valida en modo estricto).
USERCONFIG_CLAVES = {"type", "title", "description", "required", "default", "options", "multiple", "sensitive", "min", "max"}
USERCONFIG_TIPOS = {"string", "number", "boolean", "directory", "file"}

# --- Barrido de secretos ----------------------------------------------------------

EXTENSIONES_TEXTO = {".json", ".md", ".py", ".txt", ".toml", ".yml", ".yaml", ".sh", ".cfg", ".ini", ""}
CARPETAS_IGNORADAS = {".git", "__pycache__", ".venv", "node_modules"}

PATRONES_SECRETO = (
    ("clave privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("token de GitHub", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}")),
    ("clave tipo sk-", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_\-]{20,}")),
    ("token de Slack", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("clave de AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("clave de Google", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}")),
    ("cabecera Bearer con valor", re.compile(r"Bearer\s+[A-Za-z0-9._\-]{16,}")),
    ("correo electrónico", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    ("teléfono", re.compile(r"(?:\+|\b00)51[\s.\-]?9\d{2}[\s.\-]?\d{3}[\s.\-]?\d{3}\b|\b9\d{2}[\s.\-]\d{3}[\s.\-]\d{3}\b|\b9\d{8}\b")),
    ("dirección IP", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("asignación de secreto", re.compile(
        r"(?i)\b[\w\-]*(?:token|secret|password|passwd|api[_\-]?key|clave)[\w\-]*\b\s*[:=]\s*[\"']?"
        r"(?!\$\{)([A-Za-z0-9+/_\-]{16,})")),
)
# Cadenas largas con letras y números (posibles claves sin prefijo conocido).
CADENA_LARGA_RE = re.compile(r"(?<![A-Za-z0-9+/_\-])[A-Za-z0-9+/_\-]{32,}={0,2}(?![A-Za-z0-9+/_\-])")

CORREOS_PERMITIDOS = {"noreply@anthropic.com"}  # firma estándar de commits generados
IPS_PERMITIDAS = {"0.0.0.0", "127.0.0.1"}


def _es_cadena_aleatoria(texto: str) -> bool:
    if "/" in texto and texto.count("/") > 1:  # rutas o URLs
        return False
    tiene_digitos = sum(c.isdigit() for c in texto) >= 4
    tiene_mayus = any(c.isupper() for c in texto)
    tiene_minus = any(c.islower() for c in texto)
    return tiene_digitos and tiene_mayus and tiene_minus


def barrer_secretos(raiz: Path) -> list[str]:
    errores = []
    for ruta in sorted(raiz.rglob("*")):
        if not ruta.is_file() or any(p in CARPETAS_IGNORADAS for p in ruta.relative_to(raiz).parts):
            continue
        if ruta.suffix.lower() not in EXTENSIONES_TEXTO:
            continue
        if ruta.name in {".env"} or ruta.name.startswith(".env."):
            errores.append(f"{_rel(raiz, ruta)}: no debe haber archivos .env en el repo")
            continue
        try:
            texto = ruta.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, linea in enumerate(texto.splitlines(), 1):
            for nombre, patron in PATRONES_SECRETO:
                for m in patron.finditer(linea):
                    valor = m.group(0)
                    if nombre == "correo electrónico" and valor.lower() in CORREOS_PERMITIDOS:
                        continue
                    if nombre == "dirección IP" and valor in IPS_PERMITIDAS:
                        continue
                    errores.append(f"{_rel(raiz, ruta)}:{n}: parece un secreto ({nombre}): {_tapar(valor)}")
            for m in CADENA_LARGA_RE.finditer(linea):
                if _es_cadena_aleatoria(m.group(0)):
                    errores.append(f"{_rel(raiz, ruta)}:{n}: cadena larga que parece una clave: {_tapar(m.group(0))}")
    return errores


def _tapar(valor: str) -> str:
    """Nunca reimprime un secreto entero."""
    return valor[:4] + "…" if len(valor) > 6 else "…"


def _rel(raiz: Path, ruta: Path) -> str:
    try:
        return ruta.relative_to(raiz).as_posix()
    except ValueError:
        return str(ruta)


# --- Comprobaciones ---------------------------------------------------------------

class Validador:
    def __init__(self, raiz: Path):
        self.raiz = Path(raiz).resolve()
        self.errores: list[str] = []
        self.avisos: list[str] = []
        self.json: dict[str, object] = {}

    def error(self, msg: str) -> None:
        self.errores.append(msg)

    def aviso(self, msg: str) -> None:
        self.avisos.append(msg)

    # JSON ------------------------------------------------------------------------
    def cargar_json(self) -> None:
        obligatorios = {MARKETPLACE_CLAUDE, MARKETPLACE_CODEX, PLUGIN_CLAUDE, PLUGIN_CODEX, GEMINI, MCP_CLAUDE, MCP_CODEX}
        todos = sorted(
            p for p in self.raiz.rglob("*.json")
            if not any(x in CARPETAS_IGNORADAS for x in p.relative_to(self.raiz).parts)
        )
        vistos = set()
        for ruta in todos:
            rel = _rel(self.raiz, ruta)
            vistos.add(rel)
            try:
                self.json[rel] = json.loads(ruta.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                self.error(f"{rel}: JSON inválido ({e})")
        for rel in sorted(obligatorios - vistos):
            self.error(f"{rel}: falta el archivo")

    def obj(self, rel: str) -> dict:
        valor = self.json.get(rel)
        return valor if isinstance(valor, dict) else {}

    # Versiones -------------------------------------------------------------------
    def versiones(self) -> None:
        encontradas: dict[str, str] = {}
        for rel in (PLUGIN_CLAUDE, PLUGIN_CODEX, GEMINI):
            if rel in self.json:
                encontradas[rel] = self.obj(rel).get("version")
        mk = self.obj(MARKETPLACE_CLAUDE)
        for i, p in enumerate(mk.get("plugins") or []):
            if isinstance(p, dict) and "version" in p:
                encontradas[f"{MARKETPLACE_CLAUDE} plugins[{i}].version"] = p.get("version")
        for rel in (MCP_CLAUDE, MCP_CODEX, GEMINI):
            if rel not in self.json:
                continue
            wheels = WHEEL_RE.findall(json.dumps(self.json[rel]))
            if not wheels:
                self.error(f"{rel}: no se encontró la wheel compras_multicomercio-X.Y.Z-py3-none-any.whl")
            for w in wheels:
                encontradas[f"{rel} (wheel)"] = w
        for donde, v in encontradas.items():
            if not isinstance(v, str) or not SEMVER_RE.match(v):
                self.error(f"{donde}: versión ausente o no es X.Y.Z ({v!r})")
        distintas = {v for v in encontradas.values() if isinstance(v, str)}
        if len(distintas) > 1:
            detalle = ", ".join(f"{k}={v}" for k, v in encontradas.items())
            self.error(f"versiones distintas; deben ser iguales en todos los manifiestos y wheels: {detalle}")
        # El nombre del plugin también debe coincidir en todos lados.
        nombres = {rel: self.obj(rel).get("name") for rel in (PLUGIN_CLAUDE, PLUGIN_CODEX, GEMINI) if rel in self.json}
        if len(set(nombres.values())) > 1:
            self.error(f"el nombre del plugin no coincide: {nombres}")

    # Marketplaces ------------------------------------------------------------------
    def marketplaces(self) -> None:
        for rel, manifiesto in MANIFIESTO_POR_MARKETPLACE.items():
            mk = self.obj(rel)
            if not mk:
                continue
            nombre = mk.get("name")
            if not isinstance(nombre, str) or not KEBAB_RE.match(nombre):
                self.error(f"{rel}: 'name' debe ser kebab-case (minúsculas, números y guiones): {nombre!r}")
            elif nombre in NOMBRES_RESERVADOS or nombre.startswith("claudeai-") or (
                    re.search(r"anthropic|claude", nombre) and re.search(r"official|oficial", nombre)):
                self.error(f"{rel}: 'name' {nombre!r} está reservado o imita un marketplace oficial")
            plugins = mk.get("plugins")
            if not isinstance(plugins, list) or not plugins:
                self.error(f"{rel}: 'plugins' debe ser una lista no vacía")
                continue
            for i, p in enumerate(plugins):
                if not isinstance(p, dict):
                    self.error(f"{rel}: plugins[{i}] no es un objeto")
                    continue
                pnombre = p.get("name")
                if not isinstance(pnombre, str) or not KEBAB_RE.match(pnombre):
                    self.error(f"{rel}: plugins[{i}].name debe ser kebab-case: {pnombre!r}")
                fuente = p.get("source")
                if isinstance(fuente, dict):  # forma Codex: {"source": "local", "path": "./codex"}
                    if fuente.get("source") != "local":
                        self.aviso(f"{rel}: plugins[{i}].source.source={fuente.get('source')!r}; solo se valida 'local'")
                        continue
                    ruta = fuente.get("path")
                else:
                    ruta = fuente
                if not isinstance(ruta, str) or not ruta.startswith("./"):
                    self.error(f"{rel}: plugins[{i}] la ruta del plugin debe empezar por './' (es {ruta!r})")
                    continue
                carpeta = (self.raiz / ruta).resolve()
                if not carpeta.is_dir():
                    self.error(f"{rel}: plugins[{i}] apunta a {ruta!r}, que no es una carpeta existente")
                    continue
                if self.raiz not in carpeta.parents and carpeta != self.raiz:
                    self.error(f"{rel}: plugins[{i}] apunta fuera del repo: {ruta!r}")
                    continue
                if not (carpeta / manifiesto).is_file():
                    self.error(f"{rel}: plugins[{i}] apunta a {ruta!r}, pero falta {ruta.rstrip('/')}/{manifiesto}")
                    continue
                destino = self.obj(_rel(self.raiz, carpeta / manifiesto))
                if destino and destino.get("name") != pnombre:
                    self.error(f"{rel}: plugins[{i}].name={pnombre!r} no coincide con el manifiesto ({destino.get('name')!r})")
        # Claude: owner.name obligatorio.
        owner = self.obj(MARKETPLACE_CLAUDE).get("owner")
        if MARKETPLACE_CLAUDE in self.json and not (isinstance(owner, dict) and owner.get("name")):
            self.error(f"{MARKETPLACE_CLAUDE}: falta owner.name")
        # Codex: policy con valores conocidos.
        for i, p in enumerate(self.obj(MARKETPLACE_CODEX).get("plugins") or []):
            pol = p.get("policy") if isinstance(p, dict) else None
            if not isinstance(pol, dict):
                self.error(f"{MARKETPLACE_CODEX}: plugins[{i}] sin 'policy'")
                continue
            if pol.get("installation") not in {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}:
                self.error(f"{MARKETPLACE_CODEX}: plugins[{i}].policy.installation desconocido: {pol.get('installation')!r}")
            if pol.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
                self.error(f"{MARKETPLACE_CODEX}: plugins[{i}].policy.authentication desconocido: {pol.get('authentication')!r}")

    # Archivos referenciados --------------------------------------------------------
    def archivos(self) -> None:
        for rel in ICONOS:
            ruta = self.raiz / rel
            if not ruta.is_file():
                self.error(f"{rel}: falta el icono")
            elif ruta.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
                self.error(f"{rel}: el icono no es un PNG válido")
        codex = self.obj(PLUGIN_CODEX)
        base = self.raiz / "codex"
        refs = {
            "logo": (codex.get("interface") or {}).get("logo"),
            "skills": codex.get("skills"),
            "mcpServers": codex.get("mcpServers"),
        }
        if PLUGIN_CODEX in self.json:
            for campo, ruta in refs.items():
                if not isinstance(ruta, str):
                    self.error(f"{PLUGIN_CODEX}: falta '{campo}' o no es una ruta")
                    continue
                if not ruta.startswith("./"):
                    self.error(f"{PLUGIN_CODEX}: '{campo}' debe ser relativa y empezar por './' ({ruta!r})")
                destino = base / ruta
                if campo == "skills":
                    if not destino.is_dir() or not list(destino.glob("*/SKILL.md")):
                        self.error(f"{PLUGIN_CODEX}: 'skills' ({ruta!r}) no contiene ninguna carpeta con SKILL.md")
                elif not destino.is_file():
                    self.error(f"{PLUGIN_CODEX}: '{campo}' ({ruta!r}) no existe")
            prompts = (codex.get("interface") or {}).get("defaultPrompt") or []
            if len(prompts) > 3:
                self.aviso(f"{PLUGIN_CODEX}: defaultPrompt tiene {len(prompts)} frases; Codex muestra como mucho 3")
            for i, frase in enumerate(prompts):
                if not isinstance(frase, str) or not frase or len(frase) > 128:
                    self.error(f"{PLUGIN_CODEX}: defaultPrompt[{i}] debe ser texto de 1 a 128 caracteres")
        icono = self.obj(PLUGIN_CLAUDE).get("icon")
        if icono is not None and not (isinstance(icono, str) and icono.startswith("./")
                                      and (self.raiz / "claude" / icono).is_file()):
            self.error(f"{PLUGIN_CLAUDE}: 'icon' ({icono!r}) debe ser una ruta './…' a un archivo del plugin")
        gem = self.obj(GEMINI)
        ctx = gem.get("contextFileName")
        if GEMINI in self.json and (not isinstance(ctx, str) or not (self.raiz / ctx).is_file()):
            self.error(f"{GEMINI}: contextFileName={ctx!r} no existe")

    # Skills ------------------------------------------------------------------------
    @staticmethod
    def frontmatter(texto: str) -> tuple[dict[str, str] | None, str]:
        if not texto.startswith("---\n"):
            return None, texto
        fin = texto.find("\n---", 4)
        if fin < 0:
            return None, texto
        campos: dict[str, str] = {}
        for linea in texto[4:fin].splitlines():
            if ":" in linea and not linea.startswith((" ", "\t", "#")):
                k, v = linea.split(":", 1)
                campos[k.strip()] = v.strip().strip("\"'")
        return campos, texto[fin + 4:]

    def skills(self) -> None:
        cuerpos = {}
        for rel in SKILLS:
            ruta = self.raiz / rel
            if not ruta.is_file():
                self.error(f"{rel}: falta el archivo")
                continue
            campos, cuerpo = self.frontmatter(ruta.read_text(encoding="utf-8"))
            if campos is None:
                self.error(f"{rel}: falta el frontmatter (bloque --- al inicio)")
                continue
            for k in ("name", "description"):
                if not campos.get(k):
                    self.error(f"{rel}: el frontmatter necesita '{k}' no vacío")
            nombre = campos.get("name", "")
            if nombre and nombre != ruta.parent.name:
                self.error(f"{rel}: name={nombre!r} debe coincidir con la carpeta {ruta.parent.name!r}")
            if len(campos.get("description", "")) > 1024:
                self.error(f"{rel}: 'description' supera 1024 caracteres")
            cuerpos[rel] = cuerpo
        ctx = self.raiz / CONTEXTO_GEMINI
        if ctx.is_file():
            cuerpos[CONTEXTO_GEMINI] = ctx.read_text(encoding="utf-8")
        for rel, cuerpo in cuerpos.items():
            plano = " ".join(cuerpo.replace("*", "").split()).lower()
            for frase, regla in REGLAS_ESENCIALES:
                if frase not in plano:
                    self.error(f"{rel}: falta la regla esencial «{regla}» (frase esperada: «{frase}»)")
        skills = [cuerpos[r].strip() for r in SKILLS if r in cuerpos]
        if len(skills) == 2 and skills[0] != skills[1]:
            self.aviso("los dos SKILL.md tienen instrucciones distintas; revisa que digan lo mismo")

    # Clave -------------------------------------------------------------------------
    def clave(self) -> None:
        for rel in (MCP_CLAUDE, MCP_CODEX, GEMINI):
            servidores = self.obj(rel).get("mcpServers") or {}
            for nombre, srv in servidores.items():
                env = (srv or {}).get("env") or {}
                for k, v in env.items():
                    if re.search(r"(?i)token|secret|key|clave|password", k) and v not in MARCADORES_CLAVE:
                        self.error(f"{rel}: mcpServers.{nombre}.env.{k} debe ser un marcador "
                                   f"({' o '.join(sorted(MARCADORES_CLAVE))}), no un valor")
        uc = self.obj(PLUGIN_CLAUDE).get("userConfig") or {}
        for clave, op in uc.items():
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", clave):
                self.error(f"{PLUGIN_CLAUDE}: userConfig.{clave}: el nombre solo admite letras, dígitos y '_'")
            if not isinstance(op, dict):
                continue
            sobran = set(op) - USERCONFIG_CLAVES
            if sobran:
                self.error(f"{PLUGIN_CLAUDE}: userConfig.{clave} tiene claves no admitidas: {sorted(sobran)}")
            if op.get("type") not in USERCONFIG_TIPOS:
                self.error(f"{PLUGIN_CLAUDE}: userConfig.{clave}.type debe ser uno de {sorted(USERCONFIG_TIPOS)}")
            for k in ("title", "description"):
                if not op.get(k):
                    self.error(f"{PLUGIN_CLAUDE}: userConfig.{clave}.{k} es obligatorio")
        usados = set(re.findall(r"\$\{user_config\.([A-Za-z0-9_]+)\}", json.dumps(self.json.get(MCP_CLAUDE, {}))))
        for clave in sorted(usados - set(uc)):
            self.error(f"{MCP_CLAUDE}: usa ${{user_config.{clave}}}, que no está declarado en userConfig")
        opt = uc.get("compras_token")
        if PLUGIN_CLAUDE in self.json:
            if not isinstance(opt, dict):
                self.error(f"{PLUGIN_CLAUDE}: falta userConfig.compras_token")
            elif opt.get("sensitive") is not True:
                self.error(f"{PLUGIN_CLAUDE}: userConfig.compras_token debe tener sensitive: true")
            elif "default" in opt:
                self.error(f"{PLUGIN_CLAUDE}: userConfig.compras_token no debe tener valor por defecto")
        for s in self.obj(GEMINI).get("settings") or []:
            if isinstance(s, dict) and s.get("envVar") == "COMPRAS_PERU_TOKEN" and s.get("sensitive") is not True:
                self.error(f"{GEMINI}: el ajuste COMPRAS_PERU_TOKEN debe tener sensitive: true")

    def ejecutar(self) -> bool:
        self.cargar_json()
        self.versiones()
        self.marketplaces()
        self.archivos()
        self.skills()
        self.clave()
        self.errores.extend(barrer_secretos(self.raiz))
        return not self.errores


def validar(raiz: Path | str) -> Validador:
    v = Validador(Path(raiz))
    v.ejecutar()
    return v


def main(argv: list[str]) -> int:
    raiz = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    v = validar(raiz)
    for a in v.avisos:
        print(f"AVISO: {a}")
    if v.errores:
        for e in v.errores:
            print(f"ERROR: {e}")
        print(f"\n✗ {len(v.errores)} error(es) en {v.raiz.name}. Corrígelos antes de publicar.")
        return 1
    version = v.obj(PLUGIN_CLAUDE).get("version")
    print(f"✓ Compras Perú {version}: manifiestos, rutas, iconos, skills y barrido de secretos en orden.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
