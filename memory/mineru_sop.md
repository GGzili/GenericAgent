# MinerU 文档解析 SOP

## 1. 快速开始
文档解析工具：PDF / DOC(X) / PPT(X) / PNG / JPG / HTML → Markdown + 结构化 JSON。调用 mineru.net 官方 API v4，支持 OCR(109 语种)、公式/表格识别、跨页表格合并，无需本地 GPU。

准备：申请 Token（90 天有效）https://mineru.net/apiManage/token ，然后 `export MINERU_TOKEN=xxx` 或写入 `~/.config/mineru/token`。

**Python 调用方式:**
```python
import sys
sys.path.append('../memory')  # 直接挂载工具目录
from mineru import parse

# URL 或本地文件都行；out_dir 留空则只返回结果 zip 下载链接
md = parse('https://arxiv.org/pdf/2301.00001.pdf', out_dir='./out')  # 返回主 Markdown 路径
```

**CLI:**
```powershell
python ../memory/mineru.py <url或文件> -o ./out
python ../memory/mineru.py paper.pdf -o ./out --model vlm --ocr
python ../memory/mineru.py report.pdf --format docx --format latex
```

## 2. 接口要点
- 三步：提交 → 轮询 → 下载，`parse()` 已封装。本地文件自动走上传流程（`file-urls/batch` → PUT → 轮询 batch）。
- 模型 `model`：`hybrid`(默认) / `pipeline`(纯 CPU、快) / `vlm`(复杂版式、准) / `MinerU-HTML`(保留 HTML)。
- 额外格式 `--format` / `formats=`：`docx` / `html` / `latex`。
- 函数：`parse(src, out_dir, model, ocr, formula, table, pages, formats)` / `submit(src,...)->(kind,id)` / `wait(kind,id)->zip_url` / `fetch(zip_url,out_dir)->md_path`。

## 3. 注意事项
- 限制：单文件 ≤200MB / ≤600 页；每账号每日 2000 页高优先级；批量上传 ≤200 文件/次；Token 90 天有效。
- 输出 zip 内含：主 Markdown、`content_list.json`(结构化内容)、`images/`(切图)、`layout.json`(版面分析)。
- 配置：`MINERU_API_BASE` 覆盖 API 地址；`MINERU_TOKEN` 或 `~/.config/mineru/token` 提供 Token。
- 网络受限时 GitHub / AWS 等海外 URL 可能下载超时，优先用本地文件上传。
