IMAGE=internal-kubeconfig-generator

lint:
	@docker run --rm -e RUN_LOCAL=true -e KUBERNETES_KUBEVAL_OPTIONS=--ignore-missing-schemas -e VALIDATE_PYTHON_MYPY=false -v $(shell pwd):/tmp/lint github/super-linter:v4

build-local:
	@docker build --no-cache --pull -t $(IMAGE):local . -f build/container/Dockerfile

clean:
	@find . -name "*.pyc" -exec rm -f {} \;
	@find . -name "__pycache__" -exec rm -rf {} \;
	@rm -rf super-linter.log