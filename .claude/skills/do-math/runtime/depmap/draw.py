"""Draw a dependency map as SVG and as an HTML page. The input is the JSON that depmap.py derives.

This module reads the map's data and nothing of the runtime, so a map can be drawn again from its
JSON alone. `render(data)` returns the SVG, the page, the name of the layout that was used and,
when a requested layout could not be used, a sentence saying so.

Two layouts produce the same geometry (card rectangles, group rectangles, one path per edge):

    layered   written here, always available. Units are placed in layers from left to right so that
              every edge runs to a later layer, and each group is a horizontal band. An edge that
              spans several layers is led through a thread in each layer between, and the edges
              that leave one card with one meaning for one band share their threads, running as one
              line until they part. The order inside a layer is chosen by barycentre sweeps to
              reduce crossings, and the vertical positions are relaxed towards the neighbours.
              Edges are smooth curves.
    elk       ELK Layered through Node and the elkjs package, with groups as compound nodes and
              orthogonal routing. It can be used only when both are present: Node on the PATH, and
              elkjs in `node_modules/elkjs` beside this file, in the folder named by --elkjs, or
              in the folder named by the environment variable DO_MATH_ELKJS. Nothing installs it.

Which of the two draws better depends on the groups; this was observed on drawn maps. Where the
folders use each other in one direction, ELK gives the more compact drawing. Where they use each
other in a cycle, ELK places each group as one box along the flow and leads the lines of the cycle
backwards around the whole map, while a band has no such case. The cycle is the usual case, since
the definitions the root speaks of and the root itself stand in one folder. The existing generator
met the same difficulty with hand-chosen columns of chapters, which a script that runs without
judgment cannot choose. So `auto` takes ELK only when it is present and the groups are free of
cycles; `--layout elk` asks for it regardless.

What was taken from the dependency-map generator of the previous research (the folder
dependency_map/scripts/지도 of that research) and what was left there:

    taken     the layout runner (`빌드/배치.cjs`, here elk_layout.cjs) and the ELK option profile it
              was run with (`지도_설정.json`, 배치.프로필들.기본); the click viewer (`빌드/뷰어.py`, here
              viewer.html) with the attributes the drawing writes for it; the visual grammar of
              `지도_설정.json` and `빌드/그리기.py`: the line of each kind of edge (solid, dashed
              "through intermediate results", dotted reference, heavy "each complete"), the white
              casing under a line that separates crossings, rounded corners of orthogonal lines,
              the arrowheads, the palette that gives all edges leaving one card one colour, the
              group boxes, and the colours of cards, of the goal and of a completing proof.
    left      everything bound to a manuscript: chapter parsing, numbering and label resolution,
              translation, the stored graph and its overlay, candidate and review rounds; the
              compartments of a card with ports and endpoint lists; column placement of chapters,
              rails, bundles, nudging and untwisting; the label placer; the endpoint and geometry
              audits; font measurement with fontTools and embedded fonts, and inline TeX; PDF and
              PNG export through a headless browser. Text widths are estimated here from character
              classes, which is why cards keep a margin, and formulas are not typeset.
"""
from bisect import bisect_right, insort
import html
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import quote

HERE = Path(__file__).resolve().parent

# ----------------------------------------------------------------------------- the visual grammar

SANS = "'Segoe UI', 'Helvetica Neue', Arial, 'Noto Sans', sans-serif"
MONO = "Consolas, 'DejaVu Sans Mono', Menlo, monospace"
INK, SUBTLE, FAINT = '#203549', '#526A7D', '#60788B'
LINES = {'direct': ('', 2.4), 'contracted': ('12 7', 2.4), 'mention': ('2 7', 2.4), 'alternative': ('', 5.0),
         'refutation': ('16 6', 5.0)}
LEGEND = {'direct': 'named in the proof', 'contracted': 'through folded steps (named or counted on the line)',
          'mention': 'mentioned in the statement', 'alternative': 'a proof drawn as its own card, to its statement',
          'refutation': 'refutes the root: its statement is the negation of the root'}
ARROWS = {'alternative': (11, 4.6), 'refutation': (11, 4.6)}
ARROW = (8.2, 3.5)
CASING = 6
CORNER = 7
PALETTE = ['#256D9D', '#B56527', '#277E65', '#965C9D', '#B64258', '#5A778D', '#78842E', '#9B5A35', '#4D62A9',
           '#268487', '#9B4277', '#5F7844', '#6F65A5', '#AF7339', '#376E63', '#8D5969', '#1F6F8B', '#A0522D',
           '#2E8B57', '#7B3F9E', '#C0392B', '#4A6FA5', '#8A7A1E', '#B5651D', '#3B6E8F', '#6B8E23', '#9C4F96',
           '#2A7F62']
ALTERNATIVE_COLOUR = '#7350A3'
MENTION_COLOUR = '#7B92A4'
REFUTATION_COLOUR = '#A83232'
FIXED_COLOURS = {'alternative': ALTERNATIVE_COLOUR, 'mention': MENTION_COLOUR, 'refutation': REFUTATION_COLOUR}
GROUP_FILL, GROUP_STROKE = '#F8FAFC', '#BECBD6'
CARD = {'statement': ('#FFFFFF', '#8096A7', 1.6), 'definition': ('#F1F5F8', '#8096A7', 1.6),
        'proof': ('#EEE5F6', '#82719D', 1.6), 'root': ('#FFF0B8', '#8A7E58', 3.0)}
STANDINGS = {'no_proof': ('no proof', '#B64258'), 'not_confirmed': ('proof not confirmed', '#C8742B'),
             'held': ('correct, held back', '#C2A21E'), 'accepted': ('accepted', '#2E8B57')}
