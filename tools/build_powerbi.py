"""Gera o PBIP da proposta com as referências e o protocolo incorporados."""

import base64
import csv
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
NAME = "FranMarketResearch"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/"
DEFINITION = SCHEMA + "item/report/definition/"
BACKGROUND, INK, MUTED, ACCENT = "#F9F3F6", "#32232E", "#634C5C", "#84184D"
TABLES = {
    "Escopo da proposta": ("escopo", {
        "ordem": "Ordem", "elemento": "Elemento", "definicao": "Definição", "limite": "Limite",
    }),
    "Benchmark": ("benchmark", {
        "ordem": "Ordem", "referencia": "Referência", "escopo": "Contexto", "evidencia": "Prática observada",
        "aplicacao": "O que testar", "fonte": "Link da fonte",
    }),
    "Prioridades": ("prioridades", {
        "ordem": "Ordem", "decisao": "Decisão", "risco": "Atrito para investigar",
        "teste": "Teste proposto", "metrica": "Indicador", "criterio": "Regra de decisão",
    }),
    "Indicadores": ("indicadores", {
        "ordem": "Ordem", "indicador": "Indicador", "calculo": "Cálculo", "precaucao": "Como interpretar",
    }),
}


def identity(key):
    return uuid5(NAMESPACE_URL, f"https://github.com/memellsss/fran-natural-skin-market-research/{key}")


def write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def semantic_table(root, entity, stem, labels):
    path = root / "data" / f"{stem}.csv"
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        if next(reader) != list(labels):
            raise ValueError(f"Colunas inesperadas: {path}")
        for i, row in enumerate(reader, start=2):
            if len(row) != len(labels):
                raise ValueError(f"Número de colunas incorreto: {path}:{i}")
    encoded = base64.b64encode(path.read_bytes().replace(b"\r\n", b"\n")).decode("ascii")
    columns = []
    types = []
    for source, label in labels.items():
        index = source == "ordem"
        columns.append({
            "name": label, "sourceColumn": source, "dataType": "int64" if index else "string",
            "summarizeBy": "none", "lineageTag": str(identity(f"{entity}/{label}")),
        })
        types.append(f'{{"{source}", {"Int64.Type" if index else "type text"}}}')
    return {
        "name": entity, "lineageTag": str(identity(entity)), "columns": columns,
        "partitions": [{
            "name": entity, "mode": "import",
            "source": {"type": "m", "expression": [
                "let",
                f'    Conteudo = Binary.FromText("{encoded}", BinaryEncoding.Base64),',
                '    Dados = Csv.Document(Conteudo, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
                "    Cabecalhos = Table.PromoteHeaders(Dados, [PromoteAllScalars=true]),",
                f'    Tipos = Table.TransformColumnTypes(Cabecalhos, {{{", ".join(types)}}}, "pt-BR")',
                "in",
                "    Tipos",
            ]},
        }],
    }


def semantic_model(root):
    return {
        "name": NAME, "compatibilityLevel": 1601,
        "model": {
            "culture": "pt-BR", "sourceQueryCulture": "pt-BR", "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "annotations": [
                {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
                {"name": "PBI_ProTooling", "value": '["DevMode"]'},
            ],
            "tables": [semantic_table(root, entity, *spec) for entity, spec in TABLES.items()],
        },
    }


def literal(value):
    if isinstance(value, bool):
        token = str(value).lower()
    elif isinstance(value, (int, float)):
        token = f"{value}D"
    else:
        token = "'" + value.replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": token}}}


def color(hex_code):
    return {"solid": {"color": literal(hex_code)}}


def props(**values):
    return [{"properties": values}]


def textbox(*lines):
    return {"visualType": "textbox", "objects": {"general": props(paragraphs=[
        {"textRuns": [{"value": text, "textStyle": {
            "fontFamily": "Segoe UI", "fontSize": f"{size}pt", "color": shade,
            "fontWeight": "bold" if bold else "normal",
        }}]} for text, size, shade, bold in lines
    ])}}


def column(entity, name):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": name}}


def data_table(entity, title, fields):
    return {
        "visualType": "tableEx",
        "query": {
            "queryState": {"Values": {"projections": [
                {"field": column(entity, label), "queryRef": f"{entity}.{label}", "nativeQueryRef": label}
                for label in fields
            ]}},
            "sortDefinition": {"sort": [{"field": column(entity, fields[0]), "direction": "Ascending"}]},
        },
        "visualContainerObjects": {
            "background": props(show=literal(True), color=color("#FFFFFF"), transparency=literal(0)),
            "title": props(show=literal(True), text=literal(title), fontSize=literal(14), fontColor=color(INK)),
        },
        "objects": {"columnHeaders": props(wordWrap=literal(True)), "values": props(wordWrap=literal(True))},
    }


