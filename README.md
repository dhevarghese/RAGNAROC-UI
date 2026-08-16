# RAGNAROC-UI <img src="https://github.com/ColdCoffee21/RAGNAROC-UI/blob/main/assets/mjolnir-t-blue.png" alt="" width="30" height="30">
A visual interface for the RAGNAROC model to increase the ease of access to experimenters, and in-turn gain more visibility in the whole scientific community.

This platform will be continually developed so as to simulate visual attention experiments and interact with the neural correlates produced by the model. It is a multi page application developed using Dash. <img src="https://avatars.githubusercontent.com/u/5997976?s=200&v=4" alt="" width="20" height="20">

Current Status: Setup your experiments on a text based input interface. These would be validated, and passed to the model. The results are visualised on the 3D Surface plot, across the time period of the simulation. Line plots help analyse results.

Check out the website [here](http://ragnaroc.us-east-1.elasticbeanstalk.com/)

# Running locally

Requires Python 3.12, a C compiler, and the packages in the two requirements files:

```bash
pip install -r requirements.txt -r requirements-build.txt
```

Build the RAGNAROC model extension for your platform (the compiled `.so`/`.pyd` is not
checked in), then start the app:

```bash
cd cython && python setup.py build_ext --inplace && mv ragnaroc.*.so .. && cd ..
python application.py
```

The app serves at http://localhost:8050. Saved experiments and run logs go to a local
SQLite database at `data/ragnaroc.db`. Optional environment variables: `RAGNAROC_DEBUG=1`
enables Dash debug mode, `PORT` overrides the port, and `RAGNAROC_STORAGE=dynamo` (with
standard AWS credentials in the environment) switches persistence to DynamoDB.

# Features to be added
- [ ] Eye movements
- [ ] Experiment simulation
- [x] Optimised Ragnaroc

# Contribution

We are open to contribution! Follow these steps and join us ->

- Fork this repository
- Clone the repo locally
- Open your favourite IDE and start working.
- Make your awesome changes, push your changes onto a new branch.
- Send in a pull-request :)
