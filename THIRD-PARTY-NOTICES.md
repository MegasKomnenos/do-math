# Third-party notices

The project as a whole is licensed under the Mozilla Public License 2.0 (see [LICENSE](LICENSE)). The directories below are adapted from third-party projects and remain under their original licenses. Each directory contains the original license text. The Codex copies of these directories under `.agents/skills/` are generated from them and carry the same licenses.

| Directory | Upstream | License |
|---|---|---|
| `.claude/skills/skill-creator/` | `skill-creator` plugin in [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Apache License 2.0 ([LICENSE.txt](.claude/skills/skill-creator/LICENSE.txt)) |
| `.claude/skills/writing-skills/` | `writing-skills` skill in [obra/superpowers](https://github.com/obra/superpowers) 6.1.0, Copyright (c) 2025 Jesse Vincent | MIT ([LICENSE](.claude/skills/writing-skills/LICENSE)) |
| `.claude/skills/grilling/` | [mattpocock/skills](https://github.com/mattpocock/skills), Copyright (c) 2026 Matt Pocock | MIT ([LICENSE](.claude/skills/grilling/LICENSE)) |
| `.claude/skills/grill-me/` | [mattpocock/skills](https://github.com/mattpocock/skills), Copyright (c) 2026 Matt Pocock | MIT ([LICENSE](.claude/skills/grill-me/LICENSE)) |

## Changes

All files in these directories have been modified. Most were translated into Korean or rewritten, and all were adapted to this project's conventions: its writing rules, its commit and memory procedure, and its model selection rules. The skill-creator and writing-skills directories each keep a record of the adaptation, comparing the original with the local version line by line, in `references/원본_대조.md`.
