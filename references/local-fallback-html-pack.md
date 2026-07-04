# Local fallback: real images + WeChat HTML pack

Use this when the user asks for images/HTML, but `image_api` is disabled or the configured image endpoint fails verification. Do not stop at a prose explanation. Produce real files.

## Trigger

- User asks for `生成图片`, `HTML`, `微信粘贴版`, `图文包`.
- `image_api.enabled=false`, config is missing, or the image API returns non-2xx during the required verify-before-enable check.

## Default fallback

Generate deterministic `baoyu-notion` style assets locally with Python + Pillow:

1. Create an output directory, e.g. `~/wechat_articles/<slug>-output/`.
2. Generate at least:
   - `imgs/cover.png` — 1792×768 horizontal cover.
   - `imgs/infographic-3-lines.png` — vertical core-structure information graphic.
   - `imgs/infographic-4-questions.png` — vertical checklist / decision graphic.
3. Use installed CJK fonts such as `Noto Sans CJK SC` / `NotoSansCJK*.ttc` so Chinese renders correctly.
4. Build a WeChat-compatible HTML file with inline CSS and base64-embedded PNG images. This avoids external image URLs and makes the HTML self-contained.
5. Package the HTML and `imgs/` directory with Python `zipfile` if the system `zip` binary is unavailable.
6. Deliver both the `.html` and `.zip` with `MEDIA:` paths.

## Visual QA before delivery

Run visual inspection on every generated image before final reply:

- Chinese text is clear and readable on mobile.
- No tofu boxes, gibberish, truncated text, or overlapping labels.
- The image follows the selected style, usually white-background Notion knowledge-card for the default config.
- Any unusual wording is checked against the article source before calling it an error.

## User-facing wording

If the image API failed verification, say it directly and briefly, then report the fallback:

> 我实测图片 API 返回 401，所以没有假装成功；已改用本地生成 baoyu-notion 风格知识卡和信息图，并完成视觉检查。

Do not expose tokens or key values.

## Quality bar

The fallback is acceptable only if it still produces real files, not placeholders:

- HTML exists and contains all article body + CTA.
- HTML has embedded images or valid local images included in the package.
- At least one cover and two body images exist.
- Final response includes `MEDIA:` links to the ZIP, HTML, and optionally preview images.
