# 동시 수행 작업은 파이썬에서 제공하는 concurrent 모듈을 사용한다.
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def send_request(var: str):
    response = requests.get(f"http://localhost:8000/context?var={var}")
    return response.json()


if __name__ == "__main__":
    # 최대 10개의 워커를 가진 스레드 풀을 생성해서 각 스레드에 요청을 할당한다.
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_request, str(i)) for i in range(10)]

    # 수행한 결과를 모아서 출력한다.
    for future in as_completed(futures):
        print(future.result())
