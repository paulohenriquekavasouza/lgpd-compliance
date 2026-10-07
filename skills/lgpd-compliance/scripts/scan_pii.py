#!/usr/bin/env python3
import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from html import unescape

SEVERIDADES = ["critica", "alta", "media", "baixa", "info"]
ORDEM = {s: i for i, s in enumerate(SEVERIDADES)}

DIRETORIOS_IGNORADOS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "venv", ".venv", "env", "__pycache__",
    "dist", "build", ".next", ".nuxt", "target", "bin", "obj", ".idea", ".vscode", "coverage",
    ".terraform", ".gradle", ".cache", "bower_components", ".pytest_cache", ".mypy_cache",
    ".lgpd-compliance", "packages", ".vs",
}

EXTENSOES_BINARIAS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svgz", ".mp3", ".mp4", ".avi",
    ".mov", ".mkv", ".wav", ".flac", ".ogg", ".zip", ".gz", ".tar", ".rar", ".7z", ".jar", ".war",
    ".class", ".exe", ".dll", ".so", ".dylib", ".o", ".a", ".pyc", ".woff", ".woff2", ".ttf",
    ".otf", ".eot", ".lock", ".bin", ".dat", ".db", ".sqlite", ".iso", ".dmg",
}

EXTENSOES_OFFICE = {".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp"}

EXTENSOES_CODIGO = {
    ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".py", ".rb", ".php", ".java",
    ".kt", ".kts", ".scala", ".go", ".rs", ".cs", ".vb", ".swift", ".m", ".c", ".h", ".cpp", ".hpp",
    ".dart", ".sql", ".sh", ".bash", ".ps1", ".html", ".htm", ".yml", ".yaml", ".json", ".xml",
    ".tf", ".gradle", ".properties", ".ini", ".cfg", ".conf", ".toml", ".env", ".lua", ".r", ".pl",
    ".config", ".cshtml", ".razor", ".graphql", ".gql", ".proto",
}

ARTIGOS = {
    "cpf": ["art. 5º, I", "art. 6º, III", "art. 46"],
    "cnpj": ["art. 5º, I"],
    "cartao_credito": ["art. 46", "art. 6º, VII"],
    "email": ["art. 5º, I", "art. 6º, III"],
    "telefone": ["art. 5º, I", "art. 6º, III"],
    "cep": ["art. 5º, I"],
    "rg": ["art. 5º, I", "art. 46"],
    "pis": ["art. 5º, I", "art. 46"],
    "titulo_eleitor": ["art. 5º, I", "art. 46"],
    "cns": ["art. 5º, II", "art. 11"],
    "ip": ["art. 5º, I"],
    "data_nascimento": ["art. 5º, I", "art. 6º, III", "art. 14"],
    "campo_sensivel": ["art. 5º, II", "art. 11", "art. 46"],
    "dados_criancas": ["art. 14"],
    "pii_em_log": ["art. 6º, III", "art. 6º, VII", "art. 46"],
    "segredo_exposto": ["art. 46", "art. 47", "art. 48"],
    "chave_privada": ["art. 46", "art. 48"],
    "rastreador_terceiro": ["art. 7º", "art. 8º", "art. 9º", "art. 33"],
    "armazenamento_cliente": ["art. 46", "art. 6º, VII"],
    "transmissao_insegura": ["art. 46"],
    "hash_fraco": ["art. 46"],
    "tls_desabilitado": ["art. 46"],
    "envio_externo": ["art. 7º", "art. 9º, V", "art. 33"],
    "geolocalizacao": ["art. 5º, I", "art. 6º, III", "art. 9º"],
    "biometria": ["art. 5º, II", "art. 11"],
    "texto_juridico_alerta": ["art. 8º", "art. 9º", "art. 15", "art. 16"],
    "arquivo_sensivel": ["art. 46", "art. 48"],
    "resposta_entidade_completa": ["art. 6º, III", "art. 46"],
    "credencial_em_resposta": ["art. 46", "art. 6º, VII"],
    "erro_detalhado_exposto": ["art. 46", "art. 6º, VII"],
    "pii_na_url": ["art. 6º, III", "art. 46"],
    "documentacao_api_exposta": ["art. 46"],
    "cors_permissivo": ["art. 46"],
}

DESCRICOES = {
    "cpf": "CPF válido (dígitos verificadores conferem) em texto claro",
    "cnpj": "CNPJ válido (normalmente dado de pessoa jurídica; pode identificar empresário individual/MEI)",
    "cartao_credito": "Número de cartão de pagamento válido (Luhn) em texto claro",
    "email": "Endereço de e-mail",
    "telefone": "Número de telefone brasileiro",
    "cep": "CEP (identificador indireto quando combinado a outros dados)",
    "rg": "Possível número de RG",
    "pis": "PIS/PASEP/NIT válido",
    "titulo_eleitor": "Possível título de eleitor",
    "cns": "Possível Cartão Nacional de Saúde (vinculado a dado de saúde)",
    "ip": "Endereço IP público (dado pessoal quando associável a titular)",
    "data_nascimento": "Campo ou valor de data de nascimento",
    "campo_sensivel": "Campo/termo associado a dado pessoal sensível (art. 5º, II)",
    "dados_criancas": "Indício de tratamento de dados de crianças ou adolescentes",
    "pii_em_log": "Dado pessoal possivelmente registrado em log/console",
    "segredo_exposto": "Credencial, token ou segredo em código ou configuração",
    "chave_privada": "Chave privada versionada",
    "rastreador_terceiro": "Rastreador/analytics/SDK de terceiro (exige consentimento e informação; possível transferência internacional)",
    "armazenamento_cliente": "Dado pessoal ou token persistido no navegador/cliente",
    "transmissao_insegura": "URL HTTP sem TLS",
    "hash_fraco": "Hash fraco (MD5/SHA-1) possivelmente usado para senhas ou dados pessoais",
    "tls_desabilitado": "Verificação de certificado TLS desabilitada",
    "envio_externo": "Envio de dados a servidor externo a partir de script/cliente",
    "geolocalizacao": "Coleta de geolocalização",
    "biometria": "Tratamento de biometria/reconhecimento facial (dado sensível)",
    "texto_juridico_alerta": "Expressão de alerta em texto jurídico/política",
    "arquivo_sensivel": "Arquivo potencialmente sensível versionado",
    "resposta_entidade_completa": "Endpoint possivelmente devolvendo entidade/objeto completo em vez de DTO com campos necessários",
    "credencial_em_resposta": "Campo de credencial/segredo em classe de saída (DTO/Response/ViewModel/Serializer) sem exclusão da serialização",
    "erro_detalhado_exposto": "Detalhes internos de erro (stack trace, exceção, modo debug) possivelmente devolvidos ao cliente",
    "pii_na_url": "Identificador pessoal em rota ou query string (fica em logs, proxies e histórico)",
    "documentacao_api_exposta": "Documentação/introspecção da API habilitada (verificar se restrita a desenvolvimento ou autenticada)",
    "cors_permissivo": "CORS permissivo (qualquer origem)",
}

