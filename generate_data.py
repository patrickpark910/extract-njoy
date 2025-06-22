"""
Generates CSV's of (E,σ) interpolated from ENDF via NJOY
"""
import os, sys, re, shutil, csv
from datetime import datetime
import numpy as numpy
import pandas as pd
from jinja2 import Template


""" 
Put in duples of ZAID, MT that you want interpolated

ENDF Reaction Numbers (MT):
   18 = fission
  102 = absorption (fission + capture)
""" 
TARGETS = [('U238',102),]


def main():
    """ Import and configure xs data
    """

    with open("./Data/endf_mat_lookup.csv") as f:
        mat_lookup = dict(csv.reader(f))

    for target in TARGETS:
        nuclide, reaction = target

        try:
            mat = int(mat_lookup[nuclide])
        except:
            print(f" Fatal. ENDF MAT lookup for nuclide {nuclide} failed.")
            sys.exit(2)

        current_run = Reaction(nuclide,mat,reaction)

        current_run.create_paths()

        if "tape22" not in os.listdir(f"./NJOY/{current_run.njoy_subfolder}"):
            current_run.run_njoy()

        if "tape22" in os.listdir(f"./NJOY/{current_run.njoy_subfolder}"):
            current_run.read_njoy()


class Reaction:
    """
    """
    def __init__(self, nuc, mat, mt, E_min=1e-5, E_max=20e6):
        self.nuc, self.mat, self.mt = nuc, mat, mt
        self.E_min, self.E_max = E_min, E_max
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.njoy_subfolder = f"{self.nuc}_mt{self.mt}"
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
        paths_to_create = ["./NJOY/","./NJOY/temp/",f"./NJOY/{self.njoy_subfolder}","./Results/"] 
        if os.path.exists("./NJOY/temp/"):
            shutil.rmtree("./NJOY/temp/")
        for path in paths_to_create:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

    def copy_endf(self):
        """ 
        Copies over necessary .endf file from ./Data/ENDF-B-VIII.1_neutrons 
        into NJOY run directory as tape20 (ex. ./NJOY/U238-mt102/tape20)
        """
        try:
            # Define paths
            src = f"./Data/ENDF-B-VIII.1_neutrons/n-{self.Z}_{self.I}_{self.A}.endf"
            dst = os.path.join(f"./NJOY/{self.njoy_subfolder}", 'tape20')
            
            # Check if source file exists
            if not os.path.exists(src):
                raise FileNotFoundError(f" Fatal. ENDF file not found: {src}")
            
            # os.makedirs(destination_dir, exist_ok=True) # Create destination directory if it doesn't exist
            shutil.move(src, dst) # Move and rename
            
            print(f"Moved '{src}' to '{dst}'")
            
        except PermissionError:
            print(" Fatal. Permission denied. Check file/directory permissions.")
        except Exception as e:
            print(f" Fatal. Unexpected error: {e}")

    def write_njoy(self):
        """ Fills out NJOY template
        """

        self.parameters = {"datetime" : self.datetime,
                           "nuc" : self.nuc,
                           "mat" : self.mat,
                           "mt"  : self.mt,
                           "E_min": self.E_min,
                           "E_max": self.E_max,
                           }

        with open("./NJOY/njoy.template", 'r') as njoy_template:
            template_str = njoy_template.read()
            template = Template(template_str) # + '\n' + tally_str)
            template.stream(**self.parameters).dump(self.input_filepath)
            self.print_input = False
            print(f" Comment. NJOY template written: {self.input_filepath}")

    def run_njoy(self):
        cmd = f"njoy < {self.njoy_input}"
        os.system(cmd)


    def read_njoy(self):
        """ Reads tape22 output from NJOY, returns list of (E,σ)
        """
        pattern = re.compile(r'^\s*([0-9]+\.\d+(?:[Ee][+-]?\d+)?)\s+([0-9]+\.\d+(?:[Ee][+-]?\d+)?)')
        data = []

        try:
            with open(f"./NJOY/{self.njoy_subfolder}/tape22", 'r') as infile:
                for line in infile:
                    m = pattern.match(line)
                    if m:
                        data.append((m.group(1), m.group(2)))
                        # Optionally convert to float: 
                        # e = float(m.group(1)); xs = float(m.group(2))
                        # data.append((e, xs))
        except:
            print(f" Fatal. Error reading ./NJOY/{self.njoy_subfolder}/tape22")
            sys.exit(2)

        # Write to CSV
        try:
            with open(f"./Results/{self.csv_output}", 'w', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(['energy_eV', 'xs_barns'])
                writer.writerows(data)
        except:
            print(f" Fatal. Error writing ./Results/{self.csv_output}")
            sys.exit(2)

        return print(f" Wrote to ./Results/{self.csv_output}")



if __name__ == '__main__':
    main()



