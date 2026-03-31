# Roadmap

## COMPLETED — Curriculum (29 lessons, 5 phases)

### Phase 1: Sanskrit Foundation ✅
### Phase 2: Core Texts ✅ (Vedas, 5 Upanishads, Gita, Yoga Sutras)
### Phase 3: Philosophical Schools ✅ (all 6 Darshanas)
### Phase 4: Epics & Mythology ✅ (Ramayana, Mahabharata, Puranas)
### Phase 5: Living Traditions ✅ (Bhakti, Tantra, Modern thought)
### Society of Thoughts Thread ✅ (12 parallels mapped)

---

## COMPLETED — Architecture Implementation

### Core Engines ✅
- [x] Darshana Router (Buddhi) — 95% routing accuracy
- [x] 6 darshana-specific system prompts — forces method, not labels
- [x] Vritti Filter — 100% classification accuracy, novelty scoring, depth testing, cross-validation
- [x] DarshanaLLM — full LLM pipeline wrapper
- [x] Yaksha Protocol — multi-darshana parallel reasoning + debate
- [x] Ahamkara — self-model (knowledge map, attempt log, vasana tracker)

### Infrastructure Layer ✅
- [x] Smriti — SQLite persistent memory with pramana-aware decay
- [x] Pratyaksha — 5-channel perception (files, web, shell, API, environment)
- [x] Manas — attention/context management with 3 modes
- [x] Shakti — compute management with guna-aware model selection
- [x] Antahkarana — master 9-step pipeline (perceive → remember → assemble → route → budget → reason → filter → learn → respond)

### Harness ✅
- [x] CLI harness — interactive REPL + single-query mode
- [x] HTML report generator — 4 report types
- [x] pip package (pyproject.toml v0.2.0)
- [x] setup.sh + Makefile
- [x] README + QUICKSTART docs

### Integration ✅
- [x] Claude Code plugin — 10 skills, 1 agent, 1 hook
- [x] MCP server — 9 tools, 2 resource types
- [x] Local marketplace registered and plugin installed

### Quality ✅
- [x] 48 tests passing
- [x] 20-query router benchmark (95%)
- [x] 15-sample filter benchmark (100%)

---

## NEXT — What to Build

### Depth Improvements
- [ ] LLM-based Buddhi classifier (replace keyword matching for 95% → 99%)
- [ ] Embedding-based memory retrieval (replace keyword matching in Smriti)
- [ ] Run full Yaksha Protocol on 10 real hard problems, evaluate quality honestly
- [ ] Test with actual Anthropic API calls end-to-end

### Mik Integration
- [ ] Replace Mik's agent routing with Buddhi
- [ ] Add Smriti as Mik's persistent memory
- [ ] Add Vritti Filter to Mik's output pipeline
- [ ] Darshana-aligned agents in Mik's fleet

### Advanced Architecture
- [ ] Multi-round Yaksha debate with actual LLM calls
- [ ] Ahamkara integration into live pipeline (not just standalone)
- [ ] Shakti auto-learning which model tier works best per darshana
- [ ] Cross-session memory building (Smriti across conversations)
- [ ] Vritti Filter as a real-time middleware (not post-hoc)

---

## Key Numbers
- Curriculum: 29 lessons, ~15,000 lines
- Architecture: 16 Python modules, ~14,000 lines of code
- Tests: 48 passing, 95% router accuracy, 100% filter accuracy
- Plugin: 10 skills, 1 agent, 1 hook (installed in Claude Code)
- MCP: 9 tools, 2 resource types
