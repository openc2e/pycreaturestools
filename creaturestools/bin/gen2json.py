import json
import sys

from ..genetics import *


class MyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return o.decode("ascii", "backslashreplace")
        return super().default(o)


def main():
    input_filename = sys.argv[1]

    genes = read_gen3_file(input_filename)

    genes_data = [{"_version": "dna3"}]
    for gene in genes:
        data = {
            "_type": type(gene).__name__,
            "header": {_: getattr(gene.header, _) for _ in gene.header.__slots__},
        }
        for _ in gene.__slots__:
            if _ == "header":
                continue
            data[_] = getattr(gene, _)
        genes_data.append(data)
    print(json.dumps(genes_data, cls=MyEncoder, indent=4))
