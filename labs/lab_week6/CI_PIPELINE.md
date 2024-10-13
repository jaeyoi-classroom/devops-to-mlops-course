# 기본적인 CI 파이프라인 구성해 보기

## 브랜치 생성

- 'hello-ci'라는 이름으로 브랜치를 생성하고 전환합니다.
```console
git switch -c hello-ci
```

## GitHub Actions Workflow 작성

- .github/workflows/hello-ci.yml
```yaml
name: CI 실습

on:
  pull_request:
    branches:
      - main
    paths:
      - "hello/**"

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install ruff tox

      - name: Ruff을 이용해 Lint 작업 실행
        run: |
          ruff check --output-format=github .

      - name: tox을 이용해 테스트 실행
        run: tox -e py
```


## 테스트 코드 작성

- hello/test_hello.py
```python
import json

import pytest

from hello import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        yield app.test_client()


def test_health_check(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"
```

## 기능 구현

- hello/api.py에 다음 내용을 추가합니다.
```python
@bp.route("/healthcheck", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200
```


## PR 생성

- commit & push한 후, 자신의 GitHub 실습 저장소에서 PR을 만들어 봅니다.
```console
git add .
git commit -m 'CI 실습'
git push origin hello-ci
```


## Actions 확인

CI 액션이 잘 동작하는지 확인합니다.