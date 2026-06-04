from dependency_injector import containers, providers

from user.application.user_service import UserService
from user.infra.repository.user_repo import UserRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        # 의존성을 사용할 모듈을 선언한다.
        # packages 에 패키지의 경로를 기술하면 해당 패키지 하위에 있는 모듈이 모두 포함된다.
        # 만약 특정 모듈에만 제공하고 싶다면 modules=["user.application.user_service"] 와 같이 할 수 있다.
        packages=["user"],
    )

    # Factory 는 객체를 매번 생성한다. Singleton 은 처음 호출될 때 생성한 객체를 재활용한다.
    # user_repo = providers.Factory(UserRepository)
    user_repo = providers.Factory(UserRepository)

    # UserService 객체를 생성할 팩토리를 제공한다.
    # 이때 UserService 생성자로 전달될 user_repo 객체 역시 컨테이너에 있는 팩토리로 선언했다.
    user_service = providers.Factory(UserService, user_repo=user_repo)