SEVERIDADE_BASE = {
    "cpf": "alta", "cnpj": "info", "cartao_credito": "critica", "email": "baixa", "telefone": "baixa",
    "cep": "info", "rg": "media", "pis": "alta", "titulo_eleitor": "media", "cns": "alta", "ip": "info",
    "data_nascimento": "baixa", "campo_sensivel": "media", "dados_criancas": "media", "pii_em_log": "alta",
    "segredo_exposto": "critica", "chave_privada": "critica", "rastreador_terceiro": "media",
    "armazenamento_cliente": "media", "transmissao_insegura": "baixa", "hash_fraco": "media",
    "tls_desabilitado": "alta", "envio_externo": "media", "geolocalizacao": "media", "biometria": "alta",
    "texto_juridico_alerta": "media", "arquivo_sensivel": "alta",
    "resposta_entidade_completa": "media", "credencial_em_resposta": "alta", "erro_detalhado_exposto": "media",
    "pii_na_url": "media", "documentacao_api_exposta": "baixa", "cors_permissivo": "media",
}

RE_CPF = re.compile(r"(?<![\d.\-/])(\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})(?![\d.\-/])")
RE_CNPJ = re.compile(r"(?<![\d.\-/])(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14})(?![\d.\-/])")
RE_CARTAO = re.compile(r"(?<![\d\-])((?:\d[ \-]?){12,18}\d)(?![\d\-])")
RE_EMAIL = re.compile(r"(?<![\w.+\-])[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}(?![\w\-])")
RE_TELEFONE = re.compile(r"(?<!\d)(?:\+55[\s\-]?)?\(?(?:[1-9]{2})\)?[\s\-]?9?\d{4}[\s\-]\d{4}(?!\d)")
RE_CEP = re.compile(r"(?<![\d\-])\d{5}-\d{3}(?![\d\-])")
RE_RG = re.compile(r"\bR\.?G\.?\s*(?:n[ºo°.]*\s*)?[:\-]?\s*(\d{1,2}\.?\d{3}\.?\d{3}-?[\dxX])\b")
RE_PIS = re.compile(r"(?<![\d.\-])(\d{3}\.\d{5}\.\d{2}-\d)(?![\d.\-])")
RE_TITULO = re.compile(r"t[ií]tulo\s+(?:de\s+)?eleitor\D{0,15}(\d{4}\s?\d{4}\s?\d{4})", re.I)
RE_CNS = re.compile(r"\b(?:cns|cart[aã]o\s+(?:nacional\s+)?(?:de\s+)?sa[uú]de|cart[aã]o\s+sus)\b\D{0,15}([1-9]\d{2}\s?\d{4}\s?\d{4}\s?\d{4})", re.I)
RE_IP = re.compile(r"(?<![\d.])((?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3})(?![\d.])")
RE_NASC = re.compile(r"\b(data[_\s\-]?(?:de[_\s\-]?)?nasc(?:imento)?|dt[_\-]?nasc|birth[_\-]?date|date[_\-]?of[_\-]?birth|dob|nascimento)\b", re.I)

TERMOS_SENSIVEIS = [
    r"ra[cç]a", r"etnia", r"cor[_\s]da[_\s]pele", r"religi[aã]o", r"crença", r"orienta[cç][aã]o[_\s]?sexual",
    r"vida[_\s]sexual", r"identidade[_\s]de[_\s]g[eê]nero", r"sindicat\w*", r"filia[cç][aã]o[_\s]partid[aá]ria",
    r"partido[_\s]pol[ií]tico", r"opini[aã]o[_\s]pol[ií]tica", r"diagn[oó]stico", r"\bcid[_\s\-]?10\b", r"\bcid\b",
    r"doen[cç]a", r"defici[eê]ncia", r"\bpcd\b", r"alergia", r"medicamento", r"prontu[aá]rio", r"tipo[_\s]sangu[ií]neo",
    r"\bhiv\b", r"gestante", r"gravidez", r"gen[eé]tic\w*", r"\bdna\b", r"sa[uú]de[_\s]mental",
    r"religion", r"ethnicity", r"\brace\b", r"sexual[_\s]orientation", r"health[_\s]condition", r"diagnosis",
    r"disability", r"pregnan\w*", r"medical[_\s]record", r"union[_\s]member\w*",
]
RE_SENSIVEL = re.compile(r"(?i)(" + "|".join(TERMOS_SENSIVEIS) + r")")

RE_BIOMETRIA = re.compile(r"(?i)\b(biometri\w*|impress[aã]o[_\s]digital|fingerprint|face[_\s]?(?:id|recognition|match|api)|reconhecimento[_\s]facial|faceapi|face-api\.js|rekognition|liveness|selfie[_\s]?(?:check|valida))")
RE_CRIANCA = re.compile(r"(?i)\b(crian[cç]a|menor(?:es)?[_\s]de[_\s]idade|idade[_\s]m[ií]nima|respons[aá]vel[_\s]legal|consentimento[_\s]parental|aluno|estudante|child[_\s]?(?:age|data|profile|account|user)|minor[_\s]?(?:age|user|account)|under[_\s]?13|parental[_\s]consent|coppa)\b")
RE_GEO = re.compile(r"(navigator\.geolocation|getCurrentPosition|watchPosition|ACCESS_FINE_LOCATION|ACCESS_BACKGROUND_LOCATION|CLLocationManager|requestLocationPermission)")

CAMPOS_PII = r"(cpf|rg|cnpj|email|e_mail|senha|password|passwd|telefone|celular|phone|nome|name|endere[cç]o|address|token|cart[aã]o|card|cvv|nascimento|birth|ssn|documento|salario|salary|user|usuario|cliente|customer|paciente|patient)"
RE_LOG = re.compile(r"(?i)(console\.(?:log|info|warn|error|debug)|logger\.\w+|logging\.\w+|log\.(?:info|debug|warn|error|trace)|print\s*\(|println|System\.out\.print|printf|var_dump|print_r|error_log|Log\.[dievw]\s*\(|NSLog|puts\s)")
RE_LOG_PII = re.compile(r"(?i)\b" + CAMPOS_PII + r"\w*")

RE_SEGREDOS = [
    re.compile(r"(?i)\b(password|passwd|pwd|senha|secret|api[_\-]?key|apikey|access[_\-]?token|auth[_\-]?token|client[_\-]?secret|private[_\-]?key|db[_\-]?pass\w*)\b\s*[:=]\s*['\"]([^'\"\s]{6,})['\"]"),
    re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),
    re.compile(r"\b(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{50,})\b"),
    re.compile(r"\b(xox[baprs]-[A-Za-z0-9\-]{10,})\b"),
    re.compile(r"\b(AIza[0-9A-Za-z\-_]{35})\b"),
    re.compile(r"\b(sk_live_[0-9a-zA-Z]{20,}|sk-[A-Za-z0-9_\-]{20,})\b"),
    re.compile(r"(?i)\b((?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp|mssql)://[^:\s/]+:[^@\s]+@[^\s'\"]+)"),
]
RE_CHAVE_PRIVADA = re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY")

