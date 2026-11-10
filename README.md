# FarmNote — predição da altura futura do capim

Este repositório contém o artefato experimental associado ao estudo de predição
de `end_grass_height_avg_cm` desenvolvido no contexto do FarmNote. Ele reúne o
dataset analítico pseudonimizado, o pré-processamento, os quinze regressores, os
grids completos, a busca de hiperparâmetros, a avaliação, a análise SHAP e a
ablação das variáveis de movimentação/ocupação.

Este **não é** o repositório do produto FarmNote. O aplicativo Flutter, a API
completa, autenticação, MongoDB, integrações, infraestrutura, credenciais e dados
operacionais brutos não fazem parte desta distribuição.

> Nota de rastreabilidade: o manuscrito chama uma coluna de resultados de
> “Group CV RMSE”, mas o código que gerou as tabelas não executou GroupKFold.
> Quando não havia grupos, essa coluna recebia o RMSE do holdout. Por isso ela é
> idêntica ao RMSE de teste em todas as linhas publicadas. Este repositório
> preserva a execução histórica e expõe, separadamente, `search_cv_rmse`,
> `holdout_rmse` e `legacy_reported_cv_rmse`.

## Escopo científico

A unidade de análise é um evento entre duas medições consecutivas de altura no
mesmo piquete. A medição inicial e as variáveis agregadas do intervalo formam os
preditores; a medição seguinte é o alvo, em centímetros.

O dataset final contém:

- 67 eventos;
- uma origem/fazenda pseudonimizada;
- cinco piquetes pseudonimizados;
- período analítico entre 26/04/2025 e 01/02/2026, dentro do período de coleta
  mais amplo relatado no artigo (20/04/2025–08/02/2026);
- 77 colunas analíticas, das quais 60 entram no experimento completo e 16 na
  ablação sem movimentação/ocupação.

O estudo compara dois experimentos:

- `with_movement_occupation`: conjunto completo após controle de vazamento;
- `without_movement_occupation`: o mesmo pipeline, removendo por código os
  atributos de quantidade/peso do rebanho, entradas, saídas, permanência,
  ocupação ponderada, piquetes adicionais e `duration_seconds`.

## Estrutura

| Caminho | Papel |
|---|---|
| `requirements.txt` | Lock completo do ambiente científico recuperado do projeto-fonte |
| `data/pasturages_anonymized.csv` | Dataset analítico utilizado pelo pipeline público |
| `data/data_dictionary.md` | Tipo, grupo, unidade, papel, vazamento, ablação e anonimização de cada coluna |
| `src/farmnote_grass_height/data/` | Schema, leitura, validação e seleção de features |
| `src/farmnote_grass_height/preprocessing/` | Imputação, indicadores de ausência, datas, booleanos, escala e target encoding |
| `src/farmnote_grass_height/models/` | Quinze estimadores e grids completos |
| `src/farmnote_grass_height/training/` | Split histórico, GridSearchCV e persistência local dos artefatos |
| `src/farmnote_grass_height/evaluation/` | R², MSE, RMSE, MAE e regras de ranking |
| `src/farmnote_grass_height/interpretation/` | SHAP global e consolidação do top 10 |
| `scripts/` | Entradas de linha de comando para reproduzir e auditar |
| `results/reference/` | Métricas históricas sanitizadas, sem IDs ou modelos privados |
| `docs/` | Construção do dataset, proveniência, divergências, validação e checklist de publicação |
| `tests/` | Testes de schema, dataset, leakage, split, pré-processamento e registro de modelos |

## Dados e privacidade

O pipeline público começa em `data/pasturages_anonymized.csv`, isto é, no dataset
**analítico**, não nas tabelas operacionais. Os dados brutos foram coletados pelo
aplicativo FarmNote, consolidados pela API e enriquecidos com clima; o sistema
operacional completo não integra este repositório.

Quatro campos foram substituídos sem gravar um mapa reversível:

- `id` → `row_XX`;
- `user_id` → `source_XX`;
- `paddock_id` → `paddock_XX`;
- `pasturage_event_id` → `event_XX`.

A relação entre eventos e piquetes foi preservada. Os outros 4.891 valores do
CSV foram comparados textualmente com o artefato analítico de origem e não foram
alterados. Não há nomes, bovine IDs, coordenadas, endereços, tokens ou chaves no
arquivo público.

Datas exatas e séries meteorológicas foram preservadas porque alimentam as
transformações temporais e os modelos. Elas continuam sendo quasi-identificadores
e devem receber aprovação explícita do responsável pelos dados antes da
publicação definitiva. Consulte `data/README.md` e
`docs/publication_checklist.md`.

Para regenerar o CSV a partir de um artefato privado autorizado:

```bash
python scripts/anonymize_dataset.py /caminho/privado/training_dataset.csv
```

O script altera somente os quatro identificadores, valida o schema e não salva a
correspondência original → pseudônimo.

## Ambiente

