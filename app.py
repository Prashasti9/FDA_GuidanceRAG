import streamlit as st
from src.pipeline import ask

st.set_page_config(page_title="FDA GuidanceRAG", page_icon="📋", layout="centered")

st.title("📋 FDA GuidanceRAG")
st.caption("Ask questions about FDA CMC guidance documents — answers are grounded and cited, or the system will say it doesn't know.")

query = st.text_input("Ask a question:", placeholder="e.g. What documentation is required for CMC postapproval changes?")

if st.button("Ask") and query:
    with st.spinner("Retrieving and generating answer..."):
        answer = ask(query)

    st.markdown("### Answer")
    st.write(answer.text)

    if answer.abstained:
        st.info("The system abstained — it didn't find enough relevant information to answer confidently.")
    else:
        st.markdown("### Sources")
        for i, chunk in enumerate(answer.contexts, 1):
            with st.expander(f"[{i}] {chunk.source} — Page {chunk.page} — {chunk.section}"):
                st.write(chunk.text)
                st.markdown(f"[Open source document]({chunk.url})")

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Retrieve time", f"{answer.latency_ms.get('retrieve', 0):.0f} ms")
        col2.metric("Generate time", f"{answer.latency_ms.get('generate', 0):.0f} ms")
        col3.metric("Tokens used", answer.usage.get('prompt_tokens', 0) + answer.usage.get('completion_tokens', 0))
