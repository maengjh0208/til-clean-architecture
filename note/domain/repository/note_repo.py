from abc import ABCMeta, abstractmethod

from sqlalchemy.orm import Session

from note.domain.note import Note


class INoteRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_notes(
        self,
        session: Session,
        user_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[Note]]:
        pass

    @abstractmethod
    def find_by_id(self, session: Session, user_id: str, note_id: str) -> Note:
        pass

    @abstractmethod
    def save(self, session: Session, user_id: str, note: Note) -> Note:
        pass

    @abstractmethod
    def update(self, session: Session, user_id: str, note: Note) -> Note:
        pass

    @abstractmethod
    def delete(self, session: Session, user_id: str, note_id: str) -> None:
        pass

    @abstractmethod
    def delete_tags(self, session: Session, user_id, note_id: str) -> None:
        pass

    @abstractmethod
    def get_notes_by_tag_name(
        self,
        session: Session,
        user_id: str,
        tag_name: str,
        page: int,
        items_per_pages: int,
    ) -> tuple[int, list[Note]]:
        pass
