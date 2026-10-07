#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

VERSAO = "1.2.0"
PASTA_PADRAO = ".lgpd-compliance"
SEVERIDADES = ["critica", "alta", "media", "baixa", "info"]
ORDEM = {s: i for i, s in enumerate(SEVERIDADES)}
TIPOS = ["automatica", "documento", "decisao", "manual"]
STATUS = ["aberto", "em_andamento", "resolvido", "requer_decisao", "manual", "nao_aplicado", "aceito"]
STATUS_PENDENTES = {"aberto", "em_andamento", "requer_decisao"}


def configurar_saida():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def pasta_analise(alvo, saida=None):
    if saida:
        return os.path.abspath(saida)
    base = alvo if os.path.isdir(alvo) else os.path.dirname(os.path.abspath(alvo))
    return os.path.join(os.path.abspath(base), PASTA_PADRAO)


def raiz_do_alvo(alvo):
    return os.path.abspath(alvo if os.path.isdir(alvo) else os.path.dirname(os.path.abspath(alvo)))


def hash_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def resolver(arquivo, raiz):
    if not arquivo:
        return None
    return arquivo if os.path.isabs(arquivo) else os.path.join(raiz, arquivo)


def dentro(caminho, raiz):
    try:
        return os.path.commonpath([os.path.abspath(caminho), raiz]) == raiz
    except ValueError:
        return False


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def salvar(caminho, dados):
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    os.replace(temporario, caminho)


def garantir_gitignore(pasta):
    destino = os.path.join(pasta, ".gitignore")
    if not os.path.exists(destino):
        with open(destino, "w", encoding="utf-8") as f:
            f.write("*\n")


def situacao_arquivo(achado, raiz):
    caminho = resolver(achado.get("arquivo"), raiz)
    if not caminho:
        return "sem_arquivo"
    if not os.path.isfile(caminho):
        return "removido"
    if not achado.get("hash_arquivo"):
        return "sem_hash"
    return "inalterado" if hash_arquivo(caminho) == achado["hash_arquivo"] else "alterado"


def cmd_verificar(args):
    pasta = pasta_analise(args.alvo, args.saida)
    caminho = os.path.join(pasta, "analise.json")
    resultado = {
        "alvo": os.path.abspath(args.alvo),
        "pasta_analise": pasta,
        "existe": os.path.isfile(caminho),
        "scan_existe": os.path.isfile(os.path.join(pasta, "scan.json")),
    }
    if resultado["existe"]:
        dados = carregar(caminho)
        meta = dados.get("metadados", {})
        raiz = meta.get("raiz") or raiz_do_alvo(args.alvo)
        achados = dados.get("achados", [])
        desatualizados = []
        for a in achados:
            if a.get("status") not in STATUS_PENDENTES:
                continue
            s = situacao_arquivo(a, raiz)
            if s in ("alterado", "removido"):
                desatualizados.append({"id": a.get("id"), "arquivo": a.get("arquivo"), "situacao": s})
        resultado.update({
            "analise": caminho,
            "data_analise": meta.get("data_analise") or meta.get("data"),
            "versao_skill": meta.get("versao_skill"),
            "total": len(achados),
            "por_status": dict(Counter(a.get("status", "aberto") for a in achados)),
            "pendentes_por_severidade": dict(Counter(a.get("severidade") for a in achados if a.get("status", "aberto") in STATUS_PENDENTES)),
            "desatualizados": desatualizados,
        })
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


def cmd_selar(args):
    dados = carregar(args.analise)
    pasta = os.path.dirname(os.path.abspath(args.analise))
    raiz = os.path.abspath(args.raiz)
    meta = dados.setdefault("metadados", {})
    meta["raiz"] = raiz
    meta["data_analise"] = agora()
    meta["versao_skill"] = VERSAO
    meta.setdefault("data", datetime.now().strftime("%Y-%m-%d"))
    avisos = []
    for n, a in enumerate(dados.setdefault("achados", []), 1):
        a.setdefault("id", f"A{n:02d}")
        a.setdefault("status", "aberto")
        tipo = a.get("tipo_correcao")
        if tipo not in TIPOS:
            if tipo:
                avisos.append(f"{a['id']}: tipo_correcao inválido '{tipo}', usando 'manual'")
            a["tipo_correcao"] = "automatica" if not tipo and a.get("arquivo") and a.get("correcao") else "manual"
        caminho = resolver(a.get("arquivo"), raiz)
        if caminho and os.path.isfile(caminho):
            if os.path.isabs(a["arquivo"]) and dentro(caminho, raiz):
                a["arquivo"] = os.path.relpath(caminho, raiz)
            a["hash_arquivo"] = hash_arquivo(caminho)
        elif caminho:
            avisos.append(f"{a['id']}: arquivo não encontrado ({a.get('arquivo')})")
        if not a.get("historico"):
            a["historico"] = [{"data": agora(), "status": a["status"], "nota": "análise registrada"}]
    ids = [a["id"] for a in dados["achados"]]
    duplicados = [i for i, c in Counter(ids).items() if c > 1]
    if duplicados:
        avisos.append("IDs duplicados: " + ", ".join(duplicados))
    salvar(args.analise, dados)
    garantir_gitignore(pasta)
    print(json.dumps({"analise": os.path.abspath(args.analise), "achados": len(dados["achados"]), "avisos": avisos}, ensure_ascii=False, indent=2))


def cmd_pendentes(args):
    dados = carregar(args.analise)
    raiz = dados.get("metadados", {}).get("raiz") or os.path.dirname(os.path.dirname(os.path.abspath(args.analise)))
    limite = ORDEM[args.severidade]
    ids = {i.strip() for i in args.ids.split(",")} if args.ids else None
    grupos = defaultdict(list)
    for a in dados.get("achados", []):
        if a.get("status", "aberto") not in STATUS_PENDENTES:
            continue
        if ORDEM.get(a.get("severidade"), 2) > limite:
            continue
        if ids and a.get("id") not in ids:
            continue
        grupos[a.get("tipo_correcao", "manual")].append({
            "id": a.get("id"),
            "severidade": a.get("severidade"),
            "titulo": a.get("titulo"),
            "arquivo": a.get("arquivo"),
            "linha": a.get("linha"),
            "situacao_arquivo": situacao_arquivo(a, raiz),
            "status": a.get("status", "aberto"),
        })
    for itens in grupos.values():
        itens.sort(key=lambda x: (ORDEM.get(x["severidade"], 2), x["id"] or ""))
    saida = {t: grupos.get(t, []) for t in TIPOS if grupos.get(t)}
    saida["total"] = sum(len(v) for v in grupos.values())
    if ids:
        encontrados = {x["id"] for v in grupos.values() for x in v}
        faltando = sorted(ids - encontrados)
        if faltando:
            saida["ids_nao_pendentes_ou_inexistentes"] = faltando
    print(json.dumps(saida, ensure_ascii=False, indent=2))


def cmd_marcar(args):
    if args.status not in STATUS:
        print(f"Status inválido: {args.status}. Use: {', '.join(STATUS)}", file=sys.stderr)
        sys.exit(2)
    dados = carregar(args.analise)
    raiz = os.path.abspath(args.raiz) if args.raiz else dados.get("metadados", {}).get("raiz")
    alvos = {i.strip() for grupo in args.id for i in grupo.split(",")}
    atualizados = []
    for a in dados.get("achados", []):
        if a.get("id") not in alvos:
            continue
        a["status"] = args.status
        evento = {"data": agora(), "status": args.status}
        if args.nota:
            evento["nota"] = args.nota
        if args.arquivos:
            evento["arquivos_alterados"] = args.arquivos
        a.setdefault("historico", []).append(evento)
        caminho = resolver(a.get("arquivo"), raiz) if raiz else None
        if caminho and os.path.isfile(caminho):
            a["hash_arquivo"] = hash_arquivo(caminho)
        atualizados.append(a["id"])
    faltando = sorted(alvos - set(atualizados))
    salvar(args.analise, dados)
    print(json.dumps({"atualizados": atualizados, "nao_encontrados": faltando}, ensure_ascii=False))
    if faltando:
        sys.exit(1)


def main():
    configurar_saida()
    p = argparse.ArgumentParser(description="Controle de estado da análise LGPD (persistência, desatualização e status de correções).")
    sub = p.add_subparsers(dest="comando", required=True)

    v = sub.add_parser("verificar", help="informa se existe análise para o alvo e se está desatualizada")
    v.add_argument("alvo")
    v.add_argument("--saida")
    v.set_defaults(func=cmd_verificar)

    s = sub.add_parser("selar", help="registra hashes dos arquivos citados e metadados da análise")
    s.add_argument("analise")
    s.add_argument("--raiz", required=True)
    s.set_defaults(func=cmd_selar)

    pe = sub.add_parser("pendentes", help="lista achados pendentes agrupados por tipo de correção")
    pe.add_argument("analise")
    pe.add_argument("--severidade", choices=SEVERIDADES, default="baixa")
    pe.add_argument("--ids")
    pe.set_defaults(func=cmd_pendentes)

    m = sub.add_parser("marcar", help="atualiza o status de achados e registra histórico")
    m.add_argument("analise")
    m.add_argument("--id", action="append", required=True, help="ID ou lista separada por vírgula (repetível)")
    m.add_argument("--status", required=True)
    m.add_argument("--nota")
    m.add_argument("--arquivos", nargs="*")
    m.add_argument("--raiz")
    m.set_defaults(func=cmd_marcar)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
