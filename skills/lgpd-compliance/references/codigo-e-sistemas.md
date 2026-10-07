# Código, sistemas e infraestrutura

Checklist de análise e padrões de correção para software. Use junto com a saída de `scripts/scan_pii.py`.

## Sumário

1. Roteiro de análise
2. Coleta e minimização
3. Armazenamento e criptografia
4. Logs, telemetria e mensagens de erro
5. Segredos e credenciais
6. Transmissão e APIs
7. Front-end, cookies e rastreadores
8. Extensões, userscripts e automações de navegador
9. Integrações e transferência internacional
10. Retenção e eliminação
11. Direitos do titular no sistema
12. Controle de acesso e auditoria
13. Ambientes não produtivos, testes e seeds
14. IA, perfilamento e decisões automatizadas
15. Dados de crianças e dados sensíveis
16. Padrões de correção (exemplos de código)
17. Dados reais vazados no repositório

---

## 1. Roteiro de análise

1. Rode `scripts/scan_pii.py` no repositório inteiro.
2. Localize o **modelo de dados**: migrations, schemas (Prisma, TypeORM, SQLAlchemy, Django models, Entity Framework, DDL `.sql`), DTOs, interfaces e formulários. Liste todos os campos pessoais e sensíveis.
3. Siga o **fluxo**: onde o dado entra (formulário, API, importação, scraping), onde é armazenado, para onde vai (filas, terceiros, analytics, logs, backups, e-mails) e quando sai.
4. Verifique **dependências e SDKs** (`package.json`, `requirements.txt`, `pom.xml`, `Gemfile`, `go.mod`, `build.gradle`, `Podfile`) em busca de analytics, crash reporting, ads, CRM, chat, IA — cada um é um compartilhamento e possivelmente transferência internacional.
5. Verifique **configuração e infraestrutura**: `.env*`, `docker-compose`, Terraform, Kubernetes, configurações de bucket, região de hospedagem, políticas de backup.
6. Verifique o que existe para **direitos do titular**, **consentimento**, **retenção** e **auditoria**.

## 2. Coleta e minimização (art. 6º, III; art. 9º)

Sinais de violação:
- Campos obrigatórios sem necessidade para a finalidade (CPF em newsletter, data de nascimento completa quando basta "maior de 18", gênero em cadastro de e-commerce, foto de documento sem exigência legal).
- Coleta de geolocalização precisa, lista de contatos, IMEI/ID de publicidade em app sem justificativa.
- Respostas de API devolvendo o objeto inteiro do usuário (`SELECT *`, `res.json(user)`) — expõe dados que o cliente não precisa.
- Formulários sem link para política de privacidade ou sem aviso de finalidade no ponto de coleta.
- Checkbox de consentimento pré-marcado ou consentimento embutido no aceite de termos.

Correções: tornar opcional ou remover o campo, coletar faixa em vez de valor exato, DTOs de resposta com allowlist de campos, aviso de finalidade junto ao campo.

## 3. Armazenamento e criptografia (art. 46)

Sinais de violação:
- Senhas em texto claro, MD5, SHA-1 ou SHA-256 sem salt/iterações. Correto: Argon2id, bcrypt ou scrypt.
- Dados sensíveis (saúde, biometria, religião etc.) e documentos (CPF, RG, cartão) sem criptografia em repouso no nível de campo ou de volume.
- Chaves de criptografia no mesmo repositório ou banco que os dados.
- Buckets/containers públicos (S3 `public-read`, Azure Blob público, Firebase rules `allow read, write: if true`).
- Arquivos de upload (documentos, fotos) servidos por URL previsível sem autenticação.
- Backups sem criptografia ou sem controle de retenção.
- Cartão de crédito armazenado (PAN/CVV) — além da LGPD, viola PCI DSS; CVV nunca pode ser armazenado.

Correções: hashing adequado para senhas; criptografia de campo (AES-256-GCM com KMS/Vault) para sensíveis; tokenização para cartão via gateway; URLs assinadas com expiração; regras de acesso restritivas.

## 4. Logs, telemetria e mensagens de erro (arts. 6º, III e VII; 46)

Sinais de violação:
- `console.log(user)`, `logger.info(f"... {request.body}")`, log de payloads completos, headers com `Authorization`, cookies ou tokens.
- Stack traces com dados pessoais enviados a Sentry/Datadog/New Relic sem scrubbing.
- Logs de acesso guardando IP e query strings com e-mail/CPF por tempo indefinido.
- Mensagens de erro que revelam existência de cadastro ("e-mail já cadastrado", "CPF não encontrado") — enumeração de usuários.

