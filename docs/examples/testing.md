# Testing and CI/CD Examples

Examples of using WAND for testing, continuous integration, and deployment workflows.

## Cross-Browser Testing

Test a web application across multiple browsers and platforms.

### Setup

```bash
mkdir "test_{browser}_{platform}"

cat > "test_{browser}_{platform}/test_config.json" << 'EOF'
{
  "browser": "{browser}",
  "platform": "{platform}",
  "base_url": "https://app.example.com",
  "timeout": 30,
  "screenshots": true,
  "output_dir": "results_{browser}_{platform}"
}
EOF

cat > "test_{browser}_{platform}/run_tests.py" << 'EOF'
#!/usr/bin/env python3
import json
from selenium import webdriver
from selenium.webdriver.common.by import By

with open("test_config.json") as f:
    config = json.load(f)

# Setup browser
if config["browser"] == "chrome":
    driver = webdriver.Chrome()
elif config["browser"] == "firefox":
    driver = webdriver.Firefox()

# Run tests
driver.get(config["base_url"])
# ... test logic ...

driver.quit()
print(f"Tests complete: {config['browser']} on {config['platform']}")
EOF

chmod +x "test_{browser}_{platform}/run_tests.py"
```

### Execution

```bash
dir-wand --template "test_{browser}_{platform}" \
  -browser chrome firefox safari edge \
  -platform linux macos windows windows \
  --run "cd test_{browser}_{platform} && python3 run_tests.py"
```

## Performance Testing Matrix

Test application performance under different loads.

### Setup

```bash
mkdir "perf_{users}_{duration}"

cat > "perf_{users}_{duration}/loadtest.yaml" << 'EOF'
scenarios:
  - name: "Load test {users} users for {duration}s"
    executor: "ramping-vus"
    start_vus: 0
    stages:
      - duration: 30s
        target: {users}
      - duration: {duration}s
        target: {users}
      - duration: 30s
        target: 0

thresholds:
  http_req_duration:
    - "p(95)<500"
  http_req_failed:
    - "rate<0.01"
EOF

cat > "perf_{users}_{duration}/run_test.sh" << 'EOF'
#!/bin/bash
k6 run \
  --out json=results_{users}_{duration}.json \
  loadtest.yaml

echo "Load test complete: {users} users for {duration}s"
EOF

chmod +x "perf_{users}_{duration}/run_test.sh"
```

### Execution

```bash
# Test with different user counts and durations
dir-wand --swapfile perf_matrix.yaml \
  -users 10 50 100 500 1000 \
  -duration 60 120 300 600 900

dir-wand --template "perf_{users}_{duration}" \
  --swapfile perf_matrix.yaml \
  --run "cd perf_{users}_{duration} && ./run_test.sh"
```

## Docker Build Matrix

Build Docker images with different base images and versions.

### Setup

```bash
mkdir "docker_{base}_{version}"

cat > "docker_{base}_{version}/Dockerfile" << 'EOF'
FROM {base}:{version}

COPY app /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
EOF

cat > "docker_{base}_{version}/build.sh" << 'EOF'
#!/bin/bash
base="{base}"
version="{version}"

tag="myapp:${base}-${version}"

docker build -t "$tag" .

# Test the image
docker run --rm "$tag" python -c "import sys; print(sys.version)"

echo "Built and tested: $tag"
EOF

chmod +x "docker_{base}_{version}/build.sh"
```

### Execution

```bash
dir-wand --template "docker_{base}_{version}" \
  -base python alpine \
  -version 3.9 3.10 3.11 slim-3.9 slim-3.10 slim-3.11 \
  --run "cd docker_{base}_{version} && ./build.sh"
```

## Unit Test Isolation

Run unit tests with different configurations.

### Setup

```bash
mkdir "unittest_{config}_{seed}"

cat > "unittest_{config}_{seed}/pytest.ini" << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = --verbose --junit-xml=results_{config}_{seed}.xml

[config]
test_config = {config}
random_seed = {seed}
EOF

cat > "unittest_{config}_{seed}/run_tests.sh" << 'EOF'
#!/bin/bash
export TEST_CONFIG="{config}"
export RANDOM_SEED="{seed}"

pytest tests/ \
  --junit-xml=results_{config}_{seed}.xml \
  --html=report_{config}_{seed}.html

echo "Tests complete: config={config}, seed={seed}"
EOF

chmod +x "unittest_{config}_{seed}/run_tests.sh"
```

### Execution

```bash
dir-wand --template "unittest_{config}_{seed}" \
  -config minimal standard full \
  -seed 42 43 44 \
  --run "cd unittest_{config}_{seed} && ./run_tests.sh"
```

## CI/CD Pipeline Simulation

Simulate CI/CD pipeline with different deployment targets.

### Setup

```bash
mkdir "deploy_{env}_{version}"

cat > "deploy_{env}_{version}/deploy_config.yaml" << 'EOF'
deployment:
  environment: {env}
  version: {version}

infrastructure:
  env: {env}
  region: us-east-1

application:
  image: "myapp:{version}"
  replicas: 3
  resources:
    cpu: "500m"
    memory: "512Mi"

notifications:
  slack: true
  email: true
EOF

cat > "deploy_{env}_{version}/deploy.sh" << 'EOF'
#!/bin/bash
set -e

env="{env}"
version="{version}"

echo "Deploying version $version to $env"

# Build
docker build -t "myapp:$version" .

# Test
docker run --rm "myapp:$version" pytest

# Deploy (simulated)
kubectl apply -f deploy_config.yaml --dry-run=client

echo "Deployment complete: $env @ $version"
EOF

chmod +x "deploy_{env}_{version}/deploy.sh"
```

### Execution

```bash
dir-wand --template "deploy_{env}_{version}" \
  -env dev staging prod \
  -version v1.0.0 v1.1.0 v1.2.0 \
  --run "cd deploy_{env}_{version} && ./deploy.sh"
```

## Best Practices

### 1. Isolated Test Environments

Each test gets its own directory - no shared state:

```bash
dir-wand --template "test_{id}" --id 0-99 \
  --run "cd test_{id} && pytest"
```

### 2. Parallel Test Execution

Tests run concurrently:

```bash
# All 100 test suites run in parallel
dir-wand --template "suite_{num}" --num 0-99 \
  --run "cd suite_{num} && npm test"
```

### 3. Version Everything

```yaml
# test_matrix.yaml
browser:
  list: [chrome-98, firefox-97, safari-15]
platform:
  list: [ubuntu-20.04, macos-12, windows-11]
```

### 4. Collect Results

```bash
# After tests complete
mkdir -p test_results
dir-wand --run "cp test_{id}/results.xml test_results/results_{id}.xml" --id 0-99
```

### 5. Clean Up

```bash
# Remove test directories after collecting results
dir-wand --run "rm -rf test_{id}" --id 0-99
```

## See Also

- [Basic Examples](basic.md)
- [Scientific Computing](scientific.md)
- [Data Processing](data-processing.md)
