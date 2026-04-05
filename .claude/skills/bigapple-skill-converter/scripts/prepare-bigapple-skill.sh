#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: bash scripts/prepare-bigapple-skill.sh <source_skill_dir> [target_skill_name]" >&2
  exit 1
fi

SOURCE_DIR="$1"
TARGET_NAME_INPUT="${2:-}"
WORKSPACE_ROOT="${BIGAPPLE_SKILL_WORKSPACE_ROOT:-$PWD}"
FORCE_OVERWRITE="${BIGAPPLE_SKILL_FORCE_OVERWRITE:-0}"
DISPLAY_NAME_INPUT="${BIGAPPLE_SKILL_DISPLAY_NAME:-}"
INTRO_INPUT="${BIGAPPLE_SKILL_INTRO:-}"
TAGS_INPUT="${BIGAPPLE_SKILL_TAGS:-}"
EXAMPLES_INPUT="${BIGAPPLE_SKILL_EXAMPLES:-}"

python3 - "$SOURCE_DIR" "$TARGET_NAME_INPUT" "$WORKSPACE_ROOT" "$FORCE_OVERWRITE" "$DISPLAY_NAME_INPUT" "$INTRO_INPUT" "$TAGS_INPUT" "$EXAMPLES_INPUT" <<'PY'
import json
import re
import shutil
import sys
from pathlib import Path


SOURCE_DIR = Path(sys.argv[1]).expanduser().resolve()
TARGET_NAME_INPUT = sys.argv[2].strip()
WORKSPACE_ROOT = Path(sys.argv[3]).expanduser().resolve()
FORCE_OVERWRITE_RAW = sys.argv[4].strip().lower()
DISPLAY_NAME_INPUT = sys.argv[5].strip()
INTRO_INPUT = sys.argv[6].strip()
TAGS_INPUT = sys.argv[7]
EXAMPLES_INPUT = sys.argv[8]

