"""Script to plot maps from TREX-GSL500-relocatable1km"""

import glob
import os
import pickle

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd
import xarray as xr

import errors

src_dirs = {'ciopse-par': '../data/TREX2021oskers-CIOPSEv2-mshydro',
            'ciopse-ops': '../data/TREX2021oskers-CIOPSEv1p5-mshydro'}
pickle_files = {
    exp: os.path.join(src_dirs[exp],
                      'all_{}.pickle'.format(os.path.basename(src_dirs[exp])))
    for exp in src_dirs.keys()
}


def main():
    # Load data
    for exp in src_dirs.keys():
        src_dir = src_dirs[exp]
        pickle_file = pickle_files[exp]
        if not os.path.exists(pickle_file):
            dfall = load_data(src_dir)
            with open(pickle_file, 'wb') as f:
                pickle.dump(dfall, f)
        else:
            with open(pickle_file, 'rb') as f:
                dfall = pickle.load(f)
        stats = dfall.agg(['mean', 'std', 'var']).transpose()
        stats.to_csv('{}.txt'.format(os.path.basename(src_dir)))
        fig, ax = plt.subplots(1, 1, figsize=(15,5))
        mesh = plot_error_map(dfall, ax, error='speed_adjusted_error')
        cbar = plt.colorbar(mesh, ax=ax)
        cbar.set_label('adjusted speed - drifter speed [m/s]')
        ax.set_title(exp)
        fig.savefig('{}-adjusted_error.png'.format(os.path.basename(src_dir)),
                    bbox_inches='tight')

    
def plot_error_map(df, ax, error='speed_ocean_error',
                   lon_min=-69, lat_min=48, lon_max=-61, lat_max=50,
                   cmap='RdBu_r', vmin=-1, vmax=1, latstep=1, lonstep=1):
    m =  Basemap(llcrnrlon=lon_min, llcrnrlat=lat_min,
                 urcrnrlon=lon_max, urcrnrlat=lat_max,
                 projection='merc', resolution='h', ax=ax)
    x, y = m(df.lon.values, df.lat.values)
    mesh = m.hexbin(x, y, C=df[error].values, cmap=cmap, vmin=vmin, vmax=vmax,
                    gridsize=40)
    m.drawcoastlines()
    m.drawmeridians(np.arange(lon_min, lon_max, lonstep), labels=[False, False, False, True])
    m.drawparallels(np.arange(lat_min, lat_max, latstep), labels=[True, False, False, False])
    return mesh

            
def load_data(src_dir):
    files = glob.glob(os.path.join(src_dir, '*.nc'))
    files.sort()
    dfall = pd.DataFrame()
    for f in files:
        d = xr.open_dataset(f)
        d = errors.process_drifter(d)
        df = d.to_dataframe()
        df['buoyid'] = d.attrs['obs_buoyid']
        if 'obs_drifter_type' in d.attrs:
            df['drifter_type'] = d.attrs['obs_drifter_type']
        elif 'obs_model' in d.attrs:
            df['drifter_type'] = d.attrs['obs_model']
        dfall = pd.concat([dfall,df])
    return dfall



if __name__ == '__main__':
    main()
