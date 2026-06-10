# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers course syllabi from Augsburg University. Students often need quick answers about things like office hours, grading policies, late submission rules, and quiz schedules, but syllabi are long PDFs that require reading the entire document just to find one specific detail. This system lets a student ask a plain-language question and get a direct answer pulled from the actual syllabus text, without having to open and search through the document manually.

The knowledge is hard to find through official channels because there is no centralized, searchable database of syllabus content at Augsburg. Each syllabus lives as a separate PDF on Moodle, formatted differently depending on the professor. Students often are not sure whether the information they need exists in the document at all, which means they either waste time searching or give up and email the professor.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | 24F 302 Syllabus.pdf | PDF | documents/24F 302 Syllabus.pdf |
| 2 | 25S MAT 315 Syllabus.pdf | PDF | documents/25S MAT 315 Syllabus.pdf |
| 3 | 26S 350 Syllabus corrected.pdf | PDF | documents/26S 350 Syllabus corrected.pdf |
| 4 | CSC 443 Syllabus Fall 2025.docx.pdf | PDF | documents/CSC 443 Syllabus Fall 2025.docx.pdf |
| 5 | CSC373 S26 Syllabus PUBLIC.pdf | PDF | documents/CSC373 S26 Syllabus PUBLIC.pdf |
| 6 | DST 314 Syllabus Fall 2025.docx.pdf | PDF | documents/DST 314 Syllabus Fall 2025.docx.pdf |
| 7 | DST 490 Syllabus.pdf | PDF | documents/DST 490 Syllabus.pdf |
| 8 | SyllabusCSC311.pdf | PDF | documents/SyllabusCSC311.pdf |
| 9 | SyllabusCSC371.pdf | PDF | documents/SyllabusCSC371.pdf |
| 10 | SyllabusCSC391.pdf | PDF | documents/SyllabusCSC391.pdf |

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Why these choices fit your documents:**
A chunk size of 300 characters is large enough to capture a complete syllabus section — such as an office hours block, a grading policy, or a late submission rule — without cramming two different topics into the same chunk. The 50 character overlap acts as a buffer at chunk boundaries so that a sentence that gets cut at the end of one chunk still appears at the beginning of the next, preserving meaning across the boundary.

Recursive chunking was used instead of fixed-size splitting because the syllabi in this project are formatted differently from professor to professor. Some use clear section headings, some use bullet points, and some use dense paragraphs. Recursive splitting tries to cut at double newlines (section breaks) first, then single newlines (paragraph breaks), then spaces, then individual characters as a last resort. This respects the natural structure of each document rather than blindly cutting through headings or mid-sentence.

Before chunking, the text is cleaned using `clean_text()` in `ingest.py`. This removes page numbers, cover-page decoration (such as decorative math sequences on the MAT syllabus covers), navigation blocks like "Jump to a particular section," and ligature characters from LaTeX-generated PDFs that pdfplumber extracts as garbled Unicode symbols.

**Final chunk count:** 776 chunks across 10 documents

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers

This model was chosen because it runs entirely locally with no API key, no rate limits, and no cost. It is fast enough to embed all 776 chunks in under 10 seconds on a standard laptop. Since all 10 syllabi are in English and the queries come from Augsburg students asking in English, a multilingual model is not needed here.

**Production tradeoff reflection:**
If this system were deployed for all students at Augsburg University, three tradeoffs would need to be considered. First, if students speak different languages, switching to a multilingual model like paraphrase-multilingual-MiniLM would allow questions in any language without needing a translation step. Second, if the system got slow under high usage, moving to a cloud-hosted embedding API with load balancing would help distribute requests across servers. Third, if retrieval quality was suffering because the model did not understand academic terminology well enough, upgrading to a larger model like all-mpnet-base-v2 would improve accuracy on domain-specific text, though at the cost of slower inference and higher memory usage.

---

## Grounded Generation

**System prompt grounding instruction:**
The system prompt in `generate.py` enforces grounding through explicit numbered rules, not just a suggestion. The relevant rules are:

1. Answer ONLY using information that appears in the provided context. Do not use any outside knowledge, even if you are confident it is correct.
2. If the context does not contain enough information to answer the question, respond with exactly: "I don't have enough information about that in the provided syllabi."
3. Do not guess, infer, or fill in details that are not stated in the context.

The model temperature is set to 0.0 to prevent the model from introducing any creative additions. The retrieved chunks are numbered and labeled with their source filename inside the user message so the model can see exactly where each piece of information came from.

