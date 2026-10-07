# Processos, governança e operação

Para auditorias organizacionais, programas de adequação, planilhas e bases de dados, atendimento a titulares, incidentes e gestão de fornecedores.

## Sumário

1. Diagnóstico organizacional (questionário de maturidade)
2. Mapeamento de dados e ROPA
3. Planilhas, arquivos e bases avulsas
4. Atendimento aos direitos dos titulares
5. Resposta a incidentes de segurança
6. Gestão de fornecedores e operadores
7. RIPD — quando e como
8. Legítimo interesse — LIA
9. Encarregado e governança
10. Treinamento e cultura
11. Agentes de pequeno porte
12. Roteiro de adequação em fases

---

## 1. Diagnóstico organizacional

Use as perguntas abaixo quando a análise for da organização (não de um artefato). Faça-as em blocos, priorizando as que o usuário consegue responder rápido. Cada "não" vira um achado.

**Governança**
- Há encarregado indicado formalmente e divulgado publicamente? (art. 41; Res. 18/2024)
- Existe política interna de proteção de dados e de segurança da informação?
- Há programa de governança com responsável, orçamento e revisões periódicas? (art. 50)

**Inventário e bases legais**
- Existe inventário/ROPA de todas as atividades de tratamento? (art. 37)
- Cada atividade tem finalidade e base legal definidas? Dados sensíveis mapeados?
- Há tabela de temporalidade (retenção e descarte)?

**Transparência**
- Política de privacidade publicada, atualizada e coerente com a prática? (art. 9º)
- Avisos no ponto de coleta (formulários, recepção, câmeras)?

**Direitos dos titulares**
- Existe canal e procedimento para requisições, com prazos e registro? (arts. 18 e 19)

**Segurança**
- Controle de acesso por necessidade, MFA, criptografia, backup, gestão de vulnerabilidades, logs? (art. 46)
- Política de mesa limpa, descarte seguro de papel e mídias?

**Incidentes**
- Plano de resposta a incidentes, com papéis e prazos de 3 dias úteis? Registro de incidentes mantido por 5 anos? (art. 48; Res. 15/2024)

**Terceiros**
- Lista de fornecedores que tratam dados; contratos com cláusulas de proteção de dados; avaliação de segurança; transferências internacionais mapeadas? (arts. 33, 39)

**Riscos**
- RIPD para tratamentos de alto risco (sensíveis, larga escala, monitoramento, IA, crianças)? (art. 38)

**Pessoas**
- Treinamento periódico; termos de confidencialidade?

Resultado: nível de maturidade por domínio (inexistente, inicial, definido, gerenciado, otimizado) e plano de ação.

## 2. Mapeamento de dados e ROPA (art. 37)

Para cada **atividade de tratamento** (processo de negócio, não sistema), registre os campos do modelo `assets/modelos/ropa.csv`:

- Área responsável; nome do processo; descrição.
- Papel (controlador, operador, cocontrolador).
- Categorias de titulares (clientes, colaboradores, candidatos, fornecedores PF, visitantes, crianças).
- Categorias de dados; dados sensíveis (sim/não, quais).
- Finalidade; base legal (art. 7º ou 11); se legítimo interesse, referência ao LIA.
- Fonte dos dados (titular, terceiro, pública).
- Sistemas e locais de armazenamento (incluindo papel).
- Compartilhamentos (internos e externos, com finalidade).
- Transferência internacional (país, mecanismo).
- Prazo de retenção e fundamento; forma de descarte.
- Medidas de segurança.
- Riscos identificados e necessidade de RIPD.

Técnicas de levantamento: entrevistas por área com roteiro curto; análise de sistemas e integrações; varredura de pastas e drives com `scripts/scan_pii.py`; revisão de contratos de fornecedores.

Agente de pequeno porte pode usar o modelo simplificado de ROPA da ANPD (Res. 2/2022).

## 3. Planilhas, arquivos e bases avulsas

Planilhas são uma das maiores fontes de risco: circulam por e-mail, ficam em drives pessoais e não têm controle de acesso nem retenção.