RASTREADORES = {
    "Google Analytics/gtag": r"google-analytics\.com|googletagmanager\.com/gtag|gtag\s*\(\s*['\"]config|ga\s*\(\s*['\"]create",
    "Google Tag Manager": r"googletagmanager\.com/gtm\.js|GTM-[A-Z0-9]{4,}",
    "Meta Pixel": r"connect\.facebook\.net|fbq\s*\(\s*['\"](?:init|track)",
    "TikTok Pixel": r"analytics\.tiktok\.com|ttq\.load",
    "LinkedIn Insight": r"snap\.licdn\.com|_linkedin_partner_id",
    "Hotjar": r"static\.hotjar\.com|hjid",
    "Microsoft Clarity": r"clarity\.ms",
    "Mixpanel": r"mixpanel\.(?:com|init)",
    "Amplitude": r"amplitude\.(?:com|getInstance|init)",
    "Segment": r"cdn\.segment\.com|analytics\.load\(",
    "Hubspot": r"js\.hs-scripts\.com|js\.hs-analytics\.net",
    "RD Station": r"rdstation|d335luupugsy2\.cloudfront\.net",
    "DoubleClick/Google Ads": r"doubleclick\.net|googleadservices\.com|googlesyndication\.com",
    "Firebase Analytics": r"firebase/analytics|getAnalytics\(|firebase-analytics",
    "Sentry": r"@sentry/|sentry\.io|Sentry\.init",
    "Datadog RUM": r"datadoghq|DD_RUM",
    "FullStory": r"fullstory\.com",
    "Yandex Metrica": r"mc\.yandex\.ru",
    "Pinterest Tag": r"ct\.pinterest\.com|pintrk",
    "Twitter/X Pixel": r"static\.ads-twitter\.com|twq\s*\(",
}
RE_RASTREADORES = [(nome, re.compile(p, re.I)) for nome, p in RASTREADORES.items()]

RE_ARMAZ_CLIENTE = re.compile(r"(?i)(localStorage\.setItem|sessionStorage\.setItem|document\.cookie\s*=|GM_setValue|GM\.setValue|chrome\.storage\.\w+\.set|browser\.storage\.\w+\.set|AsyncStorage\.setItem|SharedPreferences|NSUserDefaults|UserDefaults\.standard\.set)")
RE_HTTP = re.compile(r"http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]|www\.w3\.org|schemas\.|xmlns|json-schema\.org|purl\.org|ns\.adobe\.com|example\.(?:com|org)|[\w.\-]*\.local\b)[\w.\-]+")
RE_HASH_FRACO = re.compile(r"(?i)(md5|sha1|sha-1)\s*\(|hashlib\.(md5|sha1)|createHash\(\s*['\"](md5|sha1)['\"]|MessageDigest\.getInstance\(\s*\"(MD5|SHA-1)\"|DigestUtils\.(md5|sha1)")
RE_CONTEXTO_SENHA = re.compile(r"(?i)(senha|password|passwd|pwd|cpf|email|token)")
RE_TLS_OFF = re.compile(r"(?i)(verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0|InsecureSkipVerify\s*:\s*true|CURLOPT_SSL_VERIFYPEER\s*,\s*(?:false|0)|ServerCertificateValidationCallback\s*=.*true|TrustAllCerts|setHostnameVerifier\(.*ALLOW_ALL)")
RE_ENVIO_EXTERNO = re.compile(r"(?i)(GM_xmlhttpRequest|GM\.xmlHttpRequest|navigator\.sendBeacon|new\s+WebSocket\s*\(\s*['\"]wss?://|fetch\s*\(\s*['\"]https?://|axios\.(?:post|put)\s*\(\s*['\"]https?://|\$\.(?:post|ajax)\s*\(\s*\{?\s*(?:url\s*:\s*)?['\"]https?://|@connect\s+\S+)")

