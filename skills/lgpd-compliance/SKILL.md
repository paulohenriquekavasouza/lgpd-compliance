---
name: lgpd-compliance
description: Auditoria e adequação à LGPD e à ANPD em dois modos — "analisar" (diagnóstico e relatório, sem alterar nada) e "corrigir" (aplica as correções propostas, reaproveitando a análise anterior se existir). Funciona com código, pastas, sistemas, bancos, planilhas, políticas de privacidade, termos, contratos, DPAs, formulários, cookies e processos; aponta violações com fundamento legal e gera relatórios, plano de ação, ROPA, RIPD, LIA, comunicação de incidente e resposta a titular. Use sempre que o usuário mencionar LGPD, ANPD, privacidade, proteção de dados, dados pessoais ou sensíveis, consentimento, encarregado/DPO, cookies, vazamento, direitos do titular, adequação ou contrato com operador, mesmo sem dizer "LGPD", como "posso guardar CPF assim?" ou "corrige os problemas de privacidade desse projeto".
license: MIT
metadata:
  version: "1.1.0"
  idioma: pt-BR
---

# LGPD Compliance

Analisa qualquer artefato em busca de não conformidades com a Lei Geral de Proteção de Dados Pessoais (Lei 13.709/2018) e com a regulamentação da ANPD, documenta o resultado e, quando solicitado, aplica as correções.

Três entregas se complementam: **diagnóstico fundamentado** (evidência concreta e dispositivo violado em cada achado), **correção acionável** (código corrigido, cláusula reescrita, documento que faltava) e **relatório utilizável** (apresentável à diretoria, ao jurídico ou à ANPD).

`<skill-dir>` nos comandos abaixo é o diretório base desta skill, informado quando ela é carregada. Use `python3`; no Windows, se não existir, use `python` ou `py`.

## 1. Interpretar os argumentos

Formato: `/lgpd-compliance [modo] [alvo] [opções]`

| Modo | Sinônimos aceitos | Efeito |
|---|---|---|
| `analisar` | analise, análise, auditar, auditoria, analyze, audit | Diagnóstico + relatório. Não altera o alvo. |
| `corrigir` | corrija, corrigir, adequar, aplicar, fix | Usa a análise existente (ou analisa primeiro) e aplica as correções. |

- **Alvo**: caminho de pasta ou arquivo (aceite caminhos com espaços, entre aspas ou não, e caminhos do Windows como `E:\Projeto X`), URL ou texto/documento colado na conversa. Sem alvo: use o diretório de trabalho atual e diga isso ao usuário.
- **Sem modo explícito**: infira pela linguagem ("analisa", "verifica", "está ok?" → analisar; "corrige", "ajusta", "adequa", "aplica" → corrigir). Na dúvida, use `analisar` — é o modo que não altera nada.
- **Opções**:
  - `--reanalisar` — no modo corrigir, ignora a análise existente e faz uma nova.
  - `--severidade <critica|alta|media|baixa>` — considera apenas achados dessa severidade para cima (padrão: todos, exceto informativos, no modo corrigir).
  - `--ids A01,A04` — no modo corrigir, trata apenas esses achados.
  - `--saida <pasta>` — onde gravar análise e relatórios (padrão abaixo).
  - `--formato md,html` — formatos do relatório (padrão: `md,html`).

Se o alvo não estiver acessível neste ambiente (ex.: caminho local do usuário numa sessão em nuvem), diga isso e ofereça alternativas: rodar os scripts localmente e enviar `scan.json`, ou indicar um repositório acessível.

## 2. Pasta de análise

A análise é persistida para que o modo `corrigir` possa reaproveitá-la e para manter histórico.

- Padrão: `<alvo>/.lgpd-compliance/` (se o alvo for um arquivo, a pasta dele). Se não houver permissão de escrita ou o alvo for texto da conversa, use uma pasta de trabalho acessível ao usuário e informe o caminho.
- Conteúdo:
  - `analise.json` — achados no schema de `references/relatorios.md`, seção 11, com os campos de controle descritos na seção 4 abaixo.
  - `scan.json` — saída bruta do scanner.
  - `relatorio.md` e `relatorio.html`.
  - `correcoes.md` — registro do que foi corrigido (modo corrigir).
  - `documentos/` — documentos gerados (políticas, DPA, termos, RIPD etc.).