Correções: logger estruturado com redator de campos (`cpf`, `email`, `senha`, `token`, `telefone`, `cartao`); `beforeSend` no Sentry; retenção de logs definida (Marco Civil exige 6 meses de registros de acesso para provedores de aplicação — guardar o necessário, não o payload); mensagens genéricas de autenticação.

## 5. Segredos e credenciais (art. 46)

Sinais: chaves de API, strings de conexão, senhas de banco, chaves privadas, tokens OAuth em código, `.env` versionado, segredos em CI sem mascaramento.

Correções: mover para gerenciador de segredos/variáveis de ambiente; adicionar ao `.gitignore`; **rotacionar** toda credencial exposta (remover do código não basta — ela continua no histórico); habilitar secret scanning e pre-commit hooks (gitleaks, trufflehog).

## 6. Transmissão e APIs (art. 46)

Sinais: `http://` para endpoints com dados pessoais; TLS desabilitado (`verify=False`, `rejectUnauthorized: false`); CORS `*` com credenciais; dados pessoais em query string (ficam em logs de proxy e histórico); ausência de rate limiting em endpoints de busca por CPF/e-mail; IDOR (acesso a `/users/123` sem checar dono).

Correções: HTTPS obrigatório com HSTS; validação de certificado; dados no corpo de requisição POST; autorização por recurso; rate limit; paginação e filtros que não permitam extração em massa.

## 7. Front-end, cookies e rastreadores

Guia orientativo da ANPD sobre cookies (2022) e arts. 7º, 8º, 9º e 33.

Sinais de violação:
- Scripts de analytics/ads (Google Analytics/gtag, Google Tag Manager, Meta Pixel `fbq`, TikTok Pixel, LinkedIn Insight, Hotjar, Microsoft Clarity, Mixpanel, Amplitude, Segment, Hubspot, RD Station) carregados **antes** de qualquer consentimento.
- Banner apenas informativo ("ao continuar navegando você aceita") ou sem opção de rejeitar com a mesma facilidade de aceitar.
- Categorias não essenciais pré-ativadas; ausência de forma de revogar depois.
- Ausência de política de cookies listando cookies, finalidade, duração e terceiros.
- Dados pessoais em `localStorage`/`sessionStorage` (acessíveis por qualquer script — risco em XSS), tokens de sessão sem `HttpOnly`, `Secure`, `SameSite`.
- Session replay gravando campos de formulário sem mascaramento.

Correções: consent management (CMP) que bloqueia scripts por categoria até o aceite; Google Consent Mode v2 com padrão `denied`; botões "Aceitar", "Rejeitar" e "Configurar" com mesmo destaque; registro do consentimento (data, versão, escolhas); cookies de sessão `HttpOnly; Secure; SameSite=Lax`; mascaramento em ferramentas de replay. Modelo de texto em `assets/modelos/aviso-de-cookies.md`.

Classificação usual: estritamente necessários (sem consentimento — legítimo interesse/execução de contrato), de desempenho/analíticos, de funcionalidade e de publicidade/marketing (consentimento).

## 8. Extensões, userscripts e automações de navegador

Relevante para repositórios de Tampermonkey/Greasemonkey, extensões Chrome/Firefox, bots e scrapers.

Sinais:
- Captura de dados de terceiros exibidos na página (perfis, mensagens, fotos, contatos) e armazenamento via `GM_setValue`, `localStorage`, `chrome.storage` ou envio a servidor (`GM_xmlhttpRequest`, `fetch`).
- Scraping de perfis de redes sociais ou apps de relacionamento — dados de terceiros que não consentiram, possivelmente sensíveis (orientação sexual inferida de app de relacionamento, fotos = possível biometria).
- Contorno de controles de privacidade da plataforma (desbloquear fotos borradas, ver quem curtiu sem assinatura, expor dados ocultos) — contraria a expectativa legítima dos titulares e os termos da plataforma; avaliar com cuidado.
- Envio de dados a endpoints externos ou de terceiros sem transparência.
- Permissões amplas (`@match *://*/*`, `<all_urls>`, `@grant` desnecessários, `@connect *`).

Ponderação: uso exclusivamente particular e não econômico por pessoa natural está fora da LGPD (art. 4º, I). Se o script for publicado e usado por terceiros, monetizado, ou enviar dados a servidor, a exceção deixa de se aplicar ao distribuidor/operador do servidor. Mesmo no uso particular, aponte riscos de violação dos termos da plataforma e de direitos de personalidade (Código Civil, arts. 20 e 21) como observação, sem classificá-los como violação da LGPD.