ENTIDADES = r"(?:paciente|usuario|usuário|user|cliente|customer|patient|funcionario|colaborador|employee|pessoa|person|medico|profissional|titular|contato|contact|lead|aluno|student|prontuario|atendimento)s?"
RE_RESPOSTA_ENTIDADE = [
    re.compile(r"(?i)\b(?:return\s+)?(?:Ok|Json|Created\w*|Results\.Ok|TypedResults\.Ok)\(\s*(?:await\s+)?(?:new\s+\{[^}]*\}\s*,\s*)?(" + ENTIDADES + r")\s*\)"),
    re.compile(r"(?i)\b(?:Ok|Json|Results\.Ok)\(\s*(?:await\s+)?_?\w*\.(" + ENTIDADES + r")\b(?![^;]*\.Select\w*\()[^;]*\.(?:ToList|ToArray|First|Single|Find)\w*\("),
    re.compile(r"(?i)\b(?:res|response|reply|ctx)\.(?:json|send|status\(\d+\)\.json)\(\s*(?:await\s+)?(" + ENTIDADES + r")\s*\)"),
    re.compile(r"(?i)\bctx\.body\s*=\s*(" + ENTIDADES + r")\s*;?$"),
    re.compile(r"(?i)\brender\s+json:\s*@?(" + ENTIDADES + r")\b\s*$"),
    re.compile(r"(?i)\bc\.JSON\(\s*[\w.]+\s*,\s*&?(" + ENTIDADES + r")\s*\)"),
    re.compile(r"(?i)\bfields\s*=\s*['\"](__all__)['\"]"),
    re.compile(r"(?i)\b(model_to_dict)\s*\("),
    re.compile(r"(?i)\bjsonify\(\s*(" + ENTIDADES + r")\.__dict__"),
]
RE_ARQUIVO_SAIDA = re.compile(r"(?i)(dto|response|resposta|viewmodel|vm|resource|serializer|output|result|retorno|presenter|view)\w*\.\w+$")
RE_ARQUIVO_ENTRADA = re.compile(r"(?i)(request|input|command|comando|create|update|login|register|signup|cadastro|alterar|criar|auth|credential|credencial|token|options|settings|config)")
RE_CAMPO_CREDENCIAL = re.compile(r"(?i)^\s*(?:\[[^\]]*\]\s*)*(?:public|private|protected|internal|readonly|export|val|var|let)?\s*(?:[\w<>\[\]?,.]+\s+)?(senha\w*|password\w*|passwd|salt|securitystamp|refresh_?token|reset_?token|access_?token|mfa_?secret|totp_?secret|two_?factor_?secret|api_?key|secret\w*|codigo_?recuperacao|recovery_?code)\s*(?:[?!]?\s*:|\{|=|;)")
RE_CAMPO_SERIALIZER = re.compile(r"(?i)\bfields\s*=\s*[\[(][^\])]*['\"](password|senha|token|secret|salt)['\"]")
RE_EXCLUSAO_SERIALIZACAO = re.compile(r"(?i)(JsonIgnore|IgnoreDataMember|@Exclude|Exclude\(|WRITE_ONLY|write_only|\$hidden|NonSerialized|transient|@JsonProperty\(\s*access|toJSON|select:\s*false|SwaggerIgnore)")
RE_ERRO_DETALHADO = [
    re.compile(r"\bUseDeveloperExceptionPage\s*\("),
    re.compile(r"(?i)customErrors\s+mode\s*=\s*\"Off\""),
    re.compile(r"^\s*DEBUG\s*=\s*True\b"),
    re.compile(r"\b(?:app\.debug\s*=\s*True|app\.run\([^)]*debug\s*=\s*True)"),
    re.compile(r"(?i)\b(?:res|response|reply)\.(?:status\(\s*\d+\s*\)\.)?(?:json|send)\(\s*(?:\{[^}]*\b(?:err|error|e|ex)(?:\.stack|\.message)?\b[^}]*\}|(?:err|error|e|ex)(?:\.stack)?)\s*\)"),
    re.compile(r"(?i)\b(?:BadRequest|Ok|StatusCode|Problem|Json|ObjectResult)\([^;]*\b(?:ex|e|exception|erro)\.(?:ToString\(\)|StackTrace|InnerException)"),
    re.compile(r"(?i)\b(?:BadRequest|StatusCode|Problem)\([^;]*\b(?:ex|exception)\.Message"),
    re.compile(r"(?i)server\.error\.include-(?:stacktrace|exception|message)\s*[=:]\s*(?:always|true)"),
    re.compile(r"(?i)\bIncludeExceptionDetails\w*\s*=\s*true"),
    re.compile(r"(?i)traceback\.format_exc\(\)[^\n]*(?:return|Response|jsonify)|(?:return|Response|jsonify)[^\n]*traceback\.format_exc\(\)"),
]
CAMPOS_URL = r"(?:cpf|cnpj|rg|email|e-mail|telefone|celular|phone|cns|cartao_?sus|nome|name|data_?nascimento|birth_?date)"
RE_PII_URL = [
    re.compile(r"(?i)\[(?:Http(?:Get|Post|Put|Patch|Delete)|Route)\(\s*\"[^\"]*\{" + CAMPOS_URL + r"\b"),
    re.compile(r"(?i)\bMap(?:Get|Post|Put|Patch|Delete)\(\s*\"[^\"]*\{" + CAMPOS_URL + r"\b"),
    re.compile(r"(?i)\.(?:get|post|put|patch|delete|all|route)\(\s*['\"`][^'\"`]*:" + CAMPOS_URL + r"\b"),
    re.compile(r"(?i)@(?:Get|Post|Put|Patch|Delete|Request)Mapping\(\s*(?:value\s*=\s*)?\"[^\"]*\{" + CAMPOS_URL + r"\b"),
    re.compile(r"(?i)@(?:Get|Post|Put|Patch|Delete)\(\s*['\"][^'\"]*:" + CAMPOS_URL + r"\b"),
    re.compile(r"(?i)(?:path|re_path|url)\(\s*r?['\"][^'\"]*<(?:\w+:)?" + CAMPOS_URL + r">"),
    re.compile(r"(?i)['\"`][^'\"`\s]*[?&]" + CAMPOS_URL + r"=(?:\$\{|['\"`]\s*\+|\{|%s|\w)"),
]
RE_DOC_API = re.compile(r"(?i)(\bUseSwagger(?:UI)?\s*\(|\bMapOpenApi\s*\(|swagger-ui-express|SwaggerModule\.setup|springdoc|@EnableSwagger2|drf_yasg|drf_spectacular|introspection\s*:\s*true|graphiql\s*:\s*true|playground\s*:\s*true)")
RE_CORS = re.compile(r"(?i)(\bAllowAnyOrigin\s*\(|SetIsOriginAllowed\(\s*_?\s*=>\s*true|Access-Control-Allow-Origin['\"]?\s*[:,]\s*['\"]\*|\bcors\(\s*\)|origin\s*:\s*(?:true|['\"]\*['\"])|CORS_ALLOW_ALL_ORIGINS\s*=\s*True|CORS_ORIGIN_ALLOW_ALL\s*=\s*True|@CrossOrigin\(\s*(?:origins\s*=\s*)?\"\*\"|allowedOrigins\(\s*\"\*\")")

ALERTAS_JURIDICOS = [
    (r"tempo\s+indeterminado|indefinidamente|prazo\s+indeterminado|permanentemente\s+armazenad", "Retenção sem prazo definido"),
    (r"para\s+quaisquer\s+fins|para\s+qualquer\s+finalidade|todos\s+os\s+fins", "Autorização genérica (nula — art. 8º, §4º)"),
    (r"ao\s+(?:utilizar|usar|acessar|navegar)[^.]{0,80}(?:concorda|aceita|consente)", "Consentimento presumido pelo uso"),
    (r"parceiros\s+comerciais|empresas\s+parceiras|terceiros\s+parceiros", "Compartilhamento com parceiros sem identificação"),
    (r"(?:vender|ceder|comercializar)\s+(?:os\s+)?(?:seus\s+)?dados", "Venda/cessão de dados"),
    (r"n[aã]o\s+(?:nos\s+)?responsabiliza\w*[^.]{0,80}(?:vazamento|acesso\s+n[aã]o\s+autorizado|incidente|dados)", "Exclusão de responsabilidade por incidentes"),
    (r"renuncia\w*[^.]{0,60}direito", "Renúncia a direitos do titular"),
    (r"alterar[^.]{0,60}(?:a\s+qualquer\s+momento|sem\s+(?:aviso|notifica))", "Alteração unilateral sem aviso"),
    (r"\bGDPR\b|Regulamento\s+\(UE\)\s*2016/679|General\s+Data\s+Protection", "Referência ao GDPR (verificar adaptação à LGPD)"),
    (r"\bDPO\b|Data\s+Protection\s+Officer", "Uso de 'DPO' — verificar menção ao encarregado (art. 41)"),
]
RE_ALERTAS = [(re.compile(p, re.I), d) for p, d in ALERTAS_JURIDICOS]

ARQUIVOS_SENSIVEIS = [
    ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
    "*.sql.gz", "*dump*.sql", "*backup*.sql", "*.bak", "credentials*", "*secret*", "*.kdbx",
    "*leads*.csv",
]
NOMES_DADOS_PESSOAIS = re.compile(r"(?i)(clientes|pacientes|funcionarios|funcionários|colaboradores|cadastro|leads|folha.*pagamento|alunos|usuarios|usuários|contatos|customers|patients|employees|users)")
EXTENSOES_DADOS = {".csv", ".tsv", ".xlsx", ".xls", ".ods", ".json", ".sql", ".txt", ".xml", ".pdf", ".docx", ".doc", ".zip", ".bak", ".mdb", ".accdb", ".dbf"}
EXCECOES_ARQUIVOS_SENSIVEIS = [".env.example", ".env.sample", ".env.template", ".env.dist"]


