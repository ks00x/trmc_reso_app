import pathlib
import re

VALID_NUMSTART = '0123456789+-'
COL_SEPERATOR_RE = '[\s;,]+' #normal whitespaces + , ;    (at least 1)

def read_textdata(fname,german_num=False):
        '''
        tries to read all sorts of tabulated ascii floating point data (csv&Co)
        returns a dict with the following keys:
        'data' : list of rows -> list of cols  (float)
        'header' : the ascii header that at the beginning that has been skipped        
        '''
        fname = pathlib.Path(fname)
        reg = re.compile(COL_SEPERATOR_RE)
        n_col = -1
        lines = 0
        firstline = -1
        header = []
        tabdat = []
        with open(fname,'r') as fp :
                for k,line in enumerate(fp) :                         
                        if german_num :
                                line = line.replace(',','.')
                        x = reg.split(line)
                        #print(k,line)
                        if len(x[0]) == 0 :                                
                                continue
                        elif x[0][0] in VALID_NUMSTART :
                                try :
                                        y = [float(y) for y in x[:-1]]
                                        if n_col > 0 :
                                                if n_col != len(y) : # the end of the tab data sequence
                                                        break
                                                tabdat += [y]
                                        else : # first numeric row
                                                n_col = len(y)
                                                firstline = k
                                        lines += 1                                        
                                except :                                        
                                        break
                                        #print('bad : ',x)
                        else :
                                header.append(line)
                                        
                d={
                        'data':tabdat,
                        'header':header,
                        'rows':lines,
                        'col':n_col,
                        'firstline':firstline
                }                
                return(d)




if __name__ == "__main__":

        if True : # demo text file
                import numpy as np
                x = np.random.random((300,2))
                np.savetxt('~temp.txt',x)
        
        p = pathlib.Path().cwd().glob('*.txt') # all txt files in the current dir
        for f in p:
                d = read_textdata(f,german_num=False)
                print(f"{f.name}: ({d['rows']} x {d['col']}) , {d['data'][0]}")
                
        
        # d = read_textdata('~temp.txt')
        # print(d)
        # import numpy as np
        # x = np.array(d['data'])
        # print(x.shape)