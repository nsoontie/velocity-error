# Script to save summary statistics of alpha

import glob
import os
import pickle

import pandas as pd
import numpy as np

exp = 'TREX2021oskers-CIOPSEv1p5-mshydro'
src_dir='../data/{}'.format(exp)
pickle_file = os.path.join(src_dir, 'all_{}.pickle'.format(exp))

with open(pickle_file, 'rb') as f:
    dfall = pickle.load(f)
    groups = dfall.groupby('buoyid')
    mean_alpha = groups.mean()[['alpha_real', 'alpha_imag']]
    mean_alpha.to_csv('{}/alpha_summary.txt'.format(src_dir))
