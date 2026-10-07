# Código, sistemas e infraestrutura

Checklist de análise e padrões de correção para software. Use junto com a saída de `scripts/scan_pii.py`.

## Sumário

1. Roteiro de análise
2. Coleta e minimização
3. Armazenamento e criptografia
4. Logs, telemetria e mensagens de erro
5. Segredos e credenciais
6. Transmissão e APIs
7. Respostas de endpoints e exposição de dados
8. Front-end, cookies e rastreadores
9. Extensões, userscripts e automações de navegador
10. Integrações e transferência internacional
11. Retenção e eliminação
12. Direitos do titular no sistema
13. Controle de acesso e auditoria
14. Ambientes não produtivos, testes e seeds
15. IA, perfilamento e decisões automatizadas
16. Dados de crianças e dados sensíveis
17. Padrões de correção (exemplos de código)
18. Dados reais vazados no repositório


---

## 1. Roteiro de análise

1. Rode `scripts/scan_pii.py` no repositório inteiro.
2. Localize o **modelo de dados**: migrations, schemas (Prisma, TypeORM, SQLAlchemy, Django models, Entity Framework, DDL `.sql`), DTOs, interfaces e formulários. Liste todos os campos pessoais e sensíveis.
3. Siga o **fluxo**: onde o dado entra (formulário, API, importação, scraping), onde é armazenado, para onde vai (filas, terceiros, analytics, logs, backups, e-mails) e quando sai.
4. Verifique **dependências e SDKs** (`package.json`, `requirements.txt`, `pom.xml`, `Gemfile`, `go.mod`, `build.gradle`, `Podfile`) em busca de analytics, crash reporting, ads, CRM, chat, IA — cada um é um compartilhamento e possivelmente transferência internacional.
5. Verifique **configuração e infraestrutura**: `.env*`, `docker-compose`, Terraform, Kubernetes, configurações de bucket, região de hospedagem, políticas de backup.
6. Faça o **inventário de endpoints** e analise o que cada um devolve (seção 7). É onde a maior parte da exposição real acontece e o scanner só aponta indícios.
7. Verifique o que existe para **direitos do titular**, **consentimento**, **retenção** e **auditoria**.

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

## 7. Respostas de endpoints e exposição de dados (arts. 6º, III e VII; 46; 49)

Endpoints que devolvem mais do que o cliente precisa, ou devolvem dados a quem não deveria vê-los, são a forma mais comum de exposição em sistemas reais. O dado sai em texto claro, fica em cache de navegador e proxy, aparece nas ferramentas de desenvolvedor e pode ser coletado em massa. Para o titular, o efeito é o mesmo de um vazamento.

### 7.1 Método

1. **Inventarie os endpoints.** Procure as definições de rota da stack:

   | Stack | Onde procurar |
   |---|---|
   | ASP.NET Core | `[ApiController]`, `[Route]`, `[HttpGet/Post/Put/Patch/Delete]`, `app.MapGet/MapPost`, retornos `ActionResult<T>`, `IActionResult`, `Ok(...)`, `Results.Ok(...)` |
   | Express / Fastify / Koa | `router.get/post(...)`, `app.get(...)`, `res.json`, `res.send`, `reply.send` |
   | NestJS | `@Controller`, `@Get/@Post`, tipos de retorno, `ClassSerializerInterceptor`, `@Exclude/@Expose` |
   | Spring | `@RestController`, `@GetMapping`, `ResponseEntity<T>`, `@JsonIgnore`, `@JsonView` |
   | Django REST / Django | `ViewSet`, `APIView`, `serializers.ModelSerializer` (`fields`, `exclude`), `JsonResponse`, `model_to_dict` |
   | FastAPI / Flask | `@app.get`, `response_model`, `jsonify`, `return dict(...)` |
   | Laravel | `routes/api.php`, `return $model`, `JsonResource`, `$hidden`, `$visible` |
   | Rails | `routes.rb`, `render json:`, serializers, `as_json` |
   | Go | `http.HandleFunc`, `gin`/`echo`/`fiber` handlers, `json.NewEncoder(w).Encode`, `c.JSON` |
   | GraphQL | schema/types, resolvers, `introspection`, campos expostos por tipo |
   | gRPC | arquivos `.proto` (mensagens de resposta) |
   | OpenAPI/Swagger | `swagger.json`, `openapi.yaml` — documentam exatamente o que cada resposta contém |

