# Hymn CSV Template Guide

## Schema

UTF-8 CSV (with or without BOM) using the header:

```csv
collection,number,title,section,text
```

- `collection`: Hymnbook or collection name (mapped to `<songbook name="..."/>`).
- `number`: Hymn number within the collection (mapped to `<songbook entry="..."/>`).
- `title`: Song title (mapped to `<titles><title>...</title></titles>`).
- `section`: OpenLyrics verse/section tag such as `v1`, `v2`, `c1`, `b1`, `p1`, `e1`, `i1`, `o1`.
- `text`: Section lyrics. Multi-line cells inside quotes preserve internal line breaks.

## Grouping and Order

- Rows sharing the same `(collection, number)` belong to one hymn and must have a consistent `title`.
- Sections are emitted in the exact order they appear in the CSV, and `<verseOrder>` records that sequence.
- If a section tag (such as `c1`) is repeated in the CSV with identical text, it is emitted once in `<lyrics>` and referenced multiple times in `<verseOrder>`.

## Example

See [hymn_template.csv](hymn_template.csv) for a multi-verse + repeated-chorus example.

## Usage

```powershell
python csv_to_openlyrics.py hymn_template.csv out_xml/
```
