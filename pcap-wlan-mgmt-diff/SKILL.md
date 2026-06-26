---
name: pcap-wlan-mgmt-diff
description: "Use when comparing two 802.11 pcap files to diff management frame IE fields. Generates standalone HTML report with per-field protocol impact assessment, tshark-driven full IE decoding, and Action-code-level frame splitting."
version: 1.0.0
author: WLAN Automation Test Engineer
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [802.11, tshark, wireshark, pcap, diff, management-frames, ie, html, impact-analysis]
    category: wlan
    related_skills: [rg-device-testing]
---

# pcap-wlan-mgmt-diff — 802.11 管理帧抓包对比分析

比较两个 pcap/pcapng 文件中的 802.11 管理帧，逐 IE 子字段对比差异，
输出独立 HTML 报告（含协议用途标注和影响等级评估）。

**零依赖**（仅需 tshark ≥ 4.x），基于 Wireshark 完整 802.11 协议栈解码。

## When to Use

- 对比两个 AP/STA 的 Probe/Assoc/Auth 行为差异
- 排查关联失败、安全协商不匹配、能力声明异常
- 分析漫游前后的 BSS 参数变化
- 对比不同固件/配置下的管理帧行为
- 用户提到"抓包对比"、"管理帧差异"、"pcap diff"等

**不要用于**：数据帧吞吐量分析、加密流量解密、实时抓包监控。

## Quick Start

```bash
# 基础对比
python3 scripts/assoc_diff.py ap1.pcap ap2.pcap -o report.html

# 按 STA MAC 过滤（仅对比该 STA 相关的管理帧）
python3 scripts/assoc_diff.py capture_a.pcapng capture_b.pcapng \
    -m 34:cf:f6:e5:63:ed -o report.html

# 大文件 (>100MB) 自动 tshark 预过滤，无需手动处理
```

| 参数 | 说明 |
|------|------|
| `file_a` `file_b` | 两个 pcap/pcapng 文件 |
| `-o report.html` | 输出 HTML 报告 |
| `-m MAC` | 按 STA MAC 过滤 |
| `--no-prefilter` | 禁用自动预过滤 |

## Architecture

```
tshark -r file -2 -R "wlan.da==MAC || ..." -V
  → 完整管理帧文本（Wireshark 协议栈）
  → Python 解析 IEEE 802.11 Wireless Management 节
  → 提取 Fixed params + Tagged params 全部子字段
  → 按帧类型（含 Action code）分组 → 顺序匹配 → 逐对对比
  → HTML 报告 + 影响评估
```

**不需要 scapy**。旧版 scapy 仅少数 Dot11Elt 子类有解码器，大量 IE 显示为"未知"。

## Report Features

### 帧类型处理
- Probe Request/Response、Authentication、Association Request/Response、Reassociation 等标准管理帧类型
- **Action 帧按 Action code 拆分**：`Delete Block Ack`、`Add Block Ack Request`、`Add Block Ack Response` 等各自独立对比
- 广播 Probe Request（SSID 为空）自动过滤
- Deauthentication 帧纳入对比

### IE 子字段展开
基于 tshark 完整协议栈，**所有 IE 的子字段自动展开**，无需硬编码解码器：

- HT/VHT/HE Capabilities & Operation 全部位图子字段
- RSN 安全参数（加密套件、AKM 列表）
- Vendor Specific（WMM/WPA 等厂商扩展）
- Country、Power Constraint、ERP、Extended Capabilities 等
- Action/Auth 帧的 Fixed parameters 节

### 影响评估
每个差异字段标注协议用途和影响等级（🔴高 🟡中 🟢低），报告底部输出综合影响分析：

```
📊 综合影响分析
🔴 高影响 (38 项) — 对吞吐量/安全性/关联有显著影响
   Privacy — 隐私/加密使能：Capability Info Privacy 位 [不匹配导致关联建立失败]
   40MHz支持 — 信道带宽：40MHz使单流速率翻倍 [吞吐量差异可达 2 倍]
🟡 中等影响 (62 项) — 影响QoS/覆盖/漫游等功能
🟢 低影响 (22 项) — 微调参数或兼容性标志
```

知识库覆盖 80+ 常见 802.11 字段，未匹配字段自动留空。

### 差异化分析
自动推理 Wi-Fi 代际（HT/VHT/HE）、射频能力对比（带宽×空间流×SGI）、抓包覆盖范围。

## Pre-requisites

```bash
# 仅需 tshark
sudo apt install tshark        # Debian/Ubuntu
brew install wireshark         # macOS

# 验证
tshark --version  # 应显示 4.x
```

## Common Pitfalls

1. **tshark 版本过低**（< 4.0）：`-2 -R` 双遍解析语法可能不支持，升级到最新版。
2. **MAC 过滤无结果**：检查 MAC 格式（小写、冒号分隔），确认该 STA 的管理帧确实存在于 pcap 中。
3. **大文件解析慢**：pcap > 100MB 自动预过滤管理帧；若仍慢，先用 `tshark -Y "wlan.fc.type==0" -w mgmt.pcapng` 手动预过滤。
4. **Action 帧不显示子类型**：确保 tshark 能正确解析 Action 帧的 Category/Action code 字段。
5. **报告文件过大**：MAC 过滤后通常报告 < 200KB；若未过滤，报告可能 > 1MB。

## Verification Checklist

- [ ] 两个 pcap 文件路径正确且可读
- [ ] tshark 版本 ≥ 4.0（`tshark --version`）
- [ ] 输出 HTML 文件可在浏览器正常打开
- [ ] 帧数量统计与预期一致
- [ ] Action 帧按子类型正确拆分
- [ ] 影响评估标注覆盖关键差异字段
- [ ] 综合影响分析节按等级分类输出

## Script Location

- `scripts/assoc_diff.py` — 主脚本（单文件，零依赖，~1300 行）
- 也可从 `/home/wudan/wlan-scapy/scripts/assoc_diff.py` 获取最新版本

## References

- `references/pcap-analysis-20260624.md` — 真实案例：680C 2.4G vs jingpin1 对比分析
- `references/field-interpretation-guide.md` — 差异字段协议解读指南：Block Ack Timeout、Capability、HT/VHT/HE、RSN、WMM 等字段的单位、含义、影响等级速查
