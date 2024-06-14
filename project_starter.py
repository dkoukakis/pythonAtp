# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 14:35:43 2024

@author: dkouk
"""
#IMPORT LIBRARIES

import fileinput
import sys
import scipy.io as sio
import os
from os import system
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import lognorm
import csv
import random
import math
import subprocess


#output_file.writeLines()
TOTAL_ERRORS = 0
TOTAL_SIMS = 0

PREV_TOTAL_ERRORS = 0
PREV_TOTAL_SIMS = 0

ground_sims = 0
reset_b = 1
# Initial values of .atp file
#PAI = '0000. $$'
i_0 = "999999." # Ipeak
f_0 = "9.99E-6" # Front duration
h_0 = "7.75E-5" # Time to half  9
s_0 = "9.999E10" # Maximum steepness

#system("cls")

#file = "C:\ATPRUN\BF_400kV_200_MED11.atp"  # .atp file address

def generate_random_I_peak(I_mean, sigma_ln):
    """
    Generate a random value for the peak lightning current I_peak 
    from a log-normal distribution defined by the mean I_mean and
    standard deviation sigma_ln of the logarithmic values.
    """
    #periorismoi revmatos
    samples = 0
    while samples < 1000 or samples > 300000:
        samples = np.random.lognormal(mean = np.log(I_mean), sigma = sigma_ln, size = 1)
    
    print(samples)
 
    return samples #I_peak_random
    

 #ipologizoume tis times me vasi to Ipeak
def calculate_tf(I_peak):                            #Calculating values
    if 3 <= I_peak <= 20000:
        return 1.77 * (I_peak/1000) ** 0.188
    elif I_peak > 20000:
        return 0.906 * (I_peak/1000) ** 0.411

def calculate_sm(I_peak):
    if 3 <= I_peak <= 20000:
        return 1.2 * (I_peak/1000) ** 0.171
    elif I_peak > 20000:
        return 0.65 * (I_peak/1000) ** 0.376
    
# Change values in file
def replacement(file, previousw, nextw):
    for line in fileinput.input(file, inplace=1):
        line = line.replace(previousw, nextw)
        sys.stdout.write(line)
    

# Constants
th = 7.75  # Duration to half-value (microseconds)
I_mean = 30100  # Mean of the peak lightning current (kA)
sigma_ln = 0.76  # Standard deviation of the log-normal distribution
D = 3.62
# Initialize
ip = 0
tf = 0
sm = 0

def continue_flag():                                                     #Decides when to stop simulations
    if TOTAL_SIMS == 0 or PREV_TOTAL_SIMS == 0 or TOTAL_ERRORS == 0 or TOTAL_SIMS<5:
        return 1
    if round(TOTAL_ERRORS / TOTAL_SIMS, 5) == round(PREV_TOTAL_ERRORS / PREV_TOTAL_SIMS, 5):
        return 0
   
   # if  TOTAL_ERRORS / TOTAL_SIMS == PREV_TOTAL_ERRORS / PREV_TOTAL_SIMS:
   #     return 0
    else:
        return 1
    
    pass

def write_to_csv(data):                                        #writing data to csv (flashover and Ip)
    with open('output.csv', 'a', newline='\n') as file:
        writer = csv.writer(file)
        # Write the row
        writer.writerow(data)

def run_process():                               #Main Function
    global file
    global pfile
    global mfile
    global rfile
    global ip
    global tf
    global sm
    global PAI
    global i_0
    global f_0
    global s_0
    global h_0
    global TOTAL_SIMS
    global TOTAL_ERRORS
    global PREV_TOTAL_ERRORS
    global PREV_TOTAL_SIMS
    global ground_sims
    global reset_b
    
    
    PAI = "PAI =0000. $$"
    i_0 = "999999." # Ipeak            initializing
    f_0 = "9.99E-6" # Front duration
    h_0 = "7.75E-5" # Time to half  9
    s_0 = "9.999E10" # Maximum steepness
    
    egm_A = 10
    egm_B = 0.65	
    egm_G = 1/0.55
    egm_h = 41.43
    reset_b = 1

    #random_int = 0
    la = []
    lb = []
    lc = []
    ip = generate_random_I_peak(I_mean, sigma_ln)[0]
    tf = calculate_tf(ip)
    sm = calculate_sm(ip)
    egm_I = ip/1000
    random_int = random.randint(0,360) #PAi apo 0 eos 360
    PAI_str = "PAI ="+ str(random_int) + ". $$"
    
    # Convert to strings with desired precision
    peak_str = str(round(ip)) + '.'
    front_str = "{:.2f}".format(round(tf, 2)) + "E-6"
    half_str = str(round(th, 2)) + "E-5" 
    #steepness_str = str(round(sm, 3)) + "E10"
    steepness_str = "{:.3f}".format(round(sm, 3)) + "E10"

    print(peak_str, front_str, half_str, steepness_str)
    
    values_Y = np.random.randint(0, 500)
    values_X = np.random.randint(0, 175)
    discretized_values_X = int(np.round(values_X / 5) * 5)
    discretized_values_Y = int(np.round(values_Y / 5) * 5)
    print("Lightning Strike Location=", discretized_values_X, discretized_values_Y)
    egm_S = egm_A *(egm_I**egm_B)
    egm_D = egm_S/ egm_G
    
    if egm_h < egm_D:
        egm_R = math.sqrt(egm_S**2 - (egm_D-egm_h)**2)
    elif egm_h >= egm_D:
        egm_R = egm_S

    distance = math.sqrt((0 - discretized_values_X)**2 + (2.8 - discretized_values_Y)**2) 
    
    if egm_R <= distance and discretized_values_Y > 2.8:
        ground_sims = ground_sims + 1
        print("lightning stroke the ground",ground_sims)
        
        #write_to_csv([ip,"Ground"])
        reset_b = 0
        pass
    elif egm_R > distance or discretized_values_Y < 2.8 :
        # Perform the replacements in the ATP file in order to run atp with new values
        print("lightning stroke the conductor")
        rfile = r"C:\ATPRUN\BF_400kV_200_MED11" + '_' + str(discretized_values_X) + "m.atp"
        file = "C:\ATPRUN\BF_400kV_200_MED11" + '_' + str(discretized_values_X) + "m.atp"
        plfile = r"C:\ATPRUN\BF_400kV_200_MED11" + '_' + str(discretized_values_X) + "m.pl4"
        matfile = r"C:\ATPRUN\BF_400kV_200_MED11" + '_' + str(discretized_values_X) + "m.mat"
        
        replacement(file, PAI, PAI_str)
        replacement(file, i_0, peak_str)
        replacement(file, f_0, front_str)
        replacement(file, h_0, half_str)
        replacement(file, s_0, steepness_str)
    
        
        
        os.chdir('C:\EEUG18\IntelF_ATP')
        command = f'tpgigi64.exe disk {file} s -r'
        try:
            result = subprocess.run(command, shell=True, check=True, text=True)
            print("Command executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Command execution failed with error: {e}")
        os.chdir('C:/Users/dkouk/Desktop/SIM')
        
        command =f'C:\Pl42mat09\pl42mat.exe {plfile}'
        subprocess.run(command)
        
        # Load the MAT file in PYTHON
        #data = sio.loadmat('C:\ATPRUN\BF_400kV_200_MED11.mat')
        data = sio.loadmat(matfile)
        #preparing for value reset on file
        PAI = PAI_str
        i_0 = peak_str
        f_0 = front_str 
        h_0 = half_str
        s_0 = steepness_str
        print("~~~~")
        PREV_TOTAL_SIMS = TOTAL_SIMS
        PREV_TOTAL_ERRORS = TOTAL_ERRORS
        TOTAL_SIMS += 1
       
        #print("~~~~")     leader
        la = data['mLa']
        lb = data['mLb']
        lc = data['mLc']
        max_la = max(la[:,0])  # Maximum value of Leader
        max_lb = max(lb[:,0])
        max_lc = max(lc[:,0])
        
       
        print("maxla:", max_la)
        print("maxlb:", max_lb)
        print("maxlc:", max_lc)
        

        #a1 array with La,Lb,Lc values  for better output to csv
        a1 = [0,0,0]  
        if (max_la>=0.95*D) or (max_lb>=0.95*D) or (max_lc>=0.95*D): #flashover a1[]=1
            if max_la>=0.95*D:
                a1[0] = 1
            if max_lb>=0.95*D:
                a1[1] = 1
            if max_lc>=0.95*D:
                a1[2] = 1
            #write_to_csv([ip,a1[0],a1[1],a1[2]])    
            
            TOTAL_ERRORS +=1
        write_to_csv([ip,a1[0],a1[1],a1[2],random_int ,discretized_values_X, discretized_values_Y])  
        pass 
      
       
    

 
    #replacing initial values on atp file
def reset():
    global file
    global i_0
    global f_0
    global s_0
    global h_0
    # Perform the replacements in the ATP file reset
    replacement(file, PAI, "PAI =0000. $$")
    replacement(file, i_0, "999999.")
    replacement(file, f_0, "9.99E-6")
    replacement(file, h_0,  "7.75E-5")
    replacement(file, s_0, "9.999E10")
    print("RESET = ",i_0 , f_0 , h_0, s_0, PAI)
    pass

write_to_csv(['Ipeak','a','b','c',"PAI",'X','Y']) #first row of csv
while continue_flag(): 
    
        run_process()  
        if reset_b == 1 :
            reset()
        print("TOTAL ERRORS:",TOTAL_ERRORS)
        print("TOTAL SIMS:",TOTAL_SIMS)
        if TOTAL_SIMS > 0 :
            print("TOTAL ERRORS RATE",round(TOTAL_ERRORS / TOTAL_SIMS, 6))
        print("THUNDER GROUND:",ground_sims)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("  ")
        os.chdir('C:\EEUG18\IntelF_ATP')
        tmp_files = [f for f in os.listdir('.') if f.endswith('.tmp')]
        for tmp_file in tmp_files:
            os.remove(tmp_file)   
        os.chdir('C:/Users/dkouk/Desktop/SIM')  

write_to_csv(["Total lightning on ground:",ground_sims])
write_to_csv(["ERROR RATE=",round(TOTAL_ERRORS / TOTAL_SIMS, 6),"TOTAL SIMS=",TOTAL_SIMS,"TOTAL ERRORS =",TOTAL_ERRORS])
# After finishing processing the simulation, delete the .tmp files
tmp_files = [f for f in os.listdir('.') if f.endswith('.tmp')]
for tmp_file in tmp_files:
  os.remove(tmp_file)     
  
  
