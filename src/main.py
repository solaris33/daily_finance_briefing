"""Daily market briefing entrypoint.

This is a minimal placeholder so GitHub Actions can call a stable command.
Replace internals with your real FinanceDataReader-based pipeline.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def build_placeholder_html() -> str:
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html>
<html lang=\"ko\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>전일 시장 요약</title>
  </head>
  <body>
    <h1>전일 시장 요약</h1>
    <p>생성 시각: {today}</p>
    <p>TODO: FinanceDataReader 데이터 수집/렌더링 로직으로 교체하세요.</p>
  </body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = datetime.now().strftime("%Y-%m-%d") + "_brief.html"
    output_path = output_dir / file_name
    output_path.write_text(build_placeholder_html(), encoding="utf-8")
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
