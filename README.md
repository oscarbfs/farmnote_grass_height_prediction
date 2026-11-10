# FarmNote — predição da altura futura do capim

Código de aprendizado de máquina do FarmNote para estimar
`end_grass_height_avg_cm`: a altura final média do capim, em centímetros, no
intervalo entre duas medições consecutivas no mesmo piquete.

O repositório acompanha o artigo *FarmNote: aplicação de aprendizado de máquina
para predição da altura futura do capim utilizando dados de pastagem,
meteorológicos e de movimentação do rebanho*. Aqui estão as instruções para
instalar, executar e reutilizar o código. A discussão científica está no artigo.

O pipeline lê um CSV analítico pseudonimizado, prepara as variáveis, compara
15 regressores com busca em grade e gera métricas e interpretações SHAP.
Há dois experimentos: com 60 variáveis e sem movimentação/ocupação, com 16.
O aplicativo e a API operacional do FarmNote não são necessários para executar.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `src/farmnote_grass_height/` | Carregamento, pré-processamento, modelos, treino, avaliação e SHAP |
| `scripts/` | Comandos de execução e verificação |
| `data/` | CSV analítico e [dicionário de dados](data/data_dictionary.md) |
| `results/reference/` | Métricas de referência do estudo |
| `tests/` | Testes do schema, seleção de variáveis, split, pré-processamento e modelos |
| `docs/` | Orientações técnicas, validação e licenças de terceiros |

## Instalação

Use Python 3.11 ou 3.12; a execução de referência foi validada com Python
3.12.10. As versões das dependências estão fixadas em `requirements.txt`.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
```

O treinamento usa os dados locais do CSV. Não exige banco de dados, conta
OpenWeather nem chave de API.

## Executar

Na raiz do repositório, confira o ambiente e o dataset:

```bash
python -m pip check
python -m pytest
python scripts/check_publication_safety.py
```

Experimento com movimentação e ocupação:

```bash
python scripts/train_models.py
python scripts/evaluate_models.py --experiment with_movement_occupation
python scripts/generate_shap.py
```

Experimento sem movimentação e ocupação:

```bash
python scripts/run_without_movement.py
python scripts/evaluate_models.py --experiment without_movement_occupation
python scripts/generate_shap.py --experiment without_movement_occupation
```

Os grids completos podem demorar. Para verificar rapidamente a instalação:

```bash
python scripts/train_models.py --smoke --models linear_regression
python scripts/evaluate_models.py --run-kind smoke --experiment with_movement_occupation
python scripts/generate_shap.py --run-kind smoke --models linear_regression --top-models 1 --max-evals 200
```

Use `--help` em cada script para consultar opções como `--dataset`,
`--output-root` e seleção de modelos. O modo `--smoke` reduz os grids e serve
apenas para verificar o funcionamento.

## Resultados

As execuções completas gravam em `results/reproduced/<experimento>/`;
as rápidas, em `results/smoke/<experimento>/`. Essas pastas são ignoradas pelo Git.

- `manifest.json`: hash do CSV, versões, variáveis, split, seeds e parâmetros;
- `metrics.csv`: métricas de treino, teste e busca em grade;
- `models/`, `predictions/` e `search_results/`: modelos, predições e scores dos grids;
- `evaluation_recomputed.csv`: conferência das métricas após recarregar os modelos;
- `shap/`: importâncias globais, gráficos e consolidação das variáveis relevantes.

A avaliação e o SHAP conferem o hash do CSV com o manifesto do treinamento.
Use o mesmo arquivo nas três etapas. Consulte [resultados](results/README.md)
e [validação](docs/validation.md).

## Como interpretar as métricas

`search_cv_rmse` é o RMSE da validação cruzada de cinco dobras no treino.
`holdout_rmse` é o RMSE do conjunto de teste. O campo
`legacy_reported_cv_rmse` preserva a métrica histórica chamada “CV RMSE” nas
tabelas do estudo, cujo valor veio do holdout; ele não representa uma segunda CV.

O protocolo histórico usa split aleatório 54/13, sem agrupamento por piquete
ou separação temporal. O ranking padrão e os cinco modelos de SHAP são
selecionados por holdout. Os atributos do intervalo descrevem um cenário
retrospectivo; uma previsão no início exige informações planejadas ou previstas.
Essas características e outras limitações de implementação estão em
[notas de execução](docs/divergences.md).

## Dados e consentimento

O CSV contém 67 eventos e 77 colunas. Quatro identificadores foram substituídos
por pseudônimos; as relações entre eventos e piquetes foram preservadas.
Não há mapa de correspondência, nomes operacionais ou coordenadas no arquivo.

A disponibilização dos dados da propriedade tem consentimento do proprietário,
inclusive caso a origem seja reconhecida. Datas, áreas, alturas, pesos,
contagens, movimentações e clima foram preservados. O conjunto é
pseudonimizado e não possui garantia de anonimato irreversível.
Consulte [formato e preparação dos dados](data/README.md).

## Licenças

| Material | Licença |
|---|---|
| Código e documentação | Apache 2.0 — [LICENSE](LICENSE) e [NOTICE](NOTICE) |
| Dataset e métricas de referência | CC BY 4.0 — [LICENSE-DATA](LICENSE-DATA), limitada aos direitos disponíveis sobre esses materiais |

Apache 2.0 permite uso, modificação e redistribuição conforme seus termos.
Preserve a licença e os avisos aplicáveis e identifique modificações.
CC BY 4.0 exige atribuição, referência à licença e indicação de alterações.

**A redistribuição das colunas meteorológicas sob CC BY 4.0 ainda depende de
confirmação dos termos do plano estudantil OpenWeather.** Essa licença não
substitui direitos do provedor. Weather data provided by
[OpenWeather](https://openweathermap.org/). Veja
[licenças de terceiros](docs/third_party_licenses.md).

As dependências mantêm suas próprias licenças. As licenças deste repositório
não abrangem o aplicativo, a API privada, o artigo ou dados operacionais externos.

## Crédito e citação

Oscar Borges Faleta Santana — Instituto Federal de Educação, Ciência e
Tecnologia Baiano, Campus Catu. Contato: <oscar.borgesfs@gmail.com>.
Copyright 2026 Oscar Borges Faleta Santana.

Citação: SANTANA, Oscar Borges Faleta. **FarmNote — predição da altura futura
do capim**. Versão 0.1.0. 2026.
[Repositório](https://github.com/oscarbfs/farmnote_grass_height_prediction).
Informe também o commit utilizado. Metadados em [CITATION.cff](CITATION.cff).

Crédito do dataset e das métricas: Oscar Borges Faleta Santana, FarmNote,
lote analítico `2026-06-01_20-44`, com enriquecimento meteorológico OpenWeather.

## Segurança

Não adicione credenciais, arquivos `.env`, dumps, planilhas operacionais,
mapas de IDs ou modelos privados. Antes de publicar alterações, execute
`python scripts/check_publication_safety.py` e consulte o
[checklist de publicação](docs/publication_checklist.md).
