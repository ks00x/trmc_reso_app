
help = r'''

# TRMC app help

   
Klaus Schwarzburg 2020, Helmholtz Zentrum Berlin      

original IGOR script function from Tom Savenije's group transcribed to a Python class 

Web Ui made with streamlit: https://www.streamlit.io/

   
The model describes a 2-layer sample stack inside a microwave cavity. The 2 sample layers are refered to as substrate and sample layer. From the modeling side, both are represented by the same model and parameters: a thickness, a dieelectric contant and a conductivity. A typical example is a thin conducting layer on a thick glass substrate. By setting one of the layers to thickness=0, the model reduces to a 1 layer model.    

The k-factor is calculated with the formulas below and by setting the 'layer' conductivity to the given value and changing it by 1% to create a $\Delta$G.

### usage tips
* the position of the resonance peak is mainly defined by the cavity dimensions and by the sample/layer dieelectric constant and the thickness of the layers. 
* The conductivity parameters of sample and cavity define the depth and width of the resonance curve
* You can upload your microwave resonance curve for fitting by drag and drop to the upload area or by using the file selector. The format of the file needs to be 2 column text file (think csv,txt) with the first column beeing the frequency values in GHz.
* Before you press fit, make sure that the model function peak has some overlap with the frequency range of your uploaded data! Otherwise the fit is likely to fail.
* a 'fixed' model parameter is held contant during the fit
* The script makes use of a an unofficial session interface of streamlit that has some problems. Sometimes you have to click twice to see the actual result of a calculation. 
* The default widget size is a bit 'Fisher Price' like... Decrease your browser windows zoom to make the widgets smaller (ctrl +/- or ctrl-mousewheel)
* change the plot graph size in the sidebar
* the plot is interactive and you can zoom in out and out and pan
* the plot can be maximized: There is a 'fullscreen' tool at the very right side when you hover over the plot!
* after a fit you can expand the fit results paragraph as text and can copy it
* do a browser page reload (F5) to reset all parameters!

### fitting strategy for thin film on a glass substrate samples
Fitting all model parameters using only the resonance curve for the sample loaded cavity is not a good strategy. It is recommended to do a sequential fit procedure where you first extract the model parameteres related to the microwave cavity itself. Do like the following:    

1. upload the resonance curve for the empty cavity and fit 'loss_fac' and 'd_iris'. If needed try to fit d1 or d2 as well (not both at the same time!). The geometric quantities (d1,d2,d_iris) should not deviate much from the known values. Otherwise there is some issue with the data. 
2. Upload the resonance curve measured with only the (glass) substrate in the cavity and fit the substrate epsilon (sub_epsr). The substrate thickness should be measured precisely and entered as a fixed value (sub_t). sub_sig = 0
3. Upload the sample resonance curve and fit layer conductivty (layer_sig) with all other parameters fixed and layer_t set to the layer thickness. The layer_epsr does not play a role for very thin (<=1um) conductive layers and can be set to 1 or any other resonable value. If this fit works well the measurements seem to be consistent. If not, you may try to fit loss_fac and probably d_iris as well. Be aware however that this indicates that some uncontrolled changes of the cavity happened when you inserted your sample/substrate. 
 


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
Marcuvitz, N.; Laboratory, M. I. of T. R. Waveguide Handbook; IET, 1951.     


Another useful, more recent technical paper is by Reid et al :   
https://iopscience.iop.org/article/10.1088/1361-6463/aa9559/pdf   


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