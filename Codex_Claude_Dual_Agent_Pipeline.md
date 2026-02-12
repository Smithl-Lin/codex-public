# Codex + Claude Code 双代理流水线

## 从批量审查修复到高端精修的工业级工作流

---

## 核心架构

完全可行，而且这正是2026年最前沿的工程实践。架构如下：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                             │
│                                                                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐         │
│  │   Stage 1    │────▶│   Stage 2    │────▶│   Stage 3    │         │
│  │  Codex 初筛  │     │  Claude 精审 │     │  人工终审    │         │
│  │  (自动/异步) │     │  (深度/交互) │     │  (合并决策)  │         │
│  └──────────────┘     └──────────────┘     └──────────────┘         │
│                                                                      │
│  AGENTS.md            CLAUDE.md            CODEOWNERS               │
│  (Codex规则)          (Claude规则)         (保护分支)               │
└─────────────────────────────────────────────────────────────────────┘
```

**Stage 1: Codex** — 快速、异步、批量。做lint级别的修复、模式化bug捕获、测试生成、格式标准化。产出：一个已经"干净了80%"的PR。

**Stage 2: Claude Code** — 深度、交互、架构级。做安全审查、设计模式评估、复杂逻辑验证、文档质量检查。产出：带有行内批注的高质量审查报告。

**Stage 3: 人工** — 最终决策权。审查两层AI的输出，合并或要求修改。

---

## 第一层：Codex 自动化设置

### 1.1 AGENTS.md — Codex的项目记忆

Codex使用`AGENTS.md`（相当于Claude Code的`CLAUDE.md`）。在项目根目录创建：

```markdown
# AGENTS.md

## Project
PD multimodal biomarker analysis. Python 3.11 + R 4.3.

## Code Standards
- Python: Black, type hints, NumPy-style docstrings
- No patient data in code/comments
- All paths via config.yaml
- Statistical tests must report effect size + CI

## Review Guidelines
- Treat hardcoded file paths as P0
- Treat missing type hints as P1  
- Treat missing docstrings on public functions as P1
- Treat unused imports as P2
- Treat TODO/FIXME in production code as P2

## Commands
```bash
python -m pytest tests/ -v
flake8 src/ --max-line-length 100
mypy src/ --ignore-missing-imports
black --check src/
```
```

### 1.2 Codex GitHub Action — PR自动审查

创建 `.github/workflows/codex-review.yml`：

```yaml
name: Codex Auto Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  codex-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: openai/codex-action@v1
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          prompt: |
            Review this PR against AGENTS.md guidelines.
            Focus on:
            1. Code style violations (Black, type hints, docstrings)
            2. Hardcoded paths or credentials
            3. Missing tests for new functions
            4. Unused imports and dead code
            5. Data leakage risks in ML pipelines
            
            For each issue found:
            - Fix it directly if the fix is unambiguous
            - Flag it with severity (P0/P1/P2) if it requires human judgment
            
            After fixes, run: python -m pytest tests/ -v
            Commit fixes with message: "fix(codex): automated code quality fixes"
          safety-strategy: sandbox
```

### 1.3 Codex CLI — 本地批量修复

在推送PR之前，用Codex CLI在本地先做一轮自动修复：

```bash
# 快速修复模式（非交互，自动执行）
codex exec "Review all Python files in src/. Fix type hints, \
  add missing docstrings, remove unused imports, \
  standardize formatting with Black. Run tests after."

# 并行多任务（Codex Cloud异步执行）
codex cloud exec --env my-env "Fix all flake8 violations in src/models/"
codex cloud exec --env my-env "Add type hints to src/preprocessing/"
codex cloud exec --env my-env "Generate missing unit tests for src/utils/"
# 三个任务并行运行，各自产出diff
```

Codex的优势在这一层体现：**速度快、成本低、可以并行开多个任务**。它不需要你坐在旁边盯着，可以去做其他事。

---

## 第二层：Claude Code 深度审查

### 2.1 Claude Code GitHub Action — 高端PR审查

在Codex完成自动修复并提交PR后，触发Claude Code做第二轮深度审查。

创建 `.github/workflows/claude-review.yml`：

```yaml
name: Claude Deep Review
on:
  pull_request_review:
    types: [submitted]
  issue_comment:
    types: [created]

