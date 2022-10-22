# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


# DOCKER TASKS
# Build the container
build: ## Build the container
    docker build -t tm_image .

run: ## Run container on port configured in `config.env`
    docker run -it --rm -v $(pwd):/app --name=tm_cont tm_image /bin/bash
# docker run -i -t --rm --env-file=./config.env -p=$(PORT):$(PORT) --name=trailmapper trailmapper

#build-nc: ## Build the container without caching
#	docker build --no-cache -t trailmapper .

#up: build run ## Run container on port configured in `config.env` (Alias to run)

#stop: ## Stop and remove a running container
#	docker stop $(APP_NAME); docker rm $(APP_NAME)
