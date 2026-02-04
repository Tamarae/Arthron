# CLAUDE.md - AI Assistant Guide for Arthron Digital Edition

## Project Overview

**Arthron** (*სიტყუაჲ ართრონთათჳს* - "Discourse on Articles") is a Level-4 Digital Scholarly Edition of an anonymous Old Georgian grammatical treatise. The project creates an interactive, web-based critical edition addressing how to translate the Greek definite article (ἄρθρον) into Georgian, a language without articles.

- **Version**: 2.4.0 (January 2025)
- **License**: CC BY-NC-SA 4.0
- **DOI**: 10.5281/zenodo.18283438
- **CTS URN**: urn:cts:georgian:shanidze.arthron.ed2025
- **Live Site**: https://tamarae.github.io/Arthron/

## Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Build the static site
python scripts/build.py

# Build and serve locally (port 8000)
python scripts/build.py --serve

# Preview at http://localhost:8000
```

## Directory Structure

```
Arthron/
├── src/
│   ├── tei/                    # TEI P5 XML source documents
│   │   ├── treatise.xml        # Main text (critical edition)
│   │   ├── lexicon.xml         # Dictionary entries
│   │   └── research.xml        # Research article (stub)
│   └── templates/              # Jinja2 HTML templates
│       ├── base.html           # Base layout with navigation
│       ├── index.html          # Landing page
│       ├── text.html           # Text viewer with apparatus (complex)
│       ├── lexicon.html        # Dictionary interface
│       ├── about.html          # Project information
│       ├── manuscripts.html    # Witness descriptions
│       ├── research.html       # Research article
│       └── sadziebeli.html     # Index/concordance
│
├── scripts/
│   ├── build.py                # Static site generator (408 lines)
│   └── tei_parser.py           # TEI XML parser (438 lines)
│
├── docs/                       # Generated output (GitHub Pages)
│   ├── data/                   # TEI + RDF/JSON-LD exports
│   │   ├── lexicon.ttl         # OntoLex-Lemon RDF
│   │   └── void.ttl            # VoID metadata
│   └── ...
│
├── requirements.txt            # Python dependencies (lxml, Jinja2)
└── CHANGELOG.md                # Version history
```

## Technology Stack

### Backend/Build
- **Python 3.x** - Static site generator
- **lxml** (≥4.9.0) - XML parsing with XPath
- **Jinja2** (≥3.1.0) - Template rendering

### Frontend
- **Tailwind CSS** - Utility-first styling (CDN, no build step)
- **Google Fonts** - Noto Sans/Serif Georgian for Old Georgian text
- **Vanilla JavaScript** - Interactive features (no bundler)

### Data Formats
- **TEI P5 XML** - Standard for digital scholarly editions
- **RDF/TTL** - Semantic web exports (OLiA, OntoLex-Lemon, SKOS)
- **JSON-LD** - Linked data for lexicon entries

## Key Data Structures

### TEI Parser Classes (scripts/tei_parser.py)

```python
@dataclass
class Section:
    n: str                    # Section number
    xml_id: str               # XML identifier
    urn: str                  # CTS URN
    incipit: str              # First 50 chars
    content: List[ContentNode]
    folios: List[Dict]        # Manuscript folio references
    apparatus: List[AppEntry]

@dataclass
class LexiconEntry:
    id: str
    lemma: str                # Headword
    pos: Optional[str]        # Part of speech
    greek: Optional[str]      # Greek equivalent
    senses: List[Dict]        # Definitions (ka, en)
    examples: List[Dict]      # Usage examples
    occurrences: List[str]    # Section references

@dataclass
class ContentNode:
    type: str                 # 'text', 'app', 'term', 'folio', 'greek', 'mentioned'
    # Additional fields vary by type
