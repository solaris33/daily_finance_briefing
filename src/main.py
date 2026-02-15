"""Daily market briefing entrypoint.

Phase 1: implement domestic section (KOSPI/KOSDAQ) with FinanceDataReader.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import FinanceDataReader as fdr


@dataclass
class IndexSummary:
    name: str
    close: float | None
    change_pct: float | None
    arrow: str
    color_class: str
    base_date: str | None
    error: str | None = None


def _format_close(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.2f}"


def _format_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{abs(value):.2f}%"


def fetch_index_summary(name: str, symbol: str) -> IndexSummary:
    start = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    try:
        df = fdr.DataReader(symbol, start)
        if "Close" not in df.columns or len(df) < 2:
            return IndexSummary(
                name=name,
                close=None,
                change_pct=None,
                arrow="-",
                color_class="na",
                base_date=None,
                error="not-enough-data",
            )

        last_two = df["Close"].dropna().tail(2)
        if len(last_two) < 2:
            return IndexSummary(
                name=name,
                close=None,
                change_pct=None,
                arrow="-",
                color_class="na",
                base_date=None,
                error="not-enough-close-values",
            )

        prev_close = float(last_two.iloc[0])
        close = float(last_two.iloc[1])
        change_pct = ((close - prev_close) / prev_close) * 100

        if change_pct > 0:
            arrow = "▲"
            color_class = "up"
        elif change_pct < 0:
            arrow = "▼"
            color_class = "down"
        else:
            arrow = "-"
            color_class = "flat"

        return IndexSummary(
            name=name,
            close=close,
            change_pct=change_pct,
            arrow=arrow,
            color_class=color_class,
            base_date=last_two.index[-1].strftime("%Y-%m-%d"),
        )
    except Exception as exc:  # noqa: BLE001
        return IndexSummary(
            name=name,
            close=None,
            change_pct=None,
            arrow="-",
            color_class="na",
            base_date=None,
            error=str(exc),
        )


def render_html(items: list[IndexSummary], generated_at: str) -> str:
    base_dates = [item.base_date for item in items if item.base_date]
    base_date_text = max(base_dates) if base_dates else "확인 불가"

    rows_html: list[str] = []
    for item in items:
        rows_html.append(
            f"""
            <th>{item.name}</th>
            """.strip()
        )
    header_row = "\n".join(rows_html)

    value_cells: list[str] = []
    for item in items:
        value_cells.append(
            f"""
            <td>
              <span class=\"{item.color_class}\">{_format_close(item.close)} {item.arrow} {_format_pct(item.change_pct)}</span>
            </td>
            """.strip()
        )
    value_row = "\n".join(value_cells)

    warning = ""
    failed_items = [item for item in items if item.error]
    if failed_items:
        details = ", ".join(f"{item.name}: {item.error}" for item in failed_items)
        warning = f"<p class=\"warning\">일부 데이터를 불러오지 못했습니다 ({details}).</p>"

    return f"""<!doctype html>
<html lang=\"ko\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>전일 시장 요약</title>
    <style>
      body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", sans-serif;
        margin: 24px;
        color: #222;
      }}
      h1 {{
        margin: 0 0 24px;
      }}
      h2 {{
        margin: 24px 0 8px;
      }}
      table {{
        width: 100%;
        max-width: 720px;
        border-collapse: collapse;
        border-top: 1px solid #666;
      }}
      th, td {{
        border: 1px solid #d6d6d6;
        text-align: center;
        padding: 14px 10px;
        font-size: 30px;
      }}
      th {{
        font-weight: 700;
        background: #fafafa;
      }}
      .up {{ color: #f44336; }}
      .down {{ color: #1976d2; }}
      .flat {{ color: #444; }}
      .na {{ color: #888; }}
      .meta {{ color: #666; font-size: 20px; }}
      .warning {{ color: #b26a00; font-size: 18px; max-width: 720px; }}
    </style>
  </head>
  <body>
    <h1>전일 시장 요약</h1>
    <h2>국내</h2>
    <table>
      <tr>
        {header_row}
      </tr>
      <tr>
        {value_row}
      </tr>
    </table>
    <p class=\"meta\">기준 거래일: {base_date_text}</p>
    <p class=\"meta\">생성 시각: {generated_at}</p>
    {warning}
  </body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    items = [
        fetch_index_summary("코스피", "KS11"),
        fetch_index_summary("코스닥", "KQ11"),
    ]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = datetime.now().strftime("%Y-%m-%d") + "_brief.html"
    output_path = output_dir / file_name
    output_path.write_text(render_html(items, generated_at), encoding="utf-8")
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
