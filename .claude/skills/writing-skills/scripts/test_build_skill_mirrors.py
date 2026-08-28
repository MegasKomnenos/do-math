# -*- coding: utf-8 -*-
"""build_skill_mirrors.py 테스트.

실행: python .claude/skills/writing-skills/scripts/test_build_skill_mirrors.py
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import build_skill_mirrors as bsm


class TestTargetConfiguration(unittest.TestCase):
    def test_agents_is_the_only_mirror_target(self):
        self.assertEqual(bsm.DEFAULT_TARGETS, [".agents"])


class TestSubstitutions(unittest.TestCase):
    def test_keep_protects_from_later_rules(self):
        subs = [
            {"keep": "~/.claude/plugins"},
            {"from": ".claude/", "to": ".agents/"},
        ]
        text = "경로 ~/.claude/plugins/cache 와 .claude/skills/x"
        self.assertEqual(
            bsm.apply_substitutions(text, subs),
            "경로 ~/.claude/plugins/cache 와 .agents/skills/x",
        )

    def test_ordered_application(self):
        subs = [
            {"from": "`.claude/settings.json`", "to": "`.agents/hooks.json`"},
            {"from": ".claude/", "to": ".agents/"},
        ]
        text = "`.claude/settings.json` 및 .claude/skills/"
        self.assertEqual(
            bsm.apply_substitutions(text, subs),
            "`.agents/hooks.json` 및 .agents/skills/",
        )


class TestFrontmatterMove(unittest.TestCase):
    MOVES = [
        {"key": "argument-hint", "label": "호출 인자"},
        {"key": "effort", "label": "권장 추론 수준"},
    ]

    def test_moves_keys_to_body_in_order(self):
        text = (
            "---\nname: x\ndescription: d\n"
            "argument-hint: \"[a]\"\neffort: max\n---\n\n# 제목\n"
        )
        expected = (
            "---\nname: x\ndescription: d\n---\n"
            "호출 인자: \"[a]\"\n권장 추론 수준: max\n\n# 제목\n"
        )
        self.assertEqual(bsm.move_frontmatter_keys(text, self.MOVES), expected)

    def test_no_target_keys_is_identity(self):
        text = "---\nname: x\ndescription: d\n---\n\n# 제목\n"
        self.assertEqual(bsm.move_frontmatter_keys(text, self.MOVES), text)

    def test_no_frontmatter_is_identity(self):
        text = "# 제목\nargument-hint: 아님\n"
        self.assertEqual(bsm.move_frontmatter_keys(text, self.MOVES), text)


class TestTransform(unittest.TestCase):
    RULES = {
        "substitutions": [{"from": "CLAUDE.md", "to": "AGENTS.md"}],
        "frontmatter_move": [{"key": "argument-hint", "label": "호출 인자"}],
        "verbatim": ["*/원본_대조.md"],
    }

    def test_verbatim_bypasses_all(self):
        raw = "CLAUDE.md 그대로".encode("utf-8")
        self.assertEqual(bsm.transform("x/references/원본_대조.md", raw, self.RULES), raw)

    def test_frontmatter_move_only_for_skill_md(self):
        raw = "---\nname: x\nargument-hint: h\n---\n본문\n".encode("utf-8")
        out_skill = bsm.transform("a/SKILL.md", raw, self.RULES).decode("utf-8")
        out_other = bsm.transform("a/other.md", raw, self.RULES).decode("utf-8")
        self.assertIn("호출 인자: h", out_skill)
        self.assertNotIn("argument-hint", out_skill)
        self.assertIn("argument-hint: h", out_other)

    def test_binary_passthrough(self):
        raw = b"\xff\xfe\x00\x01"
        self.assertEqual(bsm.transform("a/b.bin", raw, self.RULES), raw)


class TestBuildEndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.orig_root = bsm.ROOT
        bsm.ROOT = self.tmp
        self.base = self.tmp / ".claude" / "skills"
        (self.base / "alpha").mkdir(parents=True)
        (self.base / "alpha" / "SKILL.md").write_text(
            "---\nname: alpha\nargument-hint: h\n---\n\nCLAUDE.md 참조와 .claude/skills/alpha 경로\n",
            encoding="utf-8",
        )
        (self.base / "alpha" / "__pycache__").mkdir()
        (self.base / "alpha" / "__pycache__" / "junk.pyc").write_bytes(b"x")
        self.diff = self.tmp / ".agents" / "diff"
        self.diff.mkdir(parents=True)
        (self.diff / "_rules.json").write_text(json.dumps({
            "substitutions": [
                {"from": ".claude/", "to": ".agents/"},
                {"from": "CLAUDE.md", "to": "AGENTS.md"},
            ],
            "frontmatter_move": [{"key": "argument-hint", "label": "호출 인자"}],
            "verbatim": [],
        }, ensure_ascii=False), encoding="utf-8")
        self.out = self.tmp / ".agents" / "skills"

    def tearDown(self):
        bsm.ROOT = self.orig_root
        shutil.rmtree(self.tmp, ignore_errors=True)

    def build(self, check=False, bless=False):
        return bsm.build_target(".agents", check=check, bless=bless)

    def test_generates_transformed_tree_and_check_passes(self):
        ok, _ = self.build()
        self.assertTrue(ok)
        out = (self.out / "alpha" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("AGENTS.md 참조와 .agents/skills/alpha 경로", out)
        self.assertIn("호출 인자: h", out)
        self.assertFalse((self.out / "alpha" / "__pycache__").exists())
        ok, msgs = self.build(check=True)
        self.assertTrue(ok, msgs)

    def test_overlay_wins_and_orphan_removed(self):
        (self.out / "alpha").mkdir(parents=True)
        (self.out / "alpha" / "stale.md").write_text("잔존물", encoding="utf-8")
        (self.diff / "alpha").mkdir()
        (self.diff / "alpha" / "SKILL.md").write_text("오버레이 전문\n", encoding="utf-8")
        ok, _ = self.build()
        self.assertTrue(ok)
        self.assertEqual(
            (self.out / "alpha" / "SKILL.md").read_text(encoding="utf-8"), "오버레이 전문\n")
        self.assertFalse((self.out / "alpha" / "stale.md").exists())
        manifest = json.loads((self.diff / "_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("alpha/SKILL.md", manifest["overlays"])

    def test_additive_overlay_without_base(self):
        (self.diff / "alpha").mkdir()
        (self.diff / "alpha" / "extra.md").write_text("추가 문서\n", encoding="utf-8")
        ok, _ = self.build()
        self.assertTrue(ok)
        self.assertEqual(
            (self.out / "alpha" / "extra.md").read_text(encoding="utf-8"), "추가 문서\n")

    def test_stale_overlay_detected_and_blessed(self):
        (self.diff / "alpha").mkdir()
        (self.diff / "alpha" / "SKILL.md").write_text("오버레이\n", encoding="utf-8")
        ok, _ = self.build()
        self.assertTrue(ok)
        (self.base / "alpha" / "SKILL.md").write_text("정본 개정\n", encoding="utf-8")
        ok, msgs = self.build()
        self.assertFalse(ok)
        self.assertTrue(any("낡음 의심" in m for m in msgs))
        ok, msgs = self.build(bless=True)
        self.assertTrue(ok, msgs)
        ok, msgs = self.build()
        self.assertTrue(ok, msgs)

    def test_check_detects_drift(self):
        self.build()
        (self.out / "alpha" / "SKILL.md").write_text("수기 오염\n", encoding="utf-8")
        ok, msgs = self.build(check=True)
        self.assertFalse(ok)
        self.assertTrue(any("내용 불일치" in m for m in msgs))

    def test_check_mode_writes_nothing(self):
        (self.diff / "alpha").mkdir()
        (self.diff / "alpha" / "SKILL.md").write_text("오버레이\n", encoding="utf-8")
        self.build(check=True)
        self.assertFalse(self.out.exists())
        self.assertFalse((self.diff / "_manifest.json").exists())

    def test_check_fails_on_unregistered_overlay(self):
        self.build()
        (self.diff / "alpha").mkdir()
        (self.diff / "alpha" / "SKILL.md").write_text(
            (self.out / "alpha" / "SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")
        ok, msgs = self.build(check=True)
        self.assertFalse(ok)
        self.assertTrue(any("미등록" in m for m in msgs))
        self.build()
        ok, msgs = self.build(check=True)
        self.assertTrue(ok, msgs)

    def test_check_fails_on_deleted_overlay_manifest_entry(self):
        ok, _ = self.build()
        self.assertTrue(ok)
        (self.diff / "alpha").mkdir()
        overlay = self.diff / "alpha" / "SKILL.md"
        overlay.write_text(
            (self.out / "alpha" / "SKILL.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        ok, _ = self.build()
        self.assertTrue(ok)
        overlay.unlink()
        manifest_path = self.diff / "_manifest.json"
        manifest_before = manifest_path.read_text(encoding="utf-8")
        ok, msgs = self.build(check=True)
        self.assertFalse(ok)
        self.assertTrue(any("기준 해시 잔존: alpha/SKILL.md" in m for m in msgs))
        self.assertEqual(manifest_path.read_text(encoding="utf-8"), manifest_before)
        ok, _ = self.build()
        self.assertTrue(ok)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["overlays"], {})

    def test_base_deletion_propagates_and_manifest_prunes(self):
        (self.diff / "alpha").mkdir()
        (self.diff / "alpha" / "SKILL.md").write_text("오버레이\n", encoding="utf-8")
        self.build()
        (self.diff / "alpha" / "SKILL.md").unlink()
        (self.base / "alpha" / "SKILL.md").unlink()
        ok, _ = self.build()
        self.assertTrue(ok)
        self.assertFalse((self.out / "alpha").exists())
        manifest = json.loads((self.diff / "_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["overlays"], {})

    def test_nul_in_source_rejected(self):
        (self.base / "alpha" / "SKILL.md").write_bytes("본문\x00오염".encode("utf-8"))
        with self.assertRaises(SystemExit):
            self.build()

    def test_bom_source_transforms_fully(self):
        (self.base / "alpha" / "SKILL.md").write_bytes(
            "﻿---\nname: alpha\nargument-hint: h\n---\n\nCLAUDE.md\n".encode("utf-8"))
        ok, _ = self.build()
        self.assertTrue(ok)
        out = (self.out / "alpha" / "SKILL.md").read_bytes().decode("utf-8")
        self.assertNotIn("﻿", out)
        self.assertIn("호출 인자: h", out)
        self.assertIn("AGENTS.md", out)


if __name__ == "__main__":
    unittest.main()
