"""Script to plot maps from biosSVPs-CIOPSEv2"""

import glob
import os
import pickle

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd
import xarray as xr

import errors

src_dir='../data/TREX-CIOPSEv2-relocatable1km'
pickle_file = os.path.join(src_dir, 'all_TREX-CIOPSEv2-relocatable1km.pickle')


def main():
    # Load data
    if not os.path.exists(pickle_file):
        dfall = load_data(src_dir)
        with open(pickle_file, 'wb') as f:
            pickle.dump(dfall, f)
    else:
        with open(pickle_file, 'rb') as f:
            dfall = pickle.load(f)
    print(dfall.mean())
    print(dfall.std())
    fig, ax = plt.subplots(1, 1, figsize=(15,5))
    mesh = plot_error_map(dfall, ax, error='speed_adjusted_error')
    cbar = plt.colorbar(mesh, ax=ax)
    cbar.set_label('adjusted speed - drifter speed [m/s]')
    plt.show()

    
def plot_error_map(df, ax, error='speed_ocean_error',
                   lon_min=-69, lat_min=48, lon_max=-61, lat_max=51,
                   cmap='RdBu_r', vmin=-1, vmax=1, latstep=1, lonstep=1):
    m =  Basemap(llcrnrlon=lon_min, llcrnrlat=lat_min,
                 urcrnrlon=lon_max, urcrnrlat=lat_max,
                 projection='merc', resolution='h', ax=ax)
    x, y = m(df.lon.values, df.lat.values)
    mesh = m.hexbin(x, y, C=df[error].values, cmap=cmap, vmin=vmin, vmax=vmax)
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
