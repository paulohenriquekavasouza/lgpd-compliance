# Documentos jurídicos e textos voltados ao titular

Checklists, sinais de alerta e padrões de redação para políticas, termos, contratos, formulários e comunicações.

## Sumário

1. Método de revisão de documentos
2. Política de privacidade / aviso de privacidade
3. Termos de uso
4. Termo de consentimento
5. Contrato controlador–operador (DPA)
6. Contratos entre controladores (cocontroladoria, parcerias, compartilhamento)
7. Contratos comerciais em geral (cláusula de proteção de dados)
8. Contratos de trabalho e documentos de RH
9. Formulários de coleta (físicos e digitais)
10. Aviso e política de cookies
11. Comunicações de marketing
12. Editais, contratos públicos e documentos de órgãos públicos
13. Termos de imagem, voz e biometria
14. Cláusulas abusivas e expressões de alerta
15. Formato de entrega da revisão

---

## 1. Método de revisão de documentos

1. Identifique o tipo de documento, as partes e o papel de cada uma (controlador, operador, titular).
2. Liste as operações de tratamento que o documento descreve ou pressupõe (dados, finalidade, base legal, compartilhamento, retenção, transferência internacional).
3. Aplique o checklist da seção correspondente. Marque cada item como: atende, atende parcialmente, não atende, não aplicável.
4. Procure as expressões de alerta da seção 14.
5. Verifique coerência com a prática real, se conhecida (ex.: política diz que não compartilha, mas o site usa Meta Pixel; contrato diz que dados ficam no Brasil, mas o fornecedor usa nuvem nos EUA). Incoerência entre texto e prática é achado grave — viola transparência e pode tornar o consentimento nulo (art. 9º, §1º).
6. Produza achados com fundamento e redline (seção 15).

Para documentos .docx, .pdf ou .odt, extraia o texto com `scripts/scan_pii.py --dump-text <arquivo>` ou com as skills de docx/pdf, se disponíveis. Para entregar a versão revisada em Word com controle de alterações, use a skill de docx quando existir.

## 2. Política de privacidade / aviso de privacidade

Fundamento: arts. 6º, VI; 9º; 14, §2º; 18; 33; 41, §1º; Res. 19/2024 (transferência).

Checklist:
- [ ] Identificação do controlador (razão social, CNPJ, endereço) — art. 9º, III.
- [ ] Contato do controlador e **identidade e contato do encarregado** — arts. 9º, IV e 41, §1º.
- [ ] Dados coletados, por categoria, incluindo os coletados automaticamente (IP, cookies, dispositivo, localização).
- [ ] Origem dos dados quando não coletados diretamente do titular (bureaus, parceiros, fontes públicas).
- [ ] **Finalidade específica** de cada tratamento — art. 9º, I.
- [ ] **Base legal** de cada finalidade (não obrigatório literalmente pela lei, mas recomendado pela ANPD e essencial para demonstrar conformidade).
- [ ] Dados sensíveis, se houver, com a hipótese do art. 11.
- [ ] Dados de crianças e adolescentes, se houver, com regras do art. 14.
- [ ] **Compartilhamento**: com quem (categorias ou nomes), para quê — art. 9º, V.
- [ ] **Transferência internacional**: países ou regiões, mecanismo do art. 33 — Res. 19/2024.
- [ ] **Prazo de retenção** ou critério — art. 9º, II; art. 15.
- [ ] Medidas de segurança (descrição geral).
- [ ] **Direitos do titular** com menção ao art. 18 e como exercê-los, gratuitamente — art. 9º, VII; art. 18, §5º.
- [ ] Direito de petição à ANPD — art. 18, §1º.
- [ ] Revogação do consentimento e consequências de não consentir — art. 18, VIII e IX.
- [ ] Decisões automatizadas e direito de revisão, se houver — art. 20.
- [ ] Cookies (ou link para a política de cookies).
- [ ] Data da última atualização e histórico de versões; como os titulares serão avisados de alterações — art. 8º, §6º.
- [ ] Linguagem clara, em português, acessível; camadas (resumo + detalhes) recomendadas.
- [ ] Facilmente acessível (rodapé do site, tela de cadastro, loja de aplicativos).

Sinais de alerta: texto genérico copiado de outro site ou traduzido do GDPR (cita "Regulamento (UE) 2016/679" ou "DPO" sem adaptação); "podemos alterar esta política a qualquer momento sem aviso"; "compartilhamos com parceiros" sem identificar categorias e finalidades; ausência de encarregado; prazo "indeterminado".

Modelo: `assets/modelos/politica-de-privacidade.md`.

## 3. Termos de uso

Termos de uso regulam a relação contratual, mas costumam conter cláusulas de dados.

