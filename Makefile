# Makefile

up:
	docker-compose up --build

down:
	docker-compose down

logs:
	docker-compose logs -f bot

aerich-init-db:
	docker-compose run --rm aerich init-db

aerich-migrate:
	docker-compose run --rm aerich migrate

aerich-upgrade:
	docker-compose run --rm aerich upgrade

aerich-inspect:
	docker-compose run --rm aerich history

dbshell:
	docker exec -it postgres-db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

clean:
	docker-compose down -v --remove-orphans
	docker builder prune -a -f
	docker volume prune -f
	
rebuild: clean
	make up