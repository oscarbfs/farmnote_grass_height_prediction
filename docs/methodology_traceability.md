# Rastreabilidade entre o manuscrito e o repositório

Este documento indica onde cada procedimento científico descrito no manuscrito pode ser inspecionado e executado neste repositório. Ele também separa três conceitos que, na implementação histórica, acabaram registrados sob nomes semelhantes:

- **RMSE de busca**: `search_cv_rmse`, calculado nos cinco folds de `GridSearchCV` sobre a partição de treinamento;
- **RMSE de holdout**: `holdout_rmse`, calculado uma vez nos 20% reservados;
- **RMSE legado apresentado como CV**: `legacy_reported_cv_rmse`, que preserva explicitamente o valor histórico obtido por fallback a partir do holdout.

A discrepância é documentada em [divergences.md](divergences.md). O valor legado é mantido para rastrear as tabelas do manuscrito, sem ser apresentado como uma nova estimativa de validação cruzada.

## Mapa da metodologia

| Procedimento no manuscrito | Implementação ou evidência neste repositório | Saída ou verificação |
|---|---|---|
| Aquisição operacional por FarmNote | O sistema completo não é publicado; o limite desta distribuição é descrito em [dataset_construction.md](dataset_construction.md) e [provenance.md](provenance.md) | Não há banco, dump, endpoint, credencial nem aplicação Flutter neste repositório |
| Construção do conjunto analítico | Algoritmo auditado e pseudocódigo em [dataset_construction.md](dataset_construction.md); contrato das 77 colunas em [`data/schema.py`](../src/farmnote_grass_height/data/schema.py) | CSV analítico candidato em [`pasturages_anonymized.csv`](../data/pasturages_anonymized.csv), condicionado à revisão humana de publicação |
| Unidade de análise | [README dos dados](../data/README.md) e [dicionário de dados](../data/data_dictionary.md) | Uma linha por intervalo entre duas medições consecutivas de altura no mesmo piquete |
| Tipos, unidades e significado das variáveis | [Dicionário das 77 colunas](../data/data_dictionary.md) | Cada campo é classificado quanto a papel, vazamento, ablação, disponibilidade temporal e anonimização |
| Carregamento e validação do CSV | [`data/loader.py`](../src/farmnote_grass_height/data/loader.py) e [`data/schema.py`](../src/farmnote_grass_height/data/schema.py) | Validação de cabeçalho, tipos, alvo e identificadores; hash do dataset gravado no manifesto |
| Remoção de vazamento e proxies | [`data/features.py`](../src/farmnote_grass_height/data/features.py) | 60 features no experimento completo; 16 no experimento de ablação |
| Separação das variáveis por tipo | [`preprocessing/pipeline.py`](../src/farmnote_grass_height/preprocessing/pipeline.py) | Pipeline por grupos numérico, temporal, booleano e categórico |
| Imputação, indicadores de ausência e padronização | [`preprocessing/pipeline.py`](../src/farmnote_grass_height/preprocessing/pipeline.py) | Transformações são ajustadas dentro de cada fold e, depois, somente sobre o treino final |
| Transformação temporal | [`preprocessing/transformers.py`](../src/farmnote_grass_height/preprocessing/transformers.py) | Epoch, mês, dia da semana, dia do ano e indicador de fim de semana |
| Target encoding categórico | [`preprocessing/transformers.py`](../src/farmnote_grass_height/preprocessing/transformers.py) | Encoding out-of-fold com 5 folds, `smoothing=10` e semente 42 |
| Quinze famílias de regressão | [`models/registry.py`](../src/farmnote_grass_height/models/registry.py) | Registro central de factories, parâmetros fixos e nomes dos estimadores |
| Espaços de hiperparâmetros | [`models/grids.py`](../src/farmnote_grass_height/models/grids.py) | Grid bruto auditável e grid efetivo fornecido ao `GridSearchCV` |
| Divisão 80/20 | [`training/split.py`](../src/farmnote_grass_height/training/split.py) | Para 67 linhas: 54 de treino e 13 de holdout, após ordenação e embaralhamento compatíveis com a fonte |
| Busca em 5 folds | [`training/experiment.py`](../src/farmnote_grass_height/training/experiment.py) | `GridSearchCV`, scoring por RMSE negativo, `cv=5`, `refit=False` |
| Métricas R² e RMSE | [`evaluation/metrics.py`](../src/farmnote_grass_height/evaluation/metrics.py) e [`evaluate_models.py`](../scripts/evaluate_models.py) | `metrics.csv` e `evaluation_recomputed.csv`; MSE e MAE também são registrados como diagnósticos |
| Ranqueamento usado no manuscrito | [`evaluation/metrics.py`](../src/farmnote_grass_height/evaluation/metrics.py) | `article_compatible_rank` usa o RMSE de holdout legado; `search_cv_rmse` permanece disponível separadamente |
| Análise SHAP | [`interpretation/shap_analysis.py`](../src/farmnote_grass_height/interpretation/shap_analysis.py) e [`generate_shap.py`](../scripts/generate_shap.py) | CSV por modelo no espaço processado e agregado, gráfico global e consolidação das dez principais features |
| Experimento sem movimento/ocupação | Prefixos e exclusões em [`data/features.py`](../src/farmnote_grass_height/data/features.py); entrada em [`run_without_movement.py`](../scripts/run_without_movement.py) | Mesmo protocolo, com 16 features não pertencentes ao grupo retirado |
| Proveniência e limites de publicação | [provenance.md](provenance.md) e [publication_checklist.md](publication_checklist.md) | Hashes, commits auditados, pendências de licença e autorização do dataset |