KINDS = {'theorem': 'statement', 'def': 'definition', 'opaque': 'opaque definition', 'inductive': 'inductive type'}
CARD_WORDS = {'statement': 'a statement', 'definition': 'a definition', 'proof': 'a proof on its own card', 'root': 'the root'}
ROOT_STATES = {'formal_proved': 'the root is proved, and the proof is complete in Lean',
               'informal_proved': 'the root is settled by accepted proofs; no proof of it is complete in Lean yet',
               'formal_refuted': 'the root is refuted, and the refutation is complete in Lean',
               'informal_refuted': 'the root is refuted by a settled statement; the refutation is not complete in Lean yet',
               'contested': 'the root and its negation both have settled proofs, so neither stands',
               'unresolved': 'the root is open'}
# What the words on a card mean, for a reader who does not know the research method. The page shows the
# entries whose words occur on the map, and each word of the selected card carries its entry.
GLOSSARY = {
    'unit': 'A result or a definition that one would name when saying how the proof goes. Every card is a unit.',
    'step': 'A result that lives inside one proof. A step has no card; it is folded into the lines that pass through it.',
    'root': 'The proposition the research set out to settle.',
    'statement': 'A proposition stated in Lean. Its card says how its proof stands.',
    'definition': 'A definition of the Lean library.',
    'opaque definition': 'A constant of the Lean library whose value Lean does not unfold.',
    'inductive type': 'A type of the Lean library that is given by its constructors.',
    'proof': 'A proof of a statement, drawn as a card of its own. The declaration of the statement itself carries no proof.',
    'another proof': 'A further proof of a statement that has one already. The proofs are separate arguments, not joint inputs.',
    'proof on a separate card': 'The declaration of this statement carries no proof. Its proof is the card that the heavy '
                                'line comes from.',
    'no proof': 'The statement stands without a proof.',
    'proof not confirmed': 'A proof was offered, and review found a gap in it or could not finish judging it.',
    'correct, held back': 'Review found the proof correct and did not accept it: it can still be made simpler, or it closes '
                          'a part by computation without saying why that part holds.',
    'accepted': 'Review found the proof correct and accepted it.',
    'settled': 'One of its proofs is accepted, and every statement that proof names is settled in the same way.',
    'not settled': 'No proof of it is accepted and rests on settled statements only.',
    'formal': 'One of its proofs is complete in Lean: it rests on nothing but the allowed axioms, with no gap below it.',
    'refuted': 'A statement that Lean confirmed as the negation of this one is settled.',
    'refutes the root': 'Lean confirmed that this statement is the negation of the root.',
    'from the literature': 'The result is taken from a published source, which its record names.'}

CARD_WIDTH = 300
TEXT_LEFT, TEXT_RIGHT, TEXT_TOP, TEXT_BOTTOM = 20, 12, 12, 12
LABEL_SIZE, NAME_SIZE, STATUS_SIZE = 17, 11.5, 12.5
LABEL_LINE, NAME_LINE, STATUS_LINE = 22, 15, 17
VIA_SIZE, VIA_HEIGHT, VIA_SHOWN = 12.5, 19, 3
GROUP_TITLE_SIZE = 19
MARGIN = 40

# the layered layout
LAYER_GAP, CARD_GAP, THREAD_GAP, THREAD = 170, 26, 12, 12
GROUP_PAD_X, GROUP_PAD_TOP, GROUP_PAD_BOTTOM, GROUP_GAP = 28, 50, 24, 30
PORT_GAP, PORT_MARGIN = 14, 12
SWEEPS, RELAXATIONS = 24, 24

# ELK: the profile the existing generator was run with, and the padding of a group around its cards
ELK_OPTIONS = {
    'elk.algorithm': 'layered', 'elk.direction': 'RIGHT', 'elk.edgeRouting': 'ORTHOGONAL',
    'elk.hierarchyHandling': 'INCLUDE_CHILDREN', 'elk.layered.mergeEdges': 'false',
    'elk.layered.mergeHierarchyEdges': 'true',
    'elk.layered.crossingMinimization.greedySwitchHierarchical.type': 'TWO_SIDED',
    'elk.layered.crossingMinimization.greedySwitch.type': 'TWO_SIDED',
    'elk.layered.nodePlacement.strategy': 'NETWORK_SIMPLEX', 'elk.layered.thoroughness': '30',
    'elk.randomSeed': '1', 'elk.spacing.nodeNode': '60', 'elk.spacing.edgeNode': '60', 'elk.spacing.edgeEdge': '28',
    'elk.layered.spacing.nodeNodeBetweenLayers': '90', 'elk.layered.spacing.edgeNodeBetweenLayers': '26',
    'elk.layered.spacing.edgeEdgeBetweenLayers': '20', 'elk.padding': '[top=20,left=20,bottom=20,right=20]',
    'elk.json.edgeCoords': 'ROOT', 'elk.json.shapeCoords': 'ROOT'}
ELK_GROUP_PADDING = f'[top={GROUP_PAD_TOP},left={GROUP_PAD_X},bottom={GROUP_PAD_BOTTOM},right={GROUP_PAD_X}]'
ELK_TIMEOUT = 600


# ----------------------------------------------------------------------------- text

def text_width(text, size, bold=False, mono=False):
    """An estimate of the width of a line, on the wide side, from classes of characters. No font is read."""
    if mono:
        return 0.602 * size * len(text)
    total = 0.0
    for char in text:
        if char in " .,:;'|!iljtfr()[]{}·":
            total += 0.34
        elif char in 'mwMW@%—':
            total += 0.92
        elif ord(char) >= 0x2E80:
            total += 1.0
        elif char.isupper() or char.isdigit():
            total += 0.66
        else:
            total += 0.56
    return total * size * (1.07 if bold else 1.0)


def wrap(text, size, width, bold=False, mono=False, after=' '):
    """Lines no wider than `width`, broken after the characters in `after`; a piece that is too long stays whole."""
    pieces, current = [], ''
    for char in text:
        current += char
        if char in after:
            pieces.append(current)
            current = ''
    if current:
        pieces.append(current)
    lines, line = [], ''
    for piece in pieces:
        if line and text_width((line + piece).rstrip(), size, bold, mono) > width:
            lines.append(line.rstrip())
            line = piece
        else:
            line += piece
    if line.strip():
        lines.append(line.rstrip())
    return lines or ['']


