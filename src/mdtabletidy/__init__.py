"""Normalize markdown tables: consistent column widths, alignment markers, padding."""

import argparse
import re
import sys
import unicodedata

SEP_CELL_RE = re.compile(r'^:?-+:?$')
MIN_COL_WIDTH = 3


def display_width(text):
    """Terminal/monospace column count, not code point count.

    East Asian wide/fullwidth characters take two columns; combining marks
    (accents stacked on a base character) take zero, since they render on
    top of the previous column instead of advancing the cursor.
    """
    width = 0
    for ch in text:
        if unicodedata.combining(ch):
            continue
        width += 2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1
    return width


def find_pipe_positions(line):
    """Indices of '|' characters that act as cell separators.

    Skips pipes that are backslash-escaped or that fall inside an inline
    code span (a run of backticks matched by an equal-length closing run),
    per CommonMark's inline code rules.
    """
    positions = []
    i, n = 0, len(line)
    in_code = False
    code_delim_len = 0
    while i < n:
        ch = line[i]
        if ch == '`':
            j = i
            while j < n and line[j] == '`':
                j += 1
            run_len = j - i
            if not in_code:
                in_code = True
                code_delim_len = run_len
            elif run_len == code_delim_len:
                in_code = False
            i = j
            continue
        if ch == '\\' and not in_code and i + 1 < n and line[i + 1] == '|':
            i += 2
            continue
        if ch == '|' and not in_code:
            positions.append(i)
        i += 1
    return positions


def split_row(line):
    line = line.strip()
    positions = find_pipe_positions(line)
    bounds = [-1] + positions + [len(line)]
    cells = [line[bounds[k] + 1:bounds[k + 1]] for k in range(len(bounds) - 1)]
    if len(cells) > 1 and cells[0] == '' and line.startswith('|'):
        cells = cells[1:]
    if len(cells) > 1 and cells[-1] == '' and line.endswith('|'):
        cells = cells[:-1]
    return [cell.strip().replace('\\|', '|') for cell in cells]


def is_separator_row(line):
    line = line.strip()
    if not line or '-' not in line:
        return False
    cells = split_row(line)
    return bool(cells) and all(SEP_CELL_RE.match(c.strip()) for c in cells)


def looks_like_table_row(line):
    return bool(line.strip()) and bool(find_pipe_positions(line))


def parse_alignment(cell):
    cell = cell.strip()
    left = cell.startswith(':')
    right = cell.endswith(':')
    if left and right:
        return 'center'
    if right:
        return 'right'
    if left:
        return 'left'
    return None


def render_cell(text, width, align):
    pad = max(0, width - display_width(text))
    if align == 'right':
        return ' ' * pad + text
    if align == 'center':
        left = pad // 2
        return ' ' * left + text + ' ' * (pad - left)
    return text + ' ' * pad


def render_separator_cell(width, align):
    # every variant needs room for at least one dash plus its colons
    width = max(width, MIN_COL_WIDTH)
    if align == 'center':
        return ':' + '-' * (width - 2) + ':'
    if align == 'right':
        return '-' * (width - 1) + ':'
    if align == 'left':
        return ':' + '-' * (width - 1)
    return '-' * width


def format_table(block):
    header = split_row(block[0])
    sep = split_row(block[1])
    body = [split_row(line) for line in block[2:]]

    if body:
        ncols = max(len(header), len(sep), *(len(r) for r in body))
    else:
        ncols = max(len(header), len(sep))

    def pad_row(row):
        row = row[:ncols]
        return row + [''] * (ncols - len(row))

    header = pad_row(header)
    body = [pad_row(r) for r in body]
    aligns = [parse_alignment(c) for c in pad_row(sep)]

    widths = []
    for i in range(ncols):
        col_cells = [header[i]] + [r[i] for r in body]
        widths.append(max(MIN_COL_WIDTH, max(display_width(c) for c in col_cells)))

    lines = [
        '| ' + ' | '.join(render_cell(header[i], widths[i], aligns[i]) for i in range(ncols)) + ' |',
        '| ' + ' | '.join(render_separator_cell(widths[i], aligns[i]) for i in range(ncols)) + ' |',
    ]
    for row in body:
        lines.append('| ' + ' | '.join(render_cell(row[i], widths[i], aligns[i]) for i in range(ncols)) + ' |')
    return lines


def format_document(text):
    lines = text.splitlines()
    out = []
    in_code_fence = False
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_fence = not in_code_fence
            out.append(line)
            i += 1
            continue
        if (not in_code_fence and i + 1 < n
                and looks_like_table_row(line) and is_separator_row(lines[i + 1])):
            block = [line, lines[i + 1]]
            j = i + 2
            while j < n and looks_like_table_row(lines[j]):
                block.append(lines[j])
                j += 1
            out.extend(format_table(block))
            i = j
            continue
        out.append(line)
        i += 1

    result = '\n'.join(out)
    if text.endswith('\n'):
        result += '\n'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(prog='mdtabletidy', description='Normalize markdown tables in a file.')
    parser.add_argument('path', nargs='?', help='markdown file to format; reads stdin if omitted')
    parser.add_argument('-w', '--write', action='store_true',
                         help='rewrite the file in place instead of printing to stdout')
    args = parser.parse_args(argv)

    if args.path:
        with open(args.path, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        if args.write:
            parser.error('--write requires a file path, not stdin')
        text = sys.stdin.read()

    formatted = format_document(text)

    if args.write:
        with open(args.path, 'w', encoding='utf-8') as f:
            f.write(formatted)
    else:
        sys.stdout.write(formatted)


if __name__ == '__main__':
    main()
