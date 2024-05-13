include .env

APP_NAME := iris-coach

# ==============================================================================
# Docker support

COMPOSE_FILE := compose.yml --env-file .env

compose-build:
	@echo ${APP_NAME}: building w/ ${COMPOSE_FILE}
	@docker compose -f ${COMPOSE_FILE} build --no-cache
compose-up:
	@echo ${APP_NAME}: starting w/ ${COMPOSE_FILE}
	@docker compose -f ${COMPOSE_FILE} up --quiet-pull --remove-orphans
compose-down:
	@echo ${APP_NAME}: ending w/ ${COMPOSE_FILE}
	@docker compose -f ${COMPOSE_FILE} down --remove-orphans --volumes

## 🚨 Use with caution
docker-prune: compose-down
	@echo ${APP_NAME}: pruning docker images, volumes
	@docker image prune -f
	@docker system prune --volumes -af

# ==============================================================================

start: compose-build compose-up
restart:
	@docker compose restart
	@docker compose exec iris /docker-entrypoint-initdb.d/init.sh
kill: docker-prune

# ==============================================================================
# InterSystems
# ref: https://github.com/grongierisc/interoperability-embedded-python?tab=readme-ov-file#7-command-line


# ==============================================================================

start-app:
	@streamlit run src/python/rag/🧑🏻‍⚕️_Chat.py --server.port=8051 --server.address=0.0.0.0