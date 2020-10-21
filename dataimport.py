
'''
Some functions to parse ascii tabulated files (read_csv) and
custom tdms files from tmplnt (read_tdms, read_tdms3D)
'''
import pathlib
import logging
import pandas as pd
import re
from nptdms import TdmsFile
import numpy as np
import os
import textdata

logger = logging.getLogger(__name__)

def read_csv(fname,sep=None,**kwargs) :
    
    d = textdata.read_textdata(fname)
    df = pd.DataFrame(d['data'])
    df.attr_name = 'import'
    df.attr_origin = 'csv'    
    return(df)


def read_csv_pandas(fname,sep=None,**kwargs) :
    '''
    supposed to read most tabulated ascii data
    work in progress...
    '''
    i = 0
    with open(fname,'r') as fp :
        for line in fp : # skip header/info lines 0th order   
            # a more semantic analysis would be better...
            logger.debug(line)         
            r = re.search('[^0-9,\.Ee\+\-\s\t]',line)
            # if r is None:
            #     r = re.search('[+0-9]',line)
            if line == '\n' :
                pass
            elif r is None :
                break                
            else :                
                pass
            i = i+1

        sep=' '
        df = pd.read_csv(fp,sep,engine='python',**kwargs)
        df.attr_name = 'import'
        df.attr_origin = 'csv'
        return(df)



def tdms_type(fname) :
    try :
        tdms = TdmsFile(fname )
    except :
        return('None')
    try :
        ft = tdms.properties['FILETYPE']
    except : 
        ft = 'arbitrary'
    return(ft)


def read_tdms(fname) :
    '''
    this imports tdms files into a list of dataframes (2D tdms) or 
    into a single df (3D tdms) with the 1. col beeing the x axis and the following
    columns beeing the z values 
    '''
    fname = str(pathlib.Path(fname))
    tdms = TdmsFile(fname)
    # check if tdms file was generated from tmplnt labview SW
    try :
        ft = tdms.properties['FILETYPE']
    except :
        logger.error('not a TMPLNT Labview tdms file')
           
    if ft == 'LDAT2' : 
        dfs = []
        for x in tdms.groups() :
            #chan = tdms.group_channels(x)
            chan = tdms[x.name].channels()
            d = np.stack((chan[0].data,chan[1].data),axis=1)
            df = pd.DataFrame(d)
            df.attr_name = str(x)
            df.attr_origin = 'tdms'
            dfs.append(df)
        return(dfs)      
    elif ft == '3DData' :         
        groups = tdms.groups()
         # these are the linescans
        #chan = tdms.group_channels(groups[0])        
        chan = tdms[groups[0].name].channels()
        # x-axis from linescans
        #x = tdms.group_channels(groups[1])[0].data
        #y = tdms.group_channels(groups[1])[1].data
        x = tdms[groups[1].name].channels()[0].data
        y = tdms[groups[1].name].channels()[1].data
        m = np.zeros([x.size,y.size+1])
        k=1
        m[:,0] = x
        for yy in chan:
            m[:,k] = yy.data
            k = k + 1
        df = pd.DataFrame(m)
        df.attr_name = ''
        df.attr_origin = 'tdms 3D'
        return([df])

# end read_tdms()         


class read_tdms3D :
    '''
    returns an obeject that contains z and x,y axis data as well as
    metadata
    '''
    def __init__(self,fname) :
        fname = str(pathlib.Path(fname))
        tdms = TdmsFile(fname )
        # check if tdms file was generated from tmplnt labview SW
        try :
            ft = tdms.properties['FILETYPE']
        except :
            logger.error('not a TMPLNT Labview tdms file')
            
        if ft != '3DData' :     
            logger.error('not a TMPLNT 3D tdms file')    
            return   

        else :
            groups = tdms.groups()            
            self.meta = {name:value for name, value in tdms[groups[2].name].properties.items()}                    
            m = {name:value for name, value in tdms[groups[1].name].properties.items()}                    
            self.xlabel = m['x_label']
            self.ylabel = m['y_label']
            self.zlabel = m['z_label']
            # these are the linescans
            #chan = tdms.group_channels(groups[0])        
            chan = tdms[groups[0].name].channels()
            # x-axis from linescans
            self.x = tdms[groups[1].name].channels()[0].data
            self.y = tdms[groups[1].name].channels()[1].data
            self.z = np.zeros([self.x.size,self.y.size])
            k=0            
            for yy in chan:
                self.z[:,k] = yy.data
                k = k + 1
            return

# end read_tdms3D()         


def tdms_toascii(fname) :

    ft = tdms_type(fname)
    if ft == 'LDAT2' :
        pass



def autoimport(fname) :
    '''
    returns a list of pandas dataframes (or crashes)
    '''
    import os
    ext =  os.path.splitext(fname)[1]
    if ext == '.tdms' :
        return(read_tdms(fname))
    else :
        return( [read_csv(fname)] )


def test():
    f='quickyplot/demodata/1col.txt'
    dfs = autoimport(f)
    print(dfs)


if __name__ == '__main__' :
    import sys
    #test()
    #sys.exit()

    #f = 'y:/data import/ref data/TRSPCPowerDiodeCalibQE (TL FDS1010).dat'
    
    f = 'c:/users/scp/nextcloud/develop/python/firststeps/test3D.tdms'
    print('file type: ',tdms_type(f))

    #dfs = autoimport(f)
    #print(dfs[0].head(5))
    import matplotlib.pyplot as plt

    w = read_tdms3D(f)
    for k,v in w.meta.items() :
        print(k + ' = ' + v)
    print(w.xlabel)
    fig, ax = plt.subplots()
    im = ax.pcolormesh(w.x,w.y,w.z.T,cmap='plasma')
    im.xlabel = 'sadad'
    cb = fig.colorbar(im)
    #cb.ax.text(4,0.6,'current in A',rotation=270,fontsize=16)

    plt.show()