import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import norm, skew, kurtosis
from scipy.optimize import curve_fit as fit
import random
import time

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
class O_indices: #object for indices as "objectid", not as "lc[0]"
    n_index = 0
    a_hmjd = 1
    a_mag = 2
    n_umin = 3
    n_tE = 4
    a_fit_output = 5 #first entry in fit-output-array
o_indices = O_indices()

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
C = 0 # parameter for magnitude-calculation
LCamount = 20 # x LCs will be generated
n_max_chi_squared = 3 
found = 0
lost = 0 
trap = 0

# LISTS
lightc_lst = [0 for i in range(LCamount)] # stellt synthetischen Datensatz dar -> pro LC: Liste wie [Index (-> Object-ID), Magnitudenwerte, Zeitpunkte] 
detect_lst_binary = np.zeros(LCamount) # Array gefilterter ML-Events, np.zeros(x) macht Liste mit x Nullen
truetruth_lst_binary = np.zeros(LCamount) # Array mit tatsächlichen ML-Events -> muss Liste sein, da np.array keine arrays speichern kann aber kein Problem, da bei ZTF kein lclist erzeugt werden muss
lightc_lst_filtered = [] # Index (wie object ID) wird in Liste eingefügt -> am Schluss gezählt, ob alle Kriterien erfüllt
skew_lst = np.zeros(LCamount) # Skewness-Werte alles LC
std_lst = np.zeros(LCamount) # Standardabw-Werte alles LC
neumann_lst = np.zeros(LCamount)
umin_lost = []
tE_lost = []
umin_found = []
tE_found = []
filtered_lst = []
skew_ML = []
skew_noML = []
neumann_ML = []
neumann_noML = []
a_all_MLs = []

# FUNCTIONS
def f_ML_theo(n_d, n_umin, n_tE, n_I, n_t_max): #theoretische ML-Funktion, input = time-array, output = mag-array
    #umin => between 0 and 1 - the smaller, the bigger the amplitude
    #tE => duration of Event - the bigger, the wider the curve
    #I => intensity I = (light intensity)/Area of star without amplification
    #t_max => time when amplification A of I reaches maximum a
    n_u = np.sqrt(n_umin**2 + ((n_d-n_t_max)/n_tE)**2)
    if n_u*np.sqrt(n_u**2 + 4) != 0:
        n_A = n_I*((n_u**2 + 2) / (n_u*np.sqrt(n_u**2 + 4))) 
        n_M = -2.5*np.log10(n_A) # conversion luminosity to magnitude
    else: n_M = -10 #if umin = 0 and d = t0, amplitude theoretically becomes infinite 
    return n_M

def f_ML_theo_for_array(a_t, n_umin, n_tE, n_I, n_t_max):
    a_theo_mag = []
    for n_t in a_t:
        a_theo_mag.append(f_ML_theo(n_t, n_umin, n_tE, n_I, n_t_max))
    return a_theo_mag
    
# FUNCTIONS
def f_ML_theo(n_d, n_umin, n_tE, n_I, n_t_max): #theoretische ML-Funktion, input = time-array, output = mag-array
    #umin => between 0 and 1 - the smaller, the bigger the amplitude
    #tE => duration of Event - the bigger, the wider the curve
    #I => intensity I = (light intensity)/Area of star without amplification
    #t_max => time when amplification A of I reaches maximum a
    n_u = np.sqrt(n_umin**2 + ((n_d-n_t_max)/n_tE)**2)
    if n_u*np.sqrt(n_u**2 + 4) != 0:
        n_A = n_I*((n_u**2 + 2) / (n_u*np.sqrt(n_u**2 + 4))) 
        n_M = -2.5*np.log10(n_A) # conversion luminosity to magnitude
    else: n_M = -10 #if umin = 0 and d = t0, amplitude theoretically becomes infinite 
    return n_M

def f_ML_theo_for_array(a_t, n_umin, n_tE, n_I, n_t_max):
    a_theo_mag = []
    for n_t in a_t:
        a_theo_mag.append(f_ML_theo(n_t, n_umin, n_tE, n_I, n_t_max))
    return a_theo_mag


