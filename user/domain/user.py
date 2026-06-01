from dataclasses import dataclass
from datetime import datetime


# value object: id 속성 없음. 데이터만 가지고 있는 도메인 객체
@dataclass
class Profile:
    name: str
    email: str


@dataclass
class User:
    id: str
    profile: Profile
    password: str
    created_at: datetime
    updated_at: datetime
