# 680C2.4G vs jingpin1 抓包对比分析案例

> STA: 34:cf:f6:e5:63:ed | v6.0 分析: 2026-06-24 (scapy) | v8.0 重跑: 2026-06-25 (tshark)
> 报告: /tmp/assoc_diff_tshark.html

## 文件信息

| 项目 | 文件A (680C2.4G) | 文件B (jingpin1) |
|------|-----------------|-----------------|
| 文件名 | 680C2.4G.pcapng | jingpin1.pcapng |
| 预过滤后 | /tmp/680C_mgmt.pcapng | /tmp/jingpin_mgmt.pcapng |
| 管理帧总数 | 468 | 43 |

## 帧数量统计 (MAC 过滤后, tshark v8)

| 帧类型 | A | B | 说明 |
|--------|---|---|------|
| Probe Request | 17 | 21 | 过滤广播后 |
| Probe Response | 424 | 7 | A 多 417 个 (抓包覆盖更大) |
| Authentication | 2 | 2 | 一致 |
| Association Request | 1 | 1 | 一致 |
| Association Response | 1 | 1 | 一致 |
| Action + Deauth | 10 | 2 | A 抓包覆盖更大 |

## v8.0 (tshark) vs v6.0 (scapy) 差异量对比

| 指标 | v6.0 (scapy) | v8.0 (tshark) |
|------|-------------|---------------|
| IE 字段差异 | 36 | 150 |
| 子字段差异 | 22 | 1401 |
| 未知 IE | IE-36/72/90/195 | 全部解析 (20/40 BSS Coexistence, Quiet Channel 等) |
| 解码引擎 | scapy 通用 Dot11Elt | Wireshark 完整 802.11 协议栈 |

## 核心差异

1. **SSID**: A=`RG-AP680C-V2-2.4G`, B=`RG-AP680C-2.4G`
2. **Wi-Fi 代际**: A=802.11n(HT), B=802.11ac(VHT)
3. **射频能力**: A (2×2 40MHz+SGI) > B (1×1 20MHz)
4. **VHT**: 仅 B 有 VHT Capabilities + VHT Operation
5. **OBSS Scan**: 仅 A 有 (IE-74)
6. **A 抓包覆盖远大于 B**: Probe Response 多 417 个
