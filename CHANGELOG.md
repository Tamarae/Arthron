# Changelog

All notable changes to the *სიტყუაჲ ართრონთათჳს* Digital Scholarly Edition are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Variant filter UI (filter by orthographic/lexical/morphological/omission/addition)
- Synoptic alignment view (A / S / lemma columns)
- Client-side search with Lunr.js
- `<seg type="rule|example">` markup in treatise

---

## [2.4.0] - 2025-01-24

### Added
- **Academic metadata** in `base.html`: Dublin Core, Highwire Press tags for Google Scholar
- **SEO files**: `sitemap.xml` (210+ URLs), `robots.txt`
- **Lexicon notes**: `<note>` elements now displayed on entry pages
- Google Search Console verification

### Fixed
- Homily popup term links now use correct relative path (`../lexicon/`)

---

## [2.3.0] - 2025-01-20

### Added
- **Homily integration**: Full TEI encoding of John Chrysostom's Ი̃Თ Homily
  - 75 paragraphs with CTS URNs
  - 59 notes (biblical and editorial) with filter panel
  - 68 term links to lexicon
  - Pagination (15 paragraphs per page)
- **Term index**: Cross-references across all three sources (treatise, homily, research)
- **Source legend**: Color-coded references (§ amber, ჰ. green, ¶ indigo)
- Navigation link: ᲰᲝᲛᲘᲚᲘᲐ added to main menu
- Lexicon expanded to 179 entries

### Changed
- Lexicon entry page: Simplified fonts, added homily color class for occurrences

### Fixed
- Lexicon occurrence links corrected (`../` path)

---

## [2.2.0] - 2025-01-17

### Added
- **Manuscripts page**: Dynamic variant statistics pulled from TEI XML
- **About page**: Enhanced credits section, methodology, edition statistics

### Changed
- Navigation label: საძიებელი → კვლევა

### Fixed
- Research article rendering confirmed functional (115 ¶, TOC, note popups)

---

## [2.1.0] - 2025-01-09

### Added
- `<licence>` element in `lexicon.xml` (CC BY-NC-SA 4.0)
- XML download links in footer and about page
- Table and list rendering in research article

### Fixed
- Logeion dictionary links for Greek terms

---

## [2.0.0] - 2025-01

### Added
- **Phase 1 complete**: Core edition infrastructure
  - TEI P5 XML encoding for treatise, lexicon, research article
  - 218 apparatus entries with `<app>/<lem>/<rdg>` structure
  - 223 typed variants (`@type`: orthographic, lexical, morphological, omission, addition)
  - Two witnesses: MS A (Athos A-6), MS S (Tbilisi S-1141)
  
- **Phase 2 complete**: Semantic enrichment
  - `<classDecl>` taxonomy with 12 grammatical categories
  - 35 terms marked with `@ana` + `@corresp` (OLiA URIs)
  - 51 Greek equivalents with Logeion links
  
- **Linked Open Data integration**
  - OLiA ontology alignment for all grammatical terms
  - OntoLex-Lemon RDF export (`lexicon.ttl`)
  - VoID metadata for LLOD registration (`void.ttl`)
  - JSON-LD export for each lexicon entry
  
- **User interface**
  - Lexicon with search, alphabet filter, keyboard navigation
  - Term popups with definitions and LOD badges
  - Witness toggle (A/S) for manuscript reconstruction
  - Copy citation buttons (URN)
  - Research article with collapsible TOC and note popups

- **Persistent identifiers**
  - CTS URN hierarchy: `urn:cts:georgian:shanidze.arthron.ed2025`
  - DOI: [10.5281/zenodo.18283438](https://doi.org/10.5281/zenodo.18283438)
  - LLOD Cloud: [lod-cloud.net/dataset/arthron](https://lod-cloud.net/dataset/arthron)

---

## [1.0.0] - 2024-12

### Added
- Initial project setup
- Basic TEI encoding of treatise text
- Python static site generator with Jinja2
- GitHub Pages deployment

---

## Project Links

- **Live Edition**: https://tamarae.github.io/Arthron/
- **Source Code**: https://github.com/TamarAE/Arthron
- **DOI**: https://doi.org/10.5281/zenodo.18283438
- **LLOD Cloud**: https://lod-cloud.net/dataset/arthron

## Contributors

- **მზექალა შანიძე** — Scholarly Editor
- **ცირა ხახვიაშვილი** — Text Transcription  
- **თამარ კალხიტაშვილი** — Digital Edition (ილიას სახელმწიფო უნივერსიტეტი, ლინგვისტურ კვლევათა ინსტიტუტი)
