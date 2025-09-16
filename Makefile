SHELL := /bin/bash

PYTHON ?= python3
DOCKER_COMPOSE ?= docker compose
DATA_DIR ?= data
DB_DIR ?= db
SQLITE_DB ?= $(DB_DIR)/sqlite/weather.db
POSTGRES_SERVICE ?= postgres

.PHONY: pipeline
pipeline:
	@set -a; \
	if [ -f .env ]; then source .env; fi; \
	set +a; \
	if [ -n "$(DB)" ]; then \
		PIPELINE_DB_BACKEND=$(DB) $(PYTHON) src/pipeline.py; \
	else \
		$(PYTHON) src/pipeline.py; \
	fi

.PHONY: pipeline-sqlite
pipeline-sqlite:
	@$(MAKE) pipeline DB=sqlite

.PHONY: pipeline-postgres
pipeline-postgres:
	@set -e; \
	trap '$(MAKE) stop-postgres' EXIT; \
	$(MAKE) start-postgres; \
	$(MAKE) pipeline DB=postgres

.PHONY: dump
dump:
	@set -a; \
	if [ -f .env ]; then source .env; fi; \
	set +a; \
	if [ -n "$(DB)" ]; then \
		PIPELINE_DB_BACKEND=$(DB) $(PYTHON) src/dump_db.py; \
	else \
		$(PYTHON) src/dump_db.py; \
	fi

.PHONY: dump-sqlite
dump-sqlite:
	@$(MAKE) dump DB=sqlite

.PHONY: dump-postgres
dump-postgres:
	@set -e; \
	trap '$(MAKE) stop-postgres' EXIT; \
	$(MAKE) start-postgres; \
	$(MAKE) dump DB=postgres

.PHONY: clean-sqlite
clean-sqlite:
	@if [ -f $(SQLITE_DB) ]; then rm -f $(SQLITE_DB) && echo "Removed $(SQLITE_DB)"; else echo "SQLite DB not found at $(SQLITE_DB)"; fi

.PHONY: clean-data
clean-data:
	@if [ -d $(DATA_DIR) ]; then rm -rf $(DATA_DIR) && echo "Removed $(DATA_DIR) directory"; else echo "Data directory not found at $(DATA_DIR)"; fi

.PHONY: start-postgres
start-postgres:
	@$(DOCKER_COMPOSE) up -d $(POSTGRES_SERVICE)

.PHONY: stop-postgres
stop-postgres:
	@$(DOCKER_COMPOSE) stop $(POSTGRES_SERVICE) || true

.PHONY: drop-postgres
drop-postgres:
	@$(DOCKER_COMPOSE) down --remove-orphans

.PHONY: clean-postgres
clean-postgres:
	@set -e; \
	trap '$(MAKE) stop-postgres' EXIT; \
	$(MAKE) start-postgres; \
	$(DOCKER_COMPOSE) down --volumes --remove-orphans

.PHONY: clean-all
clean-all: clean-postgres clean-sqlite clean-data

.PHONY: help
help:
	@echo "Available targets:" \
	&& echo "  make pipeline           # run pipeline with configured backend" \
	&& echo "  make pipeline-sqlite    # run pipeline against SQLite (docker not needed)" \
	&& echo "  make pipeline-postgres  # run pipeline against Postgres (docker)" \
	&& echo "  make dump               # export weather_daily for current backend" \
	&& echo "  make dump-sqlite        # export weather_daily from SQLite" \
	&& echo "  make dump-postgres      # export weather_daily from Postgres" \
	&& echo "  make start-postgres     # start the Postgres container" \
	&& echo "  make stop-postgres      # stop the Postgres container" \
	&& echo "  make drop-postgres      # remove the Postgres container" \
	&& echo "  make clean-sqlite       # remove SQLite database file" \
	&& echo "  make clean-postgres     # stop and reset Postgres container" \
	&& echo "  make clean-data         # delete data directory" \
	&& echo "  make clean-all          # clean DBs and data"
