# Resultados

`reference/` contém uma cópia sanitizada das métricas do lote privado que deu
origem às tabelas do manuscrito (`2026-06-01_20-44`, versão `1780346691`). IDs de
usuário, modelos e artefatos, timestamps internos, predições por evento, pipelines
serializados e metadados categóricos do SHAP foram deliberadamente omitidos.

Esses CSVs são **referência histórica**, não evidência de uma nova reprodução.
Uma execução pública escreve seus próprios artefatos em `results/reproduced/`.

## Colunas

- `train_r2` e `train_rmse`: métricas no subconjunto de treino (54 eventos).
- `test_r2` e `test_rmse`: métricas no holdout (13 eventos).
- `legacy_reported_cv_rmse`: valor que os relatórios privados rotularam como
  “Group CV RMSE”. Sem grupos configurados, o código substituiu essa métrica pelo
  RMSE do holdout; por isso ela é idêntica a `test_rmse` em todas as linhas.
- `search_cv_rmse`: RMSE médio real da configuração vencedora dentro do
  `GridSearchCV` de cinco dobras, recuperado de `cv_results.mean_test_score`.

O manuscrito ordenou famílias pelo campo legado/holdout. Assim, a ordem publicada
não é a ordem de `search_cv_rmse`. Consulte `docs/divergences.md` antes de comparar
uma nova execução.
