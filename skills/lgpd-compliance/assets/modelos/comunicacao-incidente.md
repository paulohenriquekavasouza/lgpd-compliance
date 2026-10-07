# Incidente de segurança com dados pessoais — kit de resposta

Base: art. 48 da LGPD e Resolução CD/ANPD nº 15/2024. Prazo: **3 dias úteis** a partir do conhecimento de que o incidente afetou dados pessoais (em dobro para agente de pequeno porte). Comunicar mesmo sem todas as informações e complementar depois.

---

## 1. Avaliação de risco ou dano relevante

| Pergunta | Resposta |
|---|---|
| Data/hora da ocorrência (estimada) | [PREENCHER] |
| Data/hora do conhecimento | [PREENCHER] |
| Natureza (confidencialidade, integridade, disponibilidade) | [PREENCHER] |
| Causa (ataque, erro humano, falha de sistema, terceiro) | [PREENCHER] |
| Categorias de dados afetados | [PREENCHER] |
| Quantidade de titulares (estimada) | [PREENCHER] |
| Envolve dados sensíveis? | [S/N] |
| Envolve dados de crianças, adolescentes ou idosos? | [S/N] |
| Envolve dados financeiros? | [S/N] |
| Envolve dados de autenticação (senhas, tokens)? | [S/N] |
| Envolve dados protegidos por sigilo legal, judicial ou profissional? | [S/N] |
| Larga escala? | [S/N] |
| Pode afetar significativamente interesses e direitos fundamentais dos titulares? | [S/N — justificar] |
| **Conclusão** | [Comunicável / Não comunicável — fundamentação] |

Regra: é comunicável quando pode afetar significativamente interesses e direitos fundamentais **e** atende a pelo menos um dos critérios acima.

---

## 2. Comunicação à ANPD (conteúdo para o formulário eletrônico)

1. **Agente de tratamento:** [PREENCHER: razão social, CNPJ, endereço, porte].
2. **Encarregado / notificante:** [PREENCHER].
3. **Descrição do incidente:** [PREENCHER: o que aconteceu, quando, como foi descoberto].
4. **Natureza e categorias de dados afetados:** [PREENCHER].
5. **Titulares afetados:** [PREENCHER: número e categorias — clientes, colaboradores, crianças etc.].
6. **Medidas técnicas e de segurança utilizadas antes do incidente:** [PREENCHER — ex. criptografia dos dados afetados reduz o risco].
7. **Riscos relacionados e possíveis impactos aos titulares:** [PREENCHER — ex. fraude, phishing, discriminação, exposição].
8. **Motivos da demora, se a comunicação não for imediata:** [PREENCHER].
9. **Medidas adotadas ou a adotar para reverter ou mitigar os efeitos:** [PREENCHER].
10. **Comunicação aos titulares:** [realizada em / prevista para / forma].

---

## 3. Comunicação aos titulares

Assunto: Aviso importante sobre seus dados pessoais

Olá, [PREENCHER: nome].

Em [PREENCHER: data], identificamos [PREENCHER: descrição simples do incidente]. Os dados envolvidos foram: [PREENCHER].

**O que isso pode significar para você:** [PREENCHER: riscos em linguagem simples].

**O que já fizemos:** [PREENCHER: contenção, correção, comunicação à ANPD].

**O que recomendamos que você faça:** [PREENCHER — ex. trocar a senha, ativar verificação em duas etapas, desconfiar de contatos pedindo dados ou pagamentos em nosso nome, acompanhar extratos].

Nunca pediremos sua senha por e-mail, telefone ou mensagem.

Para dúvidas, fale com nosso encarregado: [PREENCHER].

[PREENCHER: assinatura]

---

## 4. Registro interno do incidente (guardar por no mínimo 5 anos)

| Campo | Conteúdo |
|---|---|
| ID | [PREENCHER] |
| Datas (ocorrência, conhecimento, contenção, comunicações) | [PREENCHER] |
| Descrição e causa raiz | [PREENCHER] |
| Dados e titulares afetados | [PREENCHER] |
| Avaliação de risco (seção 1) e decisão de comunicar ou não | [PREENCHER] |
| Medidas de contenção e remediação | [PREENCHER] |
| Comunicações realizadas (ANPD, titulares, outros) | [PREENCHER] |
| Lições aprendidas e ações preventivas | [PREENCHER] |
| Responsável pelo registro | [PREENCHER] |

---

## 5. Checklist de contenção (primeiras horas)

- [ ] Acionar o encarregado e o comitê de resposta.
- [ ] Interromper a exposição (remover arquivo público, desativar endpoint, isolar máquina).
- [ ] Revogar e rotacionar credenciais comprometidas.
- [ ] Preservar evidências (logs, imagens, cópias) com cadeia de custódia.
- [ ] Identificar escopo: sistemas, dados, titulares, período.
- [ ] Acionar operadores/fornecedores envolvidos.
- [ ] Avaliar necessidade de boletim de ocorrência e comunicação a outros órgãos (BCB, ANS, ANATEL, CVM, conforme setor).
- [ ] Iniciar contagem do prazo de 3 dias úteis.
