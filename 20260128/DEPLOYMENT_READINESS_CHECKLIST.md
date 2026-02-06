# A.M.A.N.I. 项目交付准备检查清单
**Date:** 2026-02-02
**Version:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
**Status:** 🟡 **需要关键改进才能运行**

---

## 执行摘要

项目架构完整且设计精良，但**缺少运行时依赖和数据初始化**。以下是使项目从代码状态到可运行状态的必要步骤。

**关键阻塞项：** 3 个
**建议改进项：** 8 个
**预计准备时间：** 4-6 小时

---

## 1. 🔴 关键阻塞项（必须解决才能运行）

### 1.1 ❌ ChromaDB 未初始化

**问题：**
```bash
amah_vector_db/ 目录不存在
```

**影响范围：**
- `GNNAssetAnchor` (amani_trinity_bridge.py:216-229) 无法加载 ChromaDB 集合
- `AMAHCenturionInjector` (amah_centurion_injection.py:534-536) 无法连接数据库
- 所有 L3 AGID 映射功能失效

**解决方案：**

```bash
cd "C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project\20260128"

# 步骤 1: 创建 ChromaDB 并导入专家数据
python batch_build_db.py

# 步骤 2: 批量加载专家资产
python expert_bulk_loader.py

# 步骤 3: 验证数据库
python -c "import chromadb; client = chromadb.PersistentClient(path='./amah_vector_db'); print(f'Collections: {[c.name for c in client.list_collections()]}')"
```

**期望输出：**
```
Collections: ['expert_map_global', 'mayo_clinic_trials']
expert_map_global count: 100559+
mayo_clinic_trials count: [merged_data.json 条数]
```

**优先级：** 🔴 **CRITICAL** — 阻塞所有查询功能

---

### 1.2 ❌ physical_node_registry.json 未生成

**问题：**
```bash
physical_node_registry.json 不存在于 20260128/ 目录
```

**影响范围：**
- `NexusRouter.auto_register()` (amani_nexus_layer_v3.py:73-99) 无法加载物理映射
- AGID → 物理节点解析失败
- L3 合规门（ComplianceGate）无法确定区域

**解决方案：**

```bash
# 生成物理节点注册表
python sync_l2_to_chromadb.py
```

**验证：**
```bash
# 应该输出: Built physical_node_registry.json with [N] entries.
# 应该输出: NexusRouter.auto_register loaded [N] mappings.

# 手动验证
python -c "import json; print(f'Registry entries: {len(json.load(open(\"physical_node_registry.json\")))}')"
```

**优先级：** 🔴 **CRITICAL** — 阻塞 L3 路由和合规检查

---

### 1.3 ⚠️ 环境变量未配置完整

**问题：**
.env 文件存在但可能未填充所有必需的 API keys

**影响范围：**
- Trinity API Connector 无法调用 GPT/Gemini/Claude（若 keys 缺失）
- MedicalReasoner 无法连接 MedGemma endpoint（Phase 4）
- 系统降级到 stub 模式（不调用真实 AI 模型）

**检查方案：**

```bash
# 验证 .env 配置
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

keys = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
    'GOOGLE_APPLICATION_CREDENTIALS': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
    'MEDGEMMA_ENDPOINT': os.getenv('MEDGEMMA_ENDPOINT'),
}

for k, v in keys.items():
    status = '✅' if v else '❌'
    print(f'{status} {k}: {\"配置\" if v else \"缺失\"}')"
```

**最低要求（Phase 1-3 运行）：**
- ✅ `GEMINI_API_KEY` 或 `ANTHROPIC_API_KEY` 或 `OPENAI_API_KEY` **至少一个**
- ⚠️ `GOOGLE_APPLICATION_CREDENTIALS` 如果使用 Vertex AI

**Phase 4 要求（MedGemma）：**
- `MEDGEMMA_ENDPOINT`

**解决方案：**
```bash
# 编辑 .env 文件填入实际 keys
nano .env  # 或 notepad .env

# 参考 .env.example 格式
```

