# Divergências, ressalvas e decisões de preservação

## Como ler este documento

O manuscrito descreve a intenção científica; o código e os artefatos privados mostram o comportamento executado. Quando as fontes divergem, este repositório não altera silenciosamente o experimento nem ajusta números para fazê-los coincidir. As referências históricas permanecem identificadas como tal, e as métricas tecnicamente distintas recebem nomes distintos.

As constatações abaixo se referem ao lote privado `2026-06-01_20-44`, associado às tabelas do manuscrito, e ao código auditado em 10 de agosto de 2026.

## 1. O “CV RMSE” publicado é o RMSE do holdout

### Manuscrito

O texto afirma que o `GridSearchCV` com cinco dobras selecionou as configurações e que o menor “CV RMSE” determinou o ranqueamento dos modelos. Nas tabelas, “CV RMSE” e “RMSE de teste” são idênticos para todos os candidatos.

### Implementação e artefatos

A busca em grade de cinco dobras foi realmente executada sobre os 54 eventos de treino, com scorer de RMSE negativo. Entretanto:

1. `group_column` foi definido como `None`;
2. por isso, a rotina complementar `GroupKFold` não foi executada e `group_cv_summary_metrics` ficou nulo;
3. ao construir `comparison_metrics`, o serviço substituiu `group_cv_rmse` ausente pelo RMSE disponível do holdout;
4. os scripts de relatório exportaram esse campo fallback com o rótulo “Group CV RMSE”;
5. o ranqueamento entre famílias usou esse valor, portanto usou o holdout.

O diagnóstico serializado registra `test_metrics_source = "holdout"`. No exemplo principal:

| Métrica do Hist Gradient Boosting | Valor |
|---|---:|
| RMSE do holdout | 4,977482 cm |
| “Group CV RMSE” legado | 4,977482 cm |
| RMSE médio real da melhor configuração no `GridSearchCV` | 4,654648 cm |

Consequentemente, a afirmação de que o Hist Gradient Boosting foi o melhor por CV não é sustentada pelo `cv_results_`: no experimento completo, o menor `search_cv_rmse` recuperado foi o do Kernel Ridge, 3,046175 cm, enquanto o Hist Gradient Boosting foi o melhor no holdout. Na ablação, o menor `search_cv_rmse` foi o do Bagging, 4,398007 cm, enquanto o LightGBM foi o melhor no holdout.

### Tratamento público

Os arquivos em `results/reference/` preservam:

- `legacy_reported_cv_rmse`: o valor publicado, igual ao holdout;
- `test_rmse`: o RMSE do holdout com nome correto;
- `search_cv_rmse`: `-max(cv_results_["mean_test_score"])`, isto é, a média de validação da configuração escolhida.

Uma nova execução deve mostrar as duas métricas e nunca chamar o fallback de validação cruzada. Os números do manuscrito não foram reescritos retroativamente.

## 2. O holdout participou do ranqueamento entre famílias

O conjunto foi separado em 54 linhas de treino e 13 de teste antes da busca. Os hiperparâmetros de cada família foram escolhidos dentro do treino, mas a comparação final entre famílias foi ordenada pelo RMSE do holdout devido ao fallback acima. Isso reutiliza o conjunto chamado de “teste” para seleção do melhor candidato global e torna sua métrica otimista como estimativa final não tocada.

Uma avaliação futura deve reservar um teste verdadeiramente final ou empregar validação externa/nested CV. O modo de reprodução histórica mantém a ordem do artigo; o relatório público também oferece a ordem por `search_cv_rmse` para auditoria.

## 3. A divisão não foi temporal nem agrupada por piquete

O artigo informa 80%/20% e `random_state = 42`. O código:

1. ordena as 67 linhas por término, início e identificador do evento;
2. embaralha índices com `random.Random(42)`;
3. toma os primeiros `floor(67 × 0,2) = 13` índices como teste;
4. usa os 54 restantes como treino.

