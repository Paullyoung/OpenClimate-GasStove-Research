#!/usr/bin/env python3
"""
Setup script for OpenClimate Gas Stove Research Repository.
Creates the required folder structure and initializes the research matrix CSV.
"""

import os
import csv
from pathlib import Path


def create_folder_structure(base_path: Path) -> None:
    """Create the required folder structure for the research repository."""
    folders = [
        "papers/raw",
        "papers/markdown",
        "scripts",
        "metadata"
    ]
    
    for folder in folders:
        folder_path = base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {folder_path}")


def create_matrix_csv(base_path: Path) -> None:
    """Create the research matrix CSV file with required headers."""
    headers = [
        "Title",
        "Author",
        "Year",
        "DOI",
        "License",
        "Region",
        "Stovetype",
        "Impact_Score"
    ]
    
    csv_path = base_path / "metadata" / "matrix.csv"
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
    
    print(f"Created matrix CSV: {csv_path}")


def main():
    # Get the repository root (parent of scripts folder)
    script_dir = Path(__file__).resolve().parent
    base_path = script_dir.parent
    
    print(f"Setting up research repository at: {base_path}\n")
    
    # Create folder structure
    create_folder_structure(base_path)
    
    # Create matrix CSV
    create_matrix_csv(base_path)
    
    print("\n✓ Repository setup complete!")


if __name__ == "__main__":
    main()
