#!/usr/bin/env python3
import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from html import escape

SEVERIDADES = ["critica", "alta", "media", "baixa", "info"]
ORDEM = {s: i for i, s in enumerate(SEVERIDADES)}
ROTULO_SEV = {"critica": "Crítica", "alta": "Alta", "media": "Média", "baixa": "Baixa", "info": "Informativa"}
PESO = {"critica": 25, "alta": 10, "media": 4, "baixa": 1, "info": 0}
PRAZO = {"critica": "Imediato (até 7 dias)", "alta": "30 dias", "media": "90 dias", "baixa": "180 dias", "info": "—"}
PI_PADRAO = {"critica": (5, 5), "alta": (4, 4), "media": (3, 3), "baixa": (2, 2), "info": (1, 1)}
ROTULO_TIPO = {"automatica": "Automática", "documento": "Documento", "decisao": "Decisão", "manual": "Manual"}
ROTULO_STATUS = {
    "aberto": "Aberto", "em_andamento": "Em andamento", "resolvido": "Resolvido", "requer_decisao": "Requer decisão",
    "manual": "Ação manual", "nao_aplicado": "Não aplicado", "aceito": "Risco aceito",
}
ROTULO_DOMINIO = {
    "governanca": "Governança",
    "transparencia": "Transparência",
    "bases_legais": "Bases legais",
    "direitos_titular": "Direitos do titular",
    "seguranca": "Segurança",
    "terceiros": "Terceiros e operadores",
    "transferencia_internacional": "Transferência internacional",
    "retencao": "Retenção e eliminação",
    "sensiveis_criancas": "Dados sensíveis e de crianças",
    "documentacao": "Documentação",
    "outros": "Outros",
}
DOMINIO_POR_CATEGORIA = {
    "cpf": "seguranca", "cnpj": "seguranca", "cartao_credito": "seguranca", "email": "seguranca",
    "telefone": "seguranca", "cep": "seguranca", "rg": "seguranca", "pis": "seguranca",
    "titulo_eleitor": "seguranca", "ip": "seguranca", "data_nascimento": "sensiveis_criancas",
    "cns": "sensiveis_criancas", "campo_sensivel": "sensiveis_criancas", "dados_criancas": "sensiveis_criancas",
    "biometria": "sensiveis_criancas", "pii_em_log": "seguranca", "segredo_exposto": "seguranca",
    "chave_privada": "seguranca", "rastreador_terceiro": "transferencia_internacional",
    "armazenamento_cliente": "seguranca", "transmissao_insegura": "seguranca", "hash_fraco": "seguranca",
    "tls_desabilitado": "seguranca", "envio_externo": "terceiros", "geolocalizacao": "bases_legais",
    "texto_juridico_alerta": "transparencia", "arquivo_sensivel": "seguranca",
    "resposta_entidade_completa": "seguranca", "credencial_em_resposta": "seguranca",
    "erro_detalhado_exposto": "seguranca", "pii_na_url": "seguranca",
    "documentacao_api_exposta": "seguranca", "cors_permissivo": "seguranca",
}
RECOMENDACOES_SCAN = {
    "cpf": "Confirmar se são dados reais. Remover do arquivo/repositório, substituir por dados sintéticos e, se versionado, limpar histórico e avaliar incidente.",
    "cartao_credito": "Remover imediatamente; nunca armazenar PAN/CVV fora de ambiente PCI. Usar tokenização do gateway. Avaliar incidente.",
    "email": "Verificar se são dados de titulares reais; minimizar e evitar exposição em código, logs e documentos.",
    "telefone": "Verificar se são dados reais; minimizar e evitar exposição.",
    "rg": "Remover documentos de identificação de arquivos não controlados; criptografar quando necessário.",
    "pis": "Remover ou proteger; dado trabalhista com acesso restrito.",
    "titulo_eleitor": "Remover ou proteger; coletar apenas se houver base legal.",
    "cns": "Dado vinculado à saúde: base do art. 11, criptografia e acesso restrito.",
    "ip": "Avaliar se o IP está associado a titulares; definir retenção (Marco Civil: 6 meses para registros de acesso).",
    "cep": "Avaliar necessidade; combinado com outros dados reidentifica titulares.",
    "cnpj": "Normalmente não é dado pessoal; verificar se identifica empresário individual/MEI.",
    "data_nascimento": "Avaliar necessidade (faixa etária ou verificação de maioridade costuma bastar); atenção a menores de idade.",
    "campo_sensivel": "Confirmar se há tratamento de dado sensível; aplicar hipótese do art. 11, criptografia de campo, acesso restrito e RIPD.",
    "dados_criancas": "Confirmar tratamento de dados de crianças/adolescentes; observar art. 14 (melhor interesse, consentimento parental quando aplicável).",
    "biometria": "Biometria é dado sensível: hipótese do art. 11 (ex.: II, g), transparência, alternativa não biométrica e RIPD.",
    "pii_em_log": "Remover dados pessoais das mensagens de log ou aplicar redação automática; definir retenção dos logs.",
    "segredo_exposto": "Mover para gerenciador de segredos/variáveis de ambiente e ROTACIONAR a credencial; remover do histórico do git.",
    "chave_privada": "Revogar e substituir a chave; remover do repositório e do histórico.",
    "rastreador_terceiro": "Carregar somente após consentimento (CMP), informar na política de cookies/privacidade e verificar mecanismo de transferência internacional (art. 33; Res. 19/2024).",
    "armazenamento_cliente": "Evitar persistir dados pessoais/tokens no navegador; usar cookies HttpOnly/Secure ou armazenamento no servidor.",
    "transmissao_insegura": "Usar HTTPS em todas as comunicações que trafeguem dados pessoais.",
    "hash_fraco": "Substituir por Argon2id/bcrypt/scrypt para senhas; HMAC-SHA256 com segredo para pseudonimização.",
    "tls_desabilitado": "Reativar a validação de certificados TLS.",
    "envio_externo": "Identificar quais dados são enviados, ao destinatário e finalidade; informar o titular e formalizar contrato/mecanismo de transferência.",
    "geolocalizacao": "Coletar somente com finalidade clara, transparência e base legal; preferir precisão reduzida e coleta sob demanda.",
    "texto_juridico_alerta": "Revisar a redação conforme references/documentos-juridicos.md (seção 14).",
    "arquivo_sensivel": "Verificar se o arquivo deveria estar versionado/compartilhado; remover e proteger se contiver dados ou credenciais.",
    "resposta_entidade_completa": "Devolver DTO específico por caso de uso com apenas os campos necessários, usando projeção na consulta; mascarar documentos e restringir dados sensíveis por perfil.",
    "credencial_em_resposta": "Remover credenciais e segredos das classes de saída e excluí-los da serialização ([JsonIgnore], @Exclude, $hidden, write_only).",
    "erro_detalhado_exposto": "Devolver erros genéricos ao cliente (com traceId) e registrar detalhes apenas no log, sem dados pessoais; desativar páginas de exceção e modo debug fora de desenvolvimento.",
    "pii_na_url": "Usar identificador interno na rota e enviar documentos/e-mail no corpo de requisições POST.",
    "documentacao_api_exposta": "Restringir Swagger/OpenAPI e introspecção do GraphQL a desenvolvimento ou exigir autenticação.",
    "cors_permissivo": "Restringir CORS às origens conhecidas, principalmente em endpoints autenticados.",
}


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def converter_scan(scan, args):
    grupos = defaultdict(list)
    for a in scan.get("achados", []):
        grupos[a["categoria"]].append(a)
    achados = []
    for categoria, itens in grupos.items():
        sev = min((i["severidade"] for i in itens), key=lambda s: ORDEM[s])
        arquivos = Counter(i["arquivo"] for i in itens)
        locais = [f"{arq} ({n})" for arq, n in arquivos.most_common(10)]
        if len(arquivos) > 10:
            locais.append(f"… e mais {len(arquivos) - 10} arquivo(s)")
        exemplos = [f"{i['arquivo']}:{i['linha']} — {i['trecho']}" for i in sorted(itens, key=lambda x: ORDEM[x["severidade"]])[:5]]
        achados.append({
            "titulo": itens[0]["descricao"].split(" — ")[0],
            "categoria": categoria,
            "dominio": DOMINIO_POR_CATEGORIA.get(categoria, "outros"),
            "severidade": sev,
            "artigos": itens[0].get("artigos", []),
            "local": "; ".join(locais),
            "evidencia": "\n".join(exemplos),
            "descricao": f"{len(itens)} ocorrência(s) em {len(arquivos)} arquivo(s) identificadas por varredura automatizada.",
            "recomendacao": RECOMENDACOES_SCAN.get(categoria, "Revisar ocorrências."),
            "tipo_correcao": "manual" if categoria in ("segredo_exposto", "chave_privada") else "automatica",
            "status": "aberto",
        })
    return {
        "metadados": {
            "titulo": args.titulo or "Relatório de Varredura — Dados Pessoais e Riscos LGPD",
            "organizacao": args.organizacao or "",
            "escopo": ", ".join(scan.get("alvos", [])),
            "data": date.today().isoformat(),
            "responsavel": args.responsavel or "",
        },
        "metodologia": f"Varredura automatizada por padrões (scan_pii.py) em {scan.get('arquivos_analisados', 0)} arquivo(s). Identificadores numéricos validados por dígito verificador. Ocorrências requerem confirmação manual.",
        "achados": achados,
    }


