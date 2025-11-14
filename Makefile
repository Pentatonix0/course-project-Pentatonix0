IMAGE_NAME ?= quiz-builder
IMAGE_TAG ?= dev
COMPOSE ?= docker compose
TRIVY_SEVERITY ?= HIGH,CRITICAL

.PHONY: help build run stop logs hadolint trivy smoke clean

help:
	@echo "Commonly used targets:"
	@echo "  build      Build the runtime image"
	@echo "  run        Start the stack via docker compose"
	@echo "  stop       Stop the stack"
	@echo "  logs       Tail container logs"
	@echo "  hadolint   Lint Dockerfile"
	@echo "  trivy      Scan the built image with Trivy"
	@echo "  smoke      Run container smoke-test (health + UID)"

build:
	docker build --target runtime -t $(IMAGE_NAME):$(IMAGE_TAG) .

run:
	$(COMPOSE) up -d

stop:
	$(COMPOSE) down --remove-orphans

logs:
	$(COMPOSE) logs -f

hadolint:
	hadolint --config hadolint.yml Dockerfile

trivy:
	mkdir -p reports
	trivy image --severity $(TRIVY_SEVERITY) --exit-code 1 --output reports/trivy-report.txt $(IMAGE_NAME):$(IMAGE_TAG)

smoke:
	./scripts/container-smoke.sh

clean:
	docker image prune -f
