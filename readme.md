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
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate (with no 'source' in front)
   ```
3. Install dependencies:
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
