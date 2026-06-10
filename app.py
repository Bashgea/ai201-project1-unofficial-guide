"""
Gradio web interface for the syllabus RAG assistant (Milestone 5).
Run with: python app.py
Then open: http://localhost:7860
"""

import gradio as gr
from generate import ask


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="Augsburg Syllabus Assistant") as demo:
    gr.Markdown("## Augsburg University Syllabus Assistant")
    gr.Markdown(
        "Ask a question about any of the 10 course syllabi. "
        "Answers come only from the actual syllabus documents."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. What is the late assignment policy for CSC 311?",
        lines=2,
    )
    btn = gr.Button("Ask", variant="primary")

    answer = gr.Textbox(label="Answer", lines=8, interactive=False)
    sources = gr.Textbox(label="Retrieved from", lines=4, interactive=False)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
