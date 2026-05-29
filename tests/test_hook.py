from unittest.mock import patch

import pytest

from docprompt.hook import main, matches_any


# --- matches_any ---


def test_matches_path_prefix():
    assert matches_any("src/api.py", ["src/"])


def test_no_match_path_prefix():
    assert not matches_any("tests/test_api.py", ["src/"])


def test_matches_glob():
    assert matches_any("module.py", ["*.py"])


def test_no_match_glob():
    assert not matches_any("module.md", ["*.py"])


def test_matches_first_of_multiple_patterns():
    assert matches_any("src/main.py", ["src/", "lib/"])


def test_matches_second_of_multiple_patterns():
    assert matches_any("lib/utils.py", ["src/", "lib/"])


# --- main ---


def run_main(staged_files, code_patterns, docs_paths):
    argv = ["doc-check"]
    for p in docs_paths:
        argv += ["--docs-path", p]
    for p in code_patterns:
        argv += ["--code-pattern", p]

    with (
        patch("sys.argv", argv),
        patch("docprompt.hook.get_staged_files", return_value=staged_files),
    ):
        return main()


def test_no_staged_files_passes():
    assert run_main([], code_patterns=["src/"], docs_paths=["docs/"]) == 0


def test_only_doc_changes_passes():
    assert run_main(["docs/index.md"], code_patterns=["src/"], docs_paths=["docs/"]) == 0


def test_code_and_doc_changes_passes():
    assert run_main(["src/api.py", "docs/api.md"], code_patterns=["src/"], docs_paths=["docs/"]) == 0


def test_code_changes_without_docs_fails():
    assert run_main(["src/api.py"], code_patterns=["src/"], docs_paths=["docs/"]) == 1


def test_failure_message_names_changed_files(capsys):
    run_main(["src/api.py"], code_patterns=["src/"], docs_paths=["docs/"])
    out = capsys.readouterr().out
    assert "src/api.py" in out
    assert "docs/" in out


def test_glob_code_pattern_fails_without_docs():
    assert run_main(["module.py"], code_patterns=["*.py"], docs_paths=["docs/"]) == 1


def test_multiple_docs_paths_passes():
    assert run_main(
        ["src/api.py", "README.md"],
        code_patterns=["src/"],
        docs_paths=["docs/", "README.md"],
    ) == 0


def test_multiple_code_patterns_fails_without_docs():
    assert run_main(["lib/utils.py"], code_patterns=["src/", "lib/"], docs_paths=["docs/"]) == 1
