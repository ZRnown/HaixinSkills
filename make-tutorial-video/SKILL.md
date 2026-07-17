# make-tutorial-video — TikTok 教程视频制作 SOP

制作竖屏 TikTok 教程视频：**Demo 效果展示 → 屏幕录像教程 → TTS 解说 → 逐词高亮字幕**。
输出 1080×1920 / 30fps MP4，画面/语音/字幕三者同步。

## 适用场景

- App 操作教程（如 DreamFace / DreamAct）
- 需要先展示效果、再教操作步骤的视频
- 需要 TTS 语音解说 + 逐词高亮字幕

## 前置条件

| 工具 | 路径 / 安装方式 |
|------|-----------------|
| Python 3.12+ | `C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe` |
| FFmpeg | `C:\Users\admin\.manify\bin\ffmpeg.exe` |
| FFprobe | `C:\Users\admin\.manify\bin\ffprobe.exe` |
| faster-whisper | `pip install faster-whisper`（模型 medium, CPU int8） |
| Node.js + npm | 用于 Remotion 渲染 |
| Remotion | `npx remotion` （项目模板见 templates/tiktok_project/） |
| Shell | `cmd /c`（WSL/bash 不可用） |

## 输入素材

| 素材 | 说明 | 示例 |
|------|------|------|
| **效果展示视频** (demo) | 展示最终效果的短视频，循环播放 | `Baby_Mapopopo.mp4` (10.3s) |
| **Demo TTS 音频** (demo_tts) | 效果展示段的解说语音 | `demo_narration_v2.wav` (6.38s) |
| **教程 TTS 音频** (tutorial_tts) | 操作步骤段的解说语音 | `tutorial_narration_v5.wav` (27.6s) |
| **原始屏幕录像** | 手机录屏，包含从主屏幕打开 App 的完整过程 | `7月15日 (3).mp4` (58.2s) |

> **关键**：原始屏幕录像**必须包含从手机主屏幕→点击App图标→App启动**的画面。
> 不要裁掉开头——这是"打开 App"解说词的对应画面。

---

## 完整流程（7 步）

### Step 1: 准备屏幕录像

清理原始录屏：裁掉顶部红条、跳切冗余等待、保持 1080×1920。

**脚本**: `templates/build_screen_recording.py`

关键参数需要根据原始录屏调整：
- `crop=1080:1836:0:70` — 裁掉顶部 70px 红条，再 scale 到 1080×1920
- `trim=0:23` — **保留开头**（主屏幕→点击App→App启动），跳切前段
- `trim=36:47` — 跳切后段（结果展示）
- 用 `split+concat` 拼接两段

```bash
cd /d <workspace>
python templates/build_screen_recording.py
# 输出: <run_dir>/screen_recording_clean.mp4 (34s, 1080x1920, 30fps, 无音频)
```

**验证**：抽取 0s / 3s / 5s 帧确认：
- 0s = 手机主屏幕（能看到 App 图标）
- 3s = App 启动画面或首页
- 5s = App 内部页面

### Step 2: 生成 Base Video（FFmpeg 拼接）

将 demo 视频 + 屏幕录像 + 三路音频合成为 base_video.mp4。

**脚本**: `templates/build_base.py`

结构：
```
Part 1 (0 ~ PART1_DURATION): Demo 视频循环 + "Create with XXX" 文字 + Demo TTS + Demo 原声(0.7音量)
Part 2 (PART1_DURATION ~ END): 屏幕录像播放 + Tutorial TTS (延迟 PART1_DURATION)
```

关键参数：
- `PART1_DURATION = demo_tts_duration + 2.0`（Demo TTS 结束后留 2 秒间隔）
- `TOTAL_DURATION = PART1_DURATION + tutorial_tts_duration + 0.15`
- `DELAY_MS = int(PART1_DURATION * 1000)` — Tutorial TTS 延迟
- 无冻帧（屏幕录像自带 App 启动画面）
- FFmpeg filter_complex: demo 视频缩放+裁切+drawtext → concat → 三路音频 amix

```bash
python templates/build_base.py
# 输出: <run_dir>/base_video.mp4
# 同时写 video_duration.txt 记录总帧数
```

### Step 3: 用 Whisper 转录 TTS（真实词级时间戳）

**绝对不要用字符数估算时间戳**——TTS 语速不均匀，句间有停顿，估算会导致字幕逐词漂移，后半段偏差可达 4-5 秒。

