# Created file quickstart.sh (this file), then `chmod +x quickstart.sh` to make it executable.
# Works in zsh, requires bash 4 or higher, which is not the default version on macOS
# find your shell with: echo $SHELL
# leave out #!/bin/bash

# Prepare environment
# Check file .env exists else exit
if [ ! -f .env ]; then
    echo "File .env not found!" >&2
    exit 1
fi
# Set environment variables
source .env
#printenv

# Collected relevant 'start' commands from README.md for easy access, 
# excluding the one time commands like pulling/loading/tagging images.

# Make sure to start this file in sopdemo root folder where docker-compose.yml is located.

# Assumption is that any running containers are stopped and removed including volumes,
# using command: docker-compose down -v

docker-compose build oracle-writer postgres-reporter
docker-compose up -d oracle19c postgres solace-broker
python3 -m venv .venv   
source .venv/bin/activate
which python
pip install --upgrade pip
pip install -r requirements.txt
python3 ez_aq_browser.py
# TODO: Python script to create queues
docker-compose up -d jpa-oracle-source jpa-postgres-target
docker-compose up -d oracle-writer
docker-compose up -d postgres-reporter
