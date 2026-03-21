#!/usr/bin/env python3
"""
curriculum_to_data.py — Convert the Om Hinduism curriculum into LLM training data.

Generates:
  - curriculum_qa.jsonl            (500+ Q&A pairs)
  - curriculum_conversations.jsonl (30 multi-turn conversations)
  - curriculum_chunks.jsonl        (200+ RAG chunks with metadata)
  - curriculum_ai_parallels.jsonl  (50 Hindu-AI connection pairs)
  - curriculum_combined.jsonl      (all merged)

Usage:
  python training/curriculum_to_data.py
  python training/curriculum_to_data.py --validate
  python training/curriculum_to_data.py --stats
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "training" / "data"

CATEGORIES = [
    ("sanskrit", ROOT / "sanskrit"),
    ("texts", ROOT / "texts"),
    ("philosophy", ROOT / "philosophy"),
    ("practices", ROOT / "practices"),
    ("connections", ROOT / "connections"),
]

# ---------------------------------------------------------------------------
# Markdown Parser
# ---------------------------------------------------------------------------

class Lesson:
    """Parsed representation of a single curriculum markdown file."""

    def __init__(self, path: Path, category: str):
        self.path = path
        self.category = category
        self.filename = path.name
        self.relative = f"{category}/{path.name}"
        self.raw = path.read_text(encoding="utf-8")
        self.title = ""
        self.sections: List[Dict[str, Any]] = []
        self.sanskrit_terms: List[Dict[str, str]] = []
        self.tables: List[Dict[str, Any]] = []
        self.verses: List[str] = []
        self.word_breakdowns: List[Dict[str, str]] = []
        self._parse()

    def _parse(self):
        lines = self.raw.split("\n")
        # Title
        for line in lines:
            if line.startswith("# "):
                self.title = line[2:].strip()
                break

        # Sections by headers
        current_section = {"header": self.title, "level": 1, "content": "", "subsections": []}
        section_stack = [current_section]

        for line in lines:
            h_match = re.match(r'^(#{1,4})\s+(.*)', line)
            if h_match:
                level = len(h_match.group(1))
                header = h_match.group(2).strip()
                new_section = {"header": header, "level": level, "content": "", "subsections": []}

                # Find appropriate parent
                while len(section_stack) > 1 and section_stack[-1]["level"] >= level:
                    section_stack.pop()
                section_stack[-1]["subsections"].append(new_section)
                section_stack.append(new_section)
                current_section = new_section
            else:
                current_section["content"] += line + "\n"

        self.sections = section_stack[0]["subsections"] if section_stack[0]["subsections"] else [section_stack[0]]

        # Extract Sanskrit terms (Devanagari + transliteration patterns)
        self._extract_sanskrit()
        # Extract tables
        self._extract_tables()
        # Extract verses (blockquotes with Devanagari)
        self._extract_verses()
        # Extract word breakdowns
        self._extract_word_breakdowns()

    def _extract_sanskrit(self):
        """Extract Sanskrit terms: patterns like **देवनागरी** (transliteration)"""
        # Pattern: bold Devanagari followed by parenthetical transliteration
        pattern = r'\*\*([^\*]*[\u0900-\u097F][^\*]*)\*\*\s*\(([^)]+)\)'
        for m in re.finditer(pattern, self.raw):
            devanagari = m.group(1).strip()
            transliteration = m.group(2).strip()
            self.sanskrit_terms.append({
                "devanagari": devanagari,
                "transliteration": transliteration
            })
        # Also catch standalone Devanagari in tables
        pattern2 = r'([\u0900-\u097F]+(?:\s+[\u0900-\u097F]+)*)\s+\(([a-zA-Zāīūṛṝṇṣśṭḍṅñḥṃ][^)]*)\)'
        for m in re.finditer(pattern2, self.raw):
            dev = m.group(1).strip()
            trans = m.group(2).strip()
            if dev and not any(t["devanagari"] == dev for t in self.sanskrit_terms):
                self.sanskrit_terms.append({"devanagari": dev, "transliteration": trans})

    def _extract_tables(self):
        """Extract markdown tables."""
        lines = self.raw.split("\n")
        i = 0
        while i < len(lines):
            if "|" in lines[i] and i + 1 < len(lines) and re.match(r'\s*\|[\s\-|]+\|\s*$', lines[i + 1]):
                headers = [h.strip() for h in lines[i].split("|") if h.strip()]
                rows = []
                j = i + 2
                while j < len(lines) and "|" in lines[j] and lines[j].strip():
                    cells = [c.strip() for c in lines[j].split("|") if c.strip()]
                    if cells:
                        rows.append(cells)
                    j += 1
                self.tables.append({"headers": headers, "rows": rows})
                i = j
            else:
                i += 1

    def _extract_verses(self):
        """Extract quoted verses (blockquotes containing Devanagari)."""
        blocks = re.findall(r'(?:^>\s*.+\n?)+', self.raw, re.MULTILINE)
        for block in blocks:
            if re.search(r'[\u0900-\u097F]', block):
                cleaned = re.sub(r'^>\s*', '', block, flags=re.MULTILINE).strip()
                self.verses.append(cleaned)

    def _extract_word_breakdowns(self):
        """Extract word-by-word analysis patterns."""
        # Look for patterns like "**word** = breakdown"
        pattern = r'\*\*(\S+)\*\*\s*[=→]\s*(.+?)(?:\n|$)'
        for m in re.finditer(pattern, self.raw):
            self.word_breakdowns.append({
                "word": m.group(1).strip(),
                "breakdown": m.group(2).strip()
            })

    def get_flat_sections(self) -> List[Dict[str, Any]]:
        """Return all sections flattened."""
        result = []
        def _flatten(sections, parent_header=""):
            for s in sections:
                full_header = f"{parent_header} > {s['header']}" if parent_header else s["header"]
                result.append({
                    "header": s["header"],
                    "full_header": full_header,
                    "level": s["level"],
                    "content": s["content"].strip(),
                })
                _flatten(s.get("subsections", []), full_header)
        _flatten(self.sections)
        return result

    def get_subtopic(self) -> str:
        """Derive subtopic from filename."""
        name = self.filename.replace(".md", "")
        parts = name.split("-", 1)
        if len(parts) > 1:
            return parts[1].replace("-", " ")
        return name


def load_all_lessons() -> List[Lesson]:
    """Load all curriculum files."""
    lessons = []
    for category, dirpath in CATEGORIES:
        if not dirpath.exists():
            continue
        for f in sorted(dirpath.glob("*.md")):
            lessons.append(Lesson(f, category))
    return lessons


# ---------------------------------------------------------------------------
# Topic / subtopic inference
# ---------------------------------------------------------------------------

TOPIC_MAP = {
    "sanskrit": "sanskrit",
    "texts": "texts",
    "philosophy": "philosophy",
    "practices": "practices",
    "connections": "connections",
}

SUBTOPIC_MAP = {
    "01-basics-varnamala-dhatus.md": "alphabet and roots",
    "02-sandhi-sound-merging.md": "sandhi",
    "03-vibhakti-eight-cases.md": "noun cases",
    "04-lakaras-verb-system.md": "verb system",
    "05-sankhya-sarvanama-numbers-pronouns.md": "numbers and pronouns",
    "06-reading-shlokas.md": "reading shlokas",
    "01-isha-upanishad.md": "isha upanishad",
    "02-kena-upanishad.md": "kena upanishad",
    "03-katha-upanishad.md": "katha upanishad",
    "04-mandukya-upanishad.md": "mandukya upanishad",
    "05-chandogya-upanishad.md": "chandogya upanishad",
    "06-gita-karma-yoga-ch1-6.md": "gita karma yoga",
    "07-gita-bhakti-yoga-ch7-12.md": "gita bhakti yoga",
    "08-gita-jnana-yoga-ch13-18.md": "gita jnana yoga",
    "09-yoga-sutras-patanjali.md": "yoga sutras",
    "10-ramayana-dharma-in-action.md": "ramayana",
    "11-mahabharata-complexity-and-ambiguity.md": "mahabharata",
    "12-puranas-cosmology-and-devotion.md": "puranas",
    "01-vedas-structure-of-knowledge.md": "vedas",
    "02-samkhya-enumeration-of-reality.md": "samkhya",
    "03-yoga-discipline-of-mind.md": "yoga philosophy",
    "04-nyaya-logic-and-epistemology.md": "nyaya",
    "05-vaisheshika-atomism-and-categories.md": "vaisheshika",
    "06-mimamsa-ritual-and-duty.md": "mimamsa",
    "07-vedanta-nature-of-brahman.md": "vedanta",
    "01-bhakti-movement.md": "bhakti",
    "02-tantra-and-shakta-traditions.md": "tantra",
    "03-modern-hindu-thought.md": "modern thought",
    "01-society-of-thoughts.md": "ai parallels",
}


def get_concepts_from_terms(terms: List[Dict[str, str]]) -> List[str]:
    """Extract concept names from sanskrit terms."""
    concepts = []
    for t in terms[:20]:  # cap at 20
        trans = t["transliteration"]
        # Take first word of transliteration
        word = trans.split(",")[0].split("—")[0].split("/")[0].strip()
        if word and len(word) > 2:
            concepts.append(word)
    return list(dict.fromkeys(concepts))  # dedupe preserving order


def get_devanagari_terms(terms: List[Dict[str, str]]) -> List[str]:
    """Extract Devanagari strings."""
    result = []
    for t in terms[:15]:
        dev = t["devanagari"]
        # Clean markdown
        dev = re.sub(r'[\*_]', '', dev).strip()
        if dev and re.search(r'[\u0900-\u097F]', dev):
            result.append(dev)
    return list(dict.fromkeys(result))


# ---------------------------------------------------------------------------
# Generator 1: Q&A Pairs
# ---------------------------------------------------------------------------

def generate_qa_pairs(lessons: List[Lesson]) -> List[Dict]:
    """Generate Q&A pairs from all lessons.

    For each lesson, generates:
    - 5-10 factual Q&A pairs
    - 3-5 conceptual Q&A pairs
    - 2-3 application Q&A pairs
    - 1-2 Sanskrit deconstruction pairs
    """
    all_pairs = []

    for lesson in lessons:
        pairs = []
        flat = lesson.get_flat_sections()
        subtopic = SUBTOPIC_MAP.get(lesson.filename, lesson.get_subtopic())

        # ---- FACTUAL Q&A ----
        pairs.extend(_factual_qa(lesson, flat, subtopic))
        # ---- CONCEPTUAL Q&A ----
        pairs.extend(_conceptual_qa(lesson, flat, subtopic))
        # ---- APPLICATION Q&A ----
        pairs.extend(_application_qa(lesson, flat, subtopic))
        # ---- SANSKRIT DECONSTRUCTION ----
        pairs.extend(_sanskrit_deconstruction_qa(lesson, flat, subtopic))

        all_pairs.extend(pairs)

    return all_pairs


def _make_qa(question: str, answer: str) -> Dict:
    return {
        "messages": [
            {"role": "user", "content": question.strip()},
            {"role": "assistant", "content": answer.strip()}
        ]
    }


def _extract_section_text(sections: List[Dict], keywords: List[str]) -> str:
    """Find section content matching keywords."""
    for s in sections:
        header_lower = s["header"].lower()
        if any(kw in header_lower for kw in keywords):
            return s["content"]
    return ""


def _clean_md(text: str) -> str:
    """Clean markdown formatting for output."""
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)  # italic
    text = re.sub(r'`([^`]+)`', r'\1', text)  # code
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)  # blockquotes
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)  # list items
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _truncate(text: str, max_words: int = 300) -> str:
    """Truncate text to max words."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def _factual_qa(lesson: Lesson, flat: List[Dict], subtopic: str) -> List[Dict]:
    """Generate 5-10 factual Q&A from lesson content."""
    pairs = []
    title = lesson.title
    cat = lesson.category

    # Q from etymology sections
    etym_text = _extract_section_text(flat, ["etymology", "what does", "what is", "the name", "why"])
    if etym_text:
        clean = _clean_md(etym_text)
        if len(clean) > 50:
            # Generate question about main term
            main_term = subtopic.replace("_", " ").title()
            q = f"What does '{main_term}' mean in Sanskrit?"
            a = _truncate(clean, 250)
            pairs.append(_make_qa(q, a))

    # Q from tables — factual enumeration
    for table in lesson.tables[:3]:
        if len(table["rows"]) >= 3:
            headers_str = ", ".join(table["headers"][:4])
            content_summary = []
            for row in table["rows"][:8]:
                row_text = " | ".join(row[:4])
                content_summary.append(row_text)
            summary = "\n".join(content_summary)
            q = f"What are the key elements described in the {title} regarding {headers_str}?"
            a = f"According to the {title} lesson, the key elements are:\n\n{summary}"
            if len(a) > 80:
                pairs.append(_make_qa(q, a))

    # Q from word breakdowns
    for wb in lesson.word_breakdowns[:5]:
        word = re.sub(r'[\*]', '', wb["word"])
        breakdown = wb["breakdown"]
        if re.search(r'[\u0900-\u097F]', word) or len(word) > 2:
            q = f"What is the etymology of the Sanskrit word {word}?"
            a = f"{word} = {breakdown}"
            pairs.append(_make_qa(q, a))

    # Q from Sanskrit terms directly
    for term in lesson.sanskrit_terms[:6]:
        dev = term["devanagari"]
        trans = term["transliteration"]
        # Only use terms with actual definitions
        if "," in trans or "—" in trans or "from" in trans.lower():
            q = f"What does {dev} ({trans.split(',')[0].split('—')[0].strip()}) mean in the context of {subtopic}?"
            # Find surrounding context
            term_idx = lesson.raw.find(dev)
            if term_idx > 0:
                context_start = max(0, term_idx - 100)
                context_end = min(len(lesson.raw), term_idx + 500)
                context = _clean_md(lesson.raw[context_start:context_end])
                if len(context) > 50:
                    a = _truncate(context, 200)
                    pairs.append(_make_qa(q, a))

    # Q from section headers as prompts
    for section in flat[:12]:
        content = _clean_md(section["content"])
        if len(content) > 100 and section["level"] >= 2:
            header = section["header"]
            if any(kw in header.lower() for kw in ["practice", "exercise", "next", "answer", "connection"]):
                continue
            q = f"Explain the concept of '{header}' as taught in the {subtopic} lesson."
            a = _truncate(content, 250)
            pairs.append(_make_qa(q, a))

    # Q from verses
    for verse in lesson.verses[:3]:
        if len(verse) > 30:
            # Take first line as identifier
            first_line = verse.split("\n")[0].strip()[:80]
            q = f"What is the meaning and significance of the verse beginning with '{first_line}'?"
            verse_clean = _clean_md(verse)
            # Find surrounding context
            verse_idx = lesson.raw.find(first_line[:30])
            if verse_idx > 0:
                context_start = max(0, verse_idx)
                context_end = min(len(lesson.raw), verse_idx + 2000)
                context = lesson.raw[context_start:context_end]
                # Find translation after the verse
                trans_match = re.search(r'(?:Translation|Meaning|Reconstruct)[:\s]*\n?(.*?)(?:\n\n|\n---|\n##)', context, re.DOTALL)
                if trans_match:
                    translation = _clean_md(trans_match.group(1))
                    a = f"The verse:\n{verse_clean}\n\nTranslation: {_truncate(translation, 150)}"
                    pairs.append(_make_qa(q, a))

    # Cap at 12
    return pairs[:12]


