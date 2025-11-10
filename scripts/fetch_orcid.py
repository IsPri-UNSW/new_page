#!/usr/bin/env python3
import glob
import frontmatter
import os
import logging
import argparse

from helpers import setup_logging
from orcid import orcid_to_bibtex, bibtex_to_markdown, BIBTEX_DIR

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
    args = parser.parse_args()
    
    # Activate Debug logging
    setup_logging(logging.INFO)
    
    if args.refetch_all:
        log.info('Refetch-all mode enabled: will process all works from ORCID')

    # Determine root path of the repository - this script is in scripts/
    ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    log.debug('Root path: %s', ROOT_PATH)

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
    
    # Convert BibTeX files to Markdown
    log.info('Converting BibTeX files to Markdown...')
    for orcid in orcid_ids:
        try:
            bibtex_to_markdown(orcid, overwrite=(args.refetch_all or args.regenerate_markdown))
            log.info('Converted BibTeX to Markdown for %s', orcid)
        except Exception as e:
            log.error('Failed to convert BibTeX for %s: %s', orcid, e)

    # Write a timestamp into data/orcid/timestamp.txt
    from datetime import datetime
    timestamp_path = os.path.join(BIBTEX_DIR, 'timestamp.txt')
    with open(timestamp_path, 'w') as f:
        f.write(datetime.now().isoformat())
    log.info('Wrote timestamp to %s', timestamp_path)


