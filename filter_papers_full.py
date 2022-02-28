from tqdm import tqdm
import json
import gzip
import time
from pebble import concurrent, ProcessPool, ProcessExpired
from concurrent.futures import TimeoutError
from multiprocessing import Lock
# from multiprocessing import Pool
from multiprocessing.managers import SyncManager
from functools import partial
from collections import Counter

from collections import defaultdict
from pathlib import Path

data_loc = Path('../20200705v1/full/')


def article_allowed(metadata):
    if metadata['mag_field_of_study'] and len(metadata['mag_field_of_study']) > 0 \
            and metadata['has_inbound_citations'] \
            and metadata['has_outbound_citations'] \
            and metadata['title'] \
            and metadata['abstract'] \
            and metadata['authors'] \
            and metadata['has_pdf_parse'] and metadata['has_pdf_parsed_abstract'] \
            and metadata['has_pdf_parsed_body_text'] and metadata['has_pdf_parsed_bib_entries'] \
            and metadata['has_pdf_parsed_ref_entries'] and metadata['abstract'] \
            and (metadata['journal'] or metadata['venue'] or metadata['arxiv_id'] or \
                 metadata['acl_id'] or metadata['pubmed_id'] or metadata['pmc_id']):
        return True

    return False


def filter_by_metadata(ab):
    venues = []
    try:
        if ab.suffix == '.gz':
            with gzip.open(ab) as f:
                for i, l in enumerate(f):
                    metadata = json.loads(l.strip())
                    if article_allowed(metadata):
                        venues.append((ab, l))
        else:
            with open(ab) as f:
                for i, l in enumerate(f):
                    metadata = json.loads(l.strip())
                    if article_allowed(metadata):
                        venues.append((ab, l))
    except BaseException as e:
        print(f"Unexpected {e=}, {type(e)=}")
    return venues


if __name__ == "__main__":
    # Get all of the statistics for venues, also time how long it takes to iterate through all the data
    start = time.time()
    Path("../filtered_metadata").mkdir(exist_ok=True)

    article_bundles = []
    for article_bundle in data_loc.glob(f"metadata/*.gz"):
        article_bundles.append(article_bundle)

    with ProcessPool() as pool:
        future = pool.map(filter_by_metadata, article_bundles, timeout=300)

        iterator = future.result()
        with tqdm(total=100) as pbar:
            while True:
                try:
                    result = next(iterator)
                    with gzip.open(f"../filtered_metadata/{result[0][0].name}", 'w') as f:
                        for l in result:
                            f.write(l[1])
                    pbar.update(1)
                except StopIteration:
                    break
                except TimeoutError as error:
                    print("function took longer than %d seconds" % error.args[1])
                except ProcessExpired as error:
                    print("%s. Exit code: %d" % (error, error.exitcode))
                except Exception as error:
                    print("function raised %s" % error)
                    print(error.traceback)  # Python's traceback of remote process