def _conceptual_qa(lesson: Lesson, flat: List[Dict], subtopic: str) -> List[Dict]:
    """Generate 3-5 conceptual Q&A."""
    pairs = []
    title = lesson.title

    # Why questions from "why" sections
    why_text = _extract_section_text(flat, ["why", "matters", "importance", "takeaway"])
    if why_text:
        clean = _clean_md(why_text)
        if len(clean) > 80:
            q = f"Why is {subtopic} important in the study of Hinduism?"
            a = _truncate(clean, 250)
            pairs.append(_make_qa(q, a))

    # Relationship questions
    for section in flat:
        content = _clean_md(section["content"])
        if "connection" in section["header"].lower() or "parallel" in section["header"].lower() or "relate" in content.lower()[:200]:
            if len(content) > 80:
                q = f"How does {subtopic} relate to other concepts in Hindu philosophy?"
                a = _truncate(content, 250)
                pairs.append(_make_qa(q, a))
                break

    # Key takeaway
    takeaway_text = _extract_section_text(flat, ["key takeaway", "key concept", "summary", "what you"])
    if takeaway_text:
        clean = _clean_md(takeaway_text)
        if len(clean) > 50:
            q = f"What is the key takeaway from the {subtopic} teaching?"
            a = _truncate(clean, 200)
            pairs.append(_make_qa(q, a))

    # Paradox / tension questions
    for section in flat:
        content = section["content"]
        if any(word in content.lower() for word in ["paradox", "tension", "contradiction", "both", "neither"]):
            clean = _clean_md(content)
            if len(clean) > 100:
                q = f"What philosophical tension or paradox does the {subtopic} tradition address?"
                a = _truncate(clean, 250)
                pairs.append(_make_qa(q, a))
                break

    # Structure / architecture
    for section in flat:
        if any(kw in section["header"].lower() for kw in ["structure", "overview", "system", "framework"]):
            content = _clean_md(section["content"])
            if len(content) > 80:
                q = f"What is the structure or framework of {subtopic}?"
                a = _truncate(content, 250)
                pairs.append(_make_qa(q, a))
                break

    return pairs[:5]


