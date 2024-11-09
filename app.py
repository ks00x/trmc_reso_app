import numpy as np
import io
import base64

# a few custom files are used here:
import textdata
from trmc_network import S11ghz
from curvefit_ks import curve_fit

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import trmcapp_help
import streamlit_param as stp


st.set_page_config(layout='wide',initial_sidebar_state='collapsed',page_title='TRMC cavity resonance calculator',page_icon='📶')
session = st.session_state
__version__ = 1.02


# ''''
# this is for streamlit version >= 1.12 using session
# changes to @cache for version 1.20

# git push hzb HEAD:master

# '''




def s11_func(freq_ghz,d1,d2,d_iris,loss_fac,copper_S,layer_t,layer_epsr,layer_sig,sub_t,sub_epsr,sub_sig):
    # helper function for fitting
    global s11
    s11.d1 = d1 #first distance in mm, distance between sample and cavity end
    s11.d2 = d2 # 'complementary' distance in mm
    s11.d_iris=d_iris # iris diameter in mm
    s11.loss_fac=loss_fac #copper loss adjustment 
    s11.layer_t=layer_t # layer thickness in mm
    s11.layer_epsr=layer_epsr #dieelectric constant layer
    #s11.layer_sig = layer_sig # conductance layer S/m
    s11.layer_sig = abs(layer_sig) # conductance layer S/m
    s11.sub_t=sub_t # substrate thickness in mm
    s11.sub_epsr=sub_epsr # substrate (quartz) epsr  
    s11.sub_sig = abs(sub_sig)
    s11.copper_S = abs(copper_S)
    # return np.array([s11.calc(x) for x in freq_ghz]) # freq_ghz is an array! , non numpy version   
    return s11.calc(freq_ghz) 



def download_link(xdata,ydata,params,fname,container,text='download'):

    s = '# trmcapp microwave cavity model\n# frequency in GHz\n'
    for p in params:
        s += f"# {p['name']} = {p['val']}, fixed = {p['fixed']}\n"
    for x,y in zip(xdata,ydata):
        s += f'{x:.6} {y:.6}\n'
    bin_str = base64.b64encode(s.encode()).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{fname}">{text}</a>'
    container.write(href, unsafe_allow_html=True)


def show_help():
    st.button('return')
    st.markdown(trmcapp_help.help)

def show_source():
    st.button('return')
    st.markdown('trmc_network.py:')
    with open('trmc_network.py','rt') as fp:
        scode = '```' + fp.read() + '```'
        st.markdown(scode)


def main():

    def do_fit():
        if len(extdata) > 1: 
            try:
                c.fit(extdata[:,0],extdata[:,1])            
                yfit = c.calc(extdata[:,0])  
                session['fit_y'] = yfit
                session['fit_chi2'] = ((yfit - extdata[:,1])**2).sum()        
            except RuntimeError:
                st.error('fit did fail!')
            session['fit_done'] = True                                  
        else : 
            session['fit_done'] = False   

    def do_kfac():         
        if kfac_min:
            k = y.argmin()
            session['kfreq'] = f[k]        
        s11.layer_sig = kfac_sigma
        session['kfac'] = s11.kfactor(session['kfreq'],rel_change=0.01)         

    @st.cache_data()
    def load_data(datastream):        
        if datastream is not None: # process uploaded file            
            datastream.seek(0)        
            buf = datastream.read()
            buf = io.BytesIO(buf)
            stream = io.TextIOWrapper(buf)        
            data = textdata.read_textdata(stream)
            data = np.array(data['data']) 
            if session.frequnit == "Hz" :
                data[:,0] = data[:,0] / 1e9
            elif session.frequnit == "MHz" :
                data[:,0] = data[:,0] / 1e3            
            return data  
        else : 
            return []        

    def reset_values():
        del session.app_init

   
    # set the order of gui elements by defining containers:
    lcol,rcol = st.columns((1,3))
    area_graph = rcol.container()
    area_info = lcol.container()
    area_kfac = st.container()    
    datastream = lcol.file_uploader(f'ascii 2 column f in {session.frequnit}',help='ascii 2 column (f,S) tab data')    
    
    area_control = st.container()                 
    extdata = load_data(datastream)
    lcol.button('reset values',on_click=reset_values)
    if datastream:
            btn_fit = lcol.button('fit model',on_click=do_fit)
    with area_control :                
        st.markdown('**parameters:**')
        session.plobj.create(c._plist[1:],st,format='%1.5g')
        c._calc_reduced()
        #session.cfit = c
        f = np.arange(fmin,fmax,fstep)
        y = c.calc(f)
        download_link(f,y,c._plist[1:],'trmcapp.txt',area_info,'download ascii')

    with area_kfac :        
        kfe = st.expander('k-factor calculation')
        kf  = kfe.form('kfacform')
        kc = kf.columns(4)
        btn_kfac = kc[0].form_submit_button('calc',on_click=do_kfac)
        kfac_min = kc[1].checkbox('use min?',value=True,key='kfac_min')     
        kc[2].number_input('freq in GHz',format='%1.4f',key='kfreq')               
        kfac_sigma = kc[3].number_input('layer sigma [S/m]',value=0.1,format='%1.4f')        
        if btn_kfac:
            st.markdown(f'k-factor @{session.kfreq:1.4}GHz is : {session.kfac}')
    
    fig = px.line(x=f,y=y,log_y=False,title='trmc resonance curve',labels={'x':'frequency GHz','y':'S11 reflectivity'},height=im_height,width=im_width)
         
    if len(extdata) > 1:                
        fig.add_trace(go.Scatter(x=extdata[:,0], y=extdata[:,1],
            mode='markers',
            name='data'),
                )
    if session['fit_done'] :                              
        fig.add_trace(go.Scatter(x=extdata[:,0], y=session['fit_y'],
        mode='markers',
        name='fit'),
            )
        chisqr = session['fit_chi2']                      
        results = area_info.expander(f'fit results (chisqr = {chisqr:1.3})')
        results.write(c.plist)
    
    area_graph.plotly_chart(fig)            
   
    
##################### init sequence #########################

# sidebar config
with st.sidebar :
    st.header(f'trmcapp V{__version__}\n')
    help = st.button('Help')
    source = st.button('show source code')
    st.selectbox('data frequency units',['Hz','MHz','GHz'],index=1,key="frequnit")
    im_width = st.number_input('image width',value=800)
    im_height = st.number_input('image height',value=400)
    param_cols = st.number_input('nr of parameter columns',value=2)
    btn_reset = st.button("reset",help="reset cache and return to default values")
    st.write('### resonance plot:')
    fmin = st.number_input('fmin',value=8.2,format='%1.4f')
    fmax = st.number_input('fmax',value=9.2,format='%1.4f')    
    fstep = st.number_input('step',value=0.001,format='%1.4f')

session.plobj = stp.paramlist(cols=param_cols)

if 'app_init' not in session or btn_reset:
    session['app_init'] = True
    s11 = S11ghz()
    c = curve_fit(s11_func)
    c.set('d1',35.825,True)
    c.set('d2',11,True)
    c.set('d_iris',9.6,False)
    c.set('loss_fac',1e-7,False)
    c.set('copper_S',5.5e7,True)
    c.set('layer_t',0.001,True)
    c.set('layer_epsr',1,True)
    c.set('layer_sig',0,True)
    c.set('sub_t',1,True)
    c.set('sub_epsr',1,False)
    c.set('sub_sig',0,True)
    session['s11'] = s11
    session['cfit'] = c
    session['fit_done'] = False        
else :
    s11 =  session['s11']
    c = session['cfit']


if help : show_help()
elif source : show_source()
else: main()