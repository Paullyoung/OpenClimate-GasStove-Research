#!/usr/bin/env python3
"""
Research script for OpenClimate Gas Stove Research Repository.
Uses pyalex to search OpenAlex for papers about gas stoves and childhood asthma.
"""

import csv
from pathlib import Path
from pyalex import Works
import pyalex


# Configure pyalex with polite pool (recommended by OpenAlex)
pyalex.config.email = "openclimate-research@example.com"


def search_openalex(query: str, max_results: int = 50) -> list[dict]:
    """
    Search OpenAlex for papers matching the query.
    Filters for Open Access only.
    """
    print(f"Searching OpenAlex for: '{query}'")
    print(f"Filtering for Open Access papers only...")
    
    results = []
    
    # Search with Open Access filter using paginate for iteration
    works_query = (
        Works()
        .search(query)
        .filter(is_oa=True)
    )
    
    # Use paginate to iterate through results
    for page in works_query.paginate(per_page=50, n_max=max_results):
        for work in page:
            if len(results) >= max_results:
                break
            
            # Extract author names
            authors = []
            if work.get("authorships"):
                for authorship in work["authorships"]:
                    if authorship.get("author") and authorship["author"].get("display_name"):
                        authors.append(authorship["author"]["display_name"])
            author_str = "; ".join(authors) if authors else "Unknown"
            
            # Extract year
            year = work.get("publication_year", "")
            
            # Extract DOI
            doi = work.get("doi", "")
            
            # Extract license
            license_info = ""
            if work.get("open_access") and work["open_access"].get("oa_url"):
                # Try to get license from primary location
                if work.get("primary_location") and work["primary_location"].get("license"):
                    license_info = work["primary_location"]["license"]
                elif work.get("best_oa_location") and work["best_oa_location"].get("license"):
                    license_info = work["best_oa_location"]["license"]
            
            # Determine AI_Ready status
            ai_ready = ""
            if license_info and "cc-by" in license_info.lower():
                # Check if it's CC-BY (not CC-BY-NC, CC-BY-ND, etc. - but we'll be generous)
                if license_info.lower() in ["cc-by", "cc-by-4.0", "cc-by-3.0", "cc-by-2.0"]:
                    ai_ready = "Gold Standard"
                elif "cc-by" in license_info.lower():
                    ai_ready = "Gold Standard"  # Include all CC-BY variants as Gold Standard
            
            result = {
                "Title": work.get("title", "Untitled"),
                "Author": author_str,
                "Year": year,
                "DOI": doi,
                "License": license_info,
                "Region": "",  # To be filled manually
                "Stovetype": "",  # To be filled manually
                "Impact_Score": "",  # To be filled manually
                "AI_Ready": ai_ready
            }
            
            results.append(result)
            print(f"  [{len(results)}/{max_results}] {result['Title'][:60]}...")
    
    return results


def save_to_csv(results: list[dict], csv_path: Path) -> None:
    """Save research results to the matrix CSV file."""
    headers = [
        "Title",
        "Author", 
        "Year",
        "DOI",
        "License",
        "Region",
        "Stovetype",
        "Impact_Score",
        "AI_Ready"
    ]
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nSaved {len(results)} papers to: {csv_path}")


def main():
    # Get the repository root
    script_dir = Path(__file__).resolve().parent
    base_path = script_dir.parent
    csv_path = base_path / "metadata" / "matrix.csv"
    
    # Search query
    query = "gas stoves air pollution childhood asthma"
    
    # Search OpenAlex
    results = search_openalex(query, max_results=50)
    
    # Count Gold Standard papers
    gold_count = sum(1 for r in results if r["AI_Ready"] == "Gold Standard")
    
    # Save results
    save_to_csv(results, csv_path)
    
    print(f"\n✓ Research complete!")
    print(f"  Total papers found: {len(results)}")
    print(f"  Gold Standard (CC-BY): {gold_count}")


if __name__ == "__main__":
    main()
