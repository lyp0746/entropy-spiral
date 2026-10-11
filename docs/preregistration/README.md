# 事前登记与核销（公开记录）

本目录是书中三项盲测（B1、B2、B3）的**可公开、可时间戳**的登记与核销记录。
它把“我们会诚实核对”从承诺变成一张**外部可检查的账本**：每一条都是 append-only，
观测后不修改旧行，只追加新行。

## 文件

| 文件 | 作用 |
|---|---|
| `registry.json` | 登记本体：预测、观测变量、成功标准、否定条件、基线快照 |
| `checkups.csv` | append-only 核销账本：每次核对追加一行（含日期、值、来源、vintage） |
| `openai_math_snapshot.json` | B3 触发事件（openai/math，2026-10-06）的机器快照 |
| `../../analysis/fetch_openai_math_snapshot.py` | 抓取并固化 B3 触发事件快照 |
| `../../analysis/preregistration_checkup.py` | 校验账本 + 生成快照报告（可扩展为联网抓取） |

## 迁移状态

- **当前（2026-10-11）**：随本仓库提交，公开 git 历史即为时间戳。
- **目标**：迁移到 GitHub Issues 或 OSF（迁移后 `registry.json` 的 `migration` 字段更新为 URL，原提交保留）。
- **核销模板**：`.github/ISSUE_TEMPLATE/blind-test-checkup.yml`，每次核对开一个 issue。

## 核销规则（摘要）

1. 登记在事件之前写定；观测后不回调。
2. 以**方向**（C<1 与否）判定，不以点值判定（命题 4.1）。
3. 核销时四项分开报告：**(i) 原始预测；(ii) 观测结果；(iii) 是否达标；(iv) 差异原因**。
4. I₂ 的事后校准遵循第 14.8.3 节规则 R1–R5（同类事件集、中位数、N^α 转移、偏差声明、事前登记）。

## 操作

```bash
# 校验账本格式并打印当前进度
python analysis/preregistration_checkup.py

# 追加一次核对（示例；实际核对请用真实来源与值）
python analysis/preregistration_checkup.py --append \
  --test B1 --indicator "本币兑美元变动" --value -0.04 --unit ratio \
  --source "IMF IFS" --vintage 2026Q4 --triggered no --note "例行季检"
```

> 数值基线需要联网/官方 vintage 才能填入；离线环境下脚本会写明“待核对”，
> 而不是伪造数值。账本的第一行（`status=baseline`）即为登记时基线。
