# Relatórios e entregáveis

Tipos de relatório, quando usar cada um, estrutura e o schema de achados aceito por `scripts/gerar_relatorio.py`.

## Sumário

1. Escolha do relatório
2. Relatório de diagnóstico (completo)
3. Sumário executivo
4. Plano de ação (5W2H)
5. Matriz de risco
6. Parecer sobre documento
7. Checklist de conformidade
8. Relatório de varredura técnica
9. Documentos regulatórios (ROPA, RIPD, LIA, incidente, resposta a titular)
10. Indicadores para acompanhamento
11. Schema JSON de achados
12. Uso do script gerar_relatorio.py
13. Formatos de saída

---

## 1. Escolha do relatório

| Público / necessidade | Relatório |
|---|---|
| Diretoria, sócios, conselho | Sumário executivo (1–2 páginas) + matriz de risco |
| Jurídico, compliance, encarregado | Diagnóstico completo + parecer sobre documentos |
| TI, desenvolvimento | Relatório de varredura técnica + achados com patch |
| Gestão do projeto de adequação | Plano de ação 5W2H + indicadores |
| ANPD, auditoria externa, cliente B2B | ROPA, RIPD, LIA, registro de incidentes, evidências |
| Titular | Resposta a requisição (linguagem simples) |

Se o usuário não especificar, gere o diagnóstico completo, que já contém sumário, matriz e plano de ação, e ofereça os demais.

## 2. Relatório de diagnóstico (completo)

1. **Capa/metadados**: título, organização, escopo, data, responsável pela análise, versão, classificação de confidencialidade ("Confidencial — contém informações sobre vulnerabilidades").
2. **Sumário executivo**: situação geral, indicador de conformidade, principais riscos (3 a 5), ações prioritárias.
3. **Escopo e metodologia**: o que foi analisado, o que ficou fora, fontes (arquivos, entrevistas, varredura automatizada), limitações.
4. **Contexto do tratamento**: papel do agente, categorias de titulares e dados, finalidades, sistemas, terceiros.
5. **Resumo por severidade e por domínio** (governança, transparência, bases legais, direitos, segurança, terceiros, retenção, crianças/sensíveis).
6. **Matriz de risco**.
7. **Achados detalhados**: um bloco por achado com os campos do schema.
8. **Pontos positivos**: o que já está adequado (dá equilíbrio e orienta o que preservar).
9. **Plano de ação** priorizado.
10. **Anexos**: saída do scanner, checklists, minutas, glossário.
11. **Aviso**: apoio técnico, não substitui parecer jurídico.

## 3. Sumário executivo

No máximo duas páginas, sem jargão técnico:
- Uma frase com a conclusão ("O sistema X apresenta 2 exposições críticas que exigem ação imediata e lacunas documentais que podem ser resolvidas em 90 dias").
- Indicador de conformidade e distribuição por severidade.
- Até 5 riscos principais traduzidos em impacto de negócio (sanção da ANPD — até 2% do faturamento, limitada a R$ 50 milhões por infração —, ações judiciais, dano reputacional, perda de contratos B2B, bloqueio de dados).
- Decisões necessárias da gestão (orçamento, indicação de encarregado, escolha de fornecedor).
- Próximos passos com prazos.

## 4. Plano de ação (5W2H)

| ID | O quê | Por quê (achado/artigo) | Onde | Quem | Quando | Como | Quanto (esforço) | Status |
|---|---|---|---|---|---|---|---|---|

Prioridade: severidade × facilidade. Ganhos rápidos de alta severidade primeiro. Prazos sugeridos por severidade: crítica — imediato (até 7 dias); alta — 30 dias; média — 90 dias; baixa — 180 dias.

## 5. Matriz de risco

Probabilidade (1 a 5) × impacto (1 a 5). Score = P × I.

- 15 a 25: crítico
- 10 a 14: alto
- 5 a 9: médio
- 1 a 4: baixo

Impacto considera titulares (dano material, moral, discriminação, fraude) e organização (sanção, judicialização, reputação). Probabilidade considera exposição, histórico, controles existentes.

Apresente como tabela 5×5 com os IDs dos achados nas células. O script gera essa tabela automaticamente quando os achados têm `probabilidade` e `impacto`; sem eles, estima a partir da severidade.

## 6. Parecer sobre documento

Ver formato em `references/documentos-juridicos.md`, seção 15.

## 7. Checklist de conformidade

Tabela por domínio com status (atende, parcial, não atende, N/A), evidência e referência ao achado. Útil para acompanhamento contínuo e para responder questionários de clientes B2B.

## 8. Relatório de varredura técnica

Gerado a partir da saída do scanner, após revisão de falsos positivos:
- Resumo por categoria e severidade.
- Ocorrências por arquivo (caminho, linha, categoria, trecho mascarado).
- Falsos positivos descartados e motivo (dá rastreabilidade).
- Correções aplicadas ou propostas, com referência ao commit/patch.

## 9. Documentos regulatórios