**优先级：** 🟡 **HIGH** — 不阻塞启动但会降级功能

---

## 2. 🟡 建议改进项（增强可靠性和完整性）

### 2.1 trinity_api_connector.py API 调用验证

**当前状态：**
- trinity_api_connector.py (lines 30-32) 使用了正确的环境变量
- 但 Gemini API 调用使用了 `GenerativeModel("gemini-3-pro-preview")`，这个模型名称可能不存在

**建议：**
```python
# 修改 trinity_api_connector.py line 30
# 当前：
self.gemini_model = GenerativeModel("gemini-3-pro-preview")

# 建议改为（实际可用的模型）：
self.gemini_model = GenerativeModel("gemini-1.5-pro")  # 或 gemini-2.0-flash-exp
```

**验证方法：**
```bash
python -c "
from trinity_api_connector import AMAHWeightedEngine
import asyncio
engine = AMAHWeightedEngine()
result = asyncio.run(engine.execute_audit_workflow('Test case'))
print(f'Result: {result}')
"
```

**优先级：** 🟡 **MEDIUM** — Trinity 共识需要

---

### 2.2 端到端测试脚本缺失

**问题：**
- `test_amani_v4_full_loop.py` 仅测试 `AMANICoreOrchestrator`
- **未测试完整的 TrinityBridge 流程** (L1→L2→L2.5→L3→L4)

**建议添加：** `test_trinity_full_pipeline.py`

```python
# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
import asyncio
from amani_trinity_bridge import TrinityBridge

async def test_full_trinity_pipeline():
    print("="*80)
    print("🧪 TrinityBridge 端到端测试")
    print("="*80)

    test_cases = [
        "65yo Male, Advanced Parkinson's, seeking DBS evaluation at Mayo Jacksonville",
        "58yo Female, NSCLC KRAS G12C+, looking for Phase III clinical trials",
        "帕金森患者，寻求 DBS 脑深部电刺激评估",  # 中文主诉测试 L2 均等化
    ]

    bridge = TrinityBridge()

    for i, case in enumerate(test_cases, 1):
        print(f"\n[Test Case {i}] {case[:60]}...")
        result = bridge.run_safe(case, top_k_agids=3)

        if result.get("intercepted"):
            print(f"  ⚠️ L1 Intercepted: {result['l1_sentinel'].get('error')}")
        else:
            l1 = result.get("l1_sentinel", {})
            l3 = result.get("l3_nexus", {})
            print(f"  ✅ L1 D-effective: {l1.get('d_effective'):.4f}")
            print(f"  ✅ L3 AGIDs: {l3.get('agids', [])[:3]}")
            if result.get("l2_equalized_input"):
                print(f"  ✅ L2 Equalized: {result['l2_equalized_input'][:60]}...")
            if result.get("l4_multimodal"):
                print(f"  ✅ L4 Keys: {list(result['l4_multimodal'].keys())}")
        print("-"*60)

if __name__ == "__main__":
    asyncio.run(test_full_trinity_pipeline())
```

**运行：**
```bash
python test_trinity_full_pipeline.py
```

**优先级：** 🟡 **MEDIUM** — 质量保证

---

### 2.3 缺少部署文档

**问题：**
- 无 `DEPLOYMENT.md` 或 `GETTING_STARTED.md`
- 新用户/运维人员不知道如何启动系统

**建议添加：** `DEPLOYMENT_GUIDE.md`（见附录）

**优先级：** 🟢 **LOW** — 不阻塞运行但影响可维护性

---

### 2.4 Streamlit 依赖检查

**问题：**
app.py 和 app_v4.py 依赖 Streamlit，但未在 manifest 中看到 requirements.txt

**解决方案：**
创建 `requirements.txt`:

