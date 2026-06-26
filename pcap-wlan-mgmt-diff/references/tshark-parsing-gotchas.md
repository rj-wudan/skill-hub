# tshark -V 解析注意事项

> 在实现 `parse_tshark_verbose()` 过程中踩过的坑。

## 1. tshark 输出目标

- **tshark -V 默认输出到 stderr**，而非 stdout
- `subprocess.run(capture_output=True)` 时，stderr 和 stdout 都会被捕获
- 返回时拼接 `r.stderr + r.stdout`，其中 stderr 是主体内容

## 2. 帧边界检测

- 帧边界标记：`Frame N: Packet, ...`（行首，无缩进）
- **不要**使用 `Frame Number:`、`Frame Length:` 等缩进字段作为帧边界
- tshark 4.6.x 中，`-c N -V` 可能只输出 1 帧（bug），应避免使用 `-c` 配合 `-V`

## 3. 管理帧体入口

- **正确标记**：`IEEE 802.11 Wireless Management`（tshark 4.x）
- **错误标记**：`IEEE 802.11 wireless LAN management frame`（旧版本/文档不一致）
- 不同帧类型（Probe/Auth/Action）都使用相同标记

## 4. 双遍解析

- 需要使用 `-2 -R` 进行双遍解析才能正确应用 read filter
- `-Y` display filter 在 `-V` 模式下可能不工作

## 5. Bitmap 字段 regex

- tshark bitmap 格式：`.... .... .... ...1 = Name: value`
- 混合模式：`.... 1001 = Name: value`（数字 + 点号，空格分隔）
- **错误 regex**：`^[.01]+` — 在空格处停止，不匹配混合模式
- **正确 regex**：`^[.01\s]+` — 允许空格

## 6. Fixed parameters

- Action/Auth/Deauth 帧没有 Tagged parameters，只有 Fixed parameters
- Fixed parameters 中的字段格式与 Tag 子字段相同
- 需作为伪 IE（id=-1）处理

## 7. Action 帧子类型

- Category code 值格式：`"Block Ack (3)"` — 包含名称和数字
- Action code 值格式：`"Delete Block Ack (0x02)"`
- 提取数字需用 `re.search(r'\((\d+)\)')`
- Action code 名称提取需用 `re.sub(r'\s*\(.*', '', value)`
