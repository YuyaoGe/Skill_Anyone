# Skill Anyone

将任何 YouTube 创作者的视频转化为结构化的 AI 技能（Skill）。自动提取知识体系与表达风格，生成可供 AI 助手使用的技能文件，让 AI 像该创作者一样回答问题。

## 工作流程

```
YouTube 视频 → 音频提取 → 文字转录 → 结构化 AI Skill
```

**三阶段处理管线：**

1. **下载** — 通过 yt-dlp 提取音频，支持多线程并发下载
2. **转录** — 优先使用 YouTube 字幕，无字幕时使用 whisper.cpp 本地转录
3. **生成** — 调用 LLM 分析知识与风格，输出标准化 Skill 文件

## 快速开始

```bash
# 安装
pip install -e .

# 配置 API 密钥
cp .env.example .env
# 编辑 .env，填入你的 API Key 和 Base URL

# 处理单个视频
youtuber2skill run https://www.youtube.com/watch?v=xxx

# 处理整个频道
youtuber2skill run https://www.youtube.com/@ChannelName

# 处理播放列表
youtuber2skill run "https://www.youtube.com/playlist?list=PLxxxxx"

# 限制视频数量
youtuber2skill run https://www.youtube.com/@ChannelName --max-videos 20
```

## 分步执行

```bash
# 阶段 1：下载音频
youtuber2skill download https://www.youtube.com/watch?v=xxx -o ./audio/

# 阶段 2：转录音频
youtuber2skill transcribe ./audio/video.wav -o ./transcripts/

# 阶段 3：生成 Skill
youtuber2skill generate ./transcripts/ -o ./skills/
```

## 配置说明

编辑 `config.yaml` 进行自定义配置：

```yaml
downloader:
  cookies_from_browser: ""       # safari / chrome / firefox（可选）
  cookies_file: cookies.txt      # Netscape 格式的 cookie 文件
  quality: 128
  threads: 3                     # 并发下载线程数

transcriber:
  model: medium                  # tiny / base / small / medium / large-v3-turbo
  language: auto                 # auto 自动检测，或指定 zh / en 等
  vad: true

skillgen:
  model: kimi-k2.5
  temperature: 1.0
  # api_key 和 base_url 通过 .env 文件加载

output:
  skills_dir: ./skills
  keep_audio: false
  keep_transcripts: true
```

API 密钥通过 `.env` 文件配置（已在 .gitignore 中）：

```bash
KIMI_API_KEY=your-api-key-here
KIMI_BASE_URL=your-base-url-here
```

## 输出结构

生成的 Skill 遵循 [AgentSkills](https://agentskills.io) 标准：

```
skills/{人物名}/
├── SKILL.md              # 入口文件
├── knowledge.md          # 结构化知识体系
├── style.md              # 表达风格规则
├── meta.json             # 元数据
└── transcripts/          # 原始转录文本
```

## 已生成的 Skill 示例

| Skill | 来源 | 视频数 | 说明 |
|-------|------|--------|------|
| 李沐 | [@mu_li](https://www.youtube.com/@mu_li) | 52 | 论文精读系列，深度学习前沿技术解构 |
| Andrej Karpathy | [@AndrejKarpathy](https://www.youtube.com/@AndrejKarpathy) | 17 | 从零实现神经网络，LLM 训练工程 |
| 吴恩达 | [Deep Learning Specialization](https://www.youtube.com/playlist?list=PLkDaE6sCZn6Hn0vK8co82zjQtt3T2Nkqc) | 34 | 深度学习专项课程，超参数调优与优化 |
| 罗永浩 | [演讲合集](https://www.youtube.com/playlist?list=PLcBaCIfsoC7cdyH8gC1SCWeK1m3KqM2KY) | 5 | 经典演讲合集 |
| 雷军 | [单视频](https://www.youtube.com/watch?v=kK6udIdqE_o) | 1 | 人生低谷与创业经历 |

## 技术栈

| 组件 | 技术 |
|------|------|
| 视频下载 | yt-dlp + ffmpeg |
| 语音转文字 | whisper.cpp（通过 pywhispercpp） |
| Skill 生成 | LLM API（OpenAI 兼容） |
| 命令行 | click |

## 环境要求

- Python 3.10+
- ffmpeg（macOS: `brew install ffmpeg`）
- whisper.cpp 模型文件（pywhispercpp 自动下载）

## 许可证

MIT

---

# Skill Anyone (English)

Transform any YouTube creator's videos into structured AI Skills. Automatically extract knowledge systems and communication styles, generating skill files that enable AI assistants to respond as that creator would.

## Pipeline

```
YouTube Video → Audio Extraction → Transcription → Structured AI Skill
```

**Three-stage processing pipeline:**

1. **Download** — Extract audio via yt-dlp with multi-threaded concurrent downloading
2. **Transcribe** — Use YouTube subtitles when available, fall back to local whisper.cpp
3. **Generate** — Analyze knowledge and style with LLM, output standardized Skill files

## Quick Start

```bash
# Install
pip install -e .

# Configure API credentials
cp .env.example .env
# Edit .env with your API Key and Base URL

# Process a single video
youtuber2skill run https://www.youtube.com/watch?v=xxx

# Process an entire channel
youtuber2skill run https://www.youtube.com/@ChannelName

# Process a playlist
youtuber2skill run "https://www.youtube.com/playlist?list=PLxxxxx"

# Limit number of videos
youtuber2skill run https://www.youtube.com/@ChannelName --max-videos 20
```

## Configuration

Edit `config.yaml` to customize:

```yaml
downloader:
  cookies_file: cookies.txt      # Netscape-format cookie file
  quality: 128
  threads: 3                     # Concurrent download threads

transcriber:
  model: medium                  # tiny / base / small / medium / large-v3-turbo
  language: auto                 # auto-detect, or specify zh / en etc.

skillgen:
  model: kimi-k2.5
  temperature: 1.0
  # api_key and base_url loaded from .env file
```

API credentials via `.env` file (gitignored):

```bash
KIMI_API_KEY=your-api-key-here
KIMI_BASE_URL=your-base-url-here
```

## Output Structure

Generated Skills follow the [AgentSkills](https://agentskills.io) standard:

```
skills/{creator-name}/
├── SKILL.md              # Entry point
├── knowledge.md          # Structured knowledge base
├── style.md              # Communication style rules
├── meta.json             # Metadata
└── transcripts/          # Source transcripts
```

## Requirements

- Python 3.10+
- ffmpeg (`brew install ffmpeg` on macOS)
- whisper.cpp model files (auto-downloaded by pywhispercpp)

## License

MIT