Checklist:
- [ ] Remete à política de privacidade em vez de reproduzir regras divergentes.
- [ ] Não embute consentimento para tratamento de dados no aceite geral (consentimento deve ser destacado e específico — art. 8º, §1º e §4º).
- [ ] Não condiciona o serviço ao fornecimento de dados desnecessários (art. 6º, III; art. 9º, §3º; art. 14, §4º para crianças).
- [ ] Não prevê renúncia a direitos do titular nem exclusão de responsabilidade do controlador por incidentes (art. 42; CDC art. 51, I).
- [ ] Idade mínima e regras para menores coerentes com art. 14.
- [ ] Conteúdo gerado por usuário com dados de terceiros: regras de remoção e responsabilidade (Marco Civil arts. 19 e 21).
- [ ] Foro e lei aplicável compatíveis com CDC quando houver consumidor.

## 4. Termo de consentimento

Fundamento: arts. 5º, XII; 8º; 9º; 11, I; 14, §1º; 33, VIII.

Checklist:
- [ ] Usado apenas quando consentimento é de fato a base adequada.
- [ ] **Separado e destacado** de outras cláusulas (art. 8º, §1º).
- [ ] **Uma finalidade por opção** — sem consentimento "em bloco" (art. 8º, §4º).
- [ ] Informa controlador, dados, finalidade, compartilhamento, prazo, direitos e forma de revogação (art. 9º).
- [ ] Revogação tão fácil quanto a concessão e gratuita (art. 8º, §5º).
- [ ] Não pré-marcado, não condicionado ao serviço quando não necessário (livre).
- [ ] Para dados sensíveis: forma específica e destacada, finalidade específica (art. 11, I).
- [ ] Para crianças: assinado por pais/responsável, com verificação razoável (art. 14, §1º e §5º).
- [ ] Para transferência internacional baseada em consentimento: informa o caráter internacional (art. 33, VIII).
- [ ] Prevê registro (data, versão, canal) — ônus da prova do controlador (art. 8º, §2º).

Modelo: `assets/modelos/termo-de-consentimento.md`.

## 5. Contrato controlador–operador (DPA)

Fundamento: arts. 37, 39, 42, §1º, I, 46, 47, 48; Res. 19/2024 (se transferência internacional); Guia ANPD de agentes de tratamento.

Checklist de cláusulas mínimas:
- [ ] Definição clara dos papéis (controlador e operador) e do objeto do tratamento.
- [ ] Descrição do tratamento: categorias de dados e de titulares, finalidade, duração, local.
- [ ] Obrigação do operador de tratar **apenas conforme instruções documentadas** do controlador (art. 39) e de avisar se considerar uma instrução ilícita.
- [ ] Confidencialidade de pessoas autorizadas.
- [ ] Medidas de segurança técnicas e administrativas (art. 46) — preferencialmente em anexo, com padrão mínimo (criptografia, controle de acesso, logs, backup, testes).
- [ ] **Suboperadores**: autorização prévia (específica ou geral com direito de oposição), mesmas obrigações por contrato, responsabilidade do operador por eles.
- [ ] **Transferência internacional**: países, mecanismo do art. 33; se cláusulas-padrão, anexar as da Res. 19/2024 sem alteração.
- [ ] Apoio ao controlador no atendimento aos direitos dos titulares (art. 18), com prazo compatível com o art. 19.
- [ ] **Notificação de incidentes** ao controlador em prazo curto (recomendado 24 a 48 horas) com as informações do art. 48, §1º, para que o controlador cumpra os 3 dias úteis.
- [ ] Apoio em RIPD e em fiscalizações da ANPD.
- [ ] Registro das operações (art. 37) e disponibilização de informações.
- [ ] **Auditoria**: direito do controlador de auditar ou receber relatórios/certificações.
- [ ] Ao término: **devolução e/ou eliminação** dos dados e de cópias, com certificação, ressalvadas obrigações legais (arts. 15, 16 e 47).
- [ ] Responsabilidade e direito de regresso, sem limitar responsabilidade perante titulares (art. 42).
- [ ] Vedação de uso dos dados para finalidade própria do operador (se usar, vira controlador — art. 42, §1º, I).

Sinais de alerta: fornecedor reservando direito de usar dados "para melhoria de seus serviços", "treinamento de modelos", "fins estatísticos" sem anonimização; limitação de responsabilidade cobrindo incidentes de dados; prazo de notificação "em tempo razoável"; foro e lei estrangeiros sem mecanismo de transferência.

Modelo: `assets/modelos/acordo-tratamento-dados.md`.

## 6. Contratos entre controladores (cocontroladoria, parcerias, compartilhamento)