def normalizar(dados, args):
    if "achados" in dados and dados.get("ferramenta", "").endswith("scan_pii.py"):
        dados = converter_scan(dados, args)
    meta = dados.setdefault("metadados", {})
    if args.titulo:
        meta["titulo"] = args.titulo
    if args.organizacao:
        meta["organizacao"] = args.organizacao
    if args.responsavel:
        meta["responsavel"] = args.responsavel
    meta.setdefault("titulo", "Diagnóstico de Conformidade com a LGPD")
    meta.setdefault("data", date.today().isoformat())
    achados = dados.setdefault("achados", [])
    for n, a in enumerate(achados, 1):
        sev = str(a.get("severidade", "media")).lower().replace("í", "i").replace("é", "e")
        if sev not in ORDEM:
            sev = {"critical": "critica", "high": "alta", "medium": "media", "low": "baixa", "informativa": "info"}.get(sev, "media")
        a["severidade"] = sev
        a.setdefault("id", f"A{n:02d}")
        a.setdefault("dominio", DOMINIO_POR_CATEGORIA.get(a.get("categoria", ""), "outros"))
        a.setdefault("status", "aberto")
        a.setdefault("prazo", PRAZO[sev])
        a.setdefault("tipo_correcao", "")
        a.setdefault("historico", [])
        p, i = PI_PADRAO[sev]
        a["probabilidade"] = int(a.get("probabilidade") or p)
        a["impacto"] = int(a.get("impacto") or i)
        if isinstance(a.get("artigos"), str):
            a["artigos"] = [a["artigos"]]
        a.setdefault("artigos", [])
    achados.sort(key=lambda a: (ORDEM[a["severidade"]], -a["probabilidade"] * a["impacto"], a["id"]))
    return dados