```

### Route System (scripts/build.py)

```python
ROUTES = {
    'index': ('index.html', 0),           # Depth 0 = root level
    'text': ('text/index.html', 1),       # Depth 1 = subdirectory
    'section': ('text/{n}.html', 1),      # Dynamic routes with params
    'lexicon': ('lexicon/index.html', 1),
    # ...
}
```

The depth system handles relative URL generation across different directory levels.

## Code Conventions

### Python
- **Dataclasses** for all data models
- **Namespace-aware XPath**: Always use `namespaces=NS` where `NS = {'tei': 'http://www.tei-c.org/ns/1.0'}`
- **Lazy loading**: XML trees are cached after first parse
- **Type hints**: Use throughout for clarity

### Templates (Jinja2)
- **Semantic HTML5**: Use `<article>`, `<section>`, `<nav>`, etc.
- **Tailwind classes**: Utility-first, no custom CSS files
- **Depth-aware URLs**: Use `url_for('endpoint', **kwargs)` function
- **Georgian text**: Apply appropriate font classes (`font-georgian`)

### TEI XML
- **Namespace**: Always declare `xmlns="http://www.tei-c.org/ns/1.0"`
- **Apparatus structure**: `<app xml:id="..."><lem wit="#A">...</lem><rdg wit="#S">...</rdg></app>`
- **References**: Use `#` prefix for internal refs (`wit="#A"`, `target="#sec.1"`)

## Build Pipeline

1. **Clean** - Remove and recreate `/build` directory
2. **Copy Assets** - CSS, JS, images, TEI source files
3. **Parse TEI** - Load XML, extract data structures via `TEIParser`
4. **Render Templates** - Generate static HTML for each route
5. **Output** - Write to `/build` (deploy by copying to `/docs`)

## Deployment

The site deploys to GitHub Pages from the `/docs` directory. After building:

```bash
# Copy build output to docs
cp -r build/* docs/

# Commit and push
git add docs/
git commit -m "Build: update static site"
git push
```

## Important Notes for AI Assistants

### Language & Text
- The treatise is in **Old Georgian** (ძველი ქართული) - handle with care
- Greek terms (ἄρθρον, etc.) should preserve proper Unicode characters
- Georgian alphabet order: აბგდევზჱთიკლმნჲოპჟრსტჳუფქღყშჩცძწჭხჴჯჰჵ

### Critical Apparatus
- Two witnesses: **MS A** (Athos A-6) and **MS S** (Tbilisi S-1141)
- Variant types: orthographic, lexical, morphological, omission, addition
- 218+ apparatus entries across ~25 sections

### Content Changes
- **Treatise content**: Edit `src/tei/treatise.xml`
- **Dictionary entries**: Edit `src/tei/lexicon.xml`
- **UI/Layout**: Edit templates in `src/templates/`
- **Build logic**: Edit `scripts/build.py` or `scripts/tei_parser.py`

### Testing Changes
After any changes, run:
```bash
python scripts/build.py --serve
```
Then verify at http://localhost:8000

### Planned Features (from CHANGELOG)
- Variant filter UI (by type)
- Synoptic alignment view (A / S / lemma columns)
- Client-side search with Lunr.js
- `<seg type="rule|example">` markup in treatise

## Common Tasks

### Add a New Lexicon Entry
1. Edit `src/tei/lexicon.xml`
2. Add `<entry>` element with required fields:
   ```xml
   <entry xml:id="lex.newterm">
     <form type="lemma"><orth>ტერმინი</orth></form>
     <gramGrp><pos>noun</pos></gramGrp>
     <sense><def xml:lang="ka">განმარტება</def></sense>
   </entry>
   ```
3. Rebuild the site

### Fix a Text Variant
1. Locate the section in `src/tei/treatise.xml`
2. Find or add the `<app>` element
3. Update `<lem>` and `<rdg>` as needed
4. Rebuild the site

### Modify Page Template
1. Edit the relevant template in `src/templates/`
2. Use `{{ url_for('endpoint') }}` for links
3. Follow Tailwind CSS conventions
4. Rebuild and test

## Project Statistics
- **Sections**: ~25 numbered divisions
- **Lexicon entries**: 179
- **Apparatus entries**: 218
- **Typed variants**: 223
- **Template lines**: ~1,500
- **Python lines**: ~850
