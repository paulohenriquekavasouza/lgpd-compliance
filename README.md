# lgpd-compliance

Skill para Claude que audita e corrige não conformidades com a **LGPD** (Lei 13.709/2018) e a regulamentação da **ANPD** em código, pastas, planilhas, documentos, contratos e processos, e gera relatórios prontos para a diretoria, o jurídico ou a fiscalização.

> O resultado é apoio técnico à conformidade e não substitui parecer jurídico de advogado habilitado.

## Uso

```
/lgpd-compliance analisar <alvo> [opções]
/lgpd-compliance corrigir <alvo> [opções]
```

| Modo | O que faz |
|---|---|
| `analisar` | Varre o alvo, analisa o contexto, registra os achados com fundamento legal e gera o relatório. Não altera nenhum arquivo do alvo. |
| `corrigir` | Reaproveita a análise anterior (ou analisa primeiro, se não houver) e aplica as correções: edita código e configuração, gera documentos ausentes, pergunta o que depende de decisão e lista as ações manuais. |

Sem modo, a skill infere pelo pedido; na dúvida, usa `analisar`.

| Opção | Descrição |
|---|---|
| `--reanalisar` | No `corrigir`, ignora a análise existente e faz uma nova. |
| `--severidade <critica\|alta\|media\|baixa>` | Considera apenas achados dessa severidade para cima. |
| `--ids A01,A04` | No `corrigir`, trata só esses achados. |
| `--saida <pasta>` | Pasta da análise (padrão: `<alvo>/.lgpd-compliance/`). |
| `--formato md,html` | Formatos do relatório. |

Exemplos:

```
/lgpd-compliance analisar ./api
/lgpd-compliance corrigir ./api --severidade alta
/lgpd-compliance corrigir "E:\Projetos\Sistema X" --ids A01,A03
/lgpd-compliance analisar politica-de-privacidade.docx
```

Também funciona por linguagem natural: "verifica se esse contrato com o fornecedor está adequado à LGPD", "corrige os problemas de privacidade deste projeto", "gera uma política de privacidade para o meu app".

### Pasta de análise

```
<alvo>/.lgpd-compliance/
├── analise.json      achados, status e histórico
├── scan.json         saída bruta da varredura
├── relatorio.md
├── relatorio.html
├── correcoes.md      registro do modo corrigir
├── documentos/       políticas, DPA, termos, RIPD etc. gerados
└── .gitignore        impede versionamento acidental
```

### O que o modo `corrigir` não faz sozinho

Ações irreversíveis ou externas ficam listadas em `correcoes.md` com passo a passo e só são executadas se você pedir explicitamente: rotação de credenciais, reescrita do histórico do git, exclusão de arquivos com dados reais, comunicação à ANPD ou a titulares, alterações em produção, commits e push.

## O que é analisado

- **Código e sistemas**: coleta excessiva, criptografia e hash de senhas, dados pessoais em logs, segredos expostos, rastreadores sem consentimento, transferência internacional, retenção, direitos do titular, controle de acesso, IA e decisões automatizadas, extensões e userscripts.
- **Documentos**: política de privacidade, termos de uso, termos de consentimento, DPA, contratos entre controladores, RH, formulários, cookies, marketing, editais, uso de imagem e biometria.
- **Processos**: maturidade, ROPA, planilhas, atendimento a titulares, incidentes (prazo de 3 dias úteis), fornecedores, encarregado, agentes de pequeno porte.
- **Base legal**: LGPD, Resoluções CD/ANPD nº 1/2021, 2/2022, 4/2023, 15/2024, 18/2024 e 19/2024, guias da ANPD, legislação correlata e prazos de retenção.

O scanner valida CPF, CNPJ, PIS e cartões por dígito verificador e lê .docx, .xlsx, .pptx, .odt e .pdf. Valores encontrados são mascarados na saída.

## Instalação

### Claude Code — via marketplace

Depois de publicar este diretório como repositório no GitHub (`<usuario>/<repositorio>`):

```
/plugin marketplace add <usuario>/<repositorio>
/plugin install lgpd-compliance@lgpd-compliance
```

### Claude Code — manual

Copie `skills/lgpd-compliance` para:

- Global: `~/.claude/skills/lgpd-compliance` (Windows: `%USERPROFILE%\.claude\skills\lgpd-compliance`)
- Por projeto: `<projeto>/.claude/skills/lgpd-compliance`

### Claude.ai / Claude Desktop

Gere o pacote compactando a pasta `skills/lgpd-compliance` em `.zip` (ou use o `.skill` das releases) e faça upload em **Configurações → Capacidades → Skills**.

## Requisitos

- Python 3.8+ (`python3`, `python` ou `py`).
- Opcional para PDF: `pypdf` (`pip install pypdf`) ou `pdftotext` (poppler-utils).

## Scripts

Podem ser usados sem o Claude:

```bash
python3 skills/lgpd-compliance/scripts/scan_pii.py <pasta> --format md
python3 skills/lgpd-compliance/scripts/scan_pii.py <pasta> --format json --output scan.json
python3 skills/lgpd-compliance/scripts/scan_pii.py --dump-text contrato.docx
python3 skills/lgpd-compliance/scripts/gerar_relatorio.py scan.json --output relatorio --format md,html
python3 skills/lgpd-compliance/scripts/estado.py verificar <pasta>
```

## Estrutura

```
.claude-plugin/
├── plugin.json
└── marketplace.json
skills/lgpd-compliance/
├── SKILL.md
├── references/      base legal, código, documentos, processos, relatórios
├── scripts/         scan_pii.py, gerar_relatorio.py, estado.py
└── assets/modelos/  política, DPA, consentimento, cookies, resposta a titular, incidente, RIPD, LIA, ROPA
```

## Licença

MIT — ver [LICENSE](LICENSE).