FORCE_OVERWRITE = FORCE_OVERWRITE_RAW in {"1", "true", "yes", "y", "on"}
TARGET_SKILLS_ROOT = WORKSPACE_ROOT / ".claude" / "skills"
IGNORED_NAMES = {".DS_Store", "__MACOSX"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def split_tags(value: str) -> list[str]:
    items = re.split(r"[\n,，；;]+", value)
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
      normalized = item.strip()
      if not normalized or normalized in seen:
          continue
      result.append(normalized)
      seen.add(normalized)
    return result


def split_examples(value: str) -> list[str]:
    normalized_value = value.replace("||", "\n")
    result: list[str] = []
    seen: set[str] = set()
    for item in normalized_value.splitlines():
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        result.append(normalized)
        seen.add(normalized)
    return result


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized or "skill"


def derive_display_name(raw_name: str, target_name: str) -> str:
    candidate = raw_name.strip()
    if candidate and candidate.lower() != target_name:
        return candidate
    return target_name.replace("-", " ").strip() or target_name


def find_skill_markdown(directory: Path) -> Path:
    exact = directory / "SKILL.md"
    if exact.exists():
        return exact

    lower = directory / "skill.md"
    if lower.exists():
        return lower

    for entry in directory.iterdir():
        if entry.is_file() and entry.name.lower() == "skill.md":
            return entry

    fail(f"Invalid skill directory: missing SKILL.md in {directory}")


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", content, re.DOTALL)
    if not match:
        return {}, content

    block = match.group(1)
    body = content[match.end():]
    data: dict[str, str] = {}
    lines = block.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if re.match(r"^description:\s*\|", line):
            desc_lines: list[str] = []
            index += 1
            while index < len(lines) and (lines[index].startswith("  ") or lines[index].startswith("\t")):
                desc_lines.append(lines[index].strip())
                index += 1
            data["description"] = "\n".join(desc_lines).strip()
            continue

        match_line = re.match(r"^(name|description):\s*(.*)$", line)
        if match_line:
            data[match_line.group(1)] = match_line.group(2).strip().strip('"').strip("'")
        index += 1

    return data, body


def ensure_frontmatter_name(content: str, target_name: str) -> str:
    match = re.match(r"^---\r?\n(.*?)\r?\n---(\r?\n)?", content, re.DOTALL)
    if not match:
        return f"---\nname: {target_name}\n---\n\n{content.lstrip()}"

    block = match.group(1)
    suffix = match.group(2) or "\n"
    body = content[match.end():]
    lines = block.splitlines()
    updated = False
    new_lines: list[str] = []
    for line in lines:
        if re.match(r"^name:\s*", line):
            new_lines.append(f"name: {target_name}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.insert(0, f"name: {target_name}")

    return f"---\n" + "\n".join(new_lines) + f"\n---{suffix}{body}"


def read_json_if_exists(file_path: Path) -> dict:
    if not file_path.exists():
        return {}
    try:
        with file_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError as exc:
        fail(f"Invalid bigapple.json: {file_path} ({exc})")


def copy_skill_directory(source_dir: Path, target_dir: Path) -> None:
    def ignore(_dir: str, names: list[str]) -> set[str]:
        ignored = {name for name in names if name in IGNORED_NAMES or name.startswith("._")}
        return ignored

    shutil.copytree(source_dir, target_dir, ignore=ignore)


if not SOURCE_DIR.exists() or not SOURCE_DIR.is_dir():
    fail(f"Skill source not found: {SOURCE_DIR}")

source_skill_markdown = find_skill_markdown(SOURCE_DIR)
source_content = source_skill_markdown.read_text(encoding="utf-8")
frontmatter, _body = parse_frontmatter(source_content)

raw_skill_name = frontmatter.get("name", "").strip() or SOURCE_DIR.name
target_name = slugify(TARGET_NAME_INPUT or raw_skill_name)
target_dir = TARGET_SKILLS_ROOT / target_name

if target_dir.exists():
    if not FORCE_OVERWRITE:
        fail(f"Target already exists: {target_dir}\nUse BIGAPPLE_SKILL_FORCE_OVERWRITE=1 to replace it.")
    shutil.rmtree(target_dir)

target_dir.parent.mkdir(parents=True, exist_ok=True)
copy_skill_directory(SOURCE_DIR, target_dir)

copied_skill_markdown = find_skill_markdown(target_dir)
canonical_skill_markdown = target_dir / "SKILL.md"
if copied_skill_markdown.name != "SKILL.md":
    copied_skill_content = copied_skill_markdown.read_text(encoding="utf-8")
    copied_skill_markdown.unlink()
    if canonical_skill_markdown.exists():
        canonical_skill_markdown.unlink()
    canonical_skill_markdown.write_text(copied_skill_content, encoding="utf-8")
else:
    canonical_skill_markdown = copied_skill_markdown

updated_skill_content = ensure_frontmatter_name(canonical_skill_markdown.read_text(encoding="utf-8"), target_name)
canonical_skill_markdown.write_text(updated_skill_content.rstrip() + "\n", encoding="utf-8")
final_skill_markdown = find_skill_markdown(target_dir)

description = frontmatter.get("description", "").strip().replace("\n", " ")
display_name = DISPLAY_NAME_INPUT or derive_display_name(raw_skill_name, target_name)
intro = INTRO_INPUT or description
tags = split_tags(TAGS_INPUT)
examples = split_examples(EXAMPLES_INPUT)

bigapple_json_path = target_dir / "bigapple.json"
existing = read_json_if_exists(bigapple_json_path)
presentation = dict(existing.get("presentation") or {})
organization = dict(existing.get("organization") or {})
publish = dict(existing.get("publish") or {})

if display_name:
    presentation["displayName"] = display_name
elif "displayName" not in presentation:
    presentation["displayName"] = derive_display_name(raw_skill_name, target_name)

if intro:
    presentation["intro"] = intro
elif "intro" not in presentation:
    presentation["intro"] = ""

if tags:
    presentation["tags"] = tags
else:
    presentation.setdefault("tags", [])

if examples:
    presentation["examples"] = examples
else:
    presentation.setdefault("examples", [])

organization.setdefault("companies", [])
organization.setdefault("departments", [])
publish["skillId"] = target_name

next_payload = dict(existing)
next_payload["schemaVersion"] = 1
next_payload["presentation"] = presentation
next_payload["organization"] = organization
next_payload["publish"] = publish
next_payload.setdefault("lineage", existing.get("lineage") if isinstance(existing.get("lineage"), dict) else {})

bigapple_json_path.write_text(json.dumps(next_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("准备成功")
print(f"sourceSkillDir: {SOURCE_DIR}")
print(f"targetSkillDir: {target_dir}")
print(f"skillName: {target_name}")
print(f"skillMarkdown: {final_skill_markdown}")
print(f"bigappleJson: {bigapple_json_path}")
print("next:")
print("1. 回到当前工作区的 BigApple 聊天界面")
print("2. 确认输入框上方出现这个 skill")
print("3. 点击 skill 上方的“发布”按钮")
print("4. 在弹窗里自己填写公司/部门，并检查展示文案")
print("5. 发布后去左上角“数字员工(skills)”页面搜索它")
PY
