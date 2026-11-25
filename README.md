# FRAN Natural Skin — proposta de pesquisa de mercado

**Você compraria uma base online sem ter certeza do tom?** Esta proposta independente testa se um guia de tom e subtom pode aumentar a confiança na escolha da Base Líquida FRAN Natural Skin. É um projeto de portfólio, sem vínculo com a marca.

[Baixar o projeto (.zip)](https://github.com/memellsss/fran-natural-skin-market-research/archive/refs/heads/main.zip) · [Metodologia](docs/metodologia.md) · [Como apresentar no LinkedIn](docs/linkedin.md)

## O que vamos testar

| Prioridade | Pergunta | O que medir |
| --- | --- | --- |
| **Guia de tom e subtom** | A mesma ficha fica mais útil com fotos em luz padronizada, indicação de subtom e equivalências aproximadas? | Confiança na escolha, indecisão e intenção declarada de compra. |
| **Demonstração de uso** | Ver a diferença entre uma e duas camadas, com e sem pó, ajuda a ajustar expectativas? | Cobertura percebida, conforto e marcação de linhas em condições comparáveis. |
| **Disponibilidade por tonalidade** | Se a cor certa estiver indisponível, a pessoa prefere esperar, pedir aviso, trocar de produto ou desistir? | Ação declarada diante do cenário, não vendas ou demanda observada. |

O benchmark reúne exemplos da L’Oréal Paris, Maybelline e Boca Rosa. São referências de como comunicar e ajudar na escolha, não comparações de fórmula ou ranking de qualidade.

## Como abrir e avaliar

1. Baixe e **extraia o ZIP inteiro**. No **Power BI Desktop** para Windows, abra [`powerbi/FranMarketResearch.pbip`](powerbi/FranMarketResearch.pbip). Se as tabelas aparecerem vazias, clique em **Atualizar agora**. O relatório carrega CSVs incorporados ao modelo, sem login, servidor ou internet.
2. Percorra **Proposta → Benchmark → Plano de validação**. As tabelas mostram fontes, hipóteses e critérios de decisão; não há gráficos ou indicadores de uma pesquisa já realizada.
3. Para experimentar o teste, abra [`pesquisa/avaliar.html`](pesquisa/avaliar.html) **no navegador a partir da pasta extraída**. Cada sessão mostra um dos cenários. O botão de download gera um JSON no seu dispositivo; nenhuma resposta é enviada. Não publique respostas individuais em Issues ou PRs.

### Conclusão da proposta

Antes de sugerir ampliar a cartela ou mudar a fórmula, a proposta compara uma ficha simples com uma ficha que descreve um guia de tom e subtom. O preço hipotético é o mesmo nos dois cenários. O objetivo é medir confiança, intenção de compra e barreiras separadamente, para decidir se vale investir em um guia real e depois testá-lo com consumidoras e consumidores.

**Limites:** esta versão não contém corpus de redes sociais, comentários brutos, respostas coletadas, estoque observado ou números de vendas. O questionário testa a descrição do guia, não a usabilidade de um guia já construído.

## Desenvolvimento

O projeto Power BI está incluído no repositório. Para regenerar e testar os arquivos a partir dos CSVs:

```bash
python tools/build_powerbi.py
python -m unittest discover -s tests -v
```

Requer Python 3.10 ou superior e usa apenas a biblioteca padrão. Regenerar o projeto reescreve as definições geradas pelo script.