- O script `estado.py selar` cria um `.gitignore` dentro dessa pasta para que relatórios com informações de vulnerabilidade não sejam versionados por acidente.

Comandos de estado:

```bash
python3 <skill-dir>/scripts/estado.py verificar <alvo> [--saida <pasta>]
python3 <skill-dir>/scripts/estado.py selar <pasta-analise>/analise.json --raiz <alvo>
python3 <skill-dir>/scripts/estado.py pendentes <pasta-analise>/analise.json [--severidade alta] [--ids A01,A02]
python3 <skill-dir>/scripts/estado.py marcar <pasta-analise>/analise.json --id A01 --status resolvido --nota "..." --raiz <alvo>
```

`verificar` informa se há análise, sua data, totais por status e quais achados estão **desatualizados** (o arquivo citado mudou ou sumiu desde a análise).

## 3. Modo `analisar`

Não modifique nenhum arquivo do alvo. Só escreva na pasta de análise.

1. **Escopo.** Identifique o objeto, o papel do agente (controlador, operador, cocontrolador), setor, porte (Res. CD/ANPD nº 2/2022), público (crianças?), dados sensíveis e transferência internacional. Infira do material o que puder; pergunte só o que mudar a análise e não for inferível. Pedido amplo ("analisa minha empresa") → proponha roteiro em etapas.
2. **Varredura.** Para pastas e arquivos:
   ```bash
   python3 <skill-dir>/scripts/scan_pii.py <alvo> --format json --output <pasta-analise>/scan.json
   ```
   Opções: `--exclude <glob>` (repetível), `--min-severity media`, `--max-size-mb 20`, `--show-values` (só se o usuário pedir — a saída costuma ir para relatórios compartilhados). O scanner valida CPF/CNPJ/PIS/cartão por dígito verificador e detecta campos sensíveis, PII em logs, segredos, rastreadores, armazenamento inseguro e cláusulas abusivas, inclusive em .docx, .xlsx, .pptx, .odt e .pdf (`--dump-text` extrai o texto).
3. **Análise contextual.** O scanner é ponto de partida: gera falsos positivos e não enxerga finalidade, base legal, transparência ou contratos. Abra os arquivos relevantes, confirme cada ocorrência e procure o que só a leitura revela. Carregue a referência do tipo de artefato:

   | Artefato | Referência |
   |---|---|
   | Código, APIs, bancos, infraestrutura, front-end, apps, scripts de navegador | `references/codigo-e-sistemas.md` |
   | Política de privacidade, termos, contratos, DPA, consentimento, formulários, cookies, marketing, RH | `references/documentos-juridicos.md` |
   | Processos, governança, planilhas, inventário, titulares, incidentes, fornecedores | `references/processos-e-governanca.md` |
   | Artigos, bases legais, prazos, sanções, resoluções, legislação correlata | `references/base-legal.md` |

   Consulte `base-legal.md` sempre que citar artigo ou prazo — um dispositivo errado compromete a credibilidade do relatório inteiro. Analise pela ótica dos princípios do art. 6º: muitas violações reais são de necessidade (coleta excessiva) ou finalidade (uso diferente do informado), não de uma regra isolada.
4. **Registrar achados** em `analise.json` (seção 4). Cada achado precisa ter a correção descrita de forma concreta o suficiente para que o modo `corrigir` a aplique depois sem reanalisar: arquivo, linha, trecho atual, mudança proposta.
5. **Selar** a análise (`estado.py selar`) para gravar os hashes dos arquivos citados.
6. **Relatório.** Leia `references/relatorios.md` e gere:
   ```bash
   python3 <skill-dir>/scripts/gerar_relatorio.py <pasta-analise>/analise.json --output <pasta-analise>/relatorio --format md,html
   ```
   Para Word, Excel ou PDF, use as skills correspondentes se existirem.
7. **Resposta ao usuário**: resumo objetivo (indicador, contagem por severidade, principais riscos), caminho dos arquivos gerados e o comando para corrigir: `/lgpd-compliance corrigir <alvo>`.

