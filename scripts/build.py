#!/usr/bin/env python3
"""
Build script for სიტყუა ართრონთათჳს Digital Edition

Parses TEI XML and renders Jinja2 templates to static HTML.

Usage:
    python build.py [--serve]
"""

import argparse
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Add scripts directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from tei_parser import TEIParser, get_alphabet


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / 'src'
TEI_DIR = SRC_DIR / 'tei'
TEMPLATE_DIR = SRC_DIR / 'templates'
ASSETS_DIR = SRC_DIR / 'assets'
BUILD_DIR = PROJECT_ROOT / 'build'


# Route definitions: endpoint -> (path_template, depth)
ROUTES = {
    'index': ('index.html', 0),
    'text': ('text/index.html', 1),
    'text_all': ('text/all.html', 1),
    'section': ('text/{n}.html', 1),
    'lexicon': ('lexicon/index.html', 1),
    'manuscripts': ('manuscripts/index.html', 1),
    'research': ('research/index.html', 1),
    'sadziebeli': ('sadziebeli.html', 0),
    'about': ('about.html', 0),
}


def witnesses_to_dict(witnesses_list):
    """Convert list of Witness objects to dict keyed by id."""
    return {w.id: {'settlement': w.settlement, 'repository': w.repository, 'locus': w.locus} for w in witnesses_list}


def make_url_for(current_depth: int):
    """
    Factory that creates a url_for function for a specific page depth.
    
    Depth 0: pages at root (index.html, about.html)
    Depth 1: pages in subdirectories (text/1.html, lexicon/index.html)
    """
    def url_for(endpoint: str, **kwargs) -> str:
        if endpoint not in ROUTES:
            return 'index.html'
        
        path_template, target_depth = ROUTES[endpoint]
        path = path_template.format(**kwargs) if kwargs else path_template
        
        # Calculate relative prefix
        if current_depth == 0:
            # From root, just use path as-is
            return path
        else:
            # From subdirectory, prepend ../ for each level
            prefix = '../' * current_depth
            return prefix + path
    
    return url_for


def setup_jinja_env() -> Environment:
    """Configure Jinja2 environment."""
    import json
    
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    
    # Add custom filters
    env.filters['truncate'] = lambda s, length: s[:length] + '...' if len(s) > length else s
    env.filters['tojson'] = lambda obj: json.dumps(obj, ensure_ascii=False)
    
    # Note: url_for is added per-render, not globally
    return env


def render_template(env: Environment, template_name: str, depth: int, **context) -> str:
    """Render a template with depth-aware url_for."""
    template = env.get_template(template_name)
    context['url_for'] = make_url_for(depth)
    return template.render(**context)


def clean_build_dir():
    """Remove and recreate build directory."""
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True)
    (BUILD_DIR / 'text').mkdir()
    (BUILD_DIR / 'lexicon').mkdir()
    (BUILD_DIR / 'manuscripts').mkdir()
    (BUILD_DIR / 'research').mkdir()
    (BUILD_DIR / 'tei').mkdir()
    (BUILD_DIR / 'css').mkdir()
    (BUILD_DIR / 'js').mkdir()


def copy_assets():
    """Copy static assets to build directory."""
    if ASSETS_DIR.exists():
        # Copy CSS
        css_src = ASSETS_DIR / 'css'
        if css_src.exists():
            for f in css_src.glob('*'):
                shutil.copy(f, BUILD_DIR / 'css')
        
        # Copy JS
        js_src = ASSETS_DIR / 'js'
        if js_src.exists():
            for f in js_src.glob('*'):
                shutil.copy(f, BUILD_DIR / 'js')
        
        # Copy images
        img_src = ASSETS_DIR / 'img'
        if img_src.exists():
            img_dst = BUILD_DIR / 'img'
            img_dst.mkdir(exist_ok=True)
            for f in img_src.glob('*'):
                shutil.copy(f, img_dst)
    
    # Copy TEI source files
    for f in TEI_DIR.glob('*.xml'):
        shutil.copy(f, BUILD_DIR / 'tei')