## Fluxo executável

```text
pasturages_anonymized.csv (77 colunas)
    -> validação de esquema e tipos
    -> seleção do alvo e das features
       -> experimento completo: 60 features
       -> experimento sem movimento/ocupação: 16 features
    -> ordenação determinística + holdout 80/20 (seed 42)
    -> pré-processador ajustado dentro de cada fold
    -> GridSearchCV de 5 folds sobre as 54 linhas de treinamento
    -> ajuste final da configuração selecionada
    -> métricas de treino, holdout e busca CV
    -> modelos, predições, resultados de busca e manifesto
    -> SHAP global dos modelos selecionados
```

O pipeline deliberadamente começa no dataset analítico. A reconstrução desde dados operacionais exigiria entidades, banco e integrações privadas do FarmNote; por isso, o procedimento auditado foi descrito em documentação, mas não foi refeito com dados inventados. O CSV público candidato deve ser publicado somente após a autorização e as verificações previstas em [publication_checklist.md](publication_checklist.md).

## Protocolo reproduzido pelo código público

### 1. Dataset e alvo

O carregador espera exatamente 77 colunas. O alvo é `end_grass_height_avg_cm`. Os campos `id`, `user_id`, `paddock_id` e `pasturage_event_id` são mantidos apenas para identidade, auditoria e preservação das relações; não são usados como quatro features em conjunto. O tratamento público previsto é uma pseudonimização estável e sem tabela reversa no repositório:

- `id` -> `row_001`, `row_002`, ...;
- `user_id` -> `source_01`, ...;
- `paddock_id` -> `paddock_01`, ...;
- `pasturage_event_id` -> `event_001`, ... .

Os demais 73 campos e suas regras estão no [dicionário de dados](../data/data_dictionary.md). A pseudonimização preserva igualdade e relacionamento, mas não transforma valores científicos como alturas, tempos, pesos ou clima.

### 2. Features e controle de vazamento

Antes do split, a lista de features é definida por regras constantes e auditáveis. No experimento completo, 16 campos de identidade, alvo, snapshot ou informação terminal são excluídos dos 76 campos diferentes do identificador técnico `id`, resultando em 60 features. Entre as exclusões estão o alvo, as medições finais de ocupação/peso, deltas dependentes do final e a altura terminal de piquetes adicionais.