def indicador(achados):
    abertos = [a for a in achados if a.get("status") not in ("resolvido", "aceito")]
    penalidade = sum(PESO[a["severidade"]] for a in abertos)
    valor = max(0, 100 - penalidade)
    if any(a["severidade"] == "critica" for a in abertos):
        valor = min(valor, 40)
    if valor >= 85:
        faixa = "Adequado com ressalvas pontuais"
    elif valor >= 65:
        faixa = "Parcialmente adequado"
    elif valor >= 40:
        faixa = "Baixa conformidade"
    else:
        faixa = "Não conforme — ação prioritária"
    return valor, faixa


def nivel_risco(score):
    if score >= 15:
        return "Crítico"
    if score >= 10:
        return "Alto"
    if score >= 5:
        return "Médio"
    return "Baixo"


def matriz(achados):
    celulas = defaultdict(list)
    for a in achados:
        if a["severidade"] == "info":
            continue
        celulas[(a["probabilidade"], a["impacto"])].append(a["id"])
    return celulas


AVISO = "Este relatório é um apoio técnico à conformidade com a LGPD e não substitui parecer jurídico elaborado por advogado habilitado. Contém informações sobre vulnerabilidades e dados pessoais mascarados: mantenha-o com acesso restrito."


def rotulo_status(a):
    return ROTULO_STATUS.get(a["status"], a["status"])


def contagem_status(achados):
    return Counter(a["status"] for a in achados)


def eventos_correcao(achados):
    eventos = []
    for a in achados:
        for ev in a.get("historico", []):
            if ev.get("nota") == "análise registrada":
                continue
            eventos.append((ev.get("data", ""), a["id"], ev))
    eventos.sort(key=lambda x: (x[0], x[1]))
    return eventos


def md_cel(texto):
    return str(texto or "").replace("|", "\\|").replace("\n", "<br>")