def valida_cpf(numero):
    d = re.sub(r"\D", "", numero)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for tam in (9, 10):
        soma = sum(int(d[i]) * (tam + 1 - i) for i in range(tam))
        dig = (soma * 10) % 11 % 10
        if dig != int(d[tam]):
            return False
    return True


def valida_cnpj(numero):
    d = re.sub(r"\D", "", numero)
    if len(d) != 14 or d == d[0] * 14:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    for pesos, pos in ((pesos1, 12), (pesos2, 13)):
        soma = sum(int(d[i]) * pesos[i] for i in range(len(pesos)))
        dig = 0 if soma % 11 < 2 else 11 - soma % 11
        if dig != int(d[pos]):
            return False
    return True


def valida_luhn(numero):
    d = re.sub(r"\D", "", numero)
    if not 13 <= len(d) <= 19 or d == d[0] * len(d):
        return False
    total = 0
    for i, c in enumerate(reversed(d)):
        n = int(c)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def bandeira_cartao(numero):
    d = re.sub(r"\D", "", numero)
    return bool(re.match(r"^(4\d{12}(\d{3})?(\d{3})?|5[1-5]\d{14}|2(2[2-9][1-9]|[3-6]\d{2}|7[01]\d|720)\d{12}|3[47]\d{13}|6(011|5\d{2})\d{12}|(636368|438935|504175|451416|636297|5067|4576|4011|506699)\d+|3(0[0-5]|[68]\d)\d{11}|(606282|3841)\d+)$", d))


def valida_pis(numero):
    d = re.sub(r"\D", "", numero)
    if len(d) != 11 or d == d[0] * 11:
        return False
    pesos = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    resto = sum(int(d[i]) * pesos[i] for i in range(10)) % 11
    dig = 0 if resto < 2 else 11 - resto
    return dig == int(d[10])


def ip_publico(ip):
    p = [int(x) for x in ip.split(".")]
    if p[0] in (0, 10, 127) or p[0] >= 224:
        return False
    if p[0] == 172 and 16 <= p[1] <= 31:
        return False
    if p[0] == 192 and p[1] == 168:
        return False
    if p[0] == 169 and p[1] == 254:
        return False
    if p[0] == 100 and 64 <= p[1] <= 127:
        return False
    if p == [8, 8, 8, 8] or p == [8, 8, 4, 4] or p == [1, 1, 1, 1] or p == [1, 0, 0, 1]:
        return False
    if all(x == 0 for x in p[1:]) or p[3] == 0 and p[2] == 0:
        return False
    return True


