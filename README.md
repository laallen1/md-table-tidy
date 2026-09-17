# mdtabletidy

Markdown tables get ugly fast once more than one person edits a file, or
once you edit one by hand after a script generated it. Column widths drift,
some rows keep the leading/trailing `|` and others don't, alignment colons
get typo'd or dropped. It still renders fine, it just looks like garbage in
a plain-text diff or editor.

`mdtabletidy` reads a markdown file, finds every table in it, and rewrites
each one with padded columns, a consistent separator row, and alignment
preserved. Everything else in the file (code fences, prose, other tables)
is left untouched.

## Example

Input:

```markdown
Name | Role |Years
--- | :---: | ---:
Ada | engineer | 12
Grace|admiral|40
Alan Turing | mathematician | 1
```

Running `mdtabletidy` on it produces:

```markdown
| Name        |     Role      | Years |
| ----------- | :-----------: | ----: |
| Ada         |   engineer    |    12 |
| Grace       |    admiral    |    40 |
| Alan Turing | mathematician |     1 |
```

Ragged rows (too few or too many cells) are padded or truncated to match
the header, so a table doesn't fall apart when someone forgets a cell.

## Usage

```
python -m mdtabletidy notes.md            # print the formatted file to stdout
python -m mdtabletidy notes.md --write    # rewrite the file in place
cat notes.md | python -m mdtabletidy      # read from stdin, print to stdout
```

Once installed (`pip install -e .` from this directory), the same thing
works as `mdtabletidy notes.md`.

## How it works

The whole thing is one module, `src/mdtabletidy/__init__.py`. It scans a
file line by line looking for a header row immediately followed by a valid
separator row (`---`, `:---`, `---:`, `:---:`), collects the table rows
that follow, and re-renders that block with widths computed from the
longest cell in each column. Fenced code blocks (` ``` ` / `~~~`) are
tracked so table-looking lines inside them are never touched. Within a
cell, a `|` inside inline code (`` `a|b` ``) is left alone instead of being
read as a cell separator; use `\|` for a literal pipe outside of code.

## Known limitations

- Column widths use `unicodedata.east_asian_width()` to count CJK
  wide/fullwidth characters as two columns and combining marks as zero, so
  padding lines up in a monospace font. Most emoji report as "narrow" or
  "ambiguous" in Unicode's data and are counted as one column, so a table
  with emoji-heavy cells can still look uneven.

## License

MIT, see `LICENSE`.