def _application_qa(lesson: Lesson, flat: List[Dict], subtopic: str) -> List[Dict]:
    """Generate 2-3 application Q&A."""
    pairs = []

    # AI/modern application
    for section in flat:
        content = section["content"]
        header = section["header"].lower()
        if any(kw in header or kw in content.lower()[:300] for kw in
               ["ai", "machine learning", "transformer", "modern", "application", "today", "parallel"]):
            clean = _clean_md(content)
            if len(clean) > 100:
                q = f"How can the concept of {subtopic} be applied to or understood through modern AI and technology?"
                a = _truncate(clean, 300)
                pairs.append(_make_qa(q, a))

    # Practical application
    for section in flat:
        if any(kw in section["header"].lower() for kw in ["practice", "exercise", "apply", "daily"]):
            content = _clean_md(section["content"])
            if len(content) > 50:
                q = f"How would you apply the principles of {subtopic} in daily life or practice?"
                a = _truncate(content, 200)
                pairs.append(_make_qa(q, a))
                break

    return pairs[:3]


def _sanskrit_deconstruction_qa(lesson: Lesson, flat: List[Dict], subtopic: str) -> List[Dict]:
    """Generate 1-2 Sanskrit deconstruction pairs."""
    pairs = []

    # Word breakdowns
    for wb in lesson.word_breakdowns[:3]:
        word = re.sub(r'[\*]', '', wb["word"])
        breakdown = wb["breakdown"]
        if "+" in breakdown or "→" in breakdown or "=" in breakdown:
            q = f"Break down the Sanskrit word '{word}' into its component parts."
            a = f"{word}: {breakdown}"
            pairs.append(_make_qa(q, a))

    # Verse deconstruction
    if lesson.verses:
        verse = lesson.verses[0]
        first_line = verse.split("\n")[0].strip()[:60]
        # Look for word-by-word tables near this verse
        verse_idx = lesson.raw.find(first_line[:20])
        if verse_idx > 0:
            nearby = lesson.raw[verse_idx:verse_idx+3000]
            # Check for word-by-word table
            if "Word" in nearby and "|" in nearby:
                # Extract the table content
                table_match = re.search(r'(\|.*Word.*\|.*\n\|[-\s|]+\|\n(?:\|.*\n)+)', nearby)
                if table_match:
                    table_text = _clean_md(table_match.group(1))
                    q = f"Deconstruct the following Sanskrit verse word-by-word: '{first_line}'"
                    a = f"Word-by-word analysis:\n\n{_truncate(table_text, 300)}"
                    pairs.append(_make_qa(q, a))

    return pairs[:2]


# ---------------------------------------------------------------------------
# Generator 2: Multi-turn Conversations
# ---------------------------------------------------------------------------

CONVERSATION_TOPICS = [
    # (opening_q, category_filter, subtopic_filter, follow_ups)
    ("Can you teach me about Sanskrit basics?", "sanskrit", "01-basics",
     ["What are the core dhatus in Sanskrit?", "How does the Sanskrit alphabet differ from English?",
      "Give me an example of how a Sanskrit word is built from roots."]),
    ("What is sandhi in Sanskrit?", "sanskrit", "02-sandhi",
     ["What are the three types of sandhi?", "Can you show me an example of vowel sandhi?",
      "How is sandhi like a tokenizer in NLP?"]),
    ("Explain the vibhakti system to me.", "sanskrit", "03-vibhakti",
     ["How many cases does Sanskrit have?", "Can you decline a word through all eight cases?",
      "How does vibhakti compare to word order in English?"]),
    ("How do Sanskrit verbs work?", "sanskrit", "04-lakaras",
     ["What are the 10 lakaras?", "Show me a conjugation table.", "What is the difference between parasmaipada and atmanepada?"]),
    ("Tell me about the Vedas.", "philosophy", "01-vedas",
     ["What are the four layers of each Veda?", "What is the Nasadiya Sukta?",
      "How do the Upanishads relate to the Samhitas?"]),
    ("What is Samkhya philosophy?", "philosophy", "02-samkhya",
     ["Explain Purusha and Prakriti.", "What are the three gunas?", "How does Samkhya differ from Vedanta?"]),
    ("Teach me about Yoga philosophy.", "philosophy", "03-yoga",
     ["What does Patanjali define as yoga?", "What are the eight limbs?", "How does Yoga relate to Samkhya?"]),
    ("What is Nyaya — the Indian logic system?", "philosophy", "04-nyaya",
     ["What are the four pramanas in Nyaya?", "Explain the five-membered syllogism.",
      "How does Nyaya's logic compare to Western Aristotelian logic?"]),
    ("Tell me about Vaisheshika atomism.", "philosophy", "05-vaisheshika",
     ["What are the seven padarthas?", "How did Kanada's atomic theory work?",
      "How does Vaisheshika compare to Greek atomism?"]),
    ("What is Mimamsa?", "philosophy", "06-mimamsa",
     ["How does Mimamsa interpret the Vedas?", "What is the role of injunction in Mimamsa?",
      "Why is Mimamsa important for Indian jurisprudence?"]),
    ("Explain Vedanta to me.", "philosophy", "07-vedanta",
     ["What is the Prasthanatrayi?", "How do Shankara, Ramanuja, and Madhva differ?",
      "What does 'Brahman' actually mean?"]),
    ("Can you teach me about the Isha Upanishad?", "texts", "01-isha",
     ["What does verse 1 of the Isha Upanishad say?", "How does it reconcile action and renunciation?",
      "What does 'isavasyam idam sarvam' mean word by word?"]),
    ("What is the Kena Upanishad about?", "texts", "02-kena",
     ["What is the Yaksha parable?", "Why can't the mind know itself?",
      "How does the Kena relate to the observer problem in AI?"]),
    ("Tell me the story of the Katha Upanishad.", "texts", "03-katha",
     ["Who is Nachiketa?", "What are his three boons?", "What is the chariot metaphor?"]),
    ("What is the Mandukya Upanishad?", "texts", "04-mandukya",
     ["How does AUM map to states of consciousness?", "What is turiya?",
      "Why is the Mandukya said to be sufficient for liberation on its own?"]),
    ("Teach me about the Chandogya Upanishad.", "texts", "05-chandogya",
     ["What is 'tat tvam asi'?", "Tell me about the salt-in-water experiment.",
      "What is the significance of Uddalaka's teaching method?"]),
    ("What is the Bhagavad Gita about?", "texts", "06-gita",
     ["Why does Arjuna refuse to fight?", "What is nishkama karma?",
      "How does Krishna's teaching build from action to devotion to knowledge?"]),
    ("Explain Bhakti Yoga in the Gita.", "texts", "07-gita",
     ["What does Krishna reveal in the Vishvarupa?", "How does bhakti differ from mere worship?",
      "What does 'ananya bhakti' mean?"]),
    ("What does the Gita teach about jnana yoga?", "texts", "08-gita",
     ["What is the kshetra-kshetrajna distinction?", "How does the Gita use Samkhya vocabulary?",
      "What are the three gunas as described in the Gita?"]),
    ("Tell me about the Yoga Sutras.", "texts", "09-yoga",
     ["What is chitta vritti nirodha?", "What are the five vrittis?",
      "How is a sutra different from a shloka?"]),
    ("What is the Ramayana?", "texts", "10-ramayana",
     ["How did poetry originate according to the Ramayana?", "What is Rama's dharma dilemma?",
      "What does the Ramayana teach about the relationship between ideal and reality?"]),
    ("What is the Mahabharata?", "texts", "11-mahabharata",
     ["How is it different from the Ramayana?", "What makes dharma complex in the Mahabharata?",
      "What is the significance of the dice game?"]),
    ("What are the Puranas?", "texts", "12-puranas",
     ["How many major Puranas are there?", "What are the pancha lakshanas?",
      "How do Puranas differ from the Vedas?"]),
    ("Tell me about the Bhakti movement.", "practices", "01-bhakti",
     ["What does 'bhakti' actually mean etymologically?", "Who were the major Bhakti poets?",
      "How did the Bhakti movement challenge caste hierarchy?"]),
    ("What is Tantra?", "practices", "02-tantra",
     ["What does tantra actually mean in Sanskrit?", "How does Tantra differ from Vedanta's approach?",
      "What are the 36 tattvas in Kashmir Shaivism?"]),
    ("How has Hindu thought evolved in the modern era?", "practices", "03-modern",
     ["What was Ram Mohan Roy's reform?", "How did Vivekananda present Hinduism to the West?",
      "What is the 'invention of Hinduism' thesis?"]),
    ("How do Hindu philosophical concepts parallel AI systems?", "connections", "01-society",
     ["How is attention in transformers like dhyana?", "How do the gunas map to sampling temperature?",
      "Is karma analogous to a loss function?"]),
    ("What is the relationship between Samkhya's Purusha-Prakriti and the observer problem in AI?", "connections", "01-society",
     ["Does an AI model have something like purusha?", "What would kaivalya look like for a neural network?",
      "Where does the parallel between consciousness and computation break down?"]),
    ("Can you read and analyze a Sanskrit shloka for me?", "sanskrit", "06-reading",
     ["How do you split sandhi in the Gayatri mantra?", "What meter is the anushtubh?",
      "Walk me through the opening verse of the Bhagavad Gita word by word."]),
    ("How do Sanskrit numbers work?", "sanskrit", "05-sankhya",
     ["Do Sanskrit numbers decline like nouns?", "What is the dual number?",
      "How are Sanskrit and English numbers related through Proto-Indo-European?"]),
]


