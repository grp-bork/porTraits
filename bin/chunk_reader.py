""" Module docstring """

import gzip


def get_lines_from_chunks(f: str, bufsize: int = 800000000):
    """
    Provides generator access to the lines of large text files.
    File is read chunk-wise into a buffer of the specified size.
    Support gzip-compressed files.

    inputs:
     - f: str -- filename
     - bufsize: int -- size of buffer

    """
    gzipped = f.endswith(".gz")
    with (gzip.open if gzipped else open)(f, "r") as _in:
        tail = ""
        while 1:
            chunk = _in.read(bufsize)
            if gzipped:
                chunk = chunk.decode()
            chunk = "".join((tail, chunk))
            if not chunk:
                break
            chunk = chunk.split("\n")
            *lines, tail = chunk
            yield from lines
        if tail:
            yield tail
