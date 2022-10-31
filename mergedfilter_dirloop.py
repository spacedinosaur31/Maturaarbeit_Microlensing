import pyarrow.parquet # for accessing .parquet-file
import numpy as np # math -> numpy = numerical python
import os #functions for interacting with operating system
from scipy.stats import skew # for skewness
import gc # garbage collector, empties RAM

# FUNCTIONS
def neumann(array): # Magnituden-Array als Input, Von-Neumann-Statistik des Arrays als Output
    neumann_lst = np.zeros(len(array))
    std = np.std(array)
    for i in range(1, len(array)):
        neumann_lst[i] = ((array[i] - array[i-1])**2)/((len(array)-1)*(std**2))
    neumann_value = np.sum(neumann_lst)
    return neumann_value

# dir = "C:\Kanti\Microlensing\Python\Parquet-Files" #path to root directory 

dir = "F:/RawData/1" #path to root directory

class o_indices: #object for indices as "objectid", not as "lc[0]", für Übersichtlichkeit
    objectid = 0
    filterid = 1
    fieldid = 2
    rcid = 3
    objra = 4
    objdec = 5
    nepochs = 6
    hmjd = 7
    mag = 8
    magerr = 9
    clrcoeff = 10
    catflags = 11

# a_a_all_LC__example = [
#     #[...],
#     [ 
#        468316400000000, #=> objectid", # 
#        3, #=> filterid", # 
#        468, #=> fieldid",
#        63, #=> rcid",
#        148.4763641357422, #=> objra",
#        7.4226508140563965, #=> objdec",
#        1, #=> nepochs",
#        array([58257.184], dtype=float32), #=> hmjd",
#        array([17.160751], dtype=float32), #=> mag",
#        array([0.02298518], dtype=float32), #=> magerr",
#        array([0.18954925], dtype=float32), #=> clrcoeff",
#        array([0, 1, 2, 4], dtype=uint16), #=> catflags",
#     ], 
#     #[...],
# ]


for s_path_root, a_s_folder, a_s_file in os.walk(dir):
    for s_name_file in a_s_file:
        if "zr" in s_name_file: # reduziert 163 69705 
            try:
                s_path_file = s_path_root + "/" + s_name_file 

                o_table = pyarrow.parquet.read_table(
                    s_path_file
                )

                o_pandas_data_frame = o_table.to_pandas()

                a_a_all_LC = o_pandas_data_frame.values #makes np.array()
                

            #make filtered list right away
                a_a_LC_vorfilter = np.array([ 
                    a_LC# a_value # 'return value'
                    for
                    a_LC # variable name in loop
                    in a_a_all_LC  # array name of iterated array
                    if (
                        a_LC[o_indices.catflags].sum() == 0 
                        and a_LC[o_indices.nepochs] > 30
                    )  # if this is true, 'return value' is returned
                ])
            
                a_objectids_vorfilter = np.array(
                    a_LC[o_indices.objectid]
                    for a_LC in a_a_LC_vorfilter
                )
                
                a_a_LC_hauptfilter = np.array([
                    a_LC for a_LC in a_a_LC_vorfilter
                    if
                    (skew(a_LC[o_indices.mag]) <= (10**((neumann(a_LC[o_indices.mag]) - 1.3)/-0.4) - 1.6)) #params in work
                ])
                            
                if len(a_a_LC_hauptfilter) > 0:
                    np.save(s_name_file + "_filtered", a_a_LC_hauptfilter) # file is saved in s_name_file_filtered.npy
                
                np.save("a_objectids_vorfilter" + s_name_file, a_objectids_vorfilter)
                os.remove(s_path_file) # delete old file
                
                # del deletes all lists, otherwise RAM gets filled 
                del a_a_LC_vorfilter
                del a_objectids_vorfilter
                del a_a_LC_hauptfilter
                del o_table
                del o_pandas_data_frame
                del a_a_all_LC

            except:
                np.save(s_name_file + "_errorfile")
                os.remove(s_path_file) # delete old file
            
            finally: #always executed
                gc.collect() # leert das RAM (Random Access Memory) -> gc = garbage collect
                continue # should cause filter always to continue, even if error occurs in except
    