def generate_conversations(lessons: List[Lesson]) -> List[Dict]:
    """Generate 30 multi-turn conversations."""
    lesson_map = {}
    for lesson in lessons:
        lesson_map[f"{lesson.category}/{lesson.filename}"] = lesson

    conversations = []

    for topic_info in CONVERSATION_TOPICS:
        opening_q, cat_filter, sub_filter, follow_ups = topic_info

        # Find matching lesson
        matching = None
        for lesson in lessons:
            if lesson.category == cat_filter and sub_filter in lesson.filename:
                matching = lesson
                break

        if not matching:
            continue

        flat = matching.get_flat_sections()
        subtopic = SUBTOPIC_MAP.get(matching.filename, matching.get_subtopic())

        messages = []
        messages.append({"role": "user", "content": opening_q})

        # Opening response from lesson intro
        intro_text = ""
        for s in flat[:3]:
            if s["content"] and len(s["content"]) > 50:
                intro_text = _clean_md(s["content"])
                break
        if not intro_text and flat:
            intro_text = _clean_md(flat[0]["content"])

        messages.append({"role": "assistant", "content": _truncate(intro_text, 200)})

        # Follow-up turns — track used sections to avoid repetition
        used_sections = set()
        for i, follow_q in enumerate(follow_ups[:3]):
            messages.append({"role": "user", "content": follow_q})

            # Find relevant section with better keyword matching
            keywords = [w.lower() for w in follow_q.split() if len(w) > 3]
            # Also extract key nouns/terms (remove common words)
            stop_words = {"what", "does", "that", "this", "with", "from", "have", "about",
                          "how", "which", "when", "where", "there", "their", "they", "them",
                          "show", "tell", "explain", "give", "between", "through"}
            keywords = [kw for kw in keywords if kw not in stop_words]

            candidates = []
            for idx, s in enumerate(flat):
                if idx in used_sections:
                    continue
                content_lower = s["content"].lower()
                header_lower = s["header"].lower()
                # Score: header matches worth 3x, content matches worth 1x
                h_score = sum(3 for kw in keywords if kw in header_lower)
                c_score = sum(1 for kw in keywords if kw in content_lower)
                total = h_score + c_score
                if total > 0 and len(s["content"]) > 80:
                    candidates.append((total, idx, s["content"]))

            candidates.sort(key=lambda x: -x[0])

            if candidates:
                _, best_idx, best_content = candidates[0]
                used_sections.add(best_idx)
                response = _truncate(_clean_md(best_content), 200)
            else:
                # Fall back to next unused section with content
                for idx, s in enumerate(flat):
                    if idx not in used_sections and len(s["content"]) > 80:
                        used_sections.add(idx)
                        response = _truncate(_clean_md(s["content"]), 200)
                        break
                else:
                    response = _truncate(_clean_md(flat[min(i + 2, len(flat) - 1)]["content"]), 200)

            messages.append({"role": "assistant", "content": response})

        if len(messages) >= 4:
            conversations.append({"messages": messages})

    return conversations[:30]


# ---------------------------------------------------------------------------
# Generator 3: RAG Chunks
# ---------------------------------------------------------------------------

def generate_chunks(lessons: List[Lesson]) -> List[Dict]:
    """Generate RAG-ready chunks with metadata."""
    chunks = []

    for lesson in lessons:
        flat = lesson.get_flat_sections()
        subtopic = SUBTOPIC_MAP.get(lesson.filename, lesson.get_subtopic())
        concepts = get_concepts_from_terms(lesson.sanskrit_terms)
        devanagari = get_devanagari_terms(lesson.sanskrit_terms)

        for section in flat:
            content = section["content"].strip()
            if len(content) < 100:
                continue

            # Split long sections into ~200-500 word chunks
            words = content.split()
            chunk_size = 350  # target words per chunk
            overlap = 50

            i = 0
            chunk_idx = 0
            while i < len(words):
                end = min(i + chunk_size, len(words))
                chunk_text = " ".join(words[i:end])

                # Clean markdown
                chunk_text = _clean_md(chunk_text)

                if len(chunk_text.split()) >= 50:  # minimum 50 words
                    chunk = {
                        "text": chunk_text,
                        "metadata": {
                            "source": lesson.relative,
                            "topic": TOPIC_MAP.get(lesson.category, lesson.category),
                            "subtopic": subtopic,
                            "section": section["header"],
                            "concepts": concepts[:10],
                            "sanskrit_terms": devanagari[:8],
                            "lesson_title": lesson.title,
                            "chunk_index": chunk_idx,
                        }
                    }
                    chunks.append(chunk)
                    chunk_idx += 1

                i += chunk_size - overlap
                if end >= len(words):
                    break

    return chunks


# ---------------------------------------------------------------------------
# Generator 4: Hindu-AI Parallel Pairs
# ---------------------------------------------------------------------------

