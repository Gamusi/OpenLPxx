# OpenLP Anglican — Offline Church Presentation Software

**A simple, offline presentation system designed to make Anglican worship services easier to prepare and project.**

OpenLP Anglican is a customized distribution of the free and open-source **OpenLP 3.1.7** church presentation software, prepared specifically for Anglican churches where internet access may be expensive, unreliable, or unavailable.

It helps churches display **hymns, Bible verses, prayers, liturgy, announcements, pictures, and videos** on a projector or large screen during worship services, while allowing the operator to prepare and preview the next item privately on the computer screen.

> **Upstream Attribution:** This project is built on **[OpenLP](https://openlp.org/)** (`v3.1.7`), originally developed by the **OpenLP Developers and contributors** (`Copyright (c) 2008–2024 OpenLP Developers`). All credit for the core application, architecture, and features belongs to the upstream OpenLP team:
> - **Official OpenLP Website:** https://openlp.org/
> - **Upstream Source Code:** https://gitlab.com/openlp/openlp
>
> *OpenLP Anglican is an independently maintained customization and is **not** an official release of the OpenLP project.*

---

## What Can It Do?

- **Display Hymns:** Prepared to support **412 Anglican hymns** with individual verses and searchable titles, lyrics, and hymn numbers so the congregation can sing along clearly.
- **Read and Project Bible Verses:** Includes the complete 66-book **World English Bible (WEB)** (`31,103` verses, Public Domain) for fast Scripture lookup and readable slide projection, plus a two-file CSV Bible import template (`books.csv` / `verses.csv`) for adding other authorized translations.
- **Display Prayers and Liturgy:** Prepared to support **39 Anglican liturgical items** (prayers, collects, creeds, confessions, and responses from *Come and Worship*) in OpenLP's Custom Slides library, preserving speaker labels such as `Leader:`, `Minister:`, `People:`, and `All:`.
- **Reusable Orders of Service:** Includes ready-made **Anglican Morning Prayer** and **Anglican Holy Communion** service templates (`.osz`) that churches can customize, rearrange, and save for weekly worship.
- **Preview Before Displaying Live:** Operators can search and preview the next hymn, Scripture reading, or prayer on the computer monitor without interrupting what the congregation sees on the projector.
- **Manage Local Church Content:** Churches can add their own hymns (directly or via a spreadsheet-friendly CSV → OpenLyrics converter), edit prayers, and save local services. Local church data is stored in a dedicated user profile designed to survive software updates and uninstallation.

---

## Works Completely Offline

Once installed, OpenLP Anglican requires **no internet connection** for setup or daily worship use:

- No first-time online setup wizard or runtime downloads.
- All required runtime components (Python 3.11, PyQt5, QtWebEngine, and 64-bit VLC/libVLC media support) are bundled for offline operation.
- Startup optimizations skip disabled PowerPoint and LibreOffice Impress COM probes so the application opens quickly on modest hardware while keeping both presentation controllers optional in Settings.

### Basic System Requirements

- **Operating System:** Windows 10 or Windows 11 (64-bit)
- **Memory:** 4 GB RAM recommended
- **Display:** Any wired projector or secondary screen (HDMI / VGA)
- **Privileges:** Administrator rights required only during initial installation; everyday operation runs under a standard user account.

---

## Current Project Status (Not Yet for Public Download)

**Development & Validation Stage:** This repository currently holds the source baseline, conversion tools, and local packaging configuration. **No public installer is released for general download yet**, pending:

1. **Content Redistribution Permissions:** Written authorization for redistributing third-party copyrighted hymnals, liturgical texts (*Come and Worship*), and copyrighted Bible translations (such as the *Good News Bible*).
2. **Clean-Machine & Hardware Validation:** Final testing on clean Windows 10/11 church workstations with physical projectors and live media playback.

---

## Licensing, Source Availability, and Content Permissions

- **Application Software (`GPL-3.0-or-later`):** OpenLP and the software modifications in this repository (`openlp-source/`) are free software licensed under the **GNU General Public License v3.0 or later** (see [`openlp-source/LICENSE`](openlp-source/LICENSE) and [`openlp-source/copyright.txt`](openlp-source/copyright.txt)). Recipients of any binary distribution built from this project are entitled to receive the complete corresponding modified source code under the GNU GPL v3+.
- **Third-Party Runtime Libraries:** Bundled runtime libraries (including Python, Qt5/PyQt5, VLC/libVLC, SQLAlchemy, and others) remain governed by their respective upstream open-source licenses.
- **Worship Content Separation:** Bibles, hymnals, and liturgical texts used with OpenLP are separate works governed by their own copyright terms; they are **not** licensed under the GNU GPL merely because OpenLP is GPL-licensed:
  - **World English Bible (`engwebp`):** Dedicated to the **Public Domain**.
  - **Anglican Hymnal & *Come and Worship* Liturgical Texts:** Subject to the copyright of their respective rights holders (e.g., Church of Uganda / Centenary Publishing House Ltd.) and must not be publicly redistributed without permission.
  - **Good News Bible (GNB):** Copyrighted translation; not bundled without appropriate licensing.