jobs:
  claude-deep-review:
    # 只在Codex审查完成后触发，或手动@claude
    if: |
      (github.event_name == 'issue_comment' && 
       contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review' &&
       github.event.review.user.login == 'codex-bot')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          model: claude-opus-4-6
          prompt: |
            This PR has already passed Codex automated review (Stage 1).
            Perform a Stage 2 deep review focusing on issues Codex cannot catch:
            
            ## Architecture Review
            - Module coupling and dependency direction
            - Design pattern appropriateness
            - Separation of concerns violations
            - API surface design quality
            
            ## ML/Data Science Specific
            - Data leakage between train/test splits
            - Feature engineering validity
            - Statistical method appropriateness
            - Reproducibility (random seeds, version pinning)
            - Model evaluation metric selection
            
            ## Security & Compliance
            - PHI/PII exposure risks (Mayo Clinic IRB compliance)
            - Input validation on data pipelines
            - Dependency vulnerability assessment
            
            ## Logic & Correctness
            - Edge cases in numerical computations
            - Off-by-one errors in data indexing
            - Null/NaN handling in data pipelines
            - Race conditions in parallel processing
            
            ## Documentation Quality
            - Are docstrings accurate (not just present)?
            - Do comments explain WHY, not just WHAT?
            - Is README current with actual behavior?
            
            Post findings as inline PR comments with confidence scores.
            Only flag issues with confidence >= 80.
          claude_args: "--allowedTools 'mcp__github__*,Bash(python -m pytest:*),Read,Grep'"
```

### 2.2 Claude Code 本地交互式精审

对于复杂的架构决策，在本地用Claude Code交互式审查：

```bash
# 启动Claude Code，加载项目上下文
cd your-project
claude

# 使用内置的code-review插件（并行启动4个审查代理）
> /code-review

# 或使用自定义的深度审查命令
> /deep-review
```

**自定义 `/deep-review` 命令** — `.claude/commands/deep-review.md`：

```markdown
Perform a deep architectural review that goes beyond what automated tools catch.

## Phase 1: Understand Intent
Read the most recent commits and PR description. What is this change trying to accomplish?

## Phase 2: Architecture Impact
- Does this change respect existing module boundaries?
- Are there hidden coupling points introduced?
- Does the data flow make sense end-to-end?
- Would this change survive a 10x scale increase?

## Phase 3: ML Pipeline Integrity
- Trace the data from raw input to model prediction
- Verify no information from test set leaks into training
- Check that feature transformations are fitted on train only
- Verify model serialization includes preprocessing steps

## Phase 4: Statistical Rigor
- Are the right statistical tests used for the data distribution?
- Is multiple comparison correction applied where needed?
- Are confidence intervals reported alongside p-values?
- Is effect size meaningful, not just statistically significant?

## Phase 5: Recommendations
For each finding, provide:
- Severity (CRITICAL / HIGH / MEDIUM / LOW)
- Confidence (0-100)
- Specific code location
- Recommended fix with code example

Only report findings with confidence >= 80.
```

### 2.3 Claude Code Security Review

Anthropic提供了官方的安全审查工具：

```bash
# 在Claude Code中直接运行
> /security-review

# 或作为GitHub Action自动触发
```

这会启动专门的安全扫描代理，检查：依赖漏洞、硬编码凭证、输入验证缺失、SQL注入风险等。

---

## 第三层：流水线串联

### 3.1 完整的GitHub Actions流水线

将两层审查串联为一条流水线：

```yaml
name: Dual-Agent Review Pipeline
on:
  pull_request:
    types: [opened, synchronize, ready_for_review]

jobs:
  # ═══════════════════════════════════════
  # Stage 1: Codex 快速修复 + 初审
  # ═══════════════════════════════════════
  codex-fix-and-review:
    runs-on: ubuntu-latest
    permissions:
      contents: write        # Codex需要推送修复
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - name: Run tests first
        run: |
          pip install -r requirements.txt
          python -m pytest tests/ -v --tb=short
      - uses: openai/codex-action@v1
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          prompt: |
            Fix all code style issues, add missing type hints,
            remove unused imports. Run tests after fixes.
            Post a summary comment on the PR.
          safety-strategy: sandbox

  # ═══════════════════════════════════════
  # Stage 2: Claude Code 深度审查
  # ═══════════════════════════════════════
  claude-deep-review:
    needs: codex-fix-and-review    # 等Codex完成后再执行
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          model: claude-opus-4-6
          prompt: |
            Codex has completed Stage 1 fixes on this PR.
            Perform Stage 2 deep review: architecture, ML integrity,
            security, statistical rigor. Post inline comments.
            Only flag issues with confidence >= 80.

  # ═══════════════════════════════════════
  # Stage 3: 质量门禁
  # ═══════════════════════════════════════
  quality-gate:
    needs: [codex-fix-and-review, claude-deep-review]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Final test suite
        run: |
          pip install -r requirements.txt
          python -m pytest tests/ -v --cov=src --cov-report=term-missing
          flake8 src/ --max-line-length 100
          mypy src/ --ignore-missing-imports
```

### 3.2 串联逻辑说明

```
PR 提交
  │
  ▼
┌──────────────────────────────────┐
│  Stage 1: Codex (自动, ~5-15分钟)  │
│                                   │
│  ✦ 修复格式问题                    │
│  ✦ 添加缺失的type hints           │
│  ✦ 删除未使用的imports             │
│  ✦ 生成缺失的单元测试              │
│  ✦ 运行测试确认修复不破坏功能       │
│  ✦ 提交修复 + 初审评论              │
└──────────────┬───────────────────┘
               │ (Codex完成后自动触发)
               ▼
