import inspect
from copy import deepcopy

class fixparameter():
    '''
    a class to handle fixed numeric parameters in function parameter lists
    '''
    def __init__(self,func=None):
        self._plist = []
        self._pred = 0              
        if func :
            self.add_by_func(func)

    def __getattr__(self,name):
        if name[0] == '_': # more general - was: if attr == "__setstate__":
            # see: https://stackoverflow.com/questions/47299243/recursionerror-when-python-copy-deepcopy
            raise AttributeError(name)              
        k = self._findme(name)                 
        if k >= 0 :
            return(self._plist[k]['val'])
        else:
            raise AttributeError(f'attribute <{name}> does not exist!')

    def __setattr__(self,name,val): 
        #print(name)
        if name[0] != '_': # important to have the class properties defined with '_'                
            k = self._findme(name)       
            if k >= 0 :            
                self._plist[k]['val'] = val                
        super().__setattr__(name,val) # this seems to be the default rule... same behavior
        

            
    def add(self,name,val,fixed):
        d={'name':name,'val':val,'fixed':fixed}
        self._plist.append(d)
        self._calc_reduced()
    
    def set(self,name,val,fixed=None):        
        for p in self._plist:
            if p['name'] == name :
                p['val'] = val
                if fixed is not None:
                    p['fixed'] = fixed
                break
        else : assert 0,f'parameter <{name}> not found'
        self._calc_reduced()
    def fix(self,name):        
        for p in self._plist:
            if p['name'] == name :                
                p['fixed'] = True
                break
        else : assert 0,f'parameter <{name}> not found'
        self._calc_reduced()

    def unfix(self,name):        
        for p in self._plist:
            if p['name'] == name :                
                p['fixed'] = False
                break                    
        else : assert 0,f'parameter <{name}> not found'
        self._calc_reduced()

    def set_reducedvals(self,vallist):
        pass
                
    def add_by_func(self,func):
        self._func = func
        x = inspect.signature(func)
        y = list(x.parameters.keys())
        self._plist = [{'name':name,'val':0,'fixed':False} for name in y]
        self._calc_reduced()
    
    def set_by_plist(self,plist):
        self._plist = plist
        self._calc_reduced()
        
    def func(self,*args):
        assert len(args) == self._pred, f"mismatched number of arguments! Expecting {self._pred}, received {len(args)}"        
        pnew = [] # the updated parameter list       
        k = 0
        for p in self._plist:
            if p['fixed'] : # use the default parameter
               pnew.append(p['val']) 
            else:# use the supplied value and put it into pnew in the right position
                pnew.append(args[k])
                k += 1
        #print(pnew)
        return( self._func(*pnew) )# call the function and return the value

    def _findme(self,name):
        for i,p in enumerate(self._plist):
            if p['name'] == name :
                return(i)
        return( -1 )
        

    @property
    def plist(self):        
        return(self._plist)
    
    @property
    def predlist(self):
        'return a parameter list for the reduced function'
        return [p['val'] for p in self._plist if not p['fixed']]

    @property
    def pvallist(self):
        'returns parameter values as a list'
        return [p['val'] for p in self._plist]
        
    def copy(self):
        x = deepcopy(self)
        return x
        
    def _calc_reduced(self):
        k=0        
        for i,p in enumerate(self._plist):
            if p['fixed'] == False:
                k += 1           
        self._pred = k

    def list_map_reduced(self,mylist):        
        return [mylist[k] for k,p in enumerate(self._plist[1:]) if not p['fixed']]
        
    def __repr__(self):        
        s = ''
        for p in self._plist:
            for k,v in p.items():
                s += f"{k:5} = {v}\n"
            s += '\n'
        return(s)


if __name__ == "__main__":
    
    def ftest(x1,x2,x3):
        return(x1+x2+x3)
    
    ff = fixparameter(ftest)    
    ff.set('x1',1,False)
    ff.set('x2',2,True) # set this parameter to fixed
    ff.set('x3',3,False)
    ff.set('x3',4)

    g = ff.copy() # a deep copy

    # our reduced function fm will have x2 set to the default
    # and depent only on 2 parameters x1,x3
    fm = ff.func 
    x = ff.predlist #get the reduced list with default values
    print(fm(3,4))
    print(fm(*x))

    print(ff._findme('x3'))
    ff.x3 = 33
    print(ff)