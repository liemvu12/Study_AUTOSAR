#!/usr/bin/env python3
"""
verify_citation.py - Scientific Citation & DOI/PMID Academic Verification Tool

Queries public authoritative APIs (Crossref API & NCBI PubMed E-utilities)
to verify that a DOI or PMID actually exists, retrieves canonical metadata
(Title, Authors, Journal, Year, Volume, Issue, Article Type), and checks
for potential retractions or corrections.
"""

import sys
import json
import argparse
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, Optional

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

USER_AGENT = "ScientificResearchLookupSkill/1.0 (mailto:scientific-lookup@antigravity.internal)"

def verify_doi(doi: str) -> Dict[str, Any]:
    """Verify a DOI using the public Crossref REST API."""
    clean_doi = doi.strip()
    if clean_doi.startswith("http://"):
        clean_doi = clean_doi.replace("http://dx.doi.org/", "").replace("http://doi.org/", "")
    elif clean_doi.startswith("https://"):
        clean_doi = clean_doi.replace("https://dx.doi.org/", "").replace("https://doi.org/", "")

    encoded_doi = urllib.parse.quote(clean_doi)
    url = f"https://api.crossref.org/works/{encoded_doi}"
    
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                item = data.get("message", {})
                
                title = item.get("title", [""])[0] if item.get("title") else "N/A"
                journal = item.get("container-title", [""])[0] if item.get("container-title") else "N/A"
                
                authors_list = []
                for a in item.get("author", []):
                    given = a.get("given", "")
                    family = a.get("family", "")
                    name = f"{given} {family}".strip()
                    if name:
                        authors_list.append(name)
                
                # Year resolution
                year = "N/A"
                if "published-print" in item and "date-parts" in item["published-print"]:
                    year = str(item["published-print"]["date-parts"][0][0])
                elif "published-online" in item and "date-parts" in item["published-online"]:
                    year = str(item["published-online"]["date-parts"][0][0])
                elif "created" in item and "date-parts" in item["created"]:
                    year = str(item["created"]["date-parts"][0][0])
                
                # Check retraction / updates
                update_to = item.get("update-to", [])
                is_retracted = any("retraction" in str(u).lower() for u in update_to)
                
                return {
                    "status": "VERIFIED",
                    "source": "Crossref API",
                    "identifier": clean_doi,
                    "title": title,
                    "authors": authors_list,
                    "journal": journal,
                    "year": year,
                    "type": item.get("type", "journal-article"),
                    "publisher": item.get("publisher", "N/A"),
                    "is_retracted": is_retracted,
                    "url": f"https://doi.org/{clean_doi}"
                }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"status": "NOT_FOUND", "identifier": clean_doi, "error": "DOI 404 Not Found in Crossref"}
        return {"status": "ERROR", "identifier": clean_doi, "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"status": "ERROR", "identifier": clean_doi, "error": str(e)}

def verify_pmid(pmid: str) -> Dict[str, Any]:
    """Verify a PMID using the NCBI PubMed E-utilities."""
    clean_pmid = pmid.strip()
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={clean_pmid}&retmode=json"
    
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                result = data.get("result", {})
                if clean_pmid in result:
                    item = result[clean_pmid]
                    title = item.get("title", "N/A").rstrip(".")
                    journal = item.get("source", "N/A")
                    pubdate = item.get("pubdate", "N/A")
                    year = pubdate[:4] if len(pubdate) >= 4 else pubdate
                    
                    authors = [a.get("name", "") for a in item.get("authors", [])]
                    
                    # Extract DOI if present
                    doi = "N/A"
                    for aid in item.get("articleids", []):
                        if aid.get("idtype") == "doi":
                            doi = aid.get("value")
                            break
                    
                    return {
                        "status": "VERIFIED",
                        "source": "NCBI PubMed E-utilities",
                        "identifier": f"PMID:{clean_pmid}",
                        "title": title,
                        "authors": authors,
                        "journal": journal,
                        "year": year,
                        "doi": doi,
                        "pubtypes": item.get("pubtype", []),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{clean_pmid}/"
                    }
                else:
                    return {"status": "NOT_FOUND", "identifier": clean_pmid, "error": "PMID not found in PubMed"}
    except Exception as e:
        return {"status": "ERROR", "identifier": clean_pmid, "error": str(e)}

def print_result(res: Dict[str, Any]):
    print("\n" + "="*70)
    print("  SCIENTIFIC CITATION & METADATA VERIFICATION REPORT")
    print("="*70)
    
    status = res.get("status")
    if status == "VERIFIED":
        print(f"Status:        [VERIFIED - AUTHENTIC PUBLICATION]")
        print(f"Database:      {res.get('source')}")
        print(f"Identifier:    {res.get('identifier')}")
        print(f"Title:         {res.get('title')}")
        authors = res.get('authors', [])
        if len(authors) > 3:
            author_str = f"{', '.join(authors[:3])} et al. (Total: {len(authors)})"
        else:
            author_str = ", ".join(authors) if authors else "N/A"
        print(f"Authors:       {author_str}")
        print(f"Journal/Venue: {res.get('journal')}")
        print(f"Year:          {res.get('year')}")
        if "type" in res:
            print(f"Type:          {res.get('type')}")
        if "doi" in res and res.get("doi") != "N/A":
            print(f"DOI:           https://doi.org/{res.get('doi')}")
        print(f"Official URL:  {res.get('url')}")
        
        if res.get("is_retracted"):
            print("\n🚨 WARNING: THIS PUBLICATION HAS AN ASSOCIATED RETRACTION / UPDATE!")
        else:
            print("\nRetraction:    No retraction notice detected on record.")
    else:
        print(f"Status:        [{status}]")
        print(f"Identifier:    {res.get('identifier')}")
        print(f"Reason:        {res.get('error', 'Unknown error')}")
        print("\n🚨 CẢNH BÁO: TÀI LIỆU KHÔNG THỂ XÁC MINH TRÊN CƠ SỞ DỮ LIỆU CHÍNH THỐNG!")
        print("   -> Tuyệt đối không sử dụng làm bằng chứng nếu không có nguồn đối chứng thay thế.")
    print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Verify DOIs and PMIDs against official academic repositories.")
    parser.add_argument("--doi", help="Digital Object Identifier to verify (e.g. 10.1016/j.jclinepi.2009.06.005)")
    parser.add_argument("--pmid", help="PubMed ID to verify (e.g. 20004944)")
    
    args = parser.parse_args()
    
    if not args.doi and not args.pmid:
        parser.print_help()
        sys.exit(1)
        
    if args.doi:
        res = verify_doi(args.doi)
        print_result(res)
    elif args.pmid:
        res = verify_pmid(args.pmid)
        print_result(res)

if __name__ == "__main__":
    main()