Recomenda-se Python 3.12.10, versão registrada no ambiente do projeto-fonte. O
pacote aceita Python 3.11 ou 3.12. As versões científicas foram recuperadas do
lockfile do experimento. As dependências principais estão fixadas em
`pyproject.toml`; o conjunto completo, incluindo transitivas, está em
`requirements.txt`:

- NumPy 2.3.1;
- pandas 2.3.1;
- scikit-learn 1.7.2;
- SciPy 1.16.0;
- LightGBM 4.6.0;
- SHAP 0.48.0;
- matplotlib 3.10.9;
- Joblib 1.5.1.

Não são necessários MongoDB, OpenWeather, Firebase nem qualquer serviço do
FarmNote.

### Instalação

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

## Metodologia implementada

### Pré-processamento

Todas as transformações são componentes do pipeline e são ajustadas somente em
cada subconjunto de treino:

- numéricas: mediana e `StandardScaler`;
- numéricas totalmente ausentes no treino: constante zero e escala;
- indicador de ausência para colunas numéricas que possuem ausência no treino;
- datas: timestamp UTC, mês, dia da semana, dia do ano e fim de semana, com
  padronização aprendida no treino;
- booleanos: conversão 0/1 e moda;
- categóricas: target encoding out-of-fold com 5 dobras, smoothing 10 e seed 42;
- categorias desconhecidas: média global do alvo aprendida no treino.

### Controle de vazamento

A seleção ocorre antes do pré-processamento em
`src/farmnote_grass_height/data/features.py`. O código exclui o alvo, IDs e
proxies de fim de evento, incluindo quantidade/peso final, deltas de peso e
altura terminal de piquetes extras. A lista executável é a fonte de verdade; o
dicionário de dados mostra o status de cada coluna.

### Modelos e busca

São avaliados Linear Regression, Ridge, Lasso, Elastic Net, SVR, Kernel Ridge,
Decision Tree, Random Forest, Extra Trees, Bagging, Gradient Boosting, Hist
Gradient Boosting, LightGBM, KNN e MLP. Os espaços completos estão em
`src/farmnote_grass_height/models/grids.py`.

Cada família usa `GridSearchCV` com:

- cinco dobras ordinárias no subconjunto de treino;
- scorer RMSE com `greater_is_better=False`;
- `n_jobs=1`;
- `refit=False`, seguido de ajuste manual da melhor configuração.

### Split e métricas

As 67 linhas são ordenadas por término, início e ID do evento. Em seguida, o
split histórico embaralha os índices com `random.Random(42)`, reserva os
primeiros `int(67 × 0,2) = 13` eventos para teste e mantém 54 para treino. Não é
um split temporal nem agrupado por piquete.

São calculados R², MSE, RMSE e MAE em treino e holdout. O relatório público ainda
grava o RMSE real da configuração vencedora nas cinco dobras.

### SHAP

O procedimento transforma as 67 linhas com o preprocessor já ajustado, usa as
primeiras até 100 linhas transformadas como background, chama `shap.Explainer`
sobre a função de predição do estimador e calcula média absoluta, desvio padrão
absoluto e média assinada. As importâncias processadas são agregadas às colunas
brutas e o top 10 dos cinco modelos é consolidado por frequência, posição média
e média de `abs(SHAP)`.

Para não republicar IDs por metadados, a versão pública não grava explicações
locais nem os mapas de categorias que estavam nos JSONs privados.

## Reprodução

Os grids completos, especialmente o LightGBM, executam milhares de combinações
em cinco dobras e podem levar bastante tempo. Os comandos padrão preservam o
experimento; `--smoke` existe somente para validar instalação e caminhos.

### 1. Auditoria antes da execução

```bash
python scripts/check_publication_safety.py
python -m pytest
```

### 2. Experimento A — com movimentação/ocupação

```bash
python scripts/train_models.py
python scripts/evaluate_models.py --experiment with_movement_occupation
python scripts/generate_shap.py
```

### 3. Experimento B — sem movimentação/ocupação

```bash
python scripts/run_without_movement.py
python scripts/evaluate_models.py --experiment without_movement_occupation
python scripts/generate_shap.py --experiment without_movement_occupation
```

### Validação rápida, sem valor científico

```bash
python scripts/train_models.py --smoke --models linear_regression hist_gradient_boosting_regressor
python scripts/run_without_movement.py --smoke --models linear_regression
python scripts/evaluate_models.py --run-kind smoke --experiment with_movement_occupation
python scripts/generate_shap.py --run-kind smoke --models linear_regression --top-models 1 --max-evals 200
```

Resultados de smoke test são gravados em `results/smoke/` e não devem ser
comparados ao artigo.

## Saídas

Cada experimento em `results/reproduced/<feature-set>/` produz:

- `manifest.json`: dataset/hash, versões, features, split, seeds e modelos;
- `metrics.csv`: métricas de treino, teste, busca-CV e campo legado;
- `models/*.joblib`: pipelines completos ajustados;
- `predictions/*.csv`: verdade e predição apenas para IDs pseudonimizados;
- `search_results/*.csv`: resultados das combinações do GridSearchCV;
- `evaluation_recomputed.csv`: conferência dos modelos serializados;
- `shap/*_global.csv`: importâncias agregadas às features brutas;
- `shap/*_processed.csv`: importâncias no espaço transformado;
- `shap/*_global.png`: gráficos globais;
- `shap/top10_consolidated.csv`: tabela consolidada entre modelos.

