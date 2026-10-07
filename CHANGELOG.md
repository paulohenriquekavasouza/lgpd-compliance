# Changelog

## 1.2.0 — 2026-10-07

- Análise de respostas de endpoints: inventário por stack (ASP.NET Core, Express, NestJS, Spring, Django REST, FastAPI, Flask, Laravel, Rails, Go, GraphQL, gRPC), sinais de exposição, severidade sugerida e correções (`references/codigo-e-sistemas.md`, seção 7).
- Exemplos de correção para ASP.NET Core, Node.js, Spring, Django REST/FastAPI e Laravel: DTOs por caso de uso, projeção, máscara, filtro por tenant, exclusão de credenciais, erros genéricos e `Cache-Control: no-store`.
- Scanner detecta: entidade devolvida diretamente pelo endpoint, credenciais em classes de saída, detalhes de erro expostos, PII em rotas e query strings, Swagger/introspecção habilitados e CORS permissivo.
- Scanner: detecção de arquivos de dados pessoais restrita a extensões de dados (evita marcar controllers e models pelo nome).

## 1.1.0 — 2026-10-07

- Modos `analisar` e `corrigir` com argumentos (`--reanalisar`, `--severidade`, `--ids`, `--saida`, `--formato`).
- Persistência da análise em `<alvo>/.lgpd-compliance/` (análise, varredura, relatórios, registro de correções e documentos gerados).
- Novo `scripts/estado.py`: verifica análise existente, detecta achados desatualizados por hash de arquivo, lista pendências por tipo de correção e registra histórico de status.
- Achados com `tipo_correcao` (automática, documento, decisão, manual) e novos status.
- Relatório com distribuição por status, tipo de correção e histórico de correções.
- Scanner: caminhos relativos ao alvo, saída UTF-8 no Windows, ignora a pasta de análise.
- Empacotamento como plugin do Claude Code com marketplace.

## 1.0.0 — 2026-10-07

- Versão inicial: scanner de dados pessoais, gerador de relatórios, referências legais, checklists e modelos de documentos.
