import os
import glob
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_expert_answer(query):
    # 1. Load your Ground Truth files
    md_files = glob.glob("papers/markdown/*.md")
    documents = []
    filenames = []
    
    for file_path in md_files:
        with open(file_path, 'r') as f:
            documents.append(f.read())
            filenames.append(os.path.basename(file_path))

    if not documents:
        return "No markdown files found. Please run the refiner first!"

    # 2. Find the most relevant paper (Semantic Search)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents + [query])
    similarity = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    best_match_idx = similarity.argmax()
    relevant_context = documents[best_match_idx]
    source_paper = filenames[best_match_idx]

    # 3. Ask GitHub Models to answer using ONLY that context
    client = OpenAI(base_url="https://models.inference.ai.azure.com", api_key=os.environ.get("GITHUB_TOKEN"))
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": f"You are the OpenClimate Expert. Use ONLY the provided context from research paper {source_paper} to answer. If the answer isn't there, say you don't know."},
            {"role": "user", "content": f"Context: {relevant_context[:5000]}\n\nQuestion: {query}"}
        ],
        model="gpt-4o"
    )
    
    return response.choices[0].message.content, source_paper

if __name__ == "__main__":
    user_query = input("What would you like to know about gas stoves and health? ")
    answer, source = get_expert_answer(user_query)
    print(f"\n--- EXPERT ANSWER (Source: {source}) ---\n")
    print(answer)
    Add research scripts and markdown files.