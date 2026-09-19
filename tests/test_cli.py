import pytest

from mdtabletidy import main

SRC = "a|b\n---|---\n1|2\n"
EXPECTED = "| a   | b   |\n| --- | --- |\n| 1   | 2   |\n"


def test_single_file_write_in_place(tmp_path):
    path = tmp_path / "one.md"
    path.write_text(SRC)

    main([str(path), "--write"])

    assert path.read_text() == EXPECTED


def test_single_file_without_write_prints_to_stdout(tmp_path, capsys):
    path = tmp_path / "one.md"
    path.write_text(SRC)

    main([str(path)])

    assert capsys.readouterr().out == EXPECTED
    assert path.read_text() == SRC


def test_multiple_files_written_in_place(tmp_path):
    first = tmp_path / "a.md"
    second = tmp_path / "b.md"
    first.write_text(SRC)
    second.write_text(SRC)

    main([str(first), str(second), "--write"])

    assert first.read_text() == EXPECTED
    assert second.read_text() == EXPECTED


def test_multiple_files_without_write_is_an_error(tmp_path):
    first = tmp_path / "a.md"
    second = tmp_path / "b.md"
    first.write_text(SRC)
    second.write_text(SRC)

    with pytest.raises(SystemExit):
        main([str(first), str(second)])


def test_glob_pattern_expands_and_writes_every_match(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.md").write_text(SRC)
    (tmp_path / "b.md").write_text(SRC)
    (tmp_path / "c.txt").write_text(SRC)

    main(["*.md", "--write"])

    assert (tmp_path / "a.md").read_text() == EXPECTED
    assert (tmp_path / "b.md").read_text() == EXPECTED
    assert (tmp_path / "c.txt").read_text() == SRC


def test_glob_pattern_with_no_matches_falls_through_to_missing_file_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError):
        main(["nothing-*.md", "--write"])
