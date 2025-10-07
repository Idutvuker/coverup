from pathlib import Path


def enumerate_lines(text: str) -> str:
    lines = text.splitlines()

    width = len(str(len(lines)))

    numbered = [f"{i:>{width}}: {line}" for i,
                line in enumerate(lines, start=1)]
    return numbered


def test_file_to_src_file(rel_test_file: Path, test_dir: Path) -> Path:
    struct = rel_test_file.relative_to(test_dir).parent
    filename = rel_test_file.name.removeprefix("test_")
    return struct / filename


def src_file_to_test_file(rel_src_file: Path, test_dir: Path) -> Path:
    struct = rel_src_file.parent
    filename = f"test_{rel_src_file.name}"
    return test_dir / struct / filename


def create_test_file(rel_src_file: Path, test_dir: Path, project_root: Path) -> Path:
    rel_test_file = src_file_to_test_file(rel_src_file, test_dir)

    test_file = project_root / rel_test_file

    test_file.parent.mkdir(parents=True, exist_ok=True)

    for parent in list(rel_test_file.parents)[:-1]:
        (project_root / parent / "__init__.py").touch(exist_ok=True)

    test_file.touch(exist_ok=True)

    return rel_test_file
