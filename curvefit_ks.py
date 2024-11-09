from fixparameter import fixparameter
import numpy as np
import scipy.optimize as opt
from copy import deepcopy

class curve_fit(fixparameter):
    '''
    curve_fit is an interface to scipy.opt.curve_fit that enables a more
    convinient handling of the fit parameter, including fixing parameters
    '''
    def __init__(self,func): # func is required!
        super().__init__(func)
    
    def calc(self,xdata):
        x = super().plist
        x[0]['val'] = xdata
        x = super().predlist
        y = super().func(*x)
        return(y)
    
    def fit(self,xdata,ydata,sigma=None,absolute_sigma=False,method=None,bounds=(-np.inf,np.inf),maxfev=600,**kwargs):
        # method{‘lm’, ‘trf’, ‘dogbox’}, optional
        
        p = super().plist
        p[0]['val'] = xdata
        p[0]['fixed'] = False
        p = super().predlist
        params, err_est = opt.curve_fit(super().func, xdata, ydata,p[1:],
            sigma=sigma,absolute_sigma=absolute_sigma,method=method,maxfev=maxfev,bounds=bounds,**kwargs)
        k = 0
        for x in super().plist[1:]:
            if not x['fixed']:
                x['val'] = params[k]
                k += 1        
        return params, err_est
    
    @property
    def plist(self):        
        return(super().plist[1:])
    
    @property
    def plist_values(self):
        'return a parameter list for the reduced function'
        return [p['val'] for p in super().plist][1:]
    
    def copy(self):
        x = deepcopy(self)
        return x
    
    def __repr__(self):        
        s = ''
        for p in super().plist[1:]:
            for k,v in p.items():
                s += f"{k:5} = {v}\n"
            s += '\n'
        return(s)
 

if __name__ == "__main__":

    import numpy as np
    
    def lorentzian(x,x0=0,fwhm=1):
        arg = 2*(x-x0)/fwhm
        return( 1/(1+arg*arg) )

    def rfres(f,f0=8,fwhm=0.01,r0=0.5):
        ret = 1 - (1-r0)*lorentzian(f,f0,fwhm)    
        return( ret )

    # parameters are accessed by their names as defined in the function, here rfres()
    # the curve_fit class treats the first parameter f in rfres (x data array), seperately.
    # the fit function must always have the 1 parameter be the x-data array
    c = curve_fit(rfres)
    
    c.set('f0',8.5,False)
    c.set('fwhm',0.02,False)
    c.set('r0',0.6,False)
    f = np.arange(8,9,0.002)
    
    mu, sigma = 0, 0.01 # testdata with noise - mean and standard deviation
    noise = np.random.normal(mu, sigma, len(f))
    testdata = c.calc(f) + noise

    g = c.copy() # we make a copy to have the original parameter set avaialable
    g.set('f0',8.5,False)
    g.set('fwhm',0.05,True) # this parameter is not fitted (fixed)
    g.set('r0',0.2,False)
    c.r0 = 0.4 # use the attribute interface...

    g.fit(f,testdata) #do the fitting!
    print('fitted parameters:\n')
    print(g)
    y = g.calc(f) #calculate the fit function with the fitted parameters
    dy = (y-testdata)**2
    #print(f'chisqr = {dy.sum()/(len(dy)-1)}') 
    print(f'chisqr = {dy.sum()}') 


    #g.plist_values

    