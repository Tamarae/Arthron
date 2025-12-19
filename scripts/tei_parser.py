"""
TEI XML Parser for სიტყუა ართრონთათჳს Digital Edition

Parses treatise.xml and lexicon.xml into Python data structures
suitable for Jinja2 template rendering.
"""

from lxml import etree
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path

# TEI namespace
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}


@dataclass
class Witness:
    id: str
    settlement: str
    repository: str
    locus: str


@dataclass
class AppEntry:
    id: str
    index: int
    lem: str
    lem_wit: Optional[str]
    readings: List[Dict[str, str]]
    note: Optional[str] = None


@dataclass
class ContentNode:
    """Represents a node in section content (text, app, term, folio, etc.)"""
    type: str  # 'text', 'app', 'term', 'folio', 'greek', 'mentioned'
    value: Optional[str] = None
    # For app nodes
    id: Optional[str] = None
    index: Optional[int] = None
    lem: Optional[str] = None
    rdg_s: Optional[str] = None
    note: Optional[str] = None
    # For term nodes
    target: Optional[str] = None
    text: Optional[str] = None
    # For folio nodes
    ed: Optional[str] = None
    n: Optional[str] = None
    # For mentioned nodes
    ka: Optional[str] = None
    grc: Optional[str] = None


@dataclass
class Section:
    n: str
    xml_id: str
    urn: str
    incipit: str
    content: List[ContentNode]
    folios: List[Dict[str, str]]
    apparatus: List[AppEntry]


@dataclass 
class LexiconEntry:
    id: str
    lemma: str
    pos: Optional[str]
    greek: Optional[str]
    senses: List[Dict[str, str]]
    examples: List[Dict[str, str]]
    occurrences: List[str]
    see_also: List[str]
    note: Optional[str]
    occurrence_count: int = 0