def build_index(env: Environment, parser: TEIParser):
    """Build landing page."""
    sections = parser.get_sections()
    entries = parser.get_lexicon_entries()
    
    html = render_template(
        env, 'index.html', depth=0,
        active_page='index',
        section_count=len(sections),
        entry_count=len(entries),
    )
    
    (BUILD_DIR / 'index.html').write_text(html, encoding='utf-8')
    print(f'  Built: index.html')


def lexicon_to_dict(entries_list):
    """Convert list of LexiconEntry objects to dict for JS embedding."""
    return {
        e.id: {
            'lemma': e.lemma,
            'greek': e.greek,
            'pos': e.pos,
            'def': e.senses[0]['def_ka'] if e.senses else '',
            'def_en': e.senses[0].get('def_en', '') if e.senses else '',
        }
        for e in entries_list
    }


def build_text_pages(env: Environment, parser: TEIParser):
    """Build text viewer pages (index, all sections view, individual sections)."""
    sections = parser.get_sections()
    witnesses = witnesses_to_dict(parser.get_witnesses())
    lexicon = lexicon_to_dict(parser.get_lexicon_entries())
    
    # Build main text page (shows first section)
    if sections:
        first_section = sections[0]
        html = render_template(
            env, 'text.html', depth=1,
            active_page='text',
            sections=sections,
            displayed_sections=[first_section],
            apparatus=first_section.apparatus,
            current_section=first_section.n,
            section_count=len(sections),
            prev_section=None,
            next_section=sections[1].n if len(sections) > 1 else None,
            show_all_link=True,
            witnesses=witnesses,
            lexicon=lexicon,
        )
        (BUILD_DIR / 'text' / 'index.html').write_text(html, encoding='utf-8')
        print(f'  Built: text/index.html')
    
    # Build "all sections" page
    all_apparatus = []
    for sec in sections:
        all_apparatus.extend(sec.apparatus)
    
    html = render_template(
        env, 'text.html', depth=1,
        active_page='text',
        sections=sections,
        displayed_sections=sections,
        apparatus=all_apparatus,
        current_section='all',
        section_count=len(sections),
        prev_section=None,
        next_section=None,
        show_all=True,
        witnesses=witnesses,
        lexicon=lexicon,
    )
    (BUILD_DIR / 'text' / 'all.html').write_text(html, encoding='utf-8')
    print(f'  Built: text/all.html')
    
    # Build individual section pages
    for i, section in enumerate(sections):
        prev_n = sections[i-1].n if i > 0 else None
        next_n = sections[i+1].n if i < len(sections) - 1 else None
        
        html = render_template(
            env, 'text.html', depth=1,
            active_page='text',
            sections=sections,
            displayed_sections=[section],
            apparatus=section.apparatus,
            current_section=section.n,
            section_count=len(sections),
            prev_section=prev_n,
            next_section=next_n,
            show_all_link=True,
            witnesses=witnesses,
            lexicon=lexicon,
        )
        (BUILD_DIR / 'text' / f'{section.n}.html').write_text(html, encoding='utf-8')
        print(f'  Built: text/{section.n}.html')


def build_lexicon(env: Environment, parser: TEIParser):
    """Build lexicon page."""
    entries = parser.get_lexicon_entries()
    alphabet = get_alphabet()
    
    html = render_template(
        env, 'lexicon.html', depth=1,
        active_page='lexicon',
        entries=entries,
        alphabet=alphabet,
        active_letter=alphabet[0] if alphabet else 'ა',
    )
    
    (BUILD_DIR / 'lexicon' / 'index.html').write_text(html, encoding='utf-8')
    print(f'  Built: lexicon/index.html')