def gerar_md(d):
    meta = d["metadados"]
    achados = d["achados"]
    valor, faixa = indicador(achados)
    cont = Counter(a["severidade"] for a in achados)
    out = [f"# {meta['titulo']}", ""]
    for chave, rotulo in (("organizacao", "Organização"), ("escopo", "Escopo"), ("data", "Data"), ("responsavel", "Responsável"), ("papel_agente", "Papel do agente"), ("versao", "Versão"), ("confidencialidade", "Classificação")):
        if meta.get(chave):
            out.append(f"- **{rotulo}:** {meta[chave]}")
    out += ["", "## Sumário executivo", ""]
    if d.get("resumo_executivo"):
        out += [d["resumo_executivo"], ""]
    out.append(f"**Indicador de conformidade:** {valor}/100 — {faixa} *(indicador interno heurístico, não oficial)*")
    out.append("")
    out.append("| Severidade | Achados |\n|---|---|")
    for s in SEVERIDADES:
        out.append(f"| {ROTULO_SEV[s]} | {cont.get(s, 0)} |")
    st = contagem_status(achados)
    if set(st) - {"aberto"}:
        out += ["", "| Status | Achados |", "|---|---|"] + [f"| {ROTULO_STATUS.get(k, k)} | {v} |" for k, v in st.most_common()]
    principais = [a for a in achados if a["severidade"] in ("critica", "alta") and a["status"] not in ("resolvido", "aceito")][:5]
    if principais:
        out += ["", "**Principais riscos pendentes:**", ""]
        for a in principais:
            out.append(f"- **[{a['id']}] {a['titulo']}** ({ROTULO_SEV[a['severidade']]})")
    if d.get("metodologia"):
        out += ["", "## Escopo e metodologia", "", d["metodologia"]]
    out += ["", "## Distribuição por domínio", "", "| Domínio | " + " | ".join(ROTULO_SEV[s] for s in SEVERIDADES) + " | Total |", "|---|" + "---|" * (len(SEVERIDADES) + 1)]
    por_dom = defaultdict(Counter)
    for a in achados:
        por_dom[a["dominio"]][a["severidade"]] += 1
    for dom, c in sorted(por_dom.items(), key=lambda x: -sum(x[1].values())):
        out.append(f"| {ROTULO_DOMINIO.get(dom, dom)} | " + " | ".join(str(c.get(s, 0)) for s in SEVERIDADES) + f" | {sum(c.values())} |")
    cel = matriz(achados)
    out += ["", "## Matriz de risco (probabilidade × impacto)", "", "| Probabilidade \\ Impacto | 1 | 2 | 3 | 4 | 5 |", "|---|---|---|---|---|---|"]
    for p in range(5, 0, -1):
        out.append(f"| **{p}** | " + " | ".join(", ".join(cel.get((p, i), [])) or "·" for i in range(1, 6)) + " |")
    out += ["", "## Achados detalhados", ""]
    for a in achados:
        out.append(f"### [{a['id']}] {a['titulo']}")
        out.append("")
        out.append(f"- **Severidade:** {ROTULO_SEV[a['severidade']]} · **Risco:** {nivel_risco(a['probabilidade'] * a['impacto'])} (P{a['probabilidade']} × I{a['impacto']}) · **Domínio:** {ROTULO_DOMINIO.get(a['dominio'], a['dominio'])} · **Status:** {rotulo_status(a)}" + (f" · **Correção:** {ROTULO_TIPO.get(a['tipo_correcao'], a['tipo_correcao'])}" if a.get("tipo_correcao") else ""))
        if a["artigos"]:
            out.append(f"- **Fundamento:** {'; '.join(a['artigos'])}")
        if a.get("local"):
            out.append(f"- **Local:** {a['local']}")
        if a.get("descricao"):
            out += ["", a["descricao"]]
        if a.get("evidencia"):
            out += ["", "**Evidência:**", "", "```", a["evidencia"], "```"]
        if a.get("recomendacao"):
            out += ["", f"**Recomendação:** {a['recomendacao']}"]
        if a.get("correcao"):
            out += ["", "**Correção proposta:**", "", "```", a["correcao"], "```"]
        out.append("")
    out += ["## Plano de ação", "", "| ID | Ação | Severidade | Tipo | Prazo | Responsável | Status |", "|---|---|---|---|---|---|---|"]
    for a in achados:
        if a["severidade"] == "info":
            continue
        out.append(f"| {a['id']} | {md_cel(a.get('recomendacao') or a['titulo'])} | {ROTULO_SEV[a['severidade']]} | {ROTULO_TIPO.get(a['tipo_correcao'], a['tipo_correcao'] or '—')} | {md_cel(a.get('prazo'))} | {md_cel(a.get('responsavel', 'A definir'))} | {rotulo_status(a)} |")
    eventos = eventos_correcao(achados)
    if eventos:
        out += ["", "## Histórico de correções", "", "| Data | ID | Status | Nota | Arquivos |", "|---|---|---|---|---|"]
        for data, ident, ev in eventos:
            out.append(f"| {data} | {ident} | {ROTULO_STATUS.get(ev.get('status'), ev.get('status'))} | {md_cel(ev.get('nota'))} | {md_cel(', '.join(ev.get('arquivos_alterados', [])))} |")
    if d.get("pontos_positivos"):
        out += ["", "## Pontos positivos", ""] + [f"- {p}" for p in d["pontos_positivos"]]
    if d.get("proximos_passos"):
        out += ["", "## Próximos passos", ""] + [f"{n}. {p}" for n, p in enumerate(d["proximos_passos"], 1)]
    out += ["", "---", "", f"*{AVISO}*", ""]
    return "\n".join(out)


