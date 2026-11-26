"""Tests of the canon: its names and files, the application of a candidate, the structural index,
the machine checks, the written part of a publication, and the commands that prepare and verify a change.

The expectations follow docs/do-math/lean-canon-design.md and the guides under reference/, not
the present behaviour of the code. Pure functions are tested on hand-written inputs in a temporary
folder. What needs a compiled canon runs on the shared small instance, through a real broker with the
stand-in compiler of tests/canon_lean.py.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import canon_tool
from canon import (Canon, CanonError, add_imports, apply_lean, apply_rearrangement, apply_written,
                   beyond_allowed, build_outcome, candidate_records, check_applied, copy_tree,
                   declaration_text, drop_modules, empty_index, extraction_source, header_scan, history_entry,
                   library_modules, load_change, merge_bibliography, module_file, name_parts, name_path,
                   parse_approach, parse_record, parse_rows, path_name, path_part, read_approaches, read_index,
                   read_record, record_file, replace_span, required_pairs, retire_approaches, sha256_text,
                   split_review, statement_differences, sync_tree, tree_hash, update_index, with_importers,
                   with_review)
from check import Invalid, check_session, prepared_candidate
from lean_broker import Paths, job_record
from runtime_support import read_json, write_json
from support import InstanceCase, earlier_form, module_text, record_text


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')
    return path


def span_of(text, snippet):
    """The span [first line, column, last line, column] of the one occurrence of a snippet, lines from 1."""
    assert text.count(snippet) == 1, snippet
    start = text.index(snippet)

    def position(offset):
        before = text[:offset]
        return [before.count('\n') + 1, offset - (before.rfind('\n') + 1)]

    return position(start) + position(start + len(snippet))


def apply_diff(lines, diff):
    """The lines that a unified diff, as difflib writes it without line ends, makes of the given lines."""
    result, position = [], 0
    rows = diff.split('\n')
    number = 0
    while number < len(rows):
        hunk = re.match(r'@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@', rows[number])
        number += 1
        if not hunk:
            continue
        count = 1 if hunk[2] is None else int(hunk[2])
        begin = int(hunk[1]) - 1 if count else int(hunk[1])
        result += lines[position:begin]
        position = begin
        while number < len(rows) and not rows[number].startswith('@@'):
            row = rows[number]
            number += 1
            if row.startswith('+'):
                result.append(row[1:])
            elif row.startswith('-'):
                assert lines[position] == row[1:], row
                position += 1
            else:
                assert lines[position] == row[1:], row
                result.append(lines[position])
                position += 1
    return result + lines[position:]


def history_diff(text):
    return text.split('```diff\n', 1)[1].rsplit('\n```', 1)[0]


class TempCase(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def moves(self, work):
        """The files that `work` moved into place, each with the sizes of the files sent to the disk before its move.

        What reaches the disk is seen at the system call that sends it there, and a move at the call that makes it."""
        flushed, moved = [], []
        fsync, replace = os.fsync, os.replace

        def flush(descriptor):
            flushed.append(os.fstat(descriptor).st_size)
            return fsync(descriptor)

        def move(temporary, destination):
            moved.append((Path(destination).name, list(flushed)))
            return replace(temporary, destination)

        with patch.object(os, 'fsync', side_effect=flush), patch.object(os, 'replace', side_effect=move):
            work()
        return moved


# --------------------------------------------------------------------------------------- names and paths

class NameTests(TempCase):
    def test_name_parts_splits_a_name_at_its_dots(self):
        self.assertEqual(name_parts('Small.Sub.oddSum_succ'), ['Small', 'Sub', 'oddSum_succ'])
        self.assertEqual(name_parts('root'), ['root'])

    def test_name_parts_keeps_the_dots_of_a_component_between_guillemets(self):
        self.assertEqual(name_parts('Small.«b.c».d'), ['Small', 'b.c', 'd'])
        self.assertEqual(name_parts('«a.b.c»'), ['a.b.c'])

    def test_name_parts_refuses_an_empty_component(self):
        for name in ('', '.root', 'Small.', 'Small..root', 'Small.«».root'):
            with self.subTest(name=name), self.assertRaisesRegex(CanonError, 'not a declaration name'):
                name_parts(name)

    def test_an_ordinary_component_is_its_own_file_name(self):
        for part in ('root', 'oddSum_succ', "x'", 'ℕ_sum', 'Auxiliary', 'console', 'COM10', 'b.c'):
            with self.subTest(part=part):
                self.assertEqual(path_part(part), part)

    def test_a_reserved_windows_device_name_gets_a_trailing_percent(self):
        for part in ('Aux', 'con', 'COM1', 'LPT9', 'aux', 'CON', 'nul', 'Prn', 'com5', 'Lpt1'):
            with self.subTest(part=part):
                self.assertEqual(path_part(part), part + '%')

    def test_forbidden_characters_and_the_percent_sign_become_codes(self):
        expected = {'<': '%3C', '>': '%3E', ':': '%3A', '"': '%22', '/': '%2F', '\\': '%5C', '|': '%7C',
                    '?': '%3F', '*': '%2A', '%': '%25', '\t': '%09', '\x1f': '%1F'}
        for char, code in expected.items():
            with self.subTest(char=char):
                self.assertEqual(path_part('a' + char + 'b'), 'a' + code + 'b')
        self.assertEqual(path_part('a:b%c'), 'a%3Ab%25c')

    def test_a_component_ending_in_a_dot_or_a_space_gets_a_trailing_percent(self):
        self.assertEqual(path_part('v1.'), 'v1.%')
        self.assertEqual(path_part('name '), 'name %')

    def test_name_path_follows_the_name(self):
        self.assertEqual(name_path('Parking.Columns.dq_col'), 'Parking/Columns/dq_col')
        self.assertEqual(name_path('Small.Aux'), 'Small/Aux%')
        self.assertEqual(name_path('COM1.lpt9'), 'COM1%/lpt9%')
        self.assertEqual(name_path('Small.«b.c».d'), 'Small/b.c/d')
        self.assertEqual(name_path('Small.«a/b»'), 'Small/a%2Fb')

    def test_path_name_reads_the_name_back_from_a_path(self):
        self.assertEqual(path_name('Parking/Columns/dq_col'), 'Parking.Columns.dq_col')
        self.assertEqual(path_name('Small/Aux%'), 'Small.Aux')
        self.assertEqual(path_name('COM1%/lpt9%'), 'COM1.lpt9')
        self.assertEqual(path_name('Small/b.c/d'), 'Small.«b.c».d')

    def test_round_trip_of_ordinary_and_encoded_names(self):
        names = ('Small.root', 'Small.Sub.oddSum_succ', "Small.x'", 'Small.ℕ_sum', 'root',
                 'Small.Aux', 'Small.con', 'COM1.LPT9', 'Small.aux.nul',
                 'Small.«b.c».d', 'Small.«v1.»', 'Small.«a:b.c»', 'Small.«50%.x»')
        for name in names:
            with self.subTest(name=name):
                self.assertEqual(path_name(name_path(name)), name)

    def test_round_trip_of_a_quoted_component_that_has_no_dot(self):
        # Lean prints such a component between guillemets, and the name read back from a record path is
        # used as a declaration name: in the pairs an extraction is asked for, and as a key of the index.
        for name in ('Small.«a:b»', 'Small.«50%»', 'Small.«a b»', 'Small.«name »', 'Small.«a/b».c'):
            with self.subTest(name=name):
                self.assertEqual(path_name(name_path(name)), name)

    def test_different_names_have_different_paths(self):
        groups = (('Small.Aux', 'Small.«Aux%»'), ('Small.a.b', 'Small.«a.b»'), ('Small.«a:b»', 'Small.«a%3Ab»'),
                  ('Small.«v.»', 'Small.«v.%»'))
        for names in groups:
            with self.subTest(names=names):
                self.assertEqual(len({name_path(name) for name in names}), len(names))

    def test_record_file(self):
        canon = Canon(self.root)
        self.assertEqual(record_file(canon, 'Small.root'), canon.records / 'Small' / 'root.md')
        self.assertEqual(record_file(canon, 'Small.Aux'), canon.records / 'Small' / 'Aux%.md')
        self.assertEqual(record_file(canon, 'Small.«b.c»'), canon.records / 'Small' / 'b.c.md')

    def test_an_encoded_record_file_can_be_written_and_read(self):
        canon = Canon(self.root)
        for name in ('Small.aux', 'Small.CON', 'Small.«a:b»', 'Small.«what?»', 'Small.«v1.»'):
            with self.subTest(name=name):
                path = write(record_file(canon, name), name)
                self.assertEqual(path.read_text(encoding='utf-8'), name)
                self.assertIn(path.name, os.listdir(path.parent))

    def test_names_that_differ_only_in_case_are_found_as_one_record_file(self):
        # Lean names are case-sensitive and each element has one record (design 4.4); the instance's
        # file system on Windows is not case-sensitive. The runtime keeps the readable paths and
        # refuses a candidate that adds such a name (check_applied reports the group).
        from canon import case_collisions
        self.assertEqual(case_collisions(['Small.Col', 'Small.col', 'Small.other', 'Small.Sub.x', 'Small.sub.X']),
                         [('Small.Col', 'Small.col'), ('Small.Sub.x', 'Small.sub.X')])
        self.assertEqual(case_collisions(['Small.a', 'Small.b']), [])


# --------------------------------------------------------------------------------------- written files

RECORD = '''---
short: odd numbers sum to a square
weight: unit
---
## Description

The sum of the first n odd numbers equals n times n.

## Statement

For every natural number n, the sum is n squared.

## Proof

By induction on n.
'''

APPROACH = '''---
title: Induction on the number of terms
sessions: s1, s2
---
## Idea

Compare the sum for n + 1 with the sum for n.

## Established

Small.oddSum_succ

## Where it stops

The arithmetic identity has not been checked.
'''


class RecordFormatTests(unittest.TestCase):
    def test_a_record_is_parsed_into_header_and_sections(self):
        record = parse_record(RECORD)
        self.assertEqual(record['meta'], {'short': 'odd numbers sum to a square', 'weight': 'unit'})
        self.assertEqual(record['sections'], {
            'Description': 'The sum of the first n odd numbers equals n times n.',
            'Statement': 'For every natural number n, the sum is n squared.',
            'Proof': 'By induction on n.'})

    def test_every_header_key_and_section_in_any_order(self):
        text = ('---\nweight: step\nsource: knuth1997\nproves: Small.root\nshort: another proof\n\n---\n'
                '## Literature\n\nKnuth, section 1.2.\n\n## Proof\n\nDirect.\n\n## Explanation\n\nWhy.\n\n'
                '## Statement\n\nWords.\n\n## Description\n\nWhat it is.\n')
        record = parse_record(text)
        self.assertEqual(record['meta'], {'weight': 'step', 'source': 'knuth1997', 'proves': 'Small.root',
                                          'short': 'another proof'})
        self.assertEqual(set(record['sections']), {'Description', 'Statement', 'Explanation', 'Proof', 'Literature'})
        self.assertEqual(parse_record(text.replace('proves:', 'refutes:'))['meta']['refutes'], 'Small.root')

    def test_windows_line_ends_are_read_as_line_ends(self):
        self.assertEqual(parse_record(RECORD.replace('\n', '\r\n')), parse_record(RECORD))

    def test_deeper_headings_and_headings_in_a_code_block_are_free(self):
        text = RECORD + ('\n### The base case\n\nThe empty sum.\n\n#### A remark\n\n```text\n## Not a section\n'
                         '## Proof\n```\n\n   ```lean\n## Statement\n   ```\n')
        proof = parse_record(text)['sections']['Proof']
        for line in ('### The base case', '#### A remark', '## Not a section', '## Proof', '## Statement'):
            self.assertIn(line, proof.split('\n'))

    def test_each_refusal(self):
        cases = {
            'no opening line': (RECORD[4:], 'begins with a line "---"'),
            'unknown header key': (RECORD.replace('weight: unit', 'weight: unit\nauthor: s1'), 'unknown header line.*author'),
            'header line without a colon': (RECORD.replace('weight: unit', 'weight: unit\nunit of the proof'),
                                            'unknown header line'),
            'repeated header key': (RECORD.replace('weight: unit', 'weight: unit\nweight: step'), 'weight appears twice'),
            'unclosed header': ('---\nshort: odd numbers sum to a square\nweight: unit\n', 'header is not closed'),
            'unknown section': (RECORD + '\n## Remarks\n\nA remark.\n', 'unknown section "## Remarks"'),
            'repeated section': (RECORD + '\n## Proof\n\nOnce more.\n', '"## Proof" appears twice'),
            'text before the first section': (RECORD.replace('---\n## Description', '---\nA stray line.\n\n## Description'),
                                              'text before the first section'),
            'no weight': (RECORD.replace('weight: unit\n', ''), 'weight: unit'),
            'invalid weight': (RECORD.replace('weight: unit', 'weight: lemma'), 'weight: unit'),
            'empty weight': (RECORD.replace('weight: unit', 'weight:'), 'weight: unit'),
            'no Description': (RECORD.replace('## Description\n\nThe sum of the first n odd numbers equals n times n.\n\n', ''),
                               'nonempty "## Description"'),
            'empty Description': (RECORD.replace('The sum of the first n odd numbers equals n times n.\n', ''),
                                  'nonempty "## Description"'),
            'proves together with refutes': (RECORD.replace('weight: unit', 'weight: unit\nproves: Small.a\nrefutes: Small.b'),
                                             'not both'),
            'invalid name in proves': (RECORD.replace('weight: unit', 'weight: unit\nproves: Small..root'),
                                       'not a declaration name'),
            'invalid name in refutes': (RECORD.replace('weight: unit', 'weight: unit\nrefutes: .root'),
                                        'not a declaration name'),
        }
        for label, (text, message) in cases.items():
            with self.subTest(label), self.assertRaisesRegex(CanonError, message):
                parse_record(text)

    def test_the_one_added_header_key_of_the_refusals_is_valid_alone(self):
        # The refusals above each change one thing; these are the same records without the violation.
        for extra in ('proves: Small.a', 'refutes: Small.b', 'source: knuth1997'):
            with self.subTest(extra):
                parse_record(RECORD.replace('weight: unit', 'weight: unit\n' + extra))

    def test_a_record_whose_header_was_left_open_is_refused(self):
        # Without the closing line, the first section heading is read as a line of the header.
        with self.assertRaisesRegex(CanonError, "unknown header line '## Description'"):
            parse_record(RECORD.replace('weight: unit\n---\n', 'weight: unit\n'))

    def test_the_message_names_the_file(self):
        with self.assertRaisesRegex(CanonError, r'^records/Small/root\.md: '):
            parse_record(RECORD.replace('weight: unit', 'weight: lemma'), 'records/Small/root.md')


class ApproachFormatTests(unittest.TestCase):
    def test_an_approach_entry_is_parsed(self):
        entry = parse_approach(APPROACH)
        self.assertEqual(entry['meta'], {'title': 'Induction on the number of terms', 'sessions': ['s1', 's2']})
        self.assertEqual(entry['sections'], {'Idea': 'Compare the sum for n + 1 with the sum for n.',
                                             'Established': 'Small.oddSum_succ',
                                             'Where it stops': 'The arithmetic identity has not been checked.'})

    def test_sessions_are_a_list(self):
        self.assertEqual(parse_approach(APPROACH.replace('sessions: s1, s2', 'sessions: s9'))['meta']['sessions'], ['s9'])
        self.assertEqual(parse_approach(APPROACH.replace('sessions: s1, s2', 'sessions:  s1 ,, s2 ,'))['meta']['sessions'],
                         ['s1', 's2'])
        self.assertEqual(parse_approach(APPROACH.replace('sessions: s1, s2\n', ''))['meta']['sessions'], [])

    def test_established_is_optional(self):
        entry = parse_approach(APPROACH.replace('## Established\n\nSmall.oddSum_succ\n\n', ''))
        self.assertNotIn('Established', entry['sections'])

    def test_each_refusal(self):
        cases = {
            'no title': (APPROACH.replace('title: Induction on the number of terms\n', ''), 'needs a "title"'),
            'empty title': (APPROACH.replace('title: Induction on the number of terms', 'title:'), 'needs a "title"'),
            'no Idea': (APPROACH.replace('## Idea\n\nCompare the sum for n + 1 with the sum for n.\n\n', ''),
                        'nonempty "## Idea"'),
            'empty Idea': (APPROACH.replace('Compare the sum for n + 1 with the sum for n.\n', ''), 'nonempty "## Idea"'),
            'no Where it stops': (APPROACH.replace('## Where it stops\n\nThe arithmetic identity has not been checked.\n', ''),
                                  'nonempty "## Where it stops"'),
            'unknown header key': (APPROACH.replace('sessions: s1, s2', 'weight: unit'), 'unknown header line'),
            'a section of a record': (APPROACH + '\n## Proof\n\nNot here.\n', 'unknown section "## Proof"'),
            'no opening line': (APPROACH[4:], 'begins with a line "---"'),
        }
        for label, (text, message) in cases.items():
            with self.subTest(label), self.assertRaisesRegex(CanonError, message):
                parse_approach(text)

    def test_the_review_section_of_the_runner_is_accepted(self):
        entry = parse_approach(with_review(APPROACH, 'Change c1 (revision 4): Closed the step.'))
        self.assertEqual(entry['sections']['Review'], 'Change c1 (revision 4): Closed the step.')
        self.assertEqual(entry['sections']['Where it stops'], 'The arithmetic identity has not been checked.')

    def test_a_record_has_no_review_section(self):
        with self.assertRaisesRegex(CanonError, 'unknown section "## Review"'):
            parse_record(RECORD + '\n## Review\n\nNot the place.\n')

    def test_split_review(self):
        self.assertEqual(split_review('Understood so far.\n\n## Review\n\nChange c1 (revision 3): Closed it.\n'),
                         ('Understood so far.\n', 'Change c1 (revision 3): Closed it.'))
        self.assertEqual(split_review('Understood so far.'), ('Understood so far.\n', None))
        self.assertEqual(split_review('Understood.\r\n\r\n## Review\r\n\r\nGood.\r\n'), ('Understood.\n', 'Good.'))

    def test_with_review(self):
        self.assertEqual(with_review('Understood so far.\n', None), 'Understood so far.\n')
        self.assertEqual(with_review('Understood so far.\n', '  Closed it.\n'),
                         'Understood so far.\n\n## Review\n\nClosed it.\n')
        once = with_review('Understood so far.\n', 'First assessment.')
        self.assertEqual(with_review(once, 'Second assessment.'), 'Understood so far.\n\n## Review\n\nSecond assessment.\n')
        self.assertEqual(with_review(once, None), 'Understood so far.\n')
        self.assertEqual(split_review(with_review(APPROACH, 'An assessment.')), (APPROACH, 'An assessment.'))


# --------------------------------------------------------------------------------------- Lean sources

SOURCE = '''namespace Small

theorem a : True := trivial  -- note

/-- Doc. -/
theorem b (n : Nat) :
    n = n := by
  rfl

end Small
'''


class LeanSourceTests(TempCase):
    def test_the_header_of_a_module_file(self):
        lines = ['module', '', 'public import Small.Defs', 'public import Small.Step', '', '@[expose] public section']
        self.assertEqual(header_scan(lines), (4, True, ['Small.Defs', 'Small.Step']))

    def test_the_header_of_a_plain_file(self):
        self.assertEqual(header_scan(['import Lean', 'import Small.Defs', '', 'open Lean']),
                         (2, False, ['Lean', 'Small.Defs']))
        self.assertEqual(header_scan(['prelude', 'import Init.Core', 'def x := 1']), (2, False, ['Init.Core']))

    def test_a_header_without_imports(self):
        self.assertEqual(header_scan(['module', '', '@[expose] public section']), (1, True, []))
        self.assertEqual(header_scan(['def x := 1', 'import Late']), (0, False, []))
        self.assertEqual(header_scan([]), (0, False, []))

    def test_the_header_scan_knows_the_forms_of_an_import(self):
        lines = ['module', 'public meta import Small.A', 'import all Small.B', 'meta import Small.C', 'def x := 1']
        self.assertEqual(header_scan(lines), (4, True, ['Small.A', 'Small.B', 'Small.C']))

    def test_the_modules_that_import_a_changed_module_are_named_with_it(self):
        # Lean compiles a module in the environment of what it imports, so a module that imports a changed one,
        # directly or through others, can come out different although its own source is the same.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, imports in (('Defs', ()), ('Root', ('Small.Defs',)), ('Step', ('Small.Defs',)),
                                  ('Top', ('Small.Step', 'Mathlib.Tactic')), ('Far', ('Small.Top',))):
                write(root / 'Small' / (name + '.lean'),
                      'module\n\n' + ''.join(f'public import {i}\n' for i in imports) + '\n-- import Small.Root\n')
            write(root / 'DoMathExtract.lean', 'import Small.Step\n')  # no module of the library
            self.assertEqual(with_importers(root, 'Small', ['Small.Step']), ['Small.Far', 'Small.Step', 'Small.Top'])
            self.assertEqual(with_importers(root, 'Small', ['Small.Defs']),
                             ['Small.Defs', 'Small.Far', 'Small.Root', 'Small.Step', 'Small.Top'])
            self.assertEqual(with_importers(root, 'Small', ['Small.Far', 'Small.New']), ['Small.Far', 'Small.New'])
            self.assertEqual(with_importers(root, 'Small', []), [])

    def test_the_header_scan_skips_comments(self):
        lines = ['/- Copyright.', '   import Fake.Module', '   /- nested -/ still a comment', '-/',
                 '-- import Other.Fake', 'module', '', 'public import Small.Defs -- the definitions',
                 '/- between -/ public import Small.Step', '', 'theorem t : True := trivial',
                 'import After.The.Header']
        self.assertEqual(header_scan(lines), (9, True, ['Small.Defs', 'Small.Step']))
        # A comment inside a line separates what stands on its two sides, as it does for Lean and for the Lean
        # broker, which reads a header through the same code (lean_broker.read_header).
        self.assertEqual(header_scan(['import/- why -/Small.Defs', 'def x := 1']), (1, False, ['Small.Defs']))

    def test_a_module_file_gets_a_public_import(self):
        text = 'module\n\npublic import Small.Defs\n\n@[expose] public section\n'
        self.assertEqual(add_imports(text, ['Small.Step']),
                         'module\n\npublic import Small.Defs\npublic import Small.Step\n\n@[expose] public section\n')

    def test_a_plain_file_gets_an_import(self):
        text = 'import Lean\nimport Small.Defs\n\nopen Lean\n'
        self.assertEqual(add_imports(text, ['Small.Step']), 'import Lean\nimport Small.Defs\nimport Small.Step\n\nopen Lean\n')

    def test_an_import_already_present_is_not_added_again(self):
        text = 'module\n\npublic import Small.Defs\nimport all Small.Step\n\n@[expose] public section\n'
        self.assertEqual(add_imports(text, ['Small.Defs']), text)
        self.assertEqual(add_imports(text, ['Small.Step']), text)
        self.assertEqual(add_imports(text, ['Small.Defs', 'Small.More', 'Small.Step']),
                         text.replace('import all Small.Step\n', 'import all Small.Step\npublic import Small.More\n'))
        self.assertEqual(add_imports(text, []), text)

    def test_several_imports_are_added_in_the_order_given(self):
        text = 'module\n\n@[expose] public section\n'
        self.assertEqual(add_imports(text, ['Small.B', 'Small.A']),
                         'module\npublic import Small.B\npublic import Small.A\n\n@[expose] public section\n')

    def test_imports_go_after_the_last_header_line_past_comments(self):
        text = ('/- A note that says: import nothing by hand. -/\nmodule\n\n-- the definitions\n'
                'public import Small.Defs  -- import Small.Step\n\n/-- Doc. -/\ntheorem t : True := trivial\n')
        self.assertEqual(add_imports(text, ['Small.Step']),
                         text.replace('-- import Small.Step\n', '-- import Small.Step\npublic import Small.Step\n'))

    def test_an_import_that_stands_only_in_a_block_comment_is_added(self):
        # header_scan skips comments, so a line of a comment is not an import of the file.
        text = '/-\nimport Small.Step\n-/\nmodule\n\npublic import Small.Defs\n\ntheorem t : True := trivial\n'
        self.assertIn('public import Small.Step', add_imports(text, ['Small.Step']).split('\n'))

    def test_declaration_text_of_one_line(self):
        self.assertEqual(declaration_text(SOURCE, [3, 0, 3, 27]), 'theorem a : True := trivial')
        self.assertEqual(declaration_text(SOURCE, [3, 8, 3, 16]), 'a : True')

    def test_declaration_text_of_several_lines(self):
        self.assertEqual(declaration_text(SOURCE, [5, 0, 8, 5]), '/-- Doc. -/\ntheorem b (n : Nat) :\n    n = n := by\n  rfl')
        self.assertEqual(declaration_text(SOURCE, [6, 8, 7, 9]), 'b (n : Nat) :\n    n = n')
        self.assertEqual(declaration_text(SOURCE, [7, 4, 8, 5]), 'n = n := by\n  rfl')

    def test_columns_count_characters(self):
        text = 'theorem c (n : ℕ) : n ≤ n := le_refl n  -- ℕ\n'
        start = len('theorem c (n : ℕ) : ')
        self.assertEqual(declaration_text(text, [1, start, 1, start + len('n ≤ n')]), 'n ≤ n')

    def test_replace_span_keeps_what_surrounds_the_span_on_its_lines(self):
        self.assertEqual(replace_span(SOURCE, [3, 8, 3, 16], "a' : False"),
                         SOURCE.replace('theorem a : True := trivial  -- note', "theorem a' : False := trivial  -- note"))
        self.assertEqual(replace_span(SOURCE, [6, 8, 7, 9], 'c : 1 = 1'),
                         SOURCE.replace('theorem b (n : Nat) :\n    n = n := by', 'theorem c : 1 = 1 := by'))

    def test_replace_span_may_change_the_number_of_lines(self):
        longer = replace_span(SOURCE, [3, 0, 3, 27], 'theorem a : True := by\n  have h := b 0\n  trivial')
        self.assertEqual(longer, SOURCE.replace('theorem a : True := trivial  -- note',
                                                'theorem a : True := by\n  have h := b 0\n  trivial  -- note'))
        self.assertEqual(longer.count('\n'), SOURCE.count('\n') + 2)
        shorter = replace_span(SOURCE, [5, 0, 8, 5], 'theorem b (n : Nat) : n = n := rfl')
        self.assertEqual(shorter, SOURCE.replace('/-- Doc. -/\ntheorem b (n : Nat) :\n    n = n := by\n  rfl',
                                                 'theorem b (n : Nat) : n = n := rfl'))
        self.assertEqual(shorter.count('\n'), SOURCE.count('\n') - 3)

    def test_replace_span_drops_the_line_ends_around_a_replacement(self):
        self.assertEqual(replace_span(SOURCE, [3, 0, 3, 27], '\ntheorem a : True :=\n  trivial\n\n'),
                         SOURCE.replace('theorem a : True := trivial', 'theorem a : True :=\n  trivial'))

    def test_the_replacement_is_the_text_at_its_span(self):
        replacement = 'theorem b (n : Nat) : n = n := by\n  cases n\n  · rfl\n  · rfl'
        text = replace_span(SOURCE, [5, 0, 8, 5], replacement)
        self.assertEqual(declaration_text(text, [5, 0, 8, 7]), replacement)

    def test_module_file(self):
        self.assertEqual(module_file('Small.Defs'), 'Small/Defs.lean')
        self.assertEqual(module_file('Small.Sub.Deep'), 'Small/Sub/Deep.lean')
        self.assertEqual(module_file('Small'), 'Small.lean')

    def test_library_modules_are_the_lean_files_of_the_library(self):
        lean = self.root / 'lean'
        for relative in ('Small/Root.lean', 'Small/Defs.lean', 'Small/Sub/Deep.lean', 'Other/Module.lean',
                         'DoMathExtract.lean', 'Small/notes.md'):
            write(lean / relative, 'module\n')
        self.assertEqual(library_modules(lean, 'Small'),
                         [('Small.Defs', lean / 'Small/Defs.lean'), ('Small.Root', lean / 'Small/Root.lean'),
                          ('Small.Sub.Deep', lean / 'Small/Sub/Deep.lean')])
        self.assertEqual(library_modules(lean, 'Absent'), [])

    def test_library_modules_are_in_name_order(self):
        # The order its docstring states, with a module that has submodules and the library's own file.
        lean = self.root / 'lean'
        for relative in ('Small.lean', 'Small/Sub.lean', 'Small/Sub/Deep.lean', 'Small/Defs.lean'):
            write(lean / relative, 'module\n')
        names = [name for name, _ in library_modules(lean, 'Small')]
        self.assertEqual(sorted(names), ['Small', 'Small.Defs', 'Small.Sub', 'Small.Sub.Deep'])
        self.assertEqual(names, sorted(names))


# --------------------------------------------------------------------------------------- candidates

STEP = '''/-- Adding the next odd number. -/
theorem oddSum_succ (n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1) := by
  rfl'''
INFORMAL = '''/-- The sum of the first `n` odd numbers is the square of `n`. -/
theorem root (n : Nat) : oddSum n = n * n := by
  have step := oddSum_succ
  sorry'''
ROOT_RECORD = record_text('The sum of the first n odd numbers equals n times n.', weight='unit',
                          statement='For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.',
                          proof='By induction on $n$; the step uses `Small.oddSum_succ`.')
STEP_RECORD = record_text('Passing from n to n + 1 adds the odd number 2n + 1 to the sum.')


class LoadChangeTests(TempCase):
    def candidate(self, **change):
        folder = self.root / 'candidate'
        write(folder / 'lean/Small/Step.lean', module_text(STEP))
        write(folder / 'lean/Small/Sub/More.lean', module_text('theorem more : oddSum 0 = 0 := by\n  rfl'))
        write(folder / 'replace/root.lean', INFORMAL + '\n')
        write(folder / 'records/Small/oddSum_succ.md', STEP_RECORD)
        write(folder / 'records/Small/root.md', ROOT_RECORD)
        write(folder / 'approaches/Small/root/induction.md', APPROACH)
        write(folder / 'questions/q0.md', 'The sum grows by one odd number at a time.\n')
        write(folder / 'evidence/Small/root/table.csv', 'n,sum\n1,1\n2,4\n')
        write(folder / 'bibliography.bib', '@book{knuth1997, title = {The Art of Computer Programming}}\n')
        self.manifest(folder, **change)
        return folder

    def manifest(self, folder, **change):
        data = {'title': 'The sum of the first odd numbers', 'description': 'An induction that proves the root.',
                'replace': [{'declaration': 'Small.root', 'file': 'replace/root.lean', 'imports': ['Small.Step']}],
                'questions': [], 'resolutions': []}
        data.update(change)
        # A key given as ... is left out of the manifest.
        write_json(folder / 'change.json', {key: value for key, value in data.items() if value is not ...})

    def refused(self, message, **change):
        with self.assertRaisesRegex(CanonError, message):
            load_change(self.candidate(**change))

    def test_a_valid_folder(self):
        change = load_change(self.candidate())
        self.assertEqual(change['title'], 'The sum of the first odd numbers')
        self.assertEqual(change['replace'], [{'declaration': 'Small.root', 'file': 'replace/root.lean',
                                              'imports': ['Small.Step']}])
        self.assertEqual(change['modules'], ['Small/Step.lean', 'Small/Sub/More.lean'])
        self.assertEqual(change['records'], ['Small/oddSum_succ.md', 'Small/root.md'])
        self.assertEqual(change['approaches'], ['Small/root/induction.md'])
        self.assertEqual(change['understanding'], ['q0.md'])
        self.assertEqual((change['questions'], change['resolutions'], change['retire']), ([], [], []))

    def test_the_smallest_manifest(self):
        folder = self.root / 'small'
        folder.mkdir()
        write_json(folder / 'change.json', {'title': 'A remark', 'description': 'Nothing but its manifest.'})
        change = load_change(folder)
        for key in ('replace', 'questions', 'resolutions', 'retire', 'modules', 'records', 'approaches', 'understanding'):
            self.assertEqual(change[key], [], key)

    def test_imports_of_a_replacement_are_optional(self):
        change = load_change(self.candidate(replace=[{'declaration': 'Small.root', 'file': 'replace/root.lean'}]))
        self.assertEqual(change['replace'][0]['imports'], [])

    def test_manifest_refusals(self):
        replacement = {'declaration': 'Small.root', 'file': 'replace/root.lean'}
        retirement = {'alternative': 'Small.root_alt', 'into': 'Small.root', 'reason': 'The proof stands under the root.'}
        cases = {
            'unknown key': ({'reviewer': 's1'}, 'unknown key in change.json: reviewer'),
            'missing title': ({'title': ...}, 'nonempty "title"'),
            'blank title': ({'title': '  '}, 'nonempty "title"'),
            'title that is no text': ({'title': 7}, 'nonempty "title"'),
            'missing description': ({'description': ...}, 'nonempty "description"'),
            'blank description': ({'description': '\n'}, 'nonempty "description"'),
            'replace that is no array': ({'replace': replacement}, '"replace" is an array'),
            'replacement that is no object': ({'replace': ['Small.root']}, 'a replacement has "declaration", "file"'),
            'replacement with an unknown key': ({'replace': [{**replacement, 'reason': 'shorter'}]},
                                                'a replacement has "declaration", "file"'),
            'replacement without a declaration': ({'replace': [{'file': 'replace/root.lean'}]},
                                                  'missing or repeated replacement declaration'),
            'repeated declaration': ({'replace': [replacement, dict(replacement)]},
                                     'missing or repeated replacement declaration'),
            'declaration that is no name': ({'replace': [{**replacement, 'declaration': 'Small..root'}]},
                                            'not a declaration name'),
            'replacement without a file': ({'replace': [{'declaration': 'Small.root'}]}, 'nonempty relative path'),
            'replacement file that does not exist': ({'replace': [{**replacement, 'file': 'replace/absent.lean'}]},
                                                     'missing or escaping file: replace/absent.lean'),
            'absolute replacement file': ({'replace': [{**replacement, 'file': '/replace/root.lean'}]},
                                          'relative /-separated path'),
            'replacement file with a drive': ({'replace': [{**replacement, 'file': 'C:/replace/root.lean'}]},
                                              'relative /-separated path'),
            'replacement file that leaves the folder': ({'replace': [{**replacement, 'file': '../outside.lean'}]},
                                                        'relative /-separated path'),
            'replacement file with a backslash': ({'replace': [{**replacement, 'file': 'replace\\root.lean'}]},
                                                  'relative /-separated path'),
            'replacement file that is a folder': ({'replace': [{**replacement, 'file': 'replace'}]},
                                                  'missing or escaping file'),
            'imports that are no array': ({'replace': [{**replacement, 'imports': 'Small.Step'}]},
                                          '"imports" lists module names'),
            'import that is no text': ({'replace': [{**replacement, 'imports': [3]}]}, '"imports" lists module names'),
            'empty import': ({'replace': [{**replacement, 'imports': ['']}]}, '"imports" lists module names'),
            'questions that are no array': ({'questions': {}}, '"questions" is an array'),
            'resolutions that are no array': ({'resolutions': 'q1'}, '"resolutions" is an array'),
            'retire that is no array': ({'retire': {'alternative': 'Small.a'}}, '"retire" is an array'),
            'retirement that is no object': ({'retire': ['Small.root_alt']}, 'a retirement has "alternative", "into" and "reason"'),
            'retirement without the statement it goes into': ({'retire': [{'alternative': 'Small.root_alt', 'reason': 'Moved.'}]},
                                                              'a retirement has "alternative", "into" and "reason"'),
            'retired declaration that is no text': ({'retire': [{**retirement, 'alternative': 7}]},
                                                    'of a retirement are nonempty text'),
            'retirement with a blank reason': ({'retire': [{**retirement, 'reason': ' '}]}, 'of a retirement are nonempty text'),
        }
        write(self.root / 'outside.lean', INFORMAL)  # so that leaving the folder is the only fault of that case
        for label, (change, message) in cases.items():
            with self.subTest(label):
                self.refused(message, **change)
        # The retirement of which the refusals above each change one thing is accepted as it stands.
        self.assertEqual(load_change(self.candidate(retire=[retirement]))['retire'], [retirement])

    def test_a_manifest_that_is_no_object(self):
        folder = self.candidate()
        write_json(folder / 'change.json', [{'title': 'A', 'description': 'B'}])
        with self.assertRaisesRegex(CanonError, 'change.json is an object'):
            load_change(folder)

    def test_a_malformed_record_is_refused_with_its_path(self):
        folder = self.candidate()
        write(folder / 'records/Small/root.md', ROOT_RECORD.replace('weight: unit', 'weight: main'))
        with self.assertRaisesRegex(CanonError, r'^records/Small/root\.md: .*weight'):
            load_change(folder)

    def test_a_malformed_approach_is_refused_with_its_path(self):
        folder = self.candidate()
        write(folder / 'approaches/Small/root/induction.md', APPROACH.replace('## Idea', '## Plan'))
        with self.assertRaisesRegex(CanonError, r'^approaches/Small/root/induction\.md: .*## Plan'):
            load_change(folder)

    def test_an_approach_with_the_review_section_is_refused(self):
        # Also where the line stands in a code block, in which a heading is otherwise free: publication cuts an
        # entry at its first line `## Review` (canon.with_review), so what follows that line would be lost.
        fenced = APPROACH.replace('## Established', '```text\n## Review\n```\n\n## Established')
        self.assertNotIn('Review', parse_approach(fenced)['sections'])
        for label, text in (('as a section', with_review(APPROACH, 'It closed the step.')), ('in a code block', fenced)):
            folder = self.candidate()
            write(folder / 'approaches/Small/root/induction.md', text)
            with self.subTest(label), self.assertRaisesRegex(
                    CanonError, r'approaches/Small/root/induction\.md: the "## Review" section is written at publication'):
                load_change(folder)

    def test_an_empty_understanding_text_is_refused(self):
        for text in ('', ' \n\n'):
            folder = self.candidate()
            write(folder / 'questions/q0.md', text)
            with self.subTest(text=text), self.assertRaisesRegex(CanonError, r'questions/q0\.md is empty'):
                load_change(folder)

    def test_an_understanding_text_with_the_review_section_is_refused_wherever_the_heading_stands(self):
        cases = {'after the text, as publication writes it':
                     with_review('The sum grows by one odd number at a time.\n', 'It settles it.'),
                 'as the first line': '## Review\n\nThis settles the question.\n',
                 'as the last line, without a line end': 'The sum grows by one odd number.\n\n## Review',
                 'with spaces after it': 'The sum grows by one odd number.\n\n## Review  \n\nThis settles it.\n'}
        for label, text in cases.items():
            folder = self.candidate()
            write(folder / 'questions/q0.md', text)
            with self.subTest(label), self.assertRaisesRegex(
                    CanonError, r'questions/q0\.md: the "## Review" section is written at publication'):
                load_change(folder)

    def test_files_with_a_byte_order_mark_are_read(self):
        folder = self.candidate()
        for relative in ('records/Small/root.md', 'approaches/Small/root/induction.md', 'questions/q0.md'):
            path = folder / relative
            path.write_bytes(b'\xef\xbb\xbf' + path.read_bytes())
        self.assertEqual(load_change(folder)['records'], ['Small/oddSum_succ.md', 'Small/root.md'])

    def test_candidate_records_are_keyed_by_the_name_path(self):
        folder = self.candidate()
        records = candidate_records(folder, load_change(folder))
        self.assertEqual(sorted(records), ['Small/oddSum_succ', 'Small/root'])
        self.assertEqual(records['Small/root'], parse_record(ROOT_RECORD))

    def test_required_pairs(self):
        records = {'Small/root_again': parse_record(record_text('Another proof.', proves='Small.root')),
                   'Small/Aux%': parse_record(record_text('A counterexample.', refutes='Small.claim')),
                   'Small/dotted.name': parse_record(record_text('Dotted.', proves='Small.root')),
                   'Small/plain': parse_record(record_text('Nothing claimed.'))}
        self.assertEqual(sorted(required_pairs(records)),
                         [('negation', 'Small.Aux', 'Small.claim'), ('same', 'Small.root_again', 'Small.root'),
                          ('same', 'Small.«dotted.name»', 'Small.root')])
        self.assertEqual(required_pairs({}), [])


# --------------------------------------------------------------------------------------- applying the Lean part

LIB = '''module

public import Small.Defs

@[expose] public section

namespace Small

/-- First. -/
theorem first (n : Nat) : oddSum n = oddSum n := by
  sorry

theorem second : oddSum 0 = 0 := by
  sorry

def helper : Nat := 1

theorem third : oddSum 1 = 1 := by sorry

end Small
'''
FIRST = '/-- First. -/\ntheorem first (n : Nat) : oddSum n = oddSum n := by\n  sorry'
SECOND = 'theorem second : oddSum 0 = 0 := by\n  sorry'
THIRD = 'theorem third : oddSum 1 = 1 := by sorry'
NEW_FIRST = ('/-- First, with its argument. -/\ntheorem first (n : Nat) : oddSum n = oddSum n := by\n'
             '  have step := oddSum_succ\n  intro\n  rfl')
NEW_SECOND = 'theorem second : oddSum 0 = 0 := rfl'
NEW_THIRD = 'theorem third : oddSum 1 = 1 := by\n  rfl'


def source_index(text, declarations):
    """A structural index, written by hand, of the named declarations of the source file Small/Lib.lean."""
    entries = {name: {'name': name, 'kind': 'theorem', 'module': 'Small.Lib', 'file': 'Small/Lib.lean',
                      'span': span_of(text, snippet), 'source_sha': sha256_text(snippet)}
               for name, snippet in declarations.items()}
    return {'revision': 1, 'modules': {}, 'entries': entries, 'aux': {}, 'pairs': {}}


class ApplyLeanTests(TempCase):
    def setUp(self):
        super().setUp()
        self.lean = self.root / 'lean'
        self.file = write(self.lean / 'Small/Lib.lean', LIB)
        write(self.lean / 'Small/Defs.lean', 'module\n')
        self.index = source_index(LIB, {'Small.first': FIRST, 'Small.second': SECOND, 'Small.third': THIRD})
        self.number = 0

    def candidate(self, modules=None, replace=None, imports=None):
        self.number += 1
        folder = self.root / f'candidate-{self.number}'
        folder.mkdir()
        for relative, text in (modules or {}).items():
            write(folder / 'lean' / relative, text)
        entries = []
        for number, (name, text) in enumerate((replace or {}).items()):
            write(folder / f'replace/{number}.lean', text + '\n')
            entries.append({'declaration': name, 'file': f'replace/{number}.lean', 'imports': (imports or {}).get(name, [])})
        write_json(folder / 'change.json', {'title': 'A change', 'description': 'What it does.', 'replace': entries})
        return folder, load_change(folder)

    def text(self):
        return self.file.read_text(encoding='utf-8')

    def test_a_new_module_is_copied_and_reported(self):
        step, deep = module_text(STEP), module_text('theorem deep : oddSum 0 = 0 := rfl')
        folder, change = self.candidate(modules={'Small/Step.lean': step, 'Small/Sub/Deep.lean': deep})
        self.assertEqual(apply_lean(self.lean, folder, change, self.index), ['Small.Step', 'Small.Sub.Deep'])
        self.assertEqual((self.lean / 'Small/Step.lean').read_text(encoding='utf-8'), step)
        self.assertEqual((self.lean / 'Small/Sub/Deep.lean').read_text(encoding='utf-8'), deep)
        self.assertEqual(self.text(), LIB)

    def test_a_new_module_whose_path_exists_is_a_conflict(self):
        folder, change = self.candidate(modules={'Small/Lib.lean': module_text(STEP)})
        with self.assertRaisesRegex(CanonError, 'Small/Lib.lean already exists'):
            apply_lean(self.lean, folder, change, self.index)
        self.assertEqual(self.text(), LIB)

    def test_a_replacement_of_a_name_the_index_does_not_have_is_a_conflict(self):
        folder, change = self.candidate(replace={'Small.fourth': 'theorem fourth : True := trivial'})
        with self.assertRaisesRegex(CanonError, 'Small.fourth is not a declaration of the canon'):
            apply_lean(self.lean, folder, change, self.index)
        self.assertEqual(self.text(), LIB)

    def test_a_replacement_stands_where_the_declaration_stood(self):
        folder, change = self.candidate(replace={'Small.second': NEW_SECOND})
        self.assertEqual(apply_lean(self.lean, folder, change, self.index), ['Small.Lib'])
        self.assertEqual(self.text(), LIB.replace(SECOND, NEW_SECOND))

    def test_a_replacement_adds_its_imports_to_the_header_of_that_file(self):
        folder, change = self.candidate(replace={'Small.first': NEW_FIRST},
                                        imports={'Small.first': ['Small.Defs', 'Small.Step']})
        self.assertEqual(apply_lean(self.lean, folder, change, self.index), ['Small.Lib'])
        self.assertEqual(self.text(), LIB.replace(FIRST, NEW_FIRST).replace(
            'public import Small.Defs\n', 'public import Small.Defs\npublic import Small.Step\n'))

    def test_several_replacements_in_one_file_all_land(self):
        # The new texts have other numbers of lines than the old ones, in both directions.
        folder, change = self.candidate(replace={'Small.first': NEW_FIRST, 'Small.second': NEW_SECOND,
                                                 'Small.third': NEW_THIRD},
                                        imports={'Small.third': ['Small.Step']})
        self.assertEqual(apply_lean(self.lean, folder, change, self.index), ['Small.Lib'])
        self.assertEqual(self.text(), LIB.replace(FIRST, NEW_FIRST).replace(SECOND, NEW_SECOND).replace(THIRD, NEW_THIRD)
                         .replace('public import Small.Defs\n', 'public import Small.Defs\npublic import Small.Step\n'))

    def test_new_modules_and_replacements_together(self):
        folder, change = self.candidate(modules={'Small/Step.lean': module_text(STEP)}, replace={'Small.third': NEW_THIRD})
        self.assertEqual(apply_lean(self.lean, folder, change, self.index), ['Small.Lib', 'Small.Step'])

    def test_a_replacement_file_with_windows_line_ends(self):
        folder, change = self.candidate(replace={'Small.first': NEW_FIRST})
        (folder / 'replace/0.lean').write_bytes(b'\xef\xbb\xbf' + (NEW_FIRST + '\n').replace('\n', '\r\n').encode('utf-8'))
        apply_lean(self.lean, folder, change, self.index)
        self.assertEqual(self.file.read_bytes().decode('utf-8'), LIB.replace(FIRST, NEW_FIRST))

    def test_a_stale_index_is_a_conflict(self):
        # The file was changed without the index: the text at the recorded span is not the recorded one.
        changed = LIB.replace(SECOND, 'theorem second : oddSum 0 = 0 := by\n  rfl  ')
        write(self.file, changed)
        folder, change = self.candidate(replace={'Small.second': NEW_SECOND})
        with self.assertRaisesRegex(CanonError, 'Small.second does not match the index'):
            apply_lean(self.lean, folder, change, self.index)
        self.assertEqual(self.text(), changed)

    def test_a_proof_replaced_by_another_publication_is_a_conflict(self):
        # Two candidates were prepared against the same proof of `second`. The first is published, and the
        # index is extracted again; the second then finds that its base is no longer what the canon holds.
        bases = {'Small.second': self.index['entries']['Small.second']['source_sha']}
        folder, change = self.candidate(replace={'Small.second': NEW_SECOND})
        apply_lean(self.lean, folder, change, self.index, bases)
        published = LIB.replace(SECOND, NEW_SECOND)
        self.assertEqual(self.text(), published)
        current = source_index(published, {'Small.first': FIRST, 'Small.second': NEW_SECOND, 'Small.third': THIRD})
        later, change = self.candidate(replace={'Small.second': 'theorem second : oddSum 0 = 0 := by\n  simp [oddSum]'})
        with self.assertRaisesRegex(CanonError, 'the proof of Small.second was replaced by another publication'):
            apply_lean(self.lean, later, change, current, bases)
        self.assertEqual(self.text(), published)

    def test_a_conflict_on_one_replacement_leaves_the_whole_file_unchanged(self):
        folder, change = self.candidate(replace={'Small.first': NEW_FIRST, 'Small.third': NEW_THIRD})
        with self.assertRaisesRegex(CanonError, 'the proof of Small.first was replaced by another publication'):
            apply_lean(self.lean, folder, change, self.index, {'Small.first': sha256_text('another proof')})
        self.assertEqual(self.text(), LIB)

    def test_a_proof_replaced_elsewhere_in_the_file_is_no_conflict(self):
        # Another publication replaced `first` and moved the lines below it; the proof of `third` is still
        # the one this candidate was written against, so it is replaced where it now stands.
        bases = {'Small.third': self.index['entries']['Small.third']['source_sha']}
        published = LIB.replace(FIRST, NEW_FIRST)
        write(self.file, published)
        current = source_index(published, {'Small.first': NEW_FIRST, 'Small.second': SECOND, 'Small.third': THIRD})
        self.assertNotEqual(current['entries']['Small.third']['span'], self.index['entries']['Small.third']['span'])
        folder, change = self.candidate(replace={'Small.third': NEW_THIRD})
        self.assertEqual(apply_lean(self.lean, folder, change, current, bases), ['Small.Lib'])
        self.assertEqual(self.text(), published.replace(THIRD, NEW_THIRD))

    def test_a_rearrangement_writes_its_files_and_deletes_the_listed_modules(self):
        write(self.lean / 'Small/Old.lean', module_text('theorem old : oddSum 0 = 0 := rfl'))
        folder = self.root / 'organizer'
        rewritten = LIB.replace(THIRD, NEW_THIRD)
        moved = module_text('theorem old : oddSum 0 = 0 := rfl')
        write(folder / 'rewrite/lean/Small/Lib.lean', rewritten)
        write(folder / 'rewrite/lean/Small/Sub/Moved.lean', moved)
        write(folder / 'rewrite/notes.md', 'Not a module.')
        written, removed = apply_rearrangement(self.lean, folder, ['Small.Old', 'Small.Absent'])
        self.assertEqual((sorted(written), removed), (['Small.Lib', 'Small.Sub.Moved'], ['Small.Old']))
        self.assertEqual(self.text(), rewritten)
        self.assertEqual((self.lean / 'Small/Sub/Moved.lean').read_text(encoding='utf-8'), moved)
        self.assertFalse((self.lean / 'Small/Old.lean').exists())
        self.assertTrue((self.lean / 'Small/Defs.lean').exists())

    def test_a_rearrangement_without_files(self):
        folder = self.root / 'organizer'
        folder.mkdir()
        self.assertEqual(apply_rearrangement(self.lean, folder, []), ([], []))
        self.assertEqual(self.text(), LIB)


class TreeTests(TempCase):
    def tree(self, name, files):
        for relative, text in files.items():
            write(self.root / name / relative, text)
        return self.root / name

    def test_tree_hash_follows_paths_and_contents(self):
        files = {'change.json': '{}', 'lean/Small/Step.lean': 'module\n', 'records/Small/step.md': 'text'}
        first = tree_hash(self.tree('a', files))
        self.assertEqual(tree_hash(self.tree('b', dict(reversed(files.items())))), first)
        self.assertNotEqual(tree_hash(self.tree('c', {**files, 'records/Small/step.md': 'other text'})), first)
        self.assertNotEqual(tree_hash(self.tree('d', {**files, 'evidence/table.csv': ''})), first)
        renamed = {('records/Small/moved.md' if key.startswith('records') else key): value for key, value in files.items()}
        self.assertNotEqual(tree_hash(self.tree('e', renamed)), first)

    def test_tree_hash_skips_the_named_files(self):
        files = {'change.json': '{}', 'lean/Small/Step.lean': 'module\n'}
        plain = tree_hash(self.tree('a', files))
        receipt = self.tree('b', {**files, 'prepared.json': '{"ok": true}'})
        self.assertNotEqual(tree_hash(receipt), plain)
        self.assertEqual(tree_hash(receipt, skip=('prepared.json',)), plain)

    def test_sync_tree_makes_the_target_hold_the_files_of_the_source(self):
        source = self.tree('source', {'Small/Defs.lean': 'defs', 'Small/Root.lean': 'new root', 'Small/Sub/New.lean': 'new'})
        target = self.tree('target', {'Small/Defs.lean': 'defs', 'Small/Root.lean': 'old root', 'Small/Gone.lean': 'gone'})
        untouched = os.stat(target / 'Small/Defs.lean')
        sync_tree(source, target)
        files = {p.relative_to(target).as_posix(): p.read_text(encoding='utf-8') for p in target.rglob('*') if p.is_file()}
        self.assertEqual(files, {'Small/Defs.lean': 'defs', 'Small/Root.lean': 'new root', 'Small/Sub/New.lean': 'new'})
        after = os.stat(target / 'Small/Defs.lean')
        self.assertEqual((after.st_mtime_ns, after.st_ino), (untouched.st_mtime_ns, untouched.st_ino))

    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_sync_tree_waits_for_a_reader_that_holds_a_file_it_removes(self):
        # A rearrangement takes a module out of the canon while a session reads it. The reader holds the file
        # open without delete sharing, as Python's `open` does, and Windows removes no file held so. The
        # removal waits for the reader, as the replacement of a changed file does.
        source = self.tree('source', {'Small/Defs.lean': 'defs'})
        target = self.tree('target', {'Small/Defs.lean': 'defs', 'Small/Gone.lean': 'gone'})
        reader = (target / 'Small/Gone.lean').open(encoding='utf-8')
        self.addCleanup(reader.close)
        with patch('runtime_support.time.sleep', side_effect=lambda seconds: reader.close()) as sleep:
            sync_tree(source, target)
        self.assertTrue(sleep.called)
        self.assertEqual([p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()], ['Small/Defs.lean'])

    def test_sync_tree_has_a_changed_file_on_the_disk_before_it_takes_its_name(self):
        # The runner saves, through to the disk, that a publication is installed, and then removes the stage the
        # modules came from. A module that the system still held in memory when the machine lost power would stand
        # in the canon without its content, and the runner that follows would install nothing again.
        source = self.tree('source', {'Small/Defs.lean': 'defs', 'Small/Root.lean': 'new root'})
        target = self.tree('target', {'Small/Defs.lean': 'defs', 'Small/Root.lean': 'old root'})
        self.assertEqual(self.moves(lambda: sync_tree(source, target)), [('Root.lean', [len('new root')])])
        self.assertEqual((target / 'Small/Root.lean').read_text(encoding='utf-8'), 'new root')

    def test_copy_tree_replaces_what_the_target_held(self):
        source = self.tree('source', {'Small/Defs.lean': 'defs'})
        target = self.tree('target', {'Small/Stale.lean': 'stale'})
        copy_tree(source, target)
        self.assertEqual([p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()], ['Small/Defs.lean'])
        copy_tree(source, self.root / 'fresh')
        self.assertEqual((self.root / 'fresh/Small/Defs.lean').read_text(encoding='utf-8'), 'defs')


# --------------------------------------------------------------------------------------- the structural index

def row(name, kind='theorem', module='Small.A', span=None, user=None, private=False, internal=False,
        type_uses=(), value_uses=(), library=(), sorry=False, collected=()):
    """One row of an extraction, in the shape the stand-in compiler and canon.extraction_source print.

    `sorry` says whether the constant's own term contains `sorry`; `collected` is what Lean collects as
    the axioms of the constant, through everything it uses."""
    user = user or name
    return {'name': name, 'kind': kind, 'module': module, 'private': private, 'internal': internal, 'user': user,
            'span': span, 'sig': user + ' : statement', 'prop': kind in ('theorem', 'axiom'),
            'statement': 'hash-of-' + user, 'type_uses': list(type_uses), 'value_uses': list(value_uses),
            'library': list(library), 'sorry': sorry, 'collected': list(collected)}


class RowTests(unittest.TestCase):
    def test_rows_and_pairs_are_read_from_the_marked_lines(self):
        first, second = row('Small.a'), row('Small.b', kind='def')
        output = '\n'.join([
            'Small/A.lean:3:8: warning: declaration uses `sorry`',
            '@@canon ' + json.dumps(first),
            'a line that mentions @@canon {"name": "not a row"}',
            '@@canon ' + json.dumps(second),
            '@@canon ' + json.dumps({'pair': 'same', 'a': 'Small.b', 'b': 'Small.a', 'holds': True}),
            '@@canon ' + json.dumps({'pair': 'negation', 'a': 'Small.c', 'b': 'Small.a', 'holds': False}),
            '@@canon ' + json.dumps({'done': True}), ''])
        rows, pairs = parse_rows(output)
        self.assertEqual(rows, [first, second])
        self.assertEqual(pairs, {'same|Small.b|Small.a': True, 'negation|Small.c|Small.a': False})

    def test_an_extraction_without_rows(self):
        self.assertEqual(parse_rows('@@canon {"done": true}\n'), ([], {}))

    def test_an_extraction_that_did_not_reach_its_last_row_is_refused(self):
        for output in ('', '@@canon ' + json.dumps(row('Small.a')) + '\nerror: maximum recursion depth\n'):
            with self.subTest(output=output), self.assertRaisesRegex(CanonError, 'extraction did not finish'):
                parse_rows(output)

    def test_the_extraction_source_names_its_modules_and_pairs(self):
        source = extraction_source('Small', ['Small.Defs', 'Small.Root'], [('same', 'Small.again', 'Small.root'),
                                                                           ('negation', 'Small.no', 'Small.root')])
        lines = source.split('\n')
        self.assertNotEqual(lines[0].strip(), 'module')  # a plain file, so that it reads the proofs
        for line in ('import Small.Defs', 'import Small.Root', 'def targets : Array Name := #[`Small.Defs, `Small.Root]',
                     'def library : Name := `Small',
                     'def pairs : Array (String × Name × Name) := #[("same", `Small.again, `Small.root), '
                     '("negation", `Small.no, `Small.root)]'):
            self.assertIn(line, lines)
        self.assertIn('"@@canon "', source)

    def test_the_extraction_asks_lean_for_the_axioms(self):
        source = extraction_source('Small', ['Small.Defs'], [])
        self.assertIn('let axioms ← collectAxioms name', source)
        self.assertIn('("collected", toJson (axioms.map toString))', source)
        self.assertIn('("sorry", used.contains ``sorryAx)', source)


A_SOURCE = '''module

@[expose] public section

namespace Small

def base : Nat := 0

def count : Nat → Nat
  | 0 => base
  | n + 1 => count n + 1

structure Point where
  x : Nat
  y : Nat

theorem lemma1 : base = 0 := by
  rfl

private theorem helper : count 0 = 0 := by
  have h := lemma1
  sorry

theorem main : base = 0 := by
  have h := helper
  exact lemma1

theorem open_statement : count 1 = 1 := by
  sorry

axiom assumed : base = 1

end Small
'''
BASE = 'def base : Nat := 0'
COUNT = 'def count : Nat → Nat\n  | 0 => base\n  | n + 1 => count n + 1'
POINT = 'structure Point where\n  x : Nat\n  y : Nat'
LEMMA1 = 'theorem lemma1 : base = 0 := by\n  rfl'
HELPER = 'private theorem helper : count 0 = 0 := by\n  have h := lemma1\n  sorry'
MAIN = 'theorem main : base = 0 := by\n  have h := helper\n  exact lemma1'
OPEN = 'theorem open_statement : count 1 = 1 := by\n  sorry'
ASSUMED = 'axiom assumed : base = 1'
PRIVATE_HELPER = '_private.Small.A.0.Small.helper'

B_SOURCE = '''module

public import Small.A

@[expose] public section

namespace Small

theorem uses_field (p : Point) : p.x = p.x := by
  rfl

theorem doomed : base = 0 := by
  exact lemma1

end Small
'''
USES_FIELD = 'theorem uses_field (p : Point) : p.x = p.x := by\n  rfl'
DOOMED = 'theorem doomed : base = 0 := by\n  exact lemma1'
B_LATER = B_SOURCE.replace(DOOMED + '\n\n', '').replace(
    'theorem uses_field', 'theorem fresh : count 0 = base := by\n  exact lemma1\n\ntheorem uses_field')
FRESH = 'theorem fresh : count 0 = base := by\n  exact lemma1'


def rows_a():
    at = lambda snippet: span_of(A_SOURCE, snippet)
    return [
        row('Small.base', 'def', span=at(BASE)),
        row('Small.count', 'def', span=at(COUNT), value_uses=['Small.base', 'Small.count']),
        # Generated by Lean for `count`: no place in the source.
        row('Small.count.eq_1', span=None, type_uses=['Small.count', 'Small.base'], value_uses=['Small.count']),
        row('Small.Point', 'inductive', span=at(POINT), value_uses=['Small.Point.mk']),
        # The constructor and the fields of a structure lie inside the structure they extend the name of.
        row('Small.Point.mk', 'ctor', span=at(POINT), type_uses=['Small.Point']),
        row('Small.Point.x', 'def', span=at('x : Nat'), type_uses=['Small.Point'], value_uses=['Small.Point.rec']),
        row('Small.Point.y', 'def', span=at('y : Nat'), type_uses=['Small.Point'], value_uses=['Small.Point.rec']),
        row('Small.Point.rec', 'rec', span=None, type_uses=['Small.Point']),
        row('Small.lemma1', span=at(LEMMA1), type_uses=['Small.base'], library=['Nat.zero_eq']),
        row(PRIVATE_HELPER, span=at(HELPER), user='Small.helper', private=True, type_uses=['Small.count'],
            value_uses=['Small.lemma1'], library=['Nat.add_comm'], sorry=True, collected=['sorryAx']),
        # Lean collects the axioms of `main` through the helper and through `main._proof_1`.
        row('Small.main', span=at(MAIN), type_uses=['Small.base'],
            value_uses=[PRIVATE_HELPER, 'Small.main._proof_1', 'Small.lemma1'], library=['Nat.le_refl'],
            collected=['Classical.choice', 'propext', 'sorryAx']),
        # Generated by Lean for `main`, marked internal; it names a field of the structure.
        row('Small.main._proof_1', span=at(MAIN), internal=True, value_uses=['Small.Point.x'],
            library=['Nat.succ_le_of_lt'], collected=['Classical.choice']),
        row('Small.open_statement', span=at(OPEN), type_uses=['Small.count'], sorry=True, collected=['sorryAx']),
        row('Small.assumed', 'axiom', span=at(ASSUMED), type_uses=['Small.base'], collected=['Small.assumed']),
    ]


def rows_b(source=B_SOURCE):
    at = lambda snippet: span_of(source, snippet)
    rows = [row('Small.uses_field', module='Small.B', span=at(USES_FIELD), type_uses=['Small.Point', 'Small.Point.x'],
                value_uses=['Small.count.eq_1'])]
    if DOOMED in source:
        rows.append(row('Small.doomed', module='Small.B', span=at(DOOMED), type_uses=['Small.base'],
                        value_uses=['Small.lemma1']))
    if FRESH in source:
        rows.append(row('Small.fresh', module='Small.B', span=at(FRESH), type_uses=['Small.count', 'Small.base'],
                        value_uses=['Small.lemma1']))
    return rows


class UpdateIndexTests(TempCase):
    def setUp(self):
        super().setUp()
        self.lean = self.root / 'lean'
        write(self.lean / 'Small/A.lean', A_SOURCE)
        write(self.lean / 'Small/B.lean', B_SOURCE)
        self.first = update_index(empty_index(), rows_a(), {}, self.lean, 1)
        self.both = update_index(self.first, rows_b(), {}, self.lean, 2)

    def test_the_entries_are_the_declarations_the_author_wrote(self):
        self.assertEqual(sorted(self.first['entries']),
                         ['Small.Point', 'Small.assumed', 'Small.base', 'Small.count', 'Small.lemma1', 'Small.main',
                          'Small.open_statement'])
        self.assertEqual({name: entry['kind'] for name, entry in self.first['entries'].items()},
                         {'Small.Point': 'inductive', 'Small.assumed': 'axiom', 'Small.base': 'def',
                          'Small.count': 'def', 'Small.lemma1': 'theorem', 'Small.main': 'theorem',
                          'Small.open_statement': 'theorem'})

    def test_what_an_entry_records(self):
        entry = self.first['entries']['Small.lemma1']
        expected = {'name': 'Small.lemma1', 'kind': 'theorem', 'module': 'Small.A', 'file': 'Small/A.lean',
                    'span': span_of(A_SOURCE, LEMMA1), 'source_sha': sha256_text(LEMMA1),
                    'statement': 'Small.lemma1 : statement', 'statement_hash': 'hash-of-Small.lemma1', 'prop': True,
                    'statement_uses': ['Small.base'], 'uses': [], 'library': ['Nat.zero_eq'], 'lean_proof': 'complete'}
        self.assertEqual({key: entry[key] for key in expected}, expected)
        self.assertEqual(entry['axioms'], [])
        self.assertFalse(self.first['entries']['Small.base']['prop'])

    def test_the_axioms_of_an_entry_are_those_lean_collected_for_its_declaration(self):
        # They are stored as the row gives them. Nothing is added from the auxiliaries folded into the entry or
        # from the entries it uses, and nothing is taken away: Lean's list already runs through all of them.
        entries = self.first['entries']
        self.assertEqual(entries['Small.main']['axioms'], ['Classical.choice', 'propext', 'sorryAx'])
        self.assertEqual(entries['Small.open_statement']['axioms'], ['sorryAx'])
        self.assertEqual(entries['Small.assumed']['axioms'], ['Small.assumed'])
        self.assertEqual(entries['Small.count']['axioms'], [])
        # A theorem whose own proof is complete and that names an open statement: Lean reports `sorryAx` for
        # it, so it is not formal, and its own proof is complete all the same.
        write(self.lean / 'Small/C.lean', 'theorem above : count 1 = 1 := by\n  exact open_statement\n')
        rows = [row('Small.above', module='Small.C', span=[1, 0, 2, 22], type_uses=['Small.count'],
                    value_uses=['Small.open_statement'], collected=['sorryAx'])]
        above = update_index(self.first, rows, {}, self.lean, 2)['entries']['Small.above']
        self.assertEqual((above['axioms'], above['lean_proof'], above['uses']),
                         (['sorryAx'], 'complete', ['Small.open_statement']))

    def test_the_source_identity_is_that_of_the_declaration_text(self):
        for name, snippet in (('Small.base', BASE), ('Small.count', COUNT), ('Small.Point', POINT), ('Small.main', MAIN)):
            with self.subTest(name):
                entry = self.first['entries'][name]
                self.assertEqual(entry['source_sha'], sha256_text(snippet))
                self.assertEqual(declaration_text(A_SOURCE, entry['span']), snippet)

    def test_the_revision_is_the_one_given(self):
        self.assertEqual((self.first['revision'], self.both['revision']), (1, 2))

    def test_an_auxiliary_declaration_is_folded_into_its_entry(self):
        aux = self.first['aux']
        for name in ('Small.Point.mk', 'Small.Point.x', 'Small.Point.y', 'Small.Point.rec'):
            self.assertEqual(aux[name], 'Small.Point', name)
        self.assertEqual(aux['Small.count.eq_1'], 'Small.count')
        self.assertEqual(aux['Small.main._proof_1'], 'Small.main')
        for name in aux:
            self.assertNotIn(name, self.first['entries'])

    def test_what_an_auxiliary_uses_counts_as_used_by_its_entry(self):
        # `main._proof_1` belongs to `main` and names a field of `Point`, which belongs to `Point`.
        main = self.first['entries']['Small.main']
        self.assertIn('Small.Point', main['uses'])
        self.assertIn('Nat.succ_le_of_lt', main['library'])

    def test_a_use_of_an_auxiliary_of_another_entry_is_a_use_of_that_entry(self):
        field = self.both['entries']['Small.uses_field']
        self.assertEqual(field['statement_uses'], ['Small.Point'])
        self.assertEqual(field['uses'], ['Small.count'])

    def test_a_private_helper_is_no_entry_and_is_replaced_by_what_it_uses(self):
        self.assertNotIn(PRIVATE_HELPER, self.first['entries'])
        self.assertNotIn('Small.helper', self.first['entries'])
        self.assertIsNone(self.first['aux'][PRIVATE_HELPER])
        main = self.first['entries']['Small.main']
        # The helper's statement speaks of `count` and its proof names `lemma1`.
        self.assertEqual(main['uses'], ['Small.Point', 'Small.count', 'Small.lemma1'])
        self.assertEqual(main['library'], ['Nat.add_comm', 'Nat.le_refl', 'Nat.succ_le_of_lt'])

    def test_statement_uses_and_proof_uses_are_recorded_separately(self):
        entries = self.both['entries']
        self.assertEqual(entries['Small.main']['statement_uses'], ['Small.base'])
        self.assertNotIn('Small.base', entries['Small.main']['uses'])
        self.assertEqual((entries['Small.doomed']['statement_uses'], entries['Small.doomed']['uses']),
                         (['Small.base'], ['Small.lemma1']))
        self.assertEqual((entries['Small.open_statement']['statement_uses'], entries['Small.open_statement']['uses']),
                         (['Small.count'], []))

    def test_whether_the_lean_proof_is_complete(self):
        entries = self.first['entries']
        self.assertEqual(entries['Small.lemma1']['lean_proof'], 'complete')
        self.assertEqual(entries['Small.count']['lean_proof'], 'complete')
        self.assertEqual(entries['Small.open_statement']['lean_proof'], 'sorry')
        self.assertEqual(entries['Small.main']['lean_proof'], 'sorry')  # through the private helper only
        self.assertFalse(next(r for r in rows_a() if r['name'] == 'Small.main')['sorry'])
        self.assertIsNone(entries['Small.Point']['lean_proof'])

    def test_sorry_in_a_definition_and_in_an_opaque_constant(self):
        write(self.lean / 'Small/C.lean', 'def partial : Nat := sorry\nopaque hidden : Nat\n')
        rows = [row('Small.partial', 'def', 'Small.C', [1, 0, 1, 26], sorry=True, collected=['sorryAx']),
                row('Small.hidden', 'opaque', 'Small.C', [2, 0, 2, 19])]
        entries = update_index(empty_index(), rows, {}, self.lean, 1)['entries']
        self.assertEqual((entries['Small.partial']['lean_proof'], entries['Small.hidden']['lean_proof']), ('sorry', 'complete'))

    def test_a_reference_to_itself_is_not_a_use(self):
        entries = self.first['entries']
        self.assertEqual(entries['Small.count']['uses'], ['Small.base'])  # the recursion names `count`
        self.assertEqual(entries['Small.Point']['uses'], [])  # the constructor's type names `Point`
        self.assertEqual(entries['Small.Point']['statement_uses'], [])

    def test_a_declaration_named_under_an_entry_and_written_elsewhere_is_an_entry(self):
        # `theorem base.zero` extends the name of `base` and has its own place in the source.
        write(self.lean / 'Small/C.lean', 'theorem base.zero : base = 0 := by\n  rfl\n')
        rows = [row('Small.base.zero', module='Small.C', span=[1, 0, 2, 5], type_uses=['Small.base'])]
        index = update_index(self.first, rows, {}, self.lean, 2)
        self.assertEqual(index['entries']['Small.base.zero']['statement_uses'], ['Small.base'])
        self.assertNotIn('Small.base.zero', index['aux'])
        # In the module of `count` as well, as long as it does not lie inside the declaration of `count`.
        rows = rows_a() + [row('Small.count.zero', span=span_of(A_SOURCE, OPEN), type_uses=['Small.count'])]
        self.assertIn('Small.count.zero', update_index(empty_index(), rows, {}, self.lean, 1)['entries'])

    def test_a_private_helper_named_under_an_entry_of_another_module_leaves_its_sorry_with_what_names_it(self):
        # `private theorem base.aux … := by sorry` in a later module: its name extends the entry `base`,
        # which stands in another module, so the helper belongs to no entry. The theorem that names it has
        # no proof of its own that is complete.
        source = ('private theorem base.aux : base = 0 := by sorry\n\n'
                  'theorem depends : base = 0 := by\n  have h := base.aux\n  exact h\n')
        write(self.lean / 'Small/C.lean', source)
        helper = '_private.Small.C.0.Small.base.aux'
        rows = [row(helper, module='Small.C', span=[1, 0, 1, 47], user='Small.base.aux', private=True,
                    type_uses=['Small.base'], sorry=True, collected=['sorryAx']),
                row('Small.depends', module='Small.C', span=[3, 0, 5, 9], type_uses=['Small.base'], value_uses=[helper],
                    collected=['sorryAx'])]
        index = update_index(self.first, rows, {}, self.lean, 2)
        self.assertNotIn(helper, index['entries'])
        depends = index['entries']['Small.depends']
        self.assertEqual((depends['lean_proof'], depends['axioms']), ('sorry', ['sorryAx']))

    def test_a_private_helper_named_under_an_entry_of_its_own_module_belongs_to_that_entry(self):
        # `private theorem first.aux … := by sorry` beside `first` in the same module: its name extends the
        # entry `first`, so it belongs to `first`. A theorem of that module that names the helper uses
        # `first`, and the helper's `sorry` makes the proof of `first` incomplete, not that of the theorem.
        first_text = 'theorem first : base = 0 := by\n  rfl'
        aux_text = 'private theorem first.aux : count 0 = 0 := by\n  sorry'
        second_text = 'theorem second : base = 0 := by\n  have h := first.aux\n  exact lemma1'
        source = '\n\n'.join([first_text, aux_text, second_text]) + '\n'
        write(self.lean / 'Small/C.lean', source)
        helper = '_private.Small.C.0.Small.first.aux'
        rows = [row('Small.first', module='Small.C', span=span_of(source, first_text), type_uses=['Small.base']),
                row(helper, module='Small.C', span=span_of(source, aux_text), user='Small.first.aux', private=True,
                    type_uses=['Small.count'], library=['Nat.add_comm'], sorry=True, collected=['sorryAx']),
                row('Small.second', module='Small.C', span=span_of(source, second_text), type_uses=['Small.base'],
                    value_uses=[helper, 'Small.lemma1'], collected=['sorryAx'])]
        index = update_index(self.first, rows, {}, self.lean, 2)
        entries = index['entries']
        self.assertNotIn(helper, entries)
        self.assertEqual(index['aux'][helper], 'Small.first')
        # The use of the helper is a use of the entry it belongs to.
        self.assertEqual(entries['Small.second']['uses'], ['Small.first', 'Small.lemma1'])
        # What the helper uses is the entry's own, and so is its `sorry`. The axioms of `first` are what
        # Lean collected for `first` itself, whose own term does not reach the helper.
        first = entries['Small.first']
        self.assertEqual((first['axioms'], first['uses'], first['library'], first['lean_proof']),
                         ([], ['Small.count'], ['Nat.add_comm'], 'sorry'))
        # The theorem that names the helper has no sorry of its own; Lean reports the helper's for it.
        second = entries['Small.second']
        self.assertEqual((second['axioms'], second['lean_proof']), (['sorryAx'], 'complete'))
        # Neither is proved in Lean from the allowed axioms: `first` for the open proof that counts as its
        # own, `second` by Lean's list.
        self.assertEqual((beyond_allowed(first, ['propext']), beyond_allowed(second, ['propext'])),
                         (['sorryAx'], ['sorryAx']))

    def test_what_keeps_an_entry_from_being_proved_from_the_allowed_axioms(self):
        allowed = ['propext', 'Classical.choice', 'Quot.sound']
        entries = self.first['entries']
        self.assertEqual(beyond_allowed(entries['Small.lemma1'], allowed), [])
        self.assertEqual(beyond_allowed(entries['Small.main'], allowed), ['sorryAx'])
        self.assertEqual(beyond_allowed(entries['Small.main'], []), ['Classical.choice', 'propext', 'sorryAx'])
        self.assertEqual(beyond_allowed(entries['Small.assumed'], allowed), ['Small.assumed'])

    def test_an_axiom_that_is_no_entry_is_named_among_the_hidden_declarations(self):
        # `private axiom shortcut` is no entry. Lean reports it for the theorem that rests on it and for a
        # theorem that names that theorem, so neither is proved from the allowed axioms although both proofs
        # are complete. The index names the axiom under `hidden`, where the check of a candidate finds it.
        axiom_text = 'private axiom shortcut : base = 1'
        rests_text = 'theorem rests : base = 1 := by\n  exact shortcut'
        further_text = 'theorem further : base = 1 := by\n  exact rests'
        source = '\n\n'.join([axiom_text, rests_text, further_text]) + '\n'
        write(self.lean / 'Small/C.lean', source)
        shortcut = '_private.Small.C.0.Small.shortcut'
        rows = [row(shortcut, 'axiom', module='Small.C', span=span_of(source, axiom_text), user='Small.shortcut',
                    private=True, type_uses=['Small.base'], collected=[shortcut]),
                row('Small.rests', module='Small.C', span=span_of(source, rests_text), type_uses=['Small.base'],
                    value_uses=[shortcut], collected=[shortcut]),
                row('Small.further', module='Small.C', span=span_of(source, further_text), type_uses=['Small.base'],
                    value_uses=['Small.rests'], collected=[shortcut])]
        index = update_index(self.first, rows, {}, self.lean, 2)
        self.assertNotIn(shortcut, index['entries'])
        rests, further = index['entries']['Small.rests'], index['entries']['Small.further']
        self.assertEqual((rests['axioms'], rests['lean_proof']), ([shortcut], 'complete'))
        self.assertEqual((further['axioms'], further['lean_proof']), ([shortcut], 'complete'))
        self.assertEqual({key: index['hidden'][shortcut][key] for key in ('module', 'user', 'axiom', 'generated')},
                         {'module': 'Small.C', 'user': 'Small.shortcut', 'axiom': True, 'generated': False})

    def test_an_axiom_that_lean_generates_under_an_entry_belongs_to_that_entry(self):
        # `native_decide` adds an axiom for each computation. Lean 4.36 names it under the declaration that
        # uses it, as a private and internal name. It belongs to that entry, and Lean reports it for the
        # entry and for what names the entry.
        computed_text = 'theorem computed : count 3 = 3 := by\n  native_decide'
        from_it_text = 'theorem from_it : count 3 = 3 := by\n  exact computed'
        source = computed_text + '\n\n' + from_it_text + '\n'
        write(self.lean / 'Small/C.lean', source)
        generated = '_private.Small.C.0.Small.computed._native.native_decide.ax_1_1'
        rows = [row('Small.computed', module='Small.C', span=span_of(source, computed_text), type_uses=['Small.count'],
                    value_uses=[generated], collected=[generated]),
                row(generated, 'axiom', module='Small.C', span=span_of(source, computed_text), private=True, internal=True,
                    user='Small.computed._native.native_decide.ax_1_1', type_uses=['Small.count'], collected=[generated]),
                row('Small.from_it', module='Small.C', span=span_of(source, from_it_text), type_uses=['Small.count'],
                    value_uses=['Small.computed'], collected=[generated])]
        index = update_index(self.first, rows, {}, self.lean, 2)
        self.assertEqual(index['aux'][generated], 'Small.computed')
        computed = index['entries']['Small.computed']
        self.assertEqual((computed['axioms'], computed['lean_proof']), ([generated], 'complete'))
        self.assertEqual(index['entries']['Small.from_it']['axioms'], [generated])
        self.assertEqual((index['hidden'][generated]['axiom'], index['hidden'][generated]['generated']), (True, True))

    def test_an_auxiliary_of_no_entry_is_passed_through_from_a_module_extracted_later(self):
        # `theorem _aid.step … := by sorry` has an internal name, so it is no entry and belongs to none. A
        # theorem of a module extracted later names it. The proof of that theorem is not complete and uses
        # `lemma1` through the auxiliary, although the row of the auxiliary is not among the rows of that extraction.
        aid_text = 'theorem _aid.step : count 0 = 0 := by\n  have h := lemma1\n  sorry'
        write(self.lean / 'Small/C.lean', aid_text + '\n')
        rows = [row('Small._aid.step', module='Small.C', span=span_of(aid_text, aid_text), internal=True,
                    type_uses=['Small.count'], value_uses=['Small.lemma1'], library=['Nat.add_comm'], sorry=True,
                    collected=['sorryAx'])]
        with_aid = update_index(self.first, rows, {}, self.lean, 2)
        self.assertEqual({key: with_aid['hidden']['Small._aid.step'][key] for key in ('module', 'uses', 'sorry', 'library')},
                         {'module': 'Small.C', 'uses': ['Small.count', 'Small.lemma1'], 'sorry': True,
                          'library': ['Nat.add_comm']})
        later_text = 'theorem later : count 0 = 0 := by\n  exact _aid.step'
        write(self.lean / 'Small/D.lean', later_text + '\n')
        rows = [row('Small.later', module='Small.D', span=span_of(later_text, later_text), type_uses=['Small.count'],
                    value_uses=['Small._aid.step'], collected=['sorryAx'])]
        index = update_index(with_aid, rows, {}, self.lean, 3)
        later = index['entries']['Small.later']
        self.assertEqual((later['uses'], later['axioms'], later['library'], later['lean_proof']),
                         (['Small.count', 'Small.lemma1'], ['sorryAx'], ['Nat.add_comm'], 'sorry'))
        # The auxiliary stays known until its own module is extracted again or removed.
        self.assertIn('Small._aid.step', index['hidden'])
        self.assertNotIn('Small._aid.step', drop_modules(index, ['Small.C'])['hidden'])

    def test_extracting_one_module_again_replaces_its_entries_and_keeps_the_others(self):
        write(self.lean / 'Small/B.lean', B_LATER)
        later = update_index(self.both, rows_b(B_LATER), {}, self.lean, 3)
        self.assertEqual(later['revision'], 3)
        self.assertEqual(sorted(name for name, entry in later['entries'].items() if entry['module'] == 'Small.B'),
                         ['Small.fresh', 'Small.uses_field'])
        self.assertNotIn('Small.doomed', later['entries'])
        for name, entry in self.first['entries'].items():
            self.assertEqual(later['entries'][name], entry, name)
        # The lines of `uses_field` moved and its text did not change.
        before, after = self.both['entries']['Small.uses_field'], later['entries']['Small.uses_field']
        self.assertNotEqual(after['span'], before['span'])
        self.assertEqual(after['span'], span_of(B_LATER, USES_FIELD))
        self.assertEqual(after['source_sha'], before['source_sha'])
        self.assertEqual(later['entries']['Small.fresh']['uses'], ['Small.lemma1'])
        self.assertEqual(later['aux'], self.both['aux'])

    def test_auxiliaries_of_a_declaration_that_is_gone_are_dropped(self):
        write(self.lean / 'Small/B.lean', B_SOURCE)
        rows = rows_b() + [row('Small.doomed._proof_1', module='Small.B', internal=True)]
        index = update_index(self.first, rows, {}, self.lean, 2)
        self.assertEqual(index['aux']['Small.doomed._proof_1'], 'Small.doomed')
        write(self.lean / 'Small/B.lean', B_LATER)
        later = update_index(index, rows_b(B_LATER), {}, self.lean, 3)
        self.assertNotIn('Small.doomed._proof_1', later['aux'])

    def test_the_result_does_not_depend_on_extracting_together_or_in_turn(self):
        together = update_index(empty_index(), rows_a() + rows_b(), {}, self.lean, 2)
        self.assertEqual(together, self.both)

    def test_pairs_are_merged(self):
        index = update_index(empty_index(), rows_a(), {'same|Small.main|Small.lemma1': True}, self.lean, 1)
        self.assertEqual(index['pairs'], {'same|Small.main|Small.lemma1': True})
        later = update_index(index, rows_b(), {'negation|Small.doomed|Small.main': False,
                                               'same|Small.main|Small.lemma1': False}, self.lean, 2)
        self.assertEqual(later['pairs'], {'same|Small.main|Small.lemma1': False, 'negation|Small.doomed|Small.main': False})

    def test_the_modules_table_has_the_file_and_its_identity(self):
        digest = lambda relative: hashlib.sha256((self.lean / relative).read_bytes()).hexdigest()
        self.assertEqual(self.first['modules'], {'Small.A': {'file': 'Small/A.lean', 'sha256': digest('Small/A.lean')}})
        self.assertEqual(self.both['modules'], {'Small.A': {'file': 'Small/A.lean', 'sha256': digest('Small/A.lean')},
                                                'Small.B': {'file': 'Small/B.lean', 'sha256': digest('Small/B.lean')}})
        write(self.lean / 'Small/B.lean', B_LATER)
        later = update_index(self.both, rows_b(B_LATER), {}, self.lean, 3)
        self.assertEqual(later['modules']['Small.B']['sha256'], digest('Small/B.lean'))
        self.assertEqual(later['modules']['Small.A'], self.both['modules']['Small.A'])

    def test_the_index_given_is_not_changed(self):
        before = copy.deepcopy(self.first)
        update_index(self.first, rows_b(), {'same|a|b': True}, self.lean, 2)
        self.assertEqual(self.first, before)

    def test_drop_modules(self):
        dropped = drop_modules(self.both, ['Small.B'])
        self.assertEqual(dropped['entries'], self.first['entries'])
        self.assertEqual(dropped['modules'], self.first['modules'])
        self.assertEqual(dropped['revision'], self.both['revision'])
        without_a = drop_modules(self.both, ['Small.A'])
        self.assertEqual(sorted(without_a['entries']), ['Small.doomed', 'Small.uses_field'])
        self.assertEqual(sorted(without_a['modules']), ['Small.B'])
        # What belonged to an entry of the dropped module goes with it.
        self.assertEqual({name for name, parent in without_a['aux'].items() if parent is not None}, set())
        self.assertEqual(drop_modules(self.both, []), self.both)


def entry(name, kind='theorem', uses=(), statement_uses=(), axioms=(), proof='complete', source=None, prop=None):
    """An entry of the structural index, written by hand."""
    return {'name': name, 'kind': kind, 'module': 'Small.M', 'file': 'Small/M.lean', 'span': [1, 0, 2, 0],
            'source_sha': source or 'source-of-' + name, 'statement': name + ' : statement',
            'statement_hash': 'statement-of-' + name, 'prop': kind == 'theorem' if prop is None else prop,
            'statement_uses': list(statement_uses), 'uses': list(uses), 'library': [], 'axioms': list(axioms),
            'lean_proof': proof if kind in ('theorem', 'def', 'opaque') else None}


def index_of(*entries):
    return {'revision': 1, 'modules': {}, 'entries': {e['name']: e for e in entries}, 'aux': {}, 'pairs': {}}


def earlier(*entries, hidden=None, judged=None):
    """An index as the code wrote it before the extraction asked Lean for the axioms: each entry carries
    `direct_axioms`, the axioms it reaches without passing through another entry."""
    index = index_of(*({**{key: value for key, value in e.items() if key != 'axioms'}, 'direct_axioms': e['axioms']}
                       for e in entries))
    return {**index, 'hidden': hidden or {}, 'judged': judged or {}}


class EarlierIndexTests(TempCase):
    """An index file written by the earlier code is read in the present form (canon.read_index)."""

    def read(self, index):
        write(self.root / 'index.json', json.dumps(index))
        return read_index(self.root / 'index.json')

    def axioms(self, index):
        return {name: entry['axioms'] for name, entry in self.read(index)['entries'].items()}

    def test_the_axioms_of_an_entry_are_those_of_everything_it_uses(self):
        index = earlier(
            entry('S.object', 'def', axioms=['Quot.sound']),
            entry('S.plain', 'def'),
            entry('S.first', axioms=['propext'], statement_uses=['S.plain']),
            entry('S.second', uses=['S.first'], axioms=['sorryAx'], proof='sorry'),
            entry('S.third', uses=['S.second'], statement_uses=['S.plain'], axioms=['Classical.choice']),
            entry('S.about', statement_uses=['S.object']))
        self.assertEqual(self.axioms(index), {
            'S.object': ['Quot.sound'], 'S.plain': [], 'S.first': ['propext'], 'S.second': ['propext', 'sorryAx'],
            'S.third': ['Classical.choice', 'propext', 'sorryAx'],
            'S.about': ['Quot.sound']})  # through what its statement uses

    def test_an_axiom_of_the_canon_counts_as_itself(self):
        index = earlier(entry('S.assumed', 'axiom'), entry('S.from_it', uses=['S.assumed'], axioms=['propext']),
                        entry('S.further', uses=['S.from_it']))
        self.assertEqual(self.axioms(index), {'S.assumed': ['S.assumed'], 'S.from_it': ['S.assumed', 'propext'],
                                              'S.further': ['S.assumed', 'propext']})

    def test_a_name_that_is_no_entry_adds_nothing(self):
        self.assertEqual(self.axioms(earlier(entry('S.a', uses=['Nat.add_comm'], axioms=['propext']))), {'S.a': ['propext']})

    def test_entries_that_use_one_another_have_the_axioms_of_all_they_use(self):
        index = earlier(entry('S.a', uses=['S.b']), entry('S.b', uses=['S.c']), entry('S.c', uses=['S.a', 'S.c']))
        self.assertEqual(self.axioms(index), {'S.a': [], 'S.b': [], 'S.c': []})
        index = earlier(entry('S.a', uses=['S.b'], axioms=['propext']), entry('S.b', uses=['S.a'], axioms=['sorryAx']),
                        entry('S.c', uses=['S.b']))
        self.assertEqual(self.axioms(index), {name: ['propext', 'sorryAx'] for name in ('S.a', 'S.b', 'S.c')})

    def test_the_rest_of_the_index_takes_the_present_form(self):
        aid = {'module': 'S.M', 'user': 'S._aid', 'axiom': False, 'generated': True, 'uses': ['S.a'],
               'axioms': ['sorryAx'], 'library': ['Nat.add_comm']}
        index = earlier(entry('S.a', axioms=['propext']), hidden={'S._aid': aid, 'S._other': {**aid, 'axioms': []}},
                        judged={'S.a': 3})
        read = self.read(index)
        self.assertEqual(sorted(read), ['aux', 'entries', 'hidden', 'modules', 'pairs', 'revision'])
        self.assertEqual(read['entries']['S.a'], entry('S.a', axioms=['propext']))
        self.assertEqual(read['hidden']['S._aid'], {'module': 'S.M', 'user': 'S._aid', 'axiom': False, 'generated': True,
                                                    'uses': ['S.a'], 'library': ['Nat.add_comm'], 'sorry': True})
        self.assertFalse(read['hidden']['S._other']['sorry'])

    def test_an_index_in_the_present_form_is_read_as_it_is(self):
        index = {**index_of(entry('S.a', axioms=['propext']), entry('S.b', uses=['S.a'])), 'hidden': {}}
        self.assertEqual(self.read(index), index)  # the axioms of S.b are Lean's and nothing is added to them

    def test_an_extraction_carries_an_earlier_index_on_in_the_present_form(self):
        lean = self.root / 'lean'
        write(lean / 'Small/A.lean', A_SOURCE)
        write(lean / 'Small/B.lean', B_SOURCE)
        first = update_index(empty_index(), rows_a(), {}, lean, 1)
        old = earlier_form(first)
        both = update_index(self.read(old), rows_b(), {}, lean, 2)
        self.assertEqual(both, update_index(first, rows_b(), {}, lean, 2))


class StatementDifferenceTests(unittest.TestCase):
    """Whether a statement, with every definition under it, is the same in two indexes (canon.statement_differences)."""

    def setUp(self):
        self.first = index_of(
            entry('S.base', 'def'), entry('S.shape', 'inductive'),
            entry('S.object', 'def', uses=['S.base', 'S.exists'], statement_uses=['S.shape']),
            entry('S.exists', statement_uses=['S.base'], uses=['S.lemma'], proof='sorry'),
            entry('S.lemma', proof='sorry'),
            entry('S.root', statement_uses=['S.object'], uses=['S.lemma'], proof='sorry'),
            entry('S.aside', 'def'))
        self.now = copy.deepcopy(self.first)

    def differences(self):
        return statement_differences(self.first, self.now, 'S.root')

    def test_a_canon_that_only_gained_proofs_states_the_same_root(self):
        self.now['entries']['S.root'].update(lean_proof='complete', source_sha='another proof', uses=['S.new'])
        self.now['entries']['S.exists'].update(lean_proof='complete', source_sha='another proof', uses=[])
        self.now['entries']['S.new'] = entry('S.new')
        self.assertEqual(self.differences(), [])

    def test_what_the_statement_does_not_reach_may_differ(self):
        self.now['entries']['S.aside'].update(source_sha='rewritten', statement_hash='restated')
        self.now['entries']['S.lemma'].update(statement_hash='restated')  # named by proofs only
        self.assertEqual(self.differences(), [])

    def test_a_changed_statement_of_the_root(self):
        self.now['entries']['S.root']['statement_hash'] = 'restated'
        self.assertEqual(self.differences(), ['the statement of S.root is not the statement the first commit has'])

    def test_a_changed_definition_under_the_statement(self):
        for name in ('S.object', 'S.base', 'S.shape'):  # named by the statement, by a body, by a type
            with self.subTest(name):
                self.now = copy.deepcopy(self.first)
                self.now['entries'][name]['source_sha'] = 'rewritten'
                self.assertEqual(self.differences(), [f'the text of the definition {name} is not the text the first commit has'])

    def test_a_changed_statement_of_a_theorem_that_a_definition_names(self):
        self.now['entries']['S.exists']['statement_hash'] = 'restated'
        self.assertEqual(self.differences(), ['the statement of S.exists is not the statement the first commit has'])

    def test_a_declaration_under_the_statement_that_is_in_one_canon_only(self):
        del self.now['entries']['S.base']
        self.assertEqual(self.differences(), ['S.base is under the statement and is not in the canon as it stands'])
        self.now = copy.deepcopy(self.first)
        self.now['entries']['S.object']['uses'].append('S.instance')
        self.now['entries']['S.instance'] = entry('S.instance', 'def')
        self.assertEqual(self.differences(), ['S.instance is under the statement and is not in the canon of the first commit'])

    def test_a_changed_kind(self):
        self.now['entries']['S.base']['kind'] = 'opaque'
        self.assertEqual(self.differences(), ['S.base was declared as def and is now declared as opaque'])

    def test_an_index_of_the_earlier_code_is_compared_as_it_is(self):
        first = earlier(*self.first['entries'].values())
        self.assertEqual(statement_differences(first, self.now, 'S.root'), [])
        self.now['entries']['S.base']['source_sha'] = 'rewritten'
        self.assertEqual(statement_differences(first, self.now, 'S.root'),
                         ['the text of the definition S.base is not the text the first commit has'])


# --------------------------------------------------------------------------------------- the machine checks

ALLOWED = ['propext', 'Classical.choice', 'Quot.sound']
ODD_SUM_RECORD = record_text('The sum of the first n odd numbers, defined by recursion on n.', weight='unit')
UNTOUCHED = ('the record changes the written proof, "proves" or "refutes" of an element whose proof the candidate '
             'does not replace')


class CheckAppliedTests(unittest.TestCase):
    """Each refusal starts from one candidate that passes: it adds `Small.step` and replaces the proof of `Small.root`."""

    def setUp(self):
        self.old = index_of(entry('Small.oddSum', 'def'),
                            entry('Small.root', statement_uses=['Small.oddSum'], axioms=['sorryAx'], proof='sorry'))
        self.new = index_of(entry('Small.oddSum', 'def'),
                            entry('Small.step', statement_uses=['Small.oddSum']),
                            entry('Small.root', uses=['Small.step'], statement_uses=['Small.oddSum'], axioms=['sorryAx'],
                                  proof='sorry', source='second-source-of-Small.root'))
        self.change = {'replace': [{'declaration': 'Small.root', 'file': 'replace/root.lean', 'imports': []}], 'retire': []}
        self.records = {'Small/step': parse_record(STEP_RECORD), 'Small/root': parse_record(ROOT_RECORD)}
        # The records the canon has, as canon.read_record gives them.
        self.existing = {'Small.oddSum': parse_record(ODD_SUM_RECORD), 'Small.root': parse_record(OLD_ROOT_RECORD)}

    def check(self, organizer=False, in_place=()):
        # A declaration the candidate adds stands in a module of the candidate's own, unless a test
        # names it as one written into a module the canon already has.
        for name, item in self.new['entries'].items():
            if name not in self.old['entries'] and name not in in_place:
                item.update(module='Small.New', file='Small/New.lean')
        return check_applied(self.old, self.new, self.change, self.records, lambda name: self.existing.get(name),
                             ALLOWED, organizer=organizer)

    def test_a_declaration_added_to_a_module_the_canon_has(self):
        errors = self.check(in_place=('Small.step',))['errors']
        self.assertEqual(len(errors), 1, errors)
        self.assertRegex(errors[0], 'Small.step is declared in Small.M, a module the canon already has; '
                                    'a new declaration goes in a new module')

    def test_an_added_name_that_differs_from_another_only_in_case(self):
        self.add(entry('Small.Step'))
        self.records['Small/Step'] = parse_record(STEP_RECORD)
        errors = self.check()['errors']
        self.assertEqual(len(errors), 1, errors)
        self.assertRegex(errors[0], 'the names Small.Step, Small.step differ only in the case of their letters')

    def refused(self, message, organizer=False):
        errors = self.check(organizer)['errors']
        self.assertEqual(len(errors), 1, errors)
        self.assertRegex(errors[0], message)

    def add(self, *entries):
        for item in entries:
            self.new['entries'][item['name']] = item

    def test_a_clean_candidate(self):
        self.assertEqual(self.check(), {'added': ['Small.step'], 'replaced': ['Small.root'],
                                        'records': ['Small.root', 'Small.step'], 'errors': [], 'retired': []})

    def test_a_candidate_that_changes_nothing(self):
        self.assertEqual(check_applied(self.old, self.old, {'replace': [], 'retire': []}, {}, lambda name: True, ALLOWED),
                         {'added': [], 'replaced': [], 'records': [], 'errors': [], 'retired': []})

    def test_a_statement_changed_in_place(self):
        self.new['entries']['Small.root']['statement_hash'] = 'another statement'
        self.refused('the statement of Small.root changed in place; a different statement enters under a new name')

    def test_a_statement_changed_in_place_without_a_replacement(self):
        self.new['entries']['Small.oddSum'].update(statement_hash='another statement', source_sha='edited')
        self.refused('the statement of Small.oddSum changed in place')

    def test_a_statement_that_elaborates_differently_although_its_text_is_unchanged(self):
        # The candidate did not touch the declaration. Something it brought into the scope of the declaration's
        # module made Lean read the same text otherwise, which shows when that module is extracted again.
        self.new['entries']['Small.oddSum']['statement_hash'] = 'another statement'
        self.refused('the statement of Small.oddSum elaborates differently with this change although its text is unchanged')

    def test_a_changed_kind(self):
        self.new['entries']['Small.oddSum']['kind'] = 'opaque'
        self.refused('the statement of Small.oddSum changed in place')

    def test_a_source_changed_without_a_replacement(self):
        self.new['entries']['Small.oddSum']['source_sha'] = 'edited'
        self.refused('the source of Small.oddSum changed although the candidate does not replace it')

    def test_a_definition_replaced_in_place(self):
        self.change['replace'].append({'declaration': 'Small.oddSum', 'file': 'replace/oddSum.lean', 'imports': []})
        self.new['entries']['Small.oddSum']['source_sha'] = 'edited'
        result = self.check()
        self.assertEqual(len(result['errors']), 1, result['errors'])
        self.assertRegex(result['errors'][0], 'Small.oddSum is a definition; a definition is not replaced in place')

    def test_a_declaration_that_disappeared(self):
        del self.new['entries']['Small.oddSum']
        self.refused('declarations disappeared from the canon: Small.oddSum')

    def test_an_added_declaration_without_a_record(self):
        del self.records['Small/step']
        self.refused(r'Small.step has no record; write records/Small/step\.md')
        self.assertEqual(self.check()['added'], ['Small.step'])

    def test_the_record_of_an_added_declaration_with_an_encoded_name(self):
        self.add(entry('Small.aux'))
        self.refused(r'Small.aux has no record; write records/Small/aux%\.md')
        self.records['Small/aux%'] = parse_record(STEP_RECORD)
        self.assertEqual(self.check()['errors'], [])
        self.assertIn('Small.aux', self.check()['records'])

    def test_a_record_that_belongs_to_no_declaration(self):
        self.records['Small/ghost'] = parse_record(STEP_RECORD)
        self.refused(r'records/Small/ghost\.md belongs to no declaration of the canon')

    def test_a_record_for_a_declaration_the_candidate_does_not_touch(self):
        # A record can be replaced by itself (design 4.4).
        self.records['Small/oddSum'] = parse_record(record_text('The sum of the first n odd numbers.', weight='unit'))
        result = self.check()
        self.assertEqual((result['errors'], result['records']), ([], ['Small.oddSum', 'Small.root', 'Small.step']))

    def untouched_base(self):
        """The canon already has `Small.step` with a written proof; the candidate replaces the root only."""
        self.old['entries']['Small.step'] = copy.deepcopy(self.new['entries']['Small.step'])
        self.existing['Small.step'] = parse_record(record_text('Passing from n to n + 1.', proof='By unfolding the sum.'))
        self.records['Small/step'] = copy.deepcopy(self.existing['Small.step'])

    def test_the_record_of_an_untouched_element_may_change_outside_its_proof(self):
        self.untouched_base()
        self.assertEqual(self.check()['errors'], [])
        self.records['Small/step'] = parse_record(
            record_text('Passing from n to n + 1 adds 2n + 1.', weight='unit', short='next odd number', source='knuth1997',
                        statement='For every n, the next sum is the sum plus 2n + 1.', proof='\nBy unfolding the sum.\n')
            + '\n## Explanation\n\nThe recursion of the definition, read as a statement.\n')
        result = self.check()
        self.assertEqual((result['errors'], result['added'], result['records']), ([], [], ['Small.root', 'Small.step']))

    def test_the_record_of_an_untouched_element_may_not_change_its_written_proof(self):
        self.untouched_base()
        self.records['Small/step'] = parse_record(record_text('Passing from n to n + 1.', proof='By induction instead.'))
        self.refused('Small.step: ' + UNTOUCHED + '; list the declaration in "replace"')

    def test_the_record_of_an_untouched_element_may_not_drop_or_gain_a_written_proof(self):
        self.untouched_base()
        self.records['Small/step'] = parse_record(record_text('Passing from n to n + 1.'))
        self.refused('Small.step: ' + UNTOUCHED)
        self.untouched_base()
        self.records['Small/oddSum'] = parse_record(ODD_SUM_RECORD + '\n## Proof\n\nA proof where the canon has none.\n')
        self.refused('Small.oddSum: ' + UNTOUCHED)

    def test_the_record_of_an_untouched_element_may_not_change_proves_or_refutes(self):
        for key in ('proves', 'refutes'):
            with self.subTest(key):
                self.untouched_base()
                self.records['Small/step'] = parse_record(record_text('Passing from n to n + 1.', proof='By unfolding the sum.',
                                                                      **{key: 'Small.root'}))
                # Lean confirmed the claim, so that the changed record is the candidate's only fault.
                self.new['pairs'] = {('same' if key == 'proves' else 'negation') + '|Small.step|Small.root': True}
                self.refused('Small.step: ' + UNTOUCHED)
                # The other direction: the canon's record makes the claim and the candidate's drops it.
                self.existing['Small.step'], self.records['Small/step'] = self.records['Small/step'], self.existing['Small.step']
                self.refused('Small.step: ' + UNTOUCHED)

    def test_the_record_of_a_replaced_declaration_may_change_its_written_proof(self):
        # The clean candidate itself: the canon's record of the root has no proof, the candidate's has one.
        self.assertNotIn('Proof', self.existing['Small.root']['sections'])
        self.assertIn('Proof', self.records['Small/root']['sections'])
        self.assertEqual(self.check()['errors'], [])
        self.change['replace'] = []
        self.new['entries']['Small.root'] = copy.deepcopy(self.old['entries']['Small.root'])
        self.refused('Small.root: ' + UNTOUCHED)

    def test_an_added_axiom(self):
        self.add(entry('Small.assumed', 'axiom'))
        self.records['Small/assumed'] = parse_record(STEP_RECORD)
        self.refused('Small.assumed is declared as an axiom')

    def test_an_axiom_that_is_no_element(self):
        # `private axiom shortcut` in the module the candidate adds is no entry, and it is refused as an entry is.
        shortcut = {'module': 'Small.New', 'user': 'Small.shortcut', 'axiom': True, 'generated': False,
                    'uses': [], 'library': [], 'sorry': False}
        self.new['hidden'] = {'_private.Small.New.0.Small.shortcut': shortcut}
        self.refused('Small.shortcut is declared as an axiom in Small.New; state it as a theorem')
        # One the canon already had is not this candidate's to answer for.
        self.old['hidden'] = dict(self.new['hidden'])
        self.assertEqual(self.check()['errors'], [])
        # One that Lean generated, as native_decide does, is not refused. What rests on it is not formal.
        generated = '_private.Small.New.0.Small.step._native.native_decide.ax_1_1'
        self.new['hidden'] = {generated: {**shortcut, 'user': 'Small.step._native.native_decide.ax_1_1', 'generated': True}}
        self.assertEqual(self.check()['errors'], [])
        # An auxiliary that is no axiom is never refused for being hidden.
        self.new['hidden'] = {'Small._aid.step': {**shortcut, 'user': 'Small._aid.step', 'axiom': False}}
        self.assertEqual(self.check()['errors'], [])

    def test_an_added_definition_with_sorry(self):
        for kind in ('def', 'opaque'):
            with self.subTest(kind):
                self.add(entry('Small.partial', kind, axioms=['sorryAx'], proof='sorry'))
                self.records['Small/partial'] = parse_record(STEP_RECORD)
                self.refused('the definition Small.partial contains sorry')

    def test_an_added_definition_that_is_complete(self):
        self.add(entry('Small.total', 'def'))
        self.records['Small/total'] = parse_record(STEP_RECORD)
        self.assertEqual(self.check()['errors'], [])

    def test_proves_that_names_no_declaration(self):
        self.records['Small/step'] = parse_record(record_text('Another proof.', proves='Small.absent'))
        self.refused('Small.step: "proves: Small.absent" names no declaration of the canon')

    def test_proves_that_lean_did_not_confirm(self):
        self.records['Small/step'] = parse_record(record_text('Another proof.', proves='Small.root'))
        self.refused('Small.step: Lean did not confirm that its statement is the statement of Small.root')
        self.new['pairs'] = {'same|Small.step|Small.root': False}
        self.refused('Small.step: Lean did not confirm that its statement is the statement of Small.root')
        self.new['pairs'] = {'negation|Small.step|Small.root': True, 'same|Small.root|Small.step': True}
        self.refused('Small.step: Lean did not confirm that its statement is the statement of Small.root')

    def test_proves_that_lean_confirmed(self):
        self.records['Small/step'] = parse_record(record_text('Another proof.', proves='Small.root'))
        self.new['pairs'] = {'same|Small.step|Small.root': True}
        self.assertEqual(self.check()['errors'], [])

    def test_refutes_that_lean_did_not_confirm(self):
        self.records['Small/step'] = parse_record(record_text('A counterexample.', refutes='Small.root'))
        self.refused('Small.step: Lean did not confirm that its statement is the negation of the statement of Small.root')
        self.new['pairs'] = {'same|Small.step|Small.root': True}
        self.refused('the negation of the statement of Small.root')

    def test_refutes_that_lean_confirmed(self):
        self.records['Small/step'] = parse_record(record_text('A counterexample.', refutes='Small.root'))
        self.new['pairs'] = {'negation|Small.step|Small.root': True}
        self.assertEqual(self.check()['errors'], [])

    def test_refutes_that_names_no_declaration(self):
        self.records['Small/step'] = parse_record(record_text('A counterexample.', refutes='Small.absent'))
        self.refused('Small.step: "refutes: Small.absent" names no declaration of the canon')

    def test_proves_and_refutes_relate_two_theorems(self):
        # A definition has no standing, so a claim is refused when either end of it is one, even where Lean
        # confirms the pair: a `def` can state a proposition, or its negation, as a theorem does.
        self.add(entry('Small.total', 'def'))
        for key, kind in (('proves', 'same'), ('refutes', 'negation')):
            for claimant, target, definition in (('Small.step', 'Small.oddSum', 'Small.oddSum'),
                                                 ('Small.total', 'Small.root', 'Small.total')):
                with self.subTest(key=key, claimant=claimant):
                    self.records['Small/step'] = parse_record(STEP_RECORD)
                    self.records['Small/total'] = parse_record(STEP_RECORD)
                    self.records[name_path(claimant)] = parse_record(record_text('A claim.', **{key: target}))
                    self.new['pairs'] = {f'{kind}|{claimant}|{target}': True}
                    self.refused(f'{claimant}: "{key}: {target}" relates two theorems, '
                                 f'and {definition} is declared as def')

    def test_a_replaced_declaration_without_any_record(self):
        del self.records['Small/root']
        del self.existing['Small.root']
        self.refused(r'Small.root has no record; write records/Small/root\.md')

    def test_a_replaced_declaration_keeps_the_record_the_canon_has(self):
        # A formalizer's peer replaces the proof and may leave the record as it is.
        del self.records['Small/root']
        result = self.check()
        self.assertEqual((result['errors'], result['replaced'], result['records']), ([], ['Small.root'], ['Small.step']))

    def test_a_theorem_with_sorry_whose_statement_is_no_proposition(self):
        self.add(entry('Small.step', proof='sorry', axioms=['sorryAx'], prop=False))
        self.refused('Small.step is a theorem whose statement is not a proposition')

    def test_a_peer_may_add_a_statement_without_a_lean_proof(self):
        self.add(entry('Small.step', proof='sorry', axioms=['sorryAx']))
        self.assertEqual(self.check()['errors'], [])

    # -- the organizer -------------------------------------------------------------------------------------

    def organizer_base(self):
        """An alternative proof of the root, entered earlier in a later module, that an organizer moves under the root."""
        self.old = index_of(entry('Small.oddSum', 'def'), entry('Small.step', statement_uses=['Small.oddSum']),
                            entry('Small.root', statement_uses=['Small.oddSum'], axioms=['sorryAx'], proof='sorry'),
                            entry('Small.root_alt', uses=['Small.step'], statement_uses=['Small.oddSum']))
        self.new = index_of(entry('Small.oddSum', 'def'), entry('Small.step', statement_uses=['Small.oddSum']),
                            entry('Small.root', uses=['Small.step'], statement_uses=['Small.oddSum'],
                                  source='moved-source-of-Small.root'))
        self.change = {'replace': [], 'retire': [{'alternative': 'Small.root_alt', 'into': 'Small.root',
                                                  'reason': 'The proof now stands under the statement.'}]}
        self.records = {}
        self.existing = {'Small.oddSum': parse_record(ODD_SUM_RECORD), 'Small.step': parse_record(STEP_RECORD),
                         'Small.root': parse_record(OLD_ROOT_RECORD),
                         'Small.root_alt': parse_record(record_text('Another proof of the root.', proves='Small.root',
                                                                    proof='By induction on $n$.'))}

    def test_an_organizer_adds_a_theorem_proved_from_the_allowed_axioms(self):
        self.old, self.change = copy.deepcopy(self.new), {'replace': [], 'retire': []}
        self.add(entry('Small.agree', uses=['Small.step'], axioms=['propext', 'Quot.sound']))
        self.records = {'Small/agree': parse_record(STEP_RECORD)}
        self.assertEqual(self.check(organizer=True), {'added': ['Small.agree'], 'replaced': [], 'records': ['Small.agree'],
                                                      'errors': [], 'retired': []})

    def test_an_organizer_theorem_with_sorry_is_refused(self):
        self.old, self.change = copy.deepcopy(self.new), {'replace': [], 'retire': []}
        self.add(entry('Small.agree', axioms=['sorryAx'], proof='sorry'))
        self.records = {'Small/agree': parse_record(STEP_RECORD)}
        self.refused('Small.agree is not proved in Lean from the allowed axioms: sorryAx', organizer=True)
        self.assertEqual(self.check(organizer=False)['errors'], [])  # a peer may leave a proof open

    def test_an_organizer_theorem_that_rests_on_an_open_proof_is_refused(self):
        self.old, self.change = copy.deepcopy(self.new), {'replace': [], 'retire': []}
        # Complete in itself; the root's proof ends in sorry, and Lean reports that for what names the root.
        self.add(entry('Small.agree', uses=['Small.root'], axioms=['sorryAx']))
        self.records = {'Small/agree': parse_record(STEP_RECORD)}
        self.refused('Small.agree is not proved in Lean from the allowed axioms: sorryAx', organizer=True)

    def test_an_organizer_theorem_from_another_axiom_is_refused(self):
        self.old, self.change = copy.deepcopy(self.new), {'replace': [], 'retire': []}
        self.add(entry('Small.agree', axioms=['propext', 'Lean.ofReduceBool']))
        self.records = {'Small/agree': parse_record(STEP_RECORD)}
        self.refused('Small.agree is not proved in Lean from the allowed axioms: Lean.ofReduceBool', organizer=True)

    def test_a_valid_retirement(self):
        self.organizer_base()
        self.assertEqual(self.check(organizer=True), {
            'added': [], 'replaced': [], 'records': [], 'errors': [],
            'retired': [{'alternative': 'Small.root_alt', 'into': 'Small.root'}]})

    def test_a_retirement_whose_alternative_is_still_there(self):
        self.organizer_base()
        self.add(self.old['entries']['Small.root_alt'])
        self.refused('retiring Small.root_alt into Small.root needs the first removed and the second kept', organizer=True)

    def test_a_retirement_whose_statement_is_gone(self):
        self.organizer_base()
        del self.new['entries']['Small.root']
        errors = self.check(organizer=True)['errors']
        self.assertTrue(any(re.search('retiring Small.root_alt into Small.root needs', e) for e in errors), errors)
        self.assertTrue(any(re.search('declarations disappeared from the canon: Small.root$', e) for e in errors), errors)

    def test_a_retirement_that_changed_what_the_proof_names(self):
        self.organizer_base()
        self.new['entries']['Small.root']['uses'] = []
        self.refused('after retiring Small.root_alt, the proof of Small.root does not name what the retired proof named',
                     organizer=True)

    def test_a_retirement_that_left_the_proof_open(self):
        self.organizer_base()
        self.new['entries']['Small.root'].update(lean_proof='sorry', axioms=['sorryAx'])
        errors = self.check(organizer=True)['errors']
        self.assertTrue(any(re.search('after retiring Small.root_alt, the proof of Small.root does not name what '
                                      'the retired proof named', e) for e in errors), errors)

    def test_a_retired_written_proof_needs_its_text_in_the_record_of_the_statement(self):
        # The alternative's proof was written in its record and ended in sorry in Lean. Under the
        # statement's own name it has a standing only if the statement's record carries the text.
        self.organizer_base()
        self.old['entries']['Small.root_alt'].update(lean_proof='sorry', axioms=['sorryAx'])
        self.new['entries']['Small.root'].update(lean_proof='sorry', axioms=['sorryAx'])
        self.refused('after retiring Small.root_alt, the record of Small.root needs the written proof that stood '
                     'in the record of the retired declaration', organizer=True)
        self.records['Small/root'] = parse_record(ROOT_RECORD)
        self.assertIn('## Proof', ROOT_RECORD)
        self.assertEqual(self.check(organizer=True)['errors'], [])

    def test_a_retirement_of_a_proof_that_named_the_statement(self):
        # The alternative derived the statement through the statement's own declaration and a step; under the
        # statement's name the proof names the step alone.
        self.organizer_base()
        self.old['entries']['Small.root_alt']['uses'] = ['Small.root', 'Small.step']
        self.assertEqual(self.check(organizer=True)['errors'], [])

    def test_a_retirement_of_a_proof_that_named_another_retired_declaration(self):
        # Two alternatives are retired by one change, and the proof of the first named the second. Under the
        # statement's own name it names the statement the second was retired into.
        self.organizer_base()
        self.old['entries']['Small.step_alt'] = entry('Small.step_alt', statement_uses=['Small.oddSum'])
        self.old['entries']['Small.root_alt']['uses'] = ['Small.step_alt']
        self.new['entries']['Small.step']['source_sha'] = 'moved-source-of-Small.step'
        self.change['retire'].append({'alternative': 'Small.step_alt', 'into': 'Small.step',
                                      'reason': 'The proof now stands under the statement.'})
        self.assertEqual(self.check(organizer=True)['errors'], [])

    def test_only_an_organizer_retires(self):
        self.organizer_base()
        result = self.check(organizer=False)
        self.assertEqual(result['retired'], [])
        self.assertTrue(any('declarations disappeared from the canon: Small.root_alt' in e for e in result['errors']),
                        result['errors'])

    def test_a_rearrangement_keeps_every_statement(self):
        self.organizer_base()
        moved = self.new['entries']['Small.step']
        moved.update(module='Small.Later', file='Small/Later.lean', span=[9, 0, 11, 5])
        self.assertEqual(self.check(organizer=True)['errors'], [])
        moved['statement_hash'] = 'another statement'
        self.refused('the statement of Small.step elaborates differently with this change', organizer=True)

    def test_a_rearrangement_does_not_rewrite_a_definition(self):
        self.organizer_base()
        self.new['entries']['Small.oddSum'].update(module='Small.Later', file='Small/Later.lean', source_sha='rewritten')
        self.refused('the text of the definition Small.oddSum changed; a rearrangement moves a definition and does '
                     'not rewrite it', organizer=True)

    def test_a_rearrangement_does_not_change_whether_a_proof_is_complete(self):
        self.organizer_base()
        self.new['entries']['Small.step'].update(lean_proof='sorry', axioms=['sorryAx'])
        self.refused('the proof of Small.step changed in what it names or in whether it is complete', organizer=True)

    def test_a_rearrangement_does_not_change_what_a_proof_names(self):
        for uses in (['Small.oddSum'], ['Small.root']):
            with self.subTest(uses=uses):
                self.organizer_base()
                self.new['entries']['Small.step']['uses'] = uses
                self.refused('the proof of Small.step changed in what it names or in whether it is complete',
                             organizer=True)

    def test_a_reference_to_a_retired_declaration_becomes_one_to_its_statement(self):
        self.organizer_base()
        self.old['entries']['Small.user'] = entry('Small.user', uses=['Small.root_alt', 'Small.step'])
        self.add(entry('Small.user', uses=['Small.root', 'Small.step'], source='source-with-the-reference-turned'))
        self.existing['Small.user'] = parse_record(STEP_RECORD)
        self.assertEqual(self.check(organizer=True)['errors'], [])
        # Turned into a reference to anything else, the proof was changed.
        self.new['entries']['Small.user']['uses'] = ['Small.step']
        self.refused('the proof of Small.user changed in what it names or in whether it is complete', organizer=True)

    def test_an_organizer_change_without_a_retirement_leaves_every_proof_as_it_was(self):
        self.old, self.change = copy.deepcopy(self.new), {'replace': [], 'retire': []}
        self.add(entry('Small.agree', uses=['Small.step']))
        self.records = {'Small/agree': parse_record(STEP_RECORD)}
        self.assertEqual(self.check(organizer=True)['errors'], [])
        self.new['entries']['Small.step']['uses'] = ['Small.agree']
        self.refused('the proof of Small.step changed in what it names or in whether it is complete', organizer=True)

    def test_the_statement_a_proof_is_retired_into_takes_that_proof(self):
        # Its Lean proof changes, by the retirement's own rule, and its record may take the written proof.
        self.organizer_base()
        self.change['replace'] = [{'declaration': 'Small.root', 'file': 'replace/root.lean', 'imports': ['Small.Step']}]
        self.records = {'Small/root': parse_record(ROOT_RECORD)}
        result = self.check(organizer=True)
        self.assertEqual((result['errors'], result['replaced'], result['records']), ([], ['Small.root'], ['Small.root']))
        self.change['replace'] = []
        self.assertEqual(self.check(organizer=True)['errors'], [])

    def test_an_organizer_does_not_change_the_written_proof_of_an_element_it_keeps(self):
        self.organizer_base()
        self.records = {'Small/step': parse_record(record_text('Passing from n to n + 1.', proof='A proof nobody reviewed.'))}
        self.refused('Small.step: ' + UNTOUCHED, organizer=True)

    def test_the_rules_of_a_rearrangement_are_the_organizers(self):
        # For a peer a text changed without a replacement is found as a changed source.
        self.new['entries']['Small.oddSum']['source_sha'] = 'rewritten'
        errors = self.check(organizer=False)['errors']
        self.assertEqual(len(errors), 1, errors)
        self.assertNotIn('rearrangement', errors[0])

    def test_a_rearrangement_that_lost_a_declaration(self):
        self.organizer_base()
        del self.new['entries']['Small.step']
        self.new['entries']['Small.root']['uses'] = ['Small.step']
        self.refused('declarations disappeared from the canon: Small.step', organizer=True)


# --------------------------------------------------------------------------------------- the written part

OLD_ROOT_RECORD = record_text('The sum of the first n odd numbers equals n times n.', weight='unit',
                              statement='For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.')
OLD_APPROACH = with_review(APPROACH.replace('The arithmetic identity has not been checked.',
                                            'The inductive step has not been stated.'),
                           'Change c-old (revision 3): Opened the approach.')
OLD_UNDERSTANDING = with_review('The sum is a square for small n.\nNothing is known about why.\n',
                                'Change c-old (revision 3): A first account.')
UNDERSTANDING = 'The sum is a square for small n.\nEach step completes a square; see `Small.oddSum_succ`.\n'


class WrittenPartTests(TempCase):
    def setUp(self):
        super().setUp()
        self.canon = Canon(self.root / 'instance')
        self.canon.root.mkdir(parents=True)
        self.candidate = self.root / 'candidate'
        self.candidate.mkdir()
        write_json(self.candidate / 'change.json', {'title': 'A change', 'description': 'What it does.'})

    def files(self, folder):
        return sorted(p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()) if folder.exists() else []

    def apply(self, records, revision=12, change_id='c-new', contribution='  Closed the step it took on.\n'):
        change = load_change(self.candidate)
        apply_written(self.canon, self.candidate, change, {'records': records}, revision, change_id, contribution)

    def test_history_entry(self):
        old = 'First line.\nThe old middle.\nShared end.\n'
        new = 'First line.\nThe new middle.\nShared end.\nAn added line.\n'
        history_entry(self.canon, 'Small.root', 'record', 7, 'c-seven', old, new, 'records/Small/root.md')
        self.assertEqual(self.files(self.canon.history), ['Small/root/000007-record.md'])
        text = (self.canon.history / 'Small/root/000007-record.md').read_text(encoding='utf-8')
        self.assertIn('Small.root', text.split('\n')[0])
        self.assertIn('revision 7', text.split('\n')[0])
        self.assertIn('c-seven', text.split('\n')[0])
        self.assertIn('`records/Small/root.md`', text)
        self.assertEqual(apply_diff(new.splitlines(), history_diff(text)), old.splitlines())
        self.assertIn('-The new middle.', history_diff(text).split('\n'))
        self.assertIn('+The old middle.', history_diff(text).split('\n'))

    def test_history_entries_of_one_element_stand_side_by_side(self):
        history_entry(self.canon, 'Small.aux', 'record', 3, 'c3', 'a\n', 'b\n', 'records/Small/aux%.md')
        history_entry(self.canon, 'Small.aux', 'approach-induction', 3, 'c3', 'a\n', 'b\n', 'approaches/Small/aux%/induction.md')
        history_entry(self.canon, 'Small.aux', 'record', 123456, 'c4', 'b\n', 'c\n', 'records/Small/aux%.md')
        self.assertEqual(self.files(self.canon.history), ['Small/aux%/000003-approach-induction.md',
                                                          'Small/aux%/000003-record.md', 'Small/aux%/123456-record.md'])

    def test_a_new_record_is_written(self):
        write(self.candidate / 'records/Small/oddSum_succ.md', STEP_RECORD)
        self.apply(['Small.oddSum_succ'])
        self.assertEqual(record_file(self.canon, 'Small.oddSum_succ').read_text(encoding='utf-8'), STEP_RECORD)
        self.assertEqual(self.files(self.canon.history), [])

    def test_a_replaced_record_leaves_a_history_entry(self):
        write(record_file(self.canon, 'Small.root'), OLD_ROOT_RECORD)
        write(self.candidate / 'records/Small/root.md', ROOT_RECORD)
        self.apply(['Small.root'])
        self.assertEqual(record_file(self.canon, 'Small.root').read_text(encoding='utf-8'), ROOT_RECORD)
        self.assertEqual(self.files(self.canon.history), ['Small/root/000012-record.md'])
        text = (self.canon.history / 'Small/root/000012-record.md').read_text(encoding='utf-8')
        self.assertIn('c-new', text)
        self.assertIn('`records/Small/root.md`', text)
        self.assertEqual(apply_diff(ROOT_RECORD.splitlines(), history_diff(text)), OLD_ROOT_RECORD.splitlines())

    def test_an_identical_record_leaves_no_history_entry(self):
        write(record_file(self.canon, 'Small.root'), ROOT_RECORD)
        (self.candidate / 'records/Small').mkdir(parents=True)
        (self.candidate / 'records/Small/root.md').write_bytes(ROOT_RECORD.replace('\n', '\r\n').encode('utf-8'))
        self.apply(['Small.root'])
        self.assertEqual(record_file(self.canon, 'Small.root').read_bytes(), ROOT_RECORD.encode('utf-8'))
        self.assertEqual(self.files(self.canon.history), [])

    def test_a_record_that_was_not_applied_is_not_written(self):
        # The record of a replacement that review declined stays as the canon has it.
        write(record_file(self.canon, 'Small.root'), OLD_ROOT_RECORD)
        write(self.candidate / 'records/Small/root.md', ROOT_RECORD)
        write(self.candidate / 'records/Small/oddSum_succ.md', STEP_RECORD)
        self.apply(['Small.oddSum_succ'])
        self.assertEqual(record_file(self.canon, 'Small.root').read_text(encoding='utf-8'), OLD_ROOT_RECORD)
        self.assertEqual(self.files(self.canon.records), ['Small/oddSum_succ.md', 'Small/root.md'])
        self.assertEqual(self.files(self.canon.history), [])

    def test_a_record_with_an_encoded_name(self):
        write(self.candidate / 'records/Small/aux%.md', STEP_RECORD)
        self.apply(['Small.aux'])
        self.assertEqual(read_record(self.canon, 'Small.aux'), parse_record(STEP_RECORD))

    def test_a_new_approach_entry_gets_the_review_stamp(self):
        write(self.candidate / 'approaches/Small/root/induction.md', APPROACH)
        self.apply([])
        text = (self.canon.approaches / 'Small/root/induction.md').read_text(encoding='utf-8')
        self.assertEqual(split_review(text), (APPROACH, 'Change c-new (revision 12): Closed the step it took on.'))
        self.assertEqual(read_approaches(self.canon, 'Small.root')['induction']['sections']['Review'],
                         'Change c-new (revision 12): Closed the step it took on.')
        self.assertEqual(self.files(self.canon.history), [])

    def test_a_replaced_approach_entry_leaves_its_difference_in_the_history(self):
        write(self.canon.approaches / 'Small/root/induction.md', OLD_APPROACH)
        write(self.candidate / 'approaches/Small/root/induction.md', APPROACH)
        self.apply([])
        current = (self.canon.approaches / 'Small/root/induction.md').read_text(encoding='utf-8')
        self.assertEqual(current, with_review(APPROACH, 'Change c-new (revision 12): Closed the step it took on.'))
        self.assertEqual(self.files(self.canon.history), ['Small/root/000012-approach-induction.md'])
        text = (self.canon.history / 'Small/root/000012-approach-induction.md').read_text(encoding='utf-8')
        self.assertIn('`approaches/Small/root/induction.md`', text)
        self.assertIn('c-new', text)
        self.assertEqual(apply_diff(current.splitlines(), history_diff(text)), OLD_APPROACH.splitlines())

    def test_the_history_of_an_approach_is_with_the_history_of_its_element(self):
        # `Small.aux` has an encoded path; the history of an element is one folder, which `view --part history` reads.
        write(self.canon.approaches / 'Small/aux%/induction.md', OLD_APPROACH)
        write(self.candidate / 'approaches/Small/aux%/induction.md', APPROACH)
        self.apply([])
        self.assertEqual(self.files(self.canon.history), [name_path('Small.aux') + '/000012-approach-induction.md'])

    def test_a_new_understanding_text_gets_the_review_stamp(self):
        write(self.candidate / 'questions/q0.md', UNDERSTANDING)
        self.apply([], revision=5, change_id='c-five', contribution='Let the research see why.')
        self.assertEqual((self.canon.questions / 'q0.md').read_text(encoding='utf-8'),
                         UNDERSTANDING + '\n## Review\n\nChange c-five (revision 5): Let the research see why.\n')
        self.assertEqual(self.files(self.canon.history), [])

    def test_a_replaced_understanding_text_leaves_its_difference_in_the_history(self):
        write(self.canon.questions / 'q0.md', OLD_UNDERSTANDING)
        write(self.candidate / 'questions/q0.md', UNDERSTANDING)
        self.apply([])
        current = (self.canon.questions / 'q0.md').read_text(encoding='utf-8')
        self.assertEqual(split_review(current), (UNDERSTANDING, 'Change c-new (revision 12): Closed the step it took on.'))
        self.assertEqual(self.files(self.canon.history), ['questions/q0/000012.md'])
        text = (self.canon.history / 'questions/q0/000012.md').read_text(encoding='utf-8')
        self.assertIn('q0', text.split('\n')[0])
        self.assertIn('c-new', text.split('\n')[0])
        self.assertEqual(apply_diff(current.splitlines(), history_diff(text)), OLD_UNDERSTANDING.splitlines())
        self.assertIn('+Nothing is known about why.', history_diff(text).split('\n'))  # what the new text removed

    def test_without_a_contribution_no_review_section_is_written(self):
        write(self.candidate / 'approaches/Small/root/induction.md', APPROACH)
        write(self.candidate / 'questions/q0.md', UNDERSTANDING)
        self.apply([], contribution=None)
        self.assertEqual((self.canon.approaches / 'Small/root/induction.md').read_text(encoding='utf-8'), APPROACH)
        self.assertEqual((self.canon.questions / 'q0.md').read_text(encoding='utf-8'), UNDERSTANDING)

    def test_evidence_files_are_copied(self):
        write(self.candidate / 'evidence/Small/root/table.csv', 'n,sum\n1,1\n2,4\n')
        (self.candidate / 'evidence/Small/root/data.bin').write_bytes(bytes(range(256)))
        write(self.canon.evidence / 'Small/root/earlier.txt', 'kept')
        self.apply([])
        self.assertEqual(self.files(self.canon.evidence), ['Small/root/data.bin', 'Small/root/earlier.txt',
                                                           'Small/root/table.csv'])
        self.assertEqual((self.canon.evidence / 'Small/root/data.bin').read_bytes(), bytes(range(256)))

    def test_a_replaced_evidence_file_is_put_in_place_whole(self):
        # A session reads the evidence a record refers to while a publication brings a new file of the same
        # name. The new file is written beside the old one and moved onto it, so the reader has the earlier
        # text whole. Where an open file cannot be replaced, the move waits for the reader, as the runtime's
        # writes do; the reader reads during that wait and lets the file go.
        target = write(self.canon.evidence / 'Small/root/table.csv', 'n,sum\n1,1\n')
        write(self.candidate / 'evidence/Small/root/table.csv', 'n,sum\n1,1\n2,4\n')
        reader = target.open(encoding='utf-8')
        self.addCleanup(reader.close)
        seen = []

        def release(seconds):
            seen.append(reader.read())
            reader.close()

        with patch('runtime_support.time.sleep', side_effect=release):
            self.apply([])
        if not reader.closed:
            seen.append(reader.read())
        self.assertEqual(seen, ['n,sum\n1,1\n'])
        self.assertEqual(target.read_text(encoding='utf-8'), 'n,sum\n1,1\n2,4\n')
        self.assertEqual(self.files(self.canon.evidence), ['Small/root/table.csv'])

    def test_an_evidence_file_is_on_the_disk_before_it_takes_its_name(self):
        # As a module of the library is (TreeTests): the publication is saved as installed after this copy, and no
        # runner copies the file a second time.
        (self.candidate / 'evidence/Small/root').mkdir(parents=True)
        (self.candidate / 'evidence/Small/root/data.bin').write_bytes(bytes(range(256)))
        self.assertEqual(self.moves(lambda: self.apply([])), [('data.bin', [256])])
        self.assertEqual((self.canon.evidence / 'Small/root/data.bin').read_bytes(), bytes(range(256)))

    def test_the_bibliography_of_a_candidate_is_merged(self):
        write(self.canon.bibliography, '@book{knuth1997,\n  title = {The Art of Computer Programming}\n}\n')
        write(self.candidate / 'bibliography.bib', '@book{knuth1997,\n  title = {Another title}\n}\n\n'
                                                   '@article{gauss1801,\n  title = {Disquisitiones}\n}\n')
        self.apply([])
        text = self.canon.bibliography.read_text(encoding='utf-8')
        self.assertIn('The Art of Computer Programming', text)
        self.assertNotIn('Another title', text)
        self.assertIn('@article{gauss1801,\n  title = {Disquisitiones}\n}', text)

    def test_a_candidate_without_written_files_changes_nothing(self):
        self.apply([])
        self.assertEqual(self.files(self.canon.root), [])
        self.assertFalse(self.canon.history.exists())

    def test_merge_bibliography_creates_the_file(self):
        self.assertFalse(self.canon.bibliography.exists())
        merge_bibliography(self.canon.bibliography,
                           '@book{knuth1997,\r\n  title = {TAOCP}\r\n}\r\n\r\n@misc{oeis, note = {A000290}}\r\n')
        self.assertEqual(self.canon.bibliography.read_text(encoding='utf-8'),
                         '@book{knuth1997,\n  title = {TAOCP}\n}\n\n@misc{oeis, note = {A000290}}\n')

    def test_merge_bibliography_appends_new_keys_and_keeps_existing_entries(self):
        first = '@book{knuth1997,\n  title = {TAOCP}\n}\n'
        write(self.canon.bibliography, first)
        merge_bibliography(self.canon.bibliography, '% a comment of the candidate\n@misc{oeis, note = {A000290}}\n'
                                                    '@book{ knuth1997 , title = {Changed}}\n@article{gauss1801, title = {D}}\n')
        self.assertEqual(self.canon.bibliography.read_text(encoding='utf-8'),
                         first + '\n@misc{oeis, note = {A000290}}\n\n@article{gauss1801, title = {D}}\n')

    def test_merge_bibliography_without_a_new_key_writes_nothing(self):
        first = '@book{knuth1997,\n  title = {TAOCP}\n}'
        write(self.canon.bibliography, first)
        merge_bibliography(self.canon.bibliography, '@book{knuth1997, title = {Changed}}\n')
        self.assertEqual(self.canon.bibliography.read_text(encoding='utf-8'), first)
        (self.root / 'empty').mkdir()
        merge_bibliography(self.root / 'empty/bibliography.bib', '% nothing\n')
        self.assertFalse((self.root / 'empty/bibliography.bib').exists())

    def test_retire_approaches_moves_them_to_the_history(self):
        write(self.canon.approaches / 'Small/root/induction.md', APPROACH)
        write(self.canon.approaches / 'Small/root/direct.md', APPROACH)
        write(self.canon.approaches / 'Small/other/kept.md', APPROACH)
        # The runner regenerates records.json, which lists the approaches of each element, when this says
        # that approaches were moved (runner.py, publish).
        self.assertTrue(retire_approaches(self.canon, 'Small.root', 15))
        self.assertFalse((self.canon.approaches / 'Small/root').exists())
        self.assertEqual(self.files(self.canon.history), ['Small/root/000015-approaches/direct.md',
                                                          'Small/root/000015-approaches/induction.md'])
        self.assertEqual(self.files(self.canon.approaches), ['Small/other/kept.md'])
        self.assertEqual(read_approaches(self.canon, 'Small.root'), {})

    def test_retire_approaches_of_an_element_with_an_encoded_name(self):
        write(self.canon.approaches / 'Small/aux%/induction.md', APPROACH)
        retire_approaches(self.canon, 'Small.aux', 2)
        self.assertEqual(self.files(self.canon.history), ['Small/aux%/000002-approaches/induction.md'])

    def test_retire_approaches_does_nothing_without_approaches(self):
        (self.canon.approaches / 'Small/empty').mkdir(parents=True)
        self.assertFalse(retire_approaches(self.canon, 'Small.root', 15))
        self.assertFalse(retire_approaches(self.canon, 'Small.empty', 15))
        self.assertFalse(self.canon.history.exists())
        self.assertTrue((self.canon.approaches / 'Small/empty').is_dir())

    def test_retire_approaches_leaves_the_approaches_of_an_element_whose_name_extends_the_name(self):
        # `Small.root.even` is an element of its own, and its folder lies inside the folder of `Small.root`.
        # Accepting the root's proof sets aside the root's approaches only (design record, section 7).
        write(self.canon.approaches / 'Small/root/induction.md', APPROACH)
        write(self.canon.approaches / 'Small/root/even/cases.md', APPROACH)
        self.assertTrue(retire_approaches(self.canon, 'Small.root', 15))
        self.assertEqual(self.files(self.canon.history), ['Small/root/000015-approaches/induction.md'])
        self.assertEqual(self.files(self.canon.approaches), ['Small/root/even/cases.md'])
        self.assertEqual(list(read_approaches(self.canon, 'Small.root.even')), ['cases'])
        self.assertEqual(read_approaches(self.canon, 'Small.root'), {})

    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_retire_approaches_waits_for_a_reader_that_holds_an_entry(self):
        # A session that reads an approach entry holds its file open without delete sharing, as Python's
        # `open` does, and Windows moves no file held so. The move waits for the reader, as the runtime's
        # writes do, and the entry is moved once.
        path = write(self.canon.approaches / 'Small/root/induction.md', APPROACH)
        reader = path.open(encoding='utf-8')
        self.addCleanup(reader.close)
        with patch('runtime_support.time.sleep', side_effect=lambda seconds: reader.close()) as sleep:
            self.assertTrue(retire_approaches(self.canon, 'Small.root', 15))
        self.assertGreaterEqual(sleep.call_count, 1)
        self.assertEqual(self.files(self.canon.history), ['Small/root/000015-approaches/induction.md'])
        self.assertEqual(self.files(self.canon.approaches), [])

    def test_retire_approaches_leaves_the_emptied_folder_when_it_cannot_be_removed(self):
        # Windows removes no folder that a process holds, such as the current directory of a shell in which
        # an operator or a session reads the entries. By then the entries are in the history, and a folder
        # without entries reads as no approaches, so the folder stays and the publication goes on. The refusal
        # is the one such a removal meets; nothing else is replaced.
        write(self.canon.approaches / 'Small/root/induction.md', APPROACH)
        with patch.object(Path, 'rmdir', side_effect=PermissionError('injected sharing violation')) as removal:
            self.assertTrue(retire_approaches(self.canon, 'Small.root', 15))
        removal.assert_called_once_with()
        self.assertEqual(self.files(self.canon.history), ['Small/root/000015-approaches/induction.md'])
        self.assertTrue((self.canon.approaches / 'Small/root').is_dir())
        self.assertEqual(read_approaches(self.canon, 'Small.root'), {})
        self.assertFalse(retire_approaches(self.canon, 'Small.root', 16))

    def test_read_record(self):
        write(record_file(self.canon, 'Small.root'), ROOT_RECORD)
        write(record_file(self.canon, 'Small.broken'), ROOT_RECORD.replace('weight: unit', 'weight: main'))
        record_file(self.canon, 'Small.marked').write_bytes(b'\xef\xbb\xbf' + STEP_RECORD.encode('utf-8'))
        self.assertEqual(read_record(self.canon, 'Small.root'), parse_record(ROOT_RECORD))
        self.assertEqual(read_record(self.canon, 'Small.marked'), parse_record(STEP_RECORD))
        self.assertIsNone(read_record(self.canon, 'Small.absent'))
        self.assertIsNone(read_record(self.canon, 'Small.broken'))

    def test_read_approaches(self):
        self.assertEqual(read_approaches(self.canon, 'Small.root'), {})
        second = APPROACH.replace('Induction on the number of terms', 'A direct count')
        write(self.canon.approaches / 'Small/root/induction.md', with_review(APPROACH, 'An assessment.'))
        write(self.canon.approaches / 'Small/root/direct.md', second)
        write(self.canon.approaches / 'Small/root/broken.md', APPROACH.replace('## Idea', '## Plan'))
        write(self.canon.approaches / 'Small/root/notes.txt', 'Not an entry.')
        entries = read_approaches(self.canon, 'Small.root')
        self.assertEqual(list(entries), ['direct', 'induction'])
        self.assertEqual(entries['direct'], parse_approach(second))
        self.assertEqual(entries['induction']['sections']['Review'], 'An assessment.')


# --------------------------------------------------------------------------------------- preparing and verifying

class CandidateToolTests(InstanceCase):
    def session(self, role='peer', task=None):
        sid = 's' + uuid.uuid4().hex[:12]
        folder = self.instance / 'sessions' / sid
        (folder / 'output').mkdir(parents=True)
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': role,
                                           'task': task or {}, 'pipeline': None})
        return folder

    def fill(self, target, **parts):
        """Put the files of a candidate, not yet prepared, into a session's output folder."""
        shutil.copytree(self.candidate(prepare=False, **parts), target, dirs_exist_ok=True)

    def tool(self, *arguments):
        """The exit code of a canon_tool command that answers in JSON, and its answer."""
        code, text = self.command_line(*arguments)
        return code, json.loads(text)

    def induction(self):
        return dict(modules={'Small/Step.lean': module_text(STEP)}, replace={'Small.root': INFORMAL},
                    imports={'Small.root': ['Small.Step']},
                    records={'Small/oddSum_succ.md': STEP_RECORD, 'Small/root.md': ROOT_RECORD},
                    approaches={'Small/root/induction.md': APPROACH})

    def test_prepare_writes_the_receipt_of_a_candidate_that_builds(self):
        session = self.session('peer')
        output = session / 'output'
        self.fill(output, **self.induction())
        before = Canon(self.instance).load_index()
        self.configure(lean={'calibration_expect_mb': 72})  # the estimate where the command line gives none
        # With no time to wait, the command returns while the build runs: exit code 124, and no receipt yet.
        code, answer = self.tool('prepare', session, '--timeout', 0)
        self.assertEqual((code, answer['waiting']), (124, True))
        self.assertFalse((output / 'prepared.json').exists())
        started = read_json(session / 'work/prepare/state.json')['build']
        # The same command comes back for that build and starts no other.
        code, summary = self.tool('prepare', session, '--timeout', 120)
        self.assertEqual(code, 0, summary)
        self.assertEqual(summary['build'], started)
        receipt = read_json(output / 'prepared.json')
        self.assertTrue(receipt['ok'])
        self.assertEqual(receipt['errors'], [])
        self.assertEqual(receipt['tree'], tree_hash(output, skip=('prepared.json',)))
        self.assertEqual(receipt['revision'], before['revision'])
        self.assertEqual(receipt['changed_modules'], ['Small.Root', 'Small.Step'])
        self.assertEqual(receipt['added'], ['Small.oddSum_succ'])
        self.assertEqual(receipt['replaced'], ['Small.root'])
        self.assertEqual(receipt['records'], ['Small.oddSum_succ', 'Small.root'])
        self.assertEqual(receipt['retired'], [])
        self.assertEqual(sorted(receipt['entries']), ['Small.oddSum_succ', 'Small.root'])
        root, step = receipt['entries']['Small.root'], receipt['entries']['Small.oddSum_succ']
        self.assertEqual({key: root[key] for key in ('kind', 'lean_proof', 'written_proof', 'uses', 'statement_uses', 'axioms')},
                         {'kind': 'theorem', 'lean_proof': 'sorry', 'written_proof': True, 'uses': ['Small.oddSum_succ'],
                          'statement_uses': ['Small.oddSum'], 'axioms': ['sorryAx']})
        self.assertEqual({key: step[key] for key in ('kind', 'lean_proof', 'written_proof', 'uses', 'statement_uses', 'axioms')},
                         {'kind': 'theorem', 'lean_proof': 'complete', 'written_proof': False, 'uses': [],
                          'statement_uses': ['Small.oddSum'], 'axioms': []})
        # The statement of the replaced declaration is the one the canon has; its base is the text it replaces.
        self.assertEqual(root['statement_hash'], before['entries']['Small.root']['statement_hash'])
        self.assertEqual(root['statement'], before['entries']['Small.root']['statement'])
        self.assertTrue(step['statement_hash'] and step['statement'])
        source = (Canon(self.instance).lean / 'Small/Root.lean').read_text(encoding='utf-8')
        self.assertEqual(receipt['bases'], {'Small.root': sha256_text(declaration_text(source, before['entries']['Small.root']['span']))})
        # The build is the session's own and finished. The command line gave no estimate of memory, so the build
        # was asked for with the one the instance's settings hold. The printed summary agrees with the receipt.
        record = job_record(Paths(self.instance), receipt['build'])
        self.assertEqual((record['status'], record['session'], record['expect_mb']), ('finished', session.name, 72))
        self.assertEqual({key: summary[key] for key in ('ok', 'build', 'added', 'replaced', 'records', 'errors')},
                         {key: receipt[key] for key in ('ok', 'build', 'added', 'replaced', 'records', 'errors')})
        self.assertEqual(summary['axioms'], {'Small.oddSum_succ': [], 'Small.root': ['sorryAx']})
        # The canon itself is untouched by a preparation.
        self.assertEqual(Canon(self.instance).load_index(), before)
        self.assertEqual((Canon(self.instance).lean / 'Small/Root.lean').read_text(encoding='utf-8'), source)
        self.assertFalse((Canon(self.instance).lean / 'Small/Step.lean').exists())
        # The receipt is for exactly these files: the same files are not built again, edited files need a new receipt.
        self.assertEqual(prepared_candidate(output)['build'], receipt['build'])
        code, again = self.tool('prepare', session, '--timeout', 120)
        self.assertEqual((code, again['build']), (0, receipt['build']))
        write(output / 'records/Small/oddSum_succ.md', STEP_RECORD + '\nA later remark.\n')
        with self.assertRaisesRegex(Invalid, 'changed after it was prepared'):
            prepared_candidate(output)
        # The command builds the edited files afresh, and the receipt it then writes is the one for them.
        code, edited = self.tool('prepare', session, '--timeout', 120)
        self.assertEqual(code, 0, edited)
        self.assertNotEqual(edited['build'], receipt['build'])
        self.assertEqual(prepared_candidate(output)['build'], edited['build'])
        # The broker answers a build submitted again while the first still runs with a record that points to
        # the first (lean_broker.Broker.ingest_build). Whether a repeat arrives in time is a matter of timing,
        # so that record is written here by hand, in the broker's form. Its outcome is that of the first build.
        repeat = 'b' + uuid.uuid4().hex
        (Paths(self.instance).builds / repeat).mkdir()
        write_json(Paths(self.instance).builds / repeat / 'result.json',
                   {'id': repeat, 'status': 'duplicate', 'duplicate_of': receipt['build']})
        outcome = build_outcome(self.instance, repeat)
        self.assertEqual((outcome['ok'], outcome['build']), (True, receipt['build']))
        self.assertEqual(outcome, build_outcome(self.instance, receipt['build']))

    def test_a_candidate_without_lean_needs_no_build(self):
        reworded = record_text('The first n odd numbers add up to the square of n.', weight='unit', short='odd sum',
                               statement='For every natural number $n$, the sum of the first $n$ odd numbers is $n^2$.')
        folder = self.candidate(records={'Small/root.md': reworded}, understanding={'q0.md': UNDERSTANDING},
                                prepare=False)
        result = canon_tool.build_candidate(self.instance, 'test', folder, self.root / 'work', 64, 5, 'peer')
        self.assertEqual({key: result[key] for key in ('ok', 'errors', 'build', 'changed_modules', 'added', 'replaced',
                                                       'records', 'entries', 'bases')},
                         {'ok': True, 'errors': [], 'build': None, 'changed_modules': [], 'added': [], 'replaced': [],
                          'records': ['Small.root'], 'entries': {}, 'bases': {}})
        self.assertEqual(result['tree'], tree_hash(folder, skip=('prepared.json',)))

    def test_a_written_proof_enters_with_a_replacement_of_the_declaration(self):
        # The canon's record of the root has no proof. A record that adds one changes the standing of the
        # root, which review judges only for a declaration the candidate lists in "replace".
        folder = self.candidate(records={'Small/root.md': ROOT_RECORD}, prepare=False)
        result = canon_tool.build_candidate(self.instance, 'test', folder, self.root / 'work', 64, 5, 'peer')
        self.assertFalse(result['ok'])
        self.assertEqual(len(result['errors']), 1, result['errors'])
        self.assertIn('Small.root: ' + UNTOUCHED + '; list the declaration in "replace"', result['errors'][0])
        self.assertIsNone(result['build'])

    def test_a_candidate_whose_manifest_is_refused(self):
        session = self.session('peer')
        self.fill(session / 'output', records={'Small/root.md': ROOT_RECORD.replace('weight: unit', 'weight: main')})
        code, summary = self.tool('prepare', session)
        self.assertEqual(code, 1)
        receipt = read_json(session / 'output/prepared.json')
        self.assertFalse(receipt['ok'])
        self.assertEqual(len(receipt['errors']), 1)
        self.assertRegex(receipt['errors'][0], r'records/Small/root\.md: .*weight')
        self.assertEqual(summary['errors'], receipt['errors'])
        with self.assertRaisesRegex(Invalid, 'prepare reported errors'):
            prepared_candidate(session / 'output')

    def test_a_candidate_that_does_not_build(self):
        broken = module_text('-- fail: the elaborator gave up on this file\n' + STEP)
        folder = self.candidate(modules={'Small/Broken.lean': broken}, records={'Small/oddSum_succ.md': STEP_RECORD},
                                prepare=False)
        work = self.root / 'work'
        result = canon_tool.build_candidate(self.instance, 'test', folder, work, 64, 120, 'peer')
        self.assertIsNotNone(result, 'the candidate build did not finish')
        self.assertFalse(result['ok'])
        self.assertTrue(result['build'])
        self.assertIn('the elaborator gave up on this file', '\n'.join(result['errors']))
        self.assertIn('Small.Broken', '\n'.join(result['errors']))
        self.assertEqual((result['added'], result['replaced'], result['entries']), ([], [], {}))
        # A build that ended without compiling is not kept: the same command on the same files builds again,
        # because a compile can also end for a reason that is not in the files.
        again = canon_tool.build_candidate(self.instance, 'test', folder, work, 64, 120, 'peer')
        self.assertIsNotNone(again, 'the candidate build did not finish')
        self.assertFalse(again['ok'])
        self.assertNotEqual(again['build'], result['build'])

        unknown = INFORMAL.replace('have step := oddSum_succ', 'have step := unknown_name')
        folder = self.candidate(replace={'Small.root': unknown}, prepare=False)
        result = self.prepare(folder, expect_ok=False)
        self.assertFalse(result['ok'])
        self.assertIn("unknown identifier 'unknown_name'", '\n'.join(result['errors']))
        self.assertIn('Small.Root', '\n'.join(result['errors']))

    def test_a_kept_build_is_made_again_once_the_canon_was_published_to(self):
        # A build is kept for the canon the candidate was applied to. After a publication that changed the
        # library, the same command on the same files applies them to the canon as it now is and builds again.
        folder = self.candidate(modules={'Small/Step.lean': module_text(STEP)},
                                records={'Small/oddSum_succ.md': STEP_RECORD}, prepare=False)
        work = self.root / 'work'
        first = canon_tool.build_candidate(self.instance, 'test', folder, work, 64, 120, 'peer')
        self.assertTrue(first and first['ok'], first)
        text = 'theorem root_again (n : Nat) : oddSum n = n * n := by\n  sorry'
        self.publish(self.candidate(modules={'Small/Again.lean': module_text(text)},
                                    records={'Small/root_again.md': record_text('The root once more.')}))
        again = canon_tool.build_candidate(self.instance, 'test', folder, work, 64, 120, 'peer')
        self.assertTrue(again and again['ok'], again)
        self.assertGreater(again['revision'], first['revision'])
        self.assertNotEqual(again['build'], first['build'])

    def test_a_build_is_not_kept_once_a_later_run_has_made_its_files_again(self):
        # The command keeps a build together with the files it applied the candidate to. A run on edited files
        # makes those files again, and it can end without a build of its own, as it does when the edit cannot be
        # applied. The earlier build then no longer belongs to the files that stand there, so the command builds
        # again when the candidate is put back as it was.
        folder = self.candidate(modules={'Small/Step.lean': module_text(STEP)},
                                records={'Small/oddSum_succ.md': STEP_RECORD}, prepare=False)
        work = self.root / 'work'
        first = canon_tool.build_candidate(self.instance, 'test', folder, work, 64, 120, 'peer')
        self.assertTrue(first and first['ok'], first)
        clash = write(folder / 'lean/Small/Root.lean', module_text(STEP))  # the canon has a module of this name
        refused = canon_tool.build_candidate(self.instance, 'test', folder, work, 64, 120, 'peer')
        self.assertIn('already exists in the canon', '\n'.join(refused['errors']))
        clash.unlink()
        again = canon_tool.build_candidate(self.instance, 'test', folder, work, 64, 120, 'peer')
        self.assertTrue(again and again['ok'], again)
        self.assertEqual((again['tree'], again['added']), (first['tree'], first['added']))

    def test_a_build_that_fails_before_any_module_is_compiled_is_reported_with_its_reason(self):
        # A new module imports a module of the library that has no file. The broker fails such a build as a whole
        # before it compiles anything (lean_broker.discover_modules), so the build's record names no module that
        # failed, and the outcome carries the status and the reason of the build itself.
        absent = module_text(STEP, imports=('Small.Defs', 'Small.Absent'))
        folder = self.candidate(modules={'Small/Step.lean': absent}, records={'Small/oddSum_succ.md': STEP_RECORD},
                                prepare=False)
        result = self.prepare(folder, expect_ok=False)
        self.assertFalse(result['ok'])
        self.assertTrue(result['build'])
        self.assertEqual(len(result['errors']), 1, result['errors'])
        self.assertRegex(result['errors'][0], r'^build: failed: .*Small\.Absent')
        self.assertEqual((result['added'], result['replaced'], result['entries']), ([], [], {}))

    def test_a_candidate_with_a_check_error(self):
        session = self.session('peer')
        self.fill(session / 'output', modules={'Small/Step.lean': module_text(STEP)})
        code, summary = self.tool('prepare', session, '--timeout', 120)
        self.assertEqual(code, 1, summary)
        receipt = read_json(session / 'output/prepared.json')
        self.assertFalse(receipt['ok'])
        self.assertEqual(len(receipt['errors']), 1, receipt['errors'])
        self.assertRegex(receipt['errors'][0], r'Small\.oddSum_succ has no record; write records/Small/oddSum_succ\.md')
        self.assertEqual(receipt['added'], ['Small.oddSum_succ'])
        self.assertEqual(receipt['entries']['Small.oddSum_succ']['lean_proof'], 'complete')

    def test_a_replacement_that_leaves_no_declaration_is_refused(self):
        # The root stands in a module of its own (reference/canon.md). A replacement text that declares
        # nothing removes it, which the check before publication has to find: a declaration disappeared.
        folder = self.candidate(replace={'Small.root': '-- The statement was withdrawn.'}, prepare=False)
        result = self.prepare(folder, expect_ok=False)
        self.assertFalse(result['ok'], result)
        self.assertIn('declarations disappeared from the canon: Small.root', result['errors'])

    def test_a_replacement_under_another_name_is_refused(self):
        renamed = INFORMAL.replace('theorem root ', 'theorem root_two ').replace('have step := oddSum_succ\n  ', '')
        folder = self.candidate(replace={'Small.root': renamed}, prepare=False)
        result = self.prepare(folder, expect_ok=False)
        self.assertFalse(result['ok'])
        errors = '\n'.join(result['errors'])
        self.assertIn('declarations disappeared from the canon: Small.root', errors)
        self.assertIn('Small.root_two has no record', errors)

    def test_a_module_outside_the_library_is_refused(self):
        # All modules live under one top-level name, the library (reference/canon.md), and the entries of
        # the index are the declarations of the instance's own library (design 8).
        other = 'module\n\n@[expose] public section\n\nnamespace Other\n\ntheorem thing : True := by\n  trivial\n\nend Other\n'
        folder = self.candidate(modules={'Other/Thing.lean': other}, records={'Other/thing.md': record_text('A thing.')},
                                prepare=False)
        result = self.prepare(folder, expect_ok=False)
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['errors'], ['module Other/Thing.lean is outside the library; the modules of this canon '
                                            'are Small.lean and the files under Small/'])
        self.assertIsNone(result['build'])  # refused before anything is compiled
        self.assertNotIn('Other.thing', result['added'])

    def test_proves_added_to_the_record_of_a_published_declaration(self):
        # Which declarations are proofs of one statement is stated in their records, and the check confirms by
        # compilation that the statements are the same (design 4.4, 5). For a declaration of the canon the
        # claim changes its standing, so it comes with the declaration listed in "replace".
        text = 'theorem root_again (n : Nat) : oddSum n = n * n := by\n  sorry'
        self.publish(self.candidate(modules={'Small/Again.lean': module_text(text)},
                                    records={'Small/root_again.md': record_text('The root once more.')}))
        self.assertIn('Small.root_again', Canon(self.instance).load_index()['entries'])
        record = {'Small/root_again.md': record_text('Another way to the root.', proves='Small.root')}
        alone = self.prepare(self.candidate(records=record, prepare=False), expect_ok=False)
        self.assertFalse(alone['ok'])
        self.assertTrue(any('Small.root_again: ' + UNTOUCHED in error for error in alone['errors']), alone['errors'])
        listed = self.prepare(self.candidate(records=record, replace={'Small.root_again': text}, prepare=False),
                              expect_ok=False)
        self.assertEqual(listed['errors'], [])
        self.assertEqual((listed['replaced'], listed['records']), (['Small.root_again'], ['Small.root_again']))

    def test_proves_is_confirmed_by_the_build(self):
        again = module_text('theorem root_again (n : Nat) : oddSum n = n * n := by\n  sorry\n\n'
                            'theorem other (n : Nat) : oddSum n = n + n := by\n  sorry')
        records = {'Small/root_again.md': record_text('Another way to the root.', proves='Small.root'),
                   'Small/other.md': record_text('Not the root.', proves='Small.root')}
        folder = self.candidate(modules={'Small/Again.lean': again}, records=records, prepare=False)
        result = self.prepare(folder, expect_ok=False)
        self.assertEqual(result['added'], ['Small.other', 'Small.root_again'])
        self.assertEqual(len(result['errors']), 1, result['errors'])
        self.assertRegex(result['errors'][0],
                         'Small.other: Lean did not confirm that its statement is the statement of Small.root')

    def test_prepare_is_for_a_peer_or_an_organizer(self):
        for role in ('attempt', 'explore', 'formalizer', 'review'):
            session = self.session(role)
            self.fill(session / 'output', records={'Small/root.md': ROOT_RECORD})
            with self.subTest(role):
                with self.assertRaisesRegex(CanonError, 'a peer or an organizer'):
                    canon_tool.prepare(session, 64, 5)
                code, answer = self.tool('prepare', session)
                self.assertEqual(code, 1)
                self.assertIn('a peer or an organizer', answer['error'])
                self.assertFalse((session / 'output/prepared.json').exists())

    def test_an_organizer_change_is_checked_as_one(self):
        session = self.session('organizer', {'batch': []})
        output = session / 'output'
        agree = module_text('theorem agree (n : Nat) : oddSum n = oddSum n := by\n  sorry')
        self.fill(output, modules={'Small/Agree.lean': agree},
                  records={'Small/agree.md': record_text('The sum agrees with itself.')})
        write_json(output / 'organization.json', {'batch': [], 'merge_questions': [], 'delete': ['Small.Root']})
        code, summary = self.tool('prepare', session, '--timeout', 120)
        self.assertEqual(code, 1, summary)
        receipt = read_json(output / 'prepared.json')
        self.assertEqual(receipt['changed_modules'], ['Small.Agree'])
        self.assertEqual(receipt['added'], ['Small.agree'])
        errors = '\n'.join(receipt['errors'])
        self.assertEqual(len(receipt['errors']), 2, receipt['errors'])
        self.assertIn('declarations disappeared from the canon: Small.root', errors)
        self.assertIn('Small.agree is not proved in Lean from the allowed axioms: sorryAx', errors)

    def test_verify_compiles_the_changed_modules_afresh(self):
        folder = self.candidate(**self.induction())  # the peer's own preparation compiled the modules once
        paths = Paths(self.instance)
        # Built again without the request to compile afresh, the modules come from the broker's cache.
        cached = canon_tool.build_candidate(self.instance, 'other', folder, self.root / 'again', 64, 120, 'peer')
        self.assertTrue(cached['ok'], cached['errors'])
        modules = job_record(paths, cached['build'])['modules']
        self.assertEqual({modules[name]['status'] for name in cached['changed_modules']}, {'cached'})

        session = self.session('review', {'kind': 'candidate', 'candidate': str(folder)})
        frozen = tree_hash(folder)
        code, summary = self.tool('verify', session, '--expect-mb', 96, '--timeout', 120)
        self.assertEqual(code, 0, summary)
        outcome = read_json(session / 'work/verify/outcome.json')
        self.assertTrue(outcome['ok'])
        self.assertEqual(outcome['tree'], tree_hash(folder, skip=('prepared.json',)))
        self.assertEqual((outcome['changed_modules'], outcome['added'], outcome['replaced']),
                         (['Small.Root', 'Small.Step'], ['Small.oddSum_succ'], ['Small.root']))
        self.assertEqual(outcome['entries'], read_json(folder / 'prepared.json')['entries'])
        self.assertEqual(summary['build'], outcome['build'])
        self.assertEqual(summary['axioms'], {'Small.oddSum_succ': [], 'Small.root': ['sorryAx']})
        record = job_record(paths, outcome['build'])
        # The build was asked for with the estimate given on the command line.
        self.assertEqual((record['status'], record['session'], record['expect_mb']), ('finished', session.name, 96))
        for name in outcome['changed_modules']:
            self.assertEqual(record['modules'][name]['status'], 'finished', name)
            self.assertEqual(record['modules'][name]['exit_code'], 0, name)
            self.assertTrue(record['modules'][name].get('job'), name)
        # The frozen candidate and the reviewing session's output are left as they were.
        self.assertEqual(tree_hash(folder), frozen)
        self.assertEqual(list((session / 'output').iterdir()), [])

    def test_verify_is_for_the_review_of_a_candidate(self):
        folder = self.candidate(records={'Small/root.md': ROOT_RECORD}, prepare=False)
        candidate = {'kind': 'candidate', 'candidate': str(folder)}
        for role, task in (('peer', candidate), ('organizer', candidate), ('attempt', candidate),
                           ('review', {'kind': 'comprehensive', 'concerns': []})):
            session = self.session(role, task)
            with self.subTest(role=role, kind=task['kind']):
                with self.assertRaisesRegex(CanonError, 'verify is for the review of a candidate'):
                    canon_tool.verify(session, 64, 5)
                code, answer = self.tool('verify', session)
                self.assertEqual(code, 1)
                self.assertIn('verify is for the review of a candidate', answer['error'])
                self.assertFalse((session / 'work/verify/outcome.json').exists())

    def test_an_unknown_build(self):
        with self.assertRaisesRegex(CanonError, 'unknown build'):
            build_outcome(self.instance, 'b' + uuid.uuid4().hex)

    def test_checkout_copies_the_module_root_into_the_session(self):
        session = self.session('attempt')
        canon = Canon(self.instance)
        files = lambda root: {p.relative_to(root).as_posix(): p.read_bytes() for p in Path(root).rglob('*') if p.is_file()}
        answer = canon_tool.checkout(session, 'work/canon')
        self.assertEqual(Path(answer['checked_out']).resolve(), (session / 'work/canon').resolve())
        self.assertEqual(answer['revision'], canon.load_index()['revision'])
        self.assertEqual(files(session / 'work/canon'), files(canon.lean))
        self.assertEqual(sorted(files(canon.lean)), ['Small/Defs.lean', 'Small/Root.lean'])
        # An empty folder that exists, given by its full path, through the command line.
        (session / 'work/empty').mkdir()
        code, answer = self.tool('checkout', session, session / 'work/empty')
        self.assertEqual((code, Path(answer['checked_out']).resolve()), (0, (session / 'work/empty').resolve()))
        self.assertEqual(files(session / 'work/empty'), files(canon.lean))

    def test_checkout_refuses_a_folder_outside_the_session(self):
        session = self.session('attempt')
        for target in (self.root / 'elsewhere', '../elsewhere', self.instance / 'canon/copy',
                       self.instance / 'sessions' / (session.name + '-other')):
            with self.subTest(target=str(target)):
                with self.assertRaisesRegex(CanonError, 'inside your session folder'):
                    canon_tool.checkout(session, target)
                self.assertFalse(Path(session / target).exists())
        code, answer = self.tool('checkout', session, self.root / 'elsewhere')
        self.assertEqual(code, 1)
        self.assertIn('inside your session folder', answer['error'])

    def test_checkout_refuses_a_folder_that_is_not_empty(self):
        session = self.session('attempt')
        own = write(session / 'work/mine/Draft.lean', 'theorem draft : True := trivial\n')
        with self.assertRaisesRegex(CanonError, 'is not empty'):
            canon_tool.checkout(session, 'work/mine')
        self.assertEqual(own.read_text(encoding='utf-8'), 'theorem draft : True := trivial\n')
        self.assertEqual([p.name for p in (session / 'work/mine').iterdir()], ['Draft.lean'])

    def test_a_link_in_the_output_of_a_session_is_refused_by_the_transport_check(self):
        # A link leads out of the folder whose files are hashed and copied at publication, so the transport
        # check refuses an output that holds one, whichever form of directory link the system allowed.
        session = self.session('attempt').resolve()
        # The check of a producing session reads that session's folder alone: the research is not replayed for it.
        with patch('check.replay', side_effect=AssertionError('the research was replayed')):
            self.assertEqual(check_session(session), [])
        outside = self.root / 'outside'
        outside.mkdir()
        link = session / 'output' / 'linked'
        try:
            os.symlink(outside, link, target_is_directory=True)
        except OSError:
            if os.name != 'nt':
                raise
            # Without the symlink privilege, a junction is the directory link Windows allows.
            subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(outside)], check=True, capture_output=True)
        self.assertEqual(check_session(session), ['filesystem links cannot be published: ' + str(link)])


if __name__ == '__main__':
    unittest.main()
