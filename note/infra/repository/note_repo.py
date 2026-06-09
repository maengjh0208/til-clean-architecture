from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from note.domain.note import Note as NoteVO
from note.domain.repository.note_repo import INoteRepository
from note.infra.db_models.notes import Note, Tag
from utils.db_utils import row_to_dict


class NoteRepository(INoteRepository):
    def get_notes(
        self,
        session: Session,
        user_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[NoteVO]]:
        # total_count
        query = select(Note).where(Note.user_id == user_id)
        total_count = session.execute(select(func.count()).select_from(query.subquery())).scalar() or 0

        # Tag 포함 + 페이징
        notes = (
            session.execute(  # SQL 실행 -> Result 객체 반환
                query.options(
                    joinedload(Note.tags)
                )  # 처음부터 JOIN 해서 한번에 가져온다. (Eager 방식. 이게 없으면 Lazy 방식)
                .offset((page - 1) * items_per_page)
                .limit(items_per_page)
            )
            .scalars()  # Result 에서 첫번째 컬럼 값만 추출 -> ScalarResult
            .unique()  # joinedload로 컬렉션 JOIN 시 중복 행 제거 필수
            .all()  # ScalarResult를 list로 변환
        )

        # select(Note.id, Note.title) 처럼 컬럼을 직접 지정하면 scalars() 없이 all() 만 해도 되는데,
        # select(Note) 처럼 객체 전체를 가져올 때는 .scalars() 로 한번 처리해줘야 Note 객체 리스트가 나온다.

        # execute() 결과 (Row 객체)
        # (Note(...),)
        # (Note(...),)

        # .scalars() 후
        # Note(...)
        # Note(...)

        note_vos = [NoteVO(**row_to_dict(note)) for note in notes]
        return total_count, note_vos

    def find_by_id(self, session: Session, user_id: str, note_id: str) -> NoteVO:
        note = (
            session.execute(
                select(Note).where(Note.id == note_id, Note.user_id == user_id).options(joinedload(Note.tags))
            )
            .scalars()
            .unique()
            .one_or_none()
        )

        if not note:
            raise HTTPException(status_code=404)

        return NoteVO(**row_to_dict(note))

    def save(self, session: Session, user_id: str, note: NoteVO) -> NoteVO:
        tags = []
        for tag in note.tags:
            existing_tag = session.execute(select(Tag).where(Tag.name == tag.name)).scalar()

            if existing_tag:
                tags.append(existing_tag)
            else:
                tags.append(
                    Tag(
                        id=tag.id,
                        name=tag.name,
                    )
                )

        new_note = Note(
            id=note.id,
            user_id=note.user_id,
            title=note.title,
            content=note.content,
            memo_date=note.memo_date,
            tags=tags,
        )

        session.add(new_note)

    def update(self, session: Session, user_id: str, note: NoteVO) -> NoteVO:
        self.delete_tags(session, user_id, note.id)

        query = select(Note).where(Note.id == note.id, Note.user_id == user_id)
        result = session.execute(query).scalar_one_or_none()

        if not result:
            raise HTTPException(status_code=422)

        result.title = note.title
        result.content = note.content
        result.memo_date = note.memo_date

        tags = []
        for tag in note.tags:
            existing_tag = session.execute(select(Tag).where(Tag.name == tag.name)).scalar()

            if existing_tag:
                tags.append(existing_tag)
            else:
                tags.append(
                    Tag(
                        id=tag.id,
                        name=tag.name,
                    )
                )

        result.tags = tags
        session.add(result)

        return NoteVO(**row_to_dict(result))

    def delete(self, session: Session, user_id: str, note_id: str) -> None:
        self.delete_tags(session, user_id, note_id)

        note = session.execute(select(Note).where(Note.id == note_id, Note.user_id == user_id)).scalar()

        if not note:
            raise HTTPException(status_code=422)

        session.delete(note)

    def delete_tags(self, session: Session, user_id, note_id: str) -> None:
        note = session.execute(select(Note).where(Note.id == note_id, Note.user_id == user_id)).scalar()

        if not note:
            raise HTTPException(status_code=422)

        note.tags = []
        session.add(note)

        unused_tags = session.execute(select(Tag).where(~Tag.notes.any())).scalars().all()

        for tag in unused_tags:
            session.delete(tag)

    def get_notes_by_tag_name(
        self,
        session: Session,
        user_id: str,
        tag_name: str,
        page: int,
        items_per_pages: int,
    ) -> tuple[int, list[NoteVO]]:
        count_query = (
            select(func.count(Note.id.distinct())).join(Note.tags).where(Note.user_id == user_id, Tag.name == tag_name)
        )
        total_count = session.execute(count_query).scalar() or 0

        if not total_count:
            return 0, []

        data_query = (
            select(Note)
            .join(Note.tags)
            .where(Note.user_id == user_id, Tag.name == tag_name)
            .options(joinedload(Note.tags))
            .offset((page - 1) * items_per_pages)
            .limit(items_per_pages)
        )
        notes = session.execute(data_query).scalars().unique().all()
        note_vos = [NoteVO(**row_to_dict(note)) for note in notes]

        return total_count, note_vos
