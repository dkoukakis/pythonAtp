# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 14:35:43 2024

@author: dkouk
"""
#IMPORT LIBRARIES
import math
import random
from os import walk
import shutil
import fileinput
import sys
import scipy.io as sio
import os
from os import system
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import lognorm
import csv
import subprocess
Ground_Sims = 0
TOTAL_ERRORS = 0
TOTAL_SIMS = 0
#Ipeak_array = []
a1 = []

# Initializing the values that count errors
PREV_TOTAL_ERRORS = 0
PREV_TOTAL_SIMS = 0
#15LIGHT -1  -999999.   9.99E-6   7.75E-5    -8888.  9.999E10
#15LIGHT -1  -999999.   9.99E-6   7.75E-5    -8888.  9.999E10
# Initial values of .atp file



# Generate Ipeak samples using a lognormal distribution
def generate_random_I_peak(I_mean, sigma_ln):
   
    samples = 0
    while samples < 1000 or samples > 300000:
        samples = np.random.lognormal(mean = np.log(I_mean), sigma = sigma_ln, size = 1)
    print(samples)
   
    return samples #I_peak_random
    



# Calculating values
def calculate_tf(I_peak):
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
def replacement(runfile1, previousw, nextw):
    for line in fileinput.input(runfile1, inplace=1):
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
egm_A = 10
egm_B = 0.65	
egm_G = 1/0.55
egm_h = 41.43
reset_b=1

# Defines the function that stops the simulation when the error rate diverges
def continue_flag():
    if TOTAL_SIMS == 0 or PREV_TOTAL_SIMS == 0 or TOTAL_ERRORS == 0 or TOTAL_SIMS < 10:
        return 1
    if round(TOTAL_ERRORS / TOTAL_SIMS, 5) == round(PREV_TOTAL_ERRORS / PREV_TOTAL_SIMS, 5):
        return 0
    else:
        return 1
    pass

# Writes the output in a .csv file
def write_to_csv(data):
    with open('output.csv', 'a', newline='\n') as file:
        writer = csv.writer(file)
        # Write the row
        writer.writerow(data)
        
# Main function of the code
def run_process():
    global runfile1
    global plfile
    global matfile
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
    global Ipeak_array
    global Ground_Sims
    global a1
    global egm_A
    global egm_B
    global egm_G
    global egm_h
    global reset_b
    global file
   # Reset condition when lightning strikes the ground
    reset_b=1
    
    # Initial values of the original .atp file
    PAI = "PAI =0000. $$"
    i_0 = "999999." # Ipeak
    f_0 = "9.99E-6" # Front duration
    h_0 = "7.75E-5" # Time to half  9
    s_0 = "9.999E10" # Maximum steepness
    
    # Generate 2D grid of coordinates
    values_Y = np.random.randint(0, 365)

    values_X = np.random.randint(0, 175)

    # Discretize the values per 5 meters
    discretized_values_X = int(np.round(values_X / 5) * 5)
    discretized_values_Y = int(np.round(values_Y / 5) * 5)
    #discretized_values_X = 100
    #discretized_values_Y = 335
    Str_value_X = str(discretized_values_X)
    print("Lightning Strike Location=", discretized_values_X, discretized_values_Y)
  
    # Generate a random Ipeak value from the predetermined sample generated at the start, 
    # then calculate tf and sm values based on ip
    ip = generate_random_I_peak(I_mean, sigma_ln)[0]
    tf = calculate_tf(ip)
    sm = calculate_sm(ip)
    
    # Generate a random int between 0 and 360 
    random_int = random.randint(0,360)
    PAI_str = "PAI ="+ str(random_int) + ". $$"
    print(PAI_str)

    # Convert to strings with desired precision
    peak_str = str(round(ip)) + '.'
    print(tf)
    front_str = "{:.2f}".format(round(tf, 2)) + "E-6"
    half_str = str(round(th, 2)) + "E-5" 
    steepness_str = "{:.3f}".format(round(sm, 3)) + "E10"
    print("Start of Simulation")
    print(peak_str, front_str, half_str, steepness_str)
    
    # Calculate variables for the EGM 
    egm_ip = ip/1000
    egm_S = egm_A * (egm_ip**egm_B)
    egm_D = egm_S/(egm_G)
    
    
    if egm_h < egm_D:
       egm_R = math.sqrt(egm_S**2 - (egm_D-egm_h)**2)
    elif egm_h >= egm_D:
       egm_R = egm_S
       
    # Calculates the Euclidean Distance from the location the struck to the transmission line
    distance = math.sqrt((0 - discretized_values_X)**2 + (2.8 - discretized_values_Y)**2)
    print("egm_R =", egm_R, ", Distance =", distance)
    
    # If statement to determine if lightning struck the ground or the conductor
    if egm_R <= distance and discretized_values_Y > 2.8:
        Ground_Sims +=1
        print("Lightning struck the ground")
        print("Ground Sims=", Ground_Sims)
        #write_to_csv([ip,'Ground'])
        reset_b = 0
        pass
        #write_to_csv([ip,'Ground'])
        
    elif egm_R > distance or discretized_values_Y < 2.8:
        print("Lightning struck the Conductor")
        
        # Programm picks the appropretiately named file
        runfile1 = "C:\ATPRUN\BF_400kV_200_MED11" +'_' + Str_value_X + 'm.atp'
        plfile = "C:\ATPRUN\BF_400kV_200_MED11" + '_' + Str_value_X + 'm.pl4'
        matfile = "C:\ATPRUN\BF_400kV_200_MED11" + '_' + Str_value_X + 'm.mat'
        
    
    # Perform the replacements in the ATP file
        replacement(runfile1, PAI, PAI_str)
        replacement(runfile1, i_0, peak_str)
        replacement(runfile1, f_0, front_str)
        replacement(runfile1, h_0, half_str)
        replacement(runfile1, s_0, steepness_str)
    

    #Ipeak_array += [peak_str]
    
    
      
   
   
        # Shell subprocess to execute the ATP core with the atp file
        os.chdir('C:\EEUG18\IntelF_ATP')
        command = f'tpgigi64.exe disk {runfile1} s -r'
        try:
            result = subprocess.run(command, shell=True, check=True, text=True)
            print("Command executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Command execution failed with error: {e}")
        os.chdir(r'C:/Users/George Diamantis/Desktop/Diplo/sim')
        
        command =f'C:\Pl42mat09\pl42mat.exe {plfile}'
        subprocess.run(command)
        plotxy = sio.loadmat(matfile)
  
    
     #makes a copy each time .atp file runs
     # Used in the troubleshooting stage of developing our code
        #filenames = next(walk("C:/Users/George Diamantis/Desktop/Diplo/Copies"), (None, None, []))[2]

       # if len(filenames)>0:
            #shutil.copy2("C:\ATPRUN\BF_400kV_200_MED11" +'_' + Str_value_X + 'm.atp', "C:/Users/George Diamantis/Desktop/Diplo/Copies/BF_400kV_200_MED11" +'_' + Str_value_X + '_' +str(len(filenames))+"m.atp" )
       # else:
            #shutil.copy2("C:\ATPRUN\BF_400kV_200_MED11" +'_' + Str_value_X + 'm.atp', "C:/Users/George Diamantis/Desktop/Diplo/Copies/BF_400kV_200_MED11" +'_' + Str_value_X + 'm.atp' )
       
        # Updates the values based on the random Ipeak 
        PAI = PAI_str
        i_0 = peak_str
        f_0 = front_str 
        h_0 = half_str
        s_0 = steepness_str
        #print("~~~~")
        
        # Error and Sims counters
        PREV_TOTAL_SIMS = TOTAL_SIMS
        PREV_TOTAL_ERRORS = TOTAL_ERRORS
    
        #print("~~~~")
        
        # Makes Arrays for mLa, mLb and mLc values from the loaded matlab file
        la = plotxy['mLa']
        lb = plotxy['mLb']
        lc = plotxy['mLc']
        max_la = max(la[:,0])  # Maximum value of Leader
        max_lb = max(lb[:,0])
        max_lc = max(lc[:,0])
    
   
        print("maxla:", max_la)
        print("maxlb:", max_lb)
        print("maxlc:", max_lc)
    
        TOTAL_SIMS +=1
        
        # Counts the backlfashover and then writes the output in the .csv file
        a1 = [0,0,0]
        if (max_la>=0.95*D) or (max_lb>=0.95*D) or (max_lc>=0.95*D):
            if max_la>=0.95*D:
                a1[0] = 1
            if max_lb>=0.95*D:
                a1[1] = 1
            if max_lc>=0.95*D:
                a1[2] = 1
        #write_to_csv([ip,a1[0],a1[1],a1[2]])

            TOTAL_ERRORS +=1
        
        write_to_csv([ip,a1[0],a1[1],a1[2], random_int, discretized_values_X, discretized_values_Y])
      
        

    pass

# Uses the replacement function to Reset the .atp file for the next simulation
def reset():
    global runfile1
    global PAI
    global i_0
    global f_0
    global s_0
    global h_0
    # Perform the replacements in the ATP file reset
    replacement(runfile1, PAI, "PAI =0000. $$")
    replacement(runfile1, i_0, "999999.")
    replacement(runfile1, f_0, "9.99E-6")
    replacement(runfile1, h_0,  "7.75E-5")
    replacement(runfile1, s_0, "9.999E10")
    print("Reset", PAI, i_0, f_0, h_0, s_0)
    
    pass

write_to_csv(['Ipeak','a','b','c', 'PAI', 'X', 'Y'])



# Criterion for the continuation of the simulation
while continue_flag():

         
        run_process() 
        if reset_b == 1:
            reset()
        print("TOTAL_ERRORS:", TOTAL_ERRORS)
        print("TOTAL_SIMS:", TOTAL_SIMS)
        if TOTAL_SIMS > 0 :
            print("Total Error Rate", round(TOTAL_ERRORS / TOTAL_SIMS, 6))
        print("Ground Sims=", Ground_Sims)
        #print("Previous Total Error Rate", round(PREV_TOTAL_ERRORS / PREV_TOTAL_SIMS, 3) )
        print("End of Simulation")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~")
        os.chdir('C:\EEUG18\IntelF_ATP')
        tmp_files = [f for f in os.listdir('.') if f.endswith('.tmp')]
        for tmp_file in tmp_files:
         os.remove(tmp_file)     
        os.chdir('C:/Users/George Diamantis/Desktop/Diplo/sim')
    
    #print("ERROR_RATE:", ERROR_RATE)
# After finishing processing the simulation, delete the .tmp files