```txt
# A.M.A.N.I. V4.0 Dependencies
streamlit>=1.30.0
chromadb>=0.4.0
pandas>=2.0.0
numpy>=1.24.0
openai>=1.3.0
anthropic>=0.18.0
google-cloud-aiplatform>=1.38.0
python-dotenv>=1.0.0
```

**安装：**
```bash
pip install -r requirements.txt
```

**优先级：** 🟡 **HIGH** — 阻塞 UI 启动

---

### 2.5 资产数据验证

**检查现有资产完整性：**

```bash
# 验证必需的数据文件
python -c "
import os, json

files = {
    'merged_data.json': '临床试验主库',
    'expert_map_data.json': '专家/PI 表',
    'hospital_center_assets.json': '医院/中心表',
    'amah_config.json': '系统配置',
}

for f, desc in files.items():
    if os.path.isfile(f):
        size = os.path.getsize(f)
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            count = len(data) if isinstance(data, list) else 1
        print(f'✅ {f:30} | {desc:20} | {count:6} 条 | {size/1024:.1f} KB')
    else:
        print(f'❌ {f:30} | {desc:20} | 缺失')
"
```

**最低要求：**
- merged_data.json: 至少 100 条试验
- expert_map_data.json: 至少 50 个专家
- hospital_center_assets.json: 至少 20 个医院

**优先级：** 🟡 **MEDIUM** — 影响查询质量

---

### 2.6 文化主诉映射数据

**验证：**
```bash
python -c "
import os, json
path = 'asset_library_l2/cultural_complaint_mapping.json'
if os.path.isfile(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        mappings = data.get('phrase_mappings', [])
        print(f'✅ 文化映射: {len(mappings)} 条规则')
        # 显示示例
        if mappings:
            print(f'示例: {mappings[0]}')
else:
    print('❌ cultural_complaint_mapping.json 缺失')
"
```

**如果缺失，创建最小映射：**
```json
{
  "phrase_mappings": [
    {
      "source_phrases": ["帕金森", "帕金森病", "Parkinson"],
      "canonical_complaint": "Parkinson's disease"
    },
    {
      "source_phrases": ["肿瘤", "癌症", "cancer", "tumor"],
      "canonical_complaint": "cancer"
    }
  ],
  "locale_detection_rules": {
    "zh": ["[\u4e00-\u9fff]"],
    "en": ["[a-zA-Z]"]
  },
  "output_language": "en"
}
```

**优先级：** 🟢 **LOW** — L2 equalization 可选（有 fallback）

---

### 2.7 Centurion Lifecycle Monitor 后台线程

**问题：**
- `Lifecycle_Pulse_Monitor` 默认 12 小时扫描（amah_centurion_injection.py:253）
- **首次运行时 Component_4 快照为 None**，需要手动触发 `run_once()`

**验证：**
amah_centurion_injection.py:512 已经处理：
```python
if self._component_4.get_snapshot() is None:
    self._component_4.run_once()
```

**建议：**
在生产环境中启用后台扫描：
```python
# 修改 app.py 或 main 入口
from amah_centurion_injection import AMAHCenturionInjector

# 启动时
injector = AMAHCenturionInjector(start_pulse_background=True)  # 改为 True
```

**优先级：** 🟢 **LOW** — run_once() fallback 已存在

---

### 2.8 错误处理和日志

**建议添加：** 结构化日志和错误追踪

```python
# 添加到主要模块
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('amani_v4.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

**优先级：** 🟢 **LOW** — 生产环境建议

---

## 3. 运行检查清单（按顺序执行）

### 3.1 环境准备

```bash
# 1. 进入项目目录
cd "C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project\20260128"

# 2. 安装依赖
pip install -r requirements.txt  # 需要先创建

# 3. 配置环境变量
cp .env.example .env
nano .env  # 填入 API keys

# 4. 验证环境变量
python -c "from config import *; print('GEMINI:', get_gemini_api_key()[:10] if get_gemini_api_key() else 'None')"
```

### 3.2 数据初始化

```bash
# 5. 创建 ChromaDB
python batch_build_db.py