2. **Para cada endpoint, siga o tipo de retorno até a definição** (entidade, DTO, ViewModel, serializer, `select` da query) e liste os campos devolvidos.
3. **Classifique cada campo**: identificador direto (nome, CPF, RG, e-mail, telefone, endereço), sensível (saúde, biometria, religião etc.), financeiro, credencial/segredo (hash de senha, token, chave, código de recuperação, MFA secret), dado de terceiro (outro paciente, outro cliente) ou interno (flags, auditoria, IDs internos).
4. **Compare com a finalidade** da tela ou integração que consome o endpoint. Abra o front-end ou cliente, quando disponível, para ver quais campos são de fato usados. Campo devolvido e nunca usado é violação de necessidade.
5. **Verifique quem pode chamar**: autenticação, autorização por papel e **por recurso** (o usuário só vê os próprios dados ou os da sua organização), multi-tenancy.
6. **Verifique como a resposta trafega e fica guardada**: cabeçalhos de cache, logs de resposta, APM.

Registre o achado por endpoint (`GET /api/pacientes/{id}`), com arquivo e linha do controller e do DTO/entidade, a lista de campos expostos desnecessariamente e a correção proposta. No relatório, uma tabela `Endpoint | Campos expostos | Classificação | Quem acessa | Correção` costuma ser a forma mais clara.

Em sistemas grandes, priorize: endpoints sem autenticação, endpoints que devolvem entidades com dados sensíveis, listagens, buscas e exportações. Informe no relatório quantos endpoints foram revisados e quais ficaram fora.

### 7.2 Sinais de violação

**Excesso de dados na resposta (necessidade)**
- Entidade do ORM devolvida diretamente: `return Ok(paciente)`, `res.json(user)`, `return user` em `@RestController`, `render json: @user`, `return $user`, `fields = '__all__'`, `model_to_dict(obj)`.
- `SELECT *` ou `Include()`/`populate()`/eager loading de relações inteiras (prontuários, endereços, dependentes) quando a tela precisa de um resumo.
- Listagens que devolvem o mesmo DTO completo do detalhe — uma lista de 500 pacientes com CPF, telefone e diagnóstico para montar um combo de seleção.
- Endpoints de autocomplete/busca devolvendo documento, e-mail e telefone completos.
- Campos computados que revelam dado sensível por inferência (ex.: `idade` + `especialidade` + `ultimoExame`).

**Credenciais e segredos na resposta (segurança)**
- `senha`, `password`, `passwordHash`, `SenhaHash`, `salt`, `securityStamp`, `refreshToken`, `resetToken`, `codigoRecuperacao`, `mfaSecret`, `apiKey`, `connectionString` em DTOs de resposta ou entidades serializadas. Hash de senha exposto permite ataque offline.
- Token de sessão no corpo de respostas que não são de login.

**Dados sensíveis em claro**
- Diagnóstico, CID, alergias, medicamentos, resultados de exame, anotações clínicas, biometria, religião ou orientação sexual devolvidos para perfis que não precisam deles (ex.: recepção, faturamento, relatório gerencial).
- CPF, RG, cartão, conta bancária sem máscara onde a tela só exibe para conferência (`***.456.789-**`, `**** 1234`).
- URLs públicas ou sem expiração para documentos, exames, fotos e anexos (`/uploads/exame-123.pdf`).

