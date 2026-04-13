from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


PROFILE_LAYERS: Dict[str, List[str]] = {
    "base": ["base"],
    "isaaclab": ["base", "isaaclab"],
}

TEMPLATE_SUFFIX = ".jinja"
PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


@dataclass(frozen=True)
class RenderedFile:
    relative_path: Path
    content: str
    source_layer: str


def template_root() -> Path:
    return Path(__file__).resolve().parent / "templates"


def available_profiles() -> List[str]:
    return sorted(PROFILE_LAYERS)


def render_text(template_text: str, context: Dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return context.get(key, match.group(0))

    return PLACEHOLDER_PATTERN.sub(replace, template_text)


def iter_layer_files(layer: str) -> Iterable[Path]:
    layer_root = template_root() / layer
    if not layer_root.exists():
        raise FileNotFoundError(f"Template layer does not exist: {layer}")
    yield from sorted(path for path in layer_root.rglob("*") if path.is_file())


def output_path_for(template_path: Path, layer: str) -> Path:
    relative_path = template_path.relative_to(template_root() / layer)
    if template_path.name.endswith(TEMPLATE_SUFFIX):
        return relative_path.with_name(template_path.name[: -len(TEMPLATE_SUFFIX)])
    return relative_path


def build_file_plan(profile: str, context: Dict[str, str]) -> List[RenderedFile]:
    if profile not in PROFILE_LAYERS:
        raise KeyError(f"Unknown profile: {profile}")

    plan: Dict[Path, RenderedFile] = {}
    for layer in PROFILE_LAYERS[profile]:
        for template_path in iter_layer_files(layer):
            output_path = output_path_for(template_path, layer)
            content = render_text(template_path.read_text(encoding="utf-8"), context)
            plan[output_path] = RenderedFile(
                relative_path=output_path,
                content=content,
                source_layer=layer,
            )
    return sorted(plan.values(), key=lambda item: item.relative_path.as_posix())


def write_files(
    files: Iterable[RenderedFile],
    target_dir: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> List[Path]:
    written_paths: List[Path] = []
    conflicts = []

    for rendered_file in files:
        destination = target_dir / rendered_file.relative_path
        if destination.exists() and not force:
            conflicts.append(rendered_file.relative_path.as_posix())

    if conflicts:
        conflict_list = "\n".join(f"- {path}" for path in conflicts)
        raise FileExistsError(
            "Refusing to overwrite existing files without --force:\n"
            f"{conflict_list}"
        )

    for rendered_file in files:
        destination = target_dir / rendered_file.relative_path
        written_paths.append(destination)
        if dry_run:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered_file.content, encoding="utf-8")

    return written_paths


def build_context(target_dir: Path) -> Dict[str, str]:
    return {
        "repo_name": target_dir.resolve().name,
    }


def handle_init(args: argparse.Namespace) -> int:
    target_dir = Path(args.target).resolve()
    context = build_context(target_dir)
    file_plan = build_file_plan(args.profile, context)
    written_paths = write_files(
        file_plan,
        target_dir,
        force=args.force,
        dry_run=args.dry_run,
    )

    action = "Planned" if args.dry_run else "Wrote"
    print(f"{action} {len(written_paths)} files for profile '{args.profile}' in {target_dir}")
    for path in written_paths:
        print(f"- {path.relative_to(target_dir)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="isaac-agent-kit",
        description="Initialize coding-agent instructions for Python and Isaac Lab repositories.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init",
        help="Render agent instruction templates into a target repository.",
    )
    init_parser.add_argument(
        "--profile",
        choices=available_profiles(),
        default="isaaclab",
        help="Template profile to render.",
    )
    init_parser.add_argument(
        "--target",
        default=".",
        help="Directory that should receive the rendered files.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated files.",
    )
    init_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the files that would be written without changing the repository.",
    )
    init_parser.set_defaults(func=handle_init)

    profiles_parser = subparsers.add_parser(
        "profiles",
        help="List available template profiles.",
    )
    profiles_parser.set_defaults(func=handle_profiles)

    return parser


def handle_profiles(_: argparse.Namespace) -> int:
    for profile in available_profiles():
        print(profile)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (FileNotFoundError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
