#!/usr/bin/env python3

import os
import pandas as pd


for root, dirs, fnames in os.walk("/Users/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/genomes"):
    for fn in fnames:
        if fn == 'diamond.out':
            fn = os.path.join(root, fn)
            print(os.path.split(os.path.dirname(fn))[1])