# 6. 加载专家数据
python expert_bulk_loader.py

# 7. 生成物理节点注册表
python sync_l2_to_chromadb.py

# 8. 验证数据
python -c "
import chromadb
client = chromadb.PersistentClient(path='./amah_vector_db')
collections = client.list_collections()
for c in collections:
    print(f'{c.name}: {c.count()} entries')
"
```

### 3.3 系统验证

```bash
# 9. 运行基准检查
python check_v4_baseline.py

# 10. 运行核心测试
python test_amani_v4_full_loop.py

# 11. 运行 Trinity 测试（创建后）
# python test_trinity_full_pipeline.py

# 12. 启动 Streamlit UI
streamlit run app.py
```

### 3.4 健康检查

访问 http://localhost:8501，测试：
- ✅ 输入英文主诉，验证 D ≤ 0.79 返回结果
- ✅ 输入中文主诉，验证 L2 均等化
- ✅ 查看影子账单（Shadow Quote）是否显示
- ✅ L3 AGID 列表是否返回

---

## 4. 已验证的工作组件 ✅

根据审核，以下组件**架构完整且无阻塞问题**：

| 组件 | 文件 | 状态 |
|------|------|------|
| L1 Entropy Gate | amani_core_v4.py, amani_trinity_bridge.py | ✅ 完整 |
| L2 Cultural Equalizer | amani_cultural_equalizer_l2.py | ✅ 完整 |
| L2 Centurion (4 components) | amah_centurion_injection.py | ✅ 完整 |
| L2.5 Value Orchestrator | amani_value_layer_v4.py | ✅ 完整 |
| L3 NexusRouter | amani_nexus_layer_v3.py | ✅ 完整 |
| L3 ComplianceGate | amani_nexus_layer_v3.py | ✅ 完整 |
| L3 GlobalNexus | amani_global_nexus_v4.py | ✅ 完整 |
| L4 UIPresenter | amani_interface_layer_v4.py | ✅ 完整 |
| L4 FeedbackOptimizer | amani_interface_layer_v4.py | ✅ 完整 |
| L4 BatchProcessQueue | medical_reasoner.py | ✅ 完整 |
| MedicalReasoner | medical_reasoner.py | ✅ 完整（endpoint 可选）|
| Orchestrator | medical_reasoner.py | ✅ 完整 |
| Billing Engine | billing_engine.py | ✅ 完整 |
| Config Module | config.py | ✅ 完整 |
| Asset Library L2 | asset_library_l2/ | ✅ 完整 |

---

## 5. 关键缺失组件总结

| 缺失项 | 类型 | 阻塞级别 | 预计修复时间 |
|--------|------|----------|--------------|
| ChromaDB 初始化 | 数据 | 🔴 CRITICAL | 30 分钟 |
| physical_node_registry.json | 数据 | 🔴 CRITICAL | 5 分钟 |
| requirements.txt | 配置 | 🟡 HIGH | 10 分钟 |
| .env 配置验证 | 配置 | 🟡 HIGH | 15 分钟 |
| trinity_api_connector.py 模型名 | 代码 | 🟡 MEDIUM | 5 分钟 |
| test_trinity_full_pipeline.py | 测试 | 🟡 MEDIUM | 30 分钟 |
| DEPLOYMENT_GUIDE.md | 文档 | 🟢 LOW | 1 小时 |
| cultural_complaint_mapping.json | 数据 | 🟢 LOW | 15 分钟 |

**总计修复时间：** 约 3-4 小时（不含文档）

---

## 6. 下一步行动计划

### 阶段 1: 立即修复（2 小时）
1. ✅ 创建 `requirements.txt`
2. ✅ 初始化 ChromaDB (`batch_build_db.py`)
3. ✅ 生成 physical_node_registry.json (`sync_l2_to_chromadb.py`)
4. ✅ 验证 .env 配置
5. ✅ 运行 `check_v4_baseline.py`

### 阶段 2: 测试验证（1 小时）
6. ✅ 创建 `test_trinity_full_pipeline.py`
7. ✅ 运行端到端测试
8. ✅ 启动 Streamlit UI 并手动测试

### 阶段 3: 文档完善（可选，1-2 小时）
9. 📝 创建 `DEPLOYMENT_GUIDE.md`
10. 📝 创建 `API_REFERENCE.md`（如需对外接口）

### 阶段 4: 生产准备（可选）
11. 🛡️ 添加结构化日志
12. 🛡️ 添加健康检查端点
13. 🛡️ 配置备份策略（ChromaDB + config）

---

## 7. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| API keys 配额耗尽 | 中 | 高 | 实现请求缓存和速率限制 |
| ChromaDB 数据损坏 | 低 | 高 | 定期备份 amah_vector_db/ |
| 模型 API 不可用 | 中 | 中 | 已有 stub fallback 机制 ✅ |
| 高并发查询性能 | 中 | 中 | 实现查询队列和缓存层 |
| L1 拦截率过高 | 低 | 中 | 调整 variance_limit 参数 |

---

## 附录 A: 快速启动脚本

创建 `quick_start.sh` (Linux/Mac) 或 `quick_start.bat` (Windows):

```bash
#!/bin/bash
# A.M.A.N.I. V4.0 快速启动脚本