def proved_apart(data):
    """The statements that carry no proof themselves and have a proof drawn as a card of its own.

    The card of such a statement would say `no proof` beside `settled`, and the card of its proof `another
    proof` although it is the only one. Their words and the mark of the standing follow this set instead."""
    apart = {unit.get('proves') for unit in data['units'] if unit['role'] == 'proof'}
    return {unit['id'] for unit in data['units'] if unit['id'] in apart and unit.get('standing') == 'no_proof'}


def status_of(unit, bare=()):
    """What a card says under the name: the kind, and for a statement or a proof its standing.

    `bare` is the set of proved_apart: the statements whose proofs are all cards of their own."""
    words = ['root'] if unit.get('root') else []
    if unit.get('refuted'):
        words.append('refuted')
    if unit.get('refutes'):
        words.append('refutes the root')
    if unit['role'] == 'proof':
        words.append('proof' if unit.get('proves') in bare else 'another proof')
    else:
        words.append(KINDS.get(unit['kind'], unit['kind']))
    if unit.get('standing'):
        words.append('proof on a separate card' if unit['id'] in bare else STANDINGS[unit['standing']][0])
        words.append('settled' if unit.get('settled') else 'not settled')
        if unit.get('formal'):
            words.append('formal')
    if unit.get('source'):
        words.append('from the literature')
    return words


def card_of(unit, bare=()):
    """The lines of a card and its height. The width is fixed, so a layout never depends on a font."""
    inner = CARD_WIDTH - TEXT_LEFT - TEXT_RIGHT
    label = wrap(unit['label'], LABEL_SIZE, inner, bold=True)
    name = wrap(unit['id'], NAME_SIZE, inner, mono=True, after='.')
    status, line = [], ''
    for word in status_of(unit, bare):  # a line never ends in a separator
        longer = line + ' · ' + word if line else word
        if line and text_width(longer, STATUS_SIZE) > inner:
            status.append(line)
            line = word
        else:
            line = longer
    status.append(line)
    height = TEXT_TOP + LABEL_LINE * len(label) + 3 + NAME_LINE * len(name) + 5 + STATUS_LINE * len(status) + TEXT_BOTTOM - 5
    return {'label': label, 'name': name, 'status': status, 'width': CARD_WIDTH, 'height': height}


def via_text(data, edge, shown=VIA_SHOWN):
    """The words written on a line that passes through folded elements; the data keeps the whole list.

    At most `shown` of them are named and the rest counted; with none named the words give the number alone."""
    names = [data['folded'].get(name, {}).get('label') or name for name in edge['via']]
    if not names:
        return None
    if not shown:
        return f"via {len(names)} step{'s' if len(names) > 1 else ''}"
    more = len(names) - shown
    return 'via ' + ', '.join(names[:shown]) + (f' and {more} more' if more > 0 else '')


def via_box(words):
    return text_width(words, VIA_SIZE) + 12, VIA_HEIGHT


# ----------------------------------------------------------------------------- the layered layout

