import math
import cmath
import numpy as np

'''
original IGOR script function from Tom Savenije group transcribed to a Python class
by Klaus Schwarzburg 2020

The parameter array in the original script:
w[0]    : copper loss factor 
w[1]    : iris diameter in mm
w[2]    : 'd1' distance between iris and sample in mm
w[3]    : eps layer
w[4]    : conductance layer
w[5]    : layer thickness in mm
w[6]    : 'd2' 'complementary length (sample - cavity end) mm
w[7]    : substrate thickness mm
w[8]    : substrate eps
w[9]    : substrate conductivity

The following paper from the ancestors of the present Delft group 
describe the impedance modeling used here. However their paper does not present
the complete formulas for the cavity stack of this model.

Infelta, P. P., de Haas, M. P., & Warman, J. M. (1977). 
The study of the transient conductivity of pulse irradiated dielectric liquids on a nanosecond timescale using microwaves. Radiation Physics and Chemistry, 10(5–6), 353–365. 
https://doi.org/10.1016/0146-5724(77)90044-9


This book seems to contain all or at least most of the details
Marcuvitz, N.; Laboratory, M. I. of T. R. Waveguide Handbook; IET, 1951.     

'''

class S11ghz():

    def __init__(self):
        'default parameters for TRMC X-band (WR-90) cavity'
        'note that the substrate/layer thickness adds to the total cavity length!'
        'L-cavity = d1 + d2 + sub_t + layer_t'
        self.a = 22.86          # long side of waveguide in mm 
        self.b = 10.16          # short side of waveguide in mm 
        self.d1 = 36            # first distance in mm, distance between sample and cavity end
        self.d2 = 12            # 'complementary' distance in mm
        self.d_iris =  9.6      # iris diameter in mm, making this large (>=100) practically removes the iris 
        self.copper_S = 5.5e7   # copper conductivity
        self.loss_fac = 1e-7    # copper loss adjustment 
        self.layer_t = 0.001    # layer thickness in mm
        self.layer_epsr = 1     # dieelectric constant layer
        self.layer_sig = 0      # conductance layer S/m
        self.sub_t = 1          # substrate thickness in mm
        self.sub_epsr = 3.6     # substrate (quartz) epsr
        self.sub_sig = 0        # substrate (quartz) sigma S/m
              
    def _prop(self,adm,gd):
        'internal helper function, numpy version'
        return( (np.tanh(gd) + adm) / (1 + adm*np.tanh(gd)) )
    
    def calc(self,freq_in_ghz): 
        'calculates the normalized reflected RF power'
        s = self._calc(freq_in_ghz)
        return( (s * s.conjugate()).real )

    def _calc(self,freq_in_ghz): 
        'calculates the complex S11 parameter, numpy version' 
        'freq_in_ghz : numpy array or scalar'       

        # d2 = self.d2 - self.sub_t # the original formula assumes a stack, so that increasing the substrate thickness increases the total cavity length
        d2 = self.d2
        pi = math.pi
        mu0 = pi*4e-7
        a = self.a / 1000.0 # long side of waveguide in m        
        eps0 = 8.842e-12
        sc = self.copper_S # copper conductivity        
        c = 1/math.sqrt(eps0*mu0)
        om = 2e9*pi*freq_in_ghz # angular frequency

        # iris impedance
        tmp = np.sqrt((om/c)**2 - (pi/a)**2) + 0j
        b_iris = 1.5*a*a/(self.d_iris/1000)**3 / tmp

        tmp = (pi*c/a/om)**2 +0j
        loss = self.loss_fac * np.sqrt(2*eps0*om*sc)/a * (1+tmp)/np.sqrt(1-tmp)

        # cavity end part
        gsq  = (pi/a)**2 - (om/c)**2 + 0j
        gair = np.sqrt(gsq) +  loss + 0j
        yrel = 1/np.tanh(gair*self.d1/1000)

        # layer impedance
        gsq = (pi/a)**2-self.layer_epsr*(om/c)**2 + (self.layer_sig*om*mu0) * 1j
        glayer = np.sqrt(gsq) + loss
        yrel *= gair/glayer
        yrel = self._prop(yrel,glayer*self.layer_t/1000)

        # substrate impedance
        gsq = (pi/a)**2-self.sub_epsr*(om/c)**2 + (self.sub_sig*om*mu0) * 1j
        gquartz = np.sqrt(gsq) + loss
        yrel *= glayer/gquartz
        yrel = self._prop(yrel,gquartz*self.sub_t/1000)

        # iris cavity part
        yrel *= gquartz/gair
        yrel = self._prop(yrel,gair*d2/1000)
        yrel -= b_iris*1j
        ret = (1-yrel)/(1+yrel)
        return( ret )
    
    def _prop_nonp(self,adm,gd):
        'internal helper function'
        return( (cmath.tanh(gd) + adm) / (1 + adm*cmath.tanh(gd)) )    
    
    def _calc_nonumpy(self,freq_in_ghz): 
        '''
        calculates the complex S11 parameter
        original version  without numpy (~ 10x slower)
        '''
        #d2 = self.d2 - self.sub_t # the original formula assumes a stack, so that increasing the substrate thickness increases the total cavity length
        d2 = self.d2
        pi = math.pi
        mu0 = pi*4e-7
        a = self.a / 1000.0 # long side of waveguide in m        
        eps0 = 8.842e-12
        sc = self.copper_S #copper conductivity        
        c = 1/math.sqrt(eps0*mu0)
        om = 2e9*pi*freq_in_ghz # angular frequency

        tmp = math.sqrt((om/c)**2 - (pi/a)**2)
        b_iris = 1.5*a*a/(self.d_iris/1000)**3 / tmp

        tmp = (pi*c/a/om)**2
        loss = self.loss_fac * math.sqrt(2*eps0*om*sc)/a * (1+tmp)/math.sqrt(1-tmp)

        # cavity end part
        gsq  = (pi/a)**2 - (om/c)**2
        gair = cmath.sqrt(gsq) +  loss
        yrel = 1/cmath.tanh(gair*self.d1/1000)

        # layer impedance
        gsq = complex((pi/a)**2-self.layer_epsr*(om/c)**2 , self.layer_sig*om*mu0)
        glayer = cmath.sqrt(gsq) + loss
        yrel *= gair/glayer
        yrel = self._prop_nonp(yrel,glayer*self.layer_t/1000)

        # substrate impedance
        gsq = complex((pi/a)**2-self.sub_epsr*(om/c)**2 , self.sub_sig*om*mu0)
        gquartz = cmath.sqrt(gsq) + loss
        yrel *= glayer/gquartz
        yrel = self._prop_nonp(yrel,gquartz*self.sub_t/1000)

        # iris cavity part
        yrel *= gquartz/gair
        yrel = self._prop_nonp(yrel,gair*d2/1000)
        yrel -= complex(0 , b_iris)
        ret = (1-yrel)/(1+yrel)
        return( ret )
    
    def kfactor(self,freq_in_ghz,rel_change = 0.01): 
        'calculate the k-factor using the current layer conductivity and solving for an incremental increase'
        beta = self.a / self.b
        #beta = 2.24
        tmp = self.layer_sig
        back = self.layer_sig
        if back == 0.0 :
            back = 1    
        t_in_m = (self.layer_t*1e-3)
        r0 = self.calc(freq_in_ghz)        
        self.layer_sig *= (1 + rel_change) # increase the conductance
        dg = (self.layer_sig - back) * t_in_m # change in conductivity
        r1 = self.calc(freq_in_ghz)        
        self.layer_sig = tmp
        kfac  = (r1-r0)/(r0*dg*beta)
        return( kfac )

    def kfactor_abs(self,freq_in_ghz,delta_sig=0.1): 
        'calculate the k-factor using the current layer conductivity and solving for an incremental increase'
        beta = self.a / self.b
        #beta = 2.24  
        tmp = self.layer_sig      
        t_in_m = (self.layer_t*1e-3)
        r0 = self.calc(freq_in_ghz)        
        self.layer_sig += delta_sig # increase the conductance
        dg = delta_sig * t_in_m # change in conductivity
        r1 = self.calc(freq_in_ghz)        
        self.layer_sig = tmp
        kfac  = (r1-r0)/(r0*dg*beta)
        return( kfac )





