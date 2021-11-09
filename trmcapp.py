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


st.set_page_config(layout='wide',initial_sidebar_state='collapsed')

# ''''
# this is for streamlit version >= 1 using st.session_state

# git remote add trmcapp2  https://git.heroku.com/trmcapp2.git
# git push trmcapp2 master

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


# helper functions to auomate the fit parameter display:
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

def parms_list(container,plist):
    # creates a 
    cols = 2 # works only for 2 columns !!!
    pl = list_partition(plist,cols)
    
    with container:
        ct = [None]*len(pl)        
        for r,row in enumerate(pl):                    
            ct[r] = st.columns(2*cols)
            plist[r*cols]['val'] = ct[r][0].number_input(row[0]['name'],value=float(row[0]['val']),format='%1.4e',key=row[0]['name'])            
            plist[r*cols]['fixed'] = ct[r][1].checkbox('fixed',value=row[0]['fixed'],key=f"{row[0]['name']}_check")        
            if cols>1 and row[1] :
                plist[r*2+1]['val'] = ct[r][2].number_input(row[1]['name'],value=float(row[1]['val']),format='%1.4e',key=row[1]['name'])                
                plist[r*2+1]['fixed'] = ct[r][3].checkbox('fixed',value=row[1]['fixed'],key=f"{row[1]['name']}_check")                
    return(pl)  


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
            c.fit(extdata[:,0],extdata[:,1])
            yfit = c.calc(extdata[:,0])  
            st.session_state['fit_done'] = True                      
            st.session_state['fit_y'] = yfit
            st.session_state['fit_chi2'] = ((yfit - extdata[:,1])**2).sum()        
        else : 
            st.session_state['fit_done'] = False   

    def do_kfac():         
        if kfac_min:
            k = y.argmin()
            st.session_state['kfreq'] = f[k]        
        s11.layer_sig = kfac_sigma
        st.session_state['kfac'] = s11.kfactor(st.session_state['kfreq'],rel_change=0.01)         

    @st.cache()
    def load_data(datastream):        
        if datastream is not None: # process uploaded file            
            datastream.seek(0)        
            buf = datastream.read()
            buf = io.BytesIO(buf)
            stream = io.TextIOWrapper(buf)        
            data = textdata.read_textdata(stream)
            data = np.array(data['data']) 
            print('filedata loaded') 
            return data  
        else : 
            return []        
                
   
    # set the order of gui elements by defining containers:
    area_graph = st.container()
    area_info = st.container()
    area_kfac = st.container()
    datastream = st.file_uploader('ascii tab data with f in GHz')    
    area_control = st.container()    
    #area_parms = st.beta_container() 
        
    extdata = load_data(datastream)
    
    with area_control :
        c_cols = st.columns((1,2,2,2))        
        if datastream:
            btn_fit = c_cols[0].button('fit',on_click=do_fit)
        fmin = c_cols[1].number_input('fmin',value=8.4,format='%1.4f')
        fmax = c_cols[2].number_input('fmax',value=9.2,format='%1.4f')    
        fstep = c_cols[3].number_input('step',value=0.001,format='%1.4f')
        st.markdown('**parameters:**')
        pf = st.form('pform')
        pf.form_submit_button('calculate resonance')#,on_click=store_parameters)
        parms_list(pf,c._plist[1:])  
        c._calc_reduced()
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
        kfac_sigma = kc[3].number_input('layer sigma [S/m]',value=1.,format='%1.4f')        
        if btn_kfac:
            st.markdown(f'k-factor @{st.session_state.kfreq:1.4}GHz is : {st.session_state.kfac}')
    
    fig = px.line(x=f,y=y,log_y=False,title='trmc resonance curve',labels={'x':'frequency GHz','y':'S11 reflectivity'},height=im_height,width=im_width)
         
    if len(extdata) > 1:                
        fig.add_trace(go.Scatter(x=extdata[:,0], y=extdata[:,1],
            mode='markers',
            name='data'),
                )
    if st.session_state['fit_done'] :                              
        fig.add_trace(go.Scatter(x=extdata[:,0], y=st.session_state['fit_y'],
        mode='markers',
        name='fit'),
            )
        chisqr = st.session_state['fit_chi2']                      
        results = area_info.expander(f'fit results (chisqr = {chisqr:1.3})')
        results.write(c.plist)
    
    area_graph.plotly_chart(fig)            
   
    # for key,val in st.session_state.items():
    #     print(key," : ",val)
    

##################### init sequence #########################



# sidebar config
st.sidebar.header('trmcapp2\n')
help = st.sidebar.button('Help')
source = st.sidebar.button('show source code')
im_width = st.sidebar.number_input('image width',value=800)
im_height = st.sidebar.number_input('image height',value=400)
btn_reset = st.sidebar.button("reset",help="reset cache and return to default values")

if 'app_init' not in st.session_state or btn_reset:
    st.session_state['app_init'] = True
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
    st.session_state['s11'] = s11
    st.session_state['cfit'] = c
    st.session_state['fit_done'] = False
    
else :
    s11 =  st.session_state['s11']
    c = st.session_state['cfit']

if help : show_help()
elif source : show_source()
else: main()