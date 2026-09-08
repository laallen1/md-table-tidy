from mdtabletidy import format_document


def test_basic_alignment_and_padding():
    src = (
        "Name | Role |Years\n"
        "--- | :---: | ---:\n"
        "Ada | engineer | 12\n"
        "Grace|admiral|40\n"
        "Alan Turing | mathematician | 1\n"
    )
    expected = (
        "| Name        |     Role      | Years |\n"
        "| ----------- | :-----------: | ----: |\n"
        "| Ada         |   engineer    |    12 |\n"
        "| Grace       |    admiral    |    40 |\n"
        "| Alan Turing | mathematician |     1 |\n"
    )
    assert format_document(src) == expected


def test_left_alignment_marker_preserved():
    src = (
        "a|b\n"
        ":--|--\n"
        "x|y\n"
    )
    out = format_document(src)
    lines = out.splitlines()
    assert lines[1] == "| :-- | --- |"


def test_ragged_rows_are_padded_and_truncated():
    src = (
        "a | b | c\n"
        "--- | --- | ---\n"
        "short\n"
        "way | too | many | cells | here\n"
    )
    out = format_document(src)
    lines = out.splitlines()
    # header defines 3 columns; every body row must match
    assert lines[2] == "| short |     |      |"
    assert lines[3] == "| way   | too | many |"


def test_escaped_pipe_kept_as_literal_in_cell():
    src = (
        "a | b\n"
        "--- | ---\n"
        r"1\|2 | x" "\n"
    )
    out = format_document(src)
    assert "1|2" in out.splitlines()[2]


def test_table_inside_code_fence_is_untouched():
    src = (
        "```\n"
        "a | b\n"
        "--- | ---\n"
        "1 | 2\n"
        "```\n"
    )
    assert format_document(src) == src


def test_table_outside_fence_is_touched_fence_is_not():
    src = (
        "a|b\n"
        "---|---\n"
        "1|2\n"
        "\n"
        "```\n"
        "x|y\n"
        "---|---\n"
        "```\n"
    )
    out = format_document(src)
    lines = out.splitlines()
    assert lines[0] == "| a   | b   |"
    # fenced block preserved verbatim, table-looking lines inside left alone
    assert lines[-4:] == ["```", "x|y", "---|---", "```"]


def test_no_trailing_newline_preserved():
    src = "a|b\n---|---\n1|2"
    out = format_document(src)
    assert not out.endswith("\n")


def test_trailing_newline_preserved():
    src = "a|b\n---|---\n1|2\n"
    out = format_document(src)
    assert out.endswith("\n")


def test_non_table_text_is_left_alone():
    src = "just some prose\nwith no tables at all\n"
    assert format_document(src) == src


def test_minimum_column_width_is_respected():
    src = (
        "a | b\n"
        "--- | ---\n"
        "1 | 2\n"
    )
    out = format_document(src)
    # single-char columns still get padded to MIN_COL_WIDTH (3) dashes
    assert out.splitlines()[1] == "| --- | --- |"


def test_pipe_inside_inline_code_span_not_split():
    src = (
        "Syntax | Meaning\n"
        "--- | ---\n"
        "`a|b` | pipe example\n"
    )
    out = format_document(src)
    lines = out.splitlines()
    assert lines[0] == "| Syntax | Meaning      |"
    assert lines[2] == "| `a|b`  | pipe example |"


def test_pipe_inside_multi_backtick_code_span_not_split():
    src = (
        "a | b\n"
        "--- | ---\n"
        "`` a | `b `` | x\n"
    )
    out = format_document(src)
    lines = out.splitlines()
    assert lines[2] == "| `` a | `b `` | x |"


def test_inline_code_pipe_alone_does_not_start_a_table():
    src = "Use `a|b` for the pipe operator.\n---\nMore text.\n"
    assert format_document(src) == src


def test_right_alignment_separator_shape():
    src = (
        "a | b\n"
        "---: | ---:\n"
        "1 | 22\n"
    )
    out = format_document(src)
    lines = out.splitlines()
    assert lines[1] == "| --: | --: |"
    assert lines[2] == "|   1 |  22 |"
