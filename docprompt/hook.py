import argparse
import subprocess
import sys
from fnmatch import fnmatch


def get_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


def matches_any(path, patterns):
    return any(path.startswith(p) or fnmatch(path, p) for p in patterns)


def main():
    parser = argparse.ArgumentParser(
        description="Fail if code changes are staged without corresponding documentation updates."
    )
    parser.add_argument(
        "--docs-path",
        required=True,
        action="append",
        dest="docs_paths",
        metavar="PATH",
        help="Path prefix for documentation files (repeatable)",
    )
    parser.add_argument(
        "--code-pattern",
        required=True,
        action="append",
        dest="code_patterns",
        metavar="PATTERN",
        help="Glob pattern or path prefix for code files that require doc updates (repeatable)",
    )
    args = parser.parse_args()

    staged = get_staged_files()

    code_changes = [f for f in staged if matches_any(f, args.code_patterns)]
    if not code_changes:
        return 0

    doc_changes = [f for f in staged if matches_any(f, args.docs_paths)]
    if doc_changes:
        return 0

    print("doc-check: code changes staged without documentation updates.\n")
    print("Changed code files:")
    for f in code_changes:
        print(f"  {f}")
    print(f"\nNo changes found under: {', '.join(args.docs_paths)}")
    print("\nUpdate the docs, or skip this check for this commit with:")
    print("  SKIP=doc-check git commit ...")
    return 1


if __name__ == "__main__":
    sys.exit(main())
