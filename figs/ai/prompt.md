Use your image_gen tool to create TWO images and save them as PNG files in the current working directory (D:\desk\llm\ch4\figs\ai). Do not write code to draw them; use real image generation.

Shared style contract (apply to both): textbook figure for a Chinese university textbook on LLM computing systems, Nature-journal schematic style. Pure white background, flat vector look, thin dark-grey (#333) outlines, pale grey fills for ordinary components, exactly ONE accent colour (muted teal #2A7F82) for the highlighted element, red only for a bottleneck. No gradients, no 3D, no drop shadows, no glow, no people, no logos, no brand names. Text must be minimal, large, perfectly legible Simplified Chinese in a plain sans-serif (黑体); if unsure about a character, use fewer words. Landscape 3:2.

Image 1 -> file name request_journey.png
Title-free schematic: "一次大模型请求的旅程". Left to right, five stations connected by arrows: 用户请求 -> 应用编排 -> 推理引擎 -> 计算芯片与显存 -> 生成回答. Under 计算芯片与显存 draw a small GPU chip icon next to a stacked memory (HBM) icon, with a thin arrow labelled 权重与KV缓存 between them. Highlight 推理引擎 in the accent colour.

Image 2 -> file name prefill_decode.png
Schematic comparing two phases. Left panel labelled 预填充 Prefill: a row of 8 input token squares processed in parallel by one wide block (many arrows at once), icon of a busy compute unit. Right panel labelled 解码 Decode: tokens generated one at a time in a loop, each step reading from a memory stack (KV缓存) with a red arrow marking the memory-read bottleneck labelled 访存瓶颈. Accent colour on the newly generated token.

After generating, copy/save the final PNGs into the current directory with exactly those file names, then print their paths and pixel sizes.
