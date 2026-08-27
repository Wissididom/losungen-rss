# Losungen RSS

A tool to convert daily Losungen (Watchwords) data into RSS feeds.

## About

This project automatically generates RSS feeds for the daily Losungen (German Protestant daily devotional readings), making them easily accessible through RSS readers. The Losungen are published annually by the Herrnhuter Brüdergemeine (Moravian Church).

## How it Works

1. **Data Source**: The project downloads the official Losungen CSV data from [https://www.losungen.de/download](https://www.losungen.de/download)
2. **Conversion**: A Python script converts the CSV data to RSS 2.0 format
3. **Publishing**: The RSS feeds are automatically deployed to GitHub Pages via GitHub Actions

## RSS Feeds

The following feeds are available:

- **Current Year**: `losungen.rss` - The current year's daily Losungen
- **By Year**: `losungen{YEAR}.rss` - Year-specific feeds (e.g., `losungen2026.rss`)

Each RSS feed contains:
- Daily entries with the Losung (Scripture verse and text)
- The corresponding Lehrtext (additional teaching text)
- Published date for each entry
- Bible references

## Technical Details

### Architecture

- **Language**: Python 3
- **Input**: ZIP archive containing CSV data (Windows-1252 encoded)
- **Output**: RSS 2.0 XML feeds
- **CI/CD**: GitHub Actions workflow

### Key Features

- Automatic daily updates via cron schedule (2:00 AM UTC)
- Only publishes entries up to the current date (no future entries)
- Stable GUIDs based on entry date for reliable feed aggregation
- UTF-8 XML output with proper XML escaping
- Multiple feed formats: current year and year-specific archives

## Usage

### Subscribing to the Feed

Add one of the RSS feeds to your RSS reader:

```
https://[repository-pages-url]/losungen.rss      # Current year
https://[repository-pages-url]/losungen2026.rss   # Specific year
```

### Running Locally

To test the conversion script with a downloaded ZIP file:

```bash
curl "https://www.losungen.de/fileadmin/media-losungen/download/Losung_2026_CSV.zip" | \
  python3 scripts/convert-to-rss.py
```

This will:
1. Read the ZIP from stdin
2. Extract the CSV file
3. Generate RSS feeds in the `rss/` directory

## Data Format

The CSV file contains the following columns:
- `Datum` - Date (DD.MM.YYYY format)
- `Losungsvers` - Losung verse reference
- `Losungstext` - Losung text
- `Lehrtextvers` - Teaching text verse reference
- `Lehrtext` - Teaching text
- `Sonntag` - Sunday name (if applicable)

## Repository Structure

```
.
├── scripts/
│   └── convert-to-rss.py     # Main conversion script
├── .github/
│   └── workflows/
│       └── *.yml              # GitHub Actions workflows
└── rss/                        # Generated RSS feeds (published to GitHub Pages)
```

## License

This project handles publicly available data from https://www.losungen.de/ which is maintained by the Herrnhuter Brüdergemeine (Moravian Church).

## References

- **Official Losungen Website**: https://www.losungen.de/
- **Download Page**: https://www.losungen.de/download
- **RSS 2.0 Specification**: https://www.rssboard.org/rss-specification