Correções: processar localmente sem persistir; não enviar a servidores; restringir `@match`/permissões; eliminar dados armazenados ao fechar; documentar no README o que é coletado.

## 9. Integrações e transferência internacional (arts. 7º, §5º; 33; 39)

Sinais: SDKs e APIs de terceiros recebendo dados pessoais (CRM, e-mail marketing, WhatsApp Business, gateways, IA generativa, tradução, OCR, antifraude) sem contrato de operador, sem informação na política e, se no exterior, sem mecanismo do art. 33.

Correções: mapear cada integração (dado enviado, finalidade, país, papel do terceiro); minimizar e pseudonimizar antes do envio; assegurar DPA com cláusulas-padrão da Res. 19/2024 quando internacional; para LLMs, não enviar dados pessoais desnecessários, desativar retenção/treinamento pelo provedor quando possível.

## 10. Retenção e eliminação (arts. 15 e 16)

Sinais: nenhuma rotina de expurgo; `soft delete` que nunca vira exclusão; dados de contas encerradas mantidos indefinidamente; backups eternos; tabelas de leads antigas.

Correções: tabela de temporalidade por categoria de dado; jobs agendados de eliminação ou anonimização; exclusão em cascata em réplicas, caches, índices de busca, data warehouse e terceiros; backups com rotação e procedimento para não restaurar dados eliminados.

## 11. Direitos do titular no sistema (arts. 18 a 20)

Verifique se há funcionalidade ou procedimento para: exportar os dados do titular (acesso e portabilidade em formato estruturado — JSON/CSV); corrigir; eliminar/anonimizar; revogar consentimentos por finalidade; listar compartilhamentos; revisar decisão automatizada. Ausência total em sistema com muitos titulares é achado alto; atendimento manual documentado pode ser suficiente para sistemas pequenos.

## 12. Controle de acesso e auditoria (arts. 6º, VII e X; 46; 37)

Sinais: usuário administrador compartilhado; ausência de perfis por necessidade de acesso; sem MFA para acesso administrativo; sem trilha de auditoria de quem consultou/exportou dados pessoais; acesso direto ao banco de produção por desenvolvedores.

Correções: RBAC/least privilege; MFA; logs de auditoria imutáveis de acesso a dados pessoais (sem registrar o conteúdo do dado); revisão periódica de acessos.

## 13. Ambientes não produtivos, testes e seeds

Sinais: dump de produção em ambiente de desenvolvimento ou homologação; fixtures/seeds com dados reais; planilhas de clientes no repositório; prints de tela com dados em issues ou documentação.

Correções: dados sintéticos (Faker com locale `pt_BR`), mascaramento/anonimização na cópia de produção, CPFs de teste claramente gerados (o scanner identifica CPFs válidos — revise se são reais).

## 14. IA, perfilamento e decisões automatizadas (arts. 12, §2º; 20)

Sinais: scoring, aprovação de crédito, triagem de currículos, precificação personalizada, moderação automatizada sem revisão humana disponível ou sem explicação de critérios; treinamento de modelos com dados pessoais sem base legal e sem transparência; inferência de dados sensíveis.

Correções: canal de revisão (art. 20); documentação de critérios; avaliação de viés (princípio da não discriminação); RIPD; minimização e pseudonimização de bases de treino.

## 15. Dados de crianças e dados sensíveis (arts. 11 e 14)

- Identifique campos sensíveis pelo nome e conteúdo (`saude`, `diagnostico`, `cid`, `alergia`, `religiao`, `raca`, `etnia`, `orientacao_sexual`, `biometria`, `digital`, `face`, `sindicato`, `partido`, `deficiencia`, `gestante`, `hiv`, `tipo_sanguineo`).
- Confira se a base legal é do art. 11 (não do art. 7º), se há criptografia reforçada, acesso restrito e RIPD.
- Para crianças: verificação de idade, consentimento parental quando aplicável, configurações protetivas por padrão, ausência de perfilamento publicitário.

## 16. Padrões de correção (exemplos de código)

Adapte ao estilo e à stack do projeto. Os exemplos abaixo são referência, não código para colar sem revisão.

### Redação de PII em logs — Node.js (pino)

```js
const pino = require('pino');

const logger = pino({
  redact: {
    paths: ['*.cpf', '*.email', '*.senha', '*.password', '*.telefone', '*.token', 'req.headers.authorization', 'req.headers.cookie'],
    censor: '[REDACTED]'
  }
});
```

### Redação de PII em logs — Python (logging)

