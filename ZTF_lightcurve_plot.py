import matplotlib.pyplot as plt
import datetime
import numpy as np
from scipy.stats import norm, skew, kurtosis, skewnorm
from scipy.stats import kde

class O_indices: #object for indices as "objectid", not as "lc[0]"
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

a_a_data = np.load("C:\Kanti\Microlensing\Python\some_filtereddata\ztf_000762_zr_c01_q4_dr11.parquet_filtered.npy", allow_pickle=True)
# shape of a_data: array(a_LC, n_fitting_difference)
# # .loc() = Befehl in Pandas, um alle zugehörigen Daten zu gewissem Objekt zu holen 
for i in range(len(a_a_data)-3, len(a_a_data)):
    lc = a_a_data[i]
    
    mag = lc[o_indices.a_mag]
    date = lc[o_indices.a_hmjd]

    # # oids = df['objectid']
    # # for oid in oids:
    # #     if oid == 202110100018804:
    # #         print(oid)
    # print(df.loc[2])   

    # print(lc1)
    # t = np.linspace(date,)
    plt.figure()
    plt.title(str(lc[o_indices.n_objectid]))
    plt.plot(date, mag, '.', color = 'red')
    # print(date)
    #print(datetime.datetime.strptime(str(int(date[0])), '%y%j').strftime('%d.%m.%Y')) 
    # Konvertierung HMJD -> GD; Dezimalstellen wurden nicht erkannt, deshalb int()
    
    # # plot skewness
    # a_x = date
    # a_mag = mag
    # r_neg = skewnorm.rvs(-1, size=1000)
    # r_pos = skewnorm.rvs(1, size=1000)
    # r_norm = skewnorm.rvs(0, size=1000)
    # plt.figure()
    # plt.title("Gaussverteilungen ML-Lichtkurve")
    # density = kde.gaussian_kde(a_mag)
    # a_y = density(a_x)
    # plt.plot(a_x, a_y)
    # plt.figure()
    plt.show()