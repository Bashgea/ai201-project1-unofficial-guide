# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Why it's valuable:

Syllabi contain a lot of information and students often need quick answers about class structure. Things like grading, office hours, late policies, and quiz schedules. Instead of reading through an entire document, students can ask a plain-language question and get a direct answer from the actual source.

Why it's hard to find officially:

Syllabi are long PDFs that require students to read through everything just to find one specific answer. Students waste time searching through pages of information, and sometimes what they are looking for isn't even there leaving them unsure whether the information exists at all.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |24F 302 Syllabus.pdf |Discrete Mathematical Structures |documents/24F 302 Syllabus.pdf |
| 2 |25S MAT Syllabus.pdf |Linear Algebra |documents/25S MAT Syllabus.pdf |
| 3 |26S 350 Syllabus corrected.pdf |Gragh Theory |documents/350 Syllabus corrected.pdf |
| 4 |CSC 443 Syllabus Fall 2025.docx.pdf |Software Engineering |documents/CSC 443 Syllabus Fall 2025.docx.pdf |
| 5 |CSC373 S26 Syllabus PUBLIC.pdf |Artificial Intelligence |documents/CSC373 S26 Syllabus PUBLIC.pdf |
| 6 |DST 314 Syllabus FALL 2025.docx.pdf |Programming for Data Science |documents/DST 314 Syllabus FALL 2025.docx.pdf |
| 7 |DST 490 Syllabus.pdf |Data Visualization for Social Justice  |documents/DST 490 Syllabus.pdf |
| 8 |SyllabusCSC311.pdf |Web Applications and Databases  |documents/SyllabusCSC311.pdf |
| 9 |SyllabusCSC371.pdf |Computer Organization  |documents/SyllabusCSC371.pdf |
| 10 |SyllabusCSC391.pdf |Programming Languages |documents/SyllabusCSC391.pdf |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