```python
import logging
import re

PADROES = [
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[CPF]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
]


class RedatorPII(logging.Filter):
    def filter(self, record):
        mensagem = record.getMessage()
        for padrao, substituto in PADROES:
            mensagem = padrao.sub(substituto, mensagem)
        record.msg, record.args = mensagem, ()
        return True


logging.getLogger().addFilter(RedatorPII())
```

### Hash de senha

```python
from argon2 import PasswordHasher

ph = PasswordHasher()
hash_senha = ph.hash(senha)
ph.verify(hash_senha, senha_informada)
```

```js
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(senha, 12);
const ok = await bcrypt.compare(senhaInformada, hash);
```

### Criptografia de campo (AES-256-GCM)

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

chave = bytes.fromhex(os.environ["CHAVE_DADOS_SENSIVEIS"])


def cifrar(texto: str) -> bytes:
    nonce = os.urandom(12)
    return nonce + AESGCM(chave).encrypt(nonce, texto.encode(), None)


def decifrar(dado: bytes) -> str:
    return AESGCM(chave).decrypt(dado[:12], dado[12:], None).decode()
```

Chave em KMS/Vault, nunca no repositório. Para buscas por igualdade em campo cifrado, armazene também um HMAC do valor normalizado.

### Pseudonimização para analytics

```python
import hmac
import hashlib
import os

SEGREDO = os.environ["SEGREDO_PSEUDONIMO"].encode()


def pseudonimo(identificador: str) -> str:
    return hmac.new(SEGREDO, identificador.strip().lower().encode(), hashlib.sha256).hexdigest()
```

### Resposta de API com allowlist (minimização)

```ts
type UsuarioPublico = Pick<Usuario, 'id' | 'nome' | 'avatarUrl'>;

function paraPublico(u: Usuario): UsuarioPublico {
  return { id: u.id, nome: u.nome, avatarUrl: u.avatarUrl };
}
```

### Carregar analytics só após consentimento

```html
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied'
  });
</script>
```

```js
function aplicarConsentimento(escolhas) {
  gtag('consent', 'update', {
    analytics_storage: escolhas.analiticos ? 'granted' : 'denied',
    ad_storage: escolhas.marketing ? 'granted' : 'denied',
    ad_user_data: escolhas.marketing ? 'granted' : 'denied',
    ad_personalization: escolhas.marketing ? 'granted' : 'denied'
  });
  if (escolhas.marketing) carregarScript('https://connect.facebook.net/en_US/fbevents.js');
}
```

### Registro de consentimento (modelo de tabela)

```sql
CREATE TABLE consentimento (
  id BIGSERIAL PRIMARY KEY,
  titular_id BIGINT NOT NULL,
  finalidade VARCHAR(100) NOT NULL,
  concedido BOOLEAN NOT NULL,
  versao_texto VARCHAR(20) NOT NULL,
  canal VARCHAR(30) NOT NULL,
  registrado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
  revogado_em TIMESTAMPTZ
);
```

### Job de retenção

```sql
UPDATE cliente
SET nome = 'ANONIMIZADO', email = NULL, cpf = NULL, telefone = NULL, anonimizado_em = now()
WHERE conta_encerrada_em < now() - INTERVAL '5 years'
  AND anonimizado_em IS NULL;
```

### Exportação de dados do titular (acesso/portabilidade)

```python
def exportar_dados_titular(titular_id):
    return {
        "cadastro": repo.cadastro(titular_id),
        "pedidos": repo.pedidos(titular_id),
        "consentimentos": repo.consentimentos(titular_id),
        "compartilhamentos": repo.compartilhamentos(titular_id),
        "gerado_em": datetime.utcnow().isoformat(),
    }
```

### Cookie de sessão seguro

```js
res.cookie('sid', token, { httpOnly: true, secure: true, sameSite: 'lax', maxAge: 1000 * 60 * 60 * 8 });
```

## 17. Dados reais vazados no repositório

Se o scanner encontrar dados pessoais reais ou segredos versionados:

1. Tratar como **possível incidente de segurança** — avaliar exposição (repositório público? forks? quanto tempo?) e aplicar `references/processos-e-governanca.md` seção de incidentes (prazo de 3 dias úteis se houver risco ou dano relevante).
2. Remover os arquivos e reescrever o histórico (`git filter-repo --path <arquivo> --invert-paths` ou BFG), forçar push, pedir invalidação de caches/forks ao provedor (GitHub permite solicitar remoção de dados sensíveis via suporte).
3. Rotacionar todas as credenciais expostas.
4. Registrar o incidente no registro interno (mínimo de 5 anos), mesmo que não seja comunicável.

Reescrever histórico é destrutivo e afeta todos os colaboradores — explique o impacto e só execute com autorização explícita do usuário.
