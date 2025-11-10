from argparse import ArgumentParser

from helpers import setup_logging
from orcid import *



if __name__ == '__main__':
    parser = ArgumentParser(description='Test ORCID fetching.')
    parser.add_argument('orcid_id', help='ORCID ID to fetch', default='0000-0001-9962-5665', nargs='?', type=str)
    args = parser.parse_args()

    setup_logging(logging.DEBUG)

    orcid_to_bibtex(args.orcid_id, refetch_all=False)

    bibtex_to_markdown(args.orcid_id, overwrite=True)