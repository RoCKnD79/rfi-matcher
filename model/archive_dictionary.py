import numpy as np
from model.data_archives import *


ARCHIVE_CLASSES = {
    "MEERKAT": MeerkatDataArchive,
    "VERY LARGE ARRAY NM": NraoDataArchive,
    "ALMA_1": NraoDataArchive,
    "ALMA_2": NraoDataArchive,
}