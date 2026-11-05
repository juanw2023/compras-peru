"""Pruebas de scripts/validar.py con unittest (sin dependencias).

    python -m unittest discover -s tests

Los casos rojos trabajan sobre copias temporales del repo; el repo real no se toca.
Los «secretos» de prueba se arman por partes para que este archivo no los contenga
literalmente (y el barrido del repo real siga en verde).
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import validar  # noqa: E402


def _cadena_falsa(n=36):
    """Cadena tipo clave (mayúsculas, minúsculas y dígitos) generada en tiempo de ejecución."""
    import string
    alfabeto = string.ascii_uppercase[:10] + string.ascii_lowercase[:10] + string.digits
    return "".join(alfabeto[(i * 7) % len(alfabeto)] for i in range(n))


def _ignorar(_dir, nombres):
    return [n for n in nombres if n in {".git", "__pycache__"}]


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.copia = Path(self._tmp.name) / "repo"
        shutil.copytree(RAIZ, self.copia, ignore=_ignorar)

    def tearDown(self):
        self._tmp.cleanup()

    def leer(self, rel):
        return json.loads((self.copia / rel).read_text(encoding="utf-8"))

    def escribir(self, rel, datos):
        (self.copia / rel).write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")

    def errores(self):
        return validar.validar(self.copia).errores

    def assertFalla(self, fragmento):
        errores = self.errores()
        self.assertTrue(errores, "se esperaba al menos un error")
        self.assertTrue(any(fragmento in e for e in errores), f"ningún error contiene {fragmento!r}: {errores}")


class Verde(unittest.TestCase):
    def test_repo_actual_valida(self):
        v = validar.validar(RAIZ)
        self.assertEqual(v.errores, [])

    def test_cli_sale_con_cero(self):
        r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "validar.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("✓", r.stdout)


class Rojos(Base):
    def test_json_roto(self):
        (self.copia / validar.PLUGIN_CODEX).write_text("{ roto", encoding="utf-8")
        self.assertFalla("JSON inválido")

    def test_version_distinta_en_manifiesto(self):
        d = self.leer(validar.PLUGIN_CODEX)
        d["version"] = "9.9.9"
        self.escribir(validar.PLUGIN_CODEX, d)
        self.assertFalla("versiones distintas")

    def test_version_distinta_en_wheel(self):
        ruta = self.copia / validar.MCP_CLAUDE
        texto = ruta.read_text(encoding="utf-8")
        version = self.leer(validar.PLUGIN_CLAUDE)["version"]
        ruta.write_text(texto.replace(f"-{version}-", "-0.0.1-"), encoding="utf-8")
        self.assertFalla("versiones distintas")

    def test_version_distinta_en_marketplace(self):
        d = self.leer(validar.MARKETPLACE_CLAUDE)
        d["plugins"][0]["version"] = "0.4.4"
        self.escribir(validar.MARKETPLACE_CLAUDE, d)
        self.assertFalla("versiones distintas")

    def test_ruta_rota_claude(self):
        d = self.leer(validar.MARKETPLACE_CLAUDE)
        d["plugins"][0]["source"] = "./no-existe"
        self.escribir(validar.MARKETPLACE_CLAUDE, d)
        self.assertFalla("no es una carpeta existente")

    def test_ruta_rota_codex(self):
        d = self.leer(validar.MARKETPLACE_CODEX)
        d["plugins"][0]["source"]["path"] = "./claude"  # existe, pero sin .codex-plugin/plugin.json
        self.escribir(validar.MARKETPLACE_CODEX, d)
        self.assertFalla("falta ./claude/.codex-plugin/plugin.json")

    def test_ruta_sin_punto_barra(self):
        d = self.leer(validar.MARKETPLACE_CLAUDE)
        d["plugins"][0]["source"] = "claude"
        self.escribir(validar.MARKETPLACE_CLAUDE, d)
        self.assertFalla("debe empezar por './'")

    def test_logo_codex_inexistente(self):
        (self.copia / "codex/assets/icon.png").unlink()
        self.assertFalla("'logo'")

    def test_icono_claude_inexistente(self):
        (self.copia / "claude/.claude-plugin/icon.png").unlink()
        self.assertFalla("falta el icono")

    def test_policy_desconocida(self):
        d = self.leer(validar.MARKETPLACE_CODEX)
        d["plugins"][0]["policy"]["authentication"] = "SIEMPRE"
        self.escribir(validar.MARKETPLACE_CODEX, d)
        self.assertFalla("policy.authentication")

    def test_skill_sin_descripcion(self):
        ruta = self.copia / validar.SKILLS[1]
        lineas = ruta.read_text(encoding="utf-8").splitlines()
        lineas = ["description:" if l.startswith("description:") else l for l in lineas]
        ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        self.assertFalla("'description' no vacío")

    def test_skill_sin_frontmatter(self):
        ruta = self.copia / validar.SKILLS[0]
        _, cuerpo = validar.Validador.frontmatter(ruta.read_text(encoding="utf-8"))
        ruta.write_text(cuerpo, encoding="utf-8")
        self.assertFalla("falta el frontmatter")

    def test_skill_pierde_la_regla_de_no_comprar(self):
        ruta = self.copia / validar.SKILLS[1]
        texto = ruta.read_text(encoding="utf-8").replace("nunca compras ni pagas", "puedes comprar")
        ruta.write_text(texto, encoding="utf-8")
        self.assertFalla("nunca compra ni paga solo")

    def test_token_literal_en_mcp(self):
        d = self.leer(validar.MCP_CLAUDE)
        d["mcpServers"]["compras-peru"]["env"]["COMPRAS_PERU_TOKEN"] = "valor" + "-de-prueba"
        self.escribir(validar.MCP_CLAUDE, d)
        self.assertFalla("debe ser un marcador")

    def test_secreto_plantado_github(self):
        falso = "gh" + "p_" + _cadena_falsa(36)
        (self.copia / "notas.md").write_text(f"token: {falso}\n", encoding="utf-8")
        self.assertFalla("parece un secreto")

    def test_secreto_plantado_cadena_larga(self):
        falso = _cadena_falsa(40)
        (self.copia / "claude" / "README.md").write_text(f"usa {falso}\n", encoding="utf-8")
        self.assertFalla("parece una clave")

    def test_correo_personal(self):
        correo = "alguien" + "@" + "ejemplo.com"
        (self.copia / "README.md").write_text(f"Escribe a {correo}\n", encoding="utf-8")
        self.assertFalla("correo electrónico")

    def test_telefono(self):
        (self.copia / "GEMINI.md").write_text("Llama al +51 9" + "87 654 321\n", encoding="utf-8")
        self.assertFalla("teléfono")

    def test_ip(self):
        (self.copia / "codex" / "README.md").write_text("Servidor en 10.2." + "3.4\n", encoding="utf-8")
        self.assertFalla("dirección IP")

    def test_nombre_reservado(self):
        d = self.leer(validar.MARKETPLACE_CLAUDE)
        d["name"] = "claude-plugins-official"
        self.escribir(validar.MARKETPLACE_CLAUDE, d)
        self.assertFalla("reservado")

    def test_userconfig_clave_desconocida(self):
        d = self.leer(validar.PLUGIN_CLAUDE)
        d["userConfig"]["compras_token"]["secreto"] = True
        self.escribir(validar.PLUGIN_CLAUDE, d)
        self.assertFalla("claves no admitidas")

    def test_userconfig_no_declarado(self):
        d = self.leer(validar.MCP_CLAUDE)
        d["mcpServers"]["compras-peru"]["env"]["OTRA"] = "${user_config.otra}"
        self.escribir(validar.MCP_CLAUDE, d)
        self.assertFalla("no está declarado")

    def test_default_prompt_largo(self):
        d = self.leer(validar.PLUGIN_CODEX)
        d["interface"]["defaultPrompt"][0] = "compara " * 20
        self.escribir(validar.PLUGIN_CODEX, d)
        self.assertFalla("defaultPrompt[0]")

    def test_cli_sale_con_uno(self):
        d = self.leer(validar.GEMINI)
        d["version"] = "1.0.0"
        self.escribir(validar.GEMINI, d)
        r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "validar.py"), str(self.copia)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("ERROR:", r.stdout)


if __name__ == "__main__":
    unittest.main()