Na ablação, além dessas exclusões, são retirados os campos com os prefixos `start_bovine_`, `end_bovine_`, `delta_bovine_`, `during_`, `avg_seconds_from_`, `avg_time_bovine_`, `extra_paddocks_`, `bovines_per_` e `bovine_weight_per_`, além de `duration_seconds`. Restam 16 features. A lista exata, inclusive os casos que exigem revisão de disponibilidade no instante de previsão, está em [data_dictionary.md](../data/data_dictionary.md).

### 3. Split e validação

As linhas são ordenadas pelas datas de fim e início e pelo identificador de evento. A compatibilidade com a fonte é obtida com `random.Random(42)`: após o embaralhamento, as primeiras `floor(67 * 0,20) = 13` posições formam o holdout e as 54 restantes formam o treino. Não há agrupamento por piquete, propriedade ou evento e o split não é temporal.

O `GridSearchCV` recebe `cv=5`; para regressão, isso corresponde ao `KFold` padrão do scikit-learn, sem embaralhamento. Cada pipeline contém o pré-processador, de modo que imputação, escala e target encoding não são ajustados no holdout e são reajustados dentro dos folds de busca.

### 4. Modelos

As quinze famílias, na ordem da fonte, são: regressão linear, Ridge, Lasso, Elastic Net, SVR, árvore de decisão, Random Forest, Extra Trees, Gradient Boosting, Histogram Gradient Boosting, k-NN, MLP, LightGBM, Kernel Ridge e Bagging.

As sementes não são uniformes entre estimadores. A implementação efetiva usa 42 no Random Forest, no LightGBM e no Bagging externo. Decision Tree, Extra Trees, Gradient Boosting, MLP e a árvore base do Bagging conservam `random_state=None`, como ocorreu nas factories auditadas, mesmo quando uma especificação histórica declarava 42 para alguns deles. Isso limita a determinização integral.

O campo bruto `early_stopping_rounds=[10]` do LightGBM é retirado do espaço efetivo de `GridSearchCV`. No ajuste final, o código preserva a sequência de tentativas da fonte, inclusive o fallback para um `fit` sem metadados quando o `eval_set` no espaço bruto é incompatível com o pipeline transformado. Consequentemente, não se deve afirmar que early stopping esteve efetivamente ativo na execução histórica apenas a partir dos artefatos disponíveis.

### 5. Métricas e seleção

Para cada modelo são gravados R², RMSE, MSE e MAE em treino e holdout. O RMSE de busca é calculado diretamente de `-search.best_score_`. A ordem `article_compatible_rank` reproduz o mecanismo histórico: menor RMSE de holdout, valor que antes foi gravado também no campo denominado Group CV RMSE.

Esse desenho usa o holdout tanto para comparar famílias quanto para reportar o desempenho escolhido. Portanto, ele deve ser entendido como reprodução do procedimento que gerou o manuscrito, e não como avaliação final intocada. Uma análise futura corrigida deve definir previamente seleção por CV e reservar um conjunto de teste não consultado, mas tal mudança não foi aplicada silenciosamente aos resultados históricos.

### 6. SHAP

Por padrão, `generate_shap.py` seleciona os cinco modelos pelo ranqueamento compatível com o artigo (`--ranking article`). A alternativa `--ranking search_cv` usa o RMSE real da busca. O procedimento histórico é preservado ao explicar o conjunto analítico inteiro (67 exemplos, pois o limite padrão é 1.000), com até 100 exemplos iniciais como background e semente SHAP 0. Isso inclui treino e holdout; não é uma explicação exclusiva do conjunto de teste.

As importâncias no espaço transformado são agregadas de volta aos nomes das features originais. Não são exportadas explicações locais nem mapeamentos categóricos identificáveis.

