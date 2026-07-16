#!/usr/bin/env bash
# ai-gzh-platform 一键安装脚本
# 1. 装 Pillow / requests（python 依赖）
# 2. 装 lark-cli（飞书 CLI，需 node 18+）
# 3. clone guizang-material-illustration + guizang-social-card-skill（配图依赖）
# 4. 引导跑 init_config.py（生成 config.json）
#
# 用法：
#   bash install.sh              # 完整安装 + 引导
#   bash install.sh --skip-init   # 跳过 init_config 引导
#   bash install.sh --skip-guizang  # 跳过归藏系列 skill 克隆

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_SKILL_DIR="${HOME}/.hermes/skills"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()   { echo -e "${BLUE}▶${NC} $*"; }
ok()    { echo -e "${GREEN}✅${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠️ ${NC} $*"; }
fail()  { echo -e "${RED}❌${NC} $*"; }

SKIP_INIT=false
SKIP_GUIZANG=false
for arg in "$@"; do
  case $arg in
    --skip-init)     SKIP_INIT=true ;;
    --skip-guizang)  SKIP_GUIZANG=true ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0 ;;
  esac
done

echo "╔══════════════════════════════════════════╗"
echo "║  AI公众号内容生产平台 · 一键安装         ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# === 1. Python 依赖 ===
log "[1/5] 安装 Python 依赖 (Pillow, requests)"
PIP_CMD="python3 -m pip"
if ! command -v pip3 >/dev/null 2>&1; then
  warn "pip3 不在 PATH，用 python3 -m pip"
fi
# PEP 668 兼容：检测是否在 venv
IN_VENV=false
if [[ -n "${VIRTUAL_ENV:-}" ]] || python3 -c "import sys; sys.exit(0 if hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix else 1)" 2>/dev/null; then
  IN_VENV=true
fi
if [[ "$IN_VENV" != "true" ]]; then
  warn "当前不在 venv 中。如果遇到 PEP 668 错误，请先激活 venv 或用 uv 装："
  echo "    uv pip install --system Pillow requests"
fi
$PIP_CMD install --quiet Pillow requests 2>&1 | tail -5 || {
  warn "Pillow/requests 安装失败，尝试 user 模式"
  $PIP_CMD install --user --quiet Pillow requests
}
ok "Pillow / requests 已就绪"

# === 2. lark-cli ===
log "[2/5] 安装 lark-cli (Node CLI for 飞书)"
if command -v lark-cli >/dev/null 2>&1; then
  ok "lark-cli 已存在: $(lark-cli --version 2>&1 | head -1)"
else
  if command -v npm >/dev/null 2>&1; then
    log "  全局安装 lark-cli（首次约 30s）..."
    npm install -g lark-cli 2>&1 | tail -3
    ok "lark-cli 已安装"
  else
    fail "未检测到 npm。请先装 Node 18+ (https://nodejs.org)"
    exit 1
  fi
fi

# === 3. 归藏材质插画 skill ===
if [[ "$SKIP_GUIZANG" != "true" ]]; then
  log "[3/5] 克隆归藏系列 skill (材质插画 + 社交卡)"

  if [[ -d "$HERMES_SKILL_DIR/guizang-material-illustration" ]]; then
    ok "guizang-material-illustration 已存在"
  else
    log "  git clone guizang-material-illustration..."
    git clone --depth 1 https://github.com/op7418/guizang-material-illustration.git \
      "$HERMES_SKILL_DIR/guizang-material-illustration" 2>&1 | tail -3
    ok "guizang-material-illustration 已克隆"
  fi

  if [[ -d "$HERMES_SKILL_DIR/guizang-social-card-skill" ]]; then
    ok "guizang-social-card-skill 已存在"
  else
    log "  git clone guizang-social-card-skill..."
    git clone --depth 1 https://github.com/op7418/guizang-social-card-skill.git \
      "$HERMES_SKILL_DIR/guizang-social-card-skill" 2>&1 | tail -3
    ok "guizang-social-card-skill 已克隆"
  fi
else
  log "[3/5] 跳过归藏系列 skill (--skip-guizang)"
fi

# === 4. config.json 模板准备 ===
log "[4/5] 准备 config.json"
if [[ -f "$SKILL_DIR/config.json" ]]; then
  ok "config.json 已存在（保留）"
else
  if [[ -f "$SKILL_DIR/config.example.json" ]]; then
    cp "$SKILL_DIR/config.example.json" "$SKILL_DIR/config.json"
    ok "已从 config.example.json 复制"
    warn "请编辑 config.json 填入飞书 token / 中转 endpoint / 品牌名"
    warn "或运行: python3 $SKILL_DIR/scripts/init_config.py"
  else
    fail "config.example.json 不存在！"
    exit 1
  fi
fi

# === 5. 引导 init_config ===
if [[ "$SKIP_INIT" != "true" ]]; then
  echo ""
  log "[5/5] 交互式配置向导"
  echo ""
  read -r -p "立即运行 init_config.py 交互式填写? (y/N): " ans
  if [[ "$ans" =~ ^[Yy]$ ]]; then
    python3 "$SKILL_DIR/scripts/init_config.py" || warn "init_config 退出，请手动再跑"
  else
    warn "跳过。请手动跑: python3 $SKILL_DIR/scripts/init_config.py"
  fi
else
  log "[5/5] 跳过 init_config 引导 (--skip-init)"
fi

# === 收尾 ===
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║              安装完成 ✅                  ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "下一步："
echo "  1. 跑门禁:  python3 $SKILL_DIR/scripts/preflight.py"
echo "  2. 写作:    读取 references/ 下对应风格的写作指引"
echo "  3. 配图:    python3 $SKILL_DIR/scripts/generate_image.py --prompt '...' --output img.png"
echo "  4. 出 HTML: python3 $SKILL_DIR/scripts/build_html.py --article article.md --imgs-dir imgs/"
echo "  5. 验证:    python3 $SKILL_DIR/scripts/postflight.py --output-dir output/xxx"
echo ""
