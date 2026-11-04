# Construção do dataset analítico

## Escopo deste documento

Este documento registra como a coleção analítica `pasturages` foi construída na API do FarmNote. Ele foi derivado da leitura do manuscrito e da implementação efetiva, principalmente de `PasturageDTO` e `BuildPasturagesUsecaseImpl`. O código operacional completo não foi transferido porque depende de entidades, repositórios, MongoDB, geometria da propriedade e serviços externos que não são necessários ao treinamento público.

O repositório científico começa, por decisão de desacoplamento e privacidade, no CSV analítico pseudonimizado. Esta descrição permite auditar sua origem; ela não pretende reconstruir a API privada.

## População e unidade de análise

O manuscrito informa coleta entre 20 de abril de 2025 e 8 de fevereiro de 2026. O conjunto bruto chegou a duas áreas, sete piquetes, 82 bovinos, 78 medições de altura, 1.278 pesagens e 915 movimentações. Após o critério de ao menos três eventos válidos por piquete, o conjunto do experimento ficou restrito à fazenda principal e reuniu:

- 67 eventos de pastejo;
- 5 piquetes;
- 61 bovinos;
- 73 medições de altura;
- 1.148 pesagens;
- 782 movimentações.

A unidade de análise é o **evento de pastejo**, definido como o intervalo entre duas medições consecutivas de altura no mesmo piquete:

```text
medição inicial ───────── registros do intervalo ───────── medição final
       X inicial                                        alvo y
```

`start_grass_height_avg_cm` é a altura da primeira medição e `end_grass_height_avg_cm` é a altura da segunda e o alvo de regressão.

## Fontes operacionais consultadas pelo construtor

A rotina privada integra os seguintes registros:

| Fonte operacional | Uso analítico |
|---|---|
| piquetes e fazendas | vínculo da área, identificador e área cadastral |
| logs de tamanho do piquete | área vigente no início do evento |
| logs de altura | limites consecutivos do evento, alturas inicial/final e alturas de piquetes extras |
| logs bovino–piquete | presença, entradas, saídas, permanência e uso de áreas adicionais |
| logs de peso | peso agregado no início, fim, entradas e saídas |
| desenho cartográfico da fazenda | centro usado para consulta meteorológica |
| registros meteorológicos | temperatura, umidade e precipitação no intervalo |

As coordenadas, geometrias, IDs de bovinos e registros elementares não aparecem no dataset público.

## Algoritmo identificado no código

### 1. Normalização das alturas

Os logs são agrupados por piquete e ordenados no tempo. Quando há mais de um registro no mesmo instante, permanece um único registro, priorizando nesta ordem:

1. registro que possui altura;
2. maior `updated_at`;
3. maior `created_at`;
4. maior identificador textual, como desempate.

Piquetes com menos de duas medições não geram eventos. Pares sem datas ou com fim menor ou igual ao início também são descartados.

### 2. Formação dos eventos

Para cada par consecutivo:

- `started_at` recebe a data da primeira medição;
- `finished_at` recebe a data da segunda;
- `duration_seconds` é a diferença entre ambas;
- o identificador operacional é formado por piquete, timestamp inicial e timestamp final;
- as duas alturas são copiadas diretamente, com flags de inferência iguais a `False`.

Embora o DTO possua infraestrutura para snapshots, a execução usada no artigo força uma única linha por evento:

```text
snapshot_type = "event"
snapshot_progress = 1.0
snapshot_cutoff_at = finished_at
```

Essas três colunas são posteriormente excluídas do treinamento.

### 3. Área do piquete

O construtor procura o último log de área com data menor ou igual ao início. Na ausência dele, usa a área cadastrada no piquete. A unidade é metro quadrado.

### 4. Clima

Para cada fazenda, o sistema privado obtém o centro geográfico e consulta os registros meteorológicos entre a primeira e a última medição de altura. Para um evento, entram registros cuja **data civil** esteja entre as datas inicial e final, inclusive.

São calculados:

- média, máximo e mínimo da temperatura;
- média da umidade;
- soma da chuva;
- flags de disponibilidade para temperatura, umidade e precipitação.

Quando não há observação, o construtor grava `0.0` e uma flag `*_known = False`. As três flags de temperatura usam a mesma condição: existência de ao menos uma temperatura.

Importante: a execução histórica usou **clima observado** no intervalo. O manuscrito reconhece que um cenário prospectivo teria de usar previsões meteorológicas.

### 5. Presença e movimentação

Um bovino é considerado presente em `t` quando sua entrada ocorreu até `t` e sua saída é nula ou posterior a `t`. Entradas e saídas no intervalo usam a janela aberta à esquerda e fechada à direita: `(started_at, finished_at]`.

São formados quatro conjuntos de bovinos:

- presentes no início;
- presentes no fim;
- que entraram durante o evento;
- que saíram durante o evento.

As contagens de entrada e saída usam bovinos distintos. Os pesos de entrada e saída, contudo, são somados por registro de movimentação encontrado; registros duplicados do mesmo bovino poderiam, em princípio, ser somados mais de uma vez. Não foi encontrada no código uma deduplicação adicional nessa etapa.

