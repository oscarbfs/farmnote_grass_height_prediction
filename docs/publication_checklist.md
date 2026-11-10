# Checklist de publicação científica

Este checklist é um gate de release. Itens marcados como **bloqueador** devem ser resolvidos antes de tornar o repositório ou o dataset públicos.

## 1. Autorização e licença

Os arquivos presentes são [LICENSE](../LICENSE) (Apache 2.0, código científico) e [LICENSE-DATA](../LICENSE-DATA) (CC BY 4.0, dataset analítico). Sua existência foi verificada; os itens abaixo registram aprovações e verificações que não podem ser presumidas apenas a partir desses arquivos.

- [ ] **BLOQUEADOR — titularidade do código:** o titular confirmou por escrito que pode autorizar a distribuição do código extraído sob Apache 2.0, inclusive das adaptações das fontes privadas.
- [ ] As obrigações das licenças de scikit-learn, LightGBM, SHAP e demais dependências foram revisadas conforme a forma de distribuição.
- [ ] O arquivo `LICENSE` corresponde à decisão do titular; os avisos de copyright e atribuição aplicáveis foram incluídos e preservados.
- [ ] O escopo da licença da documentação e das métricas em `results/reference/` foi confirmado e documentado pelo titular.
- [ ] **BLOQUEADOR — licença dos dados:** o titular confirmou que pode disponibilizar `data/pasturages_anonymized.csv` sob CC BY 4.0 e que `LICENSE-DATA` corresponde à sua decisão.
- [ ] O crédito do dataset identifica o titular/autores conforme indicado por eles, a fonte, a licença e os avisos aplicáveis, sem expor identificadores operacionais.
- [ ] **BLOQUEADOR — dados:** existe autorização explícita para disponibilizar o dataset analítico pseudonimizado.
- [ ] A autorização é compatível com a CC BY 4.0, inclusive uso comercial, adaptação e caráter irrevogável dos direitos concedidos nos termos da licença; não há promessa de restringir usos já permitidos por ela.
- [ ] Foi confirmado que o consentimento/autorização não depende de publicar o aplicativo ou a API completos.
- [ ] Autoria, afiliações, citação sugerida e contato científico foram aprovados.

## 2. Minimização e pseudonimização do dataset

- [ ] A origem usada é o dataset **analítico**, nunca um dump, planilha bruta ou exportação operacional completa.
- [ ] O arquivo tem exatamente 67 linhas e 77 colunas, ou qualquer diferença foi investigada e documentada como nova versão.
- [ ] `id` contém somente pseudônimos `row_NN`.
- [ ] `user_id` contém somente pseudônimos `source_NN`.
- [ ] `paddock_id` contém somente pseudônimos `paddock_NN` e preserva a relação entre eventos do mesmo piquete.
- [ ] `pasturage_event_id` contém somente pseudônimos `event_NN`.
- [ ] Nenhum identificador operacional permanece embutido em valores, comentários, nomes de arquivos ou metadados.
- [ ] O mapa entre valores privados e pseudônimos não foi salvo no repositório, nos artefatos ou nos logs de CI.
- [ ] Não há nomes de pessoas, propriedades ou bovinos.
- [ ] Não há IDs de bovinos, usuários, propriedades, modelos, artefatos ou documentos externos.
- [ ] Não há coordenadas, endereços, polígonos, mapas ou geometrias.
- [ ] Não há observações livres que possam conter texto identificável.
- [ ] Datas exatas foram avaliadas como quase-identificadores.
- [ ] A combinação de datas, áreas dos piquetes, contagens e pesos foi avaliada por alguém que conhece a operação.
- [ ] Foi documentado por que preservar datas e valores científicos é necessário para sazonalidade e reprodução.
- [ ] A pessoa responsável concluiu que o risco residual de reidentificação é aceitável; caso contrário, o CSV não será publicado.

## 3. Integridade científica do dataset