┌──────────────────────────────────┐
│  Stage 2: Claude (深度, ~3-8分钟)  │
│                                   │
│  ✦ 架构合理性评估                  │
│  ✦ ML管道数据泄漏检查              │
│  ✦ 统计方法正确性验证              │
│  ✦ 安全/合规扫描 (IRB, PHI)        │
│  ✦ 逻辑边界条件分析                │
│  ✦ 行内评论 (置信度>=80)           │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Stage 3: 人工终审                 │
│                                   │
│  ✦ 审查Codex的自动修复              │
│  ✦ 审查Claude的深度评论             │
│  ✦ 批准/要求修改/拒绝               │
│  ✦ 合并到主分支                     │
└──────────────────────────────────┘
```

---

## 两层代理的分工原则

| 维度 | Codex (Stage 1) | Claude Code (Stage 2) |
|------|:---:|:---:|
| **速度** | 快（5-15分钟） | 中（3-8分钟） |
| **成本** | 低（3-5x更便宜） | 高（更多token） |
| **模式** | 异步/自动 | 可交互/可自动 |
| **擅长** | 批量修复、模式匹配、代码生成 | 深度推理、架构决策、安全分析 |
| **修复能力** | 直接推送修复commit | 主要给建议，需人工确认 |
| **审查深度** | lint级 + 模式级 | 架构级 + 逻辑级 |
| **并行能力** | 强（Cloud多任务） | 中（Worktree并行） |
| **适合任务** | 格式化、类型标注、测试生成、依赖更新 | 设计审查、安全审计、统计验证、复杂重构 |

**一句话总结**：Codex做"体力活"（快速、大量、机械），Claude做"脑力活"（深入、精准、判断）。

---

## 本地开发工作流

不仅仅是CI/CD流水线——日常开发中也可以用双代理模式：

```bash
# ═══════════════════════════════════════
# 日常开发循环
# ═══════════════════════════════════════

# 1. 用Claude Code做架构规划（Plan Mode）
claude
> /plan Implement new feature: add eye tracking biomarker integration

# 2. 批准计划后，用Codex做并行实现
codex exec "Implement the data loader for eye tracking CSV files \
  following the pattern in src/preprocessing/ppmi_loader.py"
codex exec "Write unit tests for eye tracking preprocessing"
# (两个任务并行执行，你去做其他事)

# 3. Codex完成后，用Claude Code做质量审查
claude
> /code-review    # 启动4个并行审查代理

# 4. 修复Claude发现的问题
> Fix the data leakage issue Claude found in the feature engineering step

# 5. 提交
> /commit "feat: add eye tracking biomarker integration"

# 6. PR创建后，GitHub Actions自动触发双层审查
```

---

## 关键配置清单

### 需要的账号和密钥

| 服务 | 用途 | 配置位置 |
|------|------|----------|
| Anthropic API Key | Claude Code GitHub Action | GitHub Secrets: `ANTHROPIC_API_KEY` |
| OpenAI API Key | Codex GitHub Action | GitHub Secrets: `OPENAI_API_KEY` |
| GitHub App (Claude) | PR评论权限 | `claude /install-github-app` |
| GitHub App (Codex) | PR评论权限 | Codex设置面板 |

### 项目文件清单

```
your-project/
├── CLAUDE.md                          # Claude Code项目记忆
├── AGENTS.md                          # Codex项目规则
├── .claude/
│   ├── settings.json                  # 权限、Hooks
│   ├── commands/
│   │   ├── deep-review.md             # /deep-review
│   │   ├── review.md                  # /review (快速)
│   │   └── prepare-release.md         # /prepare-release
│   └── skills/                        # 自定义技能
├── .codex/
│   ├── config.toml                    # Codex CLI配置
│   └── skills/                        # Codex技能
├── .github/
│   └── workflows/
│       ├── codex-review.yml           # Stage 1自动审查
│       ├── claude-review.yml          # Stage 2深度审查
│       └── dual-pipeline.yml          # 完整双层流水线
├── .mcp.json                          # MCP服务器（GitHub, Slack等）
└── ...
```

---

## 渐进式采纳路线

**Week 1**: 创建CLAUDE.md和AGENTS.md，在本地分别试用两个工具

**Week 2**: 配置Codex GitHub Action做PR自动修复

**Week 3**: 配置Claude Code GitHub Action做PR深度审查

**Week 4**: 用`needs:`串联两层，形成完整流水线

**Week 5+**: 根据实际痛点调整AGENTS.md和CLAUDE.md中的审查规则，添加自定义命令

不要试图一步到位。每一层都可以独立运行、独立产生价值。