Checklist:
- [ ] Papéis definidos: controladores independentes ou cocontroladores (decidem em conjunto).
- [ ] Base legal de cada parte para o compartilhamento e para o uso posterior (art. 7º, §5º se o original for consentimento).
- [ ] Compatibilidade de finalidade do recebedor com a informada ao titular.
- [ ] Divisão de responsabilidades: transparência, atendimento a titulares, incidentes.
- [ ] Ponto de contato único para titulares, quando cocontroladoria.
- [ ] Responsabilidade solidária reconhecida (art. 42, §1º, II) e regras de regresso.
- [ ] Dados sensíveis de saúde: verificar vedação do art. 11, §4º.

## 7. Contratos comerciais em geral

Qualquer contrato em que uma parte acesse dados pessoais da outra (manutenção de TI, contabilidade, folha de pagamento, call center, logística, marketing, consultoria, coworking) deve conter cláusula de proteção de dados ou DPA anexo. Contratos com pessoas físicas (prestadores, representantes) envolvem também os dados do próprio contratado — política de privacidade para eles.

Cláusula mínima, quando um DPA completo for desproporcional:

> As Partes se obrigam a cumprir a Lei nº 13.709/2018 (LGPD) e a regulamentação da ANPD. Na medida em que a CONTRATADA tratar dados pessoais em nome da CONTRATANTE, atuará como operadora, tratando-os exclusivamente para a execução deste Contrato e conforme instruções documentadas da CONTRATANTE; manterá medidas de segurança técnicas e administrativas adequadas; não subcontratará o tratamento sem autorização prévia e escrita; comunicará à CONTRATANTE qualquer incidente de segurança em até 48 (quarenta e oito) horas de seu conhecimento; auxiliará no atendimento a requisições de titulares e da ANPD; e, ao término do Contrato, devolverá ou eliminará os dados pessoais, salvo obrigação legal de conservação.

## 8. Contratos de trabalho e documentos de RH

Fundamento: arts. 7º, II e V; 11, II, a e d; 6º, III; legislação trabalhista e previdenciária.

Checklist:
- [ ] Aviso de privacidade ao colaborador e candidato (finalidades: admissão, folha, eSocial, benefícios, saúde ocupacional, segurança, monitoramento).
- [ ] Base legal correta: obrigação legal (eSocial, PCMSO, CAGED) e execução de contrato — **não** consentimento, que no vínculo de emprego dificilmente é livre.
- [ ] Dados sensíveis (atestados, ASO, CID, biometria de ponto, filiação sindical, deficiência para cota, raça para censo de diversidade): hipóteses do art. 11 e acesso restrito.
- [ ] Biometria de ponto: art. 11, II, "g" (prevenção a fraude e segurança, em identificação/autenticação) ou obrigação legal; informar; alternativa para quem não pode usar.
- [ ] Monitoramento (e-mail corporativo, câmeras, geolocalização, ferramentas de produtividade): finalidade, proporcionalidade, transparência prévia; não em áreas privadas.
- [ ] Processo seletivo: não pedir dados excessivos (estado civil, religião, foto, antecedentes criminais sem justificativa legal — TST considera ilícita a exigência de certidão de antecedentes fora de hipóteses justificadas), retenção de currículos não aprovados com prazo definido.
- [ ] Dados de dependentes (inclusive crianças, art. 14) para benefícios.
- [ ] Compartilhamento com operadoras de saúde, benefícios, contabilidade terceirizada: contratos com cláusulas de dados.
- [ ] Termo de confidencialidade e treinamento em proteção de dados para quem trata dados.
- [ ] Retenção conforme prazos trabalhistas e previdenciários; eliminação do restante após desligamento.

## 9. Formulários de coleta (físicos e digitais)

Checklist:
- [ ] Cada campo é necessário para a finalidade? Campos opcionais marcados como opcionais.
- [ ] Aviso de finalidade e link para política no ponto de coleta (camada curta).
- [ ] Consentimentos separados, não pré-marcados, um por finalidade (ex.: "quero receber ofertas por e-mail").
- [ ] Dados sensíveis só se indispensáveis, com hipótese do art. 11.
- [ ] Formulários em papel: guarda segura, prazo de descarte, digitalização com controle de acesso.
- [ ] Formulários públicos (Google Forms, Typeform): configuração de privacidade, quem tem acesso às respostas, transferência internacional.
- [ ] Listas de presença e fichas de cadastro em balcão: não expor dados de um titular a outro.

Saída recomendada: tabela `Campo | Necessário? | Finalidade | Base legal | Ação (manter, tornar opcional, remover, substituir)`.

## 10. Aviso e política de cookies

Fundamento: Guia orientativo de cookies da ANPD (2022); arts. 7º, 8º, 9º, 33.

