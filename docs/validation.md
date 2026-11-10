# Verificar a instalação e os resultados

Após instalar as dependências pelo README, execute na raiz:

```bash
python -m pip check
python -m pytest
python scripts/check_publication_safety.py
```

Os testes verificam esquema, identificadores pseudonimizados, hash do dataset,
seleção de variáveis, split 54/13, pré-processamento e registro dos modelos.

Em 10 de novembro de 2026, os oito testes passaram em um clone limpo, fora do
workspace da aplicação, com Windows 11, Python 3.12.10 e `requirements.txt`.
Os dois experimentos completaram os grids dos 15 modelos: 4.116 combinações
por experimento, cinco dobras por combinação. Os 30 pipelines foram
recarregados e suas métricas conferidas pelo avaliador. O SHAP foi gerado para
os cinco modelos selecionados de cada experimento, considerando os 67 eventos.

Os melhores RMSEs de holdout nessa execução foram `4,97748243549534 cm`
com movimentação e `5,59344463895469 cm` sem movimentação. Outras famílias
apresentaram diferenças em relação às métricas de referência; a execução
integral não implica identidade bit a bit de todos os resultados.

Para conferir suas próprias saídas, execute `scripts/evaluate_models.py`
depois do treino. O script compara os valores recalculados com `metrics.csv`,
usando tolerâncias relativas e absolutas registradas na saída do comando.
As particularidades de interpretação estão em [divergences.md](divergences.md).

## Verificação de segurança

`scripts/check_publication_safety.py` procura arquivos de credenciais,
chaves privadas, URIs de banco, tokens atribuídos e identificadores operacionais
no conteúdo local. Também valida o CSV pseudonimizado. A verificação não envia
os dados a serviços externos nem substitui uma inspeção do histórico Git.

Uma inspeção adicional do histórico remoto alcançável em 10 de novembro de
2026 cobriu três commits e 56 blobs, sem achados nos padrões verificados.
Isso não garante ausência de todo segredo possível ou de dados em referências
apagadas e outros armazenamentos externos.
