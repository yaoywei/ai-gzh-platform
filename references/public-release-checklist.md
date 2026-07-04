# Public release checklist for ai-gzh-platform

Use when packaging or syncing this skill to GitHub / a public skill registry.

## Non-negotiables

1. **Never publish real `config.json`**
   - Public repo contains `config.example.json` only.
   - Real local `config.json` must be ignored.
   - Verify with `git check-ignore -v config.json`.

2. **Never publish generated article outputs**
   - Ignore `output/`, `imgs/`, and `公众号文章/`.
   - These may contain unpublished drafts, media IDs, Feishu doc IDs, or user-specific material.

3. **First-run gate must remain intact**
   - `config.example.json.setup_status` must be `needs_user_choice`.
   - `first_run_questions.required_before_generation` must be `true`.
   - `image_api.enabled`, `feishu.enabled`, and `wechat_proxy.enabled` default to `false`.
   - A new user must choose HTML style + image style before generation.

4. **Provide an actual setup path, not just instructions**
   - Keep `scripts/init_config.py` in the repo.
   - Smoke-test it in a temp directory so it does not overwrite the operator's real `config.json`.

5. **引导/模板内容不能硬编码作者个人品牌**
   - 新用户 clone 后首次引导看到的所有示例必须用通用占位符：
     - `brand_name` 示例 → `你的品牌名`（不能是实际公众号名）
     - AGENTS.md 命名约定示例 → `品牌名=AI 名`（不能是实际 `大姚=AI 名`）
     - Phase 0 交付汇总表 → `| brand_name | 你的品牌名 | AGENTS.md |`
     - 配图模板变量示例 → `| 你的品牌名 |`（不能是实际品牌名）
   - **只有两处可以保留作者名**：SKILL.md frontmatter 的 `author:` + `LICENSE` 的 Copyright。
   - **坑**：示例写的时候随手用自己的品牌名最自然，但公开仓库里等于给每个新用户看到你的公众号名。
   - 发布前必须全文扫描：`grep -rn '你的实际品牌名' SKILL.md references/ scripts/`

## Verification commands

Run from the skill root:

```bash
python3 - <<'PY'
import json
from pathlib import Path
cfg=json.loads(Path('config.example.json').read_text())
assert cfg['setup_status']=='needs_user_choice'
assert cfg['first_run_questions']['required_before_generation'] is True
assert len(cfg['first_run_questions']['html_template_options']) == 10
assert len(cfg['first_run_questions']['image_style_options']) == 6
assert cfg['image_api']['enabled'] is False
assert cfg['feishu']['enabled'] is False
assert cfg['wechat_proxy']['enabled'] is False
print('template-ok')
PY
python3 -m py_compile scripts/init_config.py scripts/generate_image.py scripts/push_draft.py scripts/compress_images.py
node --check scripts/wx-proxy.js
git check-ignore -v config.json output/ .env imgs/ 公众号文章/
```

Temp-dir smoke test for the first-run wizard:

```bash
tmp=$(mktemp -d)
cp config.example.json "$tmp/"
mkdir -p "$tmp/scripts"
cp scripts/init_config.py "$tmp/scripts/"
cd "$tmp"
printf '测试公众号\nAI提效、企业应用\n运营负责人\n老板\n传统行业老板\n2\n1\nn\nn\nn\n' | python3 scripts/init_config.py >/tmp/ai_gzh_init_test.log
python3 - <<'PY'
import json
from pathlib import Path
c=json.loads(Path('config.json').read_text())
assert c['setup_status']=='configured'
assert c['brand_name']=='测试公众号'
assert c['html_template']['style_name']=='tech-blue'
assert c['image_style']['name']=='baoyu-notion'
assert c['image_api']['enabled'] is False
assert c['feishu']['enabled'] is False
assert c['wechat_proxy']['enabled'] is False
print('init-config-smoke-ok')
PY
```

## GitHub sync note

If normal `git push` is blocked or non-interactive auth fails, use the GitHub Git Data / Contents API fallback from `github-workflows`. Build the tree from `git ls-files` only so ignored private files are not uploaded.
