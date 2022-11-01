import numpy as np # für Mathematik
import os # operating system -> für Kommunikation mit dem System
import time # um die Zeit an einem bestimmten Zeitpunkt erhalten zu können - Geschwindigkeit messen
n_max_chi_value = 3 # bei anderen Wissenschaftlern verwendeter Maximalwert für Chi

# FUNCTIONS
def f_ML_theo(n_d, n_umin, n_tE, n_I, n_t_max): #theoretische ML-Funktion, input = time-Wert (integer), output = mag-Wert (float)
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

def f_ML_theo_for_array(a_t, n_umin, n_tE, n_I, n_t_max): # Anwendung der f_ML_theo()-Funktion auf alle Elemente eines t-arrays
    a_theo_mag = []
    for n_t in a_t:
        a_theo_mag.append(f_ML_theo(n_t, n_umin, n_tE, n_I, n_t_max))
    return a_theo_mag


def fit(f_ML_theo_for_array, a_x_t, a_y_mag): # returns number: optimal difference and array: (umin, tE, I, t_max)
    a_differences = [] # hier werden alle Chi-Werte abgespeichert und dann das Minimum herausgesucht
    a_a_params = [] # Parameterwerte des Minimums von oben werden danach als Output mitgegeben
    
    
    
    # Limits (numbers) - parameters beyond these are not sensible
    
    # es werden nur Werte innerhalb der Existierenden Werte eingesetzt, da etwas anderes ohnehin sinnlos wäre (z.B. ein I von 10**(18/-2.5), obwohl tiefster mag-Wert =20
    n_min_mag = min(a_y_mag)
    n_max_mag = max(a_y_mag)
    
    n_min_t = int(min(a_x_t))
    n_max_t = int(max(a_x_t))
    
    # Microlensing-Events mit tE < 10 oder tE > Messdauer können schwer oder nicht erkannt werden, da die Funktion im Rauschen verschwindet oder zu flach ist
    n_min_tE = 10
    n_max_tE = n_max_t - n_min_t
    n_steps_umin = 5  # range()-function takes ints only -> multiplies value do eliminate decimal stuff and divides back again
    n_steps_mag = 5
    start_fit = time.time() # gibt genauen Zeitpunkt des Lesens der Zeile wieder
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
    print(stop_fit-start_fit) # Dauer Loop
    n_optimal_difference = min(a_differences)    
    return [n_optimal_difference, a_a_params[a_differences.index(n_optimal_difference)]] # output: Liste
        

class O_indices: #object for indices as "objectid", not as "lc[0]" -> für die Übersichtlichkeit
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

dir = "D:/ZTF_data/all_filtered_LCs" # hier Pfad zum Ordner, der alle Daten enthält 
# FILTER 
for s_path_root, a_s_folder, a_s_file in os.walk(dir): # für alle Ordner, Unterordner und Files des root-directorys
    for s_name_file in a_s_file:
        start = time.time()
                # process the data
        n_index = a_s_file.index(s_name_file)
        print(f"-----------processing----------------")
        print(f"file: {n_index}") # wissen, wo man steht
        print("")
        s_path_file = s_path_root + "/" + s_name_file # mache aufrufbaren Pfad (string), um auf File zuzugreifen
        a_a_data = np.load(s_path_file, allow_pickle=True) # allow_pickle = True - error in new module version, needs this in order to funtion
        
        a_a_filtered = [ # array contains arrays of LC-array and minimal fitted difference-value-number
            (a_LC, fit(f_ML_theo_for_array, a_LC[o_indices.a_hmjd], a_LC[o_indices.a_mag])) for a_LC in a_a_data # erstelle Liste aller LC, wenn Fitting-Programm bestanden
            if 
            fit(f_ML_theo_for_array, a_LC[o_indices.a_hmjd], a_LC[o_indices.a_mag])[0] < n_max_chi_value # erster Eintrag in Output Liste = Chi^2
        ]
        np.save(s_name_file + "_fitted", a_a_filtered) # File mit dem Namen s_name_file_fitted mit dem Inhalt a_a_filtered wird gespeichert
        stop = time.time() 
        print(stop-start) # wie lange das File brauchte
         
               