CSS = """
:root{--bg:#ffffff;--fg:#1d2330;--muted:#5b6475;--card:#f5f7fa;--line:#dde2ea;--accent:#1f5fbf;
--critica:#b42318;--alta:#d9480f;--media:#b08800;--baixa:#2b7a3d;--info:#5b6475}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#12151b;--fg:#e6e9ef;--muted:#9aa3b2;--card:#1b2029;--line:#2c3340;--accent:#6ea2ff;
--critica:#ff6b5e;--alta:#ff8f4d;--media:#e3c04a;--baixa:#5fcf7a;--info:#9aa3b2}}
:root[data-theme="dark"]{--bg:#12151b;--fg:#e6e9ef;--muted:#9aa3b2;--card:#1b2029;--line:#2c3340;--accent:#6ea2ff;
--critica:#ff6b5e;--alta:#ff8f4d;--media:#e3c04a;--baixa:#5fcf7a;--info:#9aa3b2}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1040px;margin:0 auto;padding:32px 16px 64px}h1{font-size:1.8rem;margin:0 0 8px}h2{margin-top:40px;border-bottom:1px solid var(--line);padding-bottom:6px}
h3{margin:0 0 8px;font-size:1.05rem}.meta{color:var(--muted);display:flex;flex-wrap:wrap;gap:4px 18px;margin-bottom:16px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}.card b{display:block;font-size:1.6rem}
.score{font-size:2.4rem;font-weight:700}.pill{display:inline-block;border-radius:999px;padding:1px 10px;font-size:.8rem;font-weight:600;color:#fff}
.critica{background:var(--critica)}.alta{background:var(--alta)}.media{background:var(--media)}.baixa{background:var(--baixa)}.info{background:var(--info)}
.t-critica{color:var(--critica)}.t-alta{color:var(--alta)}.t-media{color:var(--media)}.t-baixa{color:var(--baixa)}.t-info{color:var(--info)}
.tbl{overflow-x:auto}table{border-collapse:collapse;width:100%;margin:12px 0}th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:var(--card)}.mx td{text-align:center;width:16%;height:44px}.mx th{text-align:center}
.r1{background:rgba(43,122,61,.18)}.r2{background:rgba(176,136,0,.2)}.r3{background:rgba(217,72,15,.22)}.r4{background:rgba(180,35,24,.3)}
.achado{border:1px solid var(--line);border-left:5px solid var(--line);border-radius:8px;padding:14px 16px;margin:14px 0;background:var(--card)}
.achado.s-critica{border-left-color:var(--critica)}.achado.s-alta{border-left-color:var(--alta)}.achado.s-media{border-left-color:var(--media)}.achado.s-baixa{border-left-color:var(--baixa)}
pre{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:10px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;font-size:.85rem}
.aviso{margin-top:40px;color:var(--muted);font-size:.85rem;border-top:1px solid var(--line);padding-top:12px}
@media print{body{background:#fff;color:#000}.achado{break-inside:avoid}h2{break-after:avoid}}
"""


