import matplotlib.pyplot as plt # für Graphiken
import numpy as np # fürs Aufrufen des .npy-Formats
class O_indices: #object for indices as "objectid", not as "lc[0]" -> bessere Übersicht beim Aufrufen der Indices
    n_objectid = 0
    n_filterid = 1
    n_fieldid = 2
    n_rcid = 3
    n_objra = 4
    n_objdec = 5
    n_nepochs = 6
    a_hmjd = 7
    a_mag = 8
    a_magerr = 9
    a_clrcoeff = 10
    a_catflags = 11
o_indices = O_indices()

a_a_data = np.load("C:\Kanti\Microlensing\Python\some_filtereddata\ztf_000762_zr_c01_q4_dr11.parquet_filtered.npy", allow_pickle=True) # .npy-File aufrufen, da gefilterte Daten so abgespeichert wurden
# shape of a_data: array(a_LC, n_fitting_difference)
# # .loc() = Befehl in Pandas, um alle zugehörigen Daten zu gewissem Objekt zu holen 
for i in range(len(a_a_data)): # jede Lichtkurve plotten, kann angepasst werden falls File zu gross
    lc = a_a_data[i]
    
    mag = lc[o_indices.a_mag] # Magnituden-Array aufrufen
    date = lc[o_indices.a_hmjd] # Zeit-Array aufrufen (in Tagen)


    plt.figure() # mache ein Koordinatensystem
    plt.title(str(lc[o_indices.n_objectid]))
    plt.plot(date, mag, '.', color = 'red')
    plt.show()