def kfactor_simple(f0,fwhm,R0,c_l=0.048,c_w=0.0229,c_h=0.0102):    
    '''
    simple analytica formula for rf cavity k factor
    all values in SI units HZ,m ...
    '''
    eps0 = 8.854e-12
    epsr = 1 # air or medium
    pi = 3.14159265359    
    Q =  f0/fwhm    
    d = c_l
    a = c_w
    b = c_h
    return (2*Q*(1+1/R0**0.5))/(pi*f0*eps0*epsr*d*a/b)


class S11ghz_Ka(S11ghz):
    def __init__(self):
        'just different dimensions Ka Band (WR28) 21-42GHz'
        super().__init__()        
        self.a = 7.112
        self.b = 3.556
        self.d1 = 1 #first distance in mm, distance between sample and cavity end
        self.d2 = 25 # 'complementary' distance in mm
        self.d_iris= 3.5 # iris diameter in mm
    
if __name__ == "__main__":
    
    
    import numpy as np
    #from trmc_network import S11ghz
    import matplotlib.pyplot as plt


    f = np.arange(8.1,9.2,0.001)
    #f = np.arange(25,40,0.01)

    s = S11ghz()

    s.a = 22.86          # long side of waveguide in mm 
    s.b = 10.16          # short side of waveguide in mm 
    s.d1 = 36            # first distance in mm, distance between sample and cavity end
    s.d2 = 12            # 'complementary' distance in mm
    s.d_iris =  9.6      # iris diameter in mm, making this large (>=100) practically removes the iris 
    s.copper_S = 5.5e7   # copper conductivity
    s.loss_fac = 1e-7    # copper loss adjustment 
    s.layer_t = 0.001    # layer thickness in mm
    s.layer_epsr = 1     # dieelectric constant layer
    s.layer_sig = 0.1      # conductance layer S/m
    s.sub_t = 1          # substrate thickness in mm
    s.sub_epsr = 3.6     # substrate (quartz) epsr
    s.sub_sig = 0        # substrate (quartz) sigma S/m


    print(vars(s))    
    s11 = s.calc(f)        
    k = s11.argmin()

    print(f[k])

    print(f'k-factor = {s.kfactor(f[k])}')
    