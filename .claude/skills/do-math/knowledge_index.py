"""Render a navigation index from published records, without rewriting summaries.

The index is a set of derived files. knowledge/index.md is the general module:
it carries the preamble, the links to the last plan's documents, a table of the
other modules and the entries of every research or exploration record the last
plan did not file elsewhere. Each other module the plan declared in its output's
`index.modules` is rendered as knowledge/index/<name>.md with the same entries.
Plan, peer and review records have no entries of their own.
"""

from collections import defaultdict
import json
import re

GENERAL = 'general'
LABELS = {'research': 'research', 'explore': 'exploration'}  # entry label per category
INDEXED = tuple(LABELS)  # the only categories with index entries of their own


def plain(value):
    """Author text stays readable as raw text; escape only what could hide or relink it when rendered."""
    return re.sub(r'([\\`<\[\]])', r'\\\1', ' '.join(value.split()))


def cell(value):
    """A table cell: plain text with the column separator escaped as well."""
    return plain(value).replace('|', '\\|')


def _count(n, singular, plural=None):
    return f'{n} {singular if n == 1 else plural or singular + "s"}'


def record_link(record, label=None, prefix=''):
    return f'[{label or record}]({prefix}{record}/output.json)'


class _Relations:
    """Supersession, peer and review relations of one publication list."""

    def __init__(self, records):
        self.by_id = dict(records)
        self.replaced = defaultdict(list)
        self.reviews = defaultdict(list)
        self.peers = defaultdict(list)
        self.bundles = defaultdict(list)
        for rid, data in records:
            for old in data['supersedes']:
                self.replaced[old].append(rid)
            if data['category'] == 'review' and data['target']['kind'] == 'research':
                self.reviews[data['target']['record']].append(rid)
            elif data['category'] == 'peer':
                self.peers[data['target']['record']].append(rid)
            elif data['category'] == 'review' and data['target']['kind'] == 'bundle':
                self.bundles[data['target']['work']].append(rid)

    def entry(self, rid, data, prefix=''):
        """Lines of one research/exploration entry and its (unreviewed, conflict) flags."""
        def link(record, label=None):
            return record_link(record, label, prefix)
        overview = data['overview']
        lines = [f"## {plain(overview['title'])}", '',
                 f"{LABELS[data['category']]} · {link(rid)}", '', plain(overview['summary']), '']
        if rid in self.replaced:
            lines += ['Superseded by: ' + ', '.join(link(x) for x in self.replaced[rid]) + '.', '']
        if data['supersedes']:
            lines += ['Supersedes: ' + ', '.join(link(x) for x in data['supersedes']) + '.', '']
        for peer_id in self.peers[rid]:
            lines += ['- ' + link(peer_id, 'peer ' + peer_id) + ' · ' + plain(self.by_id[peer_id]['overview']['title'])]
        active = [r for r in self.reviews[rid] if r not in self.replaced]
        active_bundles = [r for r in self.bundles[rid] if r not in self.replaced]
        unreviewed = not active and not active_bundles
        if unreviewed:
            lines += ['Unreviewed: no current independent review record exists.', '']
        judgments = defaultdict(set)
        for review_id in active:
            review = self.by_id[review_id]
            ov = review['overview_assessment']
            lines.append(f"- {link(review_id, 'current review ' + review_id)} · overview assessment: {ov['verdict']}")
            judgments['overview'].add(ov['verdict'])
            # Keep result-level conflict detection without displaying verdict counts.
            for key in ('assessment', 'lean', 'alignment', 'terminology'):
                for result in review['results']:
                    judgments[result['result'] + '/' + key].add(result[key]['verdict'])
        for review_id in active_bundles:
            review = self.by_id[review_id]
            scopes = []
            for row in review['overview_assessments']:
                source = row['record']
                verdict = row['assessment']['verdict']
                scopes.append(('work' if source == rid else 'peer') + ' overview ' + verdict)
                judgments['overview' if source == rid else source + '/overview'].add(verdict)
            lines += ['- ' + link(review_id, 'current review ' + review_id) + ' · ' + ', '.join(scopes)]
            for row in review['results']:
                source = row['source']
                name = source.get('result') or json.dumps(source, ensure_ascii=False, sort_keys=True)
                if source['record'] != rid:
                    name = source['record'] + '/' + name
                for key in ('assessment', 'lean', 'alignment'):
                    judgments[name + '/' + key].add(row[key]['verdict'])
        conflicts = []
        for key, values in judgments.items():
            if any({a, b} <= values for a, b in [('supported', 'not_supported'),
                                                ('accepted', 'rejected'), ('matches', 'differs')]):
                conflicts.append(key)
        if conflicts:
            lines += ['', 'Conflict: ' + ', '.join(plain(x) for x in sorted(conflicts)) + '. Read the current review records together.']
        if active or active_bundles or self.peers[rid]:
            lines.append('')
        if data['category'] == 'explore':
            lines += ["Exploration record: distinguish observations and conjectures from reviewed propositions. A review's acceptance applies only to the stated claims and scopes.", '']
        return lines, unreviewed, bool(conflicts)