Modelos em `assets/modelos/`:
- `ropa.csv` — Registro das Operações de Tratamento.
- `ripd.md` — Relatório de Impacto à Proteção de Dados.
- `teste-legitimo-interesse.md` — LIA.
- `comunicacao-incidente.md` — comunicação à ANPD, aos titulares e registro interno.
- `resposta-titular.md` — resposta a requisições.

Preencha com os dados reais do contexto; marque `[PREENCHER: ...]` o que faltar.

## 10. Indicadores para acompanhamento

- Percentual de achados resolvidos por severidade.
- Atividades de tratamento mapeadas no ROPA / total estimado.
- Fornecedores com DPA / fornecedores que tratam dados.
- Requisições de titulares respondidas no prazo.
- Tempo médio entre detecção e comunicação de incidentes.
- Colaboradores treinados nos últimos 12 meses.
- Sistemas com política de retenção implementada.

## 11. Schema JSON de achados

```json
{
  "metadados": {
    "titulo": "Diagnóstico de Conformidade com a LGPD",
    "organizacao": "Empresa Exemplo Ltda.",
    "escopo": "Repositório api-clientes e política de privacidade do site",
    "data": "2026-10-07",
    "responsavel": "Equipe de Privacidade",
    "papel_agente": "controlador",
    "versao": "1.0",
    "confidencialidade": "Confidencial"
  },
  "resumo_executivo": "Texto livre.",
  "metodologia": "Texto livre.",
  "achados": [
    {
      "id": "A01",
      "titulo": "CPF gravado em logs de produção",
      "dominio": "seguranca",
      "categoria": "pii_em_log",
      "severidade": "alta",
      "probabilidade": 4,
      "impacto": 4,
      "artigos": ["art. 6º, III", "art. 46"],
      "arquivo": "src/services/pagamento.ts",
      "linha": 88,
      "local": "src/services/pagamento.ts:88",
      "evidencia": "logger.info(`pagamento ${cliente.cpf}`)",
      "descricao": "O CPF completo do cliente é registrado a cada transação.",
      "recomendacao": "Remover o CPF do log ou registrar apenas identificador interno.",
      "correcao": "Antes: logger.info(`pagamento ${cliente.cpf}`)\nDepois: logger.info(`pagamento ${cliente.id}`)",
      "tipo_correcao": "automatica",
      "prazo": "30 dias",
      "responsavel": "Engenharia",
      "status": "aberto",
      "hash_arquivo": "preenchido por estado.py selar",
      "historico": [{"data": "2026-10-07 10:00", "status": "aberto", "nota": "análise registrada"}]
    }
  ],
  "pontos_positivos": ["Senhas armazenadas com bcrypt."],
  "proximos_passos": ["Indicar encarregado e publicar contato."]
}
```

Campos obrigatórios por achado: `titulo` e `severidade`. Para que o modo `corrigir` funcione bem, preencha também `arquivo` (relativo ao alvo), `linha`, `correcao` e `tipo_correcao`.

- `severidade`: `critica`, `alta`, `media`, `baixa`, `info`.
- `dominio`: `governanca`, `transparencia`, `bases_legais`, `direitos_titular`, `seguranca`, `terceiros`, `transferencia_internacional`, `retencao`, `sensiveis_criancas`, `documentacao`.
- `tipo_correcao`: `automatica`, `documento`, `decisao`, `manual` (definições no SKILL.md, seção 4).
- `status`: `aberto`, `em_andamento`, `resolvido`, `requer_decisao`, `manual`, `nao_aplicado`, `aceito`.
- `hash_arquivo`, `historico` e `metadados.raiz`/`data_analise`/`versao_skill` são gravados por `scripts/estado.py` — não preencha à mão.

## 12. Uso do script gerar_relatorio.py

```bash
python3 scripts/gerar_relatorio.py achados.json --output relatorio --format md,html
python3 scripts/gerar_relatorio.py scan.json --output varredura --format md --titulo "Varredura técnica" --organizacao "Empresa X"
```

- Aceita o schema acima ou a saída JSON de `scan_pii.py` (converte automaticamente, agrupando ocorrências por categoria e arquivo).
- Gera: metadados, sumário, indicador de conformidade, distribuição por severidade, status e domínio, matriz de risco, achados detalhados ordenados por severidade, plano de ação com tipo de correção, histórico de correções, pontos positivos, próximos passos e aviso.
- O indicador de conformidade é heurístico (100 menos penalidades por severidade dos achados abertos) — apresente-o como referência interna, não como métrica oficial.
- O HTML é autocontido (sem dependências externas), com tema claro e escuro e pronto para impressão em PDF pelo navegador.

## 13. Formatos de saída

- **Markdown**: padrão; versionável; bom para repositórios.
- **HTML**: para compartilhar e imprimir em PDF.
- **Word (.docx)**, **Excel (.xlsx)**, **PDF**: use as skills correspondentes se estiverem disponíveis — Excel é especialmente útil para ROPA, plano de ação e checklist.
- Nomeie arquivos com data: `relatorio-lgpd-2026-10-07.html`.
- Relatórios contêm informações sobre vulnerabilidades — recomende armazenamento com acesso restrito e não versionar em repositório público.