def gerar_html(d):
    meta = d["metadados"]
    achados = d["achados"]
    valor, faixa = indicador(achados)
    cont = Counter(a["severidade"] for a in achados)
    e = lambda x: escape(str(x or ""))
    h = ["<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
         f"<title>{e(meta['titulo'])}</title><style>{CSS}</style></head><body><main>"]
    h.append(f"<h1>{e(meta['titulo'])}</h1><div class=\"meta\">")
    for chave, rotulo in (("organizacao", "Organização"), ("escopo", "Escopo"), ("data", "Data"), ("responsavel", "Responsável"), ("papel_agente", "Papel do agente"), ("versao", "Versão"), ("confidencialidade", "Classificação")):
        if meta.get(chave):
            h.append(f"<span><b>{rotulo}:</b> {e(meta[chave])}</span>")
    h.append("</div><h2>Sumário executivo</h2>")
    if d.get("resumo_executivo"):
        h.append(f"<p>{e(d['resumo_executivo'])}</p>")
    h.append(f"<div class=\"cards\"><div class=\"card\"><span>Indicador de conformidade</span><div class=\"score\">{valor}<small>/100</small></div><small>{e(faixa)}</small></div>")
    for s in SEVERIDADES:
        h.append(f"<div class=\"card\"><span class=\"t-{s}\">{ROTULO_SEV[s]}</span><b>{cont.get(s, 0)}</b></div>")
    h.append("</div><p><small>Indicador interno heurístico, não oficial.</small></p>")
    st = contagem_status(achados)
    if set(st) - {"aberto"}:
        h.append("<div class=\"cards\">" + "".join(f"<div class=\"card\"><span>{e(ROTULO_STATUS.get(k, k))}</span><b>{v}</b></div>" for k, v in st.most_common()) + "</div>")
    principais = [a for a in achados if a["severidade"] in ("critica", "alta") and a["status"] not in ("resolvido", "aceito")][:5]
    if principais:
        h.append("<p><b>Principais riscos pendentes:</b></p><ul>" + "".join(f"<li><b>[{e(a['id'])}]</b> {e(a['titulo'])} <span class=\"pill {a['severidade']}\">{ROTULO_SEV[a['severidade']]}</span></li>" for a in principais) + "</ul>")
    if d.get("metodologia"):
        h.append(f"<h2>Escopo e metodologia</h2><p>{e(d['metodologia'])}</p>")
    por_dom = defaultdict(Counter)
    for a in achados:
        por_dom[a["dominio"]][a["severidade"]] += 1
    h.append("<h2>Distribuição por domínio</h2><div class=\"tbl\"><table><tr><th>Domínio</th>" + "".join(f"<th>{ROTULO_SEV[s]}</th>" for s in SEVERIDADES) + "<th>Total</th></tr>")
    for dom, c in sorted(por_dom.items(), key=lambda x: -sum(x[1].values())):
        h.append(f"<tr><td>{e(ROTULO_DOMINIO.get(dom, dom))}</td>" + "".join(f"<td>{c.get(s, 0)}</td>" for s in SEVERIDADES) + f"<td><b>{sum(c.values())}</b></td></tr>")
    h.append("</table></div>")
    cel = matriz(achados)
    h.append("<h2>Matriz de risco</h2><div class=\"tbl\"><table class=\"mx\"><tr><th>Probabilidade \\ Impacto</th>" + "".join(f"<th>{i}</th>" for i in range(1, 6)) + "</tr>")
    for p in range(5, 0, -1):
        linha = f"<tr><th>{p}</th>"
        for i in range(1, 6):
            sc = p * i
            classe = "r4" if sc >= 15 else "r3" if sc >= 10 else "r2" if sc >= 5 else "r1"
            linha += f"<td class=\"{classe}\">{e(', '.join(cel.get((p, i), [])))}</td>"
        h.append(linha + "</tr>")
    h.append("</table></div><h2>Achados detalhados</h2>")
    for a in achados:
        s = a["severidade"]
        h.append(f"<div class=\"achado s-{s}\"><h3>[{e(a['id'])}] {e(a['titulo'])} <span class=\"pill {s}\">{ROTULO_SEV[s]}</span></h3>")
        h.append(f"<div class=\"meta\"><span><b>Risco:</b> {nivel_risco(a['probabilidade'] * a['impacto'])} (P{a['probabilidade']}×I{a['impacto']})</span><span><b>Domínio:</b> {e(ROTULO_DOMINIO.get(a['dominio'], a['dominio']))}</span><span><b>Status:</b> {e(rotulo_status(a))}</span><span><b>Correção:</b> {e(ROTULO_TIPO.get(a['tipo_correcao'], a['tipo_correcao'] or '—'))}</span><span><b>Prazo:</b> {e(a.get('prazo'))}</span></div>")
        if a["artigos"]:
            h.append(f"<p><b>Fundamento:</b> {e('; '.join(a['artigos']))}</p>")
        if a.get("local"):
            h.append(f"<p><b>Local:</b> {e(a['local'])}</p>")
        if a.get("descricao"):
            h.append(f"<p>{e(a['descricao'])}</p>")
        if a.get("evidencia"):
            h.append(f"<p><b>Evidência:</b></p><pre>{e(a['evidencia'])}</pre>")
        if a.get("recomendacao"):
            h.append(f"<p><b>Recomendação:</b> {e(a['recomendacao'])}</p>")
        if a.get("correcao"):
            h.append(f"<p><b>Correção proposta:</b></p><pre>{e(a['correcao'])}</pre>")
        h.append("</div>")
    h.append("<h2>Plano de ação</h2><div class=\"tbl\"><table><tr><th>ID</th><th>Ação</th><th>Severidade</th><th>Tipo</th><th>Prazo</th><th>Responsável</th><th>Status</th></tr>")
    for a in achados:
        if a["severidade"] == "info":
            continue
        h.append(f"<tr><td>{e(a['id'])}</td><td>{e(a.get('recomendacao') or a['titulo'])}</td><td><span class=\"pill {a['severidade']}\">{ROTULO_SEV[a['severidade']]}</span></td><td>{e(ROTULO_TIPO.get(a['tipo_correcao'], a['tipo_correcao'] or '—'))}</td><td>{e(a.get('prazo'))}</td><td>{e(a.get('responsavel', 'A definir'))}</td><td>{e(rotulo_status(a))}</td></tr>")
    h.append("</table></div>")
    eventos = eventos_correcao(achados)
    if eventos:
        h.append("<h2>Histórico de correções</h2><div class=\"tbl\"><table><tr><th>Data</th><th>ID</th><th>Status</th><th>Nota</th><th>Arquivos</th></tr>")
        for data, ident, ev in eventos:
            h.append(f"<tr><td>{e(data)}</td><td>{e(ident)}</td><td>{e(ROTULO_STATUS.get(ev.get('status'), ev.get('status')))}</td><td>{e(ev.get('nota'))}</td><td>{e(', '.join(ev.get('arquivos_alterados', [])))}</td></tr>")
        h.append("</table></div>")
    if d.get("pontos_positivos"):
        h.append("<h2>Pontos positivos</h2><ul>" + "".join(f"<li>{e(p)}</li>" for p in d["pontos_positivos"]) + "</ul>")
    if d.get("proximos_passos"):
        h.append("<h2>Próximos passos</h2><ol>" + "".join(f"<li>{e(p)}</li>" for p in d["proximos_passos"]) + "</ol>")
    h.append(f"<p class=\"aviso\">{e(AVISO)}</p></main></body></html>")
    return "\n".join(h)