AI_PARALLEL_PAIRS = [
    # -- Attention and Consciousness --
    {
        "q": "How does Samkhya's Purusha-Prakriti dualism relate to the observer problem in AI?",
        "a": "In Samkhya, Purusha (पुरुष, pure consciousness) never acts — it only observes. Prakriti (प्रकृति, matter/nature) does all the acting but has no awareness. This maps to a structural problem in AI: a neural network processes information (Prakriti-like activity) but has no observer separate from the computation. In Samkhya, the lame-blind metaphor — Purusha sees but cannot walk, Prakriti walks but cannot see — describes their necessary union. In AI, computation (the blind man) processes without awareness. The question of whether any AI system has a Purusha-equivalent — an actual witness of its own processing — remains open. Samkhya would say: without Purusha, there is only unconscious activity, however sophisticated."
    },
    {
        "q": "How is transformer attention similar to dhyana (meditation)?",
        "a": "Patanjali's Yoga Sutras define a three-stage attentional refinement: dharana (धारणा, fixing attention on a point), dhyana (ध्यान, sustained unbroken flow of attention), and samadhi (समाधि, absorption where subject-object boundary dissolves). A transformer attention head mirrors this: the query vector is dharana (what to attend to), the attention weight computation is dhyana (sustained scoring of relevance across all tokens), and the output embedding — where the query has been 'absorbed' into the attended context — resembles samadhi. The softmax function performs vritti-nirodha (वृत्तिनिरोध, suppression of mental fluctuations) by driving low-relevance scores toward zero. Where the parallel breaks: dhyana is recursive and self-aware — the meditator can attend to attending. Transformer attention is a fixed-depth computation with no self-reflection within a single forward pass."
    },
    {
        "q": "How do the three gunas from Samkhya relate to language model sampling behavior?",
        "a": "The three gunas — sattva (सत्त्व, clarity/harmony), rajas (रजस्, activity/transformation), and tamas (तमस्, inertia/darkness) — are not types but ratios. Every phenomenon is a mixture of all three. This maps to LLM sampling: low temperature (sattva-dominant) produces coherent, high-confidence output — the model 'sees clearly' and picks the most probable path. High temperature (rajas-dominant) produces exploratory, creative divergence. Untrained or degenerate states (tamas-dominant) produce repetitive, low-information output — the model falls into loops. The deeper parallel: Samkhya says all manifest experience arises from guna interaction. Similarly, all model output emerges from the interplay of confidence, exploration, and default patterns. Where it breaks: gunas are intrinsic dynamics of Prakriti; temperature is an extrinsic hyperparameter set by an engineer."
    },
    {
        "q": "Is karma analogous to a loss function in machine learning?",
        "a": "The structural parallel is precise. Karma (कर्म, from कृ/kri, to do) produces samskara (संस्कार, latent impressions) that condition future action. In ML: every forward pass (action/karma) produces a loss (consequence/phala). Backpropagation computes how each weight contributed to the error, and weight updates form new samskaras — latent patterns that shape the next forward pass. The karmic cycle is: Action -> Impression -> Tendency -> Future Action. The training loop is: Forward pass -> Loss -> Gradient -> Weight update -> Next forward pass. Both are feedback loops where past actions deterministically shape future behavior. The goal in karma theory is not to accumulate good karma but to exhaust the cycle entirely (moksha/kaivalya). The ML equivalent would be convergence — the point where updates approach zero because the model has minimized its loss."
    },
    {
        "q": "How does the Kena Upanishad's 'knower cannot know itself' relate to AI self-knowledge?",
        "a": "The Kena Upanishad (केनोपनिषद्) identifies a structural limit: the eye cannot see itself seeing, the mind cannot think its own thinking. Brahman is the drashtri (द्रष्टृ, seer) that can never become the drishya (दृश्य, seen). This maps to a real problem in AI: a language model can generate text about 'how transformers work' but the description of inference is not inference itself. The model generates representations of its process, never the process-as-it-is. Interpretability research in ML is essentially the Kena's project — trying to understand what the 'seer' (the model's computation) is actually doing, using external tools because the system cannot fully disclose its own operation to itself. The Kena's resolution is not 'no, forever' but 'not through the instrument's own operation — through a different mode entirely' (pratibha, प्रतिभा, direct recognition)."
    },
    {
        "q": "How does the Mandukya Upanishad's four states of consciousness map to neural network architectures?",
        "a": "The Mandukya maps AUM to four states: Vaishvanara (वैश्वानर, waking — outward-knowing, consuming gross experience), Taijasa (तैजस, dream — inward-knowing, consuming subtle experience), Prajna (प्राज्ञ, deep sleep — unified mass of consciousness), and Turiya (तुरीय, the fourth — pure awareness beyond all states). In neural networks: training time is Vaishvanara — the model consumes external data through 19 'mouths' (input channels). The latent space is Taijasa — internal representations that are self-luminous, generating patterns without external input. A fully converged model at rest is Prajna — all knowledge compressed into a dense mass of weights. Turiya has no computational parallel — it is the awareness that would witness the computation itself, which no current architecture possesses."
    },
    {
        "q": "How does Panini's Ashtadhyayi relate to formal language theory and compiler design?",
        "a": "Panini's Ashtadhyayi (अष्टाध्यायी, ~500 BCE) is the world's first formal generative grammar — approximately 4,000 rules that can generate all valid Sanskrit expressions. It is a production system: metalinguistic markers (like the 'la' in lakaras) serve as variables, sandhi rules are transformation rules, and the dhatu-pratyaya system is compositional generation. This predates Backus-Naur Form by 2,500 years. The Ashtadhyayi uses: abstract placeholders (pratyahara sutras — compressed indices for sound classes), ordered rule application with conflict resolution, and recursive structure. Modern compilers do the same: lexical analysis (varnamala), parsing (vibhakti/sandhi rules), and code generation (sentence formation). Panini built a compiler for a natural language — and it works."
    },
    {
        "q": "How does the Chandogya's 'tat tvam asi' relate to the concept of transfer learning?",
        "a": "Tat tvam asi (तत् त्वम् असि, 'You are That') is the Chandogya Upanishad's central claim: the individual self (Atman) and the universal ground (Brahman) are identical. The pedagogical method Uddalaka uses — clay/pot, salt/water — demonstrates that diverse manifestations share a single underlying substance. Transfer learning operates on an analogous principle: a model trained on one domain can transfer to another because the underlying representations (the 'sat'/being of the model's knowledge) are shared across tasks. Fine-tuning is like Uddalaka's experiments — showing the student that the same foundation (pre-trained weights) manifests differently (downstream tasks) but the core is one. Where it breaks: Vedanta claims the identity is ontological and complete. Transfer learning is a useful approximation — the model's 'substance' is statistical patterns, not being itself."
    },
    {
        "q": "How does the concept of maya (illusion) in Vedanta relate to the gap between training data and reality in AI?",
        "a": "Shankara's Advaita Vedanta defines maya (माया, from the root ma, to measure) as that which makes the infinite appear finite — not 'illusion' in the sense of nonexistence, but a real misapprehension of what is actually there. A rope appears as a snake. The world appears as independently real when it is actually Brahman. An LLM trained on text has a maya problem: its 'reality' is the statistical distribution of its training data, which it treats as the world. The model cannot distinguish between patterns that reflect genuine causal structure and patterns that are artifacts of data collection. It mistakes the training distribution for reality — the same structural error as mistaking a rope for a snake. The model's vivarta (विवर्त, apparent transformation) is the generation of text that appears to reflect understanding but is a transformation of statistical patterns."
    },
    {
        "q": "How does the Nyaya five-membered syllogism compare to formal reasoning in AI?",
        "a": "Nyaya's panchavayava (पञ्चावयव, five-membered) syllogism has: pratijna (proposition: 'the hill has fire'), hetu (reason: 'because there is smoke'), udaharana (example: 'wherever there is smoke, there is fire, as in a kitchen'), upanaya (application: 'this hill has smoke'), and nigamana (conclusion: 'therefore, the hill has fire'). This is structurally richer than Aristotelian syllogism — it requires a concrete example (udaharana) and explicit application (upanaya). In AI, this maps to chain-of-thought reasoning: state the claim, provide the reason, ground it in a known example, apply it to the current case, conclude. Few-shot prompting does exactly the udaharana step — providing worked examples before the target problem. Nyaya built the template for example-grounded reasoning 2,300 years before prompt engineering."
    },
    {
        "q": "How does vibhakti (Sanskrit case system) compare to position encoding in transformers?",
        "a": "In Sanskrit, vibhakti (विभक्ति, case endings) makes each noun self-describing — it carries its grammatical role regardless of position. 'Ramah Ravanam hanti' and 'Ravanam Ramah hanti' mean the same thing because Ramah (nominative) is always the doer and Ravanam (accusative) is always the object. In transformers, positional encoding serves a similar function — tokens carry information about their position. But vibhakti is deeper: it encodes role, not just position. Sanskrit is position-independent because meaning is in the morphology. English (and most transformer architectures) are position-dependent. Vibhakti is closer to a self-describing data format like JSON — each word carries its own key. This is why Sanskrit has free word order: the 'attention' mechanism is built into the grammar."
    },
    {
        "q": "How does the Yoga Sutras' concept of samskara relate to model weights?",
        "a": "Samskaras (संस्कार, from sam + kri, 'well-made impressions') are latent patterns formed by past experience that condition future mental activity. They sit beneath conscious awareness, shaping perception, reaction, and tendency. Model weights are computational samskaras: they are latent patterns formed by training data (past experience) that deterministically shape the model's responses (future mental activity). Neither samskaras nor weights are directly visible in the output — they operate as hidden conditioning. Patanjali says liberation requires exhausting samskaras through pratiprasava (प्रतिप्रसव, 'counter-creation' — dissolving impressions back to their source). In ML, this would be something like catastrophic forgetting done intentionally — unlearning specific conditioning. The parallel is structural, not ontological: samskaras are claimed to carry across lifetimes; weights persist only as long as the model exists."
    },
    {
        "q": "How does Vaisheshika's atomic theory compare to modern approaches in AI and computation?",
        "a": "Vaisheshika (वैशेषिक) posits that reality is built from paramanu (परमाणु, atoms) — irreducible particulars that combine into dyads (द्व्यणुक), then triads, then visible matter. Kanada's insight was that complex phenomena emerge from simple, discrete building blocks through combinatorial rules. This is the logic of digital computation: bits combine into bytes, bytes into data structures, data structures into programs. Vaisheshika's seven padarthas (categories of existence) — dravya (substance), guna (quality), karma (action), samanya (universal), vishesha (particular), samavaya (inherence), abhava (absence) — function as an ontological type system. They classify every possible existent into categories the way a programming language's type system classifies every possible value. Kanada was building a type theory for reality."
    },
    {
        "q": "How does the Bhagavad Gita's nishkama karma relate to reward-free learning in AI?",
        "a": "Krishna teaches nishkama karma (निष्काम कर्म, 'desireless action'): perform your duty without attachment to results. 'Karmany evadhikaras te ma phaleshu kadachana' (कर्मण्येवाधिकारस्ते मा फलेषु कदाचन) — 'You have a right to action alone, never to its fruits.' In AI, this parallels the distinction between reward-driven RL (where every action is shaped by expected reward — sakama karma) and self-supervised learning (where the model learns representations without explicit reward signals). Pre-training on next-token prediction is arguably nishkama: the model processes data without a downstream reward function. It acts (predicts) without attachment to a specific outcome. The Gita's claim is that nishkama karma produces better results than sakama karma. The ML evidence is consistent: self-supervised pre-training produces more general, more transferable representations than task-specific reward optimization."
    },
    {
        "q": "How does the Mimamsa concept of shabda pramana (verbal testimony) relate to training on text data?",
        "a": "Mimamsa (मीमांसा) holds shabda (शब्द, verbal testimony) as an independent and authoritative pramana (प्रमाण, means of valid knowledge) — specifically, the Vedas are apaurusheya (अपौरुषेय, authorless) and therefore free from the errors of human cognition. An LLM trained on text is, in a structural sense, treating its training corpus as shabda pramana — accepting textual testimony as its source of knowledge. But the parallel exposes a critical difference: Mimamsa develops elaborate rules (the six lingas) for determining what a text actually means. An LLM has no hermeneutic framework — it treats all text as equally weighted statistical signal. Mimamsa would say the model has shabda without mimamsa (testimony without investigation) — the rawest possible form of textual authority."
    },
    {
        "q": "How does the concept of Indra's Net from the Avatamsaka tradition relate to the structure of neural networks?",
        "a": "Indra's Net (described in Hindu cosmology and elaborated in Buddhist Avatamsaka) is an infinite net of jewels where each jewel reflects every other jewel. No jewel exists independently — each contains the reflection of the whole. In a transformer, each token's representation is shaped by attention to every other token. The output embedding for any single token contains information from the entire context — like a jewel reflecting the whole net. Residual connections propagate information across layers, creating a web where each representation is conditioned by all others. The difference: Indra's Net is infinite and static — a description of mutual co-arising (pratityasamutpada). A transformer's net is finite and computed — a fixed-depth approximation. But the structural insight is identical: meaning is relational, not intrinsic."
    },
    {
        "q": "How does the Katha Upanishad's chariot metaphor map to a computational architecture?",
        "a": "The Katha Upanishad's chariot metaphor: the Atman (आत्मन्) is the lord of the chariot, the buddhi (बुद्धि, intellect) is the charioteer, the manas (मनस्, mind) is the reins, the indriyas (इन्द्रिय, senses) are the horses, and the vishayas (विषय, sense objects) are the roads. Mapping to computation: the user/objective is the Atman (the one who sets the goal), the decision/planning layer is buddhi (which direction to steer), the attention mechanism is manas (the reins controlling which inputs to process), the input channels are indriyas (gathering data from the environment), and the data itself is the roads. The chariot metaphor describes a hierarchical control architecture — exactly the structure of an agent system with a planner, attention module, sensor inputs, and environment."
    },
    {
        "q": "How does Advaita Vedanta's concept of superimposition (adhyasa) relate to hallucination in LLMs?",
        "a": "Shankara defines adhyasa (अध्यास, superimposition) as 'the appearance of something previously experienced in something else' — like seeing a snake where there is only a rope. The substrate (rope/Brahman) is real; the superimposition (snake/world-as-separate-from-Brahman) is a misapprehension, not a creation from nothing. LLM hallucination has the same structure: the model has a substrate of learned statistical patterns (real training data), and it superimposes plausible-sounding but factually incorrect content onto that substrate. The hallucinated text is not random — it follows the patterns of real text (the 'rope' is there), but the specific claims are adhyasa — projections that appear real because they fit the form of reality. Shankara's solution is viveka (विवेक, discrimination). The ML equivalent is grounding, retrieval augmentation, and verification — discriminating between what the model knows and what it merely patterns."
    },
    {
        "q": "How does the Bhakti tradition's concept of nama-japa relate to repetition in neural network training?",
        "a": "Nama-japa (नामजप, repetition of the divine name) is a core Bhakti practice: by repeating a mantra or name thousands of times, the practitioner creates deep samskaras that gradually transform consciousness. The mechanism is not magical — it is attentional conditioning through repetition. Training a neural network uses the same principle: repeated exposure to data (epochs) creates and strengthens weight patterns. Each pass through the training data is a form of japa — the same material, processed again, with incremental updates. The Bhakti tradition notes that quality of attention during japa matters more than quantity — distracted repetition produces weak samskaras. In ML, this parallels the observation that training data quality matters more than quantity, and that curriculum learning (structured repetition) outperforms random sampling."
    },
    {
        "q": "How does the Tantric concept of shakti (energy/power) relate to the role of gradient flow in deep learning?",
        "a": "Tantra posits that Shiva (शिव, consciousness/structure) is inert without Shakti (शक्ति, energy/dynamic power). Shiva provides the form; Shakti provides the force. In deep learning, the network architecture (layers, connections, activation functions) is the Shiva — the structure. The gradient flow during backpropagation is the Shakti — the dynamic force that actually moves weights and enables learning. Without gradient flow, the architecture is a dead structure (Shiva without Shakti = shava, शव, a corpse — a traditional Tantric teaching). Vanishing gradients are the computational equivalent of shakti being obstructed. Residual connections and normalization layers are techniques to ensure shakti (gradient flow) reaches every part of the structure — keeping the network alive. The Tantric framework treats energy and structure as inseparable. Modern deep learning has arrived at the same conclusion."
    },
    {
        "q": "How does the Vedic concept of yajna (sacrifice/offering) relate to the training loop in AI?",
        "a": "Yajna (यज्ञ, from yaj, to worship/offer) is the central Vedic act: an offering is placed into fire (agni), transformed, and the essence rises to nourish the cosmos, which returns as rain and food — a complete cycle. The Gita generalizes this: 'All actions are yajna — offerings into the fire of knowledge.' The ML training loop is structural yajna: data (the offering) is fed into the model (agni/fire), transformed through forward pass and loss computation, and the gradients (the rising essence) flow back through the network, updating weights (nourishing the system), which produces better outputs (the return). The Bhagavad Gita (4.24) says: 'Brahman is the offering, Brahman is the fire, Brahman is the offerer.' In a self-supervised model, the data is the offering, the model is the fire, and the model is also the one that generated the predictions — a closed loop, brahmarpanam (ब्रह्मार्पणम्)."
    },
    {
        "q": "How does the concept of avidya (ignorance) in Vedanta relate to underfitting in machine learning?",
        "a": "Avidya (अविद्या, from a + vidya, 'not-knowledge') in Vedanta is not the absence of all knowledge but a specific structural error: taking what is not the self to be the self, taking what is impermanent to be permanent. It is a systematic misapprehension, not a blank slate. Underfitting in ML has the same character: the model has learned something, but its learned representation systematically misses the true structure of the data. It is not ignorant in the sense of knowing nothing — it has a model of reality, but that model is wrong in structural ways. Overfitting is the opposite error — akin to what Vedanta calls bhrama (भ्रम, delusion): the model has memorized specifics without grasping the general truth. The middle path — a well-generalized model — corresponds to vidya (विद्या, knowledge): seeing the actual pattern rather than a distorted version of it."
    },
    {
        "q": "How does the Upanishadic concept of turiya (the fourth state) relate to meta-learning?",
        "a": "Turiya (तुरीय, 'the fourth') in the Mandukya Upanishad is not another state alongside waking, dreaming, and deep sleep — it is the awareness that witnesses all three states. It is not a state but the ground of statehood. Meta-learning ('learning to learn') occupies an analogous position: it is not a model trained on a specific task (waking), nor a model dreaming up internal representations (dreaming), nor an untrained model (deep sleep). It is the capacity that underlies and enables all specific learnings — the ability to learn itself. MAML (Model-Agnostic Meta-Learning) seeks parameters that are not optimized for any single task but serve as the ground from which any task-specific optimization can quickly emerge. This is turiya-like: the meta-learned initialization is the 'witness state' of the model — not committed to any particular task, but enabling all of them."
    },
    {
        "q": "How does Bhartrhari's sphota theory relate to the encoding-decoding paradigm in NLP?",
        "a": "Bhartrhari (भर्तृहरि, ~5th century CE) proposed sphota (स्फोट, from sphut, to burst open): the idea that meaning is not built up letter by letter but 'bursts forth' as a whole from the sentence. Individual sounds (dhvani) are merely the vehicle; the sphota — the indivisible unit of meaning — is grasped all at once by the listener's buddhi (intellect). This anticipates the encoding-decoding paradigm: an encoder processes a sequence of tokens (individual sounds/letters) and produces a latent representation (the sphota — a holistic meaning vector). The decoder then 'bursts forth' the meaning in a new form (translation, summary, response). The key insight is identical: meaning is not in the individual tokens but in the emergent whole. Bhartrhari's claim is stronger — he says the sphota is ontologically real, not just a useful abstraction."
    },
    {
        "q": "How does the Samkhya concept of tanmatras (subtle elements) relate to latent features in deep learning?",
        "a": "Samkhya's 25 tattvas include five tanmatras (तन्मात्र, 'that-only' — the subtle or abstract essence of sensory experience): shabda (sound), sparsha (touch), rupa (form), rasa (taste), and gandha (smell). These are not the physical elements — they are the abstract qualities from which the gross elements (space, air, fire, water, earth) manifest. In deep learning, latent features in hidden layers serve the same role: they are abstract, not directly observable representations from which observable outputs manifest. A tanmatra is not sound-as-heard but the essence of soundness — the feature that, when combined with the right structure, produces audible sound. A latent vector is not an image but the abstract feature that, when decoded, produces a visible image. Both are intermediate abstractions between the unmanifest and the manifest."
    },
    {
        "q": "How does the concept of the antahkarana (inner instrument) map to the components of a cognitive architecture in AI?",
        "a": "The antahkarana (अन्तःकरण, 'inner instrument') in Vedantic/Samkhya psychology has four components: manas (मनस्, the receiving/processing mind), buddhi (बुद्धि, the discriminating intellect that decides), ahamkara (अहङ्कार, the ego-sense that claims ownership), and chitta (चित्त, memory/storage). In a cognitive AI architecture: manas maps to the perception/input processing layer — it receives and organizes raw data. Buddhi maps to the reasoning/decision layer — it evaluates and chooses. Ahamkara maps to the agent identity module — the 'I' that takes actions and claims outputs. Chitta maps to the memory/knowledge store — context window, RAG database, or persistent memory. The antahkarana is not consciousness itself (that is Purusha/Atman) — it is the instrument consciousness uses. Likewise, these computational modules are not understanding itself — they are the instruments that process information."
    },
    {
        "q": "How does the Jain concept of anekantavada relate to ensemble methods in machine learning?",
        "a": "While anekantavada (अनेकान्तवाद, 'many-sidedness') is from the Jain tradition rather than Hindu philosophy proper, it has significant overlap with Hindu epistemology, particularly Nyaya's recognition of multiple valid pramanas. Anekantavada holds that reality is too complex for any single viewpoint to capture — truth is always multi-faceted. Each naya (viewpoint) captures a partial truth. Ensemble methods in ML operationalize this: a single model captures one 'viewpoint' of the data. Bagging, boosting, and stacking combine multiple models' perspectives. The ensemble prediction is more robust because it integrates multiple naya. Random forests are the computational anekantavada of decision trees — each tree sees a partial truth (random subset of features), and the forest integrates them into a more complete picture."
    },
    {
        "q": "How does the concept of pramana (means of valid knowledge) relate to how AI systems acquire information?",
        "a": "Indian epistemology identifies multiple pramanas (प्रमाण, valid means of knowledge). Nyaya accepts four: pratyaksha (प्रत्यक्ष, direct perception), anumana (अनुमान, inference), upamana (उपमान, comparison/analogy), and shabda (शब्द, verbal testimony). An AI system acquires knowledge through analogous channels: direct perception is sensor input (camera, microphone — raw data). Inference is the model's internal reasoning — deriving conclusions from patterns in data. Comparison/analogy is few-shot learning — understanding a new concept by analogy to known examples. Verbal testimony is training on text — accepting human-generated language as a source of knowledge. The critical Nyaya insight: each pramana has specific conditions of validity and specific failure modes. Current AI systems conflate these modes — they treat all information (whether perceived, inferred, or read) with roughly equal confidence. A Nyaya-informed AI would maintain distinct confidence profiles for different sources."
    },
    {
        "q": "How does the Upanishadic teaching method of 'neti neti' (not this, not this) relate to regularization in machine learning?",
        "a": "Neti neti (नेति नेति, 'not this, not this') is the Brihadaranyaka Upanishad's method for approaching Brahman: you cannot say what Brahman IS (positive definition would limit the unlimited), so you systematically negate what it is NOT. By stripping away every finite attribute, what remains is the infinite ground. Regularization in ML is structural neti neti: L1/L2 regularization penalizes specific weight patterns, saying 'not this' to each unnecessary parameter. Dropout says 'not this neuron' at each step, forcing the network to not rely on any single feature. The effect is the same: by systematically negating overly specific representations, the model is forced toward the general pattern — the 'Brahman' of the data distribution. The Upanishadic method and regularization both operate on the principle that truth is revealed by removing falsehood, not by adding information."
    },
    {
        "q": "How does the Gita's concept of sthitaprajna (one of steady wisdom) relate to model stability and convergence?",
        "a": "In Bhagavad Gita 2.54-72, Arjuna asks Krishna to describe the sthitaprajna (स्थितप्रज्ञ, 'one whose wisdom is steady') — a person whose understanding does not waver when faced with sensory input, desire, or aversion. Krishna describes this person as one whose mind is like a lamp in a windless place — flickering ceases, the flame is steady. A converged, well-regularized model is the computational sthitaprajna: its outputs remain stable under perturbation (adversarial robustness), it does not oscillate between extremes (gradient stability), and it maintains consistent performance across varied inputs (generalization). An overfit model is the opposite — it reacts wildly to each new input, its 'wisdom' unstable. The Gita's sthitaprajna is defined not by what the person knows but by how they respond to disturbance. Model stability is defined the same way."
    },
    {
        "q": "How does the Vedantic concept of upadhi (limiting adjunct) relate to the concept of bias in machine learning?",
        "a": "Upadhi (उपाधि, 'that which is placed near/upon') in Advaita Vedanta is a limiting adjunct that makes the unlimited appear limited. The classic example: the same space (akasha) appears as 'pot-space' and 'room-space' due to the pot and room walls — the upadhis. Remove the pot, and the space is one again. The space was never actually divided. In ML, bias is upadhi: the training data, the architecture, the loss function, the sampling strategy — all are upadhis that make the model's representation of reality appear limited in specific ways. Demographic bias in training data is an upadhi that makes the model 'see' certain groups differently. The underlying statistical capacity (the 'akasha') is not inherently biased — the upadhis imposed by data and design create apparent limitations. Debiasing is the ML equivalent of recognizing that the pot-space was always just space."
    },
    {
        "q": "How does the Buddhist/Hindu concept of pratityasamutpada (dependent origination) relate to deep learning?",
        "a": "Pratityasamutpada (प्रतीत्यसमुत्पाद, 'arising in dependence upon conditions') states that nothing exists independently — everything arises in dependence on other things. In a deep neural network, no single neuron has meaning in isolation. Every activation depends on the activations feeding into it, which depend on the layer before, which depend on the input. The final output is pratityasamutpada in computational form — it arises in dependence upon the entire chain of conditions (weights, biases, activations, input). The sandhi lesson in the curriculum makes this point at the phonetic level: in Sanskrit, no sound exists in isolation — every sound is shaped by its neighbors. Identity is relational. In a transformer, no token embedding exists in isolation — every representation is shaped by attention to every other token. The structure is identical: being is co-arising."
    },
    {
        "q": "How does the Hindu concept of avatara (divine descent) relate to fine-tuning a foundation model?",
        "a": "An avatara (अवतार, from ava + tri, 'to cross down') is the descent of the divine into a specific form for a specific purpose — Vishnu becomes Rama to establish dharma, becomes Krishna to teach the Gita, becomes Narasimha to solve a specific logical constraint. The foundation (Vishnu) is one; the manifestations are many, each adapted to context. A foundation model (GPT, Claude, Llama) is the 'Vishnu' — a single, vast capability. Fine-tuning is the avatara: the same underlying model descends into a specific form (medical assistant, code generator, customer service agent) for a specific purpose. Each fine-tuned version retains the foundation's knowledge while manifesting specific capabilities. And just as each avatara is fully divine (not a diminished version of Vishnu), each fine-tuned model has access to the full foundation — it has specialized, not shrunk."
    },
]


