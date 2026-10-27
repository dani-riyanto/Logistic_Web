from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/sessions", tags=["Sessions"])

# 1. GET
@router.get("", response_model=List[schemas.SessionResponse])
def get_sessions(
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(models.Order)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (models.Order.customer_name.ilike(search_term)) |
            (models.Order.order_number.ilike(search_term))
        )
        
    return query.offset(skip).limit(limit).all()

# 2. GET by ID
@router.get("/{session_id}", response_model=schemas.SessionResponse)
def get_session_by_id(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.Order).filter(models.Order.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")
    return session

# 3. POST
@router.post("", response_model=schemas.SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(payload: schemas.SessionCreate, db: Session = Depends(get_db)):
    # Generate order number
    latest_order = db.query(models.Order).order_by(models.Order.id.desc()).first()
    latest_num = 1000
    if latest_order and latest_order.order_number:
        try:
            latest_num = int(latest_order.order_number.replace("#", ""))
        except ValueError:
            pass
            
    new_order_num = f"#{latest_num + 1}"
    current_time = datetime.now().strftime("%H.%M")

    # Buat object model SQLAlchemy
    new_session = models.Order(
        order_number=new_order_num,
        time=current_time,
        customer_name=payload.customer_name,
        menu_item_id=payload.menu_item_id,
        quantity=payload.quantity,
        total_price=payload.total_price,
        status=payload.status,
        notes=payload.notes
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

# 4. PUT
@router.put("/{session_id}", response_model=schemas.SessionResponse)
def update_session(session_id: int, payload: dict, db: Session = Depends(get_db)):
    db_session = db.query(models.Order).filter(models.Order.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")
    
    for key, value in payload.items():
        if hasattr(db_session, key):
            setattr(db_session, key, value)
            
    db.commit()
    db.refresh(db_session)
    return db_session

# 5. DELETE
@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    db_session = db.query(models.Order).filter(models.Order.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")
        
    db.delete(db_session)
    db.commit()
    return None