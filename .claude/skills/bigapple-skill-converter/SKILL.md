---
name: bigapple-skill-converter
description: |
  把现有 Claude skill 整理成 BigApple 可发布的项目 skill。用于校验 skill 目录、复制到当前工作区 .claude/skills、补齐 bigapple.json，并引导用户在 BigApple UI 里完成发布和验收。
---

# BigApple Skill Converter

只处理这条链路：

```text
现有 Claude skill
-> 当前工作区 .claude/skills/<skill-name>/
-> bigapple.json 补齐展示字段
-> 引导用户在 BigApple UI 里点“发布”
```

## 先做什么

先确认用户要发布哪个 skill。

输入至少要明确到下面二选一之一：

- 一个 skill 目录路径
- 当前工作区里一个明确的 skill 名称

不明确就先问，不要猜。

## 校验规则

继续之前先确认：

- 目标是一个目录
- 里面有 `SKILL.md` 或 `skill.md`
- 这是一个正常 Claude skill，而不是随便一个文档目录

不满足时直接停，并清楚告诉用户缺什么。

## 首选脚本

优先使用：

`scripts/prepare-bigapple-skill.sh`

默认行为：

- 复制到 `pwd/.claude/skills/<market-safe-name>/`
- 规范化复制后的 skill markdown 里的 `name`
- 创建或合并 `bigapple.json`
- 保留原 skill 其他资源文件

默认不要覆盖同名目标目录。只有用户明确说要覆盖时，才用：

`BIGAPPLE_SKILL_FORCE_OVERWRITE=1`

## 要补的 BigApple 字段

这个 skill 负责补：

- `presentation.displayName`
- `presentation.intro`
- `presentation.examples`
- `presentation.tags`
- `publish.skillId`

不要替用户填写这些发布归属字段：

- `organization.companies`
- `organization.departments`

这些让用户在 BigApple 发布弹窗里自己填。

## 文案要求

在运行脚本前，先根据源 skill 的 `SKILL.md` 准备好这四个值，再传给脚本：

- `displayName`：4 到 12 个字，直接说明用途
- `intro`：1 到 3 句中文，说人话
- `tags`：3 到 6 个搜索词
- `examples`：2 到 4 条用户真的会说的话，不要带 `@技能名`

不要编造源 skill 没写过的能力。

## 用法

最常用：

```bash
BIGAPPLE_SKILL_DISPLAY_NAME="技能上架助手" \
BIGAPPLE_SKILL_INTRO="把现有 Claude skill 整理成 BigApple 可发布的项目 skill，并引导完成上架验证。" \
BIGAPPLE_SKILL_TAGS="BigApple,skill,上架,市场" \
BIGAPPLE_SKILL_EXAMPLES=$'把这个 Claude skill 变成 BigApple skill\n帮我整理这个 skill 然后去发布' \
bash scripts/prepare-bigapple-skill.sh <source_skill_dir>
```

如果想指定目标目录名：

```bash
bash scripts/prepare-bigapple-skill.sh <source_skill_dir> <target_skill_name>
```

## 产物检查

脚本跑完后，至少确认：

- 目标目录已经在 `pwd/.claude/skills/<name>/`
- 里面有 `SKILL.md` 或 `skill.md`
- 里面有 `bigapple.json`
- `bigapple.json` 的展示字段不是空壳

## UI 引导

文件准备好之后，不要替用户点发布。

只引导用户自己走这条链路：

1. 回到当前工作区的 BigApple 聊天界面
2. 看输入框上方是否出现刚整理好的 skill badge
3. 如果出现，点击 skill 上方的“发布”按钮
4. 在弹窗里自己填写公司/部门，并检查展示名称、标签、自我介绍、召唤示例
5. 发布完成后，去左上角“数字员工(skills)”页面搜索这个 skill
6. 如果搜得到，就说明上架成功

如果用户说没看到 skill badge，先让他确认当前打开的是同一个工作区，再检查目标目录有没有放进 `pwd/.claude/skills/`

## 成功后的最后一步

用户确认已经在“数字员工(skills)”里搜到这个 skill 后，再问一句：

`原来的 Claude skill 还要保留吗？`

如果用户说不要了，只告诉他原路径，让他自己删除。

不要替用户删除原 skill。
