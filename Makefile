.PHONY: dev build up down logs restart frontend-backend

# 🛠 Start the dev environment
dev:
	docker-compose up --build

# 🐳 Build all containers
build:
	docker-compose build

# 🚀 Run containers in the background
up:
	docker-compose up -d

# 🛑 Stop containers
down:
	docker-compose down

# 📜 Follow logs from all services
logs:
	docker-compose logs -f

# 🔄 Restart everything
restart: down up

# 🧪 Run only frontend + backend (no Mongo or other services)
# frontend-backend:
# 	docker-compose up frontend backend