def mascarar(valor, categoria):
    v = valor.strip()
    if categoria == "email":
        usuario, _, dominio = v.partition("@")
        return (usuario[:1] + "***@" + dominio) if dominio else "***"
    if categoria in ("segredo_exposto", "chave_privada"):
        return v[:4] + "****" if len(v) > 8 else "****"
    digitos = re.sub(r"\D", "", v)
    if categoria == "cpf" and len(digitos) == 11:
        return "***." + digitos[3:6] + ".***-**"
    if categoria in ("cartao_credito",):
        return "**** **** **** " + digitos[-4:]
    if len(v) <= 4:
        return "***"
    visiveis = max(2, len(v) // 5)
    return v[:visiveis] + "*" * (len(v) - 2 * visiveis) + v[-visiveis:]


def extrair_xml_texto(xml):
    xml = re.sub(r"</(?:w:p|a:p|text:p|text:h|row|si)>", "\n", xml)
    xml = re.sub(r"<(?:w:tab|text:tab)[^>]*/>", "\t", xml)
    xml = re.sub(r"</c>", "\t", xml)
    texto = re.sub(r"<[^>]+>", "", xml)
    return unescape(texto)


def extrair_office(caminho):
    ext = os.path.splitext(caminho)[1].lower()
    partes = []
    with zipfile.ZipFile(caminho) as z:
        nomes = z.namelist()
        if ext == ".docx":
            alvos = [n for n in nomes if re.match(r"word/(document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml$", n)]
        elif ext == ".xlsx":
            alvos = [n for n in nomes if n == "xl/sharedStrings.xml" or re.match(r"xl/worksheets/sheet\d+\.xml$", n)]
        elif ext == ".pptx":
            alvos = sorted(n for n in nomes if re.match(r"ppt/(slides/slide\d+|notesSlides/notesSlide\d+)\.xml$", n))
        else:
            alvos = [n for n in nomes if n == "content.xml"]
        for n in alvos:
            xml = z.read(n).decode("utf-8", errors="ignore")
            if ext == ".xlsx" and "worksheets" in n:
                xml = re.sub(r"<c [^>]*t=\"s\"[^>]*>.*?</c>", "", xml, flags=re.S)
            partes.append(extrair_xml_texto(xml))
    return "\n".join(partes)


def extrair_pdf(caminho):
    try:
        import pypdf
        leitor = pypdf.PdfReader(caminho)
        return "\n".join((p.extract_text() or "") for p in leitor.pages)
    except ImportError:
        pass
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-layout", caminho, "-"], capture_output=True, timeout=120)
        return r.stdout.decode("utf-8", errors="ignore")
    raise RuntimeError("PDF ignorado: instale pypdf ou poppler-utils (pdftotext)")


def ler_texto(caminho, max_bytes):
    ext = os.path.splitext(caminho)[1].lower()
    if ext in EXTENSOES_OFFICE:
        return extrair_office(caminho), "documento"
    if ext == ".pdf":
        return extrair_pdf(caminho), "documento"
    if ext in EXTENSOES_BINARIAS:
        return None, None
    with open(caminho, "rb") as f:
        dados = f.read(max_bytes)
    if b"\x00" in dados[:8192]:
        return None, None
    for codificacao in ("utf-8", "latin-1"):
        try:
            texto = dados.decode(codificacao)
            break
        except UnicodeDecodeError:
            continue
    tipo = "codigo" if ext in EXTENSOES_CODIGO or os.path.basename(caminho).startswith(".env") else "texto"
    if ext in (".md", ".txt", ".rtf") or ext == "":
        tipo = "texto"
    if ext in (".csv", ".tsv"):
        tipo = "dados"
    return texto, tipo


def eh_comentario_ou_teste(caminho):
    baixo = caminho.lower().replace("\\", "/")
    return bool(re.search(r"(^|/)(tests?|__tests__|spec|specs|fixtures?|mocks?|__mocks__|examples?|samples?|seeds?)(/|$)|\.(test|spec)\.\w+$|_test\.\w+$", baixo))


class Scanner:
    def __init__(self, args):
        self.args = args
        self.achados = []
        self.erros = []
        self.arquivos_analisados = 0
        self.arquivos_ignorados = 0
        self.max_bytes = int(args.max_size_mb * 1024 * 1024)

    def registrar(self, caminho, linha, categoria, trecho, valor=None, detalhe=None, severidade=None):
        sev = severidade or SEVERIDADE_BASE[categoria]
        if eh_comentario_ou_teste(caminho) and categoria in ("cpf", "email", "telefone", "cartao_credito", "cep", "rg", "pis", "cnpj", "ip"):
            sev = SEVERIDADES[min(ORDEM[sev] + 1, len(SEVERIDADES) - 1)]
            detalhe = (detalhe + "; " if detalhe else "") + "arquivo de teste/fixture — confirmar se o dado é real"
        trecho = trecho.strip()
        if len(trecho) > 200:
            trecho = trecho[:200] + "…"
        if valor and not self.args.show_values:
            trecho = trecho.replace(valor, mascarar(valor, categoria))
            valor_exibido = mascarar(valor, categoria)
        else:
            valor_exibido = valor
        trecho = self.mascarar_trecho_geral(trecho)
        self.achados.append({
            "arquivo": getattr(self, "exibir", None) or caminho,
            "linha": linha,
            "categoria": categoria,
            "severidade": sev,
            "descricao": DESCRICOES[categoria] + (f" — {detalhe}" if detalhe else ""),
            "valor": valor_exibido,
            "trecho": trecho,
            "artigos": ARTIGOS[categoria],
        })

    def mascarar_trecho_geral(self, trecho):
        if self.args.show_values:
            return trecho
        trecho = RE_CPF.sub(lambda m: mascarar(m.group(1), "cpf") if valida_cpf(m.group(1)) else m.group(0), trecho)
        trecho = RE_CARTAO.sub(lambda m: mascarar(m.group(1), "cartao_credito") if valida_luhn(m.group(1)) and bandeira_cartao(m.group(1)) else m.group(0), trecho)
        trecho = RE_PIS.sub(lambda m: mascarar(m.group(1), "pis") if valida_pis(m.group(1)) else m.group(0), trecho)
        trecho = RE_EMAIL.sub(lambda m: m.group(0) if "*" in m.group(0) else mascarar(m.group(0), "email"), trecho)
        trecho = RE_TELEFONE.sub(lambda m: m.group(0) if "*" in m.group(0) else mascarar(m.group(0), "telefone"), trecho)
        for r in RE_SEGREDOS:
            trecho = r.sub(lambda m: m.group(0).replace(m.group(m.lastindex), mascarar(m.group(m.lastindex), "segredo_exposto")), trecho)
        return trecho

    def analisar_arquivo(self, caminho, exibir=None):
        self.exibir = exibir or caminho
        nome = os.path.basename(caminho)
        dados_pessoais = os.path.splitext(nome)[1].lower() in EXTENSOES_DADOS and NOMES_DADOS_PESSOAIS.search(nome) and not re.search(r"(?i)(schema|swagger|openapi|package|tsconfig|appsettings|mock|fixture|seed|exemplo|example|sample)", nome)
        if (dados_pessoais or any(fnmatch.fnmatch(nome.lower(), p) for p in ARQUIVOS_SENSIVEIS)) and nome.lower() not in EXCECOES_ARQUIVOS_SENSIVEIS:
            self.registrar(caminho, 0, "arquivo_sensivel", nome, detalhe="verificar se deveria estar versionado/compartilhado")
        try:
            if os.path.getsize(caminho) > self.max_bytes and os.path.splitext(caminho)[1].lower() not in EXTENSOES_OFFICE | {".pdf"}:
                self.arquivos_ignorados += 1
                self.erros.append({"arquivo": caminho, "erro": "arquivo maior que o limite; analisado parcialmente"})
            texto, tipo = ler_texto(caminho, self.max_bytes)
        except Exception as e:
            self.erros.append({"arquivo": caminho, "erro": str(e)})
            self.arquivos_ignorados += 1
            return
        if texto is None:
            self.arquivos_ignorados += 1
            return
        self.arquivos_analisados += 1
        self.analisar_texto(caminho, texto, tipo)

    def analisar_texto(self, caminho, texto, tipo):
        vistos = set()
        rastreadores_vistos = set()
        linhas = texto.splitlines()
        anterior = ""
        for i, linha in enumerate(linhas, 1):
            if len(linha) > 5000:
                linha = linha[:5000]
            self.detectar_identificadores(caminho, i, linha, vistos)
            if tipo in ("codigo", "texto", "dados") or tipo == "documento":
                self.detectar_contexto(caminho, i, linha, tipo, vistos, rastreadores_vistos)
            if tipo == "codigo":
                self.detectar_api(caminho, i, linha, anterior, vistos)
            if linha.strip():
                anterior = linha

    def detectar_api(self, caminho, i, linha, anterior, vistos):
        nome = os.path.basename(caminho)
        if re.match(r"^\s*(//|#|\*|/\*|<!--|--)", linha):
            return
        for r in RE_RESPOSTA_ENTIDADE:
            m = r.search(linha)
            if m:
                self.registrar(caminho, i, "resposta_entidade_completa", linha, detalhe=f"retorno: {m.group(1)} — confirmar o tipo e os campos serializados")
                break
        if RE_ARQUIVO_SAIDA.search(nome) and not RE_ARQUIVO_ENTRADA.search(nome):
            m = RE_CAMPO_CREDENCIAL.search(linha)
            if m and not RE_EXCLUSAO_SERIALIZACAO.search(linha) and not RE_EXCLUSAO_SERIALIZACAO.search(anterior):
                self.registrar(caminho, i, "credencial_em_resposta", linha, detalhe=f"campo: {m.group(1)} — confirmar se a classe é usada em respostas")
        m = RE_CAMPO_SERIALIZER.search(linha)
        if m:
            self.registrar(caminho, i, "credencial_em_resposta", linha, detalhe=f"campo: {m.group(1)} na lista de fields do serializer")
        for r in RE_ERRO_DETALHADO:
            if r.search(linha):
                contexto = (anterior + " " + linha).lower()
                if "isdevelopment" in contexto or "development" in contexto:
                    break
                self.registrar(caminho, i, "erro_detalhado_exposto", linha)
                break
        for r in RE_PII_URL:
            m = r.search(linha)
            if m:
                self.registrar(caminho, i, "pii_na_url", linha)
                break
        if RE_DOC_API.search(linha) and self.adicionar_unico(vistos, ("docapi", caminho)):
            self.registrar(caminho, i, "documentacao_api_exposta", linha)
        if RE_CORS.search(linha):
            self.registrar(caminho, i, "cors_permissivo", linha)

    def adicionar_unico(self, vistos, chave):
        if chave in vistos:
            return False
        vistos.add(chave)
        return True

    def detectar_identificadores(self, caminho, i, linha, vistos):
        for m in RE_CPF.finditer(linha):
            v = m.group(1)
            if valida_cpf(v) and self.adicionar_unico(vistos, ("cpf", v)):
                self.registrar(caminho, i, "cpf", linha, v)
        for m in RE_CNPJ.finditer(linha):
            v = m.group(1)
            if valida_cnpj(v) and self.adicionar_unico(vistos, ("cnpj", v)):
                self.registrar(caminho, i, "cnpj", linha, v)
        for m in RE_CARTAO.finditer(linha):
            v = m.group(1)
            d = re.sub(r"\D", "", v)
            if len(d) in (11, 14) and (valida_cpf(d) or valida_cnpj(d)):
                continue
            if valida_luhn(v) and bandeira_cartao(v) and self.adicionar_unico(vistos, ("cartao", d)):
                self.registrar(caminho, i, "cartao_credito", linha, v)
        for m in RE_PIS.finditer(linha):
            v = m.group(1)
            if valida_pis(v) and self.adicionar_unico(vistos, ("pis", v)):
                self.registrar(caminho, i, "pis", linha, v)
        for m in RE_EMAIL.finditer(linha):
            v = m.group(0)
            if m.start() > 0 and linha[m.start() - 1] in ":/":
                continue
            if re.search(r"://[^\s'\"]*$", linha[:m.start()]):
                continue
            dominio = v.split("@")[1].lower()
            if re.search(r"\.(png|jpe?g|gif|svg|webp|js|css)$", dominio) or dominio in ("example.com", "example.org", "email.com", "dominio.com", "domain.com", "test.com", "exemplo.com", "exemplo.com.br", "sentry.io", "users.noreply.github.com", "noreply.github.com"):
                continue
            if re.match(r"^(noreply|no-reply|naoresponda|nao-responda)@", v.lower()):
                continue
            if self.adicionar_unico(vistos, ("email", v.lower())):
                self.registrar(caminho, i, "email", linha, v)
        for m in RE_TELEFONE.finditer(linha):
            v = m.group(0)
            d = re.sub(r"\D", "", v)
            if not (10 <= len(d) <= 13) or len(set(d[-8:])) <= 2:
                continue
            if self.adicionar_unico(vistos, ("tel", d)):
                self.registrar(caminho, i, "telefone", linha, v)
        for m in RE_CEP.finditer(linha):
            if self.adicionar_unico(vistos, ("cep", m.group(0))):
                self.registrar(caminho, i, "cep", linha, m.group(0))
        for m in RE_RG.finditer(linha):
            if self.adicionar_unico(vistos, ("rg", m.group(1))):
                self.registrar(caminho, i, "rg", linha, m.group(1))
        for m in RE_TITULO.finditer(linha):
            if self.adicionar_unico(vistos, ("titulo", m.group(1))):
                self.registrar(caminho, i, "titulo_eleitor", linha, m.group(1))
        for m in RE_CNS.finditer(linha):
            if self.adicionar_unico(vistos, ("cns", m.group(1))):
                self.registrar(caminho, i, "cns", linha, m.group(1))
        for m in RE_IP.finditer(linha):
            v = m.group(1)
            if ip_publico(v) and not re.search(r"(?i)version|v\d|\d+\.\d+\.\d+\.\d+\s*-|sha|integrity", linha[max(0, m.start() - 15):m.start()]) and self.adicionar_unico(vistos, ("ip", v)):
                self.registrar(caminho, i, "ip", linha, v)

    def detectar_contexto(self, caminho, i, linha, tipo, vistos, rastreadores_vistos):
        eh_codigo = tipo == "codigo"
        if RE_CHAVE_PRIVADA.search(linha):
            self.registrar(caminho, i, "chave_privada", "-----BEGIN PRIVATE KEY-----")
        if eh_codigo or tipo == "texto":
            for r in RE_SEGREDOS:
                for m in r.finditer(linha):
                    v = m.group(m.lastindex)
                    if re.search(r"(?i)^(\$\{|process\.env|os\.environ|<|your|sua|seu|change|xxx|\*+|example|exemplo|placeholder|dummy|test|senha123|password)", v):
                        continue
                    if self.adicionar_unico(vistos, ("seg", v)):
                        self.registrar(caminho, i, "segredo_exposto", linha, v)
        if eh_codigo:
            if RE_LOG.search(linha):
                campos = set(m.group(1).lower() for m in RE_LOG_PII.finditer(linha.split("(", 1)[-1] if "(" in linha else linha))
                campos -= {"name", "user", "nome"} if not re.search(r"(?i)\b(user|usuario|cliente|customer|patient|paciente)\b\s*[),}]|\$\{\s*(user|usuario|cliente|customer)\s*\}|req\.body|request\.(body|data|json|form)|payload", linha) else set()
                if campos:
                    self.registrar(caminho, i, "pii_em_log", self.mascarar_trecho_geral(linha), detalhe="campos: " + ", ".join(sorted(campos)))
            if RE_ARMAZ_CLIENTE.search(linha) and RE_LOG_PII.search(linha):
                self.registrar(caminho, i, "armazenamento_cliente", self.mascarar_trecho_geral(linha))
            if RE_HASH_FRACO.search(linha) and RE_CONTEXTO_SENHA.search(linha):
                self.registrar(caminho, i, "hash_fraco", linha)
            if RE_TLS_OFF.search(linha):
                self.registrar(caminho, i, "tls_desabilitado", linha)
            m = RE_HTTP.search(linha)
            if m and not re.search(r"@(namespace|homepage|homepageURL|website|source|author)\b", linha) and self.adicionar_unico(vistos, ("http", m.group(0))):
                self.registrar(caminho, i, "transmissao_insegura", linha, detalhe=m.group(0))
            m = RE_ENVIO_EXTERNO.search(linha)
            if m and self.adicionar_unico(vistos, ("envio", linha.strip()[:80])):
                self.registrar(caminho, i, "envio_externo", self.mascarar_trecho_geral(linha), detalhe="verificar quais dados são enviados e a quem")
            if RE_GEO.search(linha) and self.adicionar_unico(vistos, ("geo", caminho)):
                self.registrar(caminho, i, "geolocalizacao", linha)
        if eh_codigo or tipo == "texto":
            for nome, r in RE_RASTREADORES:
                if nome not in rastreadores_vistos and r.search(linha):
                    rastreadores_vistos.add(nome)
                    self.registrar(caminho, i, "rastreador_terceiro", linha, detalhe=nome)
        m = RE_BIOMETRIA.search(linha)
        if m and self.adicionar_unico(vistos, ("bio", m.group(1).lower())):
            self.registrar(caminho, i, "biometria", self.mascarar_trecho_geral(linha), detalhe=m.group(1))
        for m in RE_SENSIVEL.finditer(linha):
            termo = m.group(1).lower()
            if self.adicionar_unico(vistos, ("sens", termo)):
                self.registrar(caminho, i, "campo_sensivel", self.mascarar_trecho_geral(linha), detalhe=f"termo: {termo}")
        m = RE_CRIANCA.search(linha)
        if m and self.adicionar_unico(vistos, ("crianca", m.group(1).lower())):
            self.registrar(caminho, i, "dados_criancas", self.mascarar_trecho_geral(linha), detalhe=f"termo: {m.group(1)}", severidade="info" if eh_codigo else None)
        m = RE_NASC.search(linha)
        if m and self.adicionar_unico(vistos, ("nasc", m.group(1).lower())):
            self.registrar(caminho, i, "data_nascimento", self.mascarar_trecho_geral(linha))
        if tipo in ("documento", "texto"):
            for r, desc in RE_ALERTAS:
                if r.search(linha) and self.adicionar_unico(vistos, ("jur", desc)):
                    self.registrar(caminho, i, "texto_juridico_alerta", self.mascarar_trecho_geral(linha), detalhe=desc)

    def percorrer(self, alvo):
        if os.path.isfile(alvo):
            self.analisar_arquivo(alvo)
            return
        for raiz, dirs, arquivos in os.walk(alvo):
            dirs[:] = sorted(d for d in dirs if d not in DIRETORIOS_IGNORADOS and (self.args.include_hidden or not d.startswith(".") or d in (".github", ".claude")))
            for nome in sorted(arquivos):
                caminho = os.path.join(raiz, nome)
                rel = os.path.relpath(caminho, alvo)
                if any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(nome, p) for p in self.args.exclude):
                    continue
                if os.path.islink(caminho):
                    continue
                self.analisar_arquivo(caminho, rel)


