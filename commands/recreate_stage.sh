docker compose -f ./docker-compose-stage.yml down
docker volume prune -f
# shellcheck disable=SC2046
# shellcheck disable=SC2016
docker rmi $(docker images --format '{{.Repository}}' | grep '$PROJECT_NAME')
git pull
docker compose -f docker-compose-stage.yml up --build -d