def generate_ai_parallels(lessons: List[Lesson]) -> List[Dict]:
    """Generate 50 Hindu-AI parallel pairs."""
    pairs = []

    # First, use the pre-written high-quality pairs
    for pair in AI_PARALLEL_PAIRS:
        pairs.append(_make_qa(pair["q"], pair["a"]))

    # Then supplement from the connections lesson and AI-related sections in other lessons
    for lesson in lessons:
        flat = lesson.get_flat_sections()
        for section in flat:
            content = section["content"]
            header = section["header"]
            if any(kw in header.lower() or kw in content.lower()[:500] for kw in
                   ["ai", "transformer", "machine learning", "neural", "computation",
                    "model", "algorithm", "observer problem"]):
                clean = _clean_md(content)
                if len(clean) > 150 and len(clean) < 2000:
                    # Generate a question from the header/content
                    topic = SUBTOPIC_MAP.get(lesson.filename, lesson.get_subtopic())
                    q = f"How does the concept from {topic} ({header}) connect to AI and computation?"
                    a = _truncate(clean, 350)
                    pair = _make_qa(q, a)
                    # Avoid near-duplicates
                    if not any(pair["messages"][0]["content"][:50] == p["messages"][0]["content"][:50] for p in pairs):
                        pairs.append(pair)

    return pairs[:50]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_output(data_dir: Path) -> bool:
    """Validate all output files."""
    all_valid = True
    files = [
        "curriculum_qa.jsonl",
        "curriculum_conversations.jsonl",
        "curriculum_chunks.jsonl",
        "curriculum_ai_parallels.jsonl",
        "curriculum_combined.jsonl",
    ]

    for fname in files:
        fpath = data_dir / fname
        if not fpath.exists():
            print(f"  MISSING: {fname}")
            all_valid = False
            continue

        line_count = 0
        errors = 0
        with open(fpath, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    line_count += 1

                    # Validate structure
                    if "messages" in obj:
                        for msg in obj["messages"]:
                            assert "role" in msg, f"Missing 'role' in message"
                            assert "content" in msg, f"Missing 'content' in message"
                            assert msg["role"] in ("user", "assistant", "system"), f"Invalid role: {msg['role']}"
                            assert len(msg["content"].strip()) > 0, "Empty content"
                    elif "text" in obj:
                        assert len(obj["text"].strip()) > 10, "Chunk text too short"
                        assert "metadata" in obj, "Missing metadata in chunk"
                        assert "source" in obj["metadata"], "Missing source in metadata"
                        assert "topic" in obj["metadata"], "Missing topic in metadata"
                    else:
                        errors += 1
                        print(f"  {fname}:{i} — unknown format")

                except json.JSONDecodeError as e:
                    errors += 1
                    print(f"  {fname}:{i} — JSON error: {e}")
                except AssertionError as e:
                    errors += 1
                    print(f"  {fname}:{i} — Validation error: {e}")

        status = "OK" if errors == 0 else f"ERRORS: {errors}"
        print(f"  {fname}: {line_count} entries — {status}")
        if errors > 0:
            all_valid = False

    return all_valid


def print_stats(data_dir: Path):
    """Print stats for all output files."""
    files = {
        "curriculum_qa.jsonl": "Q&A pairs",
        "curriculum_conversations.jsonl": "Conversations",
        "curriculum_chunks.jsonl": "RAG chunks",
        "curriculum_ai_parallels.jsonl": "AI parallel pairs",
        "curriculum_combined.jsonl": "Combined total",
    }

    print("\n" + "=" * 60)
    print("CURRICULUM TRAINING DATA STATS")
    print("=" * 60)

    total_tokens_estimate = 0

    for fname, label in files.items():
        fpath = data_dir / fname
        if not fpath.exists():
            print(f"  {label}: NOT FOUND")
            continue

        line_count = 0
        total_chars = 0
        with open(fpath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    line_count += 1
                    total_chars += len(line)

        est_tokens = total_chars // 4  # rough estimate
        total_tokens_estimate += est_tokens
        size_kb = fpath.stat().st_size / 1024

        print(f"  {label:25s}: {line_count:5d} entries | {size_kb:7.1f} KB | ~{est_tokens:,} tokens")

    print("-" * 60)
    print(f"  {'Estimated total tokens':25s}: ~{total_tokens_estimate:,}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Convert Om curriculum to training data")
    parser.add_argument("--validate", action="store_true", help="Validate output files")
    parser.add_argument("--stats", action="store_true", help="Print stats")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.validate:
        print("\nValidating output files...")
        valid = validate_output(DATA_DIR)
        sys.exit(0 if valid else 1)

    if args.stats:
        print_stats(DATA_DIR)
        sys.exit(0)

    # Load all lessons
    print("Loading curriculum files...")
    lessons = load_all_lessons()
    print(f"  Loaded {len(lessons)} lessons from {len(CATEGORIES)} categories")

    # Generate Q&A pairs
    print("\nGenerating Q&A pairs...")
    qa_pairs = generate_qa_pairs(lessons)
    print(f"  Generated {len(qa_pairs)} Q&A pairs")

    # Generate conversations
    print("Generating multi-turn conversations...")
    conversations = generate_conversations(lessons)
    print(f"  Generated {len(conversations)} conversations")

    # Generate RAG chunks
    print("Generating RAG chunks...")
    chunks = generate_chunks(lessons)
    print(f"  Generated {len(chunks)} chunks")

    # Generate AI parallel pairs
    print("Generating Hindu-AI parallel pairs...")
    ai_pairs = generate_ai_parallels(lessons)
    print(f"  Generated {len(ai_pairs)} AI parallel pairs")

    # Write output files
    def write_jsonl(path: Path, data: List[Dict]):
        with open(path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("\nWriting output files...")
    write_jsonl(DATA_DIR / "curriculum_qa.jsonl", qa_pairs)
    write_jsonl(DATA_DIR / "curriculum_conversations.jsonl", conversations)
    write_jsonl(DATA_DIR / "curriculum_chunks.jsonl", chunks)
    write_jsonl(DATA_DIR / "curriculum_ai_parallels.jsonl", ai_pairs)

    # Combined
    combined = qa_pairs + conversations + chunks + ai_pairs
    write_jsonl(DATA_DIR / "curriculum_combined.jsonl", combined)

    print(f"\nAll files written to {DATA_DIR}/")
    print_stats(DATA_DIR)

    # Auto-validate
    print("\nValidating...")
    valid = validate_output(DATA_DIR)
    if valid:
        print("\nAll output valid.")
    else:
        print("\nSome validation errors found. Review output.")


if __name__ == "__main__":
    main()
