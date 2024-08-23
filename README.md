# Optimos V2

The next generation of [Optimos](https://github.com/AutomatedProcessImprovement/roptimus-prime). A Resource, Roster and Batching optimizer using Prosimos simulator.

## Installation & Basic Usage

### Installation

1. Create a fresh Python 3.10 virtual environment, e.g. with `conda create --name optimos-python python=3.10`
1. Install `poetry` on your system by following the [offical guide](https://python-poetry.org/docs/#installation). Make sure, poetry is **NOT** installed in the virtual environment.
1. Activate the environment, e.g. with `conda activate optimos-python`
1. Run `poetry install` in the root directory of this repository

### Standalone Usage

_For now there is no CLI interface for the optimizer, so you have to modify the `main.py` script to your needs_

1. Open `main.py` in your editor
1. Change the `timetable_path`, `constraints_path` and `bpmn_path` to your needs.
   - _If you need a basic set of constraints for your model, you can use the `create_constraints.py` script_
1. Run `python main.py` to start the optimizer, you will see the output and process in the console
1. _If you want to change settings like the number of iterations you can do so in the `main.py` script as well_

### Usage within PIX (docker)

1. Install Docker and Docker-Compose, refer to the [official website](https://docs.docker.com/get-docker/) for installation instructions
2. Clone the [pix-portal](https://github.com/AutomatedProcessImprovement/pix-portal) repository (`git clone https://github.com/AutomatedProcessImprovement/pix-portal.git`)
3. Checkout the `integrate-optimos-v2` branch (`git checkout integrate-optimos-v2`)
4. Create the following secrets:
   - `frontend/pix-web-ui/.session.secret`
   - `backend/services/api-server/.superuser_email.secret`
   - `backend/services/api-server/.system_email.secret`
   - `backend/services/api-server/.superuser_password.secret`
   - `backend/services/api-server/.key.secret`
   - `backend/services/api-server/.system_password.secret`
   - _For local development/testing you can just fill them with example values, e.g. "secret" or "secret@secret.secret"._
   - If you want to send out mails you also need to create secrets: `backend/workers/mail/.secret_gmail_username` & `backend/workers/mail/.secret_gmail_app_password`;
     Those are the credentials for the mail account that sends out the mails. If you don't want to send out mails, you can ignore this step.
5. Create the following `.env` files:
   - `backend/workers/mail/.env`
   - `backend/workers/kronos/.env`
   - `backend/workers/simulation-prosimos/.env`
   - `backend/workers/bps-discovery-simod/.env`
   - `backend/workers/optimos/.env`
   - `backend/services/api-server/.env`
   - `backend/services/kronos/.env`
   - _You will find a `.env.example` file in each of the folders, you can copy this file and rename it to `.env`_
6. Run `docker-compose up --build` in the root directory of the pix-portal repository
7. _This will take some time_
8. Open your browser and go to `localhost:9999`. You can use the credentials from the `.superuser_email.secret` and `.superuser_password.secret` files to login.

### Usage within PIX (local + debugging)

1. Do all of the **Usage within PIX (docker)** steps above
2. Stop the docker-based optimos: `docker compose stop optimos`
3. Modify the `backend/workers/optimos/.env` file to use the local host instead of the docker container, you can rename `.env.example-local` to `.env` for that
4. Create a new Python 3.10 virtual environment (e.g. with `conda create --name optimos-python python=3.10`)
5. Activate the environment, e.g. with `conda activate optimos-python`
6. Navigate to the `backend/workers/optimos` folder in the pix repo
7. Install the dependencies with `poetry install`
8. Start the optimos worker with `python python optimos_worker/main.py`
9. **Alteratively**: Start the optimos worker with the vs code debugger by running the `Launch Optimos Worker` configuration (most likely you'll need to adjust the python binary used there, you can do that in the `.vscode/launch.json` file)

## Development

### Running Tests

To run the tests, run `pytest`. The tests should also automatically show up in the test explorer of your IDE. (For VSCode, you need to install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python))

### Collecting Coverage

To collect coverage, run `pytest --cov --cov-report=lcov:lcov.info --cov-report=term`. You can display it e.g. with the vscode extension [Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters).

## Docs

While the code should be documented in most places, you can find additional information on e.g. the architecture in the [docs folder](./docs/)

## Improvements over Legacy Optimos

- **Support to optimize Batching**
- Fully Typed
- Unit Tested (with ~90% coverage)
- Follows a Action-Store-Reducer pattern, similar to Flux
- Multi-Threaded at important parts, takes cpu core count of host machine into account
- Almost all public interfaces are documented
- Class-Based (Not a huge monolithic script)
- No throwaway file creation; Everything in memory
- Immutable Data Structures, so no change to the timetable is ever unexpected
