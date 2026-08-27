#!/usr/bin/env python3

import csv
import io
import sys
import zipfile
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape


OUTPUT_DIR = Path("rss")


def xml_escape(value):
    """Escape a value for use in XML."""
    return escape(str(value or ""))


def read_zip_from_stdin():
    """Read a ZIP archive from stdin and return the CSV rows."""

    zip_data = sys.stdin.buffer.read()

    if not zip_data:
        raise RuntimeError("No data received on stdin")

    print(
        f"Received ZIP: {len(zip_data):,} bytes",
        file=sys.stderr,
    )

    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:

        csv_files = [
            name
            for name in zf.namelist()
            if name.lower().endswith(".csv")
        ]

        if not csv_files:
            raise RuntimeError("No CSV file found in ZIP archive")

        if len(csv_files) > 1:
            print(
                f"Warning: multiple CSV files found: {csv_files}",
                file=sys.stderr,
            )

        csv_name = csv_files[0]

        print(
            f"Reading CSV: {csv_name}",
            file=sys.stderr,
        )

        # The supplied CSV is Windows-1252 encoded.
        raw_csv = zf.read(csv_name)
        csv_text = raw_csv.decode("cp1252")

        reader = csv.DictReader(
            io.StringIO(csv_text),
            delimiter=";",
        )

        rows = list(reader)

    if not rows:
        raise RuntimeError("CSV contains no data rows")

    return rows


def parse_date(value):
    return datetime.strptime(value, "%d.%m.%Y")


def make_description(row):
    """Create the HTML content for an RSS description."""

    losungsvers = xml_escape(row["Losungsvers"])
    losungstext = xml_escape(row["Losungstext"])

    lehrtextvers = xml_escape(row["Lehrtextvers"])
    lehrtext = xml_escape(row["Lehrtext"])

    return (
        "<p>"
        "<strong>Losung</strong><br>"
        f"{losungsvers}<br>"
        f"{losungstext}"
        "</p>"
        "<p>"
        "<strong>Lehrtext</strong><br>"
        f"{lehrtextvers}<br>"
        f"{lehrtext}"
        "</p>"
    )


def generate_rss(rows, year):
    """Generate an RSS 2.0 document."""

    items = []

    today = datetime.now(timezone.utc).date()

    for row in rows:

        date = parse_date(row["Datum"]).date()

        # Don't publish future entries
        if date > today:
            continue

        sunday = row.get("Sonntag", "").strip()

        title = row["Datum"]

        if sunday:
            title += f" – {sunday}"

        description = make_description(row)

        # Stable ID. This should never change between builds.
        guid = f"losungen-{date.strftime('%Y-%m-%d')}"

        # RSS requires RFC 822-style dates.
        # Use UTC to avoid depending on the machine's timezone.
        pub_date = format_datetime(
            datetime.combine(
                date,
                datetime.min.time(),
                tzinfo=timezone.utc,
            ),
            usegmt=True,
        )

        item = f"""    <item>
      <title>{xml_escape(title)}</title>
      <description><![CDATA[{description}]]></description>
      <pubDate>{pub_date}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
    </item>"""

        items.append(item)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Losungen {year}</title>
    <description>Die Losung für jeden Tag des Jahres {year}</description>
    <link>https://www.losungen.de/</link>
    <language>de</language>
    <lastBuildDate>{format_datetime(datetime.now(timezone.utc), usegmt=True)}</lastBuildDate>

{chr(10).join(items)}

  </channel>
</rss>
"""


def main():

    print("Reading ZIP from stdin...", file=sys.stderr)

    rows = read_zip_from_stdin()

    # Determine the year from the first date in the CSV.
    first_date = parse_date(rows[0]["Datum"])
    year = first_date.year

    print(
        f"Detected year: {year}",
        file=sys.stderr,
    )

    rss = generate_rss(rows, year)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / f"losungen{year}.rss"
    current_file = OUTPUT_DIR / "losungen.rss"

    output_file.write_text(
        rss,
        encoding="utf-8",
    )

    current_file.write_text(
        rss,
        encoding="utf-8",
    )

    print(
        f"Generated {len(rows)} RSS items",
        file=sys.stderr,
    )

    print(
        f"Archive: {output_file}",
        file=sys.stderr,
    )

    print(
        f"Current: {current_file}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