def layered(data, cards):
    """Place the units in layers from left to right, groups as horizontal bands, and route every edge."""
    ids = [unit['id'] for unit in data['units']]
    pairs = [(edge['source'], edge['target']) for edge in data['edges']]
    leaving = {name: [] for name in ids}
    for number, (source, target) in enumerate(pairs):
        leaving[source].append((target, number))

    # An edge that closes a cycle is turned around for the layout only; it is drawn in its own direction.
    state, turned = {}, set()
    for start in ids:
        if start in state:
            continue
        state[start] = 'open'
        stack = [(start, iter(leaving[start]))]
        while stack:
            name, rest = stack[-1]
            for target, number in rest:
                if state.get(target) == 'open':
                    turned.add(number)
                elif target not in state:
                    state[target] = 'open'
                    stack.append((target, iter(leaving[target])))
                    break
            else:
                state[name] = 'done'
                stack.pop()
    oriented = [(t, s) if number in turned else (s, t) for number, (s, t) in enumerate(pairs)]
    before, after = {name: [] for name in ids}, {name: [] for name in ids}
    for a, b in oriented:
        after[a].append(b)
        before[b].append(a)

    # Layers: the longest path from the sources, then every unit moved up to just before its first user.
    waiting = {name: len(before[name]) for name in ids}
    ready, sequence = [name for name in ids if not waiting[name]], []
    while ready:
        name = ready.pop(0)
        sequence.append(name)
        for target in after[name]:
            waiting[target] -= 1
            if not waiting[target]:
                ready.append(target)
    layer = {}
    for name in sequence:
        layer[name] = max((layer[p] + 1 for p in before[name]), default=0)
    for name in reversed(sequence):
        if after[name]:
            layer[name] = min(layer[t] for t in after[name]) - 1
    count = max(layer.values(), default=0) + 1

    # Bands: one per group, in the order of where their units stand from left to right.
    group = {unit['id']: unit['group'] for unit in data['units']}
    members = {}
    for name in ids:
        members.setdefault(group[name], []).append(name)
    bands = sorted(members, key=lambda g: (sum(layer[n] for n in members[g]) / len(members[g]), g))
    band = {name: bands.index(group[name]) for name in ids}

    # An edge across several layers is led through a thread in each layer between, in the band it enters.
    # The edges of one net share their threads: they leave one card with one meaning for one band, run
    # together as one line and part where their targets are. A definition that a hundred statements
    # mention then takes one thread in a layer and not a hundred.
    height = {name: cards[name]['height'] for name in ids}
    up, down = {name: [] for name in ids}, {name: [] for name in ids}
    chains, nets = [], []
    for number, (a, b) in enumerate(oriented):
        net = ('turned', number) if number in turned else (a, data['edges'][number]['kind'], band[b])
        chain = [a]
        for at in range(layer[a] + 1, layer[b]):
            key = ('thread', net, at)
            if key not in layer:
                layer[key], height[key], band[key], up[key], down[key] = at, THREAD, band[b], [], []
            chain.append(key)
        chain.append(b)
        chains.append(chain)
        nets.append(net)
        for first, second in zip(chain, chain[1:]):
            if second not in down[first]:
                down[first].append(second)
                up[second].append(first)

    rows = [[] for _ in range(count)]
    for key in layer:
        rows[layer[key]].append(key)
    for row in rows:
        row.sort(key=lambda key: band[key])

    def ranks(row):
        """A number per element of a layer that respects the bands and the order inside each."""
        sizes = {}
        for key in row:
            sizes[band[key]] = sizes.get(band[key], 0) + 1
        seen, found = {}, {}
        for key in row:
            seen[band[key]] = seen.get(band[key], 0) + 1
            found[key] = band[key] + seen[band[key]] / (sizes[band[key]] + 1)
        return found

    rank = {}
    for row in rows:
        rank.update(ranks(row))

    def crossings():
        total = 0
        for row in rows[:-1]:
            ends = sorted((rank[key], rank[other]) for key in row for other in down[key])
            seen = []
            for _, end in ends:
                total += len(seen) - bisect_right(seen, end)
                insort(seen, end)
        return total

    best, least = [list(row) for row in rows], crossings()
    for sweep in range(SWEEPS):
        if not least:
            break
        near = up if sweep % 2 == 0 else down
        for index in (range(count) if sweep % 2 == 0 else range(count - 1, -1, -1)):
            row = rows[index]
            centre = {key: sum(rank[n] for n in near[key]) / len(near[key]) if near[key] else rank[key] for key in row}
            row.sort(key=lambda key: (band[key], centre[key]))
            rank.update(ranks(row))
        found = crossings()
        if found < least:
            best, least = [list(row) for row in rows], found
    rows = best

    # Coordinates. A band is as tall as its tallest layer; inside it every layer is first centred, then relaxed.
    def gap(first, second):
        return CARD_GAP if isinstance(first, str) and isinstance(second, str) else THREAD_GAP

    parts = [{} for _ in range(count)]
    for index, row in enumerate(rows):
        for key in row:
            parts[index].setdefault(band[key], []).append(key)
    need = [0.0] * len(bands)
    for index in range(count):
        for number, keys in parts[index].items():
            tall = sum(height[key] for key in keys) + sum(gap(a, b) for a, b in zip(keys, keys[1:]))
            need[number] = max(need[number], tall)
    above, below, cursor = [], [], 0.0
    for number in range(len(bands)):
        above.append(cursor + GROUP_PAD_TOP)
        below.append(above[-1] + need[number])
        cursor = below[-1] + GROUP_PAD_BOTTOM + GROUP_GAP
    left = {key: GROUP_PAD_X + layer[key] * (CARD_WIDTH + LAYER_GAP) for key in layer}
    top = {}
    for index in range(count):
        for number, keys in parts[index].items():
            tall = sum(height[key] for key in keys) + sum(gap(a, b) for a, b in zip(keys, keys[1:]))
            y = above[number] + (need[number] - tall) / 2
            for position, key in enumerate(keys):
                top[key] = y
                y += height[key] + (gap(key, keys[position + 1]) if position + 1 < len(keys) else 0)

    def middle(key):
        return top[key] + height[key] / 2

    for sweep in range(RELAXATIONS):
        for index in (range(count) if sweep % 2 == 0 else range(count - 1, -1, -1)):
            for number, keys in parts[index].items():
                wanted = []
                for key in keys:
                    near = up[key] + down[key]
                    centre = sum(middle(n) for n in near) / len(near) if near else middle(key)
                    wanted.append(centre - height[key] / 2)
                floor = above[number]
                for position, key in enumerate(keys):
                    wanted[position] = max(wanted[position], floor)
                    if position + 1 < len(keys):
                        floor = wanted[position] + height[key] + gap(key, keys[position + 1])
                ceiling = below[number]
                for position in range(len(keys) - 1, -1, -1):
                    key = keys[position]
                    wanted[position] = min(wanted[position], ceiling - height[key])
                    if position:
                        ceiling = wanted[position] - gap(keys[position - 1], key)
                    top[key] = wanted[position]

    # Where a line meets a card: the ends on one side are spread in the order of where they lead. A net
    # leaves its card at one point, so that its edges are one line until they part; every edge enters at its own.
    sides = {}
    for number, chain in enumerate(chains):
        sides.setdefault((chain[0], 'right'), {}).setdefault(nets[number], []).append(middle(chain[1]))
        sides.setdefault((chain[-1], 'left'), {})[number] = [middle(chain[-2])]
    port = {}
    for (name, side), ends in sides.items():
        order = sorted(ends, key=lambda end: (sum(ends[end]) / len(ends[end]), str(end)))
        step = min(PORT_GAP, (height[name] - 2 * PORT_MARGIN) / max(len(order) - 1, 1))
        for position, end in enumerate(order):
            port[(end, side)] = middle(name) + (position - (len(order) - 1) / 2) * step

    routes = []
    for number, chain in enumerate(chains):
        points = [(left[chain[0]] + CARD_WIDTH, port[(nets[number], 'right')])]
        for key in chain[1:-1]:
            points += [(left[key], middle(key)), (left[key] + CARD_WIDTH, middle(key))]
        points.append((left[chain[-1]], port[(number, 'left')]))
        routes.append(points[::-1] if number in turned else points)

    boxes = {name: (left[name], top[name], CARD_WIDTH, height[name]) for name in ids}
    frames = {}
    for number, key in enumerate(bands):
        x0 = min(left[name] for name in members[key]) - GROUP_PAD_X
        x1 = max(left[name] for name in members[key]) + CARD_WIDTH + GROUP_PAD_X
        x1 = max(x1, x0 + text_width(key, GROUP_TITLE_SIZE, bold=True) + 44)
        frames[key] = (x0, above[number] - GROUP_PAD_TOP, x1 - x0, need[number] + GROUP_PAD_TOP + GROUP_PAD_BOTTOM)

    # A label is put on a stretch between two layers, nearest the target first, where the line is the edge's own,
    # at the first place where it covers no card and no other label. The names of three steps are often wider
    # than the space between two layers, and a label that found no free place used to lie across the cards beside
    # it and hide their words. So a label that finds no place names one step fewer and tries again, down to the
    # number of steps alone; the data keeps every name, and the page lists them for the selected unit.
    taken = [(x - 4, y - 4, w + 8, h + 8) for x, y, w, h in boxes.values()]
    labels = []
    for number, edge in enumerate(data['edges']):
        if not edge['via']:
            labels.append((None, None))
            continue
        points = routes[number]
        stretches = [(points[i], points[i + 1]) for i in range(0, len(points) - 1, 2)][::-1][:3]
        found, words = None, None
        for shown in range(VIA_SHOWN, -1, -1):
            shorter = via_text(data, edge, shown)
            if shorter == words:
                continue
            words = shorter
            wide, tall = via_box(words)
            places = []
            for t in (0.5, 0.32, 0.68):
                for (x1, y1), (x2, y2) in stretches:
                    x, y = curve_point(x1, y1, x2, y2, t)
                    places.append((x - wide / 2, y - tall / 2, wide, tall))
            found = next((place for place in places if not any(overlap(place, other) for other in taken)), None)
            if found:
                break
        found = found or places[0]  # nothing is free: the shortest words, where the line is most its own
        taken.append(found)
        labels.append((found, words))

    right = max([x + w for x, _, w, _ in frames.values()] + [x + w for x, _, w, _ in boxes.values()])
    shared = {net: index for index, net in enumerate(dict.fromkeys(nets))}
    return {'engine': 'layered', 'width': right, 'height': cursor - GROUP_GAP, 'cards': boxes, 'groups': frames,
            'edges': [{'points': routes[n], 'smooth': True, 'label': labels[n][0], 'words': labels[n][1],
                       'net': shared[nets[n]]} for n in range(len(pairs))]}