**Dados de outros titulares (controle de acesso)**
- IDOR/BOLA: `GET /pacientes/{id}` sem verificar se o registro pertence à organização ou ao usuário logado; IDs sequenciais facilitam enumeração.
- Multi-tenant sem filtro obrigatório por tenant (falta de filtro global, `WHERE empresa_id = ...` esquecido).
- Autorização por campo ausente: o mesmo DTO para administrador e para usuário comum.
- Endpoints de exportação (CSV/Excel/PDF) sem restrição de perfil, sem limite e sem registro de auditoria.
- Busca por CPF/e-mail/telefone que confirma existência de cadastro sem autenticação (enumeração).

**Erros e respostas técnicas**
- Stack trace, SQL, nomes de tabelas ou valores de parâmetros em respostas de erro: `UseDeveloperExceptionPage()` fora de desenvolvimento, `DEBUG = True`, `app.debug = True`, `customErrors mode="Off"`, `res.status(500).json(err)`, `err.stack`, `ex.ToString()` ou `ex.Message` devolvido ao cliente.
- Erros de validação ecoando o valor recebido (`"CPF 123.456.789-09 inválido"`).

**Transporte, cache e documentação**
- Respostas com dados pessoais sem `Cache-Control: no-store` (ficam em cache de navegador, CDN e proxies corporativos).
- Dados pessoais na URL (`/pacientes/cpf/12345678909`, `?email=`): ficam em logs de servidor, proxy, APM e histórico do navegador.
- Swagger/OpenAPI e introspecção do GraphQL habilitados em produção sem autenticação, expondo o modelo de dados.
- GraphQL sem limite de profundidade/complexidade, permitindo navegar de um registro para dados de outros titulares.
- Respostas completas registradas em log ou em ferramentas de APM.
- CORS permissivo (`*` ou refletindo qualquer origem) em endpoints autenticados com cookies.

### 7.3 Severidade sugerida

| Situação | Severidade |
|---|---|
| Hash de senha, token ou segredo em resposta; dado sensível ou de terceiros acessível por IDOR ou sem autenticação | Crítica |
| Dado sensível devolvido a perfis sem necessidade; entidade completa com documentos em listagens; exportação sem controle; stack trace em produção | Alta |
| Campos pessoais não usados pela tela; documentos sem máscara; PII na URL; ausência de `no-store`; Swagger público | Média |
| Campos internos desnecessários; IDs sequenciais sem outro problema | Baixa |

### 7.4 Correções

- **DTO de resposta por caso de uso** (resumo, detalhe, listagem), com allowlist explícita de campos. Não serializar entidade do ORM diretamente.
- **Projeção na consulta** (`Select(p => new PacienteResumoDto {...})`, `select: {}` no Prisma, `.only()`/`.values()` no Django, `@JsonView`) para nem carregar o que não será devolvido.
- **Exclusão de credenciais no modelo** (`[JsonIgnore]`, `@JsonIgnore`, `@Exclude()`, `$hidden`, `write_only=True`) como defesa adicional, não como mecanismo principal.
- **Mascaramento no servidor** de documentos e contatos quando a tela só precisa conferir; endpoint separado, restrito e auditado para revelar o valor completo.
- **Autorização por recurso e por tenant**: verificar dono/organização em toda consulta por ID; filtros globais de tenant; UUID como camada adicional.
- **Perfis de acesso por campo**: DTOs distintos para perfis com e sem necessidade de dados sensíveis.
- **Erros genéricos** para o cliente (`ProblemDetails` sem detalhes internos, com `traceId`) e detalhes só no log, sem dados pessoais.
- **Cabeçalhos**: `Cache-Control: no-store` em respostas com dados pessoais.
- **Identificadores pessoais fora da URL**: ID interno na rota e busca por documento via `POST` com corpo.
- **Swagger/GraphQL**: desabilitar em produção ou proteger com autenticação; limitar profundidade e complexidade.
- **Exportações**: restringir por perfil, registrar quem exportou o quê, limitar volume, arquivo com expiração.
- **Paginação obrigatória** com limite máximo por página.

