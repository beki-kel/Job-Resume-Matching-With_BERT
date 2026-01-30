#!/usr/bin/env python3
"""
Download Resume Dataset Helper Script

This script downloads a working resume dataset from Hugging Face
to use with the fine-tuning notebook.

Usage:
    python3 download_resume_dataset.py
"""

import pandas as pd
from datasets import load_dataset
import re

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'\+?\d[\d\s\-\(\)]{7,}\d', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def download_datasetmaster_resumes():
    """Download from datasetmaster/resumes (4.8k resumes)"""
    print("Downloading datasetmaster/resumes...")
    print("This dataset has 4,800+ real and synthetic resumes\n")
    
    try:
        dataset = load_dataset('datasetmaster/resumes', split='train')
        print(f"✓ Downloaded {len(dataset)} resumes")
        
        resumes = []
        for item in dataset:
            text_parts = []
            
            # Extract personal info
            if 'personal_info' in item and item['personal_info']:
                if 'summary' in item['personal_info']:
                    text_parts.append(str(item['personal_info']['summary']))
            
            # Extract experience
            if 'experience' in item and item['experience']:
                for exp in item['experience']:
                    if isinstance(exp, dict):
                        if 'description' in exp:
                            text_parts.append(str(exp['description']))
                        if 'role' in exp:
                            text_parts.append(str(exp['role']))
            
            # Extract skills
            if 'skills' in item and item['skills']:
                if isinstance(item['skills'], dict):
                    for skill_list in item['skills'].values():
                        if isinstance(skill_list, list):
                            text_parts.extend([str(s) for s in skill_list])
            
            # Extract education
            if 'education' in item and item['education']:
                for edu in item['education']:
                    if isinstance(edu, dict):
                        if 'degree' in edu:
                            text_parts.append(str(edu['degree']))
                        if 'institution' in edu:
                            text_parts.append(str(edu['institution']))
            
            # Extract projects
            if 'projects' in item and item['projects']:
                for proj in item['projects']:
                    if isinstance(proj, dict) and 'description' in proj:
                        text_parts.append(str(proj['description']))
            
            # Combine all parts
            text = ' '.join(p for p in text_parts if p and p != 'None')
            text = clean_text(text)
            
            if len(text) > 200:
                resumes.append({
                    'text': text,
                    'length': len(text)
                })
        
        df = pd.DataFrame(resumes)
        print(f"✓ Extracted {len(df)} quality resumes (>200 chars)")
        
        # Save to CSV
        output_file = 'resumes_dataset.csv'
        df.to_csv(output_file, index=False)
        print(f"✓ Saved to {output_file}")
        
        # Show stats
        print(f"\nDataset Statistics:")
        print(f"  Total resumes: {len(df)}")
        print(f"  Avg length: {df['length'].mean():.0f} chars")
        print(f"  Min length: {df['length'].min()} chars")
        print(f"  Max length: {df['length'].max()} chars")
        
        print(f"\nSample resume:")
        print(df.iloc[0]['text'][:300] + "...")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def download_unknown92_resumes():
    """Download from Unknown92/Resume_dataset"""
    print("\nTrying Unknown92/Resume_dataset...")
    
    try:
        dataset = load_dataset('Unknown92/Resume_dataset', split='train')
        print(f"✓ Downloaded {len(dataset)} resumes")
        
        resumes = []
        for item in dataset:
            # Try different field names
            text = None
            for field in ['Resume', 'resume', 'text', 'Resume_str', 'content']:
                if field in item and item[field]:
                    text = str(item[field])
                    break
            
            if not text:
                text = str(item)
            
            text = clean_text(text)
            if len(text) > 200:
                resumes.append({'text': text, 'length': len(text)})
        
        df = pd.DataFrame(resumes)
        print(f"✓ Extracted {len(df)} quality resumes")
        
        output_file = 'resumes_dataset.csv'
        df.to_csv(output_file, index=False)
        print(f"✓ Saved to {output_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def main():
    print("="*60)
    print("Resume Dataset Downloader")
    print("="*60)
    print()
    
    # Try datasetmaster first (best option)
    success = download_datasetmaster_resumes()
    
    # Try Unknown92 as fallback
    if not success:
        success = download_unknown92_resumes()
    
    if success:
        print("\n" + "="*60)
        print("✓ SUCCESS!")
        print("="*60)
        print("\nYou can now use this dataset in the notebook.")
        print("The notebook will automatically detect 'resumes_dataset.csv'")
    else:
        print("\n" + "="*60)
        print("✗ FAILED")
        print("="*60)
        print("\nCould not download any dataset.")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
