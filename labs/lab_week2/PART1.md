# Docker 설치

## Docker Desktop 설치

### Windows

1. WSL 2 설치
   - 명령 프롬프트에서 다음을 실행합니다.
   ```
   wsl --install
   ```

1. Docker Desktop 설치
   - https://docs.docker.com/desktop/install/windows-install/

### macOS

- https://docs.docker.com/desktop/install/mac-install/
- Homebrew를 이용중이라면, 설치 파일 받을 필요 없이 다음 명령어로 설치 가능
   ```
   brew install --cask docker
   ```

### Linux

- https://docs.docker.com/desktop/install/linux-install/


## Hello Docker
터미널을 실행해서 아래 명령어를 실행해 봅니다.
- Windows: PowerShell
- macOS, Linux: Terminal

```sh
docker run hello-world
```