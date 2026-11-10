# Notas de execução e interpretação

Estas notas explicam características do código que afetam o uso dos resultados.
A apresentação científica do experimento está no artigo.

## Métricas e seleção de modelos

`search_cv_rmse` é o RMSE real da busca de hiperparâmetros com cinco dobras no
treino. `holdout_rmse` é o RMSE do conjunto de teste. O campo
`legacy_reported_cv_rmse` preserva o valor histórico apresentado como “CV RMSE”,
que foi preenchido com o RMSE do holdout. Não trate esses campos como estimativas
independentes de validação cruzada.

O ranking padrão e a seleção dos cinco modelos para SHAP usam holdout.
Esse conjunto, portanto, também participa da comparação entre famílias e não
constitui um teste final intocado. No SHAP, `--ranking search_cv` permite
selecionar modelos pela métrica da busca.

## Disponibilidade das variáveis

O split é aleatório, sem isolamento temporal ou por piquete. As variáveis de
clima, movimentação e ocupação representam o intervalo observado, inclusive
seu fim. A consulta de peso inicial também pode considerar medição posterior
ao início. Remover proxies explícitos do alvo não torna essas entradas
automaticamente disponíveis no início de um evento.

`extra_paddocks_used_avg_seconds` mantém o cálculo histórico da sobreposição
de permanências em piquetes, cuja interpretação não deve ser reduzida a um
tempo exclusivamente em piquetes adicionais sem verificar a implementação.

## Variação entre execuções

Algumas factories preservam a ausência de seed da implementação histórica,
incluindo Decision Tree, Extra Trees, Gradient Boosting, Hist Gradient Boosting
e MLP. Não espere igualdade bit a bit em todas as famílias. O ajuste final do
LightGBM possui fallback para um fit comum; não presuma early stopping ativo
apenas por existir esse parâmetro no protocolo.

O SHAP considera os 67 eventos, incluindo treino e holdout. A agregação de
nomes processados por substring também é histórica e pode associar nomes
sobrepostos à variável bruta errada. As saídas são importâncias globais;
explicações locais e mapas de categorias não são exportados.

Essas características foram preservadas para executar o protocolo disponível.
Um split temporal, validação externa, novas seeds ou substituição de clima
observado por previsões constituem alterações de protocolo e devem ser
identificadas nos resultados.