echo "🚀 A.M.A.N.I. V4.0 系统初始化..."

# 1. 安装依赖
echo "📦 安装依赖..."
pip install -q streamlit chromadb pandas numpy openai anthropic google-cloud-aiplatform python-dotenv

# 2. 检查 .env
if [ ! -f .env ]; then
    echo "⚠️  .env 文件不存在，从 .env.example 复制..."
    cp .env.example .env
    echo "❗ 请编辑 .env 文件填入 API keys，然后重新运行此脚本"
    exit 1
fi

# 3. 初始化 ChromaDB
if [ ! -d amah_vector_db ]; then
    echo "🗄️  初始化 ChromaDB..."
    python batch_build_db.py
    python expert_bulk_loader.py
else
    echo "✅ ChromaDB 已存在"
fi

# 4. 生成物理节点注册表
if [ ! -f physical_node_registry.json ]; then
    echo "🗺️  生成物理节点注册表..."
    python sync_l2_to_chromadb.py
else
    echo "✅ physical_node_registry.json 已存在"
fi

# 5. 验证基准
echo "🔍 运行基准检查..."
python check_v4_baseline.py

# 6. 启动 UI
echo "🌐 启动 Streamlit UI..."
streamlit run app.py
```

---

## 附录 B: 故障排查

### B.1 ChromaDB 初始化失败

**错误：** `chromadb.errors.InvalidCollectionException`

**解决：**
```bash
# 删除旧数据库
rm -rf amah_vector_db/
# 重新初始化
python batch_build_db.py
```

### B.2 L1 Entropy Gate 频繁拦截

**症状：** 大部分请求被 L1 拦截

**调试：**
```python
from amani_trinity_bridge import ECNNSentinel

sentinel = ECNNSentinel(d_threshold=0.79, variance_limit=0.005)
text = "您的测试文本"
passed, d_eff, var_ent, agid = sentinel.gate(text)
print(f"D: {d_eff}, Variance: {var_ent}, Passed: {passed}")
```

**调整：** 如果 variance 过高，考虑增加 `variance_limit` 到 0.01

### B.3 Trinity API 超时

**错误：** `asyncio.TimeoutError`

**解决：**
```python
# 在 trinity_api_connector.py line 102 增加超时
tasks = {m: asyncio.wait_for(self.get_model_logic(m, request), timeout=20.0)  # 从 12.0 增加到 20.0
```

---

**文档版本：** 1.0
**最后更新：** 2026-02-02
**负责人：** Smith Lin
**审核人：** Claude Sonnet 4.5

*End of Deployment Readiness Checklist*