Ao analisar planilhas (.xlsx, .csv, .ods) ou pastas de arquivos:
1. Rode o scanner e identifique colunas com dados pessoais e sensíveis.
2. Pergunte (ou infira) finalidade, quem acessa, onde está armazenada, há quanto tempo existe.
3. Avalie: colunas desnecessárias para a finalidade; dados sensíveis; cópias duplicadas; compartilhamento por link público; ausência de senha/criptografia em arquivos enviados externamente; dados antigos sem uso.

Correções típicas: remover colunas; pseudonimizar (substituir CPF por ID interno); migrar para sistema com controle de acesso; restringir compartilhamento; definir data de descarte; proteger exportações.

Quando o usuário pedir correção de uma planilha, gere uma **nova** versão minimizada/pseudonimizada e preserve o original para que ele decida o descarte — eliminar dados é irreversível.

## 4. Atendimento aos direitos dos titulares (arts. 18 a 20)

Procedimento:
1. **Recebimento** por canal informado na política (e-mail do encarregado, formulário, atendimento). Registrar data/hora — o prazo começa aí.
2. **Verificação de identidade** proporcional ao risco (não exigir mais dados do que o necessário; para representante, procuração).
3. **Classificação** do direito (art. 18, I a IX; art. 20).
4. **Localização** dos dados em todos os sistemas, backups, terceiros (usar o ROPA).
5. **Análise**: há impedimento (art. 16, obrigação legal; segredo comercial; dados de terceiros)? Se sim, fundamentar.
6. **Execução** (exportar, corrigir, eliminar, anonimizar, revogar) e comunicação aos terceiros com quem houve compartilhamento (art. 18, §6º).
7. **Resposta** ao titular — gratuita, clara:
   - confirmação/acesso simplificado: imediatamente; declaração completa: até 15 dias (art. 19);
   - demais direitos: sem prazo fixado em lei — adote 15 dias como padrão de boa prática, salvo regulamento posterior da ANPD.
8. **Registro** da requisição e da resposta (prestação de contas).

Modelo de resposta: `assets/modelos/resposta-titular.md`.

## 5. Resposta a incidentes de segurança (art. 48; Res. 15/2024)

Fluxo:

1. **Detecção e contenção imediata**: isolar sistemas, revogar credenciais, remover exposição, preservar evidências (logs, cópias forenses).
2. **Avaliação** (até ter elementos suficientes, sem atrasar o prazo):
   - Houve dados pessoais afetados? Quais categorias, quantos titulares?
   - Confidencialidade, integridade ou disponibilidade?
   - Critérios de **risco ou dano relevante** (Res. 15/2024): afeta significativamente interesses e direitos fundamentais **e** envolve ao menos um de — dados sensíveis; dados de crianças, adolescentes ou idosos; dados financeiros; dados de autenticação; dados protegidos por sigilo; larga escala.
3. **Comunicação** se risco ou dano relevante: à ANPD (formulário no site da ANPD) e aos titulares, em **3 dias úteis** do conhecimento de que dados pessoais foram afetados (prazo em dobro para agente de pequeno porte). Se não houver todas as informações, comunicar o que houver e complementar.
4. **Registro** do incidente, comunicado ou não, com fatos, efeitos, medidas e fundamentação da avaliação — guarda mínima de 5 anos.
5. **Remediação e lições aprendidas**: corrigir causa raiz, atualizar plano, treinar.

Se o operador sofrer o incidente, ele deve comunicar o controlador prontamente — o controlador é quem comunica à ANPD.

Entregáveis nesta situação: linha do tempo; avaliação de risco fundamentada; minuta de comunicação à ANPD; minuta de comunicação aos titulares; plano de contenção e remediação; entrada no registro de incidentes. Modelo: `assets/modelos/comunicacao-incidente.md`.

## 6. Gestão de fornecedores e operadores

1. **Inventário** de fornecedores que acessam ou recebem dados pessoais.
2. **Classificação de risco**: volume, sensibilidade, acesso (leitura, armazenamento, processamento), localização, criticidade.
3. **Due diligence** proporcional — questionário mínimo:
   - Onde os dados são armazenados e processados (países)? Quais suboperadores?
   - Certificações (ISO 27001, ISO 27701, SOC 2)? Último pentest?
   - Criptografia em trânsito e em repouso? MFA? Gestão de acessos?
   - Prazo e forma de notificação de incidentes?
   - Usa dados do cliente para finalidade própria (ex.: treinar IA)?
   - Como devolve/elimina dados ao término?
   - Possui encarregado?
