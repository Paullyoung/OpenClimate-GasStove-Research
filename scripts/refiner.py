import os
from markitdown import MarkItDown
from openai import OpenAI

def refine_papers():
    # 1. Setup folders
    raw_dir = "papers/raw"
    md_dir = "papers/markdown"
    os.makedirs(md_dir, exist_ok=True)

    # 2. Setup GitHub Models Connection
    # Your GITHUB_TOKEN must be in your .env or environment
    token = os.environ.get("GITHUB_TOKEN")
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=token,
    )

    # Initialize the converter
    md = MarkItDown()

    # 3. Process each PDF
    for filename in os.listdir(raw_dir):
        if filename.endswith(".pdf"):
            print(f"Refining: {filename}...")
            raw_path = os.path.join(raw_dir, filename)
            md_path = os.path.join(md_dir, filename.replace(".pdf", ".md"))

            # Step A: Convert PDF to rough Markdown
            result = md.convert(raw_path)
            raw_text = result.text_content

            # Step B: AI-Cleaning (Removing 'Formatting Tax')
            # We use GPT-4o to ensure high fidelity
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a specialized Research Librarian for OpenClimate Intelligence. Clean this text. Remove page numbers, headers, footers, and legal boilerplate. KEEP all tables, data, and scientific conclusions. Preserve the DOI if found."
                    },
                    {
                        "role": "user",
                        "content": f"Here is the raw text: {raw_text[:6000]}" # Sending first 6k chars for efficiency
                    }
                ],
                model="gpt-4o",
            )

            # Step C: Save the Ground Truth
            clean_text = response.choices[0].message.content
            print(f"DEBUG: Received {len(clean_text)} characters from AI.")
            with open(md_path, "w") as f:
                f.write(clean_text)
            print(f"✅ Success: Saved {md_path}")

if __name__ == "__main__":
    refine_papers()