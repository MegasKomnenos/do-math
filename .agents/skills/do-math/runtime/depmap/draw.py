"""Draw a dependency map as SVG and as an HTML page. The input is the JSON that depmap.py derives.

This module reads the map's data and nothing of the runtime, so a map can be drawn again from its
JSON alone. `render(data)` returns the SVG and the page.

The drawing explains itself to a reader who was not told how it is made: its legend shows the lines,
the cards and the standings that occur on it, and the page receives the same legend, a sentence on
what the map shows and the meaning of the words on its cards (`guide_of`). The page is viewer.html
with the drawing, that guide and the data put in; what it does with them is described at its head.

The layout is written here and needs nothing beyond Python. It gives each card and each group a
rectangle and each edge one path. Units are placed in layers from left to right so that every
edge runs to a later layer, and each group is a horizontal band. The order inside a layer is
chosen by barycentre sweeps over the edges to the next layer, and the vertical positions are
relaxed towards those neighbours. The lines run at right angles with rounded corners. The edges
that leave one card with one meaning are one net, drawn as one line that branches, with a dot at
each branch. In the space after its card a net has a trunk, an upright line on a track; an edge
to the next layer leaves the trunk level. An edge to a later layer runs on a lane, a level line
under the cards of the band it enters and outside the frame of the group, which the edges of the
net into that band share; it leaves the lane upright before the layer of its target. So no line
passes through a card or runs along the cards inside a group, lines on neighbouring tracks and
lanes keep one distance, and every edge arrives at a card at a point of its own, for which a card
grows where many arrive. A line is written as a few pieces with narrow boxes, so that a browser
draws only those in its window. The words on a line name its folded steps where they cover no
card, and count them where the names would.

No font is read or embedded: text widths are estimated from character classes, which is why cards
keep a margin, and the drawing typesets no formula. The colours are given in the order the cards
stand in, which already makes neighbours differ. One router puts every line on a track or a lane, so
nothing is left to push apart. The checks of the lines on the finished geometry are tests, in
tests/test_depmap.py.
"""
from bisect import bisect_right, insort
import html
import json
import math
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent

# ----------------------------------------------------------------------------- the visual grammar

# Two faces, each a list of fonts that the common systems carry, since the drawing embeds none. The words are set
# as a mathematical text sets them: a Palatino in regular weight for the names of results, its italic for the
# small words beside them, and a fixed-width face for Lean names. Nothing is bold.
SERIF = ("'Palatino Linotype', Palatino, 'Book Antiqua', 'URW Palladio L', P052, 'TeX Gyre Pagella', Cambria, 'Noto Serif', "
         "Georgia, serif")
MONO = "'Cascadia Mono', 'SF Mono', Consolas, Menlo, 'DejaVu Sans Mono', monospace"
INK, SUBTLE, FAINT = '#16283A', '#56697B', '#8497A8'
LINES = {'direct': ('', 1.7), 'contracted': ('10 6', 1.7), 'mention': ('1.7 6', 1.7), 'alternative': ('', 3.6),
         'refutation': ('14 6', 3.6)}
LEGEND = {'direct': 'named in the proof, or in the body of a definition',
          'contracted': 'through folded steps (named or counted on the line)',
          'mention': 'mentioned in the statement', 'alternative': 'a proof drawn as its own card, to its statement',
          'refutation': 'refutes the root: its statement is the negation of the root'}
# The page shows the drawing without the words on its lines, so its legend says where the steps are named instead.
PAGE_LEGEND = {'contracted': 'through folded steps (the panel names them for a selected unit)'}
LIGHT_WORDS = 'a lighter line leaves a definition'
COLOUR_WORDS = 'lines that leave one card have one colour'
BRANCH_WORDS = 'a dot: lines that run as one separate here; lines that cross without a dot are not connected'
ARROWS = {'alternative': (11, 4), 'refutation': (11, 4)}
ARROW = (8, 2.9)
CASING = 4.6
DOT = 3.1  # the radius of the dot where a net branches
CORNER = 7
PALETTE = ['#256D9D', '#B56527', '#277E65', '#965C9D', '#B64258', '#5A778D', '#78842E', '#9B5A35', '#4D62A9',
           '#268487', '#9B4277', '#5F7844', '#6F65A5', '#AF7339', '#376E63', '#8D5969', '#1F6F8B', '#A0522D',
           '#2E8B57', '#7B3F9E', '#C0392B', '#4A6FA5', '#8A7A1E', '#B5651D', '#3B6E8F', '#6B8E23', '#9C4F96',
           '#2A7F62']
ALTERNATIVE_COLOUR = '#7350A3'
REFUTATION_COLOUR = '#A83232'
# The two heavy lines have a colour of their own. Every other line has the colour of the card it leaves.
FIXED_COLOURS = {'alternative': ALTERNATIVE_COLOUR, 'refutation': REFUTATION_COLOUR}
SAMPLE_COLOUR = '#4B6072'  # in the legend, a line that stands for the lines of every card
# A line that leaves a definition is drawn lighter than a line that leaves a statement: where the definitions are
# used by most statements, as in a finished proof, their lines are most of the lines, and at full strength they
# hide how the statements rest on each other. LIGHT is the share of its colour that such a line keeps; the rest is
# white, which is what an opacity of that value shows on the white casing a line lies on. The value was chosen
# on a map of 173 cards whose definitions send 656 of its 916 lines: at 0.45 and below a dotted line that runs
# alone is hard to see at reading size, and from 0.65 the lanes between the groups read as dense as at full strength.
LIGHT = 0.55
GROUP_FILL, GROUP_STROKE, GROUP_TITLE = '#F7F9FB', '#D5DEE6', '#3F566A'
# A card: its fill, its outline and the width of the outline. The outline is a hairline, and a soft shade under
# the card lifts it from the lines that pass behind it.
CARD = {'statement': ('#FFFFFF', '#AEBDC9', 1.1), 'definition': ('#F4F7F9', '#B4C1CC', 1.1),
        'proof': ('#F6F1FB', '#AD9FC6', 1.1), 'root': ('#FFF8E1', '#C9A63C', 1.8)}