Exemplos por stack na seção 17.

## 8. Front-end, cookies e rastreadores

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

## 9. Extensões, userscripts e automações de navegador

Relevante para repositórios de Tampermonkey/Greasemonkey, extensões Chrome/Firefox, bots e scrapers.

Sinais:
- Captura de dados de terceiros exibidos na página (perfis, mensagens, fotos, contatos) e armazenamento via `GM_setValue`, `localStorage`, `chrome.storage` ou envio a servidor (`GM_xmlhttpRequest`, `fetch`).
- Scraping de perfis de redes sociais ou apps de relacionamento — dados de terceiros que não consentiram, possivelmente sensíveis (orientação sexual inferida de app de relacionamento, fotos = possível biometria).
- Contorno de controles de privacidade da plataforma (desbloquear fotos borradas, ver quem curtiu sem assinatura, expor dados ocultos) — contraria a expectativa legítima dos titulares e os termos da plataforma; avaliar com cuidado.
- Envio de dados a endpoints externos ou de terceiros sem transparência.
- Permissões amplas (`@match *://*/*`, `<all_urls>`, `@grant` desnecessários, `@connect *`).

Ponderação: uso exclusivamente particular e não econômico por pessoa natural está fora da LGPD (art. 4º, I). Se o script for publicado e usado por terceiros, monetizado, ou enviar dados a servidor, a exceção deixa de se aplicar ao distribuidor/operador do servidor. Mesmo no uso particular, aponte riscos de violação dos termos da plataforma e de direitos de personalidade (Código Civil, arts. 20 e 21) como observação, sem classificá-los como violação da LGPD.

Correções: processar localmente sem persistir; não enviar a servidores; restringir `@match`/permissões; eliminar dados armazenados ao fechar; documentar no README o que é coletado.

## 10. Integrações e transferência internacional (arts. 7º, §5º; 33; 39)

Sinais: SDKs e APIs de terceiros recebendo dados pessoais (CRM, e-mail marketing, WhatsApp Business, gateways, IA generativa, tradução, OCR, antifraude) sem contrato de operador, sem informação na política e, se no exterior, sem mecanismo do art. 33.

Correções: mapear cada integração (dado enviado, finalidade, país, papel do terceiro); minimizar e pseudonimizar antes do envio; assegurar DPA com cláusulas-padrão da Res. 19/2024 quando internacional; para LLMs, não enviar dados pessoais desnecessários, desativar retenção/treinamento pelo provedor quando possível.

## 11. Retenção e eliminação (arts. 15 e 16)

Sinais: nenhuma rotina de expurgo; `soft delete` que nunca vira exclusão; dados de contas encerradas mantidos indefinidamente; backups eternos; tabelas de leads antigas.

Correções: tabela de temporalidade por categoria de dado; jobs agendados de eliminação ou anonimização; exclusão em cascata em réplicas, caches, índices de busca, data warehouse e terceiros; backups com rotação e procedimento para não restaurar dados eliminados.

## 12. Direitos do titular no sistema (arts. 18 a 20)

Verifique se há funcionalidade ou procedimento para: exportar os dados do titular (acesso e portabilidade em formato estruturado — JSON/CSV); corrigir; eliminar/anonimizar; revogar consentimentos por finalidade; listar compartilhamentos; revisar decisão automatizada. Ausência total em sistema com muitos titulares é achado alto; atendimento manual documentado pode ser suficiente para sistemas pequenos.

## 13. Controle de acesso e auditoria (arts. 6º, VII e X; 46; 37)

Sinais: usuário administrador compartilhado; ausência de perfis por necessidade de acesso; sem MFA para acesso administrativo; sem trilha de auditoria de quem consultou/exportou dados pessoais; acesso direto ao banco de produção por desenvolvedores.

Correções: RBAC/least privilege; MFA; logs de auditoria imutáveis de acesso a dados pessoais (sem registrar o conteúdo do dado); revisão periódica de acessos.