- [ ] O cabeçalho e sua ordem coincidem com `src/farmnote_grass_height/data/schema.py`.
- [ ] Os tipos e unidades foram confrontados com `data/data_dictionary.md`.
- [ ] `id` e `pasturage_event_id` são únicos.
- [ ] `end_grass_height_avg_cm` não contém ausentes.
- [ ] Os valores de altura permanecem em centímetros, área em metros quadrados, peso em quilogramas e duração em segundos.
- [ ] Separador `;`, decimal `,`, UTF-8 e timestamps ISO 8601 foram preservados.
- [ ] Ausentes não foram convertidos inadvertidamente em strings como `"None"` ou `"nan"`.
- [ ] Flags booleanas são tokens aceitos pelo carregador.
- [ ] A pseudonimização não alterou ordem de linhas, valores científicos, ausentes ou ordem de colunas.
- [ ] O hash SHA-256 do arquivo público, a data e o responsável pela revisão foram registrados fora do mapa de IDs.
- [ ] O arquivo público foi aberto e revisado visualmente por amostragem sem acessar a origem durante a inspeção final.

## 4. Vazamento e disponibilidade temporal

- [ ] A lista de exclusão em `data/features.py` coincide com a lista auditada em `data/data_dictionary.md`.
- [ ] O alvo e os proxies finais são removidos antes do pré-processamento.
- [ ] O preprocessor é ajustado apenas em folds/treino.
- [ ] A ablação remove exatamente a regra por prefixos e `duration_seconds`, deixando 16 features.
- [ ] O relatório diferencia vazamento explícito do alvo de **risco de disponibilidade temporal**.
- [ ] O manuscrito/release não afirma previsão no início do evento sem explicar que clima, movimentações e permanência foram observados no intervalo histórico.
- [ ] Qualquer avaliação prospectiva futura usa forecast arquivado, planejamento e corte temporal estrito; ela é publicada como experimento novo.
- [ ] A ressalva sobre pesos posteriores ao início foi revisada.
- [ ] A semântica de `extra_paddocks_used_avg_seconds` foi confirmada ou permanece marcada para revisão.

## 5. Métricas e rastreabilidade do manuscrito

- [ ] **BLOQUEADOR editorial:** o autor revisou a divergência “CV RMSE = holdout RMSE”.
- [ ] Resultados históricos usam o nome `legacy_reported_cv_rmse`, não são apresentados como nova reprodução.
- [ ] `search_cv_rmse` é calculado a partir do melhor `mean_test_score` da busca, com inversão do sinal.
- [ ] O relatório deixa claro que o ranqueamento do manuscrito foi feito pelo holdout.
- [ ] O teste não é descrito como completamente independente após ter sido usado para escolher a melhor família.
- [ ] Split aleatório 54/13, seed 42 e ausência de agrupamento/ordenação temporal estão documentados.
- [ ] Os resultados de uma nova execução não foram arredondados ou alterados para coincidir com o artigo.
- [ ] Diferenças decorrentes de versões, seeds omitidas ou dataset foram quantificadas.
- [ ] Decision Tree, Extra Trees, Gradient Boosting, Hist Gradient Boosting e MLP não são apresentados como totalmente determinísticos.
- [ ] O estado efetivo do early stopping do LightGBM é tratado como não confirmado enquanto `best_iteration_`/pipeline histórico não estiver disponível.
- [ ] A análise SHAP informa que os 67 eventos foram explicados e que os cinco modelos foram escolhidos pelo ranking legado/holdout.

## 6. Escopo do código público