CARD_RADIUS, SHADE, SHADE_OPACITY, SHADE_DROP = 9, '#16283A', 0.06, 3
BAR_LEFT, BAR_WIDTH, BAR_INSET = 8, 4, 11  # the mark of a standing: a rounded bar inside the left edge of its card
STANDINGS = {'no_proof': ('no proof', '#B8475A'), 'not_confirmed': ('proof not confirmed', '#C57A35'),
             'held': ('correct, held back', '#BFA02A'), 'accepted': ('accepted', '#3C9068')}
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
    'proof not confirmed': 'A proof was offered, and review found a gap in it, could not finish judging it, or has not '
                           'judged it.',
    'correct, held back': 'Review found the proof correct and did not accept it: it can still be made simpler, or it closes '
                          'a part only by large computation done without an understanding of why that part holds.',
    'accepted': 'Review found the proof correct and accepted it. A statement that was in the library before any review, '
                'and whose Lean proof is complete, stands as accepted as well: no review has judged that proof, and Lean '
                'has checked it.',
    'settled': 'One of its proofs is accepted, and every statement that proof names is settled in the same way.',
    'not settled': 'No proof of it is accepted and rests on settled statements only.',
    'formal': 'One of its proofs is complete in Lean: it rests on nothing but the allowed axioms, with no gap below it.',
    'refuted': 'A statement that Lean confirmed as the negation of this one is settled.',
    'refutes the root': 'Lean confirmed that this statement is the negation of the root.',
    'from the literature': 'The result is taken from a published source, which its record names.'}

CARD_WIDTH = 300
TEXT_LEFT, TEXT_RIGHT, TEXT_TOP, TEXT_BOTTOM = 22, 12, 12, 12
LABEL_SIZE, NAME_SIZE, STATUS_SIZE = 17, 11, 13
LABEL_LINE, NAME_LINE, STATUS_LINE = 22, 15, 18
VIA_SIZE, VIA_HEIGHT, VIA_SHOWN = 12.5, 19, 3
GROUP_TITLE_SIZE = 72  # the name of a group is the heading of a region of the map, several times the name of a card
MARGIN = 40

# the layered layout
LAYER_GAP, CARD_GAP = 130, 26
TRACK_GAP, TRACK_MARGIN, TRACK_CLEAR = 9, 34, 36  # between two tracks, from a card to the first track, between two lines on one track
LANE_GAP, LANE_MARGIN = 9, 20  # between two lanes, from the frame of a group to its first lane
GROUP_PAD_X, GROUP_PAD_TOP, GROUP_PAD_BOTTOM, GROUP_GAP = 28, 108, 24, 30
PORT_GAP, PORT_MARGIN, PORT_MIN = 14, 12, 7  # between two ends on a card, from its corner to the first; a card grows to keep the last
SWEEPS, RELAXATIONS = 24, 24


# ----------------------------------------------------------------------------- text

def text_width(text, size, mono=False):
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
    return total * size


