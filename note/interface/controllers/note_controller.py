from dataclasses import asdict
from datetime import datetime
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from common.auth import CurrentUser, get_current_user
from containers import Container
from database import get_db
from note.application.note_service import NoteService

router = InferringRouter(prefix="/notes")


class NoteResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    memo_date: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class CreateNoteBody(BaseModel):
    title: str = Field(min_length=1, max_length=64)
    content: str = Field(min_length=1)
    memo_date: str = Field(min_length=8, max_length=8)
    tags: list[str] | None = Field(default=None, min_length=1, max_length=32)


class GetNotesResponse(BaseModel):
    total_count: int
    page: int
    notes: list[NoteResponse]


class UpdateNoteBody(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=64)
    content: str | None = Field(default=None, min_length=1)
    memo_date: str | None = Field(default=None, min_length=8, max_length=8)
    tags: list[str] | None = Field(default=None)


# 반복되는 의존성 타입을 alias로 뺴서 재사용할 수 있다.
DB = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


@cbv(router)
class NoteRouter:
    @inject
    def __init__(self, note_service: Annotated[NoteService, Depends(Provide[Container.note_service])]):
        self.note_service = note_service

    # POST /notes/ - 노트 생성
    @router.post("/", status_code=201, response_model=NoteResponse)
    def create_note(
        self,
        session: DB,
        current_user: CurrentUserDep,
        body: CreateNoteBody,
    ) -> NoteResponse:
        note = self.note_service.create_note(
            session=session,
            user_id=current_user.id,
            title=body.title,
            content=body.content,
            memo_date=body.memo_date,
            tag_names=body.tags if body.tags else [],
        )

        # dataclass 는 asdict 함수로 쉽게 딕셔너리로 만들 수 있음
        response = asdict(note)
        response.update({"tags": [tag.name for tag in note.tags]})

        return response

    # GET /notes/ - 노트 목록 조회
    @router.get("/", response_model=GetNotesResponse)
    def get_notes(
        self,
        session: DB,
        current_user: CurrentUserDep,
        page: int = 1,
        items_per_page: int = 10,
    ) -> GetNotesResponse:
        total_count, notes = self.note_service.get_notes(
            session=session,
            user_id=current_user.id,
            page=page,
            items_per_page=items_per_page,
        )

        res_notes = []
        for note in notes:
            note_dict = asdict(note)
            note_dict.update({"tags": [tag.name for tag in note.tags]})
            res_notes.append(note_dict)

        return {
            "total_count": total_count,
            "page": page,
            "notes": res_notes,
        }

    # GET /notes/{note_id} - 노트 상세 조회
    @router.get("/{note_id}", response_model=NoteResponse)
    def get_note(
        self,
        session: DB,
        current_user: CurrentUserDep,
        note_id: str,
    ) -> NoteResponse:
        note = self.note_service.get_note(
            session=session,
            user_id=current_user.id,
            note_id=note_id,
        )

        response = asdict(note)
        response.update({"tags": [tag.name for tag in note.tags]})

        return response

    # PUT /notes/{note_id} - 노트 수정
    @router.put("/{note_id}", response_model=NoteResponse)
    def update_note(
        self,
        session: DB,
        current_user: CurrentUserDep,
        note_id: str,
        body: UpdateNoteBody,
    ) -> NoteResponse:
        note = self.note_service.update_note(
            session=session,
            user_id=current_user.id,
            note_id=note_id,
            title=body.title,
            content=body.content,
            memo_date=body.memo_date,
            tag_names=body.tags,
        )

        response = asdict(note)
        response.update({"tags": [tag.name for tag in note.tags]})

        return response

    # DELETE /notes/note_id - 노트 삭제
    @router.delete("/{note_id}", status_code=204)
    def delete_note(
        self,
        session: DB,
        current_user: CurrentUserDep,
        note_id: str,
    ):
        self.note_service.delete_note(
            session=session,
            user_id=current_user.id,
            note_id=note_id,
        )

    # GET /notes/tags/{tag_name}/notes - 태그 이름으로 노트 검색
    @router.get("/tags/{tag_name}/notes", response_model=GetNotesResponse)
    def get_notes_by_tag(
        self,
        session: DB,
        current_user: CurrentUserDep,
        tag_name: str,
        page: int = 1,
        items_per_page: int = 10,
    ) -> GetNotesResponse:
        total_count, notes = self.note_service.get_notes_by_tag(
            session=session,
            user_id=current_user.id,
            tag_name=tag_name,
            page=page,
            items_per_page=items_per_page,
        )

        res_notes = []
        for note in notes:
            note_dict = asdict(note)
            note_dict.update({"tags": [tag.name for tag in note.tags]})
            res_notes.append(note_dict)

        return {
            "total_count": total_count,
            "page": page,
            "notes": res_notes,
        }