## 14. Ambientes não produtivos, testes e seeds

Sinais: dump de produção em ambiente de desenvolvimento ou homologação; fixtures/seeds com dados reais; planilhas de clientes no repositório; prints de tela com dados em issues ou documentação.

Correções: dados sintéticos (Faker com locale `pt_BR`), mascaramento/anonimização na cópia de produção, CPFs de teste claramente gerados (o scanner identifica CPFs válidos — revise se são reais).

## 15. IA, perfilamento e decisões automatizadas (arts. 12, §2º; 20)

Sinais: scoring, aprovação de crédito, triagem de currículos, precificação personalizada, moderação automatizada sem revisão humana disponível ou sem explicação de critérios; treinamento de modelos com dados pessoais sem base legal e sem transparência; inferência de dados sensíveis.

Correções: canal de revisão (art. 20); documentação de critérios; avaliação de viés (princípio da não discriminação); RIPD; minimização e pseudonimização de bases de treino.

## 16. Dados de crianças e dados sensíveis (arts. 11 e 14)

- Identifique campos sensíveis pelo nome e conteúdo (`saude`, `diagnostico`, `cid`, `alergia`, `religiao`, `raca`, `etnia`, `orientacao_sexual`, `biometria`, `digital`, `face`, `sindicato`, `partido`, `deficiencia`, `gestante`, `hiv`, `tipo_sanguineo`).
- Confira se a base legal é do art. 11 (não do art. 7º), se há criptografia reforçada, acesso restrito e RIPD.
- Para crianças: verificação de idade, consentimento parental quando aplicável, configurações protetivas por padrão, ausência de perfilamento publicitário.

## 17. Padrões de correção (exemplos de código)

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

### Respostas de endpoints — ASP.NET Core

```csharp
public record PacienteResumoDto(Guid Id, string Nome, string CpfMascarado, DateOnly? ProximaConsulta);

[HttpGet]
[Authorize(Policy = "Recepcao")]
public async Task<ActionResult<PagedResult<PacienteResumoDto>>> Listar([FromQuery] int pagina = 1, [FromQuery] int tamanho = 20)
{
    tamanho = Math.Clamp(tamanho, 1, 100);
    var itens = await _db.Pacientes
        .Where(p => p.ClinicaId == _usuario.ClinicaId)
        .OrderBy(p => p.Nome)
        .Skip((pagina - 1) * tamanho).Take(tamanho)
        .Select(p => new PacienteResumoDto(p.Id, p.Nome, Mascara.Cpf(p.Cpf), p.ProximaConsulta))
        .ToListAsync();
    Response.Headers.CacheControl = "no-store";
    return Ok(new PagedResult<PacienteResumoDto>(itens, pagina, tamanho));
}

[HttpGet("{id:guid}")]
public async Task<ActionResult<PacienteDetalheDto>> Obter(Guid id)
{
    var paciente = await _db.Pacientes
        .Where(p => p.Id == id && p.ClinicaId == _usuario.ClinicaId)
        .Select(p => new PacienteDetalheDto(p.Id, p.Nome, Mascara.Cpf(p.Cpf), p.Telefone))
        .FirstOrDefaultAsync();
    return paciente is null ? NotFound() : Ok(paciente);
}
```

```csharp
modelBuilder.Entity<Paciente>().HasQueryFilter(p => p.ClinicaId == _tenant.ClinicaId);
```

```csharp
public class Usuario
{
    public Guid Id { get; set; }
    public string Email { get; set; } = "";
    [JsonIgnore] public string SenhaHash { get; set; } = "";
    [JsonIgnore] public string? RefreshToken { get; set; }
}
```

```csharp
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler();
    app.UseHsts();
}
builder.Services.AddProblemDetails(o => o.CustomizeProblemDetails = c => c.ProblemDetails.Detail = null);
```