def curve_point(x1, y1, x2, y2, t):
    """A point of the curve that joins two points with horizontal tangents (see smooth_path)."""
    xm = (x1 + x2) / 2
    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
    return a * x1 + (b + c) * xm + d * x2, (a + b) * y1 + (c + d) * y2


def overlap(first, second):
    return (first[0] < second[0] + second[2] and second[0] < first[0] + first[2]
            and first[1] < second[1] + second[3] and second[1] < first[1] + first[3])


# ----------------------------------------------------------------------------- the ELK layout

def find_elk(explicit=None):
    """(the folder of elkjs, None) when ELK can be used, else (None, what is missing)."""
    if not shutil.which('node'):
        return None, 'Node on the PATH'
    places = [explicit] if explicit else [os.environ.get('DO_MATH_ELKJS'), HERE / 'node_modules' / 'elkjs']
    for place in places:
        if place and (Path(place) / 'package.json').is_file():
            return Path(place), None
    return None, ('an elkjs package in ' + str(explicit) if explicit else
                  'the elkjs package (in depmap/node_modules/elkjs, in the folder named by --elkjs, or by DO_MATH_ELKJS)')


def elk(data, cards, package):
    """The same geometry from ELK Layered: groups are compound nodes and edges are routed orthogonally."""
    ids = [unit['id'] for unit in data['units']]
    number = {name: index for index, name in enumerate(ids)}
    children = [{'id': f'g{index}', 'layoutOptions': {'elk.padding': ELK_GROUP_PADDING},
                 'children': [{'id': f'n{number[name]}', 'width': cards[name]['width'], 'height': cards[name]['height']}
                              for name in group['units']]}
                for index, group in enumerate(data['groups'])]
    edges = []
    for index, edge in enumerate(data['edges']):
        item = {'id': f'e{index}', 'sources': [f"n{number[edge['source']]}"], 'targets': [f"n{number[edge['target']]}"]}
        words = via_text(data, edge)
        if words:
            wide, tall = via_box(words)
            item['labels'] = [{'id': f'l{index}', 'text': words, 'width': wide, 'height': tall}]
        edges.append(item)
    graph = {'id': 'root', 'layoutOptions': ELK_OPTIONS, 'children': children, 'edges': edges}
    with tempfile.TemporaryDirectory(prefix='depmap-elk-') as folder:
        source, target = Path(folder) / 'input.json', Path(folder) / 'output.json'
        source.write_text(json.dumps(graph), encoding='utf-8')
        try:
            done = subprocess.run(['node', str(HERE / 'elk_layout.cjs'), str(package), str(source), str(target)],
                                  capture_output=True, text=True, encoding='utf-8', errors='replace',
                                  timeout=ELK_TIMEOUT, stdin=subprocess.DEVNULL)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise RuntimeError(str(error))
        if done.returncode != 0 or not target.is_file():
            raise RuntimeError((done.stderr or done.stdout or 'no output').strip()[-600:])
        raw = json.loads(target.read_text(encoding='utf-8'))
    placed, routed = {}, {}

    def walk(node):
        placed[node['id']] = node
        for edge in node.get('edges') or []:
            routed[edge['id']] = edge
        for child in node.get('children') or []:
            walk(child)

    walk(raw)
    routes = []
    for index in range(len(edges)):
        sections = routed[f'e{index}'].get('sections') or []
        if len(sections) != 1:
            raise RuntimeError(f'ELK returned {len(sections)} sections for an edge; one continuous route is expected')
        section = sections[0]
        points = [section['startPoint'], *(section.get('bendPoints') or []), section['endPoint']]
        found = (routed[f'e{index}'].get('labels') or [None])[0]
        label = (found['x'], found['y'], found['width'], found['height']) if found and 'x' in found else None
        routes.append({'points': [(p['x'], p['y']) for p in points], 'smooth': False, 'label': label,
                       'words': via_text(data, data['edges'][index]), 'net': index})

    def box(key):
        node = placed[key]
        return node['x'], node['y'], node['width'], node['height']

    return {'engine': f"ELK Layered (elkjs {raw.get('__elk_version', '?')})", 'width': raw['width'], 'height': raw['height'],
            'cards': {name: box(f'n{number[name]}') for name in ids},
            'groups': {group['id']: box(f'g{index}') for index, group in enumerate(data['groups'])},
            'edges': routes}


