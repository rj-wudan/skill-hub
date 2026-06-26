# 802.11 管理帧差异字段协议解读指南

> 当 diff 报告中出现某个字段差异时，快速查阅本指南了解其协议含义、单位、影响等级。
> 基于 IEEE 802.11-2020/ax/be 标准。

---

## Action 帧字段

### Block Ack Timeout Value（ADDBA Request/Response）

| 属性 | 值 |
|------|-----|
| **定义章节** | §9.4.1.14 (Block Ack Timeout Value field) |
| **字段长度** | 2 octets (16 bits) |
| **单位** | **TUs (Time Units)** — 1 TU = 1024 μs ≈ 1.024 ms |
| **取值范围** | 0 ~ 65535 |
| **含义** | BA 协议协商后，若在该时间段内该 TID 上无任何帧交换（Data / BlockAckReq / BlockAck），则 BA 协议自动拆除 |
| **特殊值 0** | 永不超时 — BA 不会因空闲而自动失效 |
| **协议定位** | ADDBA Request 帧中为 advisory（建议性），ADDBA Response 中为协商确认值 |

**差异影响**：
- 两者不同但都非 0 → 较小值的一方先触发超时，主动发送 DELBA
- 一个为 0、另一个非 0 → 为 0 方永不主动拆除，依赖对端 DELBA
- 值差异不是协议错误，但可能导致单方已拆除、另一方仍认为有效（额外 DELBA 交互）
- 漫游场景：旧 AP 上残留 BA 若 timeout=0 则永不释放 → 资源泄漏风险

**常见值**：
- AP 侧常设 0（让 STA 管理生命周期）
- STA 侧常见 0 ~ 500 TU
- 视频/VoIP 场景建议 500~1000 TU 避免频繁重建

### Buffer Size（ADDBA Request/Response）

| 属性 | 值 |
|------|-----|
| **定义章节** | §9.4.1.13 (Block Ack Parameter Set) |
| **字段长度** | 6 bits (Block Ack Parameter Set 内) |
| **含义** | 接收方可缓存的 MPDU 最大数量 (WinSize_R)，即 BA 位图大小 |
| **取值** | 0=1, 1=2, ..., 63=64 (基本)；配合 Extended Buffer Size (ADDBA Extension 元素) 可达 1024 |
| **影响** | 决定传输窗口大小和重排序缓冲区容量 → 直接影响吞吐量 |

---

## Capability Information 字段

### Privacy (Bit 4)

| 属性 | 值 |
|------|-----|
| **位置** | Capability Information 字段 Bit 4 |
| **含义** | AP 要求所有 STA 使用加密（WEP/WPA/WPA2/WPA3） |
| **影响** | 🔴 不匹配 → 关联失败 (Status Code 18: Association denied due to requesting station not supporting all rates) |
| **关联场景** | STA 的 AssocReq 中必须匹配 AP Beacon 中的 Privacy 位 |

### Short Preamble (Bit 5)

| 属性 | 值 |
|------|-----|
| **含义** | 支持短前导码（802.11b/g 兼容性标志） |
| **影响** | 🟢 现代设备基本都支持，差异不影响功能 |

### Spectrum Management (Bit 8)

| 属性 | 值 |
|------|-----|
| **含义** | 支持频谱管理（DFS/TPC），5GHz 频段必需 |
| **影响** | 🔴 5GHz 频段缺失此位 → 无法关联（法规要求） |

---

## HT/VHT/HE Capabilities 字段

### HT Capabilities: Supported Channel Width Set

| 属性 | 值 |
|------|-----|
| **含义** | 0=20MHz only, 1=20/40MHz |
| **影响** | 🔴 40MHz 使单流速率翻倍。不匹配 → HT Operation 中可能降为 20MHz |

### HT Capabilities: Short GI for 20/40 MHz