- [ ] Nenhum diretório do backend ou frontend foi copiado em massa.
- [ ] Nenhum arquivo Dart/Flutter foi incluído.
- [ ] Não há telas, autenticação, gerenciamento de usuários, mapas ou banco local do aplicativo.
- [ ] Não há rotas FastAPI, módulos administrativos ou injeção de dependência sem função científica.
- [ ] Não há driver/configuração MongoDB, GridFS, dump ou backup.
- [ ] Não há chamadas obrigatórias a serviços externos do FarmNote.
- [ ] Não há integração ou credencial meteorológica; o pipeline lê as colunas já consolidadas.
- [ ] Imports não apontam para `app.*` ou outros pacotes privados.
- [ ] O repositório executa quando copiado para fora do workspace FarmNote.
- [ ] Modelos serializados privados, caches, logs e artefatos intermediários não foram incluídos.
- [ ] Os CSVs em `results/reference/` contêm somente métricas agregadas sanitizadas.

## 7. Segredos e configurações

- [ ] Não há `.env` nem variantes, exceto um exemplo deliberadamente vazio caso seja realmente necessário.
- [ ] Não há arquivos de chave, certificado ou configuração móvel de serviços.
- [ ] Não há senha, segredo, token, chave de API, chave de acesso ou segredo de cliente atribuído em código, documentação, notebook, JSON ou log.
- [ ] Não há cabeçalho de autorização com credencial.
- [ ] Não há URI de banco MongoDB nem URL privada.
- [ ] Não há chave privada PEM.
- [ ] Comentários, histórico Git e mensagens de commit também foram verificados, não apenas a árvore atual.
- [ ] `git ls-files` foi revisado para datasets e binários inesperados.
- [ ] O verificador local terminou sem achados:

```bash
python scripts/check_publication_safety.py
```

O verificador é uma defesa auxiliar; ele não substitui revisão humana nem scanner de histórico/segredos da plataforma de hospedagem.

## 8. Ambiente limpo e execução

- [ ] Um ambiente virtual novo foi criado fora dos ambientes da API e do aplicativo.
- [ ] A instalação funcionou apenas com o manifesto público:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e .
```

- [ ] Os testes passaram:

```bash
python -m pytest
```

- [ ] O carregamento e a validação do dataset passaram.
- [ ] O experimento completo foi executado do início ao fim.
- [ ] O experimento sem movimentação/ocupação foi executado do início ao fim.
- [ ] Foram gerados relatórios de treino, holdout, busca em grade e parâmetros selecionados.
- [ ] A análise SHAP foi gerada para os modelos previstos pelo protocolo.
- [ ] Os caminhos funcionam a partir da raiz do repositório e não dependem de diretórios irmãos.
- [ ] A execução não acessou rede, banco privado ou arquivo fora do repositório, exceto o CSV explicitamente fornecido.
- [ ] Tempo, memória, sistema operacional e versão do Python foram anotados no relatório da reprodução.

## 9. Documentação e release

- [ ] README, dicionário e metodologia descrevem o mesmo alvo e a mesma unidade de análise.
- [ ] `docs/divergences.md` foi lido e aprovado pelo autor.
- [ ] `docs/provenance.md` aponta o manuscrito e os commits corretos.
- [ ] Os comandos documentados correspondem aos scripts existentes.
- [ ] Resultados de referência estão claramente separados de resultados reproduzidos.
- [ ] Ausência do dataset, se aplicável, é declarada sem alegar reprodução.
- [ ] Limitações de amostra, fazenda única, cinco piquetes, ausência de validação externa e variáveis agronômicas ausentes são mantidas.
- [ ] A release registra hash do dataset público, commit, dependências e seeds.
- [ ] O repositório foi revisado a partir de um clone limpo da versão candidata.
- [ ] O histórico remoto foi escaneado antes de tornar o repositório público.

## Aprovação final

| Papel | Nome | Data | Decisão |
|---|---|---|---|
| responsável pelos dados |  |  | pendente |
| autor responsável |  |  | pendente |
| revisão técnica |  |  | pendente |
| titular/licenciamento |  |  | pendente |

Sem essas aprovações, publique no máximo o código/documentação autorizados e mantenha o dataset ausente.
