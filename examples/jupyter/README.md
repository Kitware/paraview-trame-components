# ParaView & Jupyter setup

The ParaView binary is purposefully missing SSL which for the context of Jupyter requires to use conda. 

## Setting a conda environment

```
conda create --name ptc python=3.12 -y
conda config --add channels conda-forge
conda activate ptc
conda install -y paraview-trame-components

# Then add jupyterlab
conda install -y jupyterlab
```

## Running PTC in Jupyter

```
jupyter lab
```

## Jupyer Examples

```
./simple.ipynb
./lite.ipynb
```
