# Extract-NJOY

A Python wrapper to easily extract linearized nuclear cross sections from NJOY. This tool is for you need to get a very fine grid of energies and microscopic cross sections (the tolerance is adjustable). You are most likely writing some script involving nuclear reaction calculations without MCNP or OpenMC.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Code Flow](#code-flow)
- [Miscellaneous](#miscellaneous)
- [Theory](#theory)

## Installation

1. Download (clone) the repository:
   ```bash
   git clone https://github.com/patrickpark910/extract-njoy.git
   cd extract-njoy
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate (with no 'source' in front)
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Open `generate_data.py` and adjust the nuclide, reaction, and tolerance you want:

```python
TARGETS =  [('U238',1,0.00001), ('Li6',18,0.1)] # njoy default = 0.001 (0.1%)
```

I recommend using the NJOY default tolerance of 0.001 (0.1%) for $1/v$ cross sections. Only crank down the tolerance for resonances.

Then activate the virtual environment (if you haven't already) and run `generate_data.py`:

```bash
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate (with no 'source' in front)
python3 generate_data.py
```

You should see something like this, e.g., for U-238 fission (MAT = 9237, MT = 18):

```bash
Running EXTRACT-NJOY for nuclide U238 (MAT 9237) for reaction MT=18.
Copied './Data/ENDF-B-VIII.1_neutrons/n-092_U_238.endf' to './NJOY/temp' as 'tape20'.
NJOY template written: ./NJOY/temp/njoy_U238_mt18.inp

 njoy 2016.78  03Feb25                                       06/23/25 04:43:23
 *****************************************************************************
 reconr...                                                                0.0s
 plotr...                                                               184.6s
                                                                        187.2s
 *****************************************************************************
 Wrote to ./NJOY/U238_mt18.csv
```

The CSV should have the pointwise (E, $\sigma$) data you want to load, at a fine enough grid to linearly interpolate.

## Code Flow

If you are curious about what's under the hood, here's basically what happens:

1. `generate_data.py` reads the list of (isotope, reaction, temperature) data you want and iterates through them in a `for` loop. For each (isotope, reaction, temperature), henceforth called "problem," it creates the `Reaction` class.

2. The `Reaction` class sets up all the other problem parameters you need, e.g., the isotope's `MAT` code and the reaction's `MT` code in ENDF-6 format. It then streams all these parameters to `njoy.template` using the `Jinja2` package. The `njoy.template` is a NJOY input with specific parameters blanked out like this: `{{ E_min }}`. `Jinja2` fills in this template to create the specific NJOY input file for the problem. 

   (NB. "ENDF" means two things: Evaluated Nuclear Data **Format**, which is what ENDF-6 is. Or, Evaluated Nuclear Data **File**, which is the library of cross sections themselves. In this repo, I use ENDF-6 format and ENDF/B.VIII.1 data.)

3. Once the NJOY input is written, it is executed. Fortran has hardcoded input and output files, so `tape20` is the ENDF data, `tape21` is the result of `RECONR`, `tape 22` is that of `BROADR`

4. Once NJOY is done, we read `tape22`, extract the linearized data, and write it as a CSV.

I understand my wrapper doesn't use NJOY as efficiently as possible, but ngl I have little confidence (and time) in making NJOY run properly for more complicated inputs. This is also something you'll most likely run infrequently, so you can afford to sit for a few extra minutes, and simple = less time spent fixing if something goes wrong.

## Miscellaneous
Some tips and tricks (mainly reminders for myself for useful things when writing this)

- Reconstruct cross sections (`RECONR` module) at specified temperatures and tolerances.

- Doppler broadening (`BROADR`) for thermal reactor applications. Doppler broadening generally should not affect 1/v cross sections.

- Resonance reconstruction (`UNRESR`) to handle unresolved resonance regions.

  

  

### Working with ENDF

- [You can look up ENDF `MAT` codes for nuclides here.](https://www-nds.iaea.org/public/download-endf/TENDL-2017/Original/iso-mat.tendl-n.txt)

### Installing NJOY21

- Download NJOY21 from [Los Alamos's repo here](https://github.com/njoy/NJOY21). If you are on Windows I highly suggest you use WSL (very easy to install). I tried and wasted like 8 hrs getting everything to work in Windows proper—it was a bit rough to finangle MSYS2, gcc, cmake, and fortran together.

- If you have trouble with `cmake` in installing `NJOY21` then you can try (for Linux/WSL):

  ```bash
  sudo apt-get update && sudo apt-get install build-essential
  ```

- If you get an error that looks like below:

  ```bash
  -- The Fortran compiler identification is unknown
  CMake Error at /usr/share/cmake-3.28/Modules/CMakeDetermineFortranCompiler.cmake:341 (configure_file):
    Operation not permitted
  ```

  you probably don't have `gfortran` installed. Fix with (for Linux/WSL):

  ```bash
  sudo apt install gfortran
  ```


### Working with NJOY21

- [You can find NJOY test problems here](https://www.njoy21.io/NJOY2016/testDescription.html) for you to base your input decks off of.
- 

## Theory

This wrapper interfaces with the NJOY nuclear data processing system to:

- Reconstruct cross sections (`RECONR` module) at specified temperatures and tolerances.
- Doppler broadening (`BROADR`) for thermal reactor applications. Doppler broadening generally should not affect 1/v cross sections.
- Resonance reconstruction (`UNRESR`) to handle unresolved resonance regions.

Here is more theory 

The Python wrapper abstracts these Fortran-based modules, enabling:

- Automated batch processing of multiple nuclides.
- Integration with Jupyter notebooks and data analysis pipelines.
- Seamless coupling to neutronics codes (e.g., MCNP, OpenMC).
