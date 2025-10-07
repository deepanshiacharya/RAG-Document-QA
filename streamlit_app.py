import streamlit as st
import requests
from urllib.parse import quote

# Constants
UPLOAD_ENDPOINT = "http://127.0.0.1:8000/upload"
QUERY_ENDPOINT = "http://127.0.0.1:8000/query"

st.title("RAG Document Q&A")

# -----------------------
# 📂 Upload Section
# -----------------------
uploaded_file = st.sidebar.file_uploader("Upload Document", type=["pdf", "docx"])
if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files)
        if response.status_code == 200:
            st.sidebar.success(" File uploaded successfully!")
            st.sidebar.json(response.json())
        else:
            st.sidebar.error(f" Upload failed: {response.text}")
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Request failed: {str(e)}")

# -----------------------
# 💬 Query Section
# -----------------------
st.header("Ask a Question")
question = st.text_input("Enter your question about the document:").strip()

if st.button("Submit"):
    if question:
        try:
            # Encode question safely for URL
            encoded_question = quote(question)
            query_url = f"{QUERY_ENDPOINT}?question={encoded_question}"

            print(f"Debug: Sending request to {query_url}")
            response = requests.post(query_url, timeout=1200)

            print(f"Debug: Response status = {response.status_code}")
            print(f"Debug: Response text = {response.text}")

            if response.status_code == 200:
                result = response.json()
                st.write("### Answer:")
                st.write(result["answer"])
                if result.get("sources"):
                    st.write("### Sources:")
                    for source in result["sources"]:
                        st.write(
                            f"- Document ID: {source['doc_id']}, Filename: {source['filename']}, Chunk ID: {source['chunk_id']}"
                        )
            else:
                st.error(f"Query failed: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
    else:
        st.warning("Please enter a question before submitting.")

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.write("PanScience Innovations - LLM Intern Assignment")
