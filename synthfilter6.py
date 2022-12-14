import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import skew
import random # generate random numbers

"""
Der Datensatz generiert eine Lichtkurvenliste lightc_lst der Anzahl LCamount. Jede Liste enthält 7 Einträge:
Index 0: id
1: Liste der Zeitpunkte
2: Liste der Magnitudenwerte
3: Falls ML-Event: umin-Wert
   sonst: None
4: Falls ML-Event: tE-Wert (Dauer des ML-Events)
   sonst: None
5: Skewness
6: Neumann-Wert
"""

# VALUES
probability = 1 # pro x (Probability) LC hat es ca. i ML-Event
magpointamount_min = 30 # Mindestanzahl Messungen
t0 = 0 # Zeitpunkt max. Helligkeit
surveylength = 500 # wie lange gesamte Messung dauerte = maximale Eventdauer
mean_skew = -0.22994225279524635  #Mittelwert von 2 fields 
mean_std = 0.15856555  # Mittelwert von 2 fields 
mean_mag = 20.421268  # Mittelwert von 2 fields 
mean_luminosity = 10**(mean_mag/(-2.5)) # convert magnitude-mean to luminosity-value for multiplication by amplification factor 
mean_neumann = 1.6 # circa
LCamount = 20 # x LCs will be generated
lost = 0
trap = 0
found = 0

# LISTS
lightc_lst = [0 for i in range(LCamount)] # stellt synthetischen Datensatz dar -> pro LC: Liste wie [Index (-> Object-ID), Magnitudenwerte, Zeitpunkte] 
detect_lst_binary = np.zeros(LCamount) # Array gefilterter ML-Events, np.zeros(x) macht Liste mit x Nullen
truetruth_lst_binary = np.zeros(LCamount) # Array mit tatsächlichen ML-Events -> muss Liste sein, da np.array keine arrays speichern kann aber kein Problem, da bei ZTF kein lclist erzeugt werden muss
lightc_lst_filtered = [] # Index (wie object ID) wird in Liste eingefügt -> am Schluss gezählt, ob alle Kriterien erfüllt
skew_lst = np.zeros(LCamount) # Skewness-Werte alles LC
std_lst = np.zeros(LCamount) # Standardabw-Werte alles LC
neumann_lst = np.zeros(LCamount)
# below: for generating plots, not necessary for generating synthetic LC
umin_lost = []
tE_lost = []
umin_found = []
tE_found = []
skew_ML = []
skew_noML = []
neumann_ML = []
neumann_noML = []
a_all_MLs = []

# FUNCTIONS
def theo(t, umin, tE): #theoretische ML-Funktion, returns mag
    t_0 = 0
    u = np.sqrt(umin**2 + ((t-t_0)/tE)**2)
    A = mean_luminosity*((u**2 + 2) / (u*np.sqrt(u**2 + 4))) 
    M = -2.5*np.log10(A) 
    return M

def neumann(array):
    neumann_lst = np.zeros(len(array))
    std = np.std(array)
    for i in range(1, len(array)):
        neumann_lst[i] = ((array[i] - array[i-1])**2)/((len(array)-1)*(std**2))
    n = np.sum(neumann_lst)
    return n