def resumo(achados):
    por_sev = Counter(a["severidade"] for a in achados)
    por_cat = Counter(a["categoria"] for a in achados)
    por_arq = Counter(a["arquivo"] for a in achados)
    return {
        "total": len(achados),
        "por_severidade": {s: por_sev.get(s, 0) for s in SEVERIDADES},
        "por_categoria": dict(por_cat.most_common()),
        "arquivos_mais_afetados": dict(por_arq.most_common(15)),
    }


def gerar_markdown(resultado):
    r = resultado["resumo"]
    out = []
    out.append("# Varredura de dados pessoais e riscos LGPD\n")
    out.append(f"- **Alvo:** {', '.join(resultado['alvos'])}")
    out.append(f"- **Data:** {resultado['data']}")
    out.append(f"- **Arquivos analisados:** {resultado['arquivos_analisados']} (ignorados: {resultado['arquivos_ignorados']})")
    out.append(f"- **Ocorrências:** {r['total']}")
    out.append("- **Valores:** " + ("exibidos sem máscara" if resultado["valores_expostos"] else "mascarados"))
    out.append("")
    out.append("## Por severidade\n")
    out.append("| Severidade | Ocorrências |\n|---|---|")
    for s in SEVERIDADES:
        out.append(f"| {s} | {r['por_severidade'][s]} |")
    out.append("\n## Por categoria\n")
    out.append("| Categoria | Ocorrências | Descrição | Fundamento |\n|---|---|---|---|")
    for c, n in r["por_categoria"].items():
        out.append(f"| {c} | {n} | {DESCRICOES[c]} | {'; '.join(ARTIGOS[c])} |")
    out.append("\n## Ocorrências\n")
    agrupado = defaultdict(list)
    for a in resultado["achados"]:
        agrupado[a["arquivo"]].append(a)
    for arquivo in sorted(agrupado, key=lambda k: min(ORDEM[a["severidade"]] for a in agrupado[k])):
        out.append(f"### `{arquivo}`\n")
        out.append("| Linha | Severidade | Categoria | Descrição | Trecho |\n|---|---|---|---|---|")
        for a in sorted(agrupado[arquivo], key=lambda x: (ORDEM[x["severidade"]], x["linha"])):
            trecho = a["trecho"].replace("|", "\\|").replace("`", "'")
            desc = a["descricao"].replace("|", "\\|")
            out.append(f"| {a['linha']} | {a['severidade']} | {a['categoria']} | {desc} | `{trecho}` |")
        out.append("")
    if resultado["erros"]:
        out.append("## Arquivos não analisados ou com aviso\n")
        for e in resultado["erros"]:
            out.append(f"- `{e['arquivo']}`: {e['erro']}")
        out.append("")
    out.append("## Observações\n")
    out.append("- Varredura automatizada por padrões: confirme cada ocorrência antes de reportá-la como violação. CPFs, CNPJs, PIS e cartões são validados por dígito verificador, mas podem ser dados de teste.")
    out.append("- A ausência de ocorrências não comprova conformidade: bases legais, finalidade, transparência e contratos exigem análise contextual.")
    out.append("- Esta saída contém indícios de dados pessoais; armazene-a com acesso restrito e elimine-a quando não for mais necessária.")
    return "\n".join(out) + "\n"


