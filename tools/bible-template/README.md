# OpenLP 3.1.7 Bible CSV Import Template

This template matches OpenLP 3.1.7's native **CSV Bible Importer** (`openlp/plugins/bibles/lib/importers/csvbible.py`).

## Files

1. **`books.csv`** — Four required columns in exact order:
   ```csv
   book_id,testament_id,book_name,book_abbreviation
   ```
   - `book_id`: Integer book identifier (e.g., `1` for Genesis, `40` for Matthew).
   - `testament_id`: `1` = Old Testament, `2` = New Testament.
   - `book_name`: Canonical book name recognized by OpenLP (or mapped during import).
   - `book_abbreviation`: Short book abbreviation (e.g., `Gen`, `Matt`).

2. **`verses.csv`** — Four required columns in exact order:
   ```csv
   book_id,chapter_number,verse_number,verse_text
   ```
   *(OpenLP also accepts `book_name` in column 1 instead of `book_id`.)*
   - `book_id`: Matches `book_id` in `books.csv`.
   - `chapter_number`: Integer chapter number (`>= 1`).
   - `verse_number`: Integer verse number (`>= 1`).
   - `verse_text`: Verse text enclosed in double quotes `"` if it contains commas or quotes.

## Formatting & Encoding Rules

- **Encoding:** UTF-8 (`utf-8` or `utf-8-sig`) — preserves Unicode characters such as Luganda `ŋ` and typographic punctuation.
- **Delimiter / Quoting:** Comma (`,`) delimiter and double quotes (`"`).
- **Header Row:** Optional; OpenLP auto-detects and skips a non-numeric header row.

## Preparing & Importing a Licensed Bible

1. Convert your **appropriately licensed** Bible dataset into `books.csv` and `verses.csv` following the column order above (replace the synthetic sample rows).
2. In OpenLP, open **File → Import → Bible**.
3. Choose **CSV** as the format, select `books.csv` and `verses.csv`, enter the Bible version name, copyright, and permissions, and complete the wizard.
