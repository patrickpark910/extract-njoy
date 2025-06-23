"""
Generates CSV's of (E,σ) interpolated from ENDF via NJOY
"""
import os, sys, re, shutil, csv
from datetime import datetime
import numpy as numpy
import pandas as pd
from jinja2 import Template

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Python'))
from utilities import *


""" 
Put in duples of ZAID, MT that you want interpolated

ENDF Reaction Numbers (MT):
    1 = total (sum of 2, 4, 5, 11, 16-18, 22-26, 28-37, 41-42, 44-45, 102-117)
        (try not to use MT=1 bc it will run each sub reaction and add up)
    2 = total elastic scattering
    4 = total inelastic scattering (sum 50-91)
   18 = fission
   19 = prompt neutron yield
  102 = radiative capture (n,gamma)
  105 = triton production (n,t)
        (T production is formally 33+36+105+116 [(n,nt)+(n,nt2a)+(n,t)+(n,pt)] 
        but most isotopes have no 33, 36, 116 data bc they are 0)
""" 
TARGETS =  [('U235',2),('U235',18),('U235',102), 
            ('U238',2),('U238',18),('U238',102), 
            ('Pb208',102)] # ('U238',1),]

TOLERANCE = 0.0001 # njoy default = 0.001 / my default = 0.00001


def main():
    """ Import and configure xs data
    """
    with open("./Data/endf_mat_lookup.csv") as f:
        mat_lookup = dict(csv.reader(f))

    for target in TARGETS:
        nuclide, reaction = target

        try:
            nuclide = format_nuclide(nuclide)
            mat = int(mat_lookup[nuclide])
            print(f"\n\nRunning EXTRACT-NJOY for nuclide {nuclide} (MAT {mat}) for reaction MT={reaction}.")
        except:
            print(f"Fatal. ENDF MAT lookup for nuclide {nuclide} failed.")
            sys.exit(2)

        current_run = Reaction(nuclide,mat,reaction)

        current_run.create_paths()

        if current_run.csv_output not in os.listdir(f"./NJOY/"):
            current_run.copy_endf()
            current_run.write_njoy()
            current_run.run_njoy()
            current_run.read_njoy()

        """
        if "tape22" not in os.listdir(f"./NJOY/{current_run.njoy_subfolder}"):
            current_run.run_njoy()

        if "tape22" in os.listdir(f"./NJOY/{current_run.njoy_subfolder}"):
            current_run.read_njoy()
        """


class Reaction:
    """
    """
    def __init__(self, nuc, mat, mt, E_min=1e-5, E_max=20e6):
        self.nuc, self.mat, self.mt = nuc, mat, mt
        self.E_min, self.E_max = E_min, E_max
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # self.njoy_subfolder = f"{self.nuc}_mt{self.mt}"
        self.njoy_workdir = f"./NJOY/temp"
        self.njoy_input = f"njoy_{self.nuc}_mt{self.mt}.inp"
        self.csv_output = f"{self.nuc}_mt{self.mt}.csv"


    def split_zaid(self):
        m = re.match(r'^([A-Za-z]+)(\d+)$', self.nuc)
        if not m:
            raise ValueError(f" Fatal. Nuclide string {self.nuc!r} is not in <letters><digits> form")
            sys.exit()

        self.I, self.A = m.groups()
        return letters, numbers


    def create_paths(self):
        """ Assign filepaths and create directories if they do not exist
        """
        paths_to_create = [self.njoy_workdir,]  # f"./NJOY/{self.njoy_subfolder}",
        if os.path.exists(self.njoy_workdir):
            shutil.rmtree(self.njoy_workdir)
        for path in paths_to_create:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)


    def copy_endf(self):
        """ 
        Copies over necessary .endf file from ./Data/ENDF-B-VIII.1_neutrons 
        into NJOY run directory as tape20 (ex. ./NJOY/U238-mt102/tape20)
        """
        self.Z, self.X, self.A = split_zaid(self.nuc)

        try:
            # Define paths
            src = f"./Data/ENDF-B-VIII.1_neutrons/n-{self.Z}_{self.X}_{self.A}.endf"
            dst = os.path.join(f"{self.njoy_workdir}", 'tape20') 
            # not sure if Python will always recognize 'tape20' as a file and not dir... -ppark
            
            # Check if source file exists
            if not os.path.exists(src):
                raise FileNotFoundError(f"ENDF file not found: {src}")
            
            # os.makedirs(destination_dir, exist_ok=True) # Create destination directory if it doesn't exist
            shutil.copy(src, dst) # Move and rename
            
            print(f"Copied '{src}' to '{self.njoy_workdir}' as 'tape20'.")
            
        except PermissionError:
            print("Fatal. Permission denied. Check file/directory permissions.")
            sys.exit(2)
        except Exception as e:
            print(f"Fatal. {e}")
            sys.exit(2)


    def write_njoy(self):
        """ Fills out NJOY template
        """
        self.parameters = {"datetime" : self.datetime,
                           "nuc" : self.nuc,
                           "mat" : self.mat,
                           "mt"  : self.mt,
                           "tol": TOLERANCE,
                           "temp_idx" : 1,
                           "E_min": self.E_min,
                           "E_max": self.E_max,
                           }

        with open("./NJOY/njoy.template", 'r') as njoy_template:
            template_str = njoy_template.read()
            template = Template(template_str) 
            template.stream(**self.parameters).dump(f"{self.njoy_workdir}/{self.njoy_input}")
            self.print_input = False
            print(f" Comment. NJOY template written: {self.njoy_workdir}/{self.njoy_input}")


    def run_njoy(self):
        try:
            prev = os.getcwd()
            os.chdir(f"{self.njoy_workdir}")
        except:
            print(f"Fatal. Error changing cwd from {prev} to {self.njoy_workdir}.")

        try:
            cmd = f"njoy < {self.njoy_input}"
            os.system(cmd)
        except:
            print(f"Fatal. Error running NJOY: {cmd}")
            sys.exit(2)

        try:
            os.chdir(f"{prev}")
        except:
            print(f"Fatal. Error changing cwd from {os.getcwd()} to {prev}.")


    def read_njoy(self):
        """ Reads tape22 output from NJOY, returns list of (E,σ)
        """
        pattern = re.compile(r'^\s*([0-9]+\.\d+(?:[Ee][+-]?\d+)?)\s+([0-9]+\.\d+(?:[Ee][+-]?\d+)?)')
        data = []

        try:
            with open(f"{self.njoy_workdir}/tape22", 'r') as infile:
                for line in infile:
                    m = pattern.match(line)
                    if m:
                        data.append((m.group(1), m.group(2)))
                        # Optionally convert to float: 
                        # e = float(m.group(1)); xs = float(m.group(2))
                        # data.append((e, xs))
        except:
            print(f"Fatal. Error reading {self.njoy_workdir}/tape22")
            sys.exit(2)

        # Write to CSV
        try:
            with open(f"./NJOY/{self.csv_output}", 'w', newline='') as outfile:
                print('oopsie woopsie')
                writer = csv.writer(outfile)
                print('fucky wucky')
                writer.writerow(['energy_eV', 'xs_barns'])
                print('sum ting wong')
                writer.writerows(data)
                # print(data)
        except:
            print(f"Fatal. Error writing ./NJOY/{self.csv_output}")
            sys.exit(2)
        
        print(f" Wrote to ./NJOY/{self.csv_output}")


if __name__ == '__main__':
    main()