def main():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(description="Varredura de dados pessoais e riscos de conformidade com a LGPD.")
    p.add_argument("alvos", nargs="+", help="arquivos ou diretórios")
    p.add_argument("--format", choices=["md", "json"], default="md")
    p.add_argument("--output", help="arquivo de saída (padrão: stdout)")
    p.add_argument("--exclude", action="append", default=[], help="glob a ignorar (repetível)")
    p.add_argument("--min-severity", choices=SEVERIDADES, default="info")
    p.add_argument("--max-size-mb", type=float, default=10)
    p.add_argument("--include-hidden", action="store_true", help="incluir diretórios ocultos")
    p.add_argument("--show-values", action="store_true", help="exibir valores sem máscara")
    p.add_argument("--dump-text", action="store_true", help="apenas extrair e imprimir o texto dos arquivos (docx, xlsx, pptx, odt, pdf)")
    args = p.parse_args()

    if args.dump_text:
        for alvo in args.alvos:
            try:
                texto, _ = ler_texto(alvo, int(args.max_size_mb * 1024 * 1024))
            except Exception as e:
                print(f"[erro ao ler {alvo}: {e}]", file=sys.stderr)
                continue
            print(f"===== {alvo} =====")
            print(texto or "")
        return

    s = Scanner(args)
    for alvo in args.alvos:
        if not os.path.exists(alvo):
            print(f"Caminho não encontrado: {alvo}", file=sys.stderr)
            sys.exit(2)
        s.percorrer(alvo)

    limite = ORDEM[args.min_severity]
    achados = [a for a in s.achados if ORDEM[a["severidade"]] <= limite]
    achados.sort(key=lambda a: (ORDEM[a["severidade"]], a["arquivo"], a["linha"]))
    resultado = {
        "ferramenta": "lgpd-compliance/scan_pii.py",
        "raiz": os.path.abspath(args.alvos[0]) if len(args.alvos) == 1 and os.path.isdir(args.alvos[0]) else None,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "alvos": args.alvos,
        "arquivos_analisados": s.arquivos_analisados,
        "arquivos_ignorados": s.arquivos_ignorados,
        "valores_expostos": bool(args.show_values),
        "resumo": resumo(achados),
        "achados": achados,
        "erros": s.erros,
    }
    saida = json.dumps(resultado, ensure_ascii=False, indent=2) if args.format == "json" else gerar_markdown(resultado)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(saida)
        print(f"Relatório salvo em {args.output} ({resultado['resumo']['total']} ocorrências)", file=sys.stderr)
    else:
        sys.stdout.write(saida)


if __name__ == "__main__":
    main()