# SYNTHETIC LC GENERATOR + FILTERING -> Produktion künstlicher LC -> random ML-Events oder nicht 
for i in range(LCamount):   
    ML_yesorno = random.randint(0, probability) #Wahrscheinlichkeit von 1/probability
    magpointamount = random.randint(magpointamount_min, 200)
    if ML_yesorno == 1: #falls Microlensing-Event
        t = np.zeros(magpointamount) # Zeitachse (x)
        mag = np.zeros(magpointamount) # Magnitudenachse (y)
        umin = random.random() # random.random() gibt Wert zwischen 0 und 1 zurück
        tE = random.randint(1, surveylength) # random.randint(x, y) gibt eine ganze Zahl zwischen x und y an
        for x in range(magpointamount):
            t[x] = random.randint(-(1/2)*surveylength, (1/2)*surveylength) # zufällige Zeitpunkte, für die jeweils mag berechnet wird
        np.ndarray.sort(t) # Zeitpunkte von klein nach gross sortieren -> richtige Reihenfolge
        for x in range(magpointamount):  # Helligkeit A abhängig von u, u abhängig t
            M = theo(t[x], umin, tE)  + random.gauss(0, mean_std) # bei beiden Gauss-Rauschen machen mit der Standardabweichung mean_std
            mag[x] = M # gleicher Index der jeweiligen mag- und t-Werte ordnet sie einander zu 
            lc_skew_value = skew(mag)
            lc_neumann_value = neumann(mag)
        skew_ML.append(lc_skew_value) # fürs Generieren von Skewness-Neumann-Plots 
        neumann_ML.append(lc_neumann_value) # fürs Generieren von Skewness-Neumann-Plots 
        lightc_lst[i] = np.array([i, t, mag, umin, tE, lc_skew_value, lc_neumann_value], dtype = object)
  
        # Filterbedingung hier:
        if (lc_skew_value < 0.9) and (lc_neumann_value < 1.2):
            detect_lst_binary[i] = 1
            found += 1
        else:
            detect_lst_binary[i] = 0
            lost += 1 # es handelte sich um ein ML-Event, das von der oberen Bedingung verpasst wurde
            
        #eventuelles Plotten der Kurve:
        # plt.figure() #make coordinate system
        # plt.plot(t, mag,".", color = "red")#t,mag = lists! -> A(t)+0.2*random -> adds random number to whole list -> for loop to handle each value separately!

    else: 
        
        t = np.zeros(magpointamount) # Zeitachse (x)
        mag = np.zeros(magpointamount) # Magnitudenachse (y)
        for x in range(magpointamount):
            t[x] = random.randint(-(1/2)*surveylength, (1/2)*surveylength)
        np.ndarray.sort(t)
        for x in range(magpointamount):
            M = mean_mag + random.gauss(0, mean_std)
            mag[x] = M
            lc_skew_value = skew(mag)
            lc_neumann_value = neumann(mag)
        skew_noML.append(lc_skew_value)
        neumann_noML.append(lc_neumann_value)
        lightc_lst[i] = np.array([i, t, mag, None, None, lc_skew_value, lc_neumann_value], dtype = object)
        plt.figure()
        plt.plot(t, mag, ".", color = "red")
        plt.show()
        if (lc_skew_value < 0.9) and (lc_neumann_value < 1.2):
            detect_lst_binary[i] = 1
            trap += 1
        else:
            detect_lst_binary[i] = 0
        # plt.figure() # make coordinate system
        # plt.plot(t, mag,".", color = "red")#t,a = lists! -> A(t)+0.2*random -> adds random number to whole list -> for loop to handle each value separately!
print(a_all_MLs)
# # umin-tE-Diagramm:
# plt.figure()
# plt.plot(tE_lost, umin_lost, ".", color = "red")
# plt.plot(tE_found, umin_found, ".", color = "green")
# plt.xlabel("tE")
# plt.ylabel("umin")
# plt.title("umin-tE")
# plt.show()
# #plt.savefig("umin_tE_plt.jpg")


# # skewness-neumann-diagramm
# plt.figure()
# plt.plot(skew_ML, neumann_ML, ".", color = "green")
# plt.plot(skew_noML, neumann_noML, ".", color = "red")
# plt.xlabel("Skewness")
# plt.ylabel("Neumann-Wert")
# plt.title("Skewness-neumann")
# plt.show()
# plt.savefig("skew_nm_plt1.jpg")

# if np.count_nonzero(detect_lst_binary == 1) != 0: #wenn kein sog "Fehlversuch"
#     print("verlorene ML: ", lost)
#     print("scheinbare ML: ", trap)
#     print("gefundene ML: ", found)
#     # print(truetruth_lst_binary)
#     # print(detect_lst_binary)
# else:
#         print("Noch nicht verstandener scheinbarer Fehlversuch. Nochmal ausführen bis es klappt.")

