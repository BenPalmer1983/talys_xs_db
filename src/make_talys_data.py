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
    try:
      if(len(sys.argv) == 2):
        make_talys_data.proc_id = int(sys.argv[1])
    except:
      exit()

    # Get Environment Variables
    proc_count = os.environ.get('PROC_COUNT')  
    if(proc_count != None):
      make_talys_data.proc_count = int(proc_count)   
    isotopes_file = os.environ.get('ISOTOPES')  
    if(isotopes_file != None):
      make_talys_data.isotopes_file = isotopes_file         
    talys_bin = os.environ.get('TALYS_BIN')
    if(talys_bin != None):
      make_talys_data.talys_bin = talys_bin    

   
    projectiles = os.environ.get('PROJECTILES')
    if(projectiles != None):
      make_talys_data.projectiles = projectiles.split(",")  
    
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

    print("Processing [" + str(make_talys_data.proc_id) + "]: ", p, Z, S, A, end="...")

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






def main():
  make_talys_data.run()

if __name__ == "__main__":
  main()    