def wrap(text, size, width, mono=False, after=' '):
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
        if line and text_width((line + piece).rstrip(), size, mono) > width:
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
    label = wrap(unit['label'], LABEL_SIZE, inner)
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

    # A net is the set of edges that leave one card with one meaning. It is drawn as one line that branches: the
    # edges leave the card at one point and part where their targets are. An edge that closes a cycle is a net alone.
    nets = [('turned', number) if number in turned else (a, data['edges'][number]['kind'])
            for number, (a, b) in enumerate(oriented)]
    far = [layer[b] - layer[a] > 1 for a, b in oriented]

    # A card is as tall as its words and as the lines that arrive at it need: each arrives at a point of its own.
    arriving = {name: 0 for name in ids}
    for _, b in oriented:
        arriving[b] += 1
    height = {name: max(cards[name]['height'], 2 * PORT_MARGIN + (arriving[name] - 1) * PORT_MIN) for name in ids}

    # The order inside a layer follows the edges to the next layer and from the one before, which are drawn in the
    # space between the two. Among the cards these edges do not order, the ones more far lines arrive at stand lower,
    # nearer the lanes their lines come from.
    up, down, distant = {name: [] for name in ids}, {name: [] for name in ids}, {name: 0 for name in ids}
    for number, (a, b) in enumerate(oriented):
        if far[number]:
            distant[b] += 1
        elif b not in down[a]:
            down[a].append(b)
            up[b].append(a)
    rows = [[] for _ in range(count)]
    for name in ids:
        rows[layer[name]].append(name)
    for row in rows:
        row.sort(key=lambda name: (band[name], distant[name]))

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

    # An edge to a later layer than the next runs on a lane: a level line under the cards of the band it enters,
    # outside the frame of the group, from the space after its source to the space before its target. The edges of
    # a net into one band share one lane, so a definition that fifty statements use sends one line along each band
    # and drops a branch before each layer where it is used. Two lanes share a row where they do not meet; the
    # lanes with the most branches lie nearest the cards, so that their branches cross the fewest lanes.
    lanes = {}  # (net, band) -> the first space, the last space, the spaces a branch leaves in
    for number, (a, b) in enumerate(oriented):
        if far[number]:
            lane = lanes.setdefault((nets[number], band[b]), [layer[a], layer[a], set()])
            lane[1] = max(lane[1], layer[b] - 1)
            lane[2].add(layer[b] - 1)
    row_of, deep = {}, [0] * len(bands)
    for index in range(len(bands)):
        taken = []
        mine = [key for key in lanes if key[1] == index]
        for key in sorted(mine, key=lambda key: (-len(lanes[key][2]), lanes[key][0], lanes[key][1], str(key))):
            first, last, _ = lanes[key]
            at = next((r for r, spans in enumerate(taken) if all(last < f or l < first for f, l in spans)), len(taken))
            if at == len(taken):
                taken.append([])
            taken[at].append((first, last))
            row_of[key] = at
        deep[index] = len(taken)

    # Coordinates. A band is as tall as its tallest layer; inside it every layer is first centred, then relaxed.
    parts = [{} for _ in range(count)]
    for index, row in enumerate(rows):
        for key in row:
            parts[index].setdefault(band[key], []).append(key)
    need = [0.0] * len(bands)
    for index in range(count):
        for number, keys in parts[index].items():
            need[number] = max(need[number], sum(height[key] for key in keys) + CARD_GAP * (len(keys) - 1))
    head, above, below, foot, cursor = [], [], [], [], 0.0
    for number in range(len(bands)):
        head.append(cursor)
        above.append(cursor + GROUP_PAD_TOP)
        below.append(above[-1] + need[number])
        foot.append(below[-1] + GROUP_PAD_BOTTOM)
        cursor = foot[-1] + (2 * LANE_MARGIN + (deep[number] - 1) * LANE_GAP if deep[number] else 0) + GROUP_GAP
    level = {key: foot[key[1]] + LANE_MARGIN + row_of[key] * LANE_GAP for key in lanes}
    top = {}
    for index in range(count):
        for number, keys in parts[index].items():
            y = above[number] + (need[number] - sum(height[key] for key in keys) - CARD_GAP * (len(keys) - 1)) / 2
            for key in keys:
                top[key] = y
                y += height[key] + CARD_GAP

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
                    floor = wanted[position] + height[key] + CARD_GAP
                ceiling = below[number]
                for position in range(len(keys) - 1, -1, -1):
                    key = keys[position]
                    wanted[position] = min(wanted[position], ceiling - height[key])
                    ceiling = wanted[position] - CARD_GAP
                    top[key] = wanted[position]

    # Where a line meets a card: the ends on one side are spread in the order of where they lead. A net
    # leaves its card at one point, so that its edges are one line until they part; every edge enters at its own.
    sides = {}
    for number, (a, b) in enumerate(oriented):
        lane = level.get((nets[number], band[b])) if far[number] else None
        sides.setdefault((a, 'right'), {}).setdefault(nets[number], []).append(middle(b) if lane is None else lane)
        sides.setdefault((b, 'left'), {})[number] = [middle(a) if lane is None else lane]
    port = {}
    for (name, side), ends in sides.items():
        order = sorted(ends, key=lambda end: (sum(ends[end]) / len(ends[end]), str(end)))
        step = min(PORT_GAP, (height[name] - 2 * PORT_MARGIN) / max(len(order) - 1, 1))
        for position, end in enumerate(order):
            port[(end, side)] = middle(name) + (position - (len(order) - 1) / 2) * step

    # In the space between two layers a line turns at right angles. A net leaves its card level and meets its
    # trunk, an upright line from which a branch leaves level to each target in the next layer and to each lane.
    # Before the layer of a far target a branch leaves the lane upright and reaches the cards it serves there. Every
    # upright line stands on a track; two share a track only where they are well apart, and a space is as wide as
    # its tracks need. The trunks stand nearer the cards the lines leave, the branches nearer the cards they reach.
    trunks, drops = [{} for _ in range(count)], [{} for _ in range(count)]

    def widen(found, key, *values):
        span = found.setdefault(key, [values[0], values[0]])
        span[0], span[1] = min(span[0], *values), max(span[1], *values)

    for number, (a, b) in enumerate(oriented):
        y1, y2 = port[(nets[number], 'right')], port[(number, 'left')]
        if far[number]:
            y = level[(nets[number], band[b])]
            widen(trunks[layer[a]], nets[number], y1, y)
            widen(drops[layer[b] - 1], (nets[number], band[b]), y, y2)
        else:
            widen(trunks[layer[a]], nets[number], y1, y2)
    # A net leaves its card on a level stub as far as its trunk, and a branch arrives at a card of the next layer on
    # a level stub from its trunk. Where two such stubs of different nets lie at nearly one height, the trunk of
    # the leaving one is kept to the left of the other, so that the two stubs do not run along each other.
    track, edge = {}, [GROUP_PAD_X]
    for index in range(count):
        stubs = {}  # net -> the heights at which its branches arrive in the next layer
        for number, (a, b) in enumerate(oriented):
            if layer[a] == index and not far[number]:
                stubs.setdefault(nets[number], []).append(port[(number, 'left')])
        before = [(first, second) for first in trunks[index] for second, heights in stubs.items() if first != second
                  and any(abs(port[(first, 'right')] - y) < PORT_MIN for y in heights)]
        used = 0
        for kind, found in (('trunk', trunks[index]), ('drop', drops[index])):
            taken, at = [], {}

            def place(key, least=0):
                low, high = found[key]
                free = (t for t in range(least, len(taken))
                        if all(high + TRACK_CLEAR <= l or h + TRACK_CLEAR <= low for l, h in taken[t].values()))
                at[key] = next(free, len(taken))
                if at[key] == len(taken):
                    taken.append({})
                taken[at[key]][key] = (low, high)

            for key in sorted(found, key=lambda key: (found[key][0], found[key][1], str(key))):
                if found[key][1] - found[key][0] >= 0.01:  # a net whose only edge runs level needs no track
                    place(key)
            for _ in range(len(before) if kind == 'trunk' else 0):
                wrong = next(((first, second) for first, second in before
                              if first in at and second in at and at[second] < at[first]), None)
                if not wrong:
                    break
                del taken[at[wrong[1]]][wrong[1]]
                place(wrong[1], at[wrong[0]])
            for key, where in at.items():
                track[(index, kind, key)] = used + where
            used += len(taken)
        edge.append(edge[-1] + CARD_WIDTH + max(LAYER_GAP, 2 * TRACK_MARGIN + max(used - 1, 0) * TRACK_GAP))
    left = {name: edge[layer[name]] for name in ids}

    def upright(index, kind, key):
        return edge[index] + CARD_WIDTH + TRACK_MARGIN + track[(index, kind, key)] * TRACK_GAP

    # A line is written in pieces, each with a narrow box around it: the part in the space after its source, the
    # lane, and the part in the space before its target. A piece ends in the middle of a level run, so that the
    # corners of the line are whole. `places` are where the words on the line may stand.
    routes, cuts, places = [], [], []
    for number, (a, b) in enumerate(oriented):
        net, first, last = nets[number], layer[a], layer[b] - 1
        x1, y1, x2, y2 = left[a] + CARD_WIDTH, port[(nets[number], 'right')], left[b], port[(number, 'left')]
        if far[number]:
            y, xt, xd = level[(net, band[b])], upright(first, 'trunk', net), upright(last, 'drop', (net, band[b]))
            points = [(x1, y1), (xt, y1), (xt, y), (xd, y), (xd, y2), (x2, y2)]
            enters, leaves = edge[first + 1], edge[last] + CARD_WIDTH  # where the lane passes the first and the last layer
            pieces = [[(x1, y1), (xt, y1), (xt, y), (enters, y)], [(enters, y), (leaves, y)],
                      [(leaves, y), (xd, y), (xd, y2), (x2, y2)]]
            where = [('end', x2, y2), ('middle', xd, (y + y2) / 2), ('middle', edge[last] + CARD_WIDTH / 2, y)]
        elif abs(y1 - y2) < 0.01:
            points = [(x1, y1), (x2, y2)]
            pieces, where = [points], [('middle', (x1 + x2) / 2, y1)]
        else:
            x = upright(first, 'trunk', net)
            points = [(x1, y1), (x, y1), (x, y2), (x2, y2)]
            pieces, where = [points], [('end', x2, y2), ('middle', x, (y1 + y2) / 2), ('start', x1, y1)]
        if number in turned:
            points, pieces = points[::-1], [piece[::-1] for piece in pieces[::-1]]
        routes.append(points)
        cuts.append(pieces)
        places.append(where)

    boxes = {name: (left[name], top[name], CARD_WIDTH, height[name]) for name in ids}
    frames = {}
    for number, key in enumerate(bands):
        x0 = min(left[name] for name in members[key]) - GROUP_PAD_X
        x1 = max(left[name] for name in members[key]) + CARD_WIDTH + GROUP_PAD_X
        x1 = max(x1, x0 + text_width(key, GROUP_TITLE_SIZE) + 48)
        frames[key] = (x0, head[number], x1 - x0, foot[number] - head[number])

    # The words on a line stand at its end before the target, else on its last upright part, else on its lane, at the
    # first of these where they cover no card and no other words. The names of three steps are often wider than
    # the room there, and words that find no free place would lie across the cards beside them. So words that
    # find no place name one step fewer and try again, down to the number of steps alone; the data keeps every
    # name, and the page lists them for the selected unit.
    taken = [(x - 4, y - 4, w + 8, h + 8) for x, y, w, h in boxes.values()]
    labels = []
    for number, edge_data in enumerate(data['edges']):
        if not edge_data['via']:
            labels.append((None, None))
            continue
        found, words = None, None
        for shown in range(VIA_SHOWN, -1, -1):
            shorter = via_text(data, edge_data, shown)
            if shorter == words:
                continue
            words = shorter
            wide, tall = via_box(words)
            spots = [(x - {'end': wide + 14, 'middle': wide / 2, 'start': -14}[how], y - tall / 2, wide, tall)
                     for how, x, y in places[number]]
            found = next((spot for spot in spots if not any(overlap(spot, other) for other in taken)), None)
            if found:
                break
        found = found or spots[0]  # nothing is free: the shortest words, where the line is most its own
        taken.append(found)
        labels.append((found, words))

    right = max([x + w for x, _, w, _ in frames.values()] + [edge[-1] - LAYER_GAP + GROUP_PAD_X])
    shared = {net: index for index, net in enumerate(dict.fromkeys(nets))}
    return {'width': right, 'height': cursor - GROUP_GAP, 'cards': boxes, 'groups': frames,
            'edges': [{'points': routes[n], 'pieces': cuts[n], 'label': labels[n][0], 'words': labels[n][1],
                       'net': shared[nets[n]]} for n in range(len(pairs))]}