## 4. Achados — campos e classificação

Campos (schema completo em `references/relatorios.md`, seção 11):

- `id`, `titulo`, `severidade`, `dominio`, `artigos`, `descricao`, `evidencia` (com dados pessoais mascarados), `recomendacao`, `prazo`, `responsavel` (área).
- `arquivo` (caminho relativo ao alvo, quando houver) e `linha` — usados para detectar se a análise ficou desatualizada.
- `correcao` — o patch ou texto proposto (antes → depois).
- `tipo_correcao`:
  - `automatica` — alteração em arquivo do alvo que o agente pode aplicar com segurança (código, configuração, texto de documento editável).
  - `documento` — documento novo a gerar a partir de `assets/modelos/` (política, DPA, termo, aviso de cookies, RIPD, LIA, ROPA, resposta a titular, comunicação de incidente).
  - `decisao` — depende de escolha de negócio ou jurídica (base legal, prazo de retenção, manter ou remover funcionalidade).
  - `manual` — exige ação fora do alcance ou irreversível: rotacionar credenciais, reescrever histórico do git, configurar nuvem, assinar contrato, comunicar a ANPD, treinar equipe.
- `status`: `aberto`, `em_andamento`, `resolvido`, `requer_decisao`, `manual`, `nao_aplicado`, `aceito` (risco aceito pelo usuário).

Severidade:

- **Crítica**: exposição atual de dados pessoais (dados reais em repositório, segredo em código, dado sensível sem proteção), tratamento sem base legal possível, dados de crianças sem salvaguarda, incidente não comunicado.
- **Alta**: violação direta de dispositivo expresso com muitos titulares ou dados sensíveis (consentimento inválido como única base, ausência de política, transferência internacional sem mecanismo, sem canal para titulares, PII em logs de produção).
- **Média**: lacunas de documentação ou controle (sem ROPA, retenção indefinida, contrato de operador incompleto, cookies sem consentimento).
- **Baixa**: redação, boas práticas, hardening.
- **Informativa**: observação ou ponto positivo.

Ajuste ao contexto (sensíveis, crianças, volume, exposição pública agravam). Separe **violação** (dispositivo descumprido), **risco** e **boa prática** — misturá-los infla o relatório.

## 5. Modo `corrigir`

O pedido de correção autoriza alterar os arquivos do alvo. Não autoriza ações irreversíveis ou externas — essas continuam exigindo confirmação explícita.

1. **Obter a análise.**
   - Rode `estado.py verificar`. Se existir análise e não houver `--reanalisar`, reutilize-a e informe a data dela.
   - Achados desatualizados: abra o arquivo, confirme se o problema persiste e atualize `linha`, `evidencia` e `correcao` (ou marque `resolvido` se já foi corrigido por outra via).
   - Sem análise (ou com `--reanalisar`): execute o modo `analisar` inteiro e siga para o passo 2 sem parar.
2. **Preparar.** Se o alvo for repositório git, verifique `git status`. Havendo alterações não commitadas, avise antes de editar, para que o usuário consiga distinguir as mudanças da skill. Não faça commit, push nem crie branch, a menos que o usuário peça.
3. **Planejar.** `estado.py pendentes` lista os achados abertos agrupados por `tipo_correcao`, filtrados por `--severidade` e `--ids`. Ordem de execução: críticos primeiro; dentro da mesma severidade, `automatica` antes de `documento`.
4. **Aplicar `automatica`.** Para cada achado:
   - Releia o trecho atual antes de editar; aplique a correção seguindo o estilo do projeto (padrões em `references/codigo-e-sistemas.md`).
   - Correções que exigem nova dependência, mudança de schema de banco ou migração de dados: crie o código e a migração, mas não execute migrações contra bancos reais.
   - Documentos existentes (política, contrato, termo): não sobrescreva o original quando ele não for texto editável versionado; gere versão revisada ao lado (`<nome>.revisado.md` ou `.docx` via skill de docx) com a tabela `Texto atual | Texto proposto | Fundamento`.
   - Marque com `estado.py marcar --status resolvido --nota "<o que foi feito>"`.