```csharp
public static class Mascara
{
    public static string Cpf(string? cpf) =>
        string.IsNullOrEmpty(cpf) || cpf.Length < 11 ? "" : $"***.{cpf.Substring(3, 3)}.{cpf.Substring(6, 3)}-**";
}
```

### Respostas de endpoints — Node.js (Express / NestJS / Prisma)

```js
app.get('/api/pacientes/:id', autenticar, async (req, res) => {
  const paciente = await prisma.paciente.findFirst({
    where: { id: req.params.id, clinicaId: req.usuario.clinicaId },
    select: { id: true, nome: true, telefone: true }
  });
  if (!paciente) return res.sendStatus(404);
  res.set('Cache-Control', 'no-store').json(paciente);
});

app.use((err, req, res, next) => {
  logger.error({ traceId: req.id, erro: err.message });
  res.status(500).json({ erro: 'Erro interno', traceId: req.id });
});
```

```ts
export class UsuarioResponse {
  id: string;
  nome: string;
  @Exclude() senhaHash: string;
  @Exclude() refreshToken: string;
}

app.useGlobalInterceptors(new ClassSerializerInterceptor(app.get(Reflector), { excludeExtraneousValues: true }));
```

### Respostas de endpoints — Spring

```java
public record PacienteResumo(UUID id, String nome, String cpfMascarado) {}

@GetMapping("/pacientes/{id}")
public ResponseEntity<PacienteResumo> obter(@PathVariable UUID id, @AuthenticationPrincipal UsuarioLogado u) {
    return repo.findByIdAndClinicaId(id, u.clinicaId())
        .map(p -> new PacienteResumo(p.getId(), p.getNome(), Mascara.cpf(p.getCpf())))
        .map(dto -> ResponseEntity.ok().cacheControl(CacheControl.noStore()).body(dto))
        .orElse(ResponseEntity.notFound().build());
}
```

```properties
server.error.include-stacktrace=never
server.error.include-message=never
springdoc.api-docs.enabled=false
```

### Respostas de endpoints — Django REST Framework / FastAPI

```python
class PacienteResumoSerializer(serializers.ModelSerializer):
    cpf = serializers.SerializerMethodField()

    class Meta:
        model = Paciente
        fields = ["id", "nome", "cpf"]

    def get_cpf(self, obj):
        return f"***.{obj.cpf[3:6]}.{obj.cpf[6:9]}-**" if obj.cpf else ""


class PacienteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PacienteResumoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Paciente.objects.filter(clinica=self.request.user.clinica).only("id", "nome", "cpf")
```

```python
class UsuarioPublico(BaseModel):
    id: UUID
    nome: str


@app.get("/usuarios/{id}", response_model=UsuarioPublico)
def obter(id: UUID, usuario=Depends(usuario_atual)):
    ...
```

### Respostas de endpoints — Laravel

```php
class Usuario extends Model
{
    protected $hidden = ['password', 'remember_token', 'two_factor_secret'];
}

class PacienteResource extends JsonResource
{
    public function toArray($request): array
    {
        return ['id' => $this->id, 'nome' => $this->nome];
    }
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

## 18. Dados reais vazados no repositório

Se o scanner encontrar dados pessoais reais ou segredos versionados:

1. Tratar como **possível incidente de segurança** — avaliar exposição (repositório público? forks? quanto tempo?) e aplicar `references/processos-e-governanca.md` seção de incidentes (prazo de 3 dias úteis se houver risco ou dano relevante).
2. Remover os arquivos e reescrever o histórico (`git filter-repo --path <arquivo> --invert-paths` ou BFG), forçar push, pedir invalidação de caches/forks ao provedor (GitHub permite solicitar remoção de dados sensíveis via suporte).
3. Rotacionar todas as credenciais expostas.
4. Registrar o incidente no registro interno (mínimo de 5 anos), mesmo que não seja comunicável.

Reescrever histórico é destrutivo e afeta todos os colaboradores — explique o impacto e só execute com autorização explícita do usuário.
