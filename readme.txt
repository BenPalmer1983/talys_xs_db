Talys Python Dictionary

Large files & source code: http://u.pc.cd/984rtalK

The Talys code has been used to generate proton reaction cross section data.

https://tendl.web.psi.ch/tendl_2019/talys.html

The data is generated from 0MeV to 50MeV (at least) in increments of 10keV.  This data are read into a Python dictionary which are then saved to pickled files.  The Talys class loads the data from these files into a dictionary.

Dictionary structure

talys.d
  ['info']
    ['name']
    ['source']
    ['help']
  ['metastable']
    [ms]
      ['ms']       (0=gs, 1=m, 2=n ...)
      ['level']    (level as in Talys output file)
      ['energy']   (metastable energy)
  ['levels']
    [level]
      ['ms']       (0=gs, 1=m, 2=n ...)
      ['level']    (level as in Talys output file)
      ['energy']   (metastable energy)
  ['residual_xs']
    [projectile]
      [target_z]
        [target_a]
          [target_m]
            [residual_code] (numpy array) (code = 1000000 * M + 1000 * Z + A)
  ['particle_xs']
    [projectile]
      [target_z]
        [target_a]
          [target_m]
            [particle] (numpy array) (particle = alpha, deuteron, gamma, helium-3, neutron, proton, triton)
  ['elastic_xs']
    [projectile]
      [target_z]
        [target_a]
          [target_m] (numpy array)
  ['nonelastic_xs']
    [projectile]
      [target_z]
        [target_a]
          [target_m] (numpy array)


Example Use:

(needs talys.py, isotopes.py, pz.py)


from talys import talys 

# Set path to talys data dir and to isotopes pickle
talys.set("../data/talys", "../data/isotopes.pz")





