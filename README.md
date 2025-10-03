# Installation
1. Install python 3.9+ (https://www.python.org/about/gettingstarted/)
2. Navigate to this repo in CMD and set up the virtual environment

```commandline
python -m venv ./venv
.\venv\Scripts\activate
pip install -e .
```

3. Run simulator:

```commandline
python .\raid_cb_simulator\simulator.py
```

If the script runs, your installation was successful.

# Testing a configuration

`raid_cb_simulator/simulator.py` is used to run individual configurations. Edit the `test()` function and set up the configuration you want to test. Several example configs already exist as reference. Once you're ready, you can test by running:

```commandline
python .\raid_cb_simulator\simulator.py
```

# Searching for configurations

`raid_cb_simulator/runner.py` is used to quickly simulate lots of configurations to find ones that work. Beginner knowledge of programming would likely be necessary to do this. Choose which of the `run_X()` functions best fit your use case and edit it with your search parameters (it might be easier to write your own!), and edit the `if __name__ == "__main__":` block at the bottom of the file to call said function. Once you're ready, you can test by running:

```commandline
python .\raid_cb_simulator\runner.py
```
