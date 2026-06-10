# 로그를 출력할 형식을 지정한다.
import logging

from context_vars import user_context

log_format = "%(asctime)s %(name)s %(levelname)s:\tuser: %(user)s %(message)s"


# 커스텀 포매터
# 기본 포매터를 상속받아 따로 정의한다.
# log_format에 %(user)s 가 있는데, 이 떄문에 파일을 저장할 때 유비콘이 새로 시작되는 과정에서 에러가 발생하기 때문이다.
class CustomFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "user"):
            record.user = "Anonymous"
        return super().format(record)


# 커스텀 핸들러
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter(log_format))

# 커스텀 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


# 커스텀 컨텍스트 필터
class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        record.user = str(user_context.get())
        return True


logger.addFilter(ContextFilter())