def overlap(first, second):
    return (first[0] < second[0] + second[2] and second[0] < first[0] + first[2]
            and first[1] < second[1] + second[3] and second[1] < first[1] + first[3])


def stretches(routes):
    """The straight parts of the lines of one net, each once: parts that lie on one another or touch are joined.

    A part that is neither level nor upright is kept as it is."""
    level, upright, found = {}, {}, []
    for points in routes:
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            if abs(y1 - y2) < 0.01 and abs(x1 - x2) >= 0.01:
                level.setdefault(round(y1, 2), []).append((min(x1, x2), max(x1, x2)))
            elif abs(x1 - x2) < 0.01 and abs(y1 - y2) >= 0.01:
                upright.setdefault(round(x1, 2), []).append((min(y1, y2), max(y1, y2)))
            elif abs(x1 - x2) >= 0.01:
                found.append(((x1, y1), (x2, y2)))
    for spans, flat in ((level, True), (upright, False)):
        for at, parts in spans.items():
            parts.sort()
            low, high = parts[0]
            for first, last in parts[1:] + [(math.inf, math.inf)]:
                if first <= high + 0.01:
                    high = max(high, last)
                else:
                    found.append(((low, at), (high, at)) if flat else ((at, low), (at, high)))
                    low, high = first, last
    return found


