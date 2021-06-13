### Zerion address scoring + 

##### Install
1. Install [poetry](https://python-poetry.org/docs/)
2. Install dependencies:
    ```bash
    poetry config --local virtualenvs.in-project true
    poetry install
    ```

##### CLI
1. Change file run_cli.py
2. Run
   ```bash
   poetry run pyhton run_cli.py
   ```

##### GUI
1. Run server
   ```bash
   poetry run pyhton representation.py
   ```
2. Open `localhost:9000` or <server_ip>:9000`