4. **Contrato** com DPA (ver `references/documentos-juridicos.md`, seção 5).
5. **Monitoramento** periódico e na renovação.

## 7. RIPD — quando e como (art. 38)

Recomende RIPD quando houver: dados sensíveis em volume; dados de crianças; monitoramento sistemático (câmeras, geolocalização, monitoramento de empregados); decisões automatizadas com efeitos relevantes; IA treinada com dados pessoais; tecnologias novas (biometria, reconhecimento facial); larga escala; legítimo interesse com impacto relevante; combinação de bases. A ANPD pode exigir a qualquer momento.

Estrutura no modelo `assets/modelos/ripd.md`: identificação; necessidade do RIPD; descrição do tratamento; partes interessadas consultadas; necessidade e proporcionalidade; identificação e avaliação de riscos (probabilidade × impacto); medidas para tratar riscos; risco residual; aprovação.

## 8. Legítimo interesse — LIA

Use quando a base escolhida for legítimo interesse (art. 10). Modelo `assets/modelos/teste-legitimo-interesse.md`, seguindo o guia da ANPD (2024): finalidade legítima → necessidade → balanceamento e salvaguardas. Se o balanceamento for desfavorável, recomende outra base ou medidas adicionais (opt-out, minimização, pseudonimização, transparência reforçada).

## 9. Encarregado e governança (art. 41; Res. 18/2024)

Verifique:
- Ato formal de indicação.
- Divulgação de identidade e contato no site (nome — pessoa natural ou jurídica —, e-mail ou formulário).
- Autonomia técnica, recursos e acesso à alta administração.
- Ausência de conflito de interesse (acúmulo com funções que decidem sobre tratamento, como diretor de TI ou marketing, exige avaliação).
- Atribuições documentadas.
- Para agentes de pequeno porte dispensados: canal de comunicação com titulares disponível (Res. 2/2022).

## 10. Treinamento e cultura

Conteúdo mínimo: conceitos e princípios; dados sensíveis; como identificar e reportar incidentes; atendimento a titulares (encaminhar ao encarregado, não responder improvisadamente); engenharia social e phishing; mesa limpa; uso de IA generativa com dados de clientes. Registrar participação (prova de governança — atenuante na dosimetria, Res. 4/2023).

## 11. Agentes de pequeno porte (Res. CD/ANPD nº 2/2022)

Incluem microempresas, empresas de pequeno porte, startups, pessoas jurídicas sem fins lucrativos, pessoas naturais e entes despersonalizados que tratam dados — **exceto** se realizarem tratamento de alto risco ou tiverem faturamento acima dos limites legais (ou pertencerem a grupo econômico que os exceda).

Flexibilizações: ROPA simplificado; dispensa de indicar encarregado (mantido canal de comunicação); prazos em dobro (inclusive comunicação de incidente e atendimento a titulares, exceto quando a lei fixar prazo distinto ou em situações de risco grave); política simplificada de segurança da informação.

Ao analisar empresas pequenas, proponha soluções proporcionais — um plano de adequação desenhado para grande empresa não será executado.

## 12. Roteiro de adequação em fases

Use para estruturar plano de ação em projetos de adequação:

| Fase | Entregas | Horizonte típico |
|---|---|---|
| 0. Contenção | Corrigir exposições críticas, rotacionar credenciais, remover dados públicos | Imediato |
| 1. Fundação | Indicar encarregado; publicar política de privacidade; canal de titulares; plano de incidentes | 30 dias |
| 2. Mapeamento | ROPA; bases legais; tabela de temporalidade; mapa de fornecedores e transferências | 30–90 dias |
| 3. Adequação | Contratos/DPA; consentimentos; cookies; minimização; segurança; RIPD e LIA | 90–180 dias |
| 4. Sustentação | Treinamentos; auditorias periódicas; métricas; revisão anual de documentos | Contínuo |
