# -*- coding: utf-8 -*-
"""
fetch_faostat.py — 按需重新下载并解压 FAOSTAT 批量数据（V5 粮食检验用）。

原始 FAOSTAT 数据约 4.4 GB，不随项目保存；本脚本用于在需要复现时重新获取。
下载 4 个数据集到 faostat_data/<CODE>/ ：
  QCL 生产 / TCL 贸易 / PP 生产者价格 / FBS 食物平衡表

用法：python analysis/fetch_faostat.py
随后运行：python analysis/food_energy_validation.py
"""
import json
import os
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(HERE, "faostat_data")
META = "http://fenixservices.fao.org/faostat/static/bulkdownloads/datasets_E.json"
WANT = {"QCL", "TCL", "PP", "FBS"}


def main():
    os.makedirs(DEST, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(
            META, headers={"User-Agent": "entropy-spiral/1.0"}), timeout=120) as r:
        catalog = json.load(r)["Datasets"]["Dataset"]
    for d in catalog:
        code = d.get("DatasetCode")
        if code not in WANT:
            continue
        url = d["FileLocation"]
        zpath = os.path.join(DEST, f"{code}.zip")
        print(f"[{code}] 下载 {url}")
        urllib.request.urlretrieve(url, zpath)
        outdir = os.path.join(DEST, code)
        os.makedirs(outdir, exist_ok=True)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(outdir)
        os.remove(zpath)  # 解压后删除压缩包，避免重复占用
        print(f"[{code}] 已解压 → {outdir}")
    print("[done] 现在可运行 analysis/food_energy_validation.py")


if __name__ == "__main__":
    main()