def pages(folder):
    specs = [
        ("overview", "Proposta", "FRAN Natural Skin • estudo independente • sem respostas coletadas", [
            ("question", 152, 127, textbox(
                ("Você compraria uma base online sem ter certeza do tom?", 23, ACCENT, True),
                ("O teste compara a mesma ficha e o mesmo preço, com ou sem a descrição de um guia de tonalidades.", 13, INK, False),
                ("Confiança e intenção são medidas separadamente. Não há dados de vendas neste relatório.", 12, MUTED, False),
            )),
            ("scope", 295, 510, data_table("Escopo da proposta", "Pergunta, público e desenho",
                                            ["Ordem", "Elemento", "Definição", "Limite"])),
        ]),
        ("benchmark", "Benchmark", "Referências de escolha • não compara fórmula ou desempenho", [
            ("market", 152, 484, data_table("Benchmark", "Como outras marcas orientam a escolha",
                                            ["Ordem", "Referência", "Contexto", "Prática observada", "O que testar"])),
            ("takeaway", 652, 145, textbox(
                ("O que vale testar primeiro", 19, ACCENT, True),
                ("Começar com indicação de subtom e fotos padronizadas antes de investir em provador virtual.", 13, INK, False),
                ("Uma cartela maior não garante uma escolha mais fácil.", 12, MUTED, False),
            )),
        ]),
        ("validation", "Plano de validação", "Hipóteses e métricas pré-definidas • nenhum resultado de coleta", [
            ("decisions", 152, 335, data_table("Prioridades", "Prioridades e regras de decisão",
                                               ["Ordem", "Decisão", "Atrito para investigar", "Teste proposto",
                                                "Indicador", "Regra de decisão"])),
            ("metrics", 503, 316, data_table("Indicadores", "Como ler o teste A/B",
                                             ["Ordem", "Indicador", "Cálculo", "Como interpretar"])),
        ]),
    ]
    ids = [identity(key).hex[:20] for key, *_ in specs]
    write(folder / "pages.json", {
        "$schema": DEFINITION + "pagesMetadata/1.0.0/schema.json", "pageOrder": ids, "activePageName": ids[0],
    })
    for i, ((key, name, description, visuals), page_id) in enumerate(zip(specs, ids, strict=True), 1):
        path = folder / page_id
        write(path / "page.json", {
            "$schema": DEFINITION + "page/1.4.0/schema.json", "name": page_id,
            "displayName": name, "displayOption": "FitToPage", "width": 1280, "height": 840,
            "objects": {"background": props(color=color(BACKGROUND), transparency=literal(0))},
        })
        header = textbox(
            (f"PESQUISA DE MERCADO   /   {i:02d}", 12, ACCENT, True),
            (name, 29, INK, True),
            (description, 13, MUTED, False),
        )
        for j, (visual_key, y, height, visual) in enumerate([("header", 23, 110, header), *visuals], 1):
            visual_id = identity(f"{key}/{visual_key}").hex[:20]
            write(path / "visuals" / visual_id / "visual.json", {
                "$schema": DEFINITION + "visualContainer/2.7.0/schema.json", "name": visual_id,
                "position": {"x": 24, "y": y, "width": 1232, "height": height, "z": j * 1000, "tabOrder": j * 1000},
                "visual": visual,
            })


def build(root=ROOT):
    folder = root / "powerbi"
    report, model = folder / f"{NAME}.Report", folder / f"{NAME}.SemanticModel"
    write(folder / f"{NAME}.pbip", {
        "$schema": SCHEMA + "pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": report.name}}],
    })
    write(report / "definition.pbir", {
        "$schema": SCHEMA + "item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": "../" + model.name}},
    })
    write(model / "definition.pbism", {
        "$schema": SCHEMA + "item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "1.0", "settings": {"qnaEnabled": False},
    })
    write(model / "model.bim", semantic_model(root))
    theme = "MarketResearch.json"
    write(report / "StaticResources" / "RegisteredResources" / theme, {
        "name": "Pesquisa de mercado", "dataColors": [ACCENT, "#514070", "#4E7775"],
        "background": "#FFFFFF", "foreground": INK, "tableAccent": ACCENT,
    })
    write(report / "definition" / "report.json", {
        "$schema": DEFINITION + "report/3.0.0/schema.json",
        "themeCollection": {"customTheme": {
            "name": theme, "type": "RegisteredResources",
            "reportVersionAtImport": {"visual": "1.8.100", "report": "2.0.100", "page": "1.3.100"},
        }},
        "resourcePackages": [{
            "name": "RegisteredResources", "type": "RegisteredResources",
            "items": [{"name": theme, "path": theme, "type": "CustomTheme"}],
        }],
    })
    write(report / "definition" / "version.json", {
        "$schema": DEFINITION + "versionMetadata/1.0.0/schema.json", "version": "2.0.0",
    })
    pages(report / "definition" / "pages")


if __name__ == "__main__":
    build()
