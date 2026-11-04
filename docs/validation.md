# Validação da extração pública

Validação executada em 10 de agosto de 2026, no Windows, com Python 3.12.10 e o
lock científico de `requirements.txt`, seguido da instalação editável do pacote
sem novas dependências. Os diretórios irmãos da API e do aplicativo não foram
importados nem necessários durante os testes.

## Ambiente e verificações estáticas

- instalação editável em `.venv` concluída;
- `python -m pip check`: nenhuma dependência quebrada;
- `python -m compileall -q src scripts`: concluído;
- `python -m pytest`: 8 testes aprovados;
- `python scripts/check_publication_safety.py`: nenhum segredo provável ou
  identificador operacional bruto encontrado;
- execução do verificador a partir de um diretório externo ao repositório:
  concluída, confirmando que os caminhos são derivados da própria árvore;
- busca manual pelos termos de credenciais solicitados: apenas menções
  documentais e expressões do próprio verificador, sem valores atribuídos;
- busca por UUIDs, `.env`, chaves e certificados: nenhum achado.

O CSV carregou com 67 linhas e 77 colunas, uma origem pseudonimizada, cinco
piquetes e 67 eventos. Seu SHA-256 é
`c68e057437c380e8f6ef29e053d33f139f8f95df4448c6563b3d9c89130cfeed`.
A comparação com o artefato analítico privado confirmou que os 4.891 campos
científicos não identificadores foram preservados; somente `id`, `user_id`,
`paddock_id` e `pasturage_event_id` foram substituídos.

## Componentes científicos

- split histórico: 54 linhas de treino e 13 de holdout, determinístico;
- experimento completo: 60 entradas brutas transformadas em 76 colunas;
- ablação: 16 entradas brutas transformadas em 24 colunas;
- matrizes de treino e holdout: somente valores finitos após o processamento;
- target encoder: 5 dobras, smoothing 10, seed 42 e suporte a grupos verificado;
- registro: 15 famílias na ordem histórica;
- todos os 15 grids efetivos foram aceitos por seus estimadores/pipelines;
- o `GridSearchCV` reduzido concluiu para 15/15 famílias nos dois conjuntos de
  features, incluindo persistência e recarga dos 30 pipelines.

O ambiente emitiu um aviso não fatal do Joblib ao tentar detectar CPUs físicas.
As execuções terminaram com código zero; isso é uma limitação do ambiente de
validação, não uma dependência científica.

## Execuções de ponta a ponta

Foram concluídos:

```text
python scripts/train_models.py --smoke
python scripts/evaluate_models.py --run-kind smoke --experiment with_movement_occupation
python scripts/generate_shap.py --run-kind smoke --experiment with_movement_occupation --models hist_gradient_boosting_regressor --top-models 1 --max-evals 200
python scripts/run_without_movement.py --smoke
python scripts/evaluate_models.py --run-kind smoke --experiment without_movement_occupation
python scripts/generate_shap.py --run-kind smoke --experiment without_movement_occupation --models linear_regression --top-models 1 --max-evals 200
```

Treino, persistência Joblib, recarregamento, recálculo das métricas, previsões,
resultados da busca e tabelas/gráficos SHAP funcionaram nos dois conjuntos de
features. As pastas geradas são ignoradas pelo Git.

## Comparação parcial com o lote histórico

Também foram executados os grids **integrais** de Linear Regression e Hist
Gradient Boosting no experimento completo, e de Linear Regression na ablação.
Isso valida o modo não-smoke sem alegar a reprodução integral das 15 famílias.

O Hist Gradient Boosting do experimento completo coincidiu com a referência até
precisão numérica: RMSE de treino `2,72047858741865`, RMSE de holdout
`4,97748243549534` e RMSE real da busca-CV `4,65464843409264`; a maior diferença
absoluta entre as cinco métricas comparadas foi `8,9e-16`.

A Linear Regression completa é numericamente mal condicionada e já apresenta
na referência R² de holdout próximo de `-2,58 milhões`. A nova execução diferiu
em `2,8e-7 cm` no RMSE de holdout e `1,2e-4` nesse R², diferenças relativas muito
pequenas, mas não identidade bit a bit. Na ablação, a maior diferença entre as
cinco métricas da Linear Regression foi `7,9e-11`.

## Limite da afirmação de reprodução

Não foi executada nesta auditoria a grade completa das 15 famílias nos dois
experimentos: só o grid do LightGBM possui milhares de combinações antes das
cinco dobras. Portanto, os CSVs de `results/reference/` continuam sendo
referências históricas sanitizadas. Uma release deve executar os comandos
completos do README, conservar seus manifestos e registrar duração e hardware
antes de declarar reprodução integral.
