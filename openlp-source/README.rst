OpenLP
======

You're probably reading this because you've just downloaded the source code for
OpenLP. If you are looking for the installer file, please go to the download
page on the web site:

    https://openlp.org/#download

If you're looking for how to contribute to OpenLP, then please look at the
OpenLP wiki:

    https://wiki.openlp.org/

Thanks for downloading OpenLP!

Customized Offline Anglican Distribution Notice
-----------------------------------------------

This repository contains an independently maintained, customized distribution
based on **OpenLP 3.1.7** for offline Anglican church worship use. It is **not**
an official release of the OpenLP project.

Upstream Attribution
~~~~~~~~~~~~~~~~~~~~

OpenLP is developed by the **OpenLP Developers and contributors**
(``Copyright (c) 2008-2024 OpenLP Developers``):

- Official OpenLP website: https://openlp.org/
- Upstream source repository: https://gitlab.com/openlp/openlp

All credit for the core OpenLP application, architecture, and features belongs
to the upstream OpenLP team and community.

Summary of Customizations
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Startup optimization:** ``openlp/plugins/presentations/lib/presentationtab.py``
  skips the PowerPoint and LibreOffice Impress availability probes during
  startup when those controllers are disabled in settings, while keeping both
  options configurable.
- **Offline deployment configuration:** Prepared to work with a preconfigured
  offline user data profile (Bibles, hymns, Custom Slides, and reusable
  service templates) without requiring first-run internet access.

Licensing, Source Availability, and Content Notice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Application software (GPL-3.0-or-later):** OpenLP and the source-code
  modifications in this repository are free software licensed under the
  **GNU General Public License v3.0 or later** (see ``LICENSE`` and
  ``copyright.txt``). Any recipient of a binary installer built from this
  repository is entitled to receive the complete corresponding modified source
  code under the terms of the GNU GPL v3+.
- **Third-party runtime libraries:** Bundled runtime dependencies (including
  Python, Qt5/PyQt5, VLC/libVLC, SQLAlchemy, and others) remain subject to
  their respective upstream open-source licenses.
- **Worship content separation:** Bibles, hymnals, and liturgical texts loaded
  into or distributed alongside OpenLP are separate content works governed by
  their own copyright and redistribution terms; they are **not** licensed under
  the GNU GPL merely by being used with OpenLP. The *World English Bible*
  (``engwebp``) is in the Public Domain. Third-party hymnals, liturgical books
  (such as *Come and Worship*), and copyrighted Bible translations (such as the
  *Good News Bible*) require separate authorization from their respective
  rights holders before public redistribution.

