from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.contacts import ContactService
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from src.core.depend_service import get_current_user
from src.database.models import User

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ContactService(db)
    return await service.create_contact(contact, current_user)


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(
        None, description="Search by name, surname or email"),
    limit: int = Query(10, description="Number of contacts to return"),
    offset: int = Query(0, description="Number of contacts to skip")
):
    service = ContactService(db)
    if search:
        return await service.search_contacts(search, current_user)
    return await service.get_contacts(limit, offset, current_user)


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(7, description="Number of days to look ahead")
):
    service = ContactService(db)
    return await service.get_upcoming_birthdays(current_user)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ContactService(db)
    contact = await service.get_contact(contact_id, current_user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ContactService(db)
    contact = await service.update_contact(contact_id, contact_update, current_user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ContactService(db)
    contact = await service.delete_contact(contact_id, current_user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact