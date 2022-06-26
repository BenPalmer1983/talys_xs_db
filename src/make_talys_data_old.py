from isotopes import isotopes
import os
import numpy
import sys
import subprocess


class make_talys_data:

  proc_id = 0
  proc_count = 1
  isotopes_file = '../data/isotopes.pz'
  wd = None
  talys_bin = 'talys'
  projectiles = ['p']
  to_do = []
  lower_z = 3
  upper_z = 92
  lower_e = 1.0
  upper_e = 150.0
  inc_e = 1.0

  def run():
    print("Talys Data")
    exit()

    # Get Environment Variables
    isotopes_file = os.environ.get('ISOTOPES')  
    if(isotopes_file != None):
      make_talys_data.isotopes_file = isotopes_file         
    talys_bin = os.environ.get('TALYS')
    if(talys_bin != None):
      make_talys_data.talys_bin = talys_bin        
    out_dir = os.environ.get('OUTDIR')
    if(out_dir != None):
      make_talys_data.wd = out_dir    
    else:
      make_talys_data.wd = os.getcwd() + "/output"
    lower_z = os.environ.get('LOWER_Z')
    if(lower_z != None):
      make_talys_data.lower_z = int(lower_z)
    upper_z = os.environ.get('UPPER_Z')
    if(upper_z != None):
      make_talys_data.upper_z = int(upper_z)
    lower_e = os.environ.get('LOWER_E')
    if(lower_e != None):
      make_talys_data.lower_e = float(lower_e)
    upper_e = os.environ.get('UPPER_E')
    if(upper_e != None):
      make_talys_data.upper_e = float(upper_e)
    inc_e = os.environ.get('INC_E')
    if(inc_e != None):
      make_talys_data.inc_e = float(inc_e)




    # Set isotopes file
    isotopes.set(make_talys_data.isotopes_file)

    # Make dirs
    make_talys_data.make_dirs()
    
    # Make ToDo list
    make_talys_data.make_todo()

    # Run Talys
    make_talys_data.run_talys()

    print("Complete.")
    exit()

  def make_dirs():
    make_talys_data.mkdir(make_talys_data.wd)
    for p in make_talys_data.projectiles:
      make_talys_data.mkdir(make_talys_data.wd + "/" + str(p))

  def make_todo():
    lower_z = make_talys_data.lower_z
    upper_z = make_talys_data.upper_z

    for p in make_talys_data.projectiles:
      ilist = isotopes.get_stable()
      for k in ilist.keys():
        if(k>=lower_z and k<=upper_z):
          Z = k
          S = isotopes.get_symbol(Z)
          Z = make_talys_data.pad_num(Z,3)
          for A in ilist[k]:
            A = make_talys_data.pad_num(A,3)
            dir = Z + "_" + S + "_" + A
            path = make_talys_data.wd + "/" + str(p) + "/" + dir
            make_talys_data.to_do.append({
                'Z': Z,
                'A': A,
                'S': S,
                'p': p,
                'path': path,
                'input_file': path + "/input.in",
                })
  

  def run_talys(): 
    for n in range(len(make_talys_data.to_do)):
      if(n % make_talys_data.proc_count == make_talys_data.proc_id):
        make_talys_data.run_isotope(n)


  def run_isotope(n): 
    Z = make_talys_data.to_do[n]['Z']
    A = make_talys_data.to_do[n]['A']
    S = make_talys_data.to_do[n]['S']
    p = make_talys_data.to_do[n]['p']
    path = make_talys_data.to_do[n]['path']
    input_file = make_talys_data.to_do[n]['input_file']

    print("Processing: ", Z, S, A, end="...")

    make_talys_data.mkdir(path)

    fh = open(input_file, 'w')
    fh.write("projectile " + str(p) + "\n")
    fh.write("element " + str(S) + "\n")
    fh.write("mass " + str(A) + "\n")
    fh.write("energy " + str(make_talys_data.lower_e) + " " + str(make_talys_data.upper_e) + " " +  str(make_talys_data.inc_e) + "\n")
    fh.write("ejectiles g n p d t h a outtype\n")
    fh.close()

    os.chdir(path)

    run_talys = True
    if(os.path.isfile('output.out')):
      line = subprocess.check_output(['tail', '-1', 'output.out'])
      if(b"TALYS team congratulates you with this successful" in line):
        run_talys = False
        print("exists.")

    if(run_talys):
      bin = make_talys_data.talys_bin
      cmd = bin + " < input.in > output.out"
      os.system(cmd)
      #      subprocess.run(cmd)
      print("complete.")

    



  def pad_num(inp, l=5):
    inp = str(inp)
    while(len(inp) < l):
      inp = "0" + inp 
    return inp 

  def mkdir(path):
    try:
      os.mkdir(path)
    except:
      pass


if(len(sys.argv) != 3 or sys.argv[1][0].lower() == 'h'):
  print("""
Talys run code

Example run:

#!/bin/bash
export ISOTOPES="/cloud/Code/python/talys/data/isotopes.pz"
export TALYS="/DATA/disk1/talys/bin/talys"
export OUTDIR="/media/ben/Archive1/tendl/created/output"
export TALYS_RUN="/cloud/Code/python/talys/src/make_talys_data.py"

python3 $TALYS_RUN 0 4
python3 $TALYS_RUN 1 4
python3 $TALYS_RUN 2 4
python3 $TALYS_RUN 3 4

  """)
  exit()

proc_id = 0
proc_count = 1
try:
  if(len(sys.argv) == 3):
    proc_id = int(sys.argv[1])
    proc_count = int(sys.argv[2])
except:
  pass



make_talys_data.proc_id = proc_id
make_talys_data.proc_count = proc_count
make_talys_data.run()


"""
isotopes.set('data/isotopes.pz')
ilist = isotopes.get_stable()


for k in ilist.keys():
  if(k>=3 and k<=92):
    Z = k
    S = isotopes.get_symbol(Z)
    
    dir_top = str(Z)
    while(len(dir_top)<3):
      dir_top = "0" + dir_top
    dir_top = dir_top + "_" + S
    mkdir("wd/" + dir_top)
    
    for A in ilist[k]:
      dir_b = str(A)
      while(len(dir_b)<3):
        dir_b = "0" + dir_b
      path = "wd/" + dir_top + "/" + dir_b
      mkdir(path)

      e = 100
      for i in range(1000):
        fh = open(path + "/" + str(numpy.round(e,1)) + ".in", 'w')
        fh.write("projectile p" + "\n")
        fh.write("element " + str(S) + "\n")
        fh.write("mass " + str(A) + "\n")
        fh.write("energy " + str(numpy.round(e/1000,1)) + "\n")
        fh.close()
        cmd = "talys < " + path + "/" + str(e) + ".in" + " > " + path + "/" + str(e) + ".out"
        os.system(cmd)

        e = e + 100
      print(S, Z, A)
      
    
"""



