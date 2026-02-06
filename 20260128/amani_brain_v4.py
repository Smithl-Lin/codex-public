# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# ==============================================================================
# 🧠 A.M.A.N.I. TRINITY ENGINE V4 — 哨兵层优化
# ==============================================================================
# 哨兵层优化：EntropyUtils 实时输出强制注入 E-CNN 第二通道，替换模拟拼接。
# Channel 1 = 语义嵌入 | Channel 2 = EntropyUtils.calculate_sliding_entropy 实时熵波形
# ==============================================================================

import math
import collections
import hashlib
import numpy as np
import time

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError:
    print("❌ 严重错误: 缺少 PyTorch。请运行: pip install torch torchvision")
    raise

# ------------------------------------------------------------------------------
# AGID 体系
# ------------------------------------------------------------------------------
def to_agid(namespace: str, node_type: str, raw_id) -> str:
    sid = hashlib.sha256(f"{namespace}:{node_type}:{raw_id}".encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"


# ==============================================================================
# 🧩 EntropyUtils — 全息熵纹理，实时输出注入 E-CNN 第二通道
# ==============================================================================
class EntropyUtils:
    @staticmethod
    def calculate_sliding_entropy(text, window_size=5):
        """
        计算文本熵纹理（波形）。实时输出，强制作为 E-CNN 第二通道输入，禁止模拟拼接。
        返回 (tensor [1, seq, 1], variance)
        """
        tokens = list(text)
        seq_len = len(tokens)
        entropy_seq = []

        if seq_len == 0:
            return torch.zeros(1, 1, 1), 0.0

        for i in range(seq_len):
            start = max(0, i - window_size // 2)
            end = min(seq_len, i + window_size // 2 + 1)
            window = tokens[start:end]
            counts = collections.Counter(window)
            ent = 0.0
            total = len(window)
            for count in counts.values():
                p = count / total
                ent -= p * math.log2(p) if p > 0 else 0
            entropy_seq.append(ent)

        # 实时熵序列 → [1, seq_len, 1]，作为 E-CNN 第二通道唯一来源
        channel2_entropy = torch.tensor(entropy_seq, dtype=torch.float32).unsqueeze(0).unsqueeze(2)
        variance = np.var(entropy_seq) if entropy_seq else 0.0
        return channel2_entropy, variance

    @staticmethod
    def variance_physical_intercept(variance: float, threshold: float = 0.005) -> bool:
        return float(variance) > threshold


# ==============================================================================
# 🛡️ E-CNN 哨兵 — 第二通道强制为 EntropyUtils 实时输出（无模拟拼接）
# ==============================================================================
class ECNN_Sentinel(nn.Module):
    """
    Channel 1: 语义嵌入 (embed_dim)
    Channel 2: 仅接受 EntropyUtils.calculate_sliding_entropy 的实时输出，不接模拟值。
    """

    def __init__(self, vocab_size=5000, embed_dim=128, num_filters=64, kernel_sizes=[3, 4, 5]):
        super(ECNN_Sentinel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        # in_channels = embed_dim + 1，其中 +1 为第二通道（熵）
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=embed_dim + 1, out_channels=num_filters, kernel_size=k)
            for k in kernel_sizes
        ])
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(len(kernel_sizes) * num_filters, 3)

    def forward(self, x_indices, channel2_entropy_tensor):
        """
        x_indices: [B, L]; channel2_entropy_tensor: [B, L, 1] 来自 EntropyUtils 实时输出。
        禁止传入模拟拼接的占位 tensor，必须为 calculate_sliding_entropy 的返回值。
        """
        # Channel 1: 语义
        ch1_embed = self.embedding(x_indices)  # [B, L, embed_dim]
        # Channel 2: 强制为 EntropyUtils 实时熵，替换原模拟拼接
        combined = torch.cat((ch1_embed, channel2_entropy_tensor), dim=2)  # [B, L, embed_dim+1]
        combined = combined.permute(0, 2, 1)  # [B, embed_dim+1, L]
        conved = [F.relu(conv(combined)) for conv in self.convs]
        pooled = [F.adaptive_max_pool1d(conv, 1).squeeze(2) for conv in conved]
        cat = torch.cat(pooled, dim=1)
        cat = self.dropout(cat)
        logits = self.fc(cat)
        return F.softmax(logits, dim=1)


# ==============================================================================
# 🔗 GNN Nexus — 输出 AGID
# ==============================================================================
class GNN_Nexus_Sim(nn.Module):
    def __init__(self, num_assets=200000, feature_dim=192):
        super(GNN_Nexus_Sim, self).__init__()
        self.asset_memory = nn.Parameter(torch.randn(100, feature_dim))
        self.query_proj = nn.Linear(192, feature_dim)

    def forward(self, intent_vector):
        query = self.query_proj(intent_vector)
        scores = torch.matmul(query, self.asset_memory.t())
        attention = F.softmax(scores, dim=1)
        best_asset_idx = torch.argmax(attention, dim=1)
        return best_asset_idx, attention


# ==============================================================================
# 🧠 AMANI Brain V4 — 哨兵层优化：仅用 EntropyUtils 实时输出注入 E-CNN
# ==============================================================================
class AMANI_Brain:
    def __init__(self):
        print("🧠 正在初始化 A.M.A.N.I. Trinity Engine V4 (哨兵层优化：熵实时注入 E-CNN 第二通道)...")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.sentinel = ECNN_Sentinel().to(self.device)
        self.nexus = GNN_Nexus_Sim().to(self.device)
        self.sentinel.eval()
        self.VARIANCE_INTERCEPT_THRESHOLD = 0.005

    def _text_to_tensor(self, text):
        indices = [hash(c) % 5000 for c in text]
        return torch.tensor(indices, dtype=torch.long).unsqueeze(0).to(self.device)

    def process_request(self, text):
        print(f"\n📩 [INPUT] \"{text}\"")
        start_time = time.time()

        # 1. EntropyUtils 实时输出，作为 E-CNN 第二通道唯一输入（无模拟拼接）
        channel2_entropy, entropy_variance = EntropyUtils.calculate_sliding_entropy(text)
        channel2_entropy = channel2_entropy.to(self.device)
        avg_entropy = channel2_entropy.mean().item()
        print(f"   🌊 全息熵(实时→E-CNN 第二通道): 均值 {avg_entropy:.4f} | 方差 {entropy_variance:.6f}")

        # 2. variance > 0.005 物理拦截
        if EntropyUtils.variance_physical_intercept(entropy_variance, self.VARIANCE_INTERCEPT_THRESHOLD):
            agid_intercept = to_agid("MAYO", "INTERCEPT", f"var_{entropy_variance:.6f}")
            print(f"   🚫 物理拦截: 方差 {entropy_variance:.6f} > 0.005 | {agid_intercept}")
            return agid_intercept

        # 3. 哨兵：第二通道强制为 EntropyUtils 实时输出
        x_indices = self._text_to_tensor(text)
        with torch.no_grad():
            routing_weights = self.sentinel(x_indices, channel2_entropy)

        w_ethnic, w_geo, w_lang = routing_weights[0].tolist()
        print(f"   🧠 路由: [族群]{w_ethnic:.2f} [区域]{w_geo:.2f} [语言]{w_lang:.2f}")

        if avg_entropy < 1.5 or w_geo > 0.5:
            dummy_intent = torch.randn(1, 192).to(self.device)
            asset_id, _ = self.nexus(dummy_intent)
            agid_node = to_agid("MAYO", "NODE", 200000 + asset_id.item())
            print(f"   📍 GNN 锁定: {agid_node}")
            final_decision = agid_node
        else:
            final_decision = to_agid("MAYO", "MODE", "MIXED_EMPATHY")

        print(f"   ✅ 输出节点: {final_decision} | ⏱️ {(time.time()-start_time)*1000:.2f} ms")
        return final_decision


if __name__ == "__main__":
    brain = AMANI_Brain()
    brain.process_request("医生，我觉得最近有点心慌。")
    brain.process_request("准备阑尾切除术，静脉注射丙泊酚20mg。")
