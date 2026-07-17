---
name: tiktok-caption-template
description: >
  A Remotion project template that produces TikTok-style bilingual caption videos
  (1080x1920 vertical, 60fps). Two caption modes: (1) Intro — English word-by-word
  highlighting with green active word + white/black-outline upcoming words, large
  bold font, positioned in lower-third; (2) Phrase — bilingual capsules (Spanish
  yellow + black stroke on white pill, English black on white pill) with spring
  entrance animation. Use when the user wants to: make a TikTok/Reels/Shorts
  captioned video, 生成短视频字幕, 做一个双语字幕视频, create word-by-word
  karaoke captions, 双语圆角胶囊字幕, or asks to "套用字幕模板".
---

# tiktok-caption-template — Remotion TikTok 双语字幕模板

一套基于 Remotion 的 TikTok 竖屏视频字幕模板，两种字幕样式可复用：
- **引子段（Intro）**：英文逐词高亮，当前词绿色 + 放大，其余白色黑描边，大号粗体
- **短语段（Phrase）**：双语圆角胶囊，西语黄色+黑描边 / 英语黑色，白色圆角背景，弹簧入场动画

## 前置条件

- **Node.js**（v22+）— 当前机器路径: `E:\Software\Manyfy\remotion-runner\bin\node.exe`
- **Remotion CLI** — 通过 `npm install` 安装在项目 `node_modules` 中
- **FFmpeg** — 用于提取验证帧和音频处理: `C:\Users\admin\.manify\bin\ffmpeg.exe`
- **代理** — `http://127.0.0.1:7897`（如果需要下载 Chrome Headless Shell）
- **字体** — TheBoldFont (`public/theboldfont.ttf`)，粗体 sans-serif，适合大字字幕

## 模板结构

```
my-tiktok-video/
├── src/
│   ├── Root.tsx                    # Remotion Composition 配置 (1080x1920, 60fps)
│   ├── load-font.ts                # TheBoldFont 字体加载
│   └── CaptionedVideo/
│       ├── index.tsx               # 主组件：分页逻辑 + Sequence 调度
│       ├── IntroPage.tsx           # 引子段字幕组件（逐词高亮）
│       └── BilingualPage.tsx       # 短语段字幕组件（双语圆角胶囊）
├── public/
│   ├── theboldfont.ttf             # 字体文件
│   └── <video>.mp4 + <subtitles>.json   # 源视频和字幕 JSON
└── package.json
```

## 核心组件说明

### 1. IntroPage.tsx — 逐词高亮引子字幕

**样式参数（可调）：**

| 参数 | 当前值 | 说明 |
|------|--------|------|
| `top` | `700` | 字幕垂直位置（1920高度中）。700 ≈ 画面 60% 处 |
| `FONT_SIZE` | `78` | 固定字号，不使用 fitText 自适应缩小 |
| `HIGHLIGHT_COLOR` | `#39E508` | 当前词高亮色（亮绿色） |
| `WebkitTextStroke` | `6px black` | 黑色描边宽度 |
| `paintOrder` | `stroke` | 描边在填充下方（避免描边盖住字） |
| `scale(active)` | `1.12` | 当前词放大倍率 |
| `maxWidth` | `width * 0.92` | 文字最大宽度（92%画面宽） |
| `gap` | `0.2em` | 词间距 |
| `lineHeight` | `1.15` | 行高（多行时） |

**Props 接口：**
```tsx
{
  tokens: Array<{ text: string; fromMs: number; toMs: number }>;
  pageStartMs: number;  // 该页起始时间(ms)，用于计算相对时间
}
```

**高亮逻辑：**
- 每帧计算 `timeInMs = (frame / fps) * 1000`
- 对每个 token 计算 `active = (t.fromMs - pageStartMs) <= timeInMs && (t.toMs - pageStartMs) > timeInMs`
- active token 显示绿色 + scale(1.12)，其余白色

### 2. BilingualPage.tsx — 双语圆角胶囊字幕

**样式参数（可调）：**

| 参数 | 当前值 | 说明 |
|------|--------|------|
| `top` | `650` | 胶囊垂直位置 |
| `borderRadius` | `80` | 圆角半径（胶囊形） |
| `padding` | `20px 56px` | 胶囊内边距 |
| `boxShadow` | `0 6px 20px rgba(0,0,0,0.35)` | 阴影 |
| 西语 `fontSize` | `72` | 西语字号 |
| 西语 `color` | `#FFD700` | 西语颜色（金色） |
| 西语 `WebkitTextStroke` | `3px black` | 西语描边 |
| 英语 `fontSize` | `60` | 英语字号 |
| 英语 `color` | `#000000` | 英语颜色（黑色） |
| `gap` | `16` | 两行间距 |
| spring `damping` | `200` | 入场弹性 |
| spring `durationInFrames` | `5` | 入场持续帧数 |