Não houve separação cronológica nem bloqueio por `paddock_id`. Eventos do mesmo piquete podem aparecer em treino e teste. O inteiro `cv=5` passado ao `GridSearchCV` de regressão corresponde ao `KFold` padrão sem embaralhamento; ele não representa `GroupKFold`.

## 4. Disponibilidade temporal das features

O manuscrito descreve a permanência de informações “observáveis ou planejáveis” para o intervalo futuro. O construtor efetivo, porém, produz somente o snapshot no fim do evento e agrega registros observados até esse fim.

Permanecem no experimento completo:

- clima observado durante o intervalo;
- entradas e saídas ocorridas no intervalo;
- pesos associados a essas movimentações;
- tempos de permanência calculados sobre todo o evento;
- uso observado de piquetes adicionais;
- ocupação ponderada por todo o intervalo;
- `finished_at` e `duration_seconds` observados.

Essas colunas não contêm a altura final explícita, mas não estariam disponíveis numa previsão estritamente feita no início, a menos que fossem substituídas por planos ou previsões registrados antes da decisão. O resultado deve ser descrito como experimento retrospectivo no nível do evento. Uma avaliação prospectiva exige um timestamp de decisão e corte estrito de disponibilidade.

Há ainda uma particularidade na busca do peso inicial: ela permite consultar pesos até o fim do evento, e a marcação de “futuro” compara com esse fim. Um peso posterior ao início pode, portanto, entrar sem ser marcado como inferido.

## 5. Clima observado versus previsão meteorológica

O código da construção calcula temperaturas, umidade e chuva a partir de observações históricas no período real. O manuscrito reconhece, na seção de limitações, que uma utilização futura precisaria substituí-las por previsões.

O repositório público preserva os valores analíticos históricos para reproduzir o experimento, mas não deve apresentar esse desempenho como validação de uma cadeia operacional com forecast. Essa cadeia ainda precisa ser testada com previsões arquivadas no instante da decisão.

## 6. Seeds parcialmente declaradas ou omitidas

Seeds efetivamente aplicadas:

| Componente | Seed |
|---|---:|
| split treino/teste | 42 |
| target encoder interno | 42 |
| Random Forest | 42 |
| Bagging externo | 42 |
| LightGBM | 42 |
| amostragem SHAP | 0 |

Ressalvas:

- As specs de Decision Tree e Extra Trees declaravam `random_state = 42`, e a tabela do manuscrito reproduz essa declaração. A factory não encaminhou o parâmetro ao estimador e ele não integrou `cv_results_["params"]`; o ajuste efetivo permaneceu com `random_state=None`.
- Gradient Boosting, Hist Gradient Boosting e MLP também foram construídos sem `random_state` explícito.
- O `KFold` externo do `GridSearchCV` não embaralha e, portanto, não usa seed.
- O estimador-base do Bagging é criado sem seed explícita, embora o Bagging externo com seed possa propagar seeds aos clones internos conforme a implementação do scikit-learn.

Assim, repetir o pipeline pode produzir variação em parte dos candidatos. O código público preserva as omissões para equivalência histórica e as documenta; adicionar seeds seria um novo experimento.

## 7. Early stopping do LightGBM não é rastreável como descrito

O artefato histórico e o manuscrito registram `early_stopping_rounds: [10, 50]`. A versão de código auditada passou apenas `[10]` na construção da spec. Em ambos os desenhos:

- `early_stopping_rounds` é removido do espaço enviado ao `GridSearchCV`, logo 10 e 50 não são comparados pela busca;
- o serviço seleciona somente o primeiro valor para tentar o ajuste final;
- quando existe holdout, ele é passado como `eval_set`, o que faria o teste influenciar o número de iterações caso a chamada fosse aceita;
- o serviço tenta combinações de argumentos e, se falharem, refaz o `fit` sem argumentos, podendo desabilitar silenciosamente o early stopping.

Os JSONs sanitizáveis não registram `best_iteration_` nem qual tentativa de `fit` venceu, e o pipeline serializado privado não foi publicado. Portanto, não é possível confirmar apenas com os materiais públicos se o modelo histórico efetivamente aplicou early stopping. Esta é uma pendência de rastreabilidade, não uma autorização para supor que ele ocorreu.