**How source attribution is surfaced in the response:**
Source attribution is handled programmatically in `generate.py` using the `_dedupe_sources()` function. This function pulls the source filenames directly from the retrieval metadata returned by ChromaDB and deduplicates them in the order they first appeared. The LLM never writes the source list — it is always built from the actual retrieval results. This means citations cannot be hallucinated; they always reflect exactly which documents were retrieved for that query.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What are the office hours for CSC 311? | MW 1:30pm–2:00pm, T 10:30am–11:00am, or by appointment | "I don't have enough information about that in the provided syllabi." | Partially relevant — CSC311 retrieved at rank 2 but the office hours chunk was not in the top 5 | Inaccurate |
| 2 | What happens if you submit a late assignment or project in CSC 311? | Late assignments and late projects receive no credit, but projects must still be submitted | "Late assignments will receive no credit. Late projects will also receive no credit, but they must still be submitted." | Relevant — SyllabusCSC311.pdf rank 1 | Accurate |
| 3 | What is the minimum grade required for CSC 311 to count toward the Computer Science major? | C- or higher | "I don't have enough information about that in the provided syllabi." | Off-target — SyllabusCSC311.pdf not retrieved at all; top 5 were all other syllabi | Inaccurate |
| 4 | What percentage of the DST 490 course grade comes from the Data Visualization Project? | 25% of the overall grade | "I don't have enough information about that in the provided syllabi." | Partially relevant — DST 490 retrieved at rank 1 but the grading breakdown chunk was not in the top 5 | Inaccurate |
| 5 | What is the late homework policy in DST 490? | Work is still due even if you miss class; late homework may be submitted but no feedback will be provided; instructor may limit late submissions | "Late homework may be submitted but no feedback will be provided. Homework is still due on the original due date even if a class is missed." | Relevant — DST 490 Syllabus.pdf rank 1 | Partially accurate — captures main policy but omits the instructor's right to limit late submissions |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**
What is the minimum grade required for CSC 311 to count toward the Computer Science major?

**What the system returned:**
"I don't have enough information about that in the provided syllabi." with sources from CSC 443, CSC 391, CSC 373, DST 490, and Graph Theory — none of which is CSC 311.

**Root cause (tied to a specific pipeline stage):**
The failure happens at the chunking and retrieval stages together. The answer in `SyllabusCSC311.pdf` is split across two consecutive chunks. Chunk 11 ends with: *"Please note that a C- or higher is required for a pass under the pass / no-pass grading option and is"* — the sentence is cut before it mentions the CS major. Chunk 12 starts with: *"required for the course to apply to the Computer Science major or minor."* — this continues the sentence but no longer contains the "C-" phrase.

Because neither chunk alone contains both "C-" and "Computer Science major" in the same piece of text, neither scores high enough in the cosine similarity ranking to beat chunks from other syllabi that have the complete sentence in one chunk. Every Steinmetz syllabus (CSC 311, CSC 371, CSC 391) includes nearly identical "C- or higher for the CS major" language, so those other syllabi's complete chunks crowd out the CSC 311 chunks that were split at the boundary. The 50-character overlap was not large enough to carry the full sentence across the boundary.

**What you would change to fix it:**
Increasing the chunk size from 300 to 500 characters would reduce the chance of a single sentence being split across a boundary, since most policy sentences in these syllabi are well under 500 characters. Alternatively, increasing the overlap from 50 to 100 characters would give the boundary chunks more shared context so that the key phrase "C- or higher" still appears alongside "Computer Science major" in the overlapping portion of the next chunk.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The architecture diagram in planning.md was the most useful part of the spec during implementation. Having the five stages labeled with specific tools — pdfplumber for ingestion, all-MiniLM-L6-v2 for embedding, ChromaDB for the vector store — meant each file had a clear job before a single line of code was written. When prompting Claude to generate each pipeline stage, the diagram made it possible to give a specific input rather than a vague request, which produced usable code on the first attempt instead of requiring repeated corrections.

**One way your implementation diverged from the spec, and why:**
The spec set top-k to 3. During testing, the smoke test against all 5 evaluation questions showed that the correct syllabus for Q1 appeared at rank 2 — it would have been missed entirely with k=3. After seeing the results, top-k was increased to 5 to give the retrieval step more room to surface the right chunk even when a cross-syllabus competitor scores slightly higher. The planning.md was updated to reflect this change.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Chunking Strategy section from planning.md (chunk size 300, overlap 50, recursive approach) and the list of 10 PDF documents.
- *What it produced:* `ingest.py` with `extract_text()`, `clean_text()`, and `chunk_text()` functions. The initial overlap implementation had a bug where the overlap tail was re-joined using the separator, causing the same sentence to appear twice at the start of every chunk after the first.
- *What I changed or overrode:* The overlap logic was rewritten twice. The first fix replaced raw-substring overlap with a list-based approach, which still produced duplicates because the overlap text was being appended as a separate element and then rejoined with the separator. The final fix followed the LangChain-style approach of popping whole pieces from the front of the current chunk until what remains fits within the overlap window, so the overlap is made of real split pieces rather than a raw character slice that collides with the next incoming piece.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from planning.md, the architecture diagram, and the requirement that sources be attributed programmatically rather than by the LLM.
- *What it produced:* `embed.py` with `build_index()` and `retrieve()`, and `generate.py` with a grounded system prompt and `ask()`. The system prompt used numbered rules and temperature 0.0 to enforce grounding, and source attribution was pulled from ChromaDB metadata in `_dedupe_sources()` so the LLM never writes citations.
- *What I changed or overrode:* After running the smoke test, top-k was raised from 3 (as specified in planning.md) to 5 because the correct chunk for Q1 appeared at rank 2 and would have been missed at k=3. The planning.md was updated to document this change and the reasoning behind it.
