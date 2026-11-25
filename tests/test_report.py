import base64
import csv
import json
import re
import unittest
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from tools.build_powerbi import NAME, ROOT, TABLES, build


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class ReleaseTest(unittest.TestCase):
    def test_public_data_allowlist(self):
        self.assertEqual({p.name for p in (ROOT / "data").glob("*.csv")},
                         {"benchmark.csv", "escopo.csv", "indicadores.csv", "prioridades.csv"})
        for path in (ROOT / "data").glob("*.csv"):
            with path.open(encoding="utf-8", newline="") as source:
                rows = list(csv.DictReader(source))
            self.assertTrue(rows)
            self.assertNotIn(None, rows[0])
            self.assertFalse({"comentario", "usuario", "email", "resposta"} & set(rows[0]))

    def test_model_matches_public_inputs_and_report_references(self):
        base = ROOT / "powerbi"
        project = read_json(base / f"{NAME}.pbip")
        report = base / project["artifacts"][0]["report"]["path"]
        model_path = report / read_json(report / "definition.pbir")["datasetReference"]["byPath"]["path"]
        model = read_json(model_path / "model.bim")["model"]
        self.assertEqual({t["name"] for t in model["tables"]}, set(TABLES))
        bindings = {}
        for table in model["tables"]:
            name = table["name"]
            bindings[name] = {c["name"] for c in table["columns"]}
            m = "\n".join(table["partitions"][0]["source"]["expression"])
            token = re.search(r'Binary.FromText\("([^"]+)"', m)[1]
            self.assertEqual(base64.b64decode(token),
                             (ROOT / "data" / f"{TABLES[name][0]}.csv").read_bytes().replace(b"\r\n", b"\n"))
        pages = report / "definition" / "pages"
        page_order = read_json(pages / "pages.json")["pageOrder"]
        self.assertEqual([read_json(pages / p / "page.json")["displayName"] for p in page_order],
                         ["Proposta", "Benchmark", "Plano de validação"])
        for page in page_order:
            for file in (pages / page / "visuals").glob("*/visual.json"):
                entry = read_json(file)
                pos = entry["position"]
                self.assertLessEqual(pos["x"] + pos["width"], 1280)
                self.assertLessEqual(pos["y"] + pos["height"], 840)
                for state in entry["visual"].get("query", {}).get("queryState", {}).values():
                    for projection in state["projections"]:
                        field = projection["field"]["Column"]
                        self.assertIn(field["Property"], bindings[field["Expression"]["SourceRef"]["Entity"]])

    def test_definitions_are_reproducible(self):
        with TemporaryDirectory() as tmp:
            draft = Path(tmp)
            copytree(ROOT / "data", draft / "data", ignore=lambda _path, names: [n for n in names if n in {"raw", "private"}])
            build(draft)
            for path in (draft / "powerbi").rglob("*"):
                if path.is_file():
                    self.assertEqual(path.read_bytes(), (ROOT / path.relative_to(draft)).read_bytes())

    def test_document_links_and_form_fields(self):
        for path in [ROOT / "README.md", *(ROOT / "docs").glob("*.md")]:
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if not link.startswith("https://"):
                    self.assertTrue((path.parent / link).is_file(), (path.name, link))
        form = (ROOT / "pesquisa" / "avaliar.html").read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r'<select[^>]+ name="([^"]+)"', form)), {
            "elegivel", "experiencia", "confianca", "escolheria_tom", "intencao_compra",
            "barreira", "melhoria", "sem_estoque",
        })
        self.assertNotIn("https://", form)


if __name__ == "__main__":
    unittest.main()
