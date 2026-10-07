# lgpd-compliance

Skill para Claude que audita e corrige não conformidades com a **LGPD** (Lei 13.709/2018) e a regulamentação da **ANPD** em código, pastas, planilhas, documentos, contratos e processos, e gera relatórios para a diretoria, o jurídico ou a fiscalização.

> O resultado é apoio técnico à conformidade e não substitui parecer jurídico de advogado habilitado.

## Sumário

- [Instalação](#instalação)
- [Uso](#uso)
- [O que é analisado](#o-que-é-analisado)
- [Scripts sem o Claude](#scripts-sem-o-claude)
- [Limitações](#limitações)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Instalação

Requisito: Python 3.8 ou superior (`python3`, `python` ou `py`). Para ler PDFs, instale também `pypdf` (`pip install pypdf`) ou `pdftotext` (poppler-utils).

### Claude Code (recomendado)

```
/plugin marketplace add paulohenriquekavasouza/lgpd-compliance
/plugin install lgpd-compliance@lgpd-compliance
```

Reinicie a sessão. A skill aparece como `/lgpd-compliance`.

Atualizar e remover:

```
/plugin marketplace update lgpd-compliance
/plugin uninstall lgpd-compliance@lgpd-compliance
```

### Claude Code (manual)

Clone o repositório e copie a pasta da skill para o diretório de skills.

Linux e macOS:

```bash
git clone https://github.com/paulohenriquekavasouza/lgpd-compliance.git
mkdir -p ~/.claude/skills
cp -r lgpd-compliance/skills/lgpd-compliance ~/.claude/skills/
```

Windows (PowerShell):

```powershell
git clone https://github.com/paulohenriquekavasouza/lgpd-compliance.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\lgpd-compliance\skills\lgpd-compliance" "$env:USERPROFILE\.claude\skills\"
```

Para usar só em um projeto, copie para `<projeto>/.claude/skills/lgpd-compliance`.

### Claude.ai e Claude Desktop

1. Baixe o repositório (**Code → Download ZIP**) e extraia.
2. Compacte a pasta `skills/lgpd-compliance` em um novo `.zip`, de forma que `lgpd-compliance/SKILL.md` fique na raiz do arquivo.
3. No Claude, abra **Configurações → Capacidades → Skills** e faça upload do `.zip`.

## Uso

```
/lgpd-compliance analisar <alvo> [opções]
/lgpd-compliance corrigir <alvo> [opções]
```

O alvo pode ser uma pasta, um arquivo (código, .docx, .xlsx, .pdf etc.) ou um texto colado na conversa. Sem alvo, a skill usa o diretório atual.

| Modo | O que faz |
|---|---|
| `analisar` | Varre o alvo, confirma as ocorrências lendo os arquivos, registra os achados com fundamento legal e gera o relatório. Não altera nenhum arquivo do alvo. |
| `corrigir` | Reaproveita a análise anterior (ou analisa primeiro, se não houver) e aplica as correções: edita código e configuração, gera documentos ausentes, pergunta o que depende de decisão de negócio e lista as ações manuais. |

Sem modo informado, a skill deduz pelo pedido; na dúvida, usa `analisar`.

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
/lgpd-compliance corrigir "D:\Projetos\Sistema X" --ids A01,A03
/lgpd-compliance analisar contratos/fornecedor-crm.docx
```

A skill também é acionada por linguagem natural, sem o comando: "esse contrato com o fornecedor está adequado à LGPD?", "corrige os problemas de privacidade deste projeto", "gera uma política de privacidade para o meu app", "tivemos um vazamento, o que fazer?".

### Fluxo do modo `corrigir`

1. Reutiliza a análise existente. Achados cujo arquivo mudou desde a análise são conferidos de novo.
2. Aplica as correções por tipo:

| Tipo | O que acontece |
|---|---|
| Automática | Edita código, configuração ou texto do alvo, seguindo o estilo do projeto. |
| Documento | Gera política, DPA, termo, aviso de cookies, RIPD, LIA ou ROPA em `.lgpd-compliance/documentos/`, marcando com `[PREENCHER]` o que não for conhecido. |
| Decisão | Reúne as escolhas de negócio (base legal, prazo de retenção etc.) e pergunta de uma vez, com recomendação. |
| Manual | Não executa; registra o passo a passo em `correcoes.md`. |

3. Roda build e testes do projeto, quando existirem, e desfaz a correção que quebrar algo.
4. Varre o alvo de novo e regenera o relatório com status e histórico de cada achado.

Ações irreversíveis ou externas só são executadas se você pedir explicitamente: rotação de credenciais, reescrita do histórico do git, exclusão de arquivos com dados reais, comunicação à ANPD ou a titulares, alterações em produção, commit e push.

### Pasta de análise

```
<alvo>/.lgpd-compliance/
├── analise.json      achados, status e histórico
├── scan.json         saída bruta da varredura
├── relatorio.md
├── relatorio.html    pronto para imprimir em PDF
├── correcoes.md      registro do modo corrigir
├── documentos/       documentos gerados
└── .gitignore        impede o versionamento acidental dos relatórios
```

Os relatórios descrevem vulnerabilidades. Guarde-os com acesso restrito.

## O que é analisado

- **Código e sistemas**: respostas de endpoints (entidades completas, campos desnecessários, credenciais, dados sensíveis sem máscara, dados de outros titulares por IDOR ou falta de filtro por tenant, detalhes de erro, PII na URL, cache), coleta excessiva, criptografia e hash de senhas, dados pessoais em logs, segredos expostos, rastreadores sem consentimento, transferência internacional, retenção, direitos do titular, controle de acesso, IA e decisões automatizadas, extensões e userscripts.
- **Documentos**: política de privacidade, termos de uso, termos de consentimento, DPA, contratos entre controladores, RH, formulários, cookies, marketing, editais, uso de imagem e biometria.
- **Processos**: maturidade, ROPA, planilhas, atendimento a titulares, incidentes (prazo de 3 dias úteis), fornecedores, encarregado, agentes de pequeno porte.
- **Base legal**: LGPD; Resoluções CD/ANPD nº 1/2021, 2/2022, 4/2023, 15/2024, 18/2024 e 19/2024; guias da ANPD; legislação correlata e prazos de retenção.

Relatórios disponíveis: diagnóstico completo, sumário executivo, plano de ação 5W2H, matriz de risco, checklist, varredura técnica, ROPA, RIPD, LIA, comunicação de incidente e resposta a titular.

## Scripts sem o Claude

O scanner e os geradores funcionam de forma independente:

```bash
python3 skills/lgpd-compliance/scripts/scan_pii.py <pasta> --format md
python3 skills/lgpd-compliance/scripts/scan_pii.py <pasta> --format json --output scan.json
python3 skills/lgpd-compliance/scripts/scan_pii.py --dump-text contrato.docx
python3 skills/lgpd-compliance/scripts/gerar_relatorio.py scan.json --output relatorio --format md,html
python3 skills/lgpd-compliance/scripts/estado.py verificar <pasta>
```

O scanner valida CPF, CNPJ, PIS e cartões por dígito verificador, detecta e-mail, telefone, CEP, RG, CNS, IP, campos sensíveis, dados de crianças, PII em logs, segredos, rastreadores, hash fraco, TLS desativado, entidades devolvidas direto por endpoints, credenciais em DTOs de resposta, erros detalhados expostos, PII em rotas, Swagger/GraphQL abertos, CORS permissivo e cláusulas abusivas, e lê .docx, .xlsx, .pptx, .odt e .pdf. Os valores encontrados são mascarados na saída; use `--show-values` apenas quando necessário.

## Limitações

- A varredura é baseada em padrões: gera falsos positivos e não comprova conformidade. A análise contextual feita pelo Claude é o que confirma ou descarta cada ocorrência.
- Normas da ANPD mudam com frequência. A base legal reflete a regulamentação conhecida até a versão publicada; confira pontos decisivos em [gov.br/anpd](https://www.gov.br/anpd).
- PDFs digitalizados (imagem) não são lidos sem OCR prévio.
- O conteúdo é voltado à legislação brasileira e escrito em português.

## Estrutura do repositório

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

## Contribuição

Issues e pull requests são bem-vindos, especialmente para:

- novas resoluções e guias da ANPD;
- padrões de detecção e redução de falsos positivos no scanner;
- modelos de documentos setoriais (saúde, educação, financeiro, setor público).

Ao alterar a skill, atualize a versão em `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` e no `SKILL.md`, e registre a mudança no [CHANGELOG](CHANGELOG.md).

## Licença

MIT — ver [LICENSE](LICENSE).
