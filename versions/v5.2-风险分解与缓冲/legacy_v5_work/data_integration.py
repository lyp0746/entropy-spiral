"""
粮食系统脆弱性指标V - 修复版本（根据真实列名结构）
"""

import pandas as pd
import numpy as np
import requests
import time
from pathlib import Path

class FoodVulnerabilityDataIntegration:
    def __init__(self, faostat_dir="faostat_data", output_dir="integrated_data"):
        self.faostat_dir = Path(faostat_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 目标国家（FAOSTAT中的英文名称）
        self.countries = ['China', 'India', 'Brazil', 'United States', 
                         'Russian Federation', 'Ukraine', 'Thailand', 'Vietnam']
        
        # 4种粮食作物
        self.crops = ['Rice', 'Wheat', 'Maize', 'Soya Beans']
        
        self.years = list(range(2010, 2026))
    
    # ============ 步骤1：加载FAOSTAT数据 ============
    def load_faostat_data(self):
        """加载已下载的FAOSTAT数据"""
        print("=" * 70)
        print("【步骤1】加载FAOSTAT数据")
        print("=" * 70)
        
        data_dict = {}
        
        try:
            prod_files = list(self.faostat_dir.glob("QCL/*.csv"))
            if prod_files:
                data_dict['production'] = pd.read_csv(prod_files[0], low_memory=False)
                print(f"✓ 生产数据加载成功: {len(data_dict['production'])} 行")
        except Exception as e:
            print(f"✗ 生产数据加载失败: {e}")
        
        try:
            trade_files = list(self.faostat_dir.glob("TCL/*.csv"))
            if trade_files:
                data_dict['trade'] = pd.read_csv(trade_files[0], low_memory=False)
                print(f"✓ 贸易数据加载成功: {len(data_dict['trade'])} 行")
        except Exception as e:
            print(f"✗ 贸易数据加载失败: {e}")
        
        try:
            price_files = list(self.faostat_dir.glob("PP/*.csv"))
            if price_files:
                data_dict['prices'] = pd.read_csv(price_files[0], low_memory=False)
                print(f"✓ 价格数据加载成功: {len(data_dict['prices'])} 行")
        except Exception as e:
            print(f"✗ 价格数据加载失败: {e}")
        
        try:
            fbs_files = list(self.faostat_dir.glob("FBS/*.csv"))
            if fbs_files:
                data_dict['balances'] = pd.read_csv(fbs_files[0], low_memory=False)
                print(f"✓ 食物平衡表加载成功: {len(data_dict['balances'])} 行")
                # 显示可用的Element类型
                print(f"  可用的Element类型:")
                elements = data_dict['balances']['Element'].unique()[:10]
                for e in elements:
                    print(f"    - {e}")
        except Exception as e:
            print(f"✗ 食物平衡表加载失败: {e}")
        
        return data_dict
    
    # ============ 步骤2：从World Bank下载补充数据 ============
    def download_world_bank_indicators(self):
        """从World Bank API下载Gini Index"""
        print("\n" + "=" * 70)
        print("【步骤2】从World Bank API下载指标")
        print("=" * 70)
        
        wb_countries = ['CHN', 'IND', 'BRA', 'USA', 'RUS', 'UKR', 'THA', 'VNM']
        indicators = {'SI.POV.GINI': 'Gini_Index', 'NY.GDP.PCAP.CD': 'GDP_per_Capita'}
        
        all_data = []
        
        for indicator_code, indicator_name in indicators.items():
            print(f"\n下载: {indicator_name}")
            
            try:
                country_codes = ';'.join(wb_countries)
                url = f"https://api.worldbank.org/v2/country/{country_codes}/indicators/{indicator_code}?format=json&per_page=10000"
                
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if len(data) > 1 and data[1]:
                    valid_count = 0
                    for record in data[1]:
                        if record['value'] is not None:
                            all_data.append({
                                'Country_Code': record['countryiso3code'],
                                'Year': int(record['date']),
                                'Indicator': indicator_name,
                                'Value': float(record['value'])
                            })
                            valid_count += 1
                    print(f"  ✓ 获取 {valid_count} 条有效记录")
                else:
                    print(f"  ⚠ 该指标无数据")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  ✗ 下载失败: {e}")
        
        if all_data:
            df = pd.DataFrame(all_data)
            pivot_df = df.pivot_table(
                index=['Country_Code', 'Year'],
                columns='Indicator',
                values='Value'
            ).reset_index()
            
            wb_path = self.output_dir / "WorldBank_Indicators.csv"
            pivot_df.to_csv(wb_path, index=False)
            print(f"\n✓ World Bank数据已保存: {wb_path}")
            return pivot_df
        else:
            print("\n✗ World Bank未获取到数据")
            return None
    
    # ============ 步骤3：从FAOSTAT推导核心指标 ============
    def calculate_core_indicators_from_faostat(self, faostat_data):
        """从FAOSTAT数据推导Θ, I, κ"""
        print("\n" + "=" * 70)
        print("【步骤3】从FAOSTAT数据推导指标")
        print("=" * 70)
        
        core_indicators = {}
        
        # 1. Θ - 权力集中度
        if 'production' in faostat_data and 'trade' in faostat_data:
            print("\n计算 Θ (权力集中度)...")
            theta_indicators = self._calculate_theta(
                faostat_data['production'],
                faostat_data['trade']
            )
            core_indicators['theta'] = theta_indicators
            print(f"✓ 计算完成: {len(theta_indicators)} 条记录")
        
        # 2. I - 反馈延迟
        if 'prices' in faostat_data:
            print("\n计算 I (反馈延迟/价格波动)...")
            I_indicators = self._calculate_I(faostat_data['prices'])
            core_indicators['I'] = I_indicators
            print(f"✓ 计算完成: {len(I_indicators)} 条记录")
        
        # 3. κ - 耦合度
        if 'trade' in faostat_data:
            print("\n计算 κ (耦合度/进口多元化)...")
            kappa_indicators = self._calculate_kappa(faostat_data['trade'])
            core_indicators['kappa'] = kappa_indicators
            print(f"✓ 计算完成: {len(kappa_indicators)} 条记录")
        
        return core_indicators
    
    def _calculate_theta(self, production_df, trade_df):
        """
        Θ = (产量集中度 + 进口依赖度 + 进口伙伴集中度) / 3
        
        从FAOSTAT长格式数据中提取：
        - Production: Element == 'Production'
        - Import quantity: Element == 'Import quantity'
        """
        theta_results = []
        
        # 过滤粮食数据
        prod = production_df[
            (production_df['Area'].isin(self.countries)) &
            (production_df['Item'].isin(self.crops)) &
            (production_df['Element'] == 'Production') &
            (production_df['Year'].isin(self.years)) &
            (production_df['Value'] > 0)
        ].copy()
        
        trade = trade_df[
            (trade_df['Area'].isin(self.countries)) &
            (trade_df['Item'].isin(self.crops)) &
            (trade_df['Year'].isin(self.years))
        ].copy()
        
        for country in self.countries:
            for year in self.years:
                # θ1: 产量集中度 (HHI of 4 crops)
                country_year_prod = prod[
                    (prod['Area'] == country) & 
                    (prod['Year'] == year)
                ]
                
                if len(country_year_prod) > 0:
                    total = country_year_prod['Value'].sum()
                    shares = country_year_prod['Value'] / total
                    hhi_prod = (shares ** 2).sum()
                else:
                    hhi_prod = np.nan
                
                # θ2: 进口依赖度
                imports = trade[
                    (trade['Area'] == country) &
                    (trade['Year'] == year) &
                    (trade['Element'] == 'Import quantity')
                ]['Value'].sum()
                
                domestic_prod = country_year_prod['Value'].sum()
                total_supply = domestic_prod + imports
                import_dep = imports / total_supply if total_supply > 0 else np.nan
                
                # θ3: 进口伙伴集中度 (HHI)
                import_data = trade[
                    (trade['Area'] == country) &
                    (trade['Year'] == year) &
                    (trade['Element'] == 'Import quantity')
                ]
                
                if len(import_data) > 0 and imports > 0:
                    partner_shares = import_data.groupby('Item')['Value'].sum() / imports
                    hhi_partners = (partner_shares ** 2).sum()
                else:
                    hhi_partners = np.nan
                
                # 综合Θ (只取有效值求平均)
                theta_values = [v for v in [hhi_prod, import_dep, hhi_partners] if not np.isnan(v)]
                theta = np.mean(theta_values) if theta_values else np.nan
                
                theta_results.append({
                    'Country': country,
                    'Year': year,
                    'Theta_HHI_Production': hhi_prod,
                    'Theta_Import_Dependency': import_dep,
                    'Theta_Partner_Concentration': hhi_partners,
                    'Theta_Combined': theta
                })
        
        return pd.DataFrame(theta_results)
    
    def _calculate_I(self, prices_df):
        """
        I = 价格波动系数 (Coefficient of Variation)
        
        从FAOSTAT价格数据计算最近10年的价格波动
        """
        I_results = []
        
        prices = prices_df[
            (prices_df['Area'].isin(self.countries)) &
            (prices_df['Item'].isin(self.crops)) &
            (prices_df['Element'] == 'Producer Price (LCU/tonne)') &
            (prices_df['Value'] > 0)
        ].copy()
        
        for country in self.countries:
            for year in self.years:
                # 计算过去10年的价格波动
                price_window = prices[
                    (prices['Area'] == country) &
                    (prices['Year'] >= year - 10) &
                    (prices['Year'] <= year)
                ]['Value']
                
                if len(price_window) > 2:  # 至少要有3个数据点
                    mean_price = price_window.mean()
                    if mean_price > 0:
                        price_cv = price_window.std() / mean_price
                    else:
                        price_cv = np.nan
                else:
                    price_cv = np.nan
                
                I_results.append({
                    'Country': country,
                    'Year': year,
                    'I_Price_CV': price_cv,
                    'I_Combined': price_cv  # 简化版本，只用价格波动
                })
        
        return pd.DataFrame(I_results)
    
    def _calculate_kappa(self, trade_df):
        """
        κ = 进口伙伴多元化程度 (有效伙伴国数)
        
        κ = 1 / HHI_partners
        """
        kappa_results = []
        
        trade = trade_df[
            (trade_df['Area'].isin(self.countries)) &
            (trade_df['Item'].isin(self.crops)) &
            (trade_df['Element'] == 'Import quantity') &
            (trade_df['Year'].isin(self.years))
        ].copy()
        
        for country in self.countries:
            for year in self.years:
                import_data = trade[
                    (trade['Area'] == country) &
                    (trade['Year'] == year)
                ]
                
                if len(import_data) > 0:
                    total_imports = import_data['Value'].sum()
                    
                    if total_imports > 0:
                        # 按商品项目计算多元化
                        item_shares = import_data.groupby('Item')['Value'].sum() / total_imports
                        hhi = (item_shares ** 2).sum()
                        # 有效商品种类数
                        effective_diversity = 1 / hhi if hhi > 0 else np.nan
                    else:
                        effective_diversity = np.nan
                else:
                    effective_diversity = np.nan
                
                kappa_results.append({
                    'Country': country,
                    'Year': year,
                    'Kappa_Import_Diversity': effective_diversity
                })
        
        return pd.DataFrame(kappa_results)
    
    # ============ 步骤4：整合所有数据 ============
    def integrate_all_data(self, core_indicators, wb_data):
        """整合所有指标数据"""
        print("\n" + "=" * 70)
        print("【步骤4】整合所有数据")
        print("=" * 70)
        
        # 初始化
        if 'theta' in core_indicators:
            merged = core_indicators['theta'].copy()
        else:
            merged = pd.DataFrame()
        
        # 逐步合并其他指标
        for key in ['I', 'kappa']:
            if key in core_indicators:
                merged = merged.merge(
                    core_indicators[key],
                    on=['Country', 'Year'],
                    how='left'
                )
        
        # 合并World Bank数据
        if wb_data is not None:
            # 创建国家代码到名称的映射
            country_code_map = {
                'CHN': 'China',
                'IND': 'India',
                'BRA': 'Brazil',
                'USA': 'United States',
                'RUS': 'Russian Federation',
                'UKR': 'Ukraine',
                'THA': 'Thailand',
                'VNM': 'Vietnam'
            }
            
            wb_data_copy = wb_data.copy()
            wb_data_copy['Country'] = wb_data_copy['Country_Code'].map(country_code_map)
            
            merged = merged.merge(
                wb_data_copy[['Country', 'Year', 'Gini_Index', 'GDP_per_Capita']],
                on=['Country', 'Year'],
                how='left'
            )
        
        # 保存
        output_path = self.output_dir / "Integrated_Food_Vulnerability_Data.csv"
        merged.to_csv(output_path, index=False)
        print(f"\n✓ 整合数据已保存: {output_path}")
        print(f"  总行数: {len(merged)}")
        print(f"  总列数: {len(merged.columns)}")
        print(f"  缺失值统计:\n{merged.isnull().sum()}")
        
        return merged
    
    # ============ 主执行函数 ============
    def run_complete_pipeline(self):
        """执行完整流程"""
        print("\n" + "█" * 70)
        print("█ 粮食系统脆弱性指标V - 完整数据获取与整合")
        print("█" * 70)
        
        faostat_data = self.load_faostat_data()
        wb_data = self.download_world_bank_indicators()
        core_indicators = self.calculate_core_indicators_from_faostat(faostat_data)
        final_data = self.integrate_all_data(core_indicators, wb_data)
        
        print("\n" + "█" * 70)
        print("█ 所有数据已成功处理！")
        print("█" * 70)
        
        print(f"\n输出文件: {self.output_dir.absolute()}")
        print(f"\n包含的指标：")
        print(f"  • Theta (权力集中度): Theta_HHI_Production, Theta_Import_Dependency, Theta_Partner_Concentration")
        print(f"  • I (反馈延迟): I_Price_CV")
        print(f"  • Kappa (耦合度): Kappa_Import_Diversity")
        print(f"  • World Bank: Gini_Index, GDP_per_Capita")
        
        return final_data


if __name__ == "__main__":
    pipeline = FoodVulnerabilityDataIntegration(
        faostat_dir="faostat_data",
        output_dir="integrated_data"
    )
    final_data = pipeline.run_complete_pipeline()
    
    print("\n【数据预览】")
    print(final_data.head(15))