class TEIParser:
    """Parser for the treatise and lexicon TEI files."""
    
    def __init__(self, tei_dir: Path):
        self.tei_dir = Path(tei_dir)
        self.treatise_path = self.tei_dir / 'treatise.xml'
        self.lexicon_path = self.tei_dir / 'lexicon.xml'
        
        self._treatise_tree = None
        self._lexicon_tree = None
        
    def _load_treatise(self):
        if self._treatise_tree is None:
            self._treatise_tree = etree.parse(str(self.treatise_path))
        return self._treatise_tree
    
    def _load_lexicon(self):
        if self._lexicon_tree is None:
            self._lexicon_tree = etree.parse(str(self.lexicon_path))
        return self._lexicon_tree
    
    def get_witnesses(self) -> List[Witness]:
        """Extract witness definitions from teiHeader."""
        tree = self._load_treatise()
        witnesses = []
        
        for wit in tree.xpath('//tei:witness', namespaces=NS):
            wit_id = wit.get('{http://www.w3.org/XML/1998/namespace}id')
            
            settlement = wit.xpath('.//tei:settlement/text()', namespaces=NS)
            settlement = settlement[0] if settlement else ''
            
            repository = wit.xpath('.//tei:repository/text()', namespaces=NS)
            repository = repository[0] if repository else ''
            
            locus = wit.xpath('.//tei:locus/text()', namespaces=NS)
            locus = locus[0] if locus else ''
            
            witnesses.append(Witness(
                id=wit_id,
                settlement=settlement,
                repository=repository,
                locus=locus
            ))
        
        return witnesses
    
    def get_cts_urn(self) -> str:
        """Extract CTS URN from publicationStmt."""
        tree = self._load_treatise()
        urn = tree.xpath('//tei:idno[@type="cts-urn"]/text()', namespaces=NS)
        return urn[0] if urn else 'urn:cts:georgian:shanidze.arthron.ed2025'
    
    def _parse_section_content(self, div_elem, app_counter: int) -> tuple:
        """
        Parse mixed content of a section div into a list of ContentNodes.
        Returns (content_list, apparatus_list, updated_counter).
        """
        content = []
        apparatus = []
        
        def process_element(elem, tail_text=None):
            nonlocal app_counter
            
            # Process the element itself
            tag = etree.QName(elem.tag).localname if isinstance(elem.tag, str) else None
            
            if tag == 'app':
                app_counter += 1
                app_id = elem.get('{http://www.w3.org/XML/1998/namespace}id', f'app.{app_counter}')
                
                # Get lemma
                lem_elem = elem.find('tei:lem', namespaces=NS)
                lem_text = ''.join(lem_elem.itertext()) if lem_elem is not None else ''
                lem_wit = lem_elem.get('wit', '').replace('#', '') if lem_elem is not None else None
                
                # Get readings
                readings = []
                rdg_s_text = None
                for rdg in elem.findall('tei:rdg', namespaces=NS):
                    wit = rdg.get('wit', '').replace('#', '')
                    rdg_text = ''.join(rdg.itertext()).strip()
                    note_elem = rdg.find('tei:note', namespaces=NS)
                    note = note_elem.text if note_elem is not None else None
                    
                    if wit == 'S' and rdg_text:
                        rdg_s_text = rdg_text
                    
                    readings.append({
                        'wit': wit,
                        'text': rdg_text if not note else '',
                        'note': note
                    })
                
                # Add to content
                content.append(ContentNode(
                    type='app',
                    id=app_id,
                    index=app_counter,
                    lem=lem_text,
                    rdg_s=rdg_s_text,
                    note=readings[0].get('note') if readings else None
                ))
                
                # Add to apparatus
                apparatus.append(AppEntry(
                    id=app_id,
                    index=app_counter,
                    lem=lem_text,
                    lem_wit=lem_wit,
                    readings=readings
                ))
                
            elif tag == 'term':
                target = elem.get('target', '').replace('#', '')
                text = ''.join(elem.itertext())
                content.append(ContentNode(
                    type='term',
                    target=target,
                    text=text
                ))
                
            elif tag == 'pb':
                ed = elem.get('ed', '').replace('#', '')
                n = elem.get('n', '')
                content.append(ContentNode(
                    type='folio',
                    ed=ed,
                    n=n
                ))
                
            elif tag == 'milestone' and elem.get('unit') == 'folio':
                ed = elem.get('ed', '').replace('#', '')
                n = elem.get('n', '')
                content.append(ContentNode(
                    type='folio',
                    ed=ed,
                    n=n
                ))
                
            elif tag == 'cb':
                ed = elem.get('ed', '').replace('#', '')
                n = elem.get('n', '')
                # Column breaks can be inline text markers
                content.append(ContentNode(
                    type='folio',
                    ed=ed,
                    n=f'{n}' if n else ''
                ))
                
            elif tag == 'foreign' and elem.get('{http://www.w3.org/XML/1998/namespace}lang') == 'grc':
                text = ''.join(elem.itertext())
                content.append(ContentNode(
                    type='greek',
                    text=text
                ))
                
            elif tag == 'mentioned':
                ka = ''.join(elem.itertext())
                # Look for following gloss with Greek
                next_sib = elem.getnext()
                grc = None
                if next_sib is not None and etree.QName(next_sib.tag).localname == 'gloss':
                    foreign = next_sib.find('tei:foreign', namespaces=NS)
                    if foreign is not None:
                        grc = ''.join(foreign.itertext())
                content.append(ContentNode(
                    type='mentioned',
                    ka=ka,
                    grc=grc
                ))
                
            elif tag == 'gloss':
                # Skip if already processed with mentioned
                pass
                
            elif tag in ('persName', 'q'):
                # Just extract text content
                text = ''.join(elem.itertext())
                content.append(ContentNode(type='text', value=text))
                
            else:
                # Process text content of unknown elements
                if elem.text:
                    content.append(ContentNode(type='text', value=elem.text))
                
                # Process children
                for child in elem:
                    process_element(child)
                    if child.tail:
                        content.append(ContentNode(type='text', value=child.tail))
            
            # Process tail text
            if tail_text:
                content.append(ContentNode(type='text', value=tail_text))
        
        # Process all paragraphs in the section
        for p in div_elem.findall('.//tei:p', namespaces=NS):
            if p.text:
                content.append(ContentNode(type='text', value=p.text))
            
            for child in p:
                process_element(child)
                if child.tail:
                    content.append(ContentNode(type='text', value=child.tail))
        
        return content, apparatus, app_counter
    
    def get_sections(self) -> List[Section]:
        """Extract all sections from the treatise body."""
        tree = self._load_treatise()
        sections = []
        app_counter = 0
        base_urn = self.get_cts_urn()
        
        for div in tree.xpath('//tei:body/tei:div[@type="section"]', namespaces=NS):
            n = div.get('n', '')
            xml_id = div.get('{http://www.w3.org/XML/1998/namespace}id', f'sec.{n}')
            
            # Get folios at start of section
            folios = []
            for pb in div.findall('tei:pb', namespaces=NS):
                folios.append({
                    'ed': pb.get('ed', '').replace('#', ''),
                    'n': pb.get('n', '')
                })
            for ms in div.findall('tei:milestone[@unit="folio"]', namespaces=NS):
                folios.append({
                    'ed': ms.get('ed', '').replace('#', ''),
                    'n': ms.get('n', '')
                })
            
            # Parse content
            content, apparatus, app_counter = self._parse_section_content(div, app_counter)
            
            # Get incipit (first ~50 chars of text)
            text_content = ''.join(
                node.value for node in content 
                if node.type == 'text' and node.value
            )
            incipit = text_content[:50].strip() if text_content else ''
            
            sections.append(Section(
                n=n,
                xml_id=xml_id,
                urn=f'{base_urn}:{n}',
                incipit=incipit,
                content=content,
                folios=folios,
                apparatus=apparatus
            ))
        
        return sections
    
    def get_lexicon_entries(self) -> List[LexiconEntry]:
        """Extract dictionary entries from lexicon.xml."""
        tree = self._load_lexicon()
        entries = []
        
        for entry in tree.xpath('//tei:entry', namespaces=NS):
            entry_id = entry.get('{http://www.w3.org/XML/1998/namespace}id', '')
            
            # Get lemma
            orth = entry.xpath('.//tei:form[@type="lemma"]/tei:orth/text()', namespaces=NS)
            lemma = orth[0] if orth else ''
            
            # Get POS
            pos = entry.xpath('.//tei:pos/text()', namespaces=NS)
            pos = pos[0] if pos else None
            
            # Get Greek equivalent
            greek = entry.xpath('.//tei:etym/tei:mentioned/text()', namespaces=NS)
            if not greek:
                greek = entry.xpath('.//tei:cit[@type="translation"]/tei:quote/text()', namespaces=NS)
            greek = greek[0] if greek else None
            
            # Get senses
            senses = []
            for sense in entry.findall('.//tei:sense', namespaces=NS):
                def_ka = sense.xpath('tei:def[@xml:lang="ka"]/text()', namespaces=NS)
                def_en = sense.xpath('tei:def[@xml:lang="en"]/text()', namespaces=NS)
                senses.append({
                    'def_ka': def_ka[0] if def_ka else '',
                    'def_en': def_en[0] if def_en else ''
                })
            
            # Get examples
            examples = []
            for cit in entry.findall('.//tei:cit[@type="example"]', namespaces=NS):
                quote = cit.xpath('tei:quote/text()', namespaces=NS)
                ref = cit.xpath('tei:bibl/tei:ref/text()', namespaces=NS)
                if quote:
                    examples.append({
                        'quote': quote[0],
                        'ref': ref[0] if ref else ''
                    })
            
            # Get occurrences (section references)
            occurrences = []
            for ref in entry.xpath('.//tei:cit/tei:bibl/tei:ref/@target', namespaces=NS):
                # Extract section number from #sec.N
                if 'sec.' in ref:
                    sec_n = ref.split('sec.')[-1]
                    occurrences.append(sec_n)
            
            # Get see-also references
            see_also = []
            for xr in entry.findall('.//tei:xr', namespaces=NS):
                ref_target = xr.xpath('tei:ref/@target', namespaces=NS)
                if ref_target:
                    see_also.append(ref_target[0].replace('#', ''))
            
            # Get note
            note = entry.xpath('tei:note/text()', namespaces=NS)
            note = note[0] if note else None
            
            entries.append(LexiconEntry(
                id=entry_id.replace('lex.', ''),
                lemma=lemma,
                pos=pos,
                greek=greek,
                senses=senses,
                examples=examples,
                occurrences=occurrences,
                see_also=see_also,
                note=note,
                occurrence_count=len(occurrences)
            ))
        
        # Sort by lemma
        entries.sort(key=lambda e: e.lemma)
        
        return entries
    
    def get_metadata(self) -> Dict[str, Any]:
        """Extract metadata from teiHeader."""
        tree = self._load_treatise()
        
        editor = tree.xpath('//tei:editor[@role="scholarly"]/tei:persName/text()', namespaces=NS)
        
        return {
            'editor': editor[0] if editor else 'აკაკი შანიძე',
            'publication_place': 'თბილისი',
            'publication_year': '1990',
            'source_title': 'ძველი ქართული ენის კათედრის შრომები, 32',
            'cts_urn': self.get_cts_urn(),
            'github_url': 'https://github.com'
        }


# Georgian alphabet for lexicon filtering
GEORGIAN_ALPHABET = list('აბგდევზჱთიკლმნჲოპჟრსტჳუფქღყშჩცძწჭხჴჯჰჵ')


def get_alphabet():
    return GEORGIAN_ALPHABET
