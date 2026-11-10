# Origem e identificação dos materiais

O código científico foi extraído e adaptado do backend FarmNote, com base no
commit `ae569cea662263ae2cabc3d344bc77fc45bad182`. O aplicativo e a API
operacional completos não integram esta distribuição.

O dataset analítico e as métricas de referência correspondem ao lote
`2026-06-01_20-44`. Foram substituídos quatro identificadores no CSV e
preservados os demais valores e a ordem das linhas.

| Arquivo | Identificação |
|---|---|
| `data/pasturages_anonymized.csv` | 67 linhas e 77 colunas |
| SHA-256 do CSV | `c68e057437c380e8f6ef29e053d33f139f8f95df4448c6563b3d9c89130cfeed` |

O SHA-256 é uma impressão digital do conteúdo: permite verificar se o arquivo
usado é o mesmo. Para conferir no PowerShell:

```powershell
Get-FileHash data/pasturages_anonymized.csv -Algorithm SHA256
```

Cada treinamento grava esse hash em `manifest.json`. Use o mesmo CSV na
avaliação e no SHAP. O hash verifica identidade do arquivo; não certifica
qualidade científica, privacidade ou autorização de uso.