对 **两段 TTS** 分别做 faster-whisper 转录：

```bash
# 转录 Demo TTS
python templates/transcribe_tts.py --audio demo_narration_v2.wav --out demo_tts_transcript.json

# 转录 Tutorial TTS
python templates/transcribe_tts.py --audio tutorial_narration_v5.wav --out tts_transcript.json
```

模型配置：
- `WhisperModel("medium", device="cpu", compute_type="int8")`
- `language="en", beam_size=5, word_timestamps=True`
- 输出 JSON: `{language, duration, words: [{word, start, end, probability}]}`

**验证**：检查转录词数和内容是否与 TTS 实际说的一致。
> 注意：Whisper 可能把专有名词听错（如 "Mapopopo" → "Mappapopo"），需人工校对修正 transcript JSON 中的 word 字段（时间戳不变）。

### Step 4: 生成 subtitles.json

将两段真实转录合并为 Remotion 格式的 subtitles.json。

**脚本**: `templates/build_subtitles.py`

- Part 1 (Demo TTS): 真实时间戳，offset = 0
- Part 2 (Tutorial TTS): 真实时间戳，offset = `PART1_DURATION_MS`（如 8380）
- 每个词生成一个 caption: `{text, startMs, endMs, tokens: [{text, fromMs, toMs}]}`

```bash
python templates/build_subtitles.py
# 输出: tiktok_project/public/subtitles.json
```

### Step 5: 配置 Remotion 项目

项目模板: `templates/tiktok_project/`（完整 Remotion 项目，含 CaptionedVideo 组件）

需要修改的文件：

1. **`src/Root.tsx`** — 设置 `durationInFrames` 为 Step 2 输出的总帧数：
```tsx
durationInFrames={1085}  // = int(TOTAL_DURATION * 30)
```

2. **`public/base_video.mp4`** — 复制 Step 2 的输出到这里

3. **`public/subtitles.json`** — Step 4 的输出

4. **`public/theboldfont.ttf`** — 字体文件（已在模板中）

### Step 6: 渲染 Remotion 视频

```bash
cd /d <run_dir>/tiktok_project
npx remotion render CaptionedVideo out/DreamAct_TikTok_Tutorial.mp4
# 耗时约 10 分钟，timeout 设 600 秒
```

### Step 7: 验证 + 交付

抽取关键时间点帧，用 vision 确认画面与字幕同步：

```bash
# 抽取 Part1/Part2 交界处 + 教程段几个关键点
ffmpeg -y -ss 8.5 -i output.mp4 -frames:v 1 -update 1 frame_8.5s.png
ffmpeg -y -ss 10 -i output.mp4 -frames:v 1 -update 1 frame_10s.png
ffmpeg -y -ss 13 -i output.mp4 -frames:v 1 -update 1 frame_13s.png
```

验证清单：
- [ ] Part1 结束时画面从 Demo 切换到屏幕录像
- [ ] 屏幕录像开头是手机主屏幕（能看到 App 图标）
- [ ] TTS 说"Open the App"时画面显示主屏幕
- [ ] TTS 说"Go to Explore"时画面已进入 App
- [ ] 字幕与 TTS 语音同步（逐词高亮跟随语音节奏）
- [ ] 总时长 / 分辨率 / 帧率正确

```bash
# 复制到最终位置
python -c "import shutil; shutil.copy2(r'.../out/DreamAct_TikTok_Tutorial.mp4', r'<workspace>/DreamAct_TikTok_Tutorial.mp4')"
```

---

## 文件结构

```
<workspace>/
├── HaixinSkills/make-tutorial-video/
│   ├── SKILL.md                          ← 本文件
│   └── templates/
│       ├── build_screen_recording.py     ← Step 1
│       ├── build_base.py                 ← Step 2
│       ├── transcribe_tts.py             ← Step 3
│       ├── build_subtitles.py            ← Step 4
│       └── tiktok_project/               ← Remotion 项目模板
│           ├── package.json
│           ├── src/
│           │   ├── Root.tsx              ← Step 5: 改 durationInFrames
│           │   ├── load-font.ts
│           │   └── CaptionedVideo/
│           │       ├── index.tsx         ← 字幕渲染组件
│           │       └── IntroPage.tsx     ← 逐词高亮组件
│           └── public/
│               ├── theboldfont.ttf
│               ├── base_video.mp4        ← Step 2 输出 (复制到这里)
│               └── subtitles.json        ← Step 4 输出
├── demo_narration_v2.wav                 ← Demo TTS
├── tutorial_narration_v5.wav             ← Tutorial TTS
└── DreamAct_TikTok_Tutorial.mp4          ← 最终输出
```

