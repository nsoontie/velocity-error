"""
Module to calculate velocity errors
Nancy Soontiens
"""

import numpy as np
import xarray as xr


def process_drifter(d):
    """Add the following variables to this drifter dataset:
    speed_drifter
    speed_ocean
    [speed_atmos]
    bearing_drifter
    bearing_ocean
    [bearing_atmos]
    [ueast_adjusted]
    [vnorth_adjusted]
    [speed_adjusted]
    [bearing_adjusted]
    Variables in square brackets are only added if winds were used in 
    correction calculations.

    Errors and vector differences are also added.
    """

    if 'alpha_real' in d.variables:
        adjusted = calculate_adjusted_current(d)
        d['ueast_adjusted'] = xr.DataArray(adjusted.real, dims=('time'))
        d['vnorth_adjusted'] = xr.DataArray(adjusted.imag, dims=('time'))
    d = append_speed_and_bearing(d)
    d = append_errors(d)
    return d


def calculate_adjusted_current(d):
    """Calculate an adjusted current adjusted = ocean + mean(alpha)*atmos"""
    vector_ocean = []
    vector_atmos = []
    mean_alpha = complex(d['alpha_real'].mean(), d['alpha_imag'].mean())
    n = len(d['ueast_ocean'])
    for i in range(n):
        vector_ocean.append(complex(d['ueast_ocean'][i], d['vnorth_ocean'][i]))
        vector_atmos.append(complex(d['ueast_atmos'][i], d['vnorth_atmos'][i]))
    adjusted = np.array(vector_ocean) + mean_alpha * np.array(vector_atmos)
    return adjusted

        
def append_speed_and_bearing(d):
    """Add speed and bearing to dataset"""
    types = ['ocean', 'drifter']
    if 'ueast_atmos' in d.variables:
        types.append('atmos')
    if 'ueast_adjusted' in d.variables:
        types.append('adjusted')
    for t in types:
        d['speed_{}'.format(t)] = magnitude(d['ueast_{}'.format(t)],
                                            d['vnorth_{}'.format(t)])
        bearing = calculate_bearing(d['ueast_{}'.format(t)],
                                    d['vnorth_{}'.format(t)])
        d['bearing_{}'.format(t)] = xr.DataArray(bearing, dims=('time'))
    return d

          
def append_errors(d):
    """Append errors for the drifter dataset. The following errors are calculated:
    speed_ocean_error
    bearing_ocean_error
    [speed_adjusted_error]
    [bearing_adjusted_error]
    ueast_ocean_vdiff
    vnorth_ocean_vdiff
    [ueast_adjusted_vdiff]
    [vnorth_adjusted_vdiff]
    Items in brackets are only added if winds were used in correction computations.
    """
    types = ['ocean',]
    if 'bearing_adjusted' in d.variables:
        types.append('adjusted')
    for t in types:
        # Bearing error
        diff = d['bearing_{}'.format(t)] - d['bearing_drifter']
        diff[diff>180] = diff[diff>180]-360
        diff[diff<-180] = diff[diff<-180]+360
        d['bearing_{}_error'.format(t)] = diff
        # Speed error
        d['speed_{}_error'.format(t)] = d['speed_{}'.format(t)] - d['speed_drifter']
        # Vector difference
        d['ueast_{}_vdiff'.format(t)] = d['ueast_{}'.format(t)] - d['ueast_drifter']
        d['vnorth_{}_vdiff'.format(t)] = d['vnorth_{}'.format(t)] - d['vnorth_drifter']
    return d


def calculate_bearing(east, north):
    """Calculate the bearing of a vector"""
    radians = np.arctan2(east, north)
    degrees = radians*180./np.pi
    degrees[degrees<0] = degrees[degrees<0] +360
    return degrees


def magnitude(x, y):
    """Calculate the magnitude of a vector"""
    return np.sqrt(x**2 + y**2)

