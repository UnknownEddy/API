# SPc: Specular Point calculation

## Introduction
SPc is a tool for calculating specular points from GNSS-R signal. The repo requires flight data from a drone and the received GNSS-R measurements from the same time period. The flight information is expected in a ".gpx" file and the GNSS-R measurements in ".ubx" files. 

## File Structure
- `data`: The raw data should be placed under `data/raw` inside `flightlog` and `ublox` folders. The processed files will be placed under `data/processed`
- `docs`: *[not yet]* Contains documentation of the repository.
- `notebooks`: Notebooks showing example usage of the repository.
- `results`: Any produced results can be found here.
- `src`: Contains subdirectories and files that represent different modules, packages, or components of the project.


## Installation
To use SPc, you need to have Python installed. You can install SPc by running the following command:
```
conda env create -f environment_locked.yml
```

## Tutorial
View `notebooks/tutorial.ipynb` for sample usage.