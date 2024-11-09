import streamlit as st
from dataclasses import dataclass

@dataclass
class param:
    name:str
    val:float
    fixed:bool

    def __getitem__(self, item):
        return getattr(self, item)
    def __setitem__(self, item, value):
        setattr(self,item,value)

class paramlist:
    """creates multi-column parameter lists driven by a list of <param> dataclass/dict entries"""
    def __init__(self,cols=2,keyprefix='plist_'):
        self.cols = cols
        self.keyprefix = keyprefix          
              
        
    def create(self,plist,container:st,format:str='%f'):
        ""        
        st.session_state.plist__ = plist #
        if self.check_duplicate(plist) :
            container.error('duplicate names in plist')
        if len(plist)%self.cols == 0 :
            rows = len(plist)
        else: rows = len(plist)+1

        for k,p in enumerate(plist):
            cn = (k % self.cols)*2  
            if cn == 0 : # new row     
                colspec = [4-(k%2)*3 for k in range(self.cols*2)] # <value> columns wider than <fix> (4:1)       
                cs = container.columns(colspec)
            key = f"{self.keyprefix}{p['name']}"
            st.session_state[key] = p['val']            
            cs[cn].number_input(p['name'],format=format,key=key,on_change=self._callback,args=(k,key,0))

            key = f"{self.keyprefix}{p['name']}_fix"
            st.session_state[key] = p['fixed']            
            cs[cn+1].checkbox('fix',key=key,on_change=self._callback,args=(k,key,1))

    def _callback(self,idx:int,key:str,item:int):
        "mapping back widget values to param list"        
        if item == 0 :
            st.session_state.plist__[idx]['val'] = st.session_state[key]
        else :
            st.session_state.plist__[idx]['fixed'] = st.session_state[key]
    
    def check_duplicate(self,plist) -> bool:
        "returns True in case of duplicate names"
        return len(plist) != len(set([p['name'] for p in plist]))             



if __name__ == '__main__':
    
    def main():
        from random import random

        def do_stuff(pl):
            for k,p in enumerate(pl):
                if p.fixed == False:
                    pl[k].value += 1
            return pl

        def reset():
            del st.session_state.init
            st.experimental_rerun() # without this it takes on extra button click to rerun....

        st.set_page_config(layout='wide')

        if 'init' not in st.session_state:
            st.session_state.init = True
            st.session_state.plist =  [param(f'param{k:02d}',random(),False) for k in range(20)]

        ncols = st.number_input('cumber of columns',value=2)
        p = paramlist(cols=ncols)        
        p.create(st.session_state.plist,st,format='%1.4f')

        but = st.button('do stuff',help="increment values by 1 if not set to <fix>")
        if but :
            st.session_state.plist = do_stuff(st.session_state.plist)
            st.experimental_rerun() # without this it takes on extra button click to rerun....

        but = st.button('reset values')
        if but :
            reset()

    main()