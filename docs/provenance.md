# Proveniência e cadeia de custódia

## Snapshot auditado

Esta extração científica foi preparada em **10 de agosto de 2026** no workspace FarmNote. As fontes complementares foram:

| Fonte | Referência auditada | Uso |
|---|---|---|
| manuscrito | `FarmNote_Artigo_Revista_Scientia.docx`, SHA-256 `09d5f04d60672b1e019bdd2c47912ef63f70bd27ae0450fd6fa4c609ff403e18` | desenho metodológico, população, métricas e resultados apresentados |
| API/backend | branch `ml`, commit `ae569cea662263ae2cabc3d344bc77fc45bad182` | implementação efetiva da construção, seleção de features, pré-processamento, treino, avaliação e SHAP |
| aplicativo Flutter | branch `main`, commit `92a79658468014229136e9eeec8b3bd0fe85b373` | confirmação do papel de coleta/exportação; nenhum código transferido |
| artefatos privados | lote `2026-06-01_20-44` | 67 × 77, métricas históricas, `cv_results_`, parâmetros e diagnósticos do lote do manuscrito |

O commit identifica a base do código, mas não substitui o hash dos arquivos. No momento da auditoria, os cinco módulos científicos centrais abaixo não possuíam diff rastreado em relação ao commit. O script `overall_results_spreadsheet.py` tinha alteração local e, por isso, é identificado também por hash.

## Impressões digitais das fontes de código

Todos os caminhos desta seção são relativos ao repositório privado da API. Os arquivos não foram publicados integralmente.

| SHA-256 | Arquivo de origem |
|---|---|
| `b00f649efb51faa35b74cef500dc2ae5895b7cb9833de40d32d32173336d9953` | `app/modules/pasturage/domain/models/dtos/pasturage_dto.py` |
| `0ad9f7d4fae115c18b90d6fa0b019ff9c234a4c7f31ad0e7277e59e403ae1d52` | `app/modules/pasturage/domain/usecases/build_pasturages_usecase_impl.py` |
| `010ebef07c41c17eb9a015127f91d583ad525698f7b0797d0c5dba8db681bac3` | `app/modules/model/external/datasources/train_pasturage_model_datasource_impl.py` |
| `0edec7993a92d35984b27bba477a6127701b4615dc805d6a6614f3674cd93514` | `app/services/machine_learning/adapters/sklearn_machine_learning_service.py` |
| `fba62a6ce1ebeec82e624b6404c4d66c47a73073da4408f4e63ec2f3ae167cd5` | `app/services/interpretability/adapters/shap_interpretability_service.py` |
| `49c634c4b7c0ad53edf5f7b5dfeed52e279740c650e2c3514e3ec9a1db36e56a` | `scripts/export_training_dataset_csv.py` |
| `01b4d23d056e46a0b75fc89edf26b17e62b46aa664aea6d4fba6854cc7ddf6a4` | `scripts/overall_results_spreadsheet.py` — snapshot local auditado |
| `d925e00b44254b7c9b85176c8ac2170dd183b63e36c889d3c620cc9184a230f7` | `scripts/moviment_features_positions_spreadsheet.py` |

## Linhagem dos dados

```text
coleta no aplicativo FarmNote
        │
        ├── medições de altura
        ├── pesagens
        ├── entradas/saídas e permanência
        └── cadastro de piquetes e áreas
        ▼
exportação/importação operacional
        ▼
API privada + registros meteorológicos históricos
        ▼
construtor de eventos `pasturages`
        ▼
filtro de ≥ 3 eventos por piquete
        ▼
dataset analítico privado (67 linhas × 77 colunas)
        ▼
revisão de autorização e risco de reidentificação
        ▼
pseudonimização de 4 identificadores, sem mapa publicado
        ▼
`data/pasturages_anonymized.csv`
        ▼
pipeline científico autônomo
```

O arquivo privado não foi copiado para o repositório público. A etapa entre “dataset analítico privado” e “CSV público” só pode ser concluída após aprovação humana.

Um candidato pseudonimizado foi gerado na árvore de trabalho e validado estruturalmente em 10 de agosto de 2026: 67 linhas, 77 colunas, quatro padrões de pseudônimo válidos, IDs de linha/evento únicos, uma origem e cinco piquetes. Seu SHA-256 é `c68e057437c380e8f6ef29e053d33f139f8f95df4448c6563b3d9c89130cfeed`. “Candidato” não significa que o titular autorizou sua distribuição; se a revisão humana reprovar o risco residual, ele deve ser retirado da release.

