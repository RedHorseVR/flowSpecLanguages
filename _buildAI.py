#!/usr/bin/env python3
import argparse
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional

# -------- AI backend (OpenAI) --------
def call_openai(system_prompt: str, user_prompt: str, model: str, api_key: Optional[str] = None, temperature: float = 0.2) -> str:
    """
    Calls OpenAI Chat Completions API.
    Requires: pip install openai
    Environment: OPENAI_API_KEY (or pass api_key)
    """
    try:
        from openai import OpenAI  # openai>=1.0
    except Exception as e:
        print("ERROR: The 'openai' package is required. Install with: pip install openai", file=sys.stderr)
        raise

    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    if not client.api_key:
        raise RuntimeError("OPENAI_API_KEY not set and no api_key provided.")

    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.choices[0].message.content or ""
    return content.strip()


# -------- Editor helpers --------
def open_in_editor(filepath: Path, editor: Optional[str]) -> None:
    """
    Open the given file in an editor.
    Priority:
      1) --editor flag if provided
      2) $VISUAL or $EDITOR
      3) Platform default opener (Windows: startfile, macOS: open, Linux: xdg-open)
    """
    if editor:
        try:
            subprocess.run([editor, str(filepath)], check=False)
            return
        except Exception as e:
            print(f"Warning: failed to launch editor '{editor}': {e}", file=sys.stderr)

    env_editor = os.getenv("VISUAL") or os.getenv("EDITOR")
    if env_editor:
        try:
            subprocess.run([env_editor, str(filepath)], check=False)
            return
        except Exception as e:
            print(f"Warning: failed to launch $VISUAL/$EDITOR '{env_editor}': {e}", file=sys.stderr)

    # Fallback to platform default
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(filepath))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(filepath)], check=False)
        else:
            subprocess.run(["xdg-open", str(filepath)], check=False)
    except Exception as e:
        print(f"Warning: failed to open with system default: {e}", file=sys.stderr)


# -------- Core logic --------
def derive_output_path(vfc_path: Path) -> Path:
    """
    Remove a single trailing '.vfc' extension from the filename.
    e.g. /a/b/thing.txt.vfc -> /a/b/thing.txt
         /a/b/thing.vfc     -> /a/b/thing
    """
    if vfc_path.suffix == ".vfc":
        return vfc_path.with_suffix("")
    # If someone passed a weird filename without .vfc, still do the best we can
    name = vfc_path.name
    if name.endswith(".vfc"):
        return vfc_path.with_name(name[:-4])
    # Otherwise, keep the same but without changing (shouldn't happen in normal use)
    return vfc_path


def main():
    parser = argparse.ArgumentParser(
        description="Run an AI with a .vfc file as the system prompt, save output to <filename> (without .vfc), and open it."
    )
    parser.add_argument("vfc_file", type=str, help="Path to the .vfc file")
    parser.add_argument(
        "-p", "--prompt",
        type=str,
        required=True,
        help="User prompt to send to the AI (the .vfc contents are used as SYSTEM prompt)."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="Model name for the AI backend (default: gpt-4o-mini)."
    )
    parser.add_argument(
        "--backend",
        type=str,
        choices=["openai"],
        default="openai",
        help="AI backend to use (currently only 'openai')."
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key for the backend; if omitted, uses environment variable (e.g., OPENAI_API_KEY)."
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature (default: 0.2)."
    )
    parser.add_argument(
        "--editor",
        type=str,
        default=None,
        help="Editor command to open the output (e.g., 'code', 'notepad', 'vim'). If omitted, uses $VISUAL/$EDITOR or OS default."
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite output file if it exists."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run through prompts and show what would happen without calling the AI or writing files."
    )

    args = parser.parse_args()

    vfc_path = Path(args.vfc_file).expanduser().resolve()
    if not vfc_path.exists():
        print(f"ERROR: input file not found: {vfc_path}", file=sys.stderr)
        sys.exit(1)

    try:
        system_prompt = vfc_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"ERROR: failed to read {vfc_path}: {e}", file=sys.stderr)
        sys.exit(1)

    out_path = derive_output_path(vfc_path)

    if out_path.exists() and not args.force:
        print(f"ERROR: output file already exists: {out_path}\nUse --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"Backend: {args.backend}")
        print(f"Model: {args.model}")
        print(f"Input (.vfc): {vfc_path}")
        print(f"Output: {out_path}")
        print(f"User prompt: {args.prompt}")
        print(f"System prompt length: {len(system_prompt)} characters")
        sys.exit(0)

    # Call AI
    try:
        if args.backend == "openai":
            ai_output = call_openai(system_prompt, args.prompt, model=args.model, api_key=args.api_key, temperature=args.temperature)
        else:
            raise ValueError(f"Unsupported backend: {args.backend}")
    except Exception as e:
        print(f"ERROR: AI call failed: {e}", file=sys.stderr)
        sys.exit(2)

    # Write output
    try:
        out_path.write_text(ai_output, encoding="utf-8")
    except Exception as e:
        print(f"ERROR: failed to write output to {out_path}: {e}", file=sys.stderr)
        sys.exit(3)

    # Open in editor
    open_in_editor(out_path, args.editor)

    print(f"Saved AI output to: {out_path}")

if __name__ == "__main__":
    main()
