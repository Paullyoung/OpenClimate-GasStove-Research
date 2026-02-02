#!/usr/bin/env python3
"""
PDF Downloader for OpenClimate Gas Stove Research Repository.
Downloads PDFs for Gold Standard (CC-BY) papers from OpenAlex.
"""

import os

import pandas as pd
import requests
from pyalex import Works
import pyalex


# Configure pyalex with polite pool
pyalex.config.email = "openclimate-research@example.com"

# Request headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; OpenClimate-Research/1.0)",
    "Accept": "application/pdf",
}


def get_pdf_url(doi: str) -> str | None:
    """Get the PDF URL from OpenAlex for a given DOI."""
    try:
        work = Works()[doi]
        if not work:
            return None
        
        # Try best_oa_location first
        if work.get("best_oa_location"):
            loc = work["best_oa_location"]
            if loc.get("pdf_url"):
                return loc["pdf_url"]
        
        # Fallback to primary_location
        if work.get("primary_location"):
            loc = work["primary_location"]
            if loc.get("pdf_url"):
                return loc["pdf_url"]
        
        # Fallback to open_access oa_url
        if work.get("open_access"):
            return work["open_access"].get("oa_url")
        
        return None
    except Exception as e:
        print(f"    Error fetching from OpenAlex: {e}")
        return None


def main():
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.dirname(script_dir)
    csv_path = os.path.join(base_path, "metadata", "matrix.csv")
    raw_dir = os.path.join(base_path, "papers", "raw")
    
    # Create papers/raw folder if it doesn't exist
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
        print(f"Created folder: {raw_dir}")
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Filter for Gold Standard papers only
    gold_standard = df[df["AI_Ready"] == "Gold Standard"]
    print(f"Found {len(gold_standard)} Gold Standard papers to download\n")
    
    downloaded = 0
    failed = 0
    
    # Loop through each Gold Standard row
    for index, row in gold_standard.iterrows():
        title = row.get("Title", "Unknown")
        doi = row.get("DOI", "")
        
        print(f"Downloading {title}...")
        
        try:
            if pd.isna(doi) or doi == "":
                print("    Skipped: No DOI available")
                failed += 1
                continue
            
            # Extract DOI identifier (remove https://doi.org/ prefix if present)
            doi_clean = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
            
            # Create filename by replacing / with _
            filename = doi_clean.replace("/", "_") + ".pdf"
            save_path = os.path.join(raw_dir, filename)
            
            # Skip if already downloaded
            if os.path.exists(save_path):
                print(f"    Already exists: {filename}")
                downloaded += 1
                continue
            
            # Get PDF URL from OpenAlex
            pdf_url = get_pdf_url(doi)
            
            if not pdf_url:
                print("    Skipped: No PDF URL found")
                failed += 1
                continue
            
            print(f"    URL: {pdf_url}")
            
            # Download the PDF
            response = requests.get(pdf_url, headers=HEADERS, timeout=60, allow_redirects=True)
            response.raise_for_status()
            
            # Check if we got a PDF
            content_type = response.headers.get("Content-Type", "").lower()
            if ("pdf" in content_type or 
                "octet-stream" in content_type or 
                response.content[:4] == b"%PDF"):
                with open(save_path, "wb") as f:
                    f.write(response.content)
                print(f"    Saved: {filename}")
                downloaded += 1
            else:
                print(f"    Warning: Got {content_type} instead of PDF")
                failed += 1
            
        except requests.exceptions.RequestException as e:
            print(f"    Error: {e}")
            failed += 1
        except Exception as e:
            print(f"    Unexpected error: {e}")
            failed += 1
    
    print(f"\n✓ Download complete!")
    print(f"  Successfully downloaded: {downloaded}")
    print(f"  Failed/Skipped: {failed}")


if __name__ == "__main__":
    main()