Checklist:
- [ ] Banner com opções "Aceitar", "Rejeitar" e "Configurar" com o mesmo destaque.
- [ ] Cookies não necessários desativados até o consentimento; nada pré-marcado.
- [ ] Granularidade por categoria (necessários, desempenho/analíticos, funcionalidade, publicidade).
- [ ] Política de cookies com tabela: nome, fornecedor, finalidade, categoria, duração, primeira/terceira parte, país.
- [ ] Forma de alterar ou revogar a escolha a qualquer momento (link permanente no rodapé).
- [ ] Sem "cookie wall" que bloqueie acesso a quem rejeitar, salvo justificativa robusta.

Modelo: `assets/modelos/aviso-de-cookies.md`.

## 11. Comunicações de marketing

Checklist:
- [ ] Base legal: consentimento (opt-in) ou legítimo interesse para clientes existentes com produtos similares, com LIA documentado e opt-out fácil.
- [ ] Opt-out em toda comunicação (link de descadastro, "SAIR" no SMS/WhatsApp).
- [ ] Origem lícita das listas — compra de mailing é de alto risco (titular não foi informado; base legal frágil).
- [ ] Telemarketing: respeito ao "Não Me Perturbe" e regras da ANATEL/Procon.
- [ ] Perfilamento para segmentação: transparência; sem uso de dados sensíveis sem consentimento específico.
- [ ] WhatsApp: consentimento conforme políticas do WhatsApp Business e LGPD.

## 12. Editais, contratos públicos e documentos de órgãos públicos

- Base: art. 7º, III e art. 23 (finalidade pública); transparência ativa compatibilizada com LAI.
- Publicação de dados pessoais em editais, resultados e diários oficiais: apenas o necessário (ex.: nome e parte mascarada do CPF — padrão `***.123.456-**`), nunca dados sensíveis.
- Contratos com fornecedores: cláusulas de operador; vedação de uso compartilhado com privados fora do art. 26.
- Indicação e publicação do encarregado (art. 23, III).

## 13. Termos de imagem, voz e biometria

- Uso de imagem: autorização (Código Civil art. 20) e LGPD (dado pessoal). Especificar finalidade, meios, prazo, território, gratuidade ou remuneração, revogação.
- Reconhecimento facial / biometria: dado sensível (art. 5º, II); exige hipótese do art. 11; RIPD recomendado; alternativa não biométrica.
- Gravação de chamadas e vídeo: informar no início; finalidade; retenção.
- Imagens de crianças: consentimento de pais/responsáveis, melhor interesse (art. 14).

## 14. Cláusulas abusivas e expressões de alerta

Busque e trate como achado (média a alta, conforme contexto):

| Expressão / padrão | Problema | Fundamento |
|---|---|---|
| "Ao utilizar o site, você concorda com..." como único consentimento | Consentimento não livre, não destacado, não específico | art. 8º, §1º e §4º |
| "Autorizo o tratamento dos meus dados para quaisquer fins" | Autorização genérica — nula | art. 8º, §4º |
| "Por tempo indeterminado", "indefinidamente", "permanentemente" | Retenção sem limite | arts. 6º, III; 15; 16 |
| "Parceiros comerciais" sem identificação | Compartilhamento opaco | art. 9º, V |
| "Podemos vender/ceder seus dados" | Base legal improvável; transparência | arts. 7º; 9º |
| "Não nos responsabilizamos por vazamentos" | Exclusão ilícita de responsabilidade | arts. 42 a 44; CDC art. 51, I |
| "O titular renuncia aos direitos..." | Direitos indisponíveis | art. 18; CDC art. 51 |
| "Podemos alterar sem aviso prévio" | Falta de informação sobre mudanças | art. 8º, §6º; art. 9º, §2º |
| Referência ao GDPR/"DPO" sem menção à LGPD/encarregado | Texto não adaptado | arts. 9º; 41 |
| Consentimento pré-assinalado ou "opt-out" para dado sensível | Consentimento inválido | arts. 8º; 11, I |
| "Dados anonimizados" que incluem e-mail, telefone ou ID | Pseudonimização tratada como anonimização | arts. 12; 13, §4º |
| "Dados armazenados em servidores seguros no exterior" sem mecanismo | Transferência internacional sem garantia | art. 33; Res. 19/2024 |

## 15. Formato de entrega da revisão

1. **Resumo**: tipo do documento, papel das partes, avaliação geral (adequado, adequado com ressalvas, inadequado) e os 3 a 5 pontos mais relevantes.
2. **Checklist** aplicado (tabela com status por item).
3. **Redline**:

| # | Cláusula / trecho | Texto atual | Texto proposto | Fundamento | Severidade |
|---|---|---|---|---|---|

4. **Cláusulas a incluir** (texto completo pronto para inserir).
5. **Versão consolidada**, se solicitada — mantendo numeração e estilo do original.
6. **Pontos que dependem de decisão** do usuário ou de informação que não está no documento.
7. Aviso de que a revisão não substitui parecer jurídico.