def fit(f_ML_theo_for_array, a_x_t, a_y_mag): # returns number: optimal difference and array: (umin, tE, I, t_max)
    a_differences = [] 
    a_a_params = []
    # Limits (numbers) - parameters beyond these are not sensible
    
    n_min_mag = min(a_y_mag)
    n_max_mag = max(a_y_mag)
    
    n_min_t = int(min(a_x_t))
    n_max_t = int(max(a_x_t))
    
    n_min_tE = 10
    n_max_tE = n_max_t - n_min_t
    n_steps_umin = 5  # range()-function takes ints only -> multiplies value do eliminate decimal stuff and divides back again
    n_steps_mag = 5
    start_fit = time.time()
    for n_umin in [(1/n_steps_umin)*x for x in range(1,n_steps_umin)]: # umin has to be between 0 and 1 but range doesn't work for floats - make list of ints and divide again
        for n_tE in range(n_min_tE, n_max_tE, 10):
            for n_mag in [(1/n_steps_mag)*x for x in range(int(n_steps_mag*n_min_mag), int(n_steps_mag*n_max_mag))]: #for I-calculation, gets converted later
                n_max_tmax = int(n_max_t - 0.5*n_tE)
                n_min_tmax = int(n_min_t + 0.5*n_tE)
                if n_min_tmax >= n_max_tmax: # manchmal kann tE zu gross werden für kleines Zeitintervall, sodass Fehler entstehen können
                    continue
                else:
                    for n_t_max in range(n_min_tmax, n_max_tmax, 10): 
                            a_theo_mag = f_ML_theo_for_array(
                                a_x_t, 
                                n_umin, 
                                n_tE, 
                                10**(n_mag/-2.5), # needs I as input but data in mag - conversion here
                                n_t_max
                            )
                            chi_squared = np.sum(
                                [
                                    ((a_y_mag[x] - a_theo_mag[x])**2)/a_theo_mag
                                    for x
                                    in range(len(a_y_mag))
                                ]
                            )
                            a_differences.append(chi_squared) # save in list and then calculate minimum 
                            a_a_params.append([n_umin, n_tE, 10**(n_mag/-2.5), n_t_max])
    stop_fit = time.time()
    print(stop_fit-start_fit)
    n_optimal_difference = min(a_differences)    
    return [n_optimal_difference, a_a_params[a_differences.index(n_optimal_difference)]]
        


# SYNTHETIC LC GENERATOR + FILTERING -> Produktion künstlicher LC -> random ML-Events oder nicht 
for i in range(LCamount):   
    ML_yesorno = random.randint(0, probability) #Wahrscheinlichkeit von 1/40
    magpointamount = random.randint(magpointamount_min, 200)
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
            M = f_ML_theo(t[x], umin, tE, mean_luminosity, t0)  + random.gauss(0, mean_std) # bei beiden Gauss-Rauschen machen
            mag[x] = M
        a_all_MLs.append([t, mag])
        fit = fit(f_ML_theo_for_array, t, mag)
        lightc_lst[i] = np.array([i, t, mag, umin, tE, fit], dtype = object)
        if fit[0] < n_max_chi_squared: 
            found += 1
        else: 
            lost += 1

        plt.figure() #make coordinate system
        plt.plot(t, mag,".", color = "red")#t,mag = lists! -> A(t)+0.2*random -> adds random number to whole list -> for loop to handle each value separately!
        plt.plot()

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
        fit = fit(f_ML_theo_for_array, t, mag)
        lightc_lst[i] = np.array([i, t, mag, None, None, fit], dtype = object)
        if fit[0] < n_max_chi_squared: 
            trap += 1
        # plt.figure() # make coordinate system
        # plt.plot(t, mag,".", color = "red")#t,a = lists! -> A(t)+0.2*random -> adds random number to whole list -> for loop to handle each value separately!

print("verlorene ML: ", lost)
print("scheinbare ML: ", trap)
print("gefundene ML: ", found)
print([(a_LC[o_indices.n_tE], a_LC[o_indices.a_fit_output[1][1]]) for a_LC in lightc_lst])
print([(a_LC[o_indices.n_umin], a_LC[o_indices.a_fit_output[0][0]]) for a_LC in lightc_lst]) # print list of tuples with 
#first entry = true parameter value
# and second entry = fitted parameter
