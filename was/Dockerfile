# Python 3.10 버전을 기반으로 이미지를 만듭니다.
FROM python:3.10-slim

# 컨테이너 안에서 작업할 폴더를 /app 으로 설정합니다.
WORKDIR /app

# 필요한 라이브러리가 적힌 requirements.txt 파일을 복사합니다.
COPY requirements.txt .

# 복사된 requirements.txt 파일을 이용해 라이브러리를 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 현재 폴더의 모든 파일(app.py 등)을 컨테이너의 /app 폴더로 복사합니다.
COPY . .

# 컨테이너가 시작될 때 실행할 명령어를 정의합니다.
CMD ["python", "app.py"]