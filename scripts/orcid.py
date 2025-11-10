import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import unicodedata
import requests
import logging
import re
import time

from pprint import pprint
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from academic.import_bibtex import import_bibtex

log = logging.getLogger()

# Determine root path of the repository - this script is in scripts/
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BIBTEX_DIR = os.path.join(ROOT_PATH, 'content', 'bibtex')
MARKDOWN_DIR = os.path.join(ROOT_PATH, 'content', 'publication')

# Helper functions used across multiple functions

def _is_empty(v: Any) -> bool:
    """Check if a value is considered empty."""
    return v in (None, "", [], {})

def _norm_doi(s: Optional[str]) -> Optional[str]:
    """Normalize a DOI string."""
    if not s:
        return None
    s = str(s).strip()
    s = s.replace("DOI:", "").replace("doi:", "").strip()
    return s.lower()

def _norm_arxiv(s: Optional[str]) -> Optional[str]:
    """Normalize an arXiv identifier."""
    if not s:
        return None
    s = str(s).replace("\t", " ").strip()
    s = s.replace("arxiv:", "arXiv:")
    if ":" in s:
        s = s.split(":", 1)[1]
    return s.strip()

def _norm_title(t: Optional[str]) -> Optional[str]:
    """Normalize a title for comparison."""
    if not t:
        return None
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode("ascii")
    t = t.lower()
    # collapse whitespace and drop trivial punctuation
    t = re.sub(r"[\s]+", " ", t)
    t = re.sub(r"[^\w\s]", "", t)
    return t.strip() or None

def _sort_key_by_date(w: Dict[str, Any]) -> tuple:
    """Generate a sort key for a work based on publication date."""
    y = int(w.get("year") or 0)
    m = int(w.get("month") or 0) if str(w.get("month") or "").isdigit() else 0
    d = int(w.get("day") or 0) if str(w.get("day") or "").isdigit() else 0
    return (y, m, d)

def _ext_ids_to_map_with_urls(ext_ids: Dict[str, Any]) -> Dict[str, Dict[str, Optional[str]]]:
    """Extract external IDs to a map including URLs (used in _cleanup_orcid_data)."""
    out: Dict[str, Dict[str, Optional[str]]] = {}
    for eid in ext_ids.get("external-id", []):
        t = eid.get("external-id-type")
        val = eid.get("external-id-value")
        url = (eid.get("external-id-url") or {}).get("value")
        if not t or not val:
            continue
        t = str(t).strip().lower()
        # keep first seen per type
        if t not in out:
            out[t] = {"value": str(val).strip(), "url": url.strip() if isinstance(url, str) else None}
    return out

def _ext_ids_to_map_simple(ext_ids: Dict[str, Any]) -> Dict[str, str]:
    """Extract external IDs to a simple map (used in enrich_orcid_work)."""
    out: Dict[str, str] = {}
    for eid in (ext_ids or {}).get("external-id", []):
        t = str(eid.get("external-id-type") or "").strip().lower()
        v = str(eid.get("external-id-value") or "").strip()
        if t and v and t not in out:
            out[t] = v
    return out

def _best_url(doi_url: Optional[str], given_url: Optional[str], arxiv_url: Optional[str], handle_url: Optional[str]) -> Optional[str]:
    """Select the best URL from available options."""
    for u in (doi_url, given_url, arxiv_url, handle_url):
        if u and u.strip():
            return u.strip()
    return None