def build_sadziebeli(env: Environment, parser: TEIParser):
    """Build index/concordance page."""
    # TODO: Extract index data from treatise automatically
    # For now, use placeholder data
    ka_grc_index = [
        {'ka': 'ა', 'grc': 'ὁ', 'refs': ['3', '5', '6']},
        {'ka': 'ტუ', 'grc': 'τοῦ', 'refs': ['3', '5', '7']},
        {'ka': 'ტა', 'grc': 'τῷ', 'refs': ['3', '5', '7', '11']},
        {'ka': 'თეას', 'grc': 'θεός', 'refs': ['4', '6', '22']},
        {'ka': 'ტრიას', 'grc': 'τριάς', 'refs': ['13']},
        {'ka': 'პნევმა', 'grc': 'πνεῦμა', 'refs': ['17', '18']},
    ]
    
    ka_index = {
        'ა': [
            {'term': 'აევილაგით-ი', 'contexts': 'აევილაგითად იჴუმევედენ 4; ა. ... აჴსენებედენ 6'},
            {'term': 'ართრონ-ი', 'contexts': 'თითადულისა ნათესავისანი არიან ათცამეტ 3; ართრონსა დაუდებს...'},
        ],
    }
    
    html = render_template(
        env, 'sadziebeli.html', depth=0,
        active_page='sadziebeli',
        ka_grc_index=ka_grc_index,
        ka_index=ka_index,
    )
    
    (BUILD_DIR / 'sadziebeli.html').write_text(html, encoding='utf-8')
    print(f'  Built: sadziebeli.html')


def build_about(env: Environment, parser: TEIParser):
    """Build about page."""
    witnesses = parser.get_witnesses()
    metadata = parser.get_metadata()
    
    html = render_template(
        env, 'about.html', depth=0,
        active_page='about',
        witnesses=witnesses,
        **metadata,
    )
    
    (BUILD_DIR / 'about.html').write_text(html, encoding='utf-8')
    print(f'  Built: about.html')


def build_manuscripts(env: Environment, parser: TEIParser):
    """Build manuscripts description page."""
    witnesses = parser.get_witnesses()
    
    html = render_template(
        env, 'manuscripts.html', depth=1,
        active_page='manuscripts',
        witnesses=witnesses,
    )
    
    (BUILD_DIR / 'manuscripts' / 'index.html').write_text(html, encoding='utf-8')
    print(f'  Built: manuscripts/index.html')


def build_research(env: Environment, parser: TEIParser):
    """Build research article page."""
    # TODO: Parse research.xml when available
    html = render_template(
        env, 'research.html', depth=1,
        active_page='research',
        article_title='სიტყუა ართრონთათვს: კვლევა',
        sections=[],  # Will be populated from research.xml
    )
    
    (BUILD_DIR / 'research' / 'index.html').write_text(html, encoding='utf-8')
    print(f'  Built: research/index.html')


def build_all():
    """Build entire site."""
    print('Building სიტყუა ართრონთათვს Digital Edition...')
    print()
    
    # Setup
    print('1. Setting up build directory...')
    clean_build_dir()
    copy_assets()
    
    # Initialize parser and Jinja
    print('2. Loading TEI data...')
    parser = TEIParser(TEI_DIR)
    env = setup_jinja_env()
    
    # Build pages
    print('3. Building pages...')
    build_index(env, parser)
    build_text_pages(env, parser)
    build_lexicon(env, parser)
    build_manuscripts(env, parser)
    build_research(env, parser)
    build_sadziebeli(env, parser)
    build_about(env, parser)
    
    print()
    print(f'Build complete! Output in: {BUILD_DIR}')
    print()
    print('To preview locally:')
    print(f'  cd {BUILD_DIR}')
    print('  python -m http.server 8000')
    print('  Open: http://localhost:8000')


def serve():
    """Serve the built site locally."""
    import http.server
    import socketserver
    
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    import os
    os.chdir(BUILD_DIR)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f'Serving at http://localhost:{PORT}')
        print('Press Ctrl+C to stop')
        httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(
        description='Build the digital edition static site'
    )
    parser.add_argument(
        '--serve', 
        action='store_true',
        help='Start local server after build'
    )
    
    args = parser.parse_args()
    
    build_all()
    
    if args.serve:
        serve()


if __name__ == '__main__':
    main()