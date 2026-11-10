# Resultados

`reference/` contém métricas agregadas do lote `2026-06-01_20-44` utilizado
nas tabelas do artigo. Esses arquivos são referência histórica, não saídas
de uma nova execução. Identificadores operacionais, modelos privados e
predições vinculadas aos registros de origem não são distribuídos aqui.

As execuções completas gravam em `results/reproduced/`; o modo `--smoke`,
em `results/smoke/`. Essas pastas são ignoradas pelo Git.

## Métricas

- `train_r2` e `train_rmse`: desempenho no treino, com 54 eventos;
- `test_r2` e `test_rmse`: desempenho no holdout, com 13 eventos;
- `legacy_reported_cv_rmse`: campo histórico chamado “CV RMSE”, preenchido pelo RMSE do holdout;
- `search_cv_rmse`: RMSE real da busca de hiperparâmetros com cinco dobras no treino.

O ranking histórico usa holdout. Consulte as
[notas de interpretação](../docs/divergences.md) antes de comparar novas saídas.

## Licença e crédito

As métricas estão sob [CC BY 4.0](../LICENSE-DATA), quanto aos direitos
disponíveis sobre esses materiais. Crédito: Oscar Borges Faleta Santana,
FarmNote, lote `2026-06-01_20-44`.
As condições dos dados meteorológicos são descritas em
[licenças de terceiros](../docs/third_party_licenses.md).