def runs(lines):
    """The lines of one net cut into runs, so that each stretch of the net is drawn once.

    `lines` holds, for each edge of the net, the pieces of its line; the edges leave one point and run together
    until they part. A run is a stretch along which the same edges run; it ends where one of them leaves the
    others, and where a piece of any of them ends. Returned for each run: its points, how far along the line it
    begins, and which edges run along it, as their positions in `lines`. Where a line turns at the start of a
    run, the run begins a little before the turn, so that the corner is drawn round."""
    def key(point):
        return round(point[0], 2), round(point[1], 2)

    def heading(a, b):
        return (b[0] > a[0] + 0.01) - (b[0] < a[0] - 0.01), (b[1] > a[1] + 0.01) - (b[1] < a[1] - 0.01)

    marks, cuts = {}, set()  # on each level and each upright line, where a line of the net has a corner; where a piece ends
    for pieces in lines:
        for piece in pieces:
            cuts.update((key(piece[0]), key(piece[-1])))
            for x, y in piece:
                marks.setdefault((0, round(x, 2)), set()).add(y)
                marks.setdefault((1, round(y, 2)), set()).add(x)
    walks, users = [], {}
    for index, pieces in enumerate(lines):
        walk, distance = [], 0.0  # the line in its shortest parts: from, to, how far along the line the part begins
        for piece in pieces:
            for a, b in zip(piece, piece[1:]):
                stops = [a, b]
                for axis in (0, 1):  # an upright part is cut at the heights marked on its line, a level part likewise
                    if abs(a[axis] - b[axis]) < 0.01 and abs(a[1 - axis] - b[1 - axis]) >= 0.01:
                        low, high = sorted((a[1 - axis], b[1 - axis]))
                        between = sorted((at for at in marks[(axis, round(a[axis], 2))] if low + 0.01 < at < high - 0.01),
                                         reverse=a[1 - axis] > b[1 - axis])
                        stops = [a] + [(a[0], at) if axis == 0 else (at, a[1]) for at in between] + [b]
                for first, second in zip(stops, stops[1:]):
                    long = math.hypot(second[0] - first[0], second[1] - first[1])
                    if long >= 0.01:
                        walk.append((first, second, distance))
                        users.setdefault(frozenset((key(first), key(second))), set()).add(index)
                        distance += long
        walks.append(walk)

    def along(part):
        return users[frozenset((key(part[0]), key(part[1])))]

    found, seen = [], set()
    for walk in walks:
        start = 0
        while start < len(walk):
            end = start
            while end + 1 < len(walk) and key(walk[end][1]) not in cuts and along(walk[end + 1]) == along(walk[start]):
                end += 1
            name = (key(walk[start][0]), key(walk[end][1]))
            if name not in seen:
                seen.add(name)
                points = [walk[start][0]]
                for first, second, _ in walk[start:end + 1]:
                    if len(points) > 1 and heading(points[-2], points[-1]) == heading(first, second):
                        points[-1] = second  # a point on a straight part is left out
                    else:
                        points.append(second)
                distance = walk[start][2]
                if start and heading(*walk[start - 1][:2]) != heading(*walk[start][:2]):
                    back = start - 1  # the straight part before the turn
                    while back and heading(*walk[back - 1][:2]) == heading(*walk[start - 1][:2]):
                        back -= 1
                    (x, y), (cx, cy) = walk[back][0], walk[start][0]
                    straight = math.hypot(cx - x, cy - y)
                    lead = min(2 * CORNER, straight)
                    points.insert(0, (cx + (x - cx) / straight * lead, cy + (y - cy) / straight * lead))
                    distance -= lead
                found.append((points, distance, sorted(along(walk[start]))))
            start = end + 1
    return found


