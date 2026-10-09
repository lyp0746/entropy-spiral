import requests
import json
import zipfile
import os
from pathlib import Path

# 下载元数据，获取所有数据集的下载链接
print("正在获取FAOSTAT数据集目录...")
metadata_url = "http://fenixservices.fao.org/faostat/static/bulkdownloads/datasets_E.json"
response = requests.get(metadata_url)
datasets = json.loads(response.text)

# 我们需要的数据集代码
needed_datasets = {
    "QCL": "Production: Crops and livestock",
    "TCL": "Trade: Crops and livestock",
    "FBS": "Food Balances (2010-)",
    "PP": "Producer Prices"  # 如果存在
}

# 创建下载文件夹
download_dir = Path("faostat_data")
download_dir.mkdir(exist_ok=True)

# 从JSON中提取并下载数据
for dataset in datasets["Datasets"]["Dataset"]:
    code = dataset.get("DatasetCode")
    
    if code in needed_datasets:
        filename = dataset.get("DatasetName", code)
        file_location = dataset.get("FileLocation")
        
        print(f"\n正在下载 {code}: {filename}")
        print(f"下载链接: {file_location}")
        
        try:
            # 下载ZIP文件
            response = requests.get(file_location, timeout=300)
            response.raise_for_status()
            
            # 保存ZIP文件
            zip_path = download_dir / f"{code}.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ {code} 下载成功")
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir / code)
            print(f"✓ {code} 解压成功")
            
        except requests.exceptions.RequestException as e:
            print(f"✗ {code} 下载失败: {e}")
        except Exception as e:
            print(f"✗ {code} 处理失败: {e}")

print("\n所有数据下载完成！")
print(f"数据保存在: {download_dir.absolute()}")