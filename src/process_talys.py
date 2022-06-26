from pz import pz
from isotopes import isotopes
import os
import numpy
import sys
import subprocess





class process_talys:

  isotopes_file = None
  data_dir = None
  metastable = None
  levels = None
  product_xs = None

  data_source = {"TALYS", "https://tendl.web.psi.ch/tendl_2019/talys.html"}




  def run():
    # Get Environment Variables
    process_talys.isotopes_file = os.environ.get('ISOTOPES')
    process_talys.data_dir = os.environ.get('DATA_DIR')   

    if(process_talys.isotopes_file == None or process_talys.data_dir == None):
      if(process_talys.isotopes_file == None):
        print("Set ISOTOPES env variable - path to isotopes.pz file")
      if(process_talys.data_dir == None):
        print("Set DATA_DIR env variable - path to directory containing talys output files")
      exit()

    # Load isotopes
    isotopes.set(process_talys.isotopes_file)

    # List of files in data store
    process_talys.files = process_talys.file_list(process_talys.data_dir)    
    
    # Process levels - metastable, level, energy
    process_talys.process_levels()

    # Reaction products
    process_talys.process_products()

    # Reaction particles
    process_talys.process_particles()

    # Process elastic and non elastic xs
    process_talys.process_elastic()
    process_talys.process_nonelastic()


    d = {}
    d['info'] = {}
    d['info']['name'] = "Talys"
    d['info']['source'] = process_talys.data_source
    d['info']['help'] = """
Talys Cross Section Data

Dictionary split into several parts.
'info'
'metastable'
'levels'



metastable

Dictionary of product metastable levels and energies by metastable level (0=m, 1=n, 2=p and so on)

    """

    # Store data
    d['metastable'] = process_talys.metastable
    d['levels'] = process_talys.levels
    d['residual_xs'] = process_talys.product_xs
    d['particle_xs'] = process_talys.particle_xs
    d['elastic_xs'] = process_talys.elastic_xs
    d['nonelastic_xs'] = process_talys.nonelastic_xs
    
    process_talys.make_dir("talys")
    pz.save("talys/info.pz", d['info'], 'lzma')
    pz.save("talys/metastable.pz", d['metastable'], 'lzma')
    pz.save("talys/levels.pz", d['levels'], 'lzma')
    pz.save("talys/residual_xs.pz", d['residual_xs'], 'lzma')
    pz.save("talys/particle_xs.pz", d['particle_xs'], 'lzma')
    pz.save("talys/elastic_xs.pz", d['elastic_xs'], 'lzma')
    pz.save("talys/nonelastic_xs.pz", d['nonelastic_xs'], 'lzma')


 
  def file_list(path, path_list=[]):
    for file_name in os.listdir(path):
      file_path = path + "/" + file_name
      if(os.path.isdir(file_path)):
        path_list = process_talys.file_list(file_path, path_list)
      elif(os.path.isfile(file_path)):
        path_list.append(file_path)
    return path_list



  def process_levels():

    isotope_metastable_levels = {}
    temp_iml = {}

    for file_path in process_talys.files:
      file_name = file_path.split("/")
      file_name = file_name[-1]
      if(file_name[0:2] == "rp" and (file_name[-4:-2] == ".L")):
        fh = open(file_path, 'r')
        n = 0
        for line in fh:
          if(n == 0):
            product_a = int(line[27:30])
            product_s = line[30:32]
            product_z = isotopes.get_z(line[30:32])
            product_m = 0
            product_code = isotopes.get_code(product_z, product_a, product_m)
            state = line[35:47]
            level = 0
            if(state[0:6] != "Ground"):
              level = int(state[5:8])
              energy = float(line[47:55])
              if(product_code not in temp_iml):
                temp_iml[product_code] = []
              if([level, energy] not in temp_iml[product_code]):
                temp_iml[product_code].append([level, energy])
          n = n + 1
        fh.close()     

    for product_code in temp_iml.keys():
      if([0,0.0] not in temp_iml[product_code]):
        temp_iml[product_code].append([0,0.0])
      temp_iml[product_code].sort(key=lambda x: x[0])

    ms = {}
    for product_code in temp_iml.keys():
      if(product_code not in ms):
        ms[product_code] = {}
        for l in range(len(temp_iml[product_code])):
          ms[product_code][l] = {}
          ms[product_code][l]['ms'] = l
          ms[product_code][l]['level'] = temp_iml[product_code][l][0]
          ms[product_code][l]['energy'] = temp_iml[product_code][l][1]
    process_talys.metastable = ms

    levels = {}
    for product_code in temp_iml.keys():
      if(product_code not in levels):
        levels[product_code] = {}
        for l in range(len(temp_iml[product_code])):
          ln = temp_iml[product_code][l][0]
          levels[product_code][ln] = {}
          levels[product_code][ln]['ms'] = l
          levels[product_code][ln]['level'] = temp_iml[product_code][l][0]
          levels[product_code][ln]['energy'] = temp_iml[product_code][l][1]
    process_talys.levels = levels

    
      
  def process_products():

    #
    # Read the total (.tot) and level (.L...) files
    # If it's in levels, use that otherwise use totals
    # 

    totals = {}
    levels = {}
    product_xs = {}

    ###############################
    # TOTALS
    ###############################

    for file_path in process_talys.files:
      file_name = file_path.split("/")
      file_name = file_name[-1]
      if(file_name[0:2] == "rp" and file_name[-4:] == ".tot"):
        fh = open(file_path, 'r')
        n = 0
        for line in fh:
          if(n == 0):
            projectile = line[1:3].strip()
            target_a = int(line[6:9])
            target_s = line[9:11]
            target_z = isotopes.get_z(line[9:11])
            target_m = 0
            product_a = int(line[27:30])
            product_s = line[30:32]
            product_z = isotopes.get_z(line[30:32])
            product_m = 0
            product_code = isotopes.get_code(product_z, product_a, product_m)
 
            # Add to totals and final
            if(projectile not in totals.keys()):
              totals[projectile] = {}
            if(target_z not in totals[projectile].keys()):
              totals[projectile][target_z] = {}
            if(target_a not in totals[projectile][target_z].keys()):
              totals[projectile][target_z][target_a] = {}
            if(target_m not in totals[projectile][target_z][target_a].keys()):
              totals[projectile][target_z][target_a][target_m] = {}
            if(product_code not in totals[projectile][target_z][target_a][target_m].keys()):
              totals[projectile][target_z][target_a][target_m][product_code] = []

          elif(line[0] != "#" and line != ""):
            e = float(line[0:12])
            xs = float(line[12:24]) / 1000.0
            totals[projectile][target_z][target_a][target_m][product_code].append([e,xs])
            #print(e, xs)
          n = n + 1
        fh.close()

    # Sort arrays
    for p in totals:
      for tz in totals[p]:
        for ta in totals[p][tz]:
          for tm in totals[p][tz][ta]:
            for rc in totals[p][tz][ta][tm]:
              totals[p][tz][ta][tm][rc] = numpy.asarray(totals[p][tz][ta][tm][rc])
              totals[p][tz][ta][tm][rc] = numpy.sort(totals[p][tz][ta][tm][rc], axis=0, kind='mergesort')

    ###############################
    # LEVELS
    ###############################

    for file_path in process_talys.files:
      file_name = file_path.split("/")
      file_name = file_name[-1]
      if(file_name[0:2] == "rp" and (file_name[-4:-2] == ".L")):
        fh = open(file_path, 'r')
        n = 0
        for line in fh:
          if(n == 0):
            projectile = line[1:3].strip()
            target_a = int(line[6:9])
            target_s = line[9:11]
            target_z = isotopes.get_z(line[9:11])
            target_m = 0
            product_a = int(line[27:30])
            product_s = line[30:32]
            product_z = isotopes.get_z(line[30:32])
            product_code = isotopes.get_code(product_z, product_a, 0)
            state = line[35:47]

            level = 0
            if(state[0:6] != "Ground"):
              level = int(state[5:8])
            product_m = process_talys.levels[product_code][level]['ms']
            product_code = isotopes.get_code(product_z, product_a, product_m)

            # Add to levels
            if(projectile not in levels.keys()):
              levels[projectile] = {}
            if(target_z not in levels[projectile].keys()):
              levels[projectile][target_z] = {}
            if(target_a not in levels[projectile][target_z].keys()):
              levels[projectile][target_z][target_a] = {}
            if(target_m not in levels[projectile][target_z][target_a].keys()):
              levels[projectile][target_z][target_a][target_m] = {}
            if(product_code not in levels[projectile][target_z][target_a][target_m].keys()):
              levels[projectile][target_z][target_a][target_m][product_code] = []


          elif(line[0] != "#" and line != ""):
            e = float(line[0:12])
            xs = float(line[12:24]) / 1000.0
            levels[projectile][target_z][target_a][target_m][product_code].append([e,xs])
          n = n + 1
        fh.close()

    # Sort arrays
    for p in levels:
      for tz in levels[p]:
        for ta in levels[p][tz]:
          for tm in levels[p][tz][ta]:
            for rc in levels[p][tz][ta][tm]:
              levels[p][tz][ta][tm][rc] = numpy.asarray(levels[p][tz][ta][tm][rc])
              levels[p][tz][ta][tm][rc] = numpy.sort(levels[p][tz][ta][tm][rc], axis=0, kind='mergesort')


    ###############################
    # Make XS
    ###############################

    for p in levels.keys():
      for tz in levels[p].keys():
        for ta in levels[p][tz].keys():
          for tm in levels[p][tz][ta].keys():
            for pcode in levels[p][tz][ta][tm].keys():
              # Add to levels
              if(projectile not in product_xs.keys()):
                product_xs[projectile] = {}
              if(tz not in product_xs[projectile].keys()):
                product_xs[projectile][tz] = {}
              if(ta not in product_xs[projectile][tz].keys()):
                product_xs[projectile][tz][ta] = {}
              if(tm not in product_xs[projectile][tz][ta].keys()):
                product_xs[projectile][tz][ta][tm] = {}
              if(pcode not in product_xs[projectile][tz][ta][tm].keys()):
                product_xs[projectile][tz][ta][tm][pcode] = levels[p][tz][ta][tm][pcode]

    for p in totals.keys():
      for tz in totals[p].keys():
        for ta in totals[p][tz].keys():
          for tm in totals[p][tz][ta].keys():
            for pcode in totals[p][tz][ta][tm].keys():
              # Add to levels
              if(projectile not in product_xs.keys()):
                product_xs[projectile] = {}
              if(tz not in product_xs[projectile].keys()):
                product_xs[projectile][tz] = {}
              if(ta not in product_xs[projectile][tz].keys()):
                product_xs[projectile][tz][ta] = {}
              if(tm not in product_xs[projectile][tz][ta].keys()):
                product_xs[projectile][tz][ta][tm] = {}
              if(pcode not in product_xs[projectile][tz][ta][tm].keys()):
                product_xs[projectile][tz][ta][tm][pcode] = totals[p][tz][ta][tm][pcode]


    # Store
    process_talys.product_xs = product_xs


    
      
  def process_particles():

    particles = {}

    for file_path in process_talys.files:
      file_name = file_path.split("/")
      file_name = file_name[-1]
      particle = None
      if(file_name == "aprod.tot"):
        particle = "alpha"
      elif(file_name == "dprod.tot"):
        particle = "deuteron"
      elif(file_name == "gprod.tot"):
        particle = "gamma"
      elif(file_name == "hprod.tot"):
        particle = "helium-3"
      elif(file_name == "nprod.tot"):
        particle = "neutron"
      elif(file_name == "pprod.tot"):
        particle = "proton"
      elif(file_name == "tprod.tot"):
        particle = "triton"

      if(particle != None):
        fh = open(file_path, 'r')
        n = 0
        for line in fh:
          if(n == 0):
            projectile = line[1:3].strip()
            target_a = int(line[6:9])
            target_s = line[9:11]
            target_z = isotopes.get_z(line[9:11])
            target_m = 0

            # Add to particles
            if(projectile not in particles.keys()):
              particles[projectile] = {}
            if(target_z not in particles[projectile].keys()):
              particles[projectile][target_z] = {}
            if(target_a not in particles[projectile][target_z].keys()):
              particles[projectile][target_z][target_a] = {}
            if(target_m not in particles[projectile][target_z][target_a].keys()):
              particles[projectile][target_z][target_a][target_m] = {}
            if(particle not in particles[projectile][target_z][target_a][target_m].keys()):
              particles[projectile][target_z][target_a][target_m][particle] = []
          elif(line[0] != "#" and line != ""):
            e = float(line[0:12])
            xs = float(line[12:24]) / 1000.0
            particles[projectile][target_z][target_a][target_m][particle].append([e,xs])
          n = n + 1
        fh.close()

    # Sort arrays
    for p in particles:
      for tz in particles[p]:
        for ta in particles[p][tz]:
          for tm in particles[p][tz][ta]:
            for rc in particles[p][tz][ta][tm]:
              particles[p][tz][ta][tm][rc] = numpy.asarray(particles[p][tz][ta][tm][rc])
              particles[p][tz][ta][tm][rc] = numpy.sort(particles[p][tz][ta][tm][rc], axis=0, kind='mergesort')

    process_talys.particle_xs = particles
    
   
  def process_elastic():

    elastic = {}

    for file_path in process_talys.files:
      file_name = file_path.split("/")
      file_name = file_name[-1]

      if(file_name == "elastic.tot"):
        fh = open(file_path, 'r')
        n = 0
        for line in fh:
          if(n == 0):
            projectile = line[1:3].strip()
            target_a = int(line[6:9])
            target_s = line[9:11]
            target_z = isotopes.get_z(line[9:11])
            target_m = 0

            # Add to elastic
            if(projectile not in elastic.keys()):
              elastic[projectile] = {}
            if(target_z not in elastic[projectile].keys()):
              elastic[projectile][target_z] = {}
            if(target_a not in elastic[projectile][target_z].keys()):
              elastic[projectile][target_z][target_a] = {}
            if(target_m not in elastic[projectile][target_z][target_a].keys()):
              elastic[projectile][target_z][target_a][target_m] = []
          elif(line[0] != "#" and line != ""):
            e = float(line[0:12])
            xs = float(line[12:24]) / 1000.0
            elastic[projectile][target_z][target_a][target_m].append([e,xs])
          n = n + 1
        fh.close()

    # Sort arrays
    for p in elastic:
      for tz in elastic[p]:
        for ta in elastic[p][tz]:
          for tm in elastic[p][tz][ta]:
            elastic[p][tz][ta][tm] = numpy.asarray(elastic[p][tz][ta][tm])
            elastic[p][tz][ta][tm] = numpy.sort(elastic[p][tz][ta][tm], axis=0, kind='mergesort')

    process_talys.elastic_xs = elastic



  def process_nonelastic():

    nonelastic = {}

    for file_path in process_talys.files:
      file_name = file_path.split("/")
      file_name = file_name[-1]

      if(file_name == "nonelastic.tot"):
        fh = open(file_path, 'r')
        n = 0
        for line in fh:
          if(n == 0):
            projectile = line[1:3].strip()
            target_a = int(line[6:9])
            target_s = line[9:11]
            target_z = isotopes.get_z(line[9:11])
            target_m = 0

            # Add to nonelastic
            if(projectile not in nonelastic.keys()):
              nonelastic[projectile] = {}
            if(target_z not in nonelastic[projectile].keys()):
              nonelastic[projectile][target_z] = {}
            if(target_a not in nonelastic[projectile][target_z].keys()):
              nonelastic[projectile][target_z][target_a] = {}
            if(target_m not in nonelastic[projectile][target_z][target_a].keys()):
              nonelastic[projectile][target_z][target_a][target_m] = []
          elif(line[0] != "#" and line != ""):
            e = float(line[0:12])
            xs = float(line[12:24]) / 1000.0
            nonelastic[projectile][target_z][target_a][target_m].append([e,xs])
          n = n + 1
        fh.close()

    # Sort arrays
    for p in nonelastic:
      for tz in nonelastic[p]:
        for ta in nonelastic[p][tz]:
          for tm in nonelastic[p][tz][ta]:
            nonelastic[p][tz][ta][tm] = numpy.asarray(nonelastic[p][tz][ta][tm])
            nonelastic[p][tz][ta][tm] = numpy.sort(nonelastic[p][tz][ta][tm], axis=0, kind='mergesort')

    process_talys.nonelastic_xs = nonelastic

 
  @staticmethod
  def make_dir(dir):
    dirs = dir.split("/")
    try:
      dir = ''
      for i in range(len(dirs)):
        dir = dir + dirs[i]
        if(not os.path.exists(dir) and dir.strip() != ''):
          os.mkdir(dir) 
        dir = dir + '/'
      return True
    except:
      return False





process_talys.run()