def junctions(edges):
    """For each edge, the points where it turns off a line that another edge of its net follows further.

    They are read from the finished routes: a corner of one edge that lies on the route of another edge of the net,
    which leaves the point in another direction. Where two edges only run together, and where two lines cross,
    there is none. A point belongs to the first edge that turns there, so a dot is drawn once."""
    def heading(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        return (0, 0) if abs(dx) < 0.01 and abs(dy) < 0.01 else ((dx > 0) - (dx < 0), 0) if abs(dx) >= abs(dy) else (0, (dy > 0) - (dy < 0))

    def leaves(points, at):
        """The direction in which a route goes on from a point on it; None where the route does not pass the point."""
        for a, b in zip(points, points[1:]):
            if abs(a[0] - at[0]) < 0.01 and abs(a[1] - at[1]) < 0.01:
                return heading(a, b)
            if (min(a[0], b[0]) - 0.01 <= at[0] <= max(a[0], b[0]) + 0.01 and min(a[1], b[1]) - 0.01 <= at[1] <= max(a[1], b[1]) + 0.01
                    and abs((b[0] - a[0]) * (at[1] - a[1]) - (b[1] - a[1]) * (at[0] - a[0])) < 0.01
                    and not (abs(b[0] - at[0]) < 0.01 and abs(b[1] - at[1]) < 0.01)):
                return heading(a, b)
        return None

    nets = {}
    for index, edge in enumerate(edges):
        nets.setdefault(edge['net'], []).append(index)
    found = [[] for _ in edges]
    for indices in nets.values():
        seen = set()
        for index in indices if len(indices) > 1 else ():
            points = edges[index]['points']
            for corner, onward in zip(points[1:-1], points[2:]):
                key = (round(corner[0], 2), round(corner[1], 2))
                mine = heading(corner, onward)
                if key not in seen and any(leaves(edges[other]['points'], corner) not in (None, mine)
                                           for other in indices if other != index):
                    seen.add(key)
                    found[index].append(corner)
    return found


# ----------------------------------------------------------------------------- SVG

def esc(text):
    return html.escape(str(text), quote=True)


def lighter(colour, share=None):
    """A colour mixed with white: what a line of `colour` shows on white at the opacity `share` (LIGHT if not given).

    The colour is written out and the line stays opaque. So the parts of a net that are drawn over one another,
    the line before a branch and the line and its arrowhead, are as light as the rest, and the page dims a
    lighter line as it dims every other line, by the opacity of its stroke."""
    share = LIGHT if share is None else share
    return '#' + ''.join(f'{round(255 - (255 - int(colour[at:at + 2], 16)) * share):02X}' for at in (1, 3, 5))


def light_sources(data):
    """The definitions that lines leave. Their lines are drawn lighter than the lines that leave a statement."""
    definitions = {unit['id'] for unit in data['units'] if unit['role'] == 'definition'}
    return {edge['source'] for edge in data['edges']} & definitions


def colour_words(kinds):
    """The sentence of the legend on the colours, for a map with these kinds of line.

    A heavy line has the colour of its kind, which its entry in the legend shows, so where heavy lines occur the
    sentence speaks of the thin ones."""
    return ('thin ' if any(kind in FIXED_COLOURS for kind in kinds) else '') + COLOUR_WORDS


def fmt(value):
    return f'{value:.2f}'.rstrip('0').rstrip('.')


def cornered_path(points):
    """A polyline with rounded corners; the radius shrinks on a short stretch."""
    parts = [f'M {fmt(points[0][0])} {fmt(points[0][1])}']
    for a, b, c in zip(points, points[1:], points[2:]):
        u, v = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
        du, dv = math.hypot(*u), math.hypot(*v)
        if not du or not dv:
            continue
        r = min(CORNER, du / 2, dv / 2)
        parts.append(f'L {fmt(b[0] + u[0] / du * r)} {fmt(b[1] + u[1] / du * r)}')
        parts.append(f'Q {fmt(b[0])} {fmt(b[1])} {fmt(b[0] + v[0] / dv * r)} {fmt(b[1] + v[1] / dv * r)}')
    parts.append(f'L {fmt(points[-1][0])} {fmt(points[-1][1])}')
    return ' '.join(parts)


def text(x, y, content, size, colour=INK, anchor='start', family=None, italic=False):
    """A line of words. The face is that of the drawing, a serif in regular weight, unless `family` names another."""
    font = f' font-family="{esc(family)}"' if family else ''
    slant = ' font-style="italic"' if italic else ''
    return (f'<text x="{fmt(x)}" y="{fmt(y)}" font-size="{size}" fill="{colour}" text-anchor="{anchor}"{slant}{font}>'
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

    def line(colour, words, dash='', width=LINES['direct'][1]):
        at = place(62 + text_width(words, 14) + 30)
        parts.append(f'<path d="M {fmt(at)} {y - 5} h 46" fill="none" stroke="{colour}" stroke-width="{width}"{dashed(dash)}/>')
        parts.append(f'<path d="M {fmt(at + 54)} {y - 5} l -9 -4 v 8 Z" fill="{colour}"/>')
        parts.append(text(at + 62, y, words, 14, SUBTLE))

    for kind in kinds:
        line(FIXED_COLOURS.get(kind, SAMPLE_COLOUR), LEGEND[kind], *LINES[kind])
    if light_sources(data):
        line(lighter(SAMPLE_COLOUR), LIGHT_WORDS)
    for role in roles:
        (fill, border, _), words = CARD[role], CARD_WORDS[role]
        at = place(26 + text_width(words, 14) + 22)
        parts.append(f'<rect x="{fmt(at)}" y="{y - 12}" width="20" height="14" rx="3.5" fill="{fill}" stroke="{border}" '
                     f'stroke-width="1.2"/>')
        parts.append(text(at + 26, y, words, 14, SUBTLE))
    for standing in standings:
        words, colour = STANDINGS[standing]
        at = place(14 + text_width(words, 14) + 22)
        parts.append(f'<rect x="{fmt(at + 2)}" y="{y - 12}" width="{BAR_WIDTH}" height="14" rx="{BAR_WIDTH / 2}" fill="{colour}"/>')
        parts.append(text(at + 14, y, words, 14, SUBTLE))
    if kinds:
        words = colour_words(kinds)
        parts.append(text(place(text_width(words, 14) + 22), y, words, 14, SUBTLE))
        at = place(40 + text_width(BRANCH_WORDS, 14) + 22)
        parts.append(f'<path d="M {fmt(at)} {y - 5} h 30 M {fmt(at + 15)} {y - 5} v -9" fill="none" stroke="{SAMPLE_COLOUR}" stroke-width="1.7"/>'
                     f'<circle cx="{fmt(at + 15)}" cy="{y - 5}" r="{DOT}" fill="{SAMPLE_COLOUR}"/>')
        parts.append(text(at + 40, y, BRANCH_WORDS, 14, SUBTLE))
    return parts, y


def number(count, word):
    """A count with its noun: `1 step`, `3 steps`."""
    return f"{count} {word}{'' if count == 1 else 's'}"


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
    subtitle = (f"{data.get('root_label') or ''} · {state_words(data)} · {number(counts['units'], 'unit')} in "
                f"{number(counts['groups'], 'group')}, {number(counts['edges'], 'line')}, "
                f"{number(len(data.get('folded') or {}), 'step')} folded into the lines · {scope_words(data)}{library}")
    width = max(geometry['width'], text_width(subtitle, 15), text_width(data['title'], 30), 640) + 2 * MARGIN
    head, baseline = legend(width - MARGIN, 104, data, bare)
    header = baseline + 28
    height = geometry['height'] + header + MARGIN
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width)}" height="{fmt(height)}" '
             f'viewBox="0 0 {fmt(width)} {fmt(height)}" font-family="{esc(SERIF)}" style="font-variant-numeric: lining-nums">',
             f'<title>{esc(data["title"])}</title>',
             f'<rect width="{fmt(width)}" height="{fmt(height)}" fill="#FFFFFF"/>',
             text(MARGIN, 46, data['title'], 30), text(MARGIN, 74, subtitle, 15, SUBTLE, italic=True)]
    # The legend is one part of the drawing, so that the page, whose panel explains the same, can leave it out.
    parts += ['<g id="legend">', *head, '</g>']
    parts.append(f'<g id="drawing" transform="translate({MARGIN},{header})">')

    # The frame of a group lies under the lines, and its name is written over them, so that the name can be read
    # where lines cross the corner it stands in.
    names = []
    for group in data['groups']:
        x, y, w, h = geometry['groups'][group['id']]
        parts.append(f'<g class="group" data-group="{esc(group["id"])}"><rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" '
                     f'height="{fmt(h)}" rx="16" fill="{GROUP_FILL}" stroke="{GROUP_STROKE}" stroke-width="1.3"/></g>')
        at = (x + 24, y + 18 + 0.74 * GROUP_TITLE_SIZE, group['label'], GROUP_TITLE_SIZE)
        # A copy with a wide edge in the colour of the ground lies under the name, so that no line cuts through it.
        names.append(text(*at, GROUP_FILL, italic=True).replace('<text ', f'<text stroke="{GROUP_FILL}" stroke-width="14" '
                                                                          'stroke-linejoin="round" ', 1))
        names.append(text(*at, GROUP_TITLE, italic=True))

    # Every thin line that leaves one card has one colour, whatever its kind; the cards are taken in the order they
    # stand in. A line that leaves a definition has that colour lighter.
    sources = sorted({edge['source'] for edge in data['edges'] if edge['kind'] not in FIXED_COLOURS},
                     key=lambda name: (geometry['cards'][name][0], geometry['cards'][name][1], name))
    colour = {name: PALETTE[index % len(PALETTE)] for index, name in enumerate(sources)}
    light = light_sources(data)
    # A white casing under a line separates it from the lines it crosses. The edges of one net run together
    # before they part, so the casings of a net are all drawn before its lines; otherwise the casing of one
    # edge would cut the line of another where it leaves the common stretch, and a branch would read as a crossing.
    # The lighter lines are drawn first, so that at a crossing the stronger line is the one that is not cut.
    parts.append('<g id="routes">')
    behind = {'mention': 0, 'contracted': 1, 'direct': 2, 'alternative': 3, 'refutation': 4}
    nets = {}
    for index in sorted(range(len(data['edges'])),
                        key=lambda i: (data['edges'][i]['source'] not in light, behind[data['edges'][i]['kind']], i)):
        nets.setdefault(geometry['edges'][index]['net'], []).append(index)
    dots = junctions(geometry['edges'])
    for indices in nets.values():
        kind = data['edges'][indices[0]]['kind']  # the edges of a net are of one kind and leave one card
        dash, stroke = LINES[kind]
        source = data['edges'][indices[0]]['source']
        ink = FIXED_COLOURS.get(kind) or colour[source]
        if source in light:
            ink = lighter(ink)
        long, half = ARROWS.get(kind, ARROW)
        period = sum(float(part) for part in dash.split())
        style = (f'fill="none" stroke="{ink}" stroke-width="{stroke}"{dashed(dash)} stroke-linecap="round" '
                 f'stroke-linejoin="round"')
        lines, tips = [], []
        for index in indices:
            route = geometry['edges'][index]
            (px, py), (ex, ey) = route['points'][-2:]
            span = math.hypot(ex - px, ey - py) or 1.0
            dx, dy = (ex - px) / span, (ey - py) / span
            pieces = [list(piece) for piece in route['pieces']]
            pieces[-1][-1] = (ex - dx * (long - 1), ey - dy * (long - 1))  # the line ends inside its arrowhead
            lines.append(pieces)
            bx, by = ex - dx * long, ey - dy * long
            tips.append(f'M {fmt(ex)} {fmt(ey)} L {fmt(bx - dy * half)} {fmt(by + dx * half)} '
                        f'L {fmt(bx + dy * half)} {fmt(by - dx * half)} Z')
        # The edges of a net lie on one another until they part. Each stretch of the net is drawn once: a stretch
        # that several edges share stands in a group of its own, which names those edges, and the rest of an edge
        # in the group of the edge. Drawn once, a line that the page dims is as faint where fifty edges share it as
        # where one runs alone, and a browser strokes it once. The distance lets a dashed line keep its rhythm.
        own, common = [[] for _ in indices], {}
        for points, distance, users in runs(lines):
            wire = (f'<path class="wire" d="{cornered_path(points)}"'
                    + (f' stroke-dashoffset="{fmt(distance % period)}"' if period and distance % period >= 0.01 else '') + '/>')
            if len(users) == 1:
                own[users[0]].append(wire)
            else:
                common.setdefault(tuple(users), []).append(wire)
        # The casing is drawn once for each straight part of the net and before its lines; the rounded corner of a
        # line stays inside the casing of the two parts it joins.
        parts.append(f'<g class="casing" fill="none" stroke="#FFFFFF" stroke-width="{stroke + CASING}" stroke-linecap="round">'
                     + ''.join(f'<path d="M {fmt(x1)} {fmt(y1)} L {fmt(x2)} {fmt(y2)}"/>' for (x1, y1), (x2, y2)
                               in stretches([geometry['edges'][index]['points'] for index in indices])) + '</g>')
        for users, wires in common.items():
            parts.append(f'<g class="shared" data-edges="{" ".join(f"e{indices[user]}" for user in users)}" {style}>'
                         + ''.join(wires) + '</g>')
        for position, index in enumerate(indices):
            edge = data['edges'][index]
            # A dot marks each point where this edge turns off the line of its net; a crossing has none.
            marks = ''.join(f'M {fmt(x - DOT)} {fmt(y)} a {DOT} {DOT} 0 1 0 {2 * DOT} 0 a {DOT} {DOT} 0 1 0 {-2 * DOT} 0 Z '
                            for x, y in dots[index])
            parts.append(
                f'<g class="edge" id="e{index}" data-source="{esc(edge["source"])}" data-target="{esc(edge["target"])}" '
                f'data-kind="{edge["kind"]}" {style}>' + ''.join(own[position])
                + (f'<path class="dot" d="{marks.strip()}" fill="{ink}" stroke="none"/>' if marks else '')
                + f'<path class="arrow" d="{tips[position]}" fill="{ink}" stroke="none"/></g>')
    parts.append('</g>')

    parts.append('<g id="cards">')
    for name, unit in units.items():
        x, y, w, h = geometry['cards'][name]
        card = cards[name]
        fill, border, thick = CARD['root' if unit.get('root') else unit['role']]
        tooltip = f"{unit['label']} ({unit['id']})"  # names a card that is too small to read; the panel has its description
        parts.append(f'<g class="node" data-node="{esc(name)}" data-role="{unit["role"]}" '
                     f'data-status="{esc(" · ".join(status_of(unit, bare)))}"><title>{esc(tooltip)}</title>'
                     f'<rect class="shade" x="{fmt(x)}" y="{fmt(y + SHADE_DROP)}" width="{fmt(w)}" height="{fmt(h)}" '
                     f'rx="{CARD_RADIUS}" fill="{SHADE}" fill-opacity="{SHADE_OPACITY}"/>'
                     f'<rect class="card" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{CARD_RADIUS}" '
                     f'fill="{fill}" stroke="{border}" stroke-width="{thick}"/>')
        if unit.get('standing') and name not in bare:  # the proof of a statement in `bare` is a card of its own
            parts.append(f'<rect class="standing" x="{fmt(x + BAR_LEFT)}" y="{fmt(y + BAR_INSET)}" width="{BAR_WIDTH}" '
                         f'height="{fmt(h - 2 * BAR_INSET)}" rx="{BAR_WIDTH / 2}" fill="{STANDINGS[unit["standing"]][1]}"/>')
        line = y + TEXT_TOP
        for words in card['label']:
            line += LABEL_LINE
            parts.append(text(x + TEXT_LEFT, line - 5, words, LABEL_SIZE))
        line += 3
        for words in card['name']:
            line += NAME_LINE
            parts.append(text(x + TEXT_LEFT, line - 4, words, NAME_SIZE, FAINT, family=MONO))
        line += 5
        for words in card['status']:
            line += STATUS_LINE
            parts.append(text(x + TEXT_LEFT, line - 5, words, STATUS_SIZE, SUBTLE, italic=True))
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
                     f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{fmt(h / 2)}" fill="#FFFFFF" '
                     f'fill-opacity="0.95" stroke="#DFE6EC" stroke-width="1"/>'
                     + text(x + w / 2, y + h - 5.5, words, VIA_SIZE, SUBTLE, anchor='middle', italic=True) + '</g>')
    parts += ['</g>', '<g id="names">', *names, '</g>', '</g></svg>']
    return '\n'.join(parts) + '\n'


