#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analysis/fetch_all_data.py
自动化数据抓取与整理：能联网时自动获取 World Bank 数据，并为需手动下载的
数据源（Saez–Zucman / FRED / Fed Z.1 / IMF / BIS）生成带链接的下载指南。

用法:
    python analysis/fetch_all_data.py --output data/
"""
import argparse
import csv
import json
import os
from datetime import datetime
from urllib.request import urlopen


class DataFetcher:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.log = []

    def fetch_json(self, url, name):
        try:
            print(f"[..] fetching {name}")
            with urlopen(url, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8"))
            self.log.append(f"OK {name}")
            print(f"[ok] {name}")
            return data
        except Exception as e:
            self.log.append(f"FAIL {name}: {e}")
            print(f"[x] {name}: {e}")
            return None

    def process_worldbank(self, raw):
        if not raw or len(raw) < 2:
            return None
        out = []
        for rec in raw[1]:
            if rec.get("value") is not None:
                out.append({"year": int(rec["date"]), "value": float(rec["value"]),
                            "source": "World Bank WDI", "quality": "A"})
        out.sort(key=lambda x: x["year"], reverse=True)
        return out

    def fetch_worldbank_gini(self):
        url = ("https://api.worldbank.org/v2/country/US/indicator/"
               "SI.POV.GINI?format=json&per_page=200")
        raw = self.fetch_json(url, "World Bank Gini (USA)")
        if raw:
            processed = self.process_worldbank(raw)
            self.save_csv("usa_gini.csv", processed)
            return processed
        return None

    def save_csv(self, filename, rows):
        if not rows:
            print(f"[!] {filename}: no data")
            return
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"[saved] {path} ({len(rows)} rows)")

    def save_json(self, filename, obj):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        print(f"[saved] {path}")

    def guides(self):
        self.save_json("saez_zucman_guide.json", {
            "source": "Saez–Zucman Wealth Database",
            "url": "https://gabriel-zucman.eu/uswealth/",
            "files": ["SaezZucman2016QJE_MainData.xlsx",
                      "AppendixTables(Distributions).xlsx"],
            "variables": ["top 1% wealth share", "top 10% wealth share",
                          "wealth composition: real estate vs financial"],
            "target_keys": ["us_top1_wealth_1980", "us_top1_wealth_2000",
                            "us_top1_wealth_2015", "us_top1_wealth_2022",
                            "us_wealth_property_1980", "us_wealth_property_2026",
                            "us_wealth_financial_1980", "us_wealth_financial_2026"],
            "note": "导出 CSV 至 data/ 后运行 analysis/build_injected.py"})
        self.save_json("fred_download_guide.json", {
            "source": "FRED (Federal Reserve Economic Data)",
            "series": {
                "SIPOVGINIUSA": "Gini (USA)",
                "DDOI06USA156NWDB": "5-bank concentration ratio",
                "BOGZ1FL102090100Q": "Net worth (households & NPOs)"},
            "target_keys": ["us_finance_profit_1980", "us_finance_profit_2000",
                            "us_finance_profit_peak", "us_finance_profit_2020"],
            "note": "每页右上 Download -> CSV"})
        self.save_json("fed_z1_guide.json", {
            "source": "Federal Reserve Financial Accounts (Z.1)",
            "url": "https://www.federalreserve.gov/releases/z1/",
            "tables": ["L.223 Household wealth composition",
                       "L.225 Nonfinancial corporate assets"]})
        self.save_json("imf_guide.json", {
            "source": "IMF World Economic Outlook / Global Debt Monitor",
            "url": "https://data.imf.org/",
            "indicators": ["General government gross debt (% GDP)",
                           "GDP constant prices"],
            "target_keys": ["global_debt_gdp_2026", "us_debt_gdp_2026"]})
        self.save_json("bis_guide.json", {
            "source": "BIS Statistics",
            "url": "https://data.bis.org/",
            "datasets": ["Consolidated banking statistics",
                         "Locational banking statistics"],
            "target_keys": ["kappa_financial_1980", "kappa_financial_2026"]})

    def run(self):
        print("=" * 60)
        print("data fetch —", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60)
        gini = self.fetch_worldbank_gini()
        self.guides()
        self.save_json("data_fetch_summary.json", {
            "timestamp": datetime.now().isoformat(),
            "auto_fetched": {"worldbank_gini": len(gini) if gini else 0},
            "log": self.log})
        print("done.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
    DataFetcher(ap.parse_args().output).run()