def main():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(description="Gera relatório de conformidade LGPD (Markdown/HTML) a partir de achados JSON ou da saída do scan_pii.py.")
    p.add_argument("entrada", help="arquivo JSON de achados ou saída JSON do scan_pii.py")
    p.add_argument("--output", default="relatorio-lgpd", help="caminho base de saída, sem extensão")
    p.add_argument("--format", default="md,html", help="md, html ou md,html")
    p.add_argument("--titulo")
    p.add_argument("--organizacao")
    p.add_argument("--responsavel")
    args = p.parse_args()

    dados = normalizar(carregar(args.entrada), args)
    formatos = [f.strip() for f in args.format.split(",") if f.strip()]
    for fmt in formatos:
        if fmt not in ("md", "html"):
            print(f"Formato não suportado: {fmt}", file=sys.stderr)
            sys.exit(2)
        conteudo = gerar_md(dados) if fmt == "md" else gerar_html(dados)
        destino = f"{args.output}.{fmt}"
        with open(destino, "w", encoding="utf-8") as f:
            f.write(conteudo)
        print(f"Gerado: {destino}")
    valor, faixa = indicador(dados["achados"])
    print(f"Achados: {len(dados['achados'])} | Indicador: {valor}/100 ({faixa})")


if __name__ == "__main__":
    main()
