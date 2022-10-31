import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import norm, skew, kurtosis
from scipy.optimize import curve_fit as fit
import random

"""
Der Datensatz generiert Lichtkurvenliste der Anzahl LCamount. Jede Liste enthält 7 Einträge:
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
probability = 1 # pro x (Probability) LC hat es ca. 1/x ML-Event
magpointamount_min = 30 # Mindestanzahl Messungen
t0 = 0 # Zeitpunkt max. Helligkeit
surveylength = 500 # wie lange gesamte Messung dauerte = maximale Eventdauer
mean_skew = -0.22994225279524635  #Mittelwert von 2 fields 
mean_std = 0.15856555  # Mittelwert von 2 fields 
mean_mag = 20.421268  # Mittelwert von 2 fields
mean_luminosity = 10**(mean_mag/(-2.5)) # convert magnitude-mean to luminosity-value for multiplication by amplification factor 
mean_neumann = 1.6 # circa
C = 0 # parameter for magnitude-calculation
LCamount = 1500 # x LCs will be generated -> here: 2000 because 10h time to calculate overnight
max_skew = 0.9
max_neumann = 1.2
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

#Lists 
lightc_lst = [0 for i in range(LCamount)] # stellt synthetischen Datensatz dar -> pro LC: Liste wie [Index (-> Object-ID), Magnitudenwerte, Zeitpunkte]
detect_lst_binary = np.zeros(LCamount) # Array gefilterter ML-Events, np.zeros(x) macht Liste mit x Nullen
truetruth_lst_binary = np.zeros(LCamount) # Array mit tatsächlichen ML-Events -> muss Liste sein, da np.array keine arrays speichern kann aber kein Problem, da bei ZTF kein lclist erzeugt werden muss
lightc_lst_filtered = [] # Index (wie object ID) wird in Liste eingefügt -> am Schluss gezählt, ob alle Kriterien erfüllt

umin_found = [] 
umin_lost = []

tE_found = [] 
tE_lost = []

skew_ML = []
skew_noML = []

neumann_ML = []
neumann_noML = []

lost = 0
trap = 0
found = 0

# SYNTHETIC LC GENERATOR + FILTERING -> Produktion künstlicher LC -> random ML-Events oder nicht 
for i in range(LCamount):   
    ML_yesorno = random.randint(0, probability) #Wahrscheinlichkeit von 1/40
    magpointamount = random.randint(magpointamount_min, 100)
    if ML_yesorno == 1: #falls Microlensing-Event
        t = np.zeros(magpointamount) # (start, end, Anz. Striche zwischen start und end) -> x-Achse
        # freie Parameter hängen von t ab -> verändern sich mit der Zeit -> Körper bewegen sich
        mag = np.zeros(magpointamount)
        umin = random.random()
        tE = random.randint(1, surveylength) # Zeitdauer, um Einstein-Radius zurückzulegen
        for x in range(magpointamount):
            t[x] = random.randint(-(1/2)*surveylength, (1/2)*surveylength)
        np.ndarray.sort(t)
        for x in range(magpointamount):  # Helligkeit A abhängig von u, u abhängig t
            M = theo(t[x], umin, tE)  + random.gauss(0, mean_std) # bei beiden Gauss-Rauschen machen
            mag[x] = M
            lc_skew_value = skew(mag)
            lc_neumann_value = neumann(mag)

        skew_ML.append(lc_skew_value)
        neumann_ML.append(lc_neumann_value)

        lightc_lst[i] = np.array([i, t, mag, umin, tE, lc_skew_value, lc_neumann_value], dtype = object)
        if (lc_skew_value < max_skew) and (lc_neumann_value < max_neumann):
            found += 1
            umin_found.append(umin)
            tE_found.append(tE)

        else:
            lost += 1
            umin_lost.append(umin)
            tE_lost.append(tE)

        # plt.figure() #make coordinate system
        # plt.plot(t, mag,".", color = "red")#t,mag = lists! -> A(t)+0.2*random -> adds random number to whole list -> for loop to handle each value separately!

    else: 
        
        t = np.zeros(magpointamount) # (start, end, Anz. Striche zwischen start und end) -> x-Achse
        # freie Parameter hängen von t ab -> verändern sich mit der Zeit -> Körper bewegen sich
        mag = np.zeros(magpointamount)
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
        if (lc_skew_value < max_skew) and (lc_neumann_value < max_neumann):
            trap += 1

        # plt.figure() # make coordinate system
        # plt.plot(t, mag,".", color = "red")#t,a = lists! -> A(t)+0.2*random -> adds random number to whole list -> for loop to handle each value separately!


# umin-tE-Diagramm:
plt.figure()
plt.plot(tE_lost, umin_lost, ".", color = "red")
plt.plot(tE_found, umin_found, ".", color = "green")
plt.xlabel("tE")
plt.ylabel("umin")
plt.show()

x = [x for x in range(-5, 3)]
y = []
   
for i in x:
    y.append(1.2)


v = [0.01*v for v in range(110, 300)]
z = []

for i in v:
    z.append(10**((i - 1.3)/-0.4) - 1.6)

m = [0.1*m for m in range(10*int(min(skew_ML)), 12)]
n = []

for i in m:
    n.append(-0.3*i + 1.1)
    

# skewness-neumann-diagramm
plt.figure()
plt.plot(skew_ML, neumann_ML, ".", color = "blue")
plt.plot(skew_noML, neumann_noML, ".", color = "red")
plt.plot(x, y, "-", color = "pink")
plt.plot(z, v, "-", color = "green")
plt.plot(m, n, "-", color = "orange")
plt.axvline(x = 0.9, color = "pink")
plt.xlabel("Skewness")
plt.ylabel("Von-Neumann-Statistik")
plt.show()

    # if np.count_nonzero(detect_lst_binary == 1) != 0: #wenn kein sog "Fehlversuch"
    #     print("verlorene ML: ", lost)
    #     print("scheinbare ML: ", trap)
    #     print("gefundene ML: ", found)
    #     print("skew ", max_skew, "neumann: ", max_neumann,"the bigger the better the filter: ", found/((lost + 1)*(trap+1))) # -> the bigger this value, the better the filter, trap+1 because otherwise /zero
    #     # print(truetruth_lst_binary)
    #     # print(detect_lst_binary)
# else:
#         print("Noch nicht vers8j8j888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888tandener scheinbarer Fehlversuch. Nochmal ausführen bis es klappt.")