## Comandos e produtos

Os comandos abaixo pressupõem que o ambiente indicado pelo arquivo de dependências do repositório já foi instalado. `--smoke` valida o encadeamento com um valor por hiperparâmetro, mas **não reproduz a busca do artigo**.

| Objetivo | Comando | Produtos principais |
|---|---|---|
| Treinar as 15 famílias com todas as features elegíveis | `python scripts/train_models.py` | `results/reproduced/with_movement_occupation/{manifest.json,metrics.csv,models/,predictions/,search_results/}` |
| Treinar a ablação sem movimento/ocupação | `python scripts/run_without_movement.py` | `results/reproduced/without_movement_occupation/{manifest.json,metrics.csv,models/,predictions/,search_results/}` |
| Recalcular e conferir métricas do experimento completo | `python scripts/evaluate_models.py --experiment with_movement_occupation` | `results/reproduced/with_movement_occupation/evaluation_recomputed.csv`; saída não zero se a diferença absoluta exceder `1e-10` |
| Recalcular e conferir métricas da ablação | `python scripts/evaluate_models.py --experiment without_movement_occupation` | `results/reproduced/without_movement_occupation/evaluation_recomputed.csv` |
| Gerar SHAP compatível com a seleção do manuscrito | `python scripts/generate_shap.py --experiment with_movement_occupation --ranking article` | `shap/*_global.csv`, `*_processed.csv`, `*_global.png`, `top10_consolidated.csv` e `metadata.json` |
| Gerar SHAP segundo o RMSE real da busca | `python scripts/generate_shap.py --experiment with_movement_occupation --ranking search_cv` | Mesmos produtos, com seleção de modelos potencialmente diferente |
| Validação rápida do encadeamento | `python scripts/train_models.py --smoke` e `python scripts/run_without_movement.py --smoke` | Artefatos sob `results/smoke/`; não são comparáveis ao artigo |

O argumento `--models` permite limitar os modelos em treinamento ou avaliação. Os scripts também aceitam caminhos alternativos via `--dataset` e `--output-root`. Os manifestos registram o hash SHA-256 do CSV, versões de runtime, índices e identificadores pseudonimizados das partições, features e hiperparâmetros selecionados; a avaliação e o SHAP recusam um dataset cujo hash seja diferente do usado no treinamento.

## Resultados de referência e nova execução

Os resultados de referência auditados devem permanecer distinguíveis de artefatos produzidos em uma nova máquina:

- arquivos sob `results/reference/` documentam a evidência histórica extraída e sanitizada;
- arquivos sob `results/reproduced/` são produzidos ao executar os scripts públicos;
- arquivos sob `results/smoke/` servem apenas para verificação técnica reduzida.

Diferenças podem ocorrer por seeds omitidas em algumas factories, versões das bibliotecas, implementação numérica dos estimadores e comportamento efetivo do fallback de ajuste do LightGBM. Nenhuma métrica deve ser alterada para coincidir artificialmente com o manuscrito.

## Limites desta rastreabilidade

- Não há dados operacionais brutos, banco MongoDB, API completa, infraestrutura, autenticação, segredo ou credencial nesta distribuição.
- Nenhum arquivo Flutter foi copiado. O aplicativo foi consultado apenas para delimitar a coleta; sua lógica de interface não é necessária para executar o experimento sobre o dataset analítico.
- A disponibilidade temporal de `finished_at`, clima observado no intervalo e features agregadas durante o evento depende do instante operacional pretendido para a previsão. O código histórico foi preservado, mas esses campos estão marcados para revisão científica no dicionário e em [divergences.md](divergences.md).
- A licença continua pendente de decisão do titular; a ausência de uma licença explícita não concede permissão de reutilização.
- A autorização para disponibilizar o CSV pseudonimizado continua sendo uma etapa humana obrigatória, mesmo depois das verificações técnicas.
