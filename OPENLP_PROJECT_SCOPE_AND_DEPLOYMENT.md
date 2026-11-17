# OpenLP Anglican Offline Distribution — Project Scope & Deployment Specification

**Status:** Agreed product requirements / baseline for Gemini agents  
**Date:** 17 November 2026  
**Project workspace:** `D:\OpenLPxx`  
**Reference software:** OpenLP 3.1.7  
**Document purpose:** Single standing reference for planning and implementing a minimally modified, ready-to-use, offline OpenLP distribution for local Anglican churches in Uganda.

> **Decision rule:** Does this change materially improve the product's functionality, reliability, usability, or maintainability in its *actual deployment environment*? If not, we probably don't need it.

## 1. Product objective

Deliver **one identical, complete, offline Windows installer** that installs OpenLP with an English-language interface, ready-to-use Anglican worship materials, approved Bible translations, sensible display settings, and no first-run online downloads or content-import steps. Churches receive the same standard product but can thereafter manage their **own independent local data**.

This project is **not** a rewrite, a new projection platform, a major UI redesign, or a general-purpose software-engineering exercise. The core product is OpenLP; customize only where the existing product cannot meet a confirmed deployment need.

### Definition of success

A minimally trained church operator can install the complete package without internet, launch it directly into a usable OpenLP workspace, prepare and conduct a service (planned or spontaneous), locate hymns and Bible passages quickly, project to a wired second display, locally add/edit content, back up data using native facilities, and install a newer offline release without losing local changes.

## 2. Actual deployment environment — locked

| Area | Agreed requirement |
|---|---|
| Sites | Independent local Anglican churches; one shared standard distribution across churches |
| Typical workstation | One older Windows desktop/laptop per site |
| Windows | Windows 10 and Windows 11 are expected; older systems are not committed targets |
| Memory | Aim for usability on 4 GB RAM machines; less than 4 GB is best-effort until tested |
| Display | One wired projector (e.g. HDMI/VGA); no LAN, router, or network equipment assumed |
| Internet | No internet for installation or everyday worship use |
| Operators | Very basic computer literacy |
| Installer | One self-contained offline Windows installer `.exe`; administrator rights permitted **during setup only** |
| Daily privileges | Running OpenLP must not require administrator rights |
| Branding | Retain existing OpenLP name, logo, identity and standard UI |
| Local content | Churches independently add, edit, remove and organize their own content |
| Updates | Periodic offline installer upgrades delivered by USB/file transfer; existing local content/settings must survive |
| Backup | Use OpenLP's existing manual backup/export/restore capabilities plus concise user guidance; no new backup subsystem |

**Installer interpretation:** “Single executable” means one **complete offline installer file** that contains the app and dependencies, not necessarily a literally self-contained, no-extraction portable `.exe`. Do not pursue single-binary packaging if a conventional installer meets the requirement.

## 3. Experience and workflow — locked

### 3.1 First launch

- Launch straight into **fully configured OpenLP**; no first-time setup wizard, download prompt, manual database initialization, or manual import of bundled materials.
- Include all **legally distributable** standard hymns, permitted Bible texts, Anglican liturgical items, prebuilt service templates, and sensible visual settings.
- If OpenLP normally retrieves first-run resources online, solve that only as much as is necessary to make the offline, preloaded experience work.
- Preserve the stock English OpenLP interface and branding.

### 3.2 Worship operation

- Support **both** preparation of an entire service in advance and spontaneous lookup/projection of unplanned hymns, Bible passages and prayers during worship.
- Use OpenLP's existing **Service Manager**, **Preview**, **Live**, **search**, and projector functionality.
- The congregation sees the actual Live output on the projector, **not** operator actions/searches on the computer screen.
- A computer without a connected projector should remain usable for preparation and preview using stock OpenLP behavior; do not build a separate display controller.
- Default projection aesthetic: **simple, highly readable text**. Keep existing rich-media/background/video/theme capabilities available for occasional use.
- Bible slides: use OpenLP's existing **automatic, readability-focused** splitting/formatting (avoid custom rendering).
- Hymns: preserve individually identified verses, choruses, numbering, and verse order, so operators can use stock OpenLP functionality to present selected, skipped or repeated verses.

