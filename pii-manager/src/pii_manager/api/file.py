"""
File-based API
"""

import sys
import re
import json
import gzip
import bz2
import lzma
from itertools import zip_longest

from typing import Dict, List, TextIO, Iterable, Optional, Union

from pii_manager.api import PiiManager
from pii_manager.helper.exception import PiiManagerException


def openfile(name: str, mode: str) -> TextIO:
    """
    Open files, raw text or compressed (gzip, bzip2 or xz)
    """
    name = str(name)
    if name == "-":
        return sys.stdout if mode.startswith("w") else sys.stdin
    elif name.endswith(".gz"):
        return gzip.open(name, mode, encoding="utf-8")
    elif name.endswith(".bz2"):
        return bz2.open(name, mode, encoding="utf-8")
    elif name.endswith(".xz"):
        return lzma.open(name, mode, encoding="utf-8")
    else:
        return open(name, mode, encoding="utf-8")


def sentence_splitter(doc: str) -> Iterable[str]:
    """
    Split text by sentence separators
     (keeping the separator at the end of the sentence, so that joining the
    pieces recovers exactly the same text)
    """
    split = re.split(r"(\s*[\.!\?．。]\s+)", doc)
    args = [iter(split)] * 2
    for sentence, sep in zip_longest(*args, fillvalue=""):
        if sentence:
            yield sentence + sep


def write_extract(result: Iterable[Dict], index: Dict, out: TextIO):
    """
    Write output for "extract" mode as NDJSON
    """
    for pii in result:
        elem = {"name": pii.elem.name, "value": pii.value, "pos": pii.pos}
        if index:
            elem.update(index)
        json.dump(elem, out, ensure_ascii=False)
        print(file=out)


def write(
    result: Union[str, Iterable[Dict]], mode: str, index: Optional[Dict], out: TextIO
):
    """
    Write processing result to output
    """
    if mode == "extract":
        write_extract(result, index, out)
    else:
        out.write(result)


def print_tasks(proc: PiiManager, out: TextIO):
    print("\n. Installed tasks:", file=out)
    for pii, doc in proc.task_info().items():
        print(" ", pii.name, "\n   ", doc, file=out)


# ----------------------------------------------------------------------


def process_file(
    infile: str,
    outfile: str,
    lang: str,
    country: List[str] = None,
    tasks: List[str] = None,
    all_tasks: bool = False,
    split: str = "line",
    mode: str = "replace",
    template: str = None,
    debug: bool = False,
    show_tasks: bool = False,
    show_stats: bool = False,
) -> Dict:
    """
    Process PII tasks on a file
    """
    # Create the object
    proc = PiiManager(
        lang,
        country,
        tasks,
        all_tasks=all_tasks,
        mode=mode,
        template=template,
        debug=debug,
    )
    if show_tasks:
        print_tasks(proc, sys.stderr)

    # Process the file
    print(". Reading from:", infile, file=sys.stderr)
    print(". Writing to:", outfile, file=sys.stderr)
    with openfile(infile, "rt") as fin:
        with openfile(outfile, "wt") as fout:
            if split == "block":
                write(proc(fin.read()), mode, None, fout)
            elif split == "line":
                for n, line in enumerate(fin):
                    write(proc(line), mode, {"line": n + 1}, fout)
            elif split == "sentence":
                for n, sentence in enumerate(sentence_splitter(fin.read())):
                    write(proc(sentence), mode, {"sentence": n + 1}, fout)
            else:
                raise PiiManagerException("invalid split mode: {}", split)

    if show_stats:
        print("\n. Statistics:", file=sys.stderr)
        for k, v in proc.stats.items():
            print(f"  {k:20} :  {v:5}", file=sys.stderr)

    return proc.stats