**Props 接口：**
```tsx
{
  spanish: string;
  english: string;
}
```

### 3. index.tsx — 主组件调度逻辑

**关键配置项：**

```tsx
const INTRO_END_FRAME = 695;  // 引子结束帧 (11.58s × 60fps)
const WORDS_PER_PAGE = 3;      // 引子段每页显示词数
```

**分页逻辑：**
1. 从字幕 JSON 加载 `Caption[]`，过滤 `endMs <= 11600` 的词作为引子字幕
2. `buildIntroPages()` 按每 `WORDS_PER_PAGE` 个词分组，生成 `{ tokens, startMs, endMs }` 页
3. 每页用 `<Sequence>` 包裹，`from` = 页起始帧，`durationInFrames` = 到下一页起始帧
4. 短语段用 `PHRASE_DATA` 数组手动定义 `{ startFrame, durationFrames, spanish, english }`

**如何替换为你自己的内容：**

1. **替换视频和字幕**：
   - 把你的视频放到 `public/` 下，更新 `Root.tsx` 中的 `src`
   - 把 Whisper 转录的 JSON 放到 `public/` 下（格式：`Caption[]`，每个 caption 有 `tokens`）
   - 更新 `index.tsx` 中的 `subtitlesFile` 路径

2. **调整引子/短语分界点**：
   - 修改 `INTRO_END_FRAME`（= 秒数 × 60）

3. **自定义短语数据**：
   - 修改 `PHRASE_DATA` 数组，每项 `{ startFrame, durationFrames, spanish, english }`

4. **调整字幕位置/大小**：
   - 引子：修改 `IntroPage.tsx` 的 `top`、`FONT_SIZE`、`HIGHLIGHT_COLOR` 等
   - 短语：修改 `BilingualPage.tsx` 的 `top`、`borderRadius`、颜色等

## 字幕 JSON 格式

使用 `video-transcribe` skill 或 `@remotion/install-whisper-cpp` 生成，格式为 `Caption[]`：

```json
[
  {
    "text": "Hi!",
    "startMs": 0,
    "endMs": 440,
    "tokens": [
      { "text": "Hi!", "fromMs": 0, "toMs": 440 }
    ]
  },
  ...
]
```

- 每个 caption 代表一个词（word-level timestamps）
- `tokens` 数组包含该词的时间戳
- 引子段使用 tokens 实现逐词高亮
- 短语段不需要 tokens（直接用 `PHRASE_DATA` 手动定义）

## 渲染命令

```bash
cd /d C:\Users\admin\.manify\workspace\my-tiktok-video
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897
set PATH=E:\Software\Manyfy\remotion-runner\bin;%PATH%
node.exe node_modules\@remotion\cli\remotion-cli.js render CaptionedVideo <输出路径> --codec=h264 --crf=18 --concurrency=2 --log=info
```

**注意：** 2877帧渲染约需 7-10 分钟，会超过 `run_terminal` 的 5 分钟超时。
用后台批处理方式启动：
1. 写一个 `.bat` 文件包含上述命令
2. 用 `Start-Process -WindowStyle Hidden` 启动
3. 在 `.bat` 中用 `echo RENDER_DONE >> status.txt` 标记完成
4. 轮询检查 status.txt

## 验证帧提取

渲染完成后，用 ffmpeg 提取关键帧验证字幕效果：

```bash
ffmpeg -i <output.mp4> -ss <秒> -frames:v 1 -update 1 -y <frame.png>
```

建议提取引子段（0-11s）的 3s/5s/8s/10s 帧和短语段的 13s/20s 帧分别验证。

## 参数调整速查

| 想要的效果 | 修改文件 | 参数 |
|-----------|---------|------|
| 引子字幕上移/下移 | IntroPage.tsx | `top`（减小=上移，增大=下移） |
| 引子字幕变大/变小 | IntroPage.tsx | `FONT_SIZE` |
| 引子高亮色 | IntroPage.tsx | `HIGHLIGHT_COLOR` |
| 引子描边粗细 | IntroPage.tsx | `WebkitTextStroke` |
| 引子每页词数 | index.tsx | `WORDS_PER_PAGE` |
| 短语字幕位置 | BilingualPage.tsx | `top` |
| 短语胶囊圆角 | BilingualPage.tsx | `borderRadius` |
| 西语颜色 | BilingualPage.tsx | `spanishStyle.color` |
| 短语字号 | BilingualPage.tsx | `spanishStyle.fontSize` / `englishStyle.fontSize` |
| 视频尺寸/帧率 | Root.tsx | `width` / `height` / `fps` / `durationInFrames` |
| 引子/短语分界 | index.tsx | `INTRO_END_FRAME` |
