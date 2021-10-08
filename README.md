# timbit

The easiest way to run this software is to install [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) to manage packets and
environemnts. If you don't believe in pipenv, you can install packages mentioned
in Pipfile.

If you have installed pipenv, clone the repo and:

```sh

$ cd timbit
$ make build_env
$ make run

```

To run the simulation you must have a proper config file. You can use an existing config.example, just copy it in the same directory as `config`

If you don't have pipenv, install packages and evaluate `python3 simulate.py`.

