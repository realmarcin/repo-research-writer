# Cascading Year Search Strategy for Literature Research

**Purpose**: Prioritize recent work but ensure comprehensive coverage by cascading back to older years when recent work is insufficient.

---

## Search Tiers

### Tier 1: Recent Work (Last 2-3 years: 2024-2026)

**Target**: 15-20 papers
**Query Format**: `[method] 2024`, `[method] 2025`, `[method] 2026`
**Venues**: NeurIPS, ICLR, ICML, Nature, Science, major domain journals

**Decision**:
- ✅ If ≥15 papers found → Proceed to synthesis (Phase 3)
- ⚠️ If <15 papers found → Continue to Tier 2

**Rationale**: Most manuscripts benefit from citing very recent work (last 2-3 years) to demonstrate currency and awareness of state-of-the-art.

---

### Tier 2: Medium Recent (4-6 years back: 2020-2023)

**Target**: Fill gap to reach 15-20 total papers
**Query Format**: `[method] 2020..2023`, `[method] recent advances`
**Focus**: High-impact venues, foundational methodology papers

**Decision**:
- ✅ If total ≥15 papers → Proceed to synthesis
- ⚠️ If <15 papers found → Continue to Tier 3

**Rationale**: Papers from 2020-2023 capture the evolution of methods and major breakthroughs that may not yet be superseded.

---

### Tier 3: Foundational Work (7-10 years back: 2016-2019)

**Target**: Fill remaining gap to reach 15-20 total papers
**Query Format**: `[method] survey`, `[domain] review`, `[method] seminal`
**Focus**: Highly cited (>500 citations), seminal/foundational papers

**Decision**:
- ✅ Proceed to synthesis with papers found
- ⚠️ If <10 papers total across all tiers → Acceptable for niche topics, but document in literature.md

**Rationale**: Foundational papers from 2016-2019 establish core concepts and are often still the primary citations for fundamental techniques.

---

## Stopping Criteria

**Success**: 15-20 papers found across all tiers
**Fallback**: If <15 papers after all tiers, accept what was found (minimum 8-10 papers for niche topics)

**Never compromise on quality**: Better to have 10 highly relevant papers than 20 tangentially related papers.

---

## Application to Search Categories

Apply tier strategy to each search category:

### 1. Foundational Papers (highly cited)
- **Tier 1**: Recent reviews (2024-2026) - e.g., "transformer architectures review 2024"
- **Tier 2**: Medium recent surveys (2020-2023) - e.g., "deep learning survey 2021"
- **Tier 3**: Seminal papers (2016-2019) - e.g., "attention is all you need" (2017)

### 2. Recent Advances
- **Tier 1**: Latest conference papers (NeurIPS 2024/2025, ICLR 2025)
- **Tier 2**: Post-pandemic innovations (2020-2023)
- **Tier 3**: Pre-pandemic breakthroughs (2016-2019)

### 3. Direct Competitors
- **Tier 1**: Recent improvements/extensions of competing methods
- **Tier 2**: Original competing method papers (often 2020-2023)
- **Tier 3**: Foundational work that competing methods build upon

### 4. Application Domain
- **Tier 1**: Recent applications (2024-2026)
- **Tier 2**: Established applications (2020-2023)
- **Tier 3**: Pioneering applications (2016-2019)

---

## Examples

### Example 1: Active Research Area (Transformers for Biology)

**Tier 1 Search**: `transformers protein structure 2024`
- **Found**: 18 papers (NeurIPS 2024, Nature 2024, bioRxiv 2024)
- **Decision**: ✅ Sufficient papers, proceed to synthesis
- **Result**: Literature focused on very recent work

### Example 2: Emerging Area (Agentic AI for Science)

**Tier 1 Search**: `agentic AI scientific discovery 2024`
- **Found**: 8 papers (insufficient)
- **Decision**: ⚠️ Continue to Tier 2

**Tier 2 Search**: `autonomous AI agents science 2020..2023`
- **Found**: 6 more papers (total: 14, still slightly under target)
- **Decision**: ⚠️ Continue to Tier 3 for 1-2 more papers

**Tier 3 Search**: `AI scientific discovery review`
- **Found**: 3 foundational papers (total: 17)
- **Decision**: ✅ Sufficient coverage, proceed to synthesis
- **Result**: Balanced literature covering emergence and foundations

### Example 3: Niche/Specialized Topic (Microbial Cultivation Media Design)

**Tier 1 Search**: `AI microbial growth media 2024`
- **Found**: 3 papers (very insufficient)
- **Decision**: ⚠️ Continue to Tier 2

**Tier 2 Search**: `machine learning cultivation 2020..2023`
- **Found**: 4 more papers (total: 7, still under target)
- **Decision**: ⚠️ Continue to Tier 3

**Tier 3 Search**: `genome-scale metabolic modeling media design 2016..2019`
- **Found**: 5 foundational papers (total: 12)
- **Decision**: ✅ Acceptable for niche topic (12 papers)
- **Result**: Comprehensive coverage of limited literature

### Example 4: Mature Field (Flux Balance Analysis)

**Tier 1 Search**: `flux balance analysis 2024`
- **Found**: 5 papers (recent applications, insufficient)
- **Decision**: ⚠️ Continue to Tier 2

**Tier 2 Search**: `flux balance analysis review 2020..2023`
- **Found**: 7 more papers (total: 12, approaching target)
- **Decision**: ⚠️ Continue to Tier 3 for foundational papers

**Tier 3 Search**: `constraint-based modeling seminal`
- **Found**: 6 highly cited papers (total: 18)
- **Decision**: ✅ Sufficient coverage
- **Result**: Balanced literature with recent applications and foundational theory

---

## Implementation in rrwrite-research-literature Skill

The skill automatically implements this cascading strategy:

1. **Phase 2 (Literature Search)**: Starts with Tier 1 queries
2. **Count Results**: After each tier, counts total papers found
3. **Decision Logic**: If <15 papers, automatically expands to next tier
4. **Synthesis (Phase 3)**: Generates literature.md with balanced coverage across years

**No manual intervention required** - the skill handles tier progression automatically.

---

## Benefits

1. **Recency Bias**: Prioritizes recent work, demonstrating manuscript currency
2. **Fallback Coverage**: Ensures comprehensive coverage even for niche topics
3. **Quality Over Quantity**: Focuses on finding the RIGHT papers, not just ANY papers
4. **Automatic**: No user decisions needed - skill cascades through tiers automatically
5. **Documented Gaps**: If <10 papers found, skill documents this as a research gap

---

## When NOT to Use Cascading Strategy

**Skip cascading and use all years (2016-2026) from start when:**
- Writing a comprehensive review/survey paper
- Documenting historical evolution of a method
- Comparing long-term trends across a decade
- Field has consistent publication rate across all years

**For standard research papers**: Always use cascading strategy to prioritize recency.

---

## Related Documentation

- `rrwrite-research-literature/SKILL.md` - Full skill implementation
- `rationalization-table.md` - Why evidence quality matters
- `citation-rules-by-section.md` - Where to cite recent vs. foundational work
