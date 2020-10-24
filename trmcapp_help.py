
help = r'''

# TRMC app help

   
Klaus Schwarzburg 2020, Helmholtz Zentrum Berlin      

original IGOR script function from Tom Savenije's group transcribed to a Python class   
   
The model describes a 2-layer sample stack inside a microwave cavity. The 2 sample layers are refered to as substrate and sample layer. From the modeling side, both are represented by the same model and parameters: a thickness, a dieelectric contant and a conductivity. A typical example is a thin conducting layer on a thick glass substrate. By setting on of the layers to thickness=0, the model reduces to a 1 layer model.    

The k-factor is calculated with the formulas below and by setting the 'layer' conductivity to the given value and changing it by 1% to create a $\Delta$G.

### usage tips
* a 'fixed' model parameter is held contant during the fit
* The default widget size is a bit 'Fisher Price' like... Decrease your browser windows zoom to make the widgets smaller (ctrl +/- or ctrl-mousewheel)
* change the plot graph size in the sidebar
* the plot is interactive and you can zoom in out and out and pan
* the plot can be maximized: There is a 'fullscreen' tool at the very right side when you hover over the plot!
* after a fit you can expand the fit results paragraph as text and can copy it
* do a browser page reload (F5) to reset all parameters!


 


### default parameters for TRMC X-band (WR-90) cavity   
note that the substrate/layer thickness adds to the total cavity length!   
L-cavity = d1 + d2 + sub_t + layer_t         
a = 22.86          # long side of waveguide in mm    
b = 10.16          # short side of waveguide in mm    
d1 = 36            # first distance in mm, distance between sample and cavity end   
d2 = 12            # 'complementary' distance in mm   
d_iris =  9.6      # iris diameter in mm, making this large (>=100) practically removes the iris    
copper_S = 5.5e7   # copper conductivity   
loss_fac = 1e-7    # copper loss adjustment    
layer_t = 0.001    # layer thickness in mm   
layer_epsr = 1     # dieelectric constant layer   
layer_sig = 0      # conductance layer S/m   
sub_t = 1          # substrate thickness in mm   
sub_epsr = 3.6     # substrate (quartz) epsr   
sub_sig = 0        # substrate (quartz) sigma S/m   
   
The parameter array in the original script:   
w[0]    : copper loss factor    
w[1]    : iris diameter in mm   
w[2]    : 'd1' distance between iris and sample in mm   
w[3]    : eps layer   
w[4]    : conductivity layer [S/m]  
w[5]    : layer thickness in mm   
w[6]    : 'd2' 'complementary length (sample - cavity end) mm   
w[7]    : substrate thickness mm   
w[8]    : substrate eps   
w[9]    : substrate conductivity [S/m]   

The following paper from the ancestors of the present Delft group
describe the impedance modeling used here. However their paper does not present
the complete formulas for the cavity stack of this model.   

Infelta, P. P., de Haas, M. P., & Warman, J. M. (1977).    
The study of the transient conductivity of pulse irradiated dielectric liquids on a nanosecond timescale using microwaves. Radiation Physics and Chemistry, 10(5–6), 353–365. 
https://doi.org/10.1016/0146-5724(77)90044-9   


This book seems to contain all or at least most of the details:   
https://ia800308.us.archive.org/24/items/WaveguideHandbook/Marcuvitz-WaveguideHandbook.pdf





## k factor calculation

### Conversion of detector voltage to rf reflection coefficient dP/P
   
The power is roughly a quadratic function of the RF detector voltage (n~2):  

$$
P=a V^n
$$   

In the dark, the detector voltage is Vo. We make a Taylor expansion at V=Vo:  

$$
P(V_{0}+\Delta V) = P(V_{0}) + a n V_{0}^{n-1} \Delta V
$$   
   
$$
\Delta P(V_{0}+\Delta V) = a n V_{0}^{n-1} \Delta V
$$   
   
Finally we get:   

$$
\frac{\Delta P(V_{0}+\Delta V)}{P(V_{0})} =  \frac{a n V_{0}^{n-1} \Delta V}{a V_{0}^{n} } = n \frac{\Delta V}{V_{0}}
$$


### calculating conductivity $\sigma$ and conductance G from the laser pulse energy density $P_{L}$   

The semiconductor sample may be homogenously illuminated by lightpulses with a energy density $P_{L}$ given in units of J/cm2. The sample fills the cavity with dimensions b = 10.2mm and a = 22.9mm (X-band) and it has a thickness of d. The RF electric field oscillates in the direction of the shorter side (b). If we assume that all photons having a wavelength $\lambda$ are absorbed, a carrier density of $\Delta N$ is created:

$$
\Delta N = \frac{P_{L} \lambda}{h c} \frac{1}{d}
$$   

With c=speed of light and h Plancks constant. The increase charge carrier count corresponds to a change in conductivity:

$$
\Delta\sigma = e \Delta N (\mu_{e} + \mu_{h})
$$   

With $\mu_{e} , \mu_{h}$ mobility of electrons and holes and e the elementary charge. To calculate the total conductance change $\Delta G$ the RF E-field is seeing, we need the area A perpendicular to the Field and thickness L of the sample in the direction of E:

$$
\Delta G = \Delta\sigma \frac{A}{L}
$$   

With A = a*d and L=b we get:

$$
\Delta G = \Delta\sigma \frac{a}{b} d = \Delta\sigma \beta d
$$   

With $\beta = a/b$ (=2.245 for X band)



### k - factor    

The sensitivty k-factor is defined by:

$$
k = \frac{\frac{\Delta P}{P}}{\Delta G}
$$   

With the formulas from above we can express this via measureable quantities and with a well defined reference sample with known mobility we can calculate k:

$$
k = \Delta V \frac{n}{V_{0}} \times \frac{h c}{\beta e (\mu_{e} + \mu_{h}) } \times \frac{1}{P_{L} \lambda}
$$

If k is known , we can caclulate the sum of mobilities:

$$
(\mu_{e} + \mu_{h}) = \Delta V \frac{n}{V_{0}} \times \frac{h c}{\beta e } \times \frac{1}{P_{L} \lambda} \times \frac{1}{k}
$$




'''