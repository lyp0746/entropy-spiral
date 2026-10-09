"""
探查FAOSTAT数据的实际列名结构
"""

import pandas as pd
from pathlib import Path

faostat_dir = Path("faostat_data")

print("=" * 70)
print("FAOSTAT数据列名探查")
print("=" * 70)

# 检查每个数据集的列名
datasets = {
    'QCL': 'Production',
    'TCL': 'Trade',
    'PP': 'Prices',
    'FBS': 'Food Balances'
}

for code, name in datasets.items():
    csv_files = list(faostat_dir.glob(f"{code}/*.csv"))
    if csv_files:
        print(f"\n【{name}】{code}")
        print(f"  文件: {csv_files[0].name}")
        
        # 只读前100行用于列名检查
        df = pd.read_csv(csv_files[0], nrows=100)
        print(f"  列名: {list(df.columns)}")
        print(f"  总行数: {len(pd.read_csv(csv_files[0], usecols=[0]))}")
        print(f"\n  数据样本:")
        print(f"  {df.iloc[0].to_dict()}")