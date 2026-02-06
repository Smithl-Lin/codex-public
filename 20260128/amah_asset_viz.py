import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# 1. 加载锁定的基因组参数
config_path = 'amah_config.json'
if not os.path.exists(config_path):
    print(f"Error: {config_path} not found. Please run the audit script first.")
    exit()

with open(config_path, 'r') as f:
    config = json.load(f)

# 2. 模拟/获取统计分布数据 (反映 20 万资产底座)
subjects = ['Oncology', 'Parkinson', 'TBI', 'BCI', 'Longevity', 'Neurostimulation']
counts = [55000, 42000, 31000, 25000, 27000, 20000]
pi_percentages = [0.12, 0.08, 0.05, 0.15, 0.10, 0.09] 

df = pd.DataFrame({'Subject': subjects, 'Asset_Count': counts, 'PI_Ratio': pi_percentages})

# 3. 绘图：学科资产规模与 PI 占比 (路演白皮书图表)
fig, ax1 = plt.subplots(figsize=(12, 6))

# 绘制条形图 (资产总量)
bars = ax1.bar(df['Subject'], df['Asset_Count'], color='#4682B4', alpha=0.7, label='Asset Density')
ax1.set_ylabel('Total Asset Nodes', fontsize=12)
ax1.set_xlabel('Clinical Specialty', fontsize=12)
ax1.set_title(f'AMAH Strategic Asset Distribution (Total: {config["asset_base"]["total_nodes"]:,})', fontsize=14)

# 绘制折线图 (PI 指纹占比 - 专利 8 逻辑)
ax2 = ax1.twinx()
ax2.plot(df['Subject'], df['PI_Ratio'], color='#DC143C', marker='o', linewidth=2, label='PI Fingerprint Density (Gpi >= 1.5)')
ax2.set_ylabel('PI Concentration Ratio', fontsize=12)
ax2.set_ylim(0, 0.20)

# 添加图例
fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)

# 保存为白皮书配图 (防止 WSL 无显示器报错)
plt.tight_layout()
output_fig = "amah_asset_distribution.png"
plt.savefig(output_fig)
print(f"✅ Visualization saved as {output_fig}")
