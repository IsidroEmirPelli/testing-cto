.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser test clean

help:
	@echo "Comandos disponibles:"
	@echo "  make build          - Construir imágenes Docker"
	@echo "  make up             - Levantar servicios"
	@echo "  make down           - Detener servicios"
	@echo "  make restart        - Reiniciar servicios"
	@echo "  make logs           - Ver logs"
	@echo "  make shell          - Abrir shell en el contenedor web"
	@echo "  make migrate        - Ejecutar migraciones"
	@echo "  make makemigrations - Crear migraciones"
	@echo "  make createsuperuser - Crear superusuario de Django"
	@echo "  make test           - Ejecutar tests"
	@echo "  make test-unit      - Ejecutar tests unitarios"
	@echo "  make clean          - Limpiar contenedores y volúmenes"
	@echo "  make dev-setup      - Configurar entorno de desarrollo"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec web /bin/bash

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

test:
	docker-compose exec web pytest

test-unit:
	docker-compose exec web pytest tests/unit/

test-coverage:
	docker-compose exec web pytest --cov=src --cov-report=html

clean:
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

dev-setup:
	@echo "Configurando entorno de desarrollo..."
	cp .env.example .env
	docker-compose build
	docker-compose up -d
	@echo "Esperando a que la base de datos esté lista..."
	sleep 10
	docker-compose exec web python manage.py migrate
	@echo "¡Entorno listo! Usa 'make logs' para ver los logs"
	@echo "Para crear un superusuario: make createsuperuser"

check:
	docker-compose exec web python manage.py check
