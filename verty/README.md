# Verty - 视频事故检测与分析工具

## 项目简介

Verty 是一个用于视频事故检测与分析的 Python 工具集，主要功能包括视频帧提取、图像事故识别和结果统计分析。该项目通过调用外部 API 对交通事故图像进行智能识别，并生成详细的分析报告。

## 项目结构

```
verty/
├── src/                          # 源代码目录
│   ├── clear_step_0.py          # 清理工具：清除旧文件和图片
│   ├── cut_video_img_step_1.py  # 视频处理：从视频中提取关键帧
│   └── verty_img_save_res_to_exl_step_1.py  # 图像分析：调用API识别并生成Excel报告
├── video/                        # 视频文件存储目录
│   ├── left_video/              # 负样本视频（正常场景）
│   └── right_video/             # 正样本视频（事故场景）
├── left_img/                    # 负样本图片（从left_video提取）
├── right_img/                   # 正样本图片（从right_video提取）
├── extracted_frames/            # 其他提取的帧图片
├── 异常视频/                     # 异常视频存储
└── res.xlsx                     # 分析结果Excel文件（自动生成）
```

## 功能模块详解

### 1. clear_step_0.py - 数据清理模块

**功能**：清理项目中的旧数据，为新的分析做准备。

**主要操作**：
- 删除之前生成的 `res.xlsx` 结果文件
- 清空 `left_img` 和 `right_img` 目录中的所有 `.jpg` 图片文件

**使用方法**：
```bash
python src/clear_step_0.py
```

### 2. cut_video_img_step_1.py - 视频帧提取模块

**功能**：从视频文件中提取关键帧图片，用于后续的事故识别分析。

**核心特性**：
- 支持并行处理多个视频文件
- 从视频第9秒开始提取10帧图片（每秒1帧）
- 自动处理视频读取错误和重试机制
- 支持 MP4 格式视频文件

**处理流程**：
1. 扫描 `video/left_video/` 和 `video/right_video/` 目录
2. 对每个 MP4 视频文件，从第9秒开始提取10帧
3. 将提取的帧保存到对应的图片目录（left_img 或 right_img）
4. 图片命名格式：`{视频名称}_{帧序号:02d}.jpg`

**使用方法**：
```bash
python src/cut_video_img_step_1.py
```

**依赖库**：
- `opencv-python` (cv2)
- `concurrent.futures`

### 3. verty_img_save_res_to_exl_step_1.py - 图像识别与报告生成模块

**功能**：调用外部 API 对提取的图片进行事故识别，并生成详细的 Excel 分析报告。

**核心特性**：
- 支持多线程并行处理图片
- 集成进度条显示处理进度
- 自动区分正样本和负样本
- 生成详细的 Excel 分析报告

**API 接口**：
- **URL**: `http://35.46.5.84:18000/check_accident`
- **方法**: POST
- **数据格式**: JSON `{"image": "base64编码的图片数据"}`
- **返回格式**: 
  ```json
  {
    "accident": true/false,
    "time": "时间信息",
    "address": "地址信息", 
    "description": "描述信息"
  }
  ```

**Excel 报告字段**：
- **样本类型**：正样本（right_img）或负样本（left_img）
- **是否识别成功**：API 返回的事故识别结果
- **识别结果**：包含时间、地址、描述的详细信息
- **图片名称**：原始图片文件名
- **图片来自的文件夹名称**：图片所在目录

**使用方法**：
```bash
python src/verty_img_save_res_to_exl_step_1.py
```

**依赖库**：
- `requests` - HTTP 请求
- `openpyxl` - Excel 文件操作
- `tqdm` - 进度条显示
- `base64` - 图片编码

## 完整工作流程

### 步骤1：环境准备
```bash
# 安装依赖
pip install opencv-python requests openpyxl tqdm

# 准备视频文件
# 将正常场景视频放入 video/left_video/
# 将事故场景视频放入 video/right_video/
```

### 步骤2：清理旧数据
```bash
python src/clear_step_0.py
```

### 步骤3：提取视频帧
```bash
python src/cut_video_img_step_1.py
```

### 步骤4：识别分析并生成报告
```bash
python src/verty_img_save_res_to_exl_step_1.py
```

### 步骤5：查看结果
分析完成后，在项目根目录下会生成 `res.xlsx` 文件，包含所有图片的识别结果和统计信息。

## 注意事项

1. **网络连接**：确保能够访问 API 服务器 `35.46.5.84:18000`
2. **视频格式**：目前仅支持 MP4 格式的视频文件
3. **图片格式**：支持 JPG、JPEG、PNG 格式的图片文件
4. **路径配置**：代码中使用了绝对路径，使用前请根据实际情况修改路径配置
5. **API 限制**：请注意 API 调用频率限制，避免过于频繁的请求

## 错误处理

- **视频读取失败**：自动重试3次，超过次数后跳过该视频
- **API 调用失败**：记录错误信息并继续处理其他图片
- **文件操作错误**：提供详细的错误信息便于调试

## 扩展建议

1. **配置文件**：将硬编码的路径和 API 地址提取到配置文件中
2. **批处理脚本**：创建一键执行所有步骤的批处理脚本
3. **结果可视化**：添加图表生成功能，直观展示识别结果统计
4. **多格式支持**：扩展支持更多视频和图片格式
5. **日志系统**：添加详细的日志记录功能

## 技术栈

- **Python 3.x**
- **OpenCV** - 视频处理
- **Requests** - HTTP 客户端
- **OpenPyXL** - Excel 文件操作
- **TQDM** - 进度条显示
- **ThreadPoolExecutor** - 多线程处理

---

*该项目用于航天长峰运维团队的视频事故检测分析工作*