# ----------------------------------------------------------------------------- SVG

def esc(text):
    return html.escape(str(text), quote=True)


def fmt(value):
    return f'{value:.2f}'.rstrip('0').rstrip('.')


def smooth_path(points):
    """Curves with horizontal tangents between layers, straight across a layer."""
    parts = [f'M {fmt(points[0][0])} {fmt(points[0][1])}']
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        if abs(y1 - y2) < 0.01:
            parts.append(f'L {fmt(x2)} {fmt(y2)}')
        else:
            xm = (x1 + x2) / 2
            parts.append(f'C {fmt(xm)} {fmt(y1)} {fmt(xm)} {fmt(y2)} {fmt(x2)} {fmt(y2)}')
    return ' '.join(parts)


def cornered_path(points, radius=CORNER):
    """A polyline with rounded corners; the radius shrinks on a short stretch."""
    parts = [f'M {fmt(points[0][0])} {fmt(points[0][1])}']
    for a, b, c in zip(points, points[1:], points[2:]):
        u, v = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
        du, dv = math.hypot(*u), math.hypot(*v)
        if not du or not dv:
            continue
        r = min(radius, du / 2, dv / 2)
        parts.append(f'L {fmt(b[0] + u[0] / du * r)} {fmt(b[1] + u[1] / du * r)}')
        parts.append(f'Q {fmt(b[0])} {fmt(b[1])} {fmt(b[0] + v[0] / dv * r)} {fmt(b[1] + v[1] / dv * r)}')
    parts.append(f'L {fmt(points[-1][0])} {fmt(points[-1][1])}')
    return ' '.join(parts)


def text(x, y, content, size, colour=INK, weight=400, anchor='start', family=None):
    font = f' font-family="{esc(family)}"' if family else ''
    bold = f' font-weight="{weight}"' if weight != 400 else ''
    return (f'<text x="{fmt(x)}" y="{fmt(y)}" font-size="{size}" fill="{colour}" text-anchor="{anchor}"{bold}{font}>'
            f'{esc(content)}</text>')


def dashed(dash):
    """The attribute of a dash pattern; a solid line carries none."""
    return f' stroke-dasharray="{dash}"' if dash else ''


def occurring(data, bare=()):
    """What a legend of this map has to explain: the kinds of line, the kinds of card and the standings that occur.

    Each is listed in the order of the visual grammar. The standing of a statement whose proof is a card of
    its own is not marked on its card, so it does not count."""
    kinds = {edge['kind'] for edge in data['edges']}
    roles = {'root' if unit.get('root') else unit['role'] for unit in data['units']}
    standings = {unit['standing'] for unit in data['units'] if unit.get('standing') and unit['id'] not in bare}
    return ([kind for kind in LEGEND if kind in kinds], [role for role in CARD if role in roles],
            [standing for standing in STANDINGS if standing in standings])


def legend(limit, y, data, bare=()):
    """Under the title: the lines, the cards and the standings that occur on this map. Returns the parts and the last baseline.

    The entries run from left to right and continue on a new row where the next would pass `limit`."""
    parts, x = [], MARGIN
    kinds, roles, standings = occurring(data, bare)

    def place(width):
        nonlocal x, y
        if x > MARGIN and x + width > limit:
            x, y = MARGIN, y + 26
        x += width
        return x - width

    for kind in kinds:
        (dash, width), words = LINES[kind], LEGEND[kind]
        colour = FIXED_COLOURS.get(kind, '#4B6072')
        at = place(62 + text_width(words, 14) + 30)
        parts.append(f'<path d="M {fmt(at)} {y - 5} h 46" fill="none" stroke="{colour}" stroke-width="{width}"{dashed(dash)}/>')
        parts.append(f'<path d="M {fmt(at + 54)} {y - 5} l -9 -4 v 8 Z" fill="{colour}"/>')
        parts.append(text(at + 62, y, words, 14, SUBTLE))
    for role in roles:
        (fill, border, _), words = CARD[role], CARD_WORDS[role]
        at = place(26 + text_width(words, 14) + 22)
        parts.append(f'<rect x="{fmt(at)}" y="{y - 12}" width="20" height="14" rx="3" fill="{fill}" stroke="{border}" '
                     f'stroke-width="1.4"/>')
        parts.append(text(at + 26, y, words, 14, SUBTLE))
    for standing in standings:
        words, colour = STANDINGS[standing]
        at = place(14 + text_width(words, 14) + 22)
        parts.append(f'<rect x="{fmt(at)}" y="{y - 12}" width="8" height="14" rx="2" fill="{colour}"/>')
        parts.append(text(at + 14, y, words, 14, SUBTLE))
    if kinds:
        words = 'lines that leave one card have one colour'
        parts.append(text(place(text_width(words, 14) + 22), y, words, 14, SUBTLE))
    return parts, y


def scope_words(data):
    """Which units the map shows, in words."""
    if data.get('scope') == 'all':
        return 'every unit of the library'
    refuted = str(data.get('root_state') or '').endswith('refuted')
    return 'the units the refutation of the root rests on' if refuted else 'the units the proof of the root rests on'


def state_words(data):
    """How the root stands, in words; a state this code does not know is shown as it is."""
    return ROOT_STATES.get(data.get('root_state')) or f"root state: {data.get('root_state')}"


def svg_of(data, cards, geometry, bare=()):
    units = {unit['id']: unit for unit in data['units']}
    counts = data['counts']
    library = f" · library {data['library']}, revision {data.get('revision')}" if data.get('library') else ''
    subtitle = (f"{data.get('root_label') or ''} · {state_words(data)} · {counts['units']} units in {counts['groups']} groups, "
                f"{counts['edges']} lines, {len(data.get('folded') or {})} steps folded into the lines · "
                f"{scope_words(data)}{library}")
    width = max(geometry['width'], text_width(subtitle, 15), text_width(data['title'], 30, bold=True), 640) + 2 * MARGIN
    head, baseline = legend(width - MARGIN, 104, data, bare)
    header = baseline + 28
    height = geometry['height'] + header + MARGIN
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width)}" height="{fmt(height)}" '
             f'viewBox="0 0 {fmt(width)} {fmt(height)}" font-family="{esc(SANS)}">',
             f'<title>{esc(data["title"])}</title>',
             f'<rect width="{fmt(width)}" height="{fmt(height)}" fill="#FFFFFF"/>',
             text(MARGIN, 46, data['title'], 30, weight=700), text(MARGIN, 74, subtitle, 15, SUBTLE)]
    parts += head
    parts.append(f'<g id="drawing" transform="translate({MARGIN},{header})">')

    for group in data['groups']:
        x, y, w, h = geometry['groups'][group['id']]
        parts.append(f'<g class="group" data-group="{esc(group["id"])}"><rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" '
                     f'height="{fmt(h)}" rx="14" fill="{GROUP_FILL}" stroke="{GROUP_STROKE}" stroke-width="1.8"/>'
                     + text(x + 20, y + 32, group['label'], GROUP_TITLE_SIZE, weight=700) + '</g>')

    # Every edge that leaves one card has one colour; the cards are taken in the order they stand in.
    sources = sorted({edge['source'] for edge in data['edges'] if edge['kind'] in ('direct', 'contracted')},
                     key=lambda name: (geometry['cards'][name][0], geometry['cards'][name][1], name))
    colour = {name: PALETTE[index % len(PALETTE)] for index, name in enumerate(sources)}
    # A white casing under a line separates it from the lines it crosses. The edges of one net run together
    # before they part, so the casings of a net are all drawn before its lines; otherwise the casing of one
    # edge would cut the line of another where it leaves the common stretch, and a branch would read as a crossing.
    parts.append('<g id="routes">')
    behind = {'mention': 0, 'contracted': 1, 'direct': 2, 'alternative': 3, 'refutation': 4}
    nets = {}
    for index in sorted(range(len(data['edges'])), key=lambda i: (behind[data['edges'][i]['kind']], i)):
        nets.setdefault(geometry['edges'][index]['net'], []).append(index)
    for indices in nets.values():
        casings, lines = [], []
        for index in indices:
            edge, route = data['edges'][index], geometry['edges'][index]
            dash, stroke = LINES[edge['kind']]
            ink = FIXED_COLOURS.get(edge['kind']) or colour[edge['source']]
            long, half = ARROWS.get(edge['kind'], ARROW)
            points = list(route['points'])
            (px, py), (ex, ey) = points[-2], points[-1]
            if route['smooth']:
                dx, dy = (1.0 if ex >= px else -1.0), 0.0
            else:
                span = math.hypot(ex - px, ey - py) or 1.0
                dx, dy = (ex - px) / span, (ey - py) / span
            points[-1] = (ex - dx * (long - 1), ey - dy * (long - 1))
            d = smooth_path(points) if route['smooth'] else cornered_path(points)
            bx, by = ex - dx * long, ey - dy * long
            tip = (f'M {fmt(ex)} {fmt(ey)} L {fmt(bx - dy * half)} {fmt(by + dx * half)} '
                   f'L {fmt(bx + dy * half)} {fmt(by - dx * half)} Z')
            casings.append(f'<path class="casing" d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{stroke + CASING}" '
                           f'stroke-linecap="round" stroke-linejoin="round"/>')
            lines.append(
                f'<g class="edge" id="e{index}" data-source="{esc(edge["source"])}" data-target="{esc(edge["target"])}" '
                f'data-kind="{edge["kind"]}">'
                f'<path class="wire" d="{d}" fill="none" stroke="{ink}" stroke-width="{stroke}"{dashed(dash)} '
                f'stroke-linecap="round" stroke-linejoin="round"/>'
                f'<path class="arrow" d="{tip}" fill="{ink}"/></g>')
        parts += casings + lines
    parts.append('</g>')

    parts.append('<g id="cards">')
    for name, unit in units.items():
        x, y, w, h = geometry['cards'][name]
        card = cards[name]
        fill, border, thick = CARD['root' if unit.get('root') else unit['role']]
        tooltip = unit['id'] + (' — ' + unit['description'] if unit.get('description') else '')
        parts.append(f'<g class="node" data-node="{esc(name)}" data-role="{unit["role"]}" '
                     f'data-status="{esc(" · ".join(status_of(unit, bare)))}"><title>{esc(tooltip)}</title>'
                     f'<rect class="card" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="8" '
                     f'fill="{fill}" stroke="{border}" stroke-width="{thick}"/>')
        if unit.get('standing') and name not in bare:  # the proof of a statement in `bare` is a card of its own
            parts.append(f'<path class="standing" d="M {fmt(x + 8)} {fmt(y)} Q {fmt(x)} {fmt(y)} {fmt(x)} {fmt(y + 8)} '
                         f'V {fmt(y + h - 8)} Q {fmt(x)} {fmt(y + h)} {fmt(x + 8)} {fmt(y + h)} Z" '
                         f'fill="{STANDINGS[unit["standing"]][1]}"/>')
        line = y + TEXT_TOP
        for words in card['label']:
            line += LABEL_LINE
            parts.append(text(x + TEXT_LEFT, line - 5, words, LABEL_SIZE, weight=700))
        line += 3
        for words in card['name']:
            line += NAME_LINE
            parts.append(text(x + TEXT_LEFT, line - 4, words, NAME_SIZE, FAINT, family=MONO))
        line += 5
        for words in card['status']:
            line += STATUS_LINE
            parts.append(text(x + TEXT_LEFT, line - 5, words, STATUS_SIZE, SUBTLE))
        parts.append('</g>')
    parts.append('</g>')

    parts.append('<g id="labels">')
    for index, edge in enumerate(data['edges']):
        place, words = geometry['edges'][index]['label'], geometry['edges'][index].get('words')
        if not place or not words:
            continue
        x, y, w, h = place
        whole = 'via ' + ', '.join(edge['via'])
        parts.append(f'<g class="route-label" data-edge="e{index}"><title>{esc(whole)}</title>'
                     f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="4" fill="#FFFFFF" '
                     f'fill-opacity="0.93" stroke="#DDE5EB" stroke-width="1"/>'
                     + text(x + w / 2, y + h - 5.5, words, VIA_SIZE, INK, anchor='middle') + '</g>')
    parts.append('</g></g></svg>')
    return '\n'.join(parts) + '\n'


