# 1. 베이스 이미지
FROM python:3.12-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. requirementx.txt 복사 후 패키지 설치
COPY requirements.txt .
# 이미지 빌드시 실행
# fastapi-utils 는 내부적으로 psutil을 의존하는데, psutil은 C 컴파일러(gcc)가 핊요함. 그런데 python:3.12-slim 이미지에는 gcc가 없어서 gcc 설치를 추가
RUN apt-get update && apt-get install -y gcc python3-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 복사
COPY . .

# 5. 컨테이너 실행 명령어
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