### 3.3 Reusable Anglican services and custom material

- Supply complete **ready-made Anglican orders of service** containing the **actual authorized prayers, responses, creeds and other liturgical texts**, not empty headings alone.
- Churches can open a prepared service, change hymns/readings/items, rearrange it and save their own version; preserve the original standard template from accidental overwriting where feasible using existing workflows.
- Individual prayers, creeds, confessions, responses and liturgical sections go in **OpenLP's existing Custom Slides library** under descriptive, searchable titles.
- The same individual items can also appear in preloaded full service templates.
- Liturgical dialogue includes appropriate **speaker labels**, e.g. `Minister:`, `Congregation:`, `Reader:`, `All:`. Do not create a special renderer for these labels.
- Use *Come and Worship* as a candidate content source, subject to extractability, accurate organization, and permissions.

## 4. Content and organization — locked

### 4.1 Language

- **Application interface: English only.**
- Imported hymns, prayers and Bibles may use **any language**, including Ugandan languages. No language-specific code paths or translation-switch feature is required.
- Formats are defined by **structure** (song, stanza, chorus; Bible book/chapter/verse), not language.
- Ensure text survives Unicode import/export and relevant characters render in available fonts; treat this as compatibility, not a new multilingual subsystem.

### 4.2 Hymns and songs

- Include standard authorized hymn collections, beginning with the **414 Luganda hymns** found in the supplied Anglican Hymnal APK, insofar as permissions permit distribution.
- Preserve **hymnbook/collection**, **hymn number**, **title**, **lyrics**, **individual verses**, **choruses** and **verse order**.
- Operators must be able to locate a hymn by **collection + number** (e.g. “Anglican 25”) and by **title/lyrics**, even when several collections contain the same number.
- Use existing OpenLP song search/library behavior first; if collection+number lookup proves inadequate, implement the smallest change necessary rather than inventing a new song database.
- Local users must be able to add and correct songs later.

**Agreed user-facing import path:**

1. Provide a **universal, spreadsheet-friendly CSV template** (human-editable in Excel/LibreOffice) containing the necessary song metadata and clearly delimited verses/choruses.
2. Supply a **lightweight external CSV → OpenLyrics XML converter**; keep it outside OpenLP core.
3. Import generated OpenLyrics with OpenLP's **existing** song import wizard.
4. Support batch import of hymn collections. Do not require operators to know XML or SQL.

The precise CSV column schema is a **small implementation decision still to design and test**. Avoid rigid “Verse 1 … Verse 99” columns if a cleaner, variable-length schema is more reliable. Deliver one simple example template and a short instruction sheet.

### 4.3 Bible translations

- Initial distribution should bundle commonly used **authorized** Bible translations, with **Good News Bible / Good News Translation (GNB/GNT)** a specifically desired translation.
- **World English Bible (WEB) is NOT Good News Bible.** It may serve as an openly distributable baseline or additional translation but **does not satisfy the GNB requirement**.
- The supplied Konibee Bible APK **does not contain Bible text**. Do not pretend it provides an extractable GNB. Obtain a legitimate separate Bible source.
- A complete copyrighted translation, including GNB, must **not** be embedded in a distributable installer without suitable authorization/redistribution rights. Until then, include eligible translations and document GNB as a **pending content dependency**, not a completed feature.
- Use OpenLP's existing Bible library, search and projection tools; no new Bible database engine or slide renderer.

**Agreed import facilities:**

- Provide a simple **two-file CSV Bible import template** and short instructions (`books.csv` / `verses.csv`, using the exact schema confirmed against OpenLP 3.1.7).
- Retain OpenLP's existing **OSIS** and **Zefania XML** import options for already-compatible datasets.
- Multiple translations and arbitrary content languages should remain supported.
- Do not manually retype complete Bibles or build an additional importer unless native functionality fails a confirmed need.