---

## 踩坑记录

### 1. 字幕与语音不同步
- **原因**：用字符数均匀分配词时间戳，TTS 实际语速不均匀 + 句间停顿 → 后半段漂移 4-5 秒
- **修复**：必须用 faster-whisper 做真实词级时间戳转录

### 2. 开头字幕内容与 TTS 不匹配
- **原因**：Part 1 字幕手写内容（"in a few simple steps"）但 TTS 实际说的是别的（"Watch this, now let me show you..."）
- **修复**：Part 1 也必须用 Whisper 转录 TTS，不能手写

### 3. 教程段开头画面"消失"
- **原因**：`build_screen_recording.py` 用 `trim=3:23` 裁掉了原始录像前 3 秒（主屏幕→点击App→启动）
- **修复**：改为 `trim=0:23`，保留 App 启动过程

### 4. 冻帧产生黑屏
- **原因**：用 `tpad=start=90` 做冻帧，某些 FFmpeg 版本产生黑帧
- **修复**：改用提取首帧→loop 静止视频→concat 拼接；或直接不要冻帧（录像自带启动画面时）

### 5. 3 秒冻帧导致音画不同步
- **原因**：TTS 在 Part1 结束后立即开始说"Open the App"，但画面冻在 App 内部 3 秒不滚动
- **修复**：去掉冻帧，让录像自然播放（主屏幕→启动→进入 App 与 TTS 自然同步）

### 6. Whisper 专有名词听错
- **示例**："Mapopopo" → "Mappapopo", "DreamFace" → "Dreamface"
- **修复**：转录后人工校对 transcript JSON 中的 word 字段（时间戳不变）

### 7. cmd 中文路径编码问题
- **原因**：`copy` 命令在含中文路径下报"语法不正确"
- **修复**：用 Python `shutil.copy2()` 代替 cmd `copy`

### 9. Demo 和 Tutorial 两段 TTS 音色不一致
- **原因**：分别用不同时间、不同参数生成两段 TTS
- **修复**：用 `dream_voice_clone` 克隆 demo 音频音色 → 拿 `clone_id` 后用 `dream_tts_clone` 一次性生成完整旁白 → Whisper 找分界点 → FFmpeg `-t / -ss` 切分

### 10. 克隆音色语速与原旁白不同，导致音画不同步
- **原因**：克隆音色朗读速度可能与原始 TTS 差异很大（本例原始 27.6s，克隆 42.9s，慢了55%），屏幕录像动作时间不变，画面和语音错位
- **修复**：用 FFmpeg `atempo` 加速 tutorial 音频到原始时长（42.93→27.6s，atempo=1.554）。注意 `atempo` 范围 [0.5, 2.0]，超出需链式（如 `atempo=2.0,atempo=1.2`）
- **原因**：`ffmpeg -frames:v 1 output.png` 不加 `-update 1` 会报 pattern invalid
- **修复**：加 `-update 1` 参数

---

## 参数速查

| 参数 | 公式 | 示例值 |
|------|------|--------|
| PART1_DURATION | demo_tts_duration + 2.0 | 8.380s |
| PART2_DURATION | tutorial_tts_duration + 0.15 | 27.775s |
| TOTAL_DURATION | PART1 + PART2 | 36.155s |
| TOTAL_FRAMES | int(TOTAL_DURATION × 30) | 1085 |
| DELAY_MS | int(PART1_DURATION × 1000) | 8380 |
| PART2_OFFSET_MS | 同 DELAY_MS | 8380 |

## FFmpeg filter_complex 速查

```
# 视频流
[0:v] scale+crop+drawtext → trim=PART1 → [demo]
[1:v] format+setpts → trim=PART2 → [screen]
[demo][screen] concat → [outv]

# 音频流
[0:a] aloop + atrim → volume=0.7 → [demo_bg]      # Demo 原声循环, 降音量
[2:a] atrim → volume=1.0 → [demo_tts]               # Demo TTS
[3:a] adelay=DELAY_MS + atrim → volume=1.0 → [tut_tts]  # Tutorial TTS 延迟
[demo_bg][demo_tts][tut_tts] amix=3:normalize=0 → [outa]
```