### 6. Associação de pesos

Para cada bovino e instante de interesse, a rotina segue esta ordem:

1. peso exatamente no instante;
2. peso mais próximo, quando a distância é de até 24 horas;
3. interpolação linear entre o peso anterior e o posterior;
4. último peso anterior, se não houver posterior;
5. primeiro peso posterior, se não houver anterior;
6. ausente, se não houver registro utilizável.

A idade registrada é a distância temporal absoluta em horas. Interpolação é marcada como inferida. Um peso com distância superior a 24 horas também é marcado como inferido. Para o estado final, a busca admite até 24 horas depois do término e marca essa utilização como futura.

Há uma ressalva importante para o estado inicial: a chamada usa o fim do evento como `cutoff`, de modo que um peso posterior ao início, mas anterior ao fim, pode ser escolhido. A função só marca como “futuro” um registro posterior ao `cutoff`, e não posterior ao instante inicial. Assim, `start_bovine_total_weight_kg_inferred` não representa perfeitamente a disponibilidade do peso no começo do evento.

Os totais somam apenas pesos encontrados, enquanto a contagem inclui todos os bovinos do conjunto. A fração inferida usa como denominador a quantidade de pesos efetivamente usados.

### 7. Permanência e piquetes adicionais

Para cada intervalo bovino–piquete, calcula-se a sobreposição em segundos com o evento. A sobreposição no piquete-alvo alimenta:

- permanência média dos quatro grupos de bovinos;
- número médio de bovinos ponderado pelo tempo;
- peso médio presente ponderado pelo tempo;
- versões divididas pela área.

Qualquer outro piquete com sobreposição no mesmo evento é considerado adicional. Para esses piquetes são consolidados quantidade, área total e altura no início e no fim. A altura de um piquete extra pode usar medição próxima, interpolação ou carregamento do valor de uma extremidade.

`extra_paddocks_used_avg_seconds` merece revisão de nomenclatura: a implementação calcula a média da sobreposição total de cada bovino em **todos** os piquetes, e não exclusivamente nos piquetes extras.

### 8. Valores padrão e indicadores de disponibilidade

Diversas colunas numéricas ausentes são convertidas em `0.0` antes da persistência. Flags de inferência ausentes viram `False`; flags `*_known` ausentes também viram `False`. Os offsets de entrada/saída e algumas permanências podem continuar nulos quando não há evento ou grupo correspondente, acompanhados da flag de disponibilidade.

Essa convenção significa que zero e ausência podem ter semânticas diferentes; as flags de qualidade devem permanecer no dataset.

### 9. Critério mínimo por piquete

O treinamento consulta a coleção `pasturages` com `pasturage_count_min_per_paddock = 3`. O filtro reduziu 70 eventos candidatos a 67 e eliminou piquetes de baixa representatividade. Ele não é um split agrupado: depois desse filtro, as linhas são divididas aleatoriamente entre treino e teste.

## Ordenação e exportação

Antes do treinamento, as linhas são ordenadas por:

1. `finished_at`;
2. `started_at`;
3. `pasturage_event_id`.

O exportador privado normaliza cada registro novamente pelo DTO e grava todas as 77 colunas. Os arquivos “com” e “sem” movimentação contêm o mesmo dataset; a diferença entre os experimentos é a seleção das features em código.

## Disponibilidade temporal e interpretação correta

O código efetivo constrói cada linha somente ao final do evento. A remoção de atributos finais explícitos evita vazamento direto do alvo, mas não cria automaticamente um cenário de previsão no início. Permanecem, no experimento completo, valores derivados de clima observado, entradas, saídas, permanência e ocupação de todo o intervalo. `finished_at` e `duration_seconds` também são observados no dataset histórico.

Portanto, os resultados reproduzem uma associação retrospectiva no nível do evento. Para afirmar desempenho prospectivo no começo do evento seria necessário definir um instante de decisão e substituir ou limitar cada atributo à informação disponível nesse instante:

- data de fim e duração planejadas, não observadas;
- previsão meteorológica arquivada, não clima realizado;
- plano de movimentação/ocupação conhecido naquele momento;
- pesos com corte estrito no instante da previsão.

Essa diferença é registrada em [`divergences.md`](divergences.md) e não foi corrigida silenciosamente no artefato científico.

## Fallback público e privacidade

Não é seguro publicar automaticamente o arquivo privado encontrado no workspace. Ele contém UUIDs e identificadores relacionáveis à operação. O repositório público aceita `data/pasturages_anonymized.csv`, produzido após:

1. revisão de autorização e minimização;
2. pseudonimização estável de `id`, `user_id`, `paddock_id` e `pasturage_event_id`;
3. exclusão de qualquer mapa reversível;
4. revisão de datas e combinações que possam reidentificar a propriedade;
5. varredura de segredos e metadados privados;
6. validação do esquema, das 67 linhas esperadas e do alvo.

Se o arquivo não for autorizado, o repositório permanece como documentação e implementação do pipeline, sem alegar reprodução numérica.
