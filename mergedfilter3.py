import pyarrow.parquet # um auf Parquet-File zuzugreifen
import pandas # um auf Pandas-Dataframe zuzugreifen
import numpy as np # Mathe
import os #functions for interacting with operating system
from scipy.stats import skew
import json # um auf .json-File mit Linkliste zugreifen zu können
import wget # zum Herunterladen
import gc # zum Random Access Memory leeren (mit zwischengespeicherten Listen etc. - sonst stürzt der Computer irgendwann ab)

# FUNCTIONS
def neumann(array):
    neumann_lst = np.zeros(len(array))
    std = np.std(array)
    for i in range(1, len(array)):
        neumann_lst[i] = ((array[i] - array[i-1])**2)/((len(array)-1)*(std**2))
    neumann_value = np.sum(neumann_lst)
    return neumann_value

# dir = "C:\Kanti\Microlensing\Python\Parquet-Files" #path to root directory 
dir = "./data" #path to root directory
dir = "./Parquet-Files" #path to root directory

class O_indices: #object for indices as "objectid", not as "lc[0]", für Übersichtlichkeit
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

# Opening .json file
o_file_0 = open('./a_s_url_https_irsa_ipac_caltech_edu_data_ZTF_lc_lc_dr11_0.json')
o_file_1 = open('./a_s_url__https__irsa_ipac_caltech_edu_data_ZTF_lc_lc_dr11_1.json')
  
# returns json object as a dictionary
a_s_url_0 = json.load(o_file_0)
a_s_url_1 = json.load(o_file_1)
a_s_url__merged = a_s_url_0 + a_s_url_1

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

class O_indices: #object for indices as "objectid", not as "lc[0]"
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
o_indices = O_indices()

s_path_current_directory = os.path.dirname(os.path.realpath(__file__)) # os.path.dirname(x) gibt den Namen des Ordners an, in dem das File mit dem path x gespeichert ist

n_len_a_s_url__merged = len(a_s_url__merged) # 163319

for s_url in a_s_url__merged:
   if "zr" in s_url: #reduces to 69705 
        try:
            # .split(x) teilt ein string an der Stelle x in zwei Strings auf, .pop() löscht den ersten Teil
            s_urlpath_file = s_url.split("://").pop() # z.B. 
            s_name_file = s_urlpath_file.split("/").pop() #
            wget.download(s_url) # prints dots to show download progress
            
            # process the data
            n_index = a_s_url__merged.index(s_url)
            print(f"-----------processing----------------")
            print(f"file: {n_index} of {n_len_a_s_url__merged}")
            print("")

            s_path_file = s_path_current_directory + "/" + s_name_file

            o_table = pyarrow.parquet.read_table( 
                s_path_file    
            )


            o_pandas_data_frame = o_table.to_pandas() # make accessible Pandas DataFrame

            a_a_all_LC = o_pandas_data_frame.values #makes np.array()
            

            a_a_LC_vorfilter = np.array([ 
                a_LC# return value
                for
                a_LC # variable name in loop
                in a_a_all_LC  # array name of iterated array
                if (
                    a_LC[o_indices.catflags].sum() == 0 
                    and a_LC[o_indices.nepochs] > 30
                )  # if this is true, 'return value' is returned
            ])
        
            a_objectids_vorfilter = np.array(
                a_LC[O_indices.objectid]
                for a_LC in a_a_LC_vorfilter
            )
            
            a_a_LC_hauptfilter = np.array([
                a_LC for a_LC in a_a_LC_vorfilter
                if
                (skew(a_LC[o_indices.mag]) <= (10**((neumann(a_LC[o_indices.mag]) - 1.3)/-0.4) - 1.6)) 
            ])
                        
            if len(a_a_LC_hauptfilter) > 0:
                np.save(s_name_file + "_filtered", a_a_LC_hauptfilter) # file is saved in s_name_file_filtered.npy
            
            np.save("a_objectids_vorfilter" + s_name_file, a_objectids_vorfilter)
            os.remove(s_path_file) # delete old file
            
            # delete all to not overwhelm RAM
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
            gc.collect()
            continue # should cause filter always to continue, even if error occurs in except
   