Arquivos gerados são ignorados pelo Git. `results/reference/` contém somente as
métricas históricas sanitizadas que correspondem às tabelas do manuscrito; não
é apresentado como uma nova execução.

O escopo e os resultados da validação realizada durante esta extração estão em
`docs/validation.md`. Ela inclui smoke tests dos 15 estimadores, execução CLI dos
dois experimentos e uma comparação parcial com grids integrais; não afirma que a
busca completa dos 15 modelos foi reexecutada.

## Correspondência artigo ↔ código

| Artigo | Repositório |
|---|---|
| Construção do dataset | `docs/dataset_construction.md`, entrada em `data/` |
| Variáveis e tipos | `data/data_dictionary.md`, `src/farmnote_grass_height/data/schema.py` |
| Pré-processamento | `src/farmnote_grass_height/preprocessing/` |
| Controle de vazamento | `src/farmnote_grass_height/data/features.py` |
| Modelos e grids | `src/farmnote_grass_height/models/` |
| Split e GridSearchCV | `src/farmnote_grass_height/training/` |
| Métricas | `src/farmnote_grass_height/evaluation/` |
| SHAP | `src/farmnote_grass_height/interpretation/`, `scripts/generate_shap.py` |
| Experimento sem movimento | `scripts/run_without_movement.py` |

## Limitações e divergências conhecidas

O arquivo `docs/divergences.md` registra em detalhes as diferenças encontradas.
As principais são:

1. o “Group CV RMSE” publicado é um fallback do holdout; a CV de tuning existe,
   mas possui valores e ranking diferentes;
2. o ranking de famílias e a seleção dos cinco modelos para SHAP foram feitos
   pelo holdout, embora o texto diga CV RMSE;
3. o split não isola piquetes nem respeita ordem temporal;
4. o factory histórico não aplicou todas as seeds declaradas nos specs;
5. o early stopping do LightGBM provavelmente caiu para fit comum;
6. SHAP foi calculado sobre treino + holdout;
7. `finished_at`, clima observado e movimentos ocorridos no intervalo refletem
   um cenário retrospectivo; sua disponibilidade em uma previsão prospectiva
   depende de planejamento/previsão externa;
8. a agregação SHAP histórica por substring pode associar nomes processados
   sobrepostos à feature bruta errada; o comportamento foi mantido e documentado.

Esses pontos não foram corrigidos silenciosamente, pois isso produziria outro
experimento.

## Licença

O repositório contém dois arquivos de licença, com escopos distintos:

| Material | Licença | Texto integral |
|---|---|---|
| Código científico em `src/`, `scripts/` e `tests/` | Apache License 2.0 (`Apache-2.0`) | [LICENSE](LICENSE) |
| Dataset analítico `data/pasturages_anonymized.csv` | Creative Commons Attribution 4.0 International (`CC-BY-4.0`) | [LICENSE-DATA](LICENSE-DATA) |

A [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) permite uso,
modificação e redistribuição, inclusive comercial, conforme seus termos. Na
redistribuição, inclua a licença, preserve os avisos aplicáveis e identifique
os arquivos modificados; preserve também as atribuições de um arquivo `NOTICE`,
se ele acompanhar o material de origem.

A [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) permite compartilhar
e adaptar os dados, inclusive para fins comerciais, conforme seus termos. Ao
compartilhá-los, dê o crédito exigido, mantenha os avisos fornecidos, indique a
licença com um link e informe alterações. Não imponha restrições adicionais
ao exercício dos direitos concedidos. Para rastreabilidade científica, registre
também a versão ou o commit e o hash do CSV utilizado.

Essas licenças se referem ao artefato científico e não estendem permissões ao
aplicativo FarmNote, à API privada, ao manuscrito ou aos dados operacionais
excluídos desta distribuição. As dependências mantêm suas próprias licenças.

A presença dos arquivos de licença não comprova, por si só, a autorização dos
titulares do código e dos dados nem resolve direitos de terceiros ou questões
de privacidade. A confirmação da titularidade, as informações de atribuição e
a aprovação da publicação do CSV continuam no
[checklist de publicação](docs/publication_checklist.md). O responsável também
deve confirmar o enquadramento da documentação e das métricas de referência,
que não estão explicitados nos arquivos de licença. A ausência de licença nas
fontes privadas, registrada na auditoria original, não deve ser confundida com
a presença de `LICENSE` e `LICENSE-DATA` neste repositório.

## Segurança

Nunca adicione `.env`, credenciais do OpenWeather, URIs MongoDB, dumps, XLSX do
aplicativo, JSONs privados de modelos ou dados operacionais. Execute
`python scripts/check_publication_safety.py` antes de cada publicação e revise
manualmente o checklist em `docs/publication_checklist.md`.