## Correspondência entre fonte e componente público

| Fonte privada | Extração/adaptação pública | Elemento preservado |
|---|---|---|
| `PasturageDTO` | `src/farmnote_grass_height/data/schema.py` | 77 campos, aliases, tipos e ordem de modelagem |
| `_build_feature_names` | `src/farmnote_grass_height/data/features.py` | lista de vazamento/proxies e regra da ablação |
| exportador do dataset | `scripts/anonymize_dataset.py` e `src/farmnote_grass_height/data/loader.py` | formato CSV, ordenação e validação; acesso ao banco removido |
| specs criadas pelo datasource | `src/farmnote_grass_height/models/grids.py` | quinze famílias e espaços de busca efetivos |
| factory do serviço de ML | `src/farmnote_grass_height/models/registry.py` | estimadores, parâmetros fixos e seeds efetivamente encaminhadas ou omitidas |
| preprocessor do serviço de ML | `src/farmnote_grass_height/preprocessing/` | imputação, padronização, flags, datas, booleanos e target encoding |
| split do serviço de ML | `src/farmnote_grass_height/training/split.py` | ordenação prévia, `random.Random(42)` e 80%/20% |
| treino e tuning | `src/farmnote_grass_height/training/` | `GridSearchCV`, cinco dobras, scorer RMSE e artefatos |
| cálculo de métricas | `src/farmnote_grass_height/evaluation/` | R², MSE, RMSE, MAE e ranqueamentos explícitos |
| serviço de interpretabilidade | `src/farmnote_grass_height/interpretation/` | SHAP no espaço transformado e agregação por feature bruta |
| planilhas privadas do lote | `results/reference/` | somente métricas sanitizadas; IDs e predições por evento removidos |
| construtor privado | `docs/dataset_construction.md` | descrição auditável, sem infraestrutura operacional |

## Natureza das adaptações

As adaptações públicas são estruturais:

- remoção de injeção de dependência, DTOs base, repositórios, datas proprietárias e persistência MongoDB;
- entrada direta por CSV validado;
- substituição dos modelos de dataframe privados por estruturas pandas/listas aceitas pelo scikit-learn;
- centralização de grids e seleção de features;
- separação entre RMSE real da busca e campo legado rotulado como CV;
- gravação local de artefatos sem IDs internos ou serviços externos;
- documentação explícita das divergências em vez de correção silenciosa.

As fórmulas e decisões que determinam o experimento histórico foram preservadas quando identificáveis. Alterações científicas desejáveis — split temporal, nested CV, forecast meteorológico real ou novas seeds — devem ser implementadas como protocolos novos, não como substituições não registradas.

## Materiais deliberadamente não publicados

- aplicativo Flutter, inclusive telas, autenticação, mapas e banco local;
- API completa, rotas, injeção de dependência e módulos administrativos;
- banco MongoDB, dumps, GridFS e configurações de produção;
- exportações XLSX e datasets com UUIDs;
- IDs de usuários, propriedades, bovinos, modelos e artefatos;
- coordenadas e geometrias;
- predições por evento vinculáveis aos registros privados;
- metadados SHAP que contêm categorias/identificadores originais;
- pipelines serializados privados;
- credenciais, tokens, URLs privadas, arquivos `.env` e configurações meteorológicas.

## Limites desta proveniência

1. O candidato a dataset possui hash registrado, mas sua inclusão na release ainda depende da aprovação do arquivo pseudonimizado.
2. O lote histórico armazena o pipeline fora dos JSONs de relatório. Sem esse artefato privado, não foi possível confirmar `best_iteration_`/early stopping do LightGBM.
3. Não há licença definida nos repositórios de origem; a autorização de código e dados continua pendente.
4. O hash do manuscrito identifica a cópia analisada, não uma versão editorial futura.

Quando `pasturages_anonymized.csv` for aprovado, registre em documento de release, sem mapa de IDs: hash SHA-256 público, número de linhas/colunas, data da revisão, responsável pela autorização e commit do código usado na reprodução.