def _layout(modules, entries):
    """Declared modules in order, general first; records not filed elsewhere fall into general.

    An undeclared general module carries no title or description of its own."""
    declared = list(modules or [])
    general = next((m for m in declared if m['name'] == GENERAL), {'name': GENERAL, 'title': None, 'description': None})
    others = [m for m in declared if m['name'] != GENERAL]
    filed = {rid for m in others for rid in m['records']}
    # Entries keep publication order whatever order the plan listed them in.
    ordered = [(rid, data) for rid, data in entries if rid not in filed]
    layout = [(dict(general, records=[rid for rid, _ in ordered]))]
    for module in others:
        wanted = set(module['records'])
        layout.append(dict(module, records=[rid for rid, _ in entries if rid in wanted]))
    return layout


def render_index_files(records, status=None, glossary=None, latest_plan=None, modules=None):
    """records are (id, manifest) pairs in publication order; status and glossary are
    the latest plan id when that plan has research-status.md or glossary.md; modules is
    that plan's `index.modules`. Returns {relative path: content} for every index file."""
    relations = _Relations(records)
    by_id = relations.by_id
    entries = [(rid, data) for rid, data in records if data['category'] in LABELS]
    layout = _layout(modules, entries)
    general, others = layout[0], layout[1:]
    rendered = {}  # module name -> (lines, unreviewed count, conflict count)
    for module in layout:
        prefix = '' if module['name'] == GENERAL else '../'
        lines, unreviewed, conflicts = [], 0, 0
        for rid in module['records']:
            entry, is_unreviewed, has_conflict = relations.entry(rid, by_id[rid], prefix)
            lines += entry
            unreviewed += is_unreviewed
            conflicts += has_conflict
        rendered[module['name']] = (lines, unreviewed, conflicts)

    lines = ['# Published knowledge index', '',
             'A navigation list the runner generates from the published records. Titles and summaries are the authors\' own text; '
             'the overview assessment is each review record\'s `overview_assessment` value and states whether the research\'s overview matches the reviewed scope of results. '
             '`supported` does not mean the research goal as a whole was solved or that every result is Lean-certified. '
             'Per-result mathematical verdicts, Lean verdicts, alignment with the exposition and their grounds are read in the linked review records.', '']
    lines += ['A peer is a response that read the output independently and worked its mathematics. A peer\'s new claims are uncertified until the later review. '
              'A bundle review judges the work and the peer together and does not certify an exploration\'s observations and conjectures wholesale.', '']
    lines += ['This file is the general module of the index. The last plan files records that only some tasks need into further modules, '
              'listed in the module table below and rendered under `index/`; open a module when its description concerns your task. '
              'A record filed in a module has the same standing as one listed here. Plan, peer and review records have no entries of their own.', '']
    if status:
        lines += [f'Current research status: [{status}/research-status.md]({status}/research-status.md)'
                  " (the last plan's research status)", '']
    if glossary:
        lines += [f'Global glossary: [{glossary}/glossary.md]({glossary}/glossary.md)'
                  ' (definitions of the mathematical objects and symbols shared across the run, updated by the last plan)', '']
    if latest_plan:
        lines += [f'Latest plan: {record_link(latest_plan)} (its reason, requests and index layout)', '']
    filed = sum(len(m['records']) for m in others)
    lines += [f'{_count(len(records), "published record")} · {_count(len(entries), "index entry", "index entries")} '
              '(plan, peer and review records not listed separately) · '
              f'{len(general["records"])} in the general module · {filed} filed in {_count(len(others), "other module")} · publication order · '
              "go from each record's `output.json` to its expositions, proofs and computation data.", '']
    goal_reviews = [rid for rid, data in records
                    if data['category'] == 'review' and data['target']['kind'] == 'goal'
                    and rid not in relations.replaced]
    if goal_reviews:
        lines += ['Goal reviews: ' + ', '.join(
            record_link(rid) + ' · ' + by_id[rid]['goal']['verdict'] for rid in goal_reviews), '']
    if others:
        # Not a heading: `## ` headings are reserved for record entries throughout the index.
        lines += ['**Modules filed by the last plan** (the entries below the table are the general module):', '',
                  '| Module | Description | Records | Unreviewed | Conflicts |', '|---|---|---|---|---|']
        for module in others:
            _, unreviewed, conflicts = rendered[module['name']]
            lines.append(f"| [{cell(module['title'])}](index/{module['name']}.md) | {cell(module['description'])} "
                         f"| {len(module['records'])} | {unreviewed} | {conflicts} |")
        lines.append('')
    if general['description'] is not None:
        lines += [f"**{plain(general['title'])}**: {plain(general['description'])}", '']
    lines += rendered[GENERAL][0]
    files = {'index.md': '\n'.join(lines).rstrip() + '\n'}
    for module in others:
        body, unreviewed, conflicts = rendered[module['name']]
        head = [f"# {plain(module['title'])}", '', plain(module['description']), '',
                f"Part of the index: [index.md](../index.md) · {_count(len(module['records']), 'record')} · "
                f"{unreviewed} unreviewed · {conflicts} with conflicting reviews · publication order. "
                'A record filed here has the same standing as one in the general module; '
                'read its current reviews in the linked review records.', '']
        files[f'index/{module["name"]}.md'] = '\n'.join(head + body).rstrip() + '\n'
    return files


def render_index(records, status=None, glossary=None, latest_plan=None, modules=None):
    """The general module (knowledge/index.md) alone; see render_index_files."""
    return render_index_files(records, status, glossary, latest_plan, modules)['index.md']
