"""Script to plot stuff from TREX"""

import glob
import os
import pickle

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd
import xarray as xr

import errors


exps = ['TREX-CIOPSEv2-relocatable1km', 'TREX-GSL500-relocatable1km']
src_dirs = {exp: '../data/{}'.format(exp) for exp in exps}
pickle_files = {
    exp: os.path.join(src_dirs[exp],
                      'all_{}.pickle'.format(exp)) for exp in exps
}
#Fontsize for plots
FS=16
# GridSize
GS=40
#Min number of points in hexbins
MN=5

def main():
    # Load data
    for exp in exps:
        print(exp)
        model = exp.split('-')[1]
        src_dir = src_dirs[exp]
        pickle_file = pickle_files[exp]
        if not os.path.exists(pickle_file):
            dfall = load_data(src_dir)
            with open(pickle_file, 'wb') as f:
                pickle.dump(dfall, f)
        else:
            with open(pickle_file, 'rb') as f:
                dfall = pickle.load(f)
        stats = dfall.agg(['mean', 'std']).transpose()
        stats.to_csv('{}.txt'.format(exp))
        error_labels = ['adjusted speed - drifter speed [m/s]',
                        'adjusted speed relative error',
                        'ocean speed - drifter speed [m/s]',
                        'ocean speed relative error']
        error_vars = [
            dfall['speed_adjusted_error'].values,
            np.abs(dfall['speed_adjusted_error'].values)/dfall['speed_drifter'].values,
            dfall['speed_ocean_error'].values,
            np.abs(dfall['speed_ocean_error'].values)/dfall['speed_drifter'].values]
        titles = ['adjusted', 'adjusted_percent', 'ocean', 'ocean_percent']
        for error_label, error_var, title in zip(error_labels, error_vars, titles):
            if 'relative' in error_label:
                vmin = 0
                vmax = 2
                bins = np.arange(vmin, vmax+.2, .2)
                cmap='inferno_r'
            else:
                vmin = -1
                vmax = 1
                bins = np.arange(vmin, vmax+.1, .1)
                cmap='RdBu_r'
            fig, ax = plt.subplots(1, 1, figsize=(15,5))
            mesh = plot_error_map(dfall, ax, error_var,
                                  gridsize=GS, mincnt=MN, vmin=vmin, vmax=vmax,
                                  cmap=cmap)
            cbar = plt.colorbar(mesh, ax=ax)
            cbar.set_label(error_label, fontsize=FS)
            cbar.ax.tick_params(labelsize=FS-2)
            ax.set_title(model, fontsize=FS)
            fig.savefig('figures/{}-{}.png'.format(exp, title), bbox_inches='tight')
            fig, ax = plt.subplots(1,1)
            plot_histogram(error_var, ax, bins=bins)
            ax.set_xlabel(error_label)
            ax.set_title(model)
            fig.savefig('figures/hist_{}-{}.png'.format(exp, title), bbox_inches='tight')
        # Data density plots
        fig, ax = plt.subplots(1, 1, figsize=(15,5))
        mesh = plot_density_map(dfall, ax, gridsize=GS, mincnt=MN)
        cbar = plt.colorbar(mesh, ax=ax)
        cbar.set_label('Number of data points', fontsize=FS)
        cbar.ax.tick_params(labelsize=FS-2)
        ax.set_title(model, fontsize=FS)
        fig.savefig('figures/{}-density.png'.format(exp), bbox_inches='tight')
        # All tracks
        if exp == 'TREX-CIOPSEv2-relocatable1km':
            continue
        fig, ax = plt.subplots(1, 1, figsize=(15,5))
        plot_tracks(dfall, ax)
        ax.set_title('2020 MEOPAR TReX Drifters', fontsize=FS)
        fig.savefig('figures/TREX-drifters.png', bbox_inches='tight')        


def plot_histogram(var, ax, bins=np.arange(-1,1.2,.2)):
    ax.hist(var, bins=bins)
    ax.grid()

    
def plot_density_map(df, ax, lon_min=-69, lat_min=48, lon_max=-61, lat_max=51,
                     cmap='magma_r', latstep=1, lonstep=2,
                     gridsize=100, mincnt=10):
    m =  Basemap(llcrnrlon=lon_min, llcrnrlat=lat_min,
                 urcrnrlon=lon_max, urcrnrlat=lat_max,
                 projection='merc', resolution='h', ax=ax)
    x, y = m(df.lon.values, df.lat.values)
    mesh = m.hexbin(x, y, cmap=cmap, gridsize=gridsize, mincnt=mincnt, bins='log')
    m.drawcoastlines()
    m.drawmeridians(np.arange(lon_min, lon_max, lonstep),
                    labels=[False, False, False, True],
                    fontsize=FS)
    m.drawparallels(np.arange(lat_min, lat_max, latstep),
                    labels=[True, False, False, False],
                    fontsize=FS)
    return mesh
    
        
def plot_error_map(df, ax, error_var,
                   lon_min=-69, lat_min=48, lon_max=-61, lat_max=51,
                   cmap='RdBu_r', vmin=-1, vmax=1, latstep=1, lonstep=2,
                   gridsize=100, mincnt=10):
    m =  Basemap(llcrnrlon=lon_min, llcrnrlat=lat_min,
                 urcrnrlon=lon_max, urcrnrlat=lat_max,
                 projection='merc', resolution='h', ax=ax)
    x, y = m(df.lon.values, df.lat.values)
    mesh = m.hexbin(x, y, C=error_var, cmap=cmap,
                    vmin=vmin, vmax=vmax, gridsize=gridsize, mincnt=mincnt)
    m.drawcoastlines()
    m.drawmeridians(np.arange(lon_min, lon_max, lonstep),
                    labels=[False, False, False, True],
                    fontsize=FS)
    m.drawparallels(np.arange(lat_min, lat_max, latstep),
                    labels=[True, False, False, False],
                    fontsize=FS)
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


def plot_tracks(df, ax,
                lon_min=-69, lat_min=48, lon_max=-61, lat_max=51,
                latstep=1, lonstep=2):
    m =  Basemap(llcrnrlon=lon_min, llcrnrlat=lat_min,
                 urcrnrlon=lon_max, urcrnrlat=lat_max,
                 projection='merc', resolution='h', ax=ax)
    
    groups = df.groupby('buoyid')
    for name, g in groups:
        x, y = m(g.lon.values, g.lat.values)
        m.plot(x,y,'-')
        m.plot(x[0], y[0], 'g.')
    m.drawcoastlines()
    m.drawmeridians(np.arange(lon_min, lon_max, lonstep),
                    labels=[False, False, False, True],
                    fontsize=FS)
    m.drawparallels(np.arange(lat_min, lat_max, latstep),
                    labels=[True, False, False, False],
                    fontsize=FS)


if __name__ == '__main__':
    main()
