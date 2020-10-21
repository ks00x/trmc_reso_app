'''
a bunch of small helper functions for physics engenering problems
'''
import scipy.constants as sc
import math
import numpy as np

def number_of_photons(power_in_W=1,wavelength_in_m=540e-9) :
    '''number of photons/s calculated from light power and wavelength'''
    return( power_in_W*wavelength_in_m/(sc.h*sc.c))



def nm_to_eV(wl_in_nm) :
    return( sc.h*sc.c/(wl_in_nm*1e-9*sc.e) )

def eV_to_nm(ev) :
    return(  sc.h*sc.c/(ev*sc.e)*1e9 )

def lorentzian(x,x0=0,fwhm=1):
    'lorentzian line profile with ampltidue 1, position  x0 and width fwhm'
    arg = 2*(x-x0)/fwhm
    return( 1/(1+arg*arg) )


def log_range(start,stop,pts_per_decade,endpoint=True):
    a = math.log10(start)
    b = math.log10(stop)
    if endpoint:
        x = 10**np.arange(a,b,1.0/pts_per_decade)        
        return(  np.append(x,stop) )
    else:
        return( 10**np.arange(a,b,1.0/pts_per_decade) )

