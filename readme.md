# Extract-NJOY

A Python wrapper to easily extract linearized nuclear cross sections from NJOY. This tool is for you need to get a very fine grid of energies and microscopic cross sections (the tolerance is adjustable). You are most likely writing some script involving nuclear reaction calculations without MCNP or OpenMC.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Code Flow](#code-flow)
- [Miscellaneous](#miscellaneous)
- [Theory](#theory)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Download (clone) the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Open `generate_data.py` and adjust the nuclide, reaction, and tolerance you want:

```python
TARGETS =  [('U238',1,0.00001), ('Li6',18,0.1)]
```

Then run `generate_data.py`:

```bash
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
python3 generate_data.py
```

## Code Flow

1. **Input Parsing**: Reads NJOY input deck and configuration files.
2. **Wrapper Invocation**: Calls the appropriate NJOY modules (e.g., `reconr`, `broadr`, `unresr`) via subprocess.
3. **Output Collection**: Captures NJOY tape files (e.g., `tape21`, `tape22`) in a designated output directory.
4. **Post-processing**: Parses the raw tape files into Python data structures (lists, dicts, Pandas DataFrames).
5. **Error Handling**: Validates NJOY return codes and raises descriptive exceptions on failure.
6. **Results Export**: Saves processed data to CSV.

## Miscellaneous
Some tips and tricks (mainly reminders for myself for useful things when writing this)



## Theory

This wrapper interfaces with the NJOY nuclear data processing system to:

- **Reconstruct cross sections** (`RECONR` module) at specified temperatures and tolerances.
- **Doppler broadening** (`BROADR`) for thermal reactor applications. Doppler broadening generally should not affect 1/v cross sections.
- **Resonance reconstruction** (`UNRESR`) to handle unresolved resonance regions.

The Python wrapper abstracts these Fortran-based modules, enabling:

- Automated batch processing of multiple nuclides.
- Integration with Jupyter notebooks and data analysis pipelines.
- Seamless coupling to neutronics codes (e.g., MCNP, OpenMC).
