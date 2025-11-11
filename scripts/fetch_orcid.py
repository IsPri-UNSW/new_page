#!/usr/bin/env python3
import glob
import frontmatter
import os
import logging
import argparse
from pathlib import Path

from helpers import setup_logging
from orcid import orcid_to_bibtex, bibtex_to_markdown, merge_all_bibtex_files, BIBTEX_DIR

log = logging.getLogger()

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Fetch ORCID publications for team members and generate BibTeX files.'
    )
    parser.add_argument(
        '-r',
        '--refetch-all',
        action='store_true',
        help='Refetch all works from ORCID, ignoring existing BibTeX entries'
    )
    parser.add_argument(
        '-g',
        '--regenerate-markdown',
        action='store_true',
        help='Regenerate Markdown files from existing BibTeX files'
    )
    parser.add_argument(
        '-s',
        '--skip',
        action='store_true',
        default=False,
        help='Skip fetching and only regenerate Markdown files'
    )
    args = parser.parse_args()
    
    # Activate Debug logging
    setup_logging(logging.INFO)
    
    if args.refetch_all:
        log.info('Refetch-all mode enabled: will process all works from ORCID')

    # Determine root path of the repository - this script is in scripts/
    ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    log.debug('Root path: %s', ROOT_PATH)

    if not args.skip:
        orcid_ids = []
        for path in glob.glob(os.path.join(ROOT_PATH, 'content', 'authors', '*/', '_index.md')):
            log.debug('Processing %s', path)
            try:
                post = frontmatter.load(path)
            except Exception:
                log.error('Failed to load %s', path)
                continue
            orcid = post.get('orcid')
            if orcid:
                try:
                    orcid_to_bibtex(orcid, refetch_all=args.refetch_all)
                    log.info('Fetched %s', orcid)
                    orcid_ids.append(orcid)
                except Exception as e:
                    log.error('Failed %s: %s', orcid, e)
    
    # Merge all BibTeX files into a single deduplicated all.bib
    log.info('Merging all BibTeX files into all.bib...')
    try:
        merge_all_bibtex_files()
        log.info('Successfully merged BibTeX files')
    except Exception as e:
        log.error(f'Failed to merge BibTeX files: {e}')
    
    # Convert the merged all.bib to Markdown
    log.info('Converting merged BibTeX file to Markdown...')
    try:
        all_bib_file = Path(BIBTEX_DIR) / 'all.bib'
        bibtex_to_markdown(all_bib_file, overwrite=(args.refetch_all or args.regenerate_markdown))
        log.info('Converted all.bib to Markdown')
    except Exception as e:
        log.error(f'Failed to convert BibTeX: {e}')

    # Write a timestamp into data/orcid/timestamp.txt
    from datetime import datetime
    timestamp_path = os.path.join(BIBTEX_DIR, 'timestamp.txt')
    with open(timestamp_path, 'w') as f:
        f.write(datetime.now().isoformat())
    log.info('Wrote timestamp to %s', timestamp_path)