def _pick_summary(summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pick the best summary from a list of work summaries."""
    # Prefer entries with a journal/conference title, then with a URL, then latest last-modified-date, then highest display-index
    def score(ws: Dict[str, Any]) -> tuple:
        venue = (ws.get("journal-title") or {}).get("value")
        url = (ws.get("url") or {}).get("value")
        lmd = (ws.get("last-modified-date") or {}).get("value") or 0
        di_raw = ws.get("display-index")
        try:
            di = int(di_raw) if di_raw is not None else -1
        except Exception:
            di = -1
        return (
            1 if venue else 0,
            1 if url else 0,
            int(lmd),
            di,
        )
    return max(summaries, key=score)

def _date_parts(ws: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Extract date parts from a work summary."""
    pd = ws.get("publication-date") or {}
    return {
        "year": ((pd.get("year") or {}).get("value")) if isinstance(pd.get("year"), dict) else None,
        "month": ((pd.get("month") or {}).get("value")) if isinstance(pd.get("month"), dict) else None,
        "day": ((pd.get("day") or {}).get("value")) if isinstance(pd.get("day"), dict) else None,
    }

def _merge_dict_preferring_non_empty(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
    """Merge src dict into dst, preferring non-empty values."""
    for k, v in src.items():
        if _is_empty(v):
            continue
        if k not in dst or _is_empty(dst[k]):
            dst[k] = v

def _merge_authors(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
    """Merge authors from src into dst, avoiding duplicates."""
    da = dst.get("authors") or []
    sa = src.get("authors") or []
    if not da and sa:
        dst["authors"] = sa
        return
    if sa:
        seen = set()
        merged = []
        # build initial
        for a in da:
            key = (str(a.get("orcid") or "").lower(), str(a.get("name") or "").lower())
            if key not in seen:
                seen.add(key)
                merged.append(a)
        # add from src
        for a in sa:
            key = (str(a.get("orcid") or "").lower(), str(a.get("name") or "").lower())
            if key not in seen:
                seen.add(key)
                merged.append(a)
        dst["authors"] = merged

def fetch_orcid_json(orcid_id: str) -> dict:
    """Fetch ORCID works for a given ORCID ID."""
    url = f'https://pub.orcid.org/v3.0/{orcid_id}/works'
    headers = {'Accept': 'application/orcid+json, application/json', 'User-Agent': 'IsPri-UNSW-hugo-site'}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        log.info('Fetched %s', orcid_id)
        return r.json()
    except Exception as e:
        log.error('Failed %s: %s', orcid_id, e)
        return {}
    
def _cleanup_orcid_data(data: dict) -> List[Dict[str, Any]]:
    """
    Clean up the ORCID data and return one dict per work suitable for BibTeX-style processing.

    :param data: Raw ORCID JSON as dict
    :returns: List of cleaned works with keys such as title, year, type, doi, arxiv, venue, url
    """
    works: List[Dict[str, Any]] = []
    for grp in data.get("group", []):
        # Collect external IDs at group level for deduped identifiers
        gid_map = _ext_ids_to_map_with_urls(grp.get("external-ids") or {})
        doi = _norm_doi((gid_map.get("doi") or {}).get("value"))
        doi_url = (gid_map.get("doi") or {}).get("url")
        arxiv_raw = (gid_map.get("arxiv") or {}).get("value")
        arxiv = _norm_arxiv(arxiv_raw)
        arxiv_url = (gid_map.get("arxiv") or {}).get("url")
        handle_url = (gid_map.get("handle") or {}).get("url")
        isbn = (gid_map.get("isbn") or {}).get("value")
        issn = (gid_map.get("issn") or {}).get("value")
        eid = (gid_map.get("eid") or {}).get("value")

        summaries = grp.get("work-summary") or []
        if not summaries:
            continue
        ws = _pick_summary(summaries)

        title_obj = (ws.get("title") or {}).get("title") or {}
        title = title_obj.get("value") if isinstance(title_obj, dict) else None
        wtype = ws.get("type")
        venue = ((ws.get("journal-title") or {}).get("value")) or None
        given_url = (ws.get("url") or {}).get("value")
        url = _best_url(doi_url, given_url, arxiv_url, handle_url)

        date = _date_parts(ws)
        put_code = ws.get("put-code")
        path = ws.get("path")
        src = ws.get("source") or {}
        source_name = ((src.get("source-name") or {}).get("value")) if isinstance(src.get("source-name"), dict) else None

        # Construct minimal BibTeX-like dict
        work: Dict[str, Any] = {
            "title": title,
            "type": wtype,
            "venue": venue,
            "year": date.get("year"),
            "month": date.get("month"),
            "day": date.get("day"),
            "doi": doi,
            "arxiv": arxiv,
            "isbn": isbn,
            "issn": issn,
            "scopus_eid": eid,
            "url": url,
            "orcid_put_code": put_code,
            "orcid_path": path,
            "orcid_source": source_name,
        }

        # Normalise trivial empties
        work = {k: (v.strip() if isinstance(v, str) else v) for k, v in work.items() if v not in (None, "", [], {})}
        works.append(work)

    # Sort newest first by (year, month, day) when available
    works.sort(key=_sort_key_by_date, reverse=True)
    return works

def enrich_orcid_work(work: Dict[str, Any], token: Optional[str] = None, base_url: str = "https://pub.orcid.org/v3.0", session: Optional[requests.Session] = None, timeout: int = 20, retries: int = 3, backoff: float = 0.8) -> Dict[str, Any]:
    """
    Enrich a cleaned ORCID work dict with full work metadata from ORCID.

    :param work: One item produced by _cleanup_orcid_data
    :param token: OAuth2 token for higher rate limits (optional)
    :param base_url: ORCID API base URL
    :param session: Optional requests.Session
    :param timeout: HTTP timeout seconds
    :param retries: Retry count for transient errors
    :param backoff: Backoff factor between retries
    :returns: The input dict augmented with fields such as authors, abstract, volume, pages, citation_bibtex
    """
    # Expect fields provided by _cleanup_orcid_data: "orcid_path" and "orcid_put_code"
    path = str(work.get("orcid_path") or "")
    put_code = str(work.get("orcid_put_code") or "").strip()
    if not path or not put_code:
        return work

    m = re.search(r"/(\d{4}-\d{4}-\d{4}-\d{3}[0-9Xx])/", path)
    if not m:
        return work
    orcid_id = m.group(1)

    url = f"{base_url}/{orcid_id}/work/{put_code}"
    owns = session or requests.Session()
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def _normalise_identifiers(ext_map: Dict[str, str]) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "doi": _norm_doi(ext_map.get("doi")),
            "arxiv": _norm_arxiv(ext_map.get("arxiv")),
            "pmid": ext_map.get("pmid"),
            "pmcid": ext_map.get("pmc"),
            "isbn": ext_map.get("isbn"),
            "issn": ext_map.get("issn"),
            "scopus_eid": ext_map.get("eid"),
            "handle": ext_map.get("handle"),
        }
        return {k: v for k, v in out.items() if v}

    def _contributors_list(wj: Dict[str, Any]) -> List[Dict[str, Any]]:
        res: List[Dict[str, Any]] = []
        contribs = ((wj.get("contributors") or {}).get("contributor")) or []
        for c in contribs:
            name = (((c.get("credit-name") or {}).get("value")) if isinstance(c.get("credit-name"), dict) else None) or (((c.get("contributor-name") or {}).get("value")) if isinstance(c.get("contributor-name"), dict) else None)
            orcid_path = (((c.get("contributor-orcid") or {}).get("path")) if isinstance(c.get("contributor-orcid"), dict) else None)
            role = (((c.get("contributor-attributes") or {}).get("contributor-role")) if isinstance(c.get("contributor-attributes"), dict) else None) or c.get("contributor-role")
            seq = (((c.get("contributor-attributes") or {}).get("contributor-sequence")) if isinstance(c.get("contributor-attributes"), dict) else None) or c.get("contributor-sequence")
            item = {k: v for k, v in {"name": name, "orcid": orcid_path, "role": role, "sequence": seq}.items() if v}
            if item:
                res.append(item)
        return res

    def _best_citations(wj: Dict[str, Any]) -> Dict[str, str]:
        out: Dict[str, str] = {}
        cit = wj.get("citation") or {}
        ctype = cit.get("citation-type")
        ctext = cit.get("citation")
        if isinstance(ctype, str) and isinstance(ctext, str):
            if ctype.upper() == "BIBTEX":
                out["citation_bibtex"] = ctext.strip()
            elif ctype.upper() in {"RIS", "REFMAN"}:
                out["citation_ris"] = ctext.strip()
        for it in (wj.get("citations") or {}).get("citation", []) if isinstance(wj.get("citations"), dict) else []:
            t = str(it.get("citation-type") or "").upper()
            s = str(it.get("citation") or "")
            if t == "BIBTEX" and "citation_bibtex" not in out and s.strip():
                out["citation_bibtex"] = s.strip()
            if t in {"RIS", "REFMAN"} and "citation_ris" not in out and s.strip():
                out["citation_ris"] = s.strip()
        return out

    last_err: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            r = owns.get(url, headers=headers, timeout=timeout)
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep((attempt + 1) * backoff)
                continue
            r.raise_for_status()
            wj = r.json()

            # Titles
            t_main = ((wj.get("title") or {}).get("title") or {})
            title = t_main.get("value") if isinstance(t_main, dict) else None
            subtitle = ((wj.get("title") or {}).get("subtitle") or {}).get("value") if isinstance((wj.get("title") or {}).get("subtitle"), dict) else None
            translated = ((wj.get("title") or {}).get("translated-title") or {}).get("value") if isinstance((wj.get("title") or {}).get("translated-title"), dict) else None

            # Dates
            pd = wj.get("publication-date") or {}
            year = ((pd.get("year") or {}).get("value")) if isinstance(pd.get("year"), dict) else None
            month = ((pd.get("month") or {}).get("value")) if isinstance(pd.get("month"), dict) else None
            day = ((pd.get("day") or {}).get("value")) if isinstance(pd.get("day"), dict) else None

            # Venue and bibliographic fields
            venue = ((wj.get("journal-title") or {}).get("value")) if isinstance(wj.get("journal-title"), dict) else None
            volume = wj.get("volume")
            issue = wj.get("issue")
            pages = wj.get("pages")
            publisher = wj.get("publisher")
            language = wj.get("language-code")
            abstract = wj.get("short-description")
            wtype = wj.get("type") or wj.get("work-type")
            url_field = ((wj.get("url") or {}).get("value")) if isinstance(wj.get("url"), dict) else None
            created = ((wj.get("created-date") or {}).get("value")) if isinstance(wj.get("created-date"), dict) else None
            modified = ((wj.get("last-modified-date") or {}).get("value")) if isinstance(wj.get("last-modified-date"), dict) else None

            # IDs, authors, citations
            ids_norm = _normalise_identifiers(_ext_ids_to_map_simple(wj.get("external-ids") or {}))
            authors = _contributors_list(wj)
            citations = _best_citations(wj)

            enrichment: Dict[str, Any] = {
                "title": title,
                "subtitle": subtitle,
                "translated_title": translated,
                "venue": venue,
                "volume": volume,
                "issue": issue,
                "pages": pages,
                "publisher": publisher,
                "language": language,
                "abstract": abstract,
                "type": wtype,
                "url": url_field,
                "year": year,
                "month": month,
                "day": day,
                "authors": authors,
                "orcid_created": created,
                "orcid_last_modified": modified,
            }
            enrichment.update(ids_norm)
            enrichment.update(citations)

            _merge_dict_preferring_non_empty(work, enrichment)

            # Heuristic DOI extraction from BibTeX if still missing
            if not work.get("doi") and work.get("citation_bibtex"):
                mdoi = re.search(r"doi\s*=\s*[{]?\s*([^},\s]+)\s*[}]?", work["citation_bibtex"], flags=re.IGNORECASE)
                if mdoi:
                    work["doi"] = mdoi.group(1).strip()

            return work
        except Exception as e:
            last_err = e
            time.sleep((attempt + 1) * backoff)
            continue
    return work

def enrich_orcid_works(data: dict) -> dict:
    """Enrich all works in the cleaned ORCID data dict."""
    works = data if isinstance(data, list) else []
    enriched_works = []
    for work in works:
        enriched = enrich_orcid_work(work)
        enriched_works.append(enriched)
    return enriched_works

def deduplicate_orcid_works(works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate based on DOI OR arXiv ID OR title.
    Join the data of duplicates, preferring non-empty fields.
    """
    groups: List[Dict[str, Any]] = []  # each item: {"work": dict, "keys": {"doi": set, "arxiv": set, "title": set}}
    doi_map: Dict[str, int] = {}
    arxiv_map: Dict[str, int] = {}
    title_map: Dict[str, int] = {}

    for w in works:
        k_doi = _norm_doi(w.get("doi"))
        k_arx = _norm_arxiv(w.get("arxiv"))
        k_tit = _norm_title(w.get("title"))

        matched_groups = []
        if k_doi and k_doi in doi_map:
            matched_groups.append(doi_map[k_doi])
        if k_arx and k_arx in arxiv_map:
            matched_groups.append(arxiv_map[k_arx])
        if k_tit and k_tit in title_map:
            matched_groups.append(title_map[k_tit])

        matched_groups = list(dict.fromkeys(matched_groups))  # unique in order

        if not matched_groups:
            # create new group
            grp_idx = len(groups)
            groups.append({
                "work": dict(w),  # copy
                "keys": {
                    "doi": set([k_doi]) if k_doi else set(),
                    "arxiv": set([k_arx]) if k_arx else set(),
                    "title": set([k_tit]) if k_tit else set(),
                },
            })
            if k_doi:
                doi_map[k_doi] = grp_idx
            if k_arx:
                arxiv_map[k_arx] = grp_idx
            if k_tit:
                title_map[k_tit] = grp_idx
            continue

        # attach to the first matched group
        main_idx = matched_groups[0]
        main = groups[main_idx]["work"]

        # merge fields
        _merge_dict_preferring_non_empty(main, w)
        _merge_authors(main, w)

        # store back
        groups[main_idx]["work"] = main

        # record new keys for the main group
        if k_doi:
            groups[main_idx]["keys"]["doi"].add(k_doi)
            doi_map[k_doi] = main_idx
        if k_arx:
            groups[main_idx]["keys"]["arxiv"].add(k_arx)
            arxiv_map[k_arx] = main_idx
        if k_tit:
            groups[main_idx]["keys"]["title"].add(k_tit)
            title_map[k_tit] = main_idx

        # if this work matches multiple existing groups, merge those groups into main
        for other_idx in matched_groups[1:]:
            if other_idx == main_idx:
                continue
            other = groups[other_idx]
            # merge dicts
            _merge_dict_preferring_non_empty(main, other["work"])
            _merge_authors(main, other["work"])
            # move key ownership
            for kd in list(other["keys"]["doi"]):
                doi_map[kd] = main_idx
                groups[main_idx]["keys"]["doi"].add(kd)
            for ka in list(other["keys"]["arxiv"]):
                arxiv_map[ka] = main_idx
                groups[main_idx]["keys"]["arxiv"].add(ka)
            for kt in list(other["keys"]["title"]):
                title_map[kt] = main_idx
                groups[main_idx]["keys"]["title"].add(kt)
            # mark other as empty group
            groups[other_idx]["work"] = {}

    # collect non-empty groups
    merged = [g["work"] for g in groups if g["work"]]

    # final normalisation: ensure one doi/arxiv/title kept as strings already present in work
    # sort newest first
    merged.sort(key=_sort_key_by_date, reverse=True)
    return merged


def _bibtex_to_works(bib_db: BibDatabase) -> List[Dict[str, Any]]:
    """
    Convert BibTeX database entries to work dictionaries for comparison.
    
    :param bib_db: BibDatabase object
    :returns: List of work dictionaries with normalized keys
    """
    works = []
    for entry in bib_db.entries:
        work = {
            "title": entry.get("title"),
            "doi": _norm_doi(entry.get("doi")),
            "arxiv": _norm_arxiv(entry.get("eprint")),
            "year": entry.get("year"),
            "bibtex_key": entry.get("ID"),
        }
        works.append(work)
    return works


def _filter_existing_works(new_works: List[Dict[str, Any]], existing_works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter out works that already exist in the BibTeX database.
    
    :param new_works: List of works from ORCID
    :param existing_works: List of works extracted from existing BibTeX
    :returns: List of works that don't already exist
    """
    # Build lookup sets for existing works
    existing_dois = set()
    existing_arxivs = set()
    existing_titles = set()
    
    for work in existing_works:
        doi = work.get("doi")
        if doi:
            existing_dois.add(doi)
        
        arxiv = work.get("arxiv")
        if arxiv:
            existing_arxivs.add(arxiv)
        
        title = _norm_title(work.get("title"))
        if title:
            existing_titles.add(title)
    
    # Filter new works
    filtered = []
    for work in new_works:
        work_doi = _norm_doi(work.get("doi"))
        work_arxiv = _norm_arxiv(work.get("arxiv"))
        work_title = _norm_title(work.get("title"))
        
        # Check if work already exists by DOI, arXiv, or title
        if work_doi and work_doi in existing_dois:
            log.debug(f"Skipping existing work (DOI match): {work.get('title', 'Unknown')}")
            continue
        if work_arxiv and work_arxiv in existing_arxivs:
            log.debug(f"Skipping existing work (arXiv match): {work.get('title', 'Unknown')}")
            continue
        if work_title and work_title in existing_titles:
            log.debug(f"Skipping existing work (title match): {work.get('title', 'Unknown')}")
            continue
        
        filtered.append(work)
    
    return filtered


def _generate_bibtex_key(work: Dict[str, Any], index: int) -> str:
    """Generate a BibTeX citation key for a work."""
    # Try to extract first author's last name
    authors = work.get("authors", [])
    if authors and isinstance(authors, list) and len(authors) > 0:
        first_author = authors[0].get("name", "")
        # Try to extract last name (assume it's the last word)
        if first_author:
            parts = first_author.strip().split()
            last_name = parts[-1] if parts else "Unknown"
        else:
            last_name = "Unknown"
    else:
        last_name = "Unknown"
    
    # Clean the last name for use in citation key
    last_name = re.sub(r'[^\w]', '', last_name)
    
    # Get year
    year = work.get("year", "")
    
    # Get first word of title
    title = work.get("title", "")
    if title:
        title_words = re.findall(r'\w+', title)
        first_word = title_words[0].lower() if title_words else "untitled"
    else:
        first_word = "untitled"
    
    # Construct key: LastnameYYYYFirstword or use index as fallback
    if year:
        key = f"{last_name}{year}{first_word}"
    else:
        key = f"{last_name}{first_word}{index}"
    
    return key


def _format_authors_bibtex(authors: List[Dict[str, Any]]) -> str:
    """Format authors list for BibTeX."""
    if not authors:
        return ""
    
    author_names = []
    for author in authors:
        name = author.get("name", "").strip()
        if name:
            author_names.append(name)
    
    return " and ".join(author_names)


def _infer_entry_type(work: Dict[str, Any]) -> str:
    """Infer BibTeX entry type from work metadata."""
    wtype = str(work.get("type", "")).lower()
    
    # Map ORCID work types to BibTeX entry types
    if "journal" in wtype or "article" in wtype:
        return "article"
    elif "conference" in wtype or "proceeding" in wtype:
        return "inproceedings"
    elif "book" in wtype and "chapter" not in wtype:
        return "book"
    elif "chapter" in wtype:
        return "incollection"
    elif "thesis" in wtype or "dissertation" in wtype:
        return "phdthesis"
    elif "report" in wtype or "technical" in wtype:
        return "techreport"
    elif "preprint" in wtype or work.get("arxiv"):
        return "misc"
    else:
        # Default to misc for unknown types
        return "misc"


def works_to_bibtex(works: List[Dict[str, Any]]) -> BibDatabase:
    """
    Convert a list of works to BibTeX format.
    
    :param works: List of work dictionaries from deduplicate_orcid_works
    """
    db = BibDatabase()
    entries = []
    
    seen_keys = set()
    
    for idx, work in enumerate(works):
        # Generate unique citation key
        base_key = _generate_bibtex_key(work, idx)
        key = base_key
        counter = 1
        while key in seen_keys:
            key = f"{base_key}_{counter}"
            counter += 1
        seen_keys.add(key)
        
        # Determine entry type
        entry_type = _infer_entry_type(work)
        
        # Build entry dict
        entry = {
            "ID": key,
            "ENTRYTYPE": entry_type,
        }
        
        # Add standard fields
        if work.get("title"):
            entry["title"] = work["title"]
        
        if work.get("authors"):
            entry["author"] = _format_authors_bibtex(work["authors"])
        
        if work.get("year"):
            entry["year"] = str(work["year"])
        
        if work.get("month"):
            entry["month"] = str(work["month"])
        
        if work.get("doi"):
            entry["doi"] = work["doi"]
        
        if work.get("url"):
            entry["url"] = work["url"]
        
        if work.get("venue"):
            # Map venue to appropriate field based on entry type
            if entry_type == "article":
                entry["journal"] = work["venue"]
            elif entry_type in ("inproceedings", "incollection"):
                entry["booktitle"] = work["venue"]
            else:
                entry["journal"] = work["venue"]
        
        if work.get("volume"):
            entry["volume"] = str(work["volume"])
        
        if work.get("issue"):
            entry["number"] = str(work["issue"])
        
        if work.get("pages"):
            entry["pages"] = str(work["pages"])
        
        if work.get("publisher"):
            entry["publisher"] = work["publisher"]
        
        if work.get("abstract"):
            entry["abstract"] = work["abstract"]
        
        if work.get("arxiv"):
            entry["eprint"] = work["arxiv"]
            entry["eprinttype"] = "arXiv"
            entry["archiveprefix"] = "arXiv"
        
        if work.get("isbn"):
            entry["isbn"] = work["isbn"]
        
        if work.get("issn"):
            entry["issn"] = work["issn"]
        
        # Add optional fields
        if work.get("language"):
            entry["language"] = work["language"]
        
        if work.get("subtitle"):
            entry["subtitle"] = work["subtitle"]
        
        entries.append(entry)
    
    db.entries = entries

    return db


def orcid_to_bibtex(orcid_id: str, output_dir: str | Path = BIBTEX_DIR, refetch_all: bool = False) -> None:
    """
    Fetch ORCID works, process them, and write to BibTeX file.
    
    :param orcid_id: ORCID identifier (e.g., '0000-0002-1825-0097')
    :param output_dir: Directory to write the .bib file
    :param refetch_all: If True, refetch and process all works even if they exist in the BibTeX file
    :returns: List of processed work dictionaries
    """
    bib_file = Path(output_dir) / f"{orcid_id}.bib"
    
    # Load existing data if present
    loaded_db: Optional[BibDatabase] = None
    existing_works: List[Dict[str, Any]] = []
    if bib_file.exists() and not refetch_all:
        with open(bib_file, 'r', encoding='utf-8') as f:
            loaded_db = bibtexparser.load(f)
        log.info(f"Loaded existing BibTeX file with {len(loaded_db.entries)} entries from {bib_file}")
        existing_works = _bibtex_to_works(loaded_db)
    elif bib_file.exists() and refetch_all:
        log.info(f"Refetch all mode enabled - ignoring existing BibTeX file at {bib_file}")

    # Fetch and process data
    data = fetch_orcid_json(orcid_id)
    data = _cleanup_orcid_data(data)
    
    # Filter out works that already exist in the BibTeX file (unless refetch_all is True)
    if existing_works and not refetch_all:
        original_count = len(data)
        data = _filter_existing_works(data, existing_works)
        log.info(f"Filtered {original_count - len(data)} existing works, {len(data)} new works to process")
    
    # Only enrich and process new works
    if data:
        data = enrich_orcid_works(data)
        data = deduplicate_orcid_works(data)
        new_bib_db = works_to_bibtex(data)
        
        # Merge with existing database (only if not refetch_all mode)
        if loaded_db and not refetch_all:
            # Combine entries: existing + new
            merged_db = BibDatabase()
            merged_db.entries = loaded_db.entries + new_bib_db.entries
            bib_db = merged_db
            log.info(f"Merged {len(loaded_db.entries)} existing entries with {len(new_bib_db.entries)} new entries")
        else:
            bib_db = new_bib_db
            if refetch_all:
                log.info(f"Refetch all mode: replacing file with {len(new_bib_db.entries)} entries")
    else:
        # No new works, keep existing database
        if loaded_db:
            bib_db = loaded_db
            log.info("No new works to add, keeping existing BibTeX file unchanged")
        else:
            # No existing file and no new works
            bib_db = BibDatabase()
            log.info("No works found to write")

    # Write to BibTeX file only if there's something to write
    if bib_db.entries:
        bib_file.parent.mkdir(parents=True, exist_ok=True)
        with open(bib_file, 'w', encoding='utf-8') as f:
            bibtexparser.dump(bib_db, f)
        
        log.info(f"Wrote {len(bib_db.entries)} total BibTeX entries to {bib_file}")


def bibtex_to_markdown(orcid_id: str, bibtex_dir: str | Path = BIBTEX_DIR, overwrite: bool = False) -> None:
    """
    Convert BibTeX file to Markdown files using the academic package.
    
    :param orcid_id: ORCID identifier
    :param bibtex_dir: Directory containing the BibTeX files
    """
    import subprocess
    
    bibtex_file = Path(bibtex_dir) / f"{orcid_id}.bib"
    if not bibtex_file.exists():
        log.warning(f"BibTeX file not found: {bibtex_file}")
        return
    
    # Output directory for markdown files
    output_dir = Path(MARKDOWN_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create _index.md for Hugo page bundle if it doesn't exist
    index_file = output_dir / '_index.md'
    if not index_file.exists():
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Publications
---
""")
        log.debug(f"Created {index_file}")

    import_bibtex(
        bibtex=bibtex_file,
        pub_dir=output_dir,
        compact=False,
        normalize=True,
        overwrite=overwrite,
    )
    log.info(f"Converted BibTeX to Markdown files in {output_dir}")
    
    # Post-process to fix invalid dates
    _fix_invalid_dates(output_dir)


def _fix_invalid_dates(output_dir: Path) -> None:
    """
    Post-process markdown files to remove invalid date fields.
    
    The academic CLI sometimes generates invalid dates like '-01-01' when
    the year is missing from the BibTeX entry. This function removes such
    invalid date fields to prevent Hugo parsing errors.
    """
    import frontmatter
    import re
    
    for md_file in output_dir.rglob("index.md"):
        if md_file.name == "_index.md":
            continue
        
        try:
            post = frontmatter.load(md_file)
            
            # Check if date field exists and is invalid
            if 'date' in post.metadata:
                date_str = str(post.metadata['date'])
                # Check for invalid dates like '-01-01' or dates missing year
                if re.match(r'^-\d{2}-\d{2}$', date_str) or not re.search(r'\d{4}', date_str):
                    log.debug(f"Removing invalid date '{date_str}' from {md_file}")
                    del post.metadata['date']
                    
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(frontmatter.dumps(post))
                        
        except Exception as e:
            log.error(f"Failed to process {md_file}: {e}")


