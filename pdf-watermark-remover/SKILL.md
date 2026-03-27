---
name: pdf-watermark-remover
description: 去除PDF中的旋转/斜体文字水印，保留正文完整
---

# PDF水印去除工具

去除PDF文档中的旋转文字水印（如45度角的人名+日期水印），同时完整保留正文内容。

## 适用场景

- PDF中包含斜体/旋转文字水印
- 水印内容通常包括：人名+日期、单位名称、保密标识等
- 水印重复出现在页面各处
- 需要保留原始正文的字体、颜色、格式

## 使用方法

### 1. 安装依赖

```bash
pip install pikepdf
```

### 2. 运行脚本

```python
from remove_watermark import remove_rotated_watermark

# 处理单个文件
remove_rotated_watermark(
    input_path="input.pdf",
    output_path="output.pdf"
)

# 批量处理目录
from remove_watermark import batch_remove_watermark

batch_remove_watermark(
    source_dir="/path/to/input",
    target_dir="/path/to/output"
)
```

### 3. 命令行使用

```bash
python remove_watermark.py -i input.pdf -o output.pdf
python remove_watermark.py -s /path/to/source -t /path/to/target
```

## 技术原理

### 水印识别特征

1. **旋转角度**: 水印通常旋转30-45度
2. **PDF内容流**: Tm操作中的b和c参数不为0表示旋转
3. **常见模式**: 
   - "人名 YYYY-MM-DD"
   - "单位名称+人名"
   - "保密标识+下载时间"

### 核心算法

通过直接编辑PDF内容流，删除包含旋转矩阵的文本块：

```
BT (Begin Text) ... Tm (Text Matrix) ... ET (End Text)
```

如果Tm操作的b或c参数不为0，说明文本有旋转，整个BT...ET块被删除。

## 注意事项

### 成功的方法
- ✅ pikepdf直接编辑内容流
- ✅ 检测Tm矩阵的旋转参数
- ✅ 删除整个BT...ET文本块

### 避免的方法
- ❌ PyMuPDF redaction - 会误删正文
- ❌ 白色矩形覆盖 - 无法覆盖旋转文本
- ❌ 字体名称过滤 - 可能误删正文

## 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| input_path | str | 输入PDF文件路径 |
| output_path | str | 输出PDF文件路径 |
| source_dir | str | 源目录（批量处理） |
| target_dir | str | 目标目录（批量处理） |
| rotation_threshold | float | 旋转检测阈值（默认0.01） |

## 示例

### 示例1: 处理单个文件
```python
from remove_watermark import remove_rotated_watermark

remove_rotated_watermark(
    "report.pdf",
    "report_clean.pdf"
)
```

### 示例2: 批量处理
```python
from remove_watermark import batch_remove_watermark

batch_remove_watermark(
    source_dir="~/Documents/watermarked",
    target_dir="~/Documents/clean"
)
```

## 故障排除

### 水印未被去除
- 检查水印是否真的是旋转文本（dir向量y≠0）
- 调整rotation_threshold参数
- 使用PyMuPDF检查文本特征：`page.get_text("dict")`

### 正文被误删
- 确保使用本skill提供的方法
- 不要直接使用PyMuPDF的redaction功能
- 检查是否有其他旋转的非水印内容

## 依赖

- Python 3.7+
- pikepdf
- PyMuPDF (可选，用于验证)