## 8. Snapshots previstos no código, mas não usados no dataset final

O construtor contém helpers para snapshots `before`, `during` e `end`, com progressos configuráveis. Contudo, `build_pasturages` sobrescreve essa possibilidade com uma única linha final (`event`, `1.0`, cutoff no fim). O manuscrito descreve eventos, não múltiplos snapshots, e os resultados usam 67 linhas de evento. O repositório científico preserva esse desenho efetivo e não expande artificialmente a amostra.

## 9. A seleção dos modelos explicados por SHAP também seguiu o fallback

O manuscrito informa análise dos cinco candidatos com menor CV RMSE. O script privado selecionou os cinco menores valores do campo chamado `group_cv_rmse`; como esse campo era o fallback do holdout, os cinco modelos explicados foram os cinco melhores no holdout.

Além disso, o serviço SHAP recebeu o dataframe analítico completo, não somente as 13 linhas do holdout. Com 67 linhas e `sample_size=1000`, todas foram explicadas. O background foi formado pelas primeiras até 100 linhas transformadas, e a seed de amostragem foi 0. A importância global, portanto, resume comportamento do modelo sobre treino e teste combinados; não é uma explicação exclusiva do conjunto de teste.

## 10. Semântica de `extra_paddocks_used_avg_seconds`

O nome e a interpretação sugerem tempo médio em piquetes adicionais. O código soma a sobreposição de cada bovino em todos os piquetes durante o intervalo e tira a média entre bovinos. A coluna foi preservada porque mudar a fórmula alteraria o experimento; seu nome/descrição precisa de confirmação do autor antes da publicação final.

## 11. Evolução de 72 para 77 colunas

Um CSV legado em `assets/data/` possui 72 colunas. O DTO e o artefato final de 1º de junho possuem 77, acrescentando:

`temp_avg_c_known`, `temp_max_c_known`, `temp_min_c_known`, `humidity_avg_pct_known` e `precip_total_mm_known`.

O repositório público adota o esquema final de 77 colunas, que corresponde ao lote dos resultados do manuscrito. O CSV legado não foi copiado.

## 12. Licenças da distribuição e autorização das fontes

Na auditoria original, não foi encontrado arquivo de licença nos repositórios da API, do aplicativo ou no repositório científico original. A árvore atual da distribuição científica contém [LICENSE](../LICENSE), com Apache 2.0 para o código, e [LICENSE-DATA](../LICENSE-DATA), com CC BY 4.0 para o dataset analítico. Portanto, a descrição anterior de ausência de licença nesta distribuição estava desatualizada.

Esses arquivos não licenciam automaticamente os projetos privados nem comprovam a autorização de seus titulares para a extração. A confirmação dos direitos sobre o código extraído, o crédito dos dados e a aprovação de sua publicação permanecem no [checklist](publication_checklist.md). O escopo e as condições resumidas estão na seção [Licença do README](../README.md#licença).

## 13. Escopo do frontend

O Flutter serviu à coleta e exportação de alturas, pesagens e movimentações. Nenhum arquivo Flutter foi copiado: telas, armazenamento local, autenticação, mapas e fluxo operacional não são necessários para executar o pipeline sobre o dataset analítico. A relação com a coleta é descrita em documentação, evitando publicar o produto FarmNote.

## Pendências para revisão do autor

1. Corrigir ou explicar no manuscrito o uso do termo “CV RMSE” e o ranqueamento baseado no holdout.
2. Decidir se as conclusões devem ser refeitas usando `search_cv_rmse`, nested CV ou teste externo.
3. Definir formalmente o instante de previsão e a disponibilidade de cada feature.
4. Confirmar o comportamento efetivo do early stopping a partir do pipeline/log privado, se ainda disponível.
5. Confirmar a semântica de `extra_paddocks_used_avg_seconds`.
6. Confirmar com os titulares a aplicação das licenças presentes, completar as informações de atribuição e obter autorização explícita para publicar o dataset analítico pseudonimizado.
