import numpy as np
import os #functions for interacting with operating system
import gc

dir_filteredfiles = "D:/ZTF_data/all_filtered_LCs" #path to directory with fields from Object-IDs below 
objectid_confirmed_MLs = [
                        809210400023757, # field 809, ccid 10, qid 4
                        777213100018919, # 777, 13, 1
                        778216100021253, # 778, 16, 1
                        656201200010418, # 656, 1, 2
                        280202300109995, # 280, 2, 3
                        331203300021759, # 331, 3, 3
                        383204100097537, # 383, 4, 1
                        332313300058865, # 332, 13, 3
                        332309200017469, # 332, 9, 2
                        383207200022322, # 383, 7, 2
                        435212300026373, # 435, 12, 3 
                        383206100019683, # 383, 6, 1
                        435216100025385, # 435, 16, 1
                        383213100097329, # 383, 13, 1
                        333203100035832, # 333, 3, 1
                        487208100122149, # 487, 8, 1
                        538206100027913, # 538, 6, 1
                        487215200096940, # 487, 15, 2
                        384207100022342, # 384, 7, 1
                        684207200011685, # 684, 7, 2
] 

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

a_a_compared = []
for s_path_root, a_s_folder, a_s_file in os.walk(dir_filteredfiles):
    for s_name_file in a_s_file: 
            s_path_file = s_path_root + "/" + s_name_file

            a_a_data = np.load(s_path_file, allow_pickle=True) # [a_LC, a_LC, ...]
            for a_LC in a_a_data:
                if (a_LC[o_indices.objectid] in objectid_confirmed_MLs):
                    a_a_compared.append(a_LC[o_indices.objectid])

if a_a_compared == objectid_confirmed_MLs:
    print("Results correct, filter good")
    print(a_a_compared)
else:
    print("Resulsts incorrect")
    print(a_a_compared)
