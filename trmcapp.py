import physbits
import numpy as np
import math
import dataimport as di
import textdata
import pathlib
import io
from trmc_network import S11ghz
from curvefit_ks import curve_fit
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import trmcapp_help
import SessionState


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


def  list_partition(list1D, columns=2):
    l = []    
    for k,p in enumerate(list1D):        
        col = k % columns        
        if col == 0  :            
            l.append([p] + [None]*(columns-1))     
            l[-1][0] = p       
        else :
            l[-1][col] = p
    return l

def parms_list(container,plist,kid=0):
    # creates a 
    cols = 2
    pl = list_partition(plist,cols)
    
    with container:
        ct = [None]*len(pl)
        #kid = 1
        for r,row in enumerate(pl):                    
            ct[r] = st.beta_columns(2*cols)
            plist[r*cols]['val'] = ct[r][0].number_input(row[0]['name'],value=float(row[0]['val']),format='%1.4e',key=kid)
            kid +=1
            plist[r*cols]['fixed'] = ct[r][1].checkbox('fixed',value=row[0]['fixed'],key=kid)
            kid +=1
            if cols>1 and row[1] :
                plist[r*2+1]['val'] = ct[r][2].number_input(row[1]['name'],value=float(row[1]['val']),format='%1.4e',key=kid)
                kid +=1
                plist[r*2+1]['fixed'] = ct[r][3].checkbox('fixed',value=row[1]['fixed'],key=kid)
    return(pl)        


st.beta_set_page_config(layout='wide',initial_sidebar_state='collapsed')

help = st.sidebar.button('Help')
im_width = st.sidebar.number_input('image width',value=800)
im_height = st.sidebar.number_input('image height',value=400)


s11 = S11ghz()
c = curve_fit(s11_func)
c.set('d1',35.825,False)
c.set('d2',11,True)
c.set('d_iris',9.6,False)
c.set('loss_fac',1e-7,False)
c.set('copper_S',5.5e7,True)
c.set('layer_t',0.001,True)
c.set('layer_epsr',1,True)
c.set('layer_sig',0,True)
c.set('sub_t',1,True) # by adding a substrate with eps=1 we account for the proper total cavity length
c.set('sub_epsr',1,True)
c.set('sub_sig',0,True)

# we need the extra session state thing to feed the fitted parameters back  to the widgets
state = SessionState.get(kfreq=8.5,paramlist=c.plist)
c._plist[1:] = state.paramlist
c._calc_reduced()

if help :    
    st.button('return')
    st.markdown(trmcapp_help.help)

else :

    # set the order of gui elements:
    area_graph = st.beta_container()
    area_info = st.beta_container()
    area_kfac = st.beta_container()
    datastream = st.file_uploader('ascii tab data with f in GHz',)    
    area_control = st.beta_container()
    st.markdown('**parameters:**')
    area_parms = st.beta_container() 
    pl = parms_list(area_parms,c.plist,kid=10000)
    c._calc_reduced()

    extdata = []
    if datastream is not None:             
        datastream.seek(0)        
        buf = datastream.read()
        buf = io.BytesIO(buf)
        stream = io.TextIOWrapper(buf)        
        extdata = textdata.read_textdata(stream)
        extdata = np.array(extdata['data'])            

    with area_control :
        c_cols = st.beta_columns(5)
        btn_calc = c_cols[0].button('calculate')
        if datastream:
            btn_fit = c_cols[1].button('fit')
        fmin = c_cols[2].number_input('fmin',value=8.0,format='%1.4f')
        fmax = c_cols[3].number_input('fmax',value=9.2,format='%1.4f')    
        fstep = c_cols[4].number_input('step',value=0.001,format='%1.4f')

    with area_kfac :
        kf = st.beta_expander('k-factor calculation')
        kc = kf.beta_columns(4)
        btn_kfac = kc[0].button('calc')
        kfac_min = kc[1].checkbox('use min?',value=True)        
        kfac_freq = kc[2].number_input('freq in GHz',value=state.kfreq,format='%1.4f')
        kfac_sigma = kc[3].number_input('layer sigma [S/m]',value=1.)
    

    with area_graph:

        if True :        
            f = np.arange(fmin,fmax,fstep)
            y = c.calc(f)
            fig = px.line(x=f,y=y,log_y=False,title='plotly express',labels={'x':'frequency GHz','y':'S11 reflectivity'},height=im_height,width=im_width)
            if len(extdata) > 1:                
                fig.add_trace(go.Scatter(x=extdata[:,0], y=extdata[:,1],
                    mode='markers',
                    name='imported data'),
                     )
                if btn_fit:
                    c.fit(extdata[:,0],extdata[:,1])
                    yfit = c.calc(extdata[:,0])
                    state.paramlist = c.plist
                    fig.add_trace(go.Scatter(x=extdata[:,0], y=yfit,
                    mode='markers',
                    name='fit'),
                     )
                    chisqr = ((yfit - extdata[:,1])**2).sum()
                    results = area_info.beta_expander(f'fit results (chisqr = {chisqr:1.3})')
                    results.write(c.plist)

            st.plotly_chart(fig)            
            if btn_kfac :
                if kfac_min:
                    k = y.argmin()
                    kfac_freq = f[k]
                state.kfreq = kfac_freq                    
                s11.layer_sig = kfac_sigma
                kf = s11.kfactor(kfac_freq,rel_change=0.01)
                area_kfac.markdown(f'kafactor @{kfac_freq:1.4}GHz is : {kf}')




        else:
            fig = px.line(title='plotly express',labels={'x':'frequency GHz','y':'S11 reflectivity'},height=im_height,width=im_width)
            st.plotly_chart(fig)
            #st.markdown('no plot yet') # leaving the container emtpy causes weird problems!