def guide_of(data, bare=()):
    """What the page's panel says about this map before a unit is chosen, as HTML: what it shows and how to read it.

    It is written here, beside the visual grammar, so that the page explains the lines, the cards and the
    standings in the colours and dashes they are drawn with, and only those that occur on this map. The
    glossary holds the words of the cards of this map; the page also shows an entry with each word of a
    chosen card."""
    counts, units = data['counts'], {unit['id']: unit for unit in data['units']}
    name = esc(data.get('root_label') or data['root'])
    if data['root'] in units:
        name = f'<a href="#node={quote(data["root"], safe="")}">{name}</a>'
    steps = len(data.get('folded') or {})
    folded = (f' {steps} smaller step{"s have" if steps > 1 else " has"} no card and {"are" if steps > 1 else "is"} folded '
              f'into the lines that pass through {"them" if steps > 1 else "it"}.') if steps else ''
    parts = [f'<p class="about">The root of this research is {name}: {esc(state_words(data))}. The map shows '
             f'{esc(scope_words(data))}: {counts["units"]} units, each a card, in {counts["groups"]} groups, joined by '
             f'{counts["edges"]} lines.{folded}</p>']
    kinds, roles, standings = occurring(data, bare)
    parts.append('<div class="legend"><h3>How to read the map</h3>'
                 '<p>An arrow runs from what is used to what uses it, so the map is read from the left, where the '
                 'definitions and the first results stand, towards the root. Lines that leave one card have one colour.</p><ul>')
    for kind in kinds:
        dash, width = LINES[kind]
        colour = FIXED_COLOURS.get(kind, '#4B6072')
        parts.append(f'<li><svg class="sample" width="56" height="12" viewBox="0 0 56 12" aria-hidden="true">'
                     f'<path d="M 1 6 h 44" fill="none" stroke="{colour}" stroke-width="{width}"{dashed(dash)}/>'
                     f'<path d="M 55 6 l -10 -4.5 v 9 Z" fill="{colour}"/></svg>{esc(LEGEND[kind])}</li>')
    for role in roles:
        fill, border, _ = CARD[role]
        parts.append(f'<li><span class="sample card" style="background:{fill};border-color:{border}"></span>'
                     f'{esc(CARD_WORDS[role])}</li>')
    for standing in standings:
        words, colour = STANDINGS[standing]
        parts.append(f'<li><span class="sample bar" style="background:{colour}"></span>'
                     f'the bar at the left of a card: {esc(words)}</li>')
    parts.append('</ul></div>')
    said = {word for unit in data['units'] for word in status_of(unit, bare)}
    parts.append('<div class="glossary"><h3>The words on the cards</h3><dl>')
    for word, meaning in GLOSSARY.items():
        if word in said or word in ('unit', 'step'):
            parts.append(f'<dt data-word="{esc(word)}">{esc(word)}</dt><dd>{esc(meaning)}</dd>')
    parts.append('</dl></div>')
    return '\n'.join(parts)


def page_of(svg, data, bare=()):
    """The viewer page: the same SVG inline, the guide to this map, and the map's data for the panel beside it."""
    template = (HERE / 'viewer.html').read_text(encoding='utf-8')
    head, rest = template.split('__GUIDE__', 1)
    middle, rest = rest.split('__SVG__', 1)
    between, tail = rest.split('__DATA__', 1)
    payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    return head.replace('__TITLE__', esc(data['title'])) + guide_of(data, bare) + middle + svg + between + payload + tail


def groups_in_a_cycle(data):
    """Whether the groups depend on each other in a cycle, as when one folder holds both the definitions and the root."""
    group = {unit['id']: unit['group'] for unit in data['units']}
    after = {key: set() for key in group.values()}
    for edge in data['edges']:
        if group[edge['source']] != group[edge['target']]:
            after[group[edge['source']]].add(group[edge['target']])
    left = set(after)
    while left:
        free = {key for key in left if not any(key in after[other] for other in left)}
        if not free:
            return True
        left -= free
    return False


def render(data, layout='auto', elkjs=None):
    """(SVG, page, layout used, note). `layout` is 'auto', 'layered' or 'elk'.

    'auto' takes ELK when it is present and the groups do not depend on each other in a cycle. ELK
    draws a group as one box placed along the flow, so a cycle among groups sends lines backwards
    around the whole drawing; the built-in layout draws a group as a band and has no such case."""
    bare = proved_apart(data)
    cards = {unit['id']: card_of(unit, bare) for unit in data['units']}
    geometry, note = None, None
    if layout in ('auto', 'elk'):
        package, missing = find_elk(elkjs)
        if package is None and (layout == 'elk' or elkjs):
            if layout == 'elk':
                raise ValueError('the ELK layout needs ' + missing)
            note = f'ELK was not used because it needs {missing}; the built-in layered layout was used.'
        elif package is not None and layout == 'auto' and groups_in_a_cycle(data):
            note = ('ELK is present and was not used: the groups depend on each other in a cycle, which ELK draws with '
                    'lines running backwards around the map. --layout elk draws it with ELK all the same.')
        elif package is not None:
            try:
                geometry = elk(data, cards, package)
            except RuntimeError as error:
                if layout == 'elk':
                    raise ValueError('the ELK layout failed: ' + str(error))
                note = f'ELK failed ({error}); the built-in layered layout was used.'
    if geometry is None:
        geometry = layered(data, cards)
    svg = svg_of(data, cards, geometry, bare)
    return svg, page_of(svg, data, bare), geometry['engine'], note
