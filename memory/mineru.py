"""MinerU 文档解析 — PDF/Office/图片 → Markdown/JSON，调用 mineru.net 官方 API v4。
Token: 环境变量 MINERU_TOKEN 或 ~/.config/mineru/token（申请: https://mineru.net/apiManage/token）。
"""
import os, sys, time, zipfile, argparse
import requests

BASE = os.environ.get("MINERU_API_BASE", "https://mineru.net/api/v4")


def _token():
    t = os.environ.get("MINERU_TOKEN", "")
    if not t:
        p = os.path.expanduser("~/.config/mineru/token")
        t = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    t = t.strip()
    if not t:
        sys.exit("缺少 MinerU Token：设置 MINERU_TOKEN 或写入 ~/.config/mineru/token "
                 "(申请: https://mineru.net/apiManage/token)")
    return t


def _hdr():
    return {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"}


def _data(r):
    r.raise_for_status()
    j = r.json()
    if j.get("code", 0) != 0:
        sys.exit(f"MinerU API 错误 {j.get('code')}: {j.get('msg')}")
    return j["data"]


def submit(src, model="hybrid", ocr=False, formula=True, table=True, pages="", formats=None):
    """提交解析任务，src 为 http(s) URL 或本地文件路径。返回 ('task'|'batch', id)。"""
    opt = {"model_version": model, "is_ocr": ocr, "enable_formula": formula, "enable_table": table}
    if pages:
        opt["page_ranges"] = pages
    if formats:
        opt["extra_formats"] = formats
    if src.startswith(("http://", "https://")):
        tid = _data(requests.post(f"{BASE}/extract/task", headers=_hdr(), json={"url": src, **opt}))["task_id"]
        return "task", tid
    d = _data(requests.post(f"{BASE}/file-urls/batch", headers=_hdr(),
                            json={"files": [{"name": os.path.basename(src), **opt}]}))
    up = d["file_urls"][0]
    up = up if isinstance(up, str) else up["url"]
    with open(src, "rb") as fh:
        requests.put(up, data=fh, headers={"Content-Type": ""}).raise_for_status()
    return "batch", d["batch_id"]


def wait(kind, _id, interval=5, timeout=1800):
    """轮询直到完成，返回结果 zip 下载 URL。"""
    end = time.time() + timeout
    while time.time() < end:
        if kind == "task":
            d = _data(requests.get(f"{BASE}/extract/task/{_id}", headers=_hdr()))
        else:
            d = _data(requests.get(f"{BASE}/extract-results/batch/{_id}", headers=_hdr()))["extract_result"][0]
        st = d.get("state")
        if st == "done":
            return d["full_zip_url"]
        if st == "failed":
            sys.exit(f"解析失败: {d.get('err_msg')}")
        print(f"[{st}] ...", file=sys.stderr)
        time.sleep(interval)
    sys.exit("轮询超时")


def fetch(zip_url, out_dir):
    """下载并解压结果 zip 到 out_dir，返回主 Markdown 路径（若有）。"""
    os.makedirs(out_dir, exist_ok=True)
    zp = os.path.join(out_dir, "mineru_result.zip")
    with requests.get(zip_url, stream=True) as r:
        r.raise_for_status()
        with open(zp, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
    with zipfile.ZipFile(zp) as z:
        z.extractall(out_dir)
        mds = [n for n in z.namelist() if n.endswith(".md")]
    return os.path.join(out_dir, mds[0]) if mds else ""


def parse(src, out_dir="", **kw):
    """一步到位：提交 → 等待 →（out_dir 非空则）下载解压。返回 Markdown 路径或结果 zip 链接。"""
    zip_url = wait(*submit(src, **kw))
    return fetch(zip_url, out_dir) if out_dir else zip_url


def _cli():
    ap = argparse.ArgumentParser(description="MinerU 文档解析 → Markdown/JSON")
    ap.add_argument("source", help="文档 URL 或本地文件路径")
    ap.add_argument("--model", default="hybrid", help="hybrid(默认)/pipeline/vlm/MinerU-HTML")
    ap.add_argument("--ocr", action="store_true", help="强制 OCR")
    ap.add_argument("--no-formula", action="store_true", help="关闭公式识别")
    ap.add_argument("--no-table", action="store_true", help="关闭表格识别")
    ap.add_argument("--pages", default="", help='页码范围，如 "1-5,8"')
    ap.add_argument("--format", action="append", dest="formats", help="额外格式 docx/html/latex，可重复")
    ap.add_argument("-o", "--output", default="", help="下载并解压到该目录")
    a = ap.parse_args()
    print(parse(a.source, out_dir=a.output, model=a.model, ocr=a.ocr,
                formula=not a.no_formula, table=not a.no_table, pages=a.pages, formats=a.formats))


if __name__ == "__main__":
    _cli()