def guide_of(data, bare=()):
    """What the page's panel says about this map before a unit is chosen, as HTML: what it shows and how to read it.

    It is written here, beside the visual grammar, so that the page explains the lines, the cards and the
    standings in the colours and dashes they are drawn with, and only those that occur on this map. The
    glossary holds the words of the cards of this map and the kinds of its folded steps; the page also shows
    an entry with each word of a chosen card or step."""
    counts, units = data['counts'], {unit['id']: unit for unit in data['units']}
    name = esc(data.get('root_label') or data['root'])
    if data['root'] in units:
        name = f'<a href="#node={quote(data["root"], safe="")}">{name}</a>'
    steps = len(data.get('folded') or {})
    folded = (f' {steps} smaller step{"s have" if steps > 1 else " has"} no card and {"are" if steps > 1 else "is"} folded '
              f'into the lines that pass through {"them" if steps > 1 else "it"}.') if steps else ''
    parts = [f'<p class="about">The root of this research is {name}: {esc(state_words(data))}. The map shows '
             f'{esc(scope_words(data))}: {number(counts["units"], "unit")}, each a card, in '
             f'{number(counts["groups"], "group")}, joined by {number(counts["edges"], "line")}.{folded}</p>']
    kinds, roles, standings = occurring(data, bare)
    parts.append('<div class="legend"><h3>How to read the map</h3>'
                 '<p>An arrow runs from what is used to what uses it, so the map is read from the left, where the '
                 f'definitions and the first results stand, towards the root. {esc(colour_words(kinds).capitalize())}; '
                 'where they run as one line, a dot marks each point at which one of them leaves it. Lines that cross '
                 'without a dot are not connected.</p><ul>')

    def line(colour, words, dash='', width=LINES['direct'][1]):
        parts.append(f'<li><svg class="sample" width="56" height="12" viewBox="0 0 56 12" aria-hidden="true">'
                     f'<path d="M 1 6 h 44" fill="none" stroke="{colour}" stroke-width="{width}"{dashed(dash)}/>'
                     f'<path d="M 55 6 l -10 -4.5 v 9 Z" fill="{colour}"/></svg>{esc(words)}</li>')

    for kind in kinds:
        line(FIXED_COLOURS.get(kind, SAMPLE_COLOUR), PAGE_LEGEND.get(kind, LEGEND[kind]), *LINES[kind])
    if light_sources(data):
        line(lighter(SAMPLE_COLOUR), LIGHT_WORDS)
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
    # The panel of a folded step names the kind of the step, a word that no card of the map may say.
    said |= {KINDS.get(step['kind'], step['kind']) for step in (data.get('folded') or {}).values()}
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
    # In a script element </script ends the data, and <!-- followed by <script keeps the element open past its
    # own end tag. With every < written as an escape, no text of a record begins either.
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    return head.replace('__TITLE__', esc(data['title'])) + guide_of(data, bare) + middle + svg + between + payload + tail


def render(data):
    """(SVG, page): the drawing of a map and the page that shows it."""
    bare = proved_apart(data)
    cards = {unit['id']: card_of(unit, bare) for unit in data['units']}
    geometry = layered(data, cards)
    svg = svg_of(data, cards, geometry, bare)
    return svg, page_of(svg, data, bare)