5. **Gerar `documento`.** A partir de `assets/modelos/`, preenchido com o que se sabe do contexto, salvo em `<pasta-analise>/documentos/`. Marque `[PREENCHER: ...]` o que faltar e nunca invente dados da organização (CNPJ, endereço, nome do encarregado). Marque como `resolvido` com nota indicando os campos pendentes de preenchimento.
6. **Tratar `decisao`.** Não decida silenciosamente. Reúna todas as decisões e apresente-as de uma vez, com opções, prós e contras e uma recomendação (use a ferramenta de perguntas ao usuário, se disponível). Aplique o que for decidido; o que ficar sem resposta recebe `requer_decisao`.
7. **Registrar `manual`.** Não execute. Escreva o passo a passo em `correcoes.md` e marque `manual`. Inclui obrigatoriamente: rotação de credenciais expostas, reescrita de histórico do git (`git filter-repo`/BFG) e force push, exclusão de arquivos com dados reais, comunicação à ANPD ou a titulares, alterações em ambientes de produção. Se o usuário pedir explicitamente uma dessas ações, explique o impacto e só então execute.
8. **Validar.** Rode as verificações do projeto que existirem e forem rápidas (build, lint, testes — ex.: `dotnet build`, `npm test`, `pytest`). Se uma correção quebrar o build e não puder ser ajustada dentro do escopo, reverta-a e marque `nao_aplicado` com o motivo. Rode o scanner de novo e compare com o `scan.json` anterior.
9. **Registrar e relatar.**
   - Atualize `correcoes.md`: data; achados resolvidos e arquivos alterados; documentos gerados; decisões tomadas; pendências manuais com passo a passo; itens não aplicados e motivo.
   - Regenere o relatório (`gerar_relatorio.py`) — ele mostra status e histórico de cada achado.
   - Responda com: o que foi corrigido, o que ficou pendente e por quê, ações manuais necessárias em ordem de prioridade, caminho dos arquivos.

Alvos que não são pastas (documento único, texto colado): `corrigir` entrega a versão revisada do documento como novo arquivo, mais o redline.

## 6. Outros usos

Os modos cobrem a maioria dos pedidos. Ajuste a profundidade quando o pedido for:

- **Pergunta pontual** ("posso logar o e-mail?") — resposta direta com fundamento e correção; não crie pasta de análise nem relatório, a menos que pedido.
- **Criação de documento** (política, DPA, termo, cookies, RIPD, LIA, ROPA) — a partir dos modelos, adaptado ao contexto.
- **Incidente** — avaliar risco ou dano relevante, prazo de 3 dias úteis (Res. CD/ANPD nº 15/2024), minutas de comunicação à ANPD e aos titulares, contenção e registro (`assets/modelos/comunicacao-incidente.md`).
- **Requisição de titular** — direito exercido (art. 18), prazo (art. 19), minuta de resposta (`assets/modelos/resposta-titular.md`).
- **Fornecedor/operador** — questionário de due diligence e análise do contrato.
- **Privacy by design** — revisão de especificação ou arquitetura antes da implementação.
- **LGPD x GDPR** — divergências quando o projeto atende os dois públicos.

## 7. Conduta

- Mascare dados pessoais em respostas e relatórios; não copie dados reais para arquivos novos sem necessidade; recomende eliminar cópias de análise quando não forem mais úteis.
- Seja específico: "o campo `cpf` é gravado em texto claro em `models/user.py:42`" é útil; "verifique a segurança" não é.
- Quando a lei for omissa ou a ANPD não tiver regulamentado o tema, diga isso e indique a interpretação mais conservadora.
- Considere legislação correlata que determine retenção ou tratamento (Marco Civil, CLT, tributária, CDC, normas setoriais) — `references/base-legal.md`.
- Normas da ANPD mudam. Com acesso à web, confirme pontos decisivos em gov.br/anpd e cite a data da consulta.
- Inclua em todo relatório e no fechamento uma linha informando que o resultado é apoio técnico à conformidade e não substitui parecer jurídico de advogado habilitado. Uma vez, sem repetir a cada resposta.