### 4.4 Liturgical materials

- Anglican Hymnal APK includes 16 liturgical/creed/tract entries in addition to its hymns, with one duplicate archive entry to handle during extraction.
- *Come and Worship* contains service/liturgy resources and possibly additional hymns, but requires decoding Android compiled `resources.arsc` to recover accurate keys, order and text.
- Import reusable liturgical material as native **Custom Slides** and complete service arrangements as **OpenLP service files** wherever possible.
- Do not create a separate liturgy management UI.
- Preserve content provenance and verify that text/ordering were imported accurately before shipping.

## 5. Current assets and technical findings

**Workspace:** `D:\OpenLPxx` (per Gemini's environment report). Original files at report time:

```text
D:\OpenLPxx\
├── OpenLP-3.1.7.tar.gz
├── com-konibee-bible-20200406-62230566-0d41b0f05d518f8e5119eba9bee30426.apk
├── com.certapps.anglicanhymnal_2.11.apk
└── Come+and+Worship_23.0_APKPure.xapk
```

The user additionally confirmed that **OpenLP is already installed locally**. The source archive is available to extract; the installed application should remain an undisturbed working reference.

**Verified by Gemini's reconnaissance (not independently re-tested here):**

| Source | Finding | Minimal path |
|---|---|---|
| OpenLP 3.1.7 source | Python desktop app built on **PyQt5/PyQtWebEngine** (not PySide6), with native Songs, Bibles, Custom Slides, Services | Extract and use existing source/importers |
| Anglican Hymnal APK | `assets/hymn1.txt`–`hymn414.txt`, `assets/list.txt`, plus liturgical text entries; straightforward plaintext ZIP entries | External conversion to OpenLyrics; liturgical items into Custom Slides |
| Come and Worship XAPK | Base APK content embedded in compiled Android `resources.arsc`, not plaintext DB; ordered associations require targeted decoding | Decode only needed assets; import into existing OpenLP content model |
| Konibee Bible APK | Reader/downloader with **no bundled Bible text** | Seek separate authorized Bible dataset |
| REA | `rea-agents` 6.9.0 MCP successfully activated in Antigravity | Use selectively; no additional RE engines unless a concrete extraction blocker requires one |
| Python | Host Python 3.14.2; possible compatibility risk for OpenLP 3.1.7 dependencies | Use a compatible isolated runtime if needed; verify with a working source launch |
| G-Code skills | 8 installed globally under `.gemini\config\skills` with Superpowers available | Use selectively for focused tasks |

**Likely existing OpenLP formats (source-reviewed by Gemini):** Songs: OpenLyrics XML; Bibles: CSV, OSIS, Zefania; Services: `.osz`/`.oszl`; Custom Slides: existing custom-library database and items. Verify exact format constraints when writing each converter, not via another broad audit.

### Proposed workspace layout (not yet an authorized change)

Keep original archives separate from extracted source and derived conversion outputs. A simple arrangement is adequate, e.g. `openlp-source/`, `tools/`, and `research/` alongside the original packages. **Do not reorganize files without a scoped task approving it.**

## 6. Offline packaging and upgrade behavior — locked

### Fresh installation

- Distribute one conventional Windows installer executable usable from USB with **no network**.
- Bundle OpenLP executable/runtime, all required app dependencies, approved standard library data, service templates, themes and initial settings.
- Create normal shortcuts and start OpenLP in a ready-to-use state with its **standard interface**.
- Elevated permissions may be used for installation, not daily operation.
- Avoid requiring installation of Python, Qt, Java, Node, runtime packages, or Internet-based downloads on the church machine.
- Use OpenLP's existing display selection/projection behavior; physical Windows/projector extended-desktop setup may still need basic user configuration.

### Subsequent upgrades

- New releases arrive as **complete offline installers** and can be applied to an existing installation.
- Keep program binaries/resources distinct from **per-church user data**.
- Preserve all church-added/modified songs, Bibles, custom slides, service files, themes and settings.
- New standard content may be *added* without overwriting local modifications. Do not assume that blind reseeding/overwriting a database is safe.
- Prefer a simple, safe, idempotent standard-content installation/update strategy, grounded in OpenLP's data handling. Do not build online synchronization or a custom update-management framework.
- Validate at minimum: fresh install offline; run as ordinary user; reinstall/upgrade retains local custom material.

### Backup

Use **existing native manual OpenLP backup/export/restore capability**, where verified. Provide a short operator guide. Do not add cloud backups, backup daemons, automatic schedulers or a new backup format. Clarify any limitations of native backup coverage in the instructions instead of claiming capabilities not tested.

## 7. Technical boundaries and exclusions

**Strong defaults:**

- Preserve OpenLP's original branding, layout, Preview, Live, projector output, search, service manager, song library, Bible library, and Custom Slides.
- Prefer **configuration, packaged data and external conversion tools** over source-code edits.
- Source changes are allowed **only** for a demonstrated deployment-critical shortfall (e.g. offline first launch or reliable library lookup), scoped to the smallest safe patch.
- Keep local installation simple and responsive on lower-spec computers; avoid unnecessary background services and heavy dependencies.

**Explicitly not in scope:**

- New UI redesign, operator/advanced mode system, new projection engine, custom language-switching system, new Bible DB engine, custom built-in hymn CSV importer, internet/LAN/cloud services, centralized content management, synchronization, user accounts, automatic backup engine, elaborate installer selection wizard, or endless quality/refactoring projects.

Do not silently add any of these as “best practice” improvements.

## 8. Agent execution contract — mandatory

### Product-first principle

**Build what the churches will actually use.** Do not convert this into an architecture redesign, repeated investigations, or a chase for theoretical completeness. Good, clean, fit-for-purpose code is required; unnecessary engineering ceremony is not.

### Working method

1. **ChatGPT and project owner decide scope here.** Gemini agents perform the specified work; do not self-authorize new product requirements.
2. Work on **one approved micro-atomic task at a time**, split into **subatomic steps** with a concrete finish line.
3. Each task prompt states: exact objective, files allowed to change, constraints, acceptance criteria, and stop condition.
4. Use **G-Code skills** (`rules`, `blueprint`, `forge`, `code-audit`, `polish`, etc.) and Superpowers **when relevant**, not ritualistically. Use subagents for genuinely separable work, not trivial file operations.
5. Apply **TDD to behavior-changing code** where tests are practical: focused failing test → minimal implementation → passing test. Extraction, copying and other mechanical tasks need simple verification, not ceremonial TDD.
6. Protect existing working functionality; run **focused regression checks** covering touched behavior and critical worship flows.
7. Report concise evidence: files modified, key decisions, tests/checks and results, actual blockers. Stop at acceptance.
8. Fix concrete high-impact failures. **No recursive audit → refactor → re-audit loops**, no speculative optimizations, no unrelated cleanup.
9. Preserve the known-working installed OpenLP application; develop against the extracted source/reference separately.
10. Never claim a feature or installer is complete until verified; keep remaining blocked content (especially GNB permissions/source) visible as pending, not hidden.

### A task is complete when

Its defined result works, its focused tests/checks pass, essential existing behavior is intact, and no material blocker remains for that task. **Then close it and move on.** Avoid repeated reviews merely because additional improvements are conceivable.

## 9. Bounded delivery roadmap

The initial working estimate discussed was **14 main tasks / about 40–50 atomic tasks**. This is a **rough planning guide**, not a requirement to create or complete 50 artificial tasks. Compress, skip or split tasks when necessary to reach a usable release sooner.

| Phase | Main task |
|---|---|
| Baseline | 1. Extract OpenLP 3.1.7 source cleanly |
| Baseline | 2. Record a clean source reference/Git baseline without disturbing installed OpenLP |
| Baseline | 3. Run an isolated compatible source environment, only if needed for build work |
| Content | 4. Extract 414 Luganda hymns and metadata |
| Content | 5. Implement universal CSV → OpenLyrics converter and example template |
| Content | 6. Decode only necessary Come and Worship liturgical resources |
| Content | 7. Assemble reusable full Anglican service templates and Custom Slides |
| Content | 8. Provide Bible CSV book/verse templates and instructions |
| Content | 9. Bundle legally authorized Bible translation(s); pursue GNB only with required rights/data |
| Configuration | 10. Prepare preloaded libraries and normal OpenLP settings |
| Configuration | 11. Ensure first launch is immediately usable and offline |
| Packaging | 12. Build self-contained offline Windows installer |
| Packaging | 13. Ensure offline installer upgrades preserve church data and add standard content safely |
| Verification | 14. Test real offline install, first launch, basic hymn/Bible/service/projection workflows, and upgrade preservation |

**Immediate next task already scoped:** **Task 1.1 — extract `OpenLP-3.1.7.tar.gz` into `D:\OpenLPxx\openlp-source` with no source edits, Git initialization, dependency installation, or unrelated work.** Gemini should only proceed when the project owner sends that prompt.

## 10. Open constraints and decisions intentionally deferred

These are **bounded implementation details or genuine dependencies**, not invitations to restart project-wide discovery:

- **Good News Bible:** Obtain a legitimate complete data source and permission to distribute it. If unavailable, release with other authorized translation(s) and clearly mark GNB as pending; do not mislabel WEB as GNB.
- **Copyright/permissions for APK-derived hymns and liturgy:** Confirm redistribution rights before distributing a church-wide installer containing the extracted texts. Technical extractability alone does not grant permission.
- **CSV layouts:** Finalize the smallest clear hymn CSV schema and actual Bible CSV schema when building templates; test with representative data and Unicode.
- **Collection + number search:** Verify whether stock OpenLP provides the needed operational lookup with collection metadata. Patch only if actually inadequate.
- **OpenLP/Python compatibility:** Validate a working source/build environment on Windows; prefer the lowest-effort compatible runtime rather than porting 3.1.7 to Python 3.14 for its own sake.
- **Installer implementation:** Use established OpenLP packaging conventions or a conventional Windows installer approach, whichever produces a reliable fully offline result with minimal change.
- **Hardware baseline:** Verify usability on a representative 4 GB Windows machine; less than 4 GB remains best effort.

## 11. Final acceptance checklist

- [ ] One installer works on a **computer with no internet** and requires no online resources.
- [ ] Installed application launches directly into **stock, English OpenLP**, ready to use.
- [ ] Approved standard hymns, Bible(s), prayers and complete Anglican service arrangements are preloaded.
- [ ] Hymns searchable by appropriate **collection/number**, title and lyrics.
- [ ] Hymn verse and chorus structure preserved; selected verse order functions.
- [ ] Bible passage lookup and default automatic readable slides work.
- [ ] Custom Slides show labeled liturgical responses correctly.
- [ ] A complete service can be prepared, modified and saved; spontaneous content can be projected.
- [ ] Preview and Live work; an attached wired projector shows only intended Live content.
- [ ] A church can add/edit its own hymns and other materials using ordinary OpenLP functions.
- [ ] Universal hymn CSV template/converter and Bible CSV templates/instructions are provided.
- [ ] Manual native backup/export and restore approach is documented and tested to the extent claimed.
- [ ] Upgrade from a previous offline release **preserves church-specific data and settings** while safely adding eligible standard resources.
- [ ] Regular operator usage does not require Windows administrator permission.
- [ ] No unlicensed copyrighted content is distributed; missing GNB rights/data remain explicitly disclosed.
- [ ] No unnecessary OpenLP redesign, parallel databases or infrastructure was introduced.

---

**Authority of this file:** This document records decisions already made in the ChatGPT deployment interview. If an implementation choice conflicts with a locked requirement, stop that particular task and ask for a targeted decision. Do not reopen settled questions or initiate broad investigations. Any change to scope must be explicitly approved by the project owner.