| 属性 | 值 |
|------|-----|
| **含义** | SGI=400ns (vs 标准 800ns GI)，提升约 11% 速率 |
| **影响** | 🟡 差异导致 SGI 无法协商启用 |

### VHT Capabilities: Supported Channel Width Set

| 属性 | 值 |
|------|-----|
| **取值** | 0=80MHz, 1=160MHz, 2=80+80MHz |
| **影响** | 🔴 直接影响最大物理速率 |

### HE Capabilities: HE MAC Capabilities 各子字段

| 字段 | 含义 | 影响 |
|------|------|------|
| OM Control Support | 支持 Operating Mode 控制 | 🟢 |
| Maximum AMPDU Length Exponent | A-MPDU 最大长度 | 🟡 影响聚合效率 |
| Multi-TID Aggregation Support | 多 TID 聚合 | 🟡 影响 QoS 聚合效率 |

---

## RSN 字段

### Group Cipher Suite

| 属性 | 值 |
|------|-----|
| **含义** | 组播/广播加密套件 |
| **常见值** | 00-0F-AC-04 (CCMP), 00-0F-AC-06 (GCMP), 00-0F-AC-08 (GCMP-256) |
| **影响** | 🔴 不匹配 → 关联失败。AES-CCMP 为最低共同要求 |

### Pairwise Cipher Suite

| 属性 | 值 |
|------|-----|
| **含义** | 单播加密套件列表 |
| **影响** | 🔴 AP 须在 STA 请求的列表中选一个；无交集 → 关联失败 |

### AKM Suite

| 属性 | 值 |
|------|-----|
| **含义** | 认证和密钥管理套件 |
| **常见值** | 00-0F-AC-02 (PSK), 00-0F-AC-06 (802.1X), 00-0F-AC-08 (SAE/WPA3), 00-0F-AC-12 (FT-PSK), 00-0F-AC-0B (FT-802.1X) |
| **影响** | 🔴 无交集的 AKM → 安全协商失败 |

### RSN Capabilities: MFP Required/Capable

| 属性 | 值 |
|------|-----|
| **含义** | Management Frame Protection (802.11w) |
| **影响** | 🔴 MFP Required 且 STA 不支持 → 关联失败 (Status Code 31) |

---

## WMM/WME 字段

### WMM Parameter: AIFSN / ECWmin / ECWmax / TXOP Limit

| 属性 | 值 |
|------|-----|
| **含义** | EDCA 参数 — 控制各 AC (VO/VI/BE/BK) 的信道竞争行为 |
| **单位** | AIFSN=slots, ECWmin/max=slots, TXOP Limit=32μs 单位 |
| **影响** | 🟡 参数差异影响 QoS 优先级和空口公平性 |

---

## Power / Regulatory 字段

### Country: First Channel Number / Number of Channels / Max Transmit Power

| 属性 | 值 |
|------|-----|
| **含义** | 国家码规定的可用信道和最大发射功率 |
| **单位** | Max Transmit Power = dBm |
| **影响** | 🔴 国家码不匹配 → 可能违反法规限制 |

### Power Constraint

| 属性 | 值 |
|------|-----|
| **单位** | dB |
| **含义** | STA 发射功率需降低该值（相对法规上限） |
| **影响** | 🟡 差异影响 STA 实际发射功率 → 覆盖范围 |

---

## 时间单位速查

| 字段 | 单位 | 换算 |
|------|------|------|
| Beacon Interval | TU | 1 TU = 1024 μs |
| DTIM Period | Beacon Interval 倍数 | 无量纲 |
| Block Ack Timeout | TU | 1 TU = 1024 μs |
| BSS Max Idle Period | 1000 TU (= 1.024 s) | 特殊大单位 |
| TXOP Limit | 32 μs | 802.11 PHY 时隙基准 |
| TSF Timer | μs | 1 MHz 时钟 |
| Channel Switch Count | Beacon Interval 倍数 | 无量纲 |
