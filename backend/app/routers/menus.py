# backend/app/routers/menus.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.orm import Session

from app.schemas import MenuCreate, MenuResponse
from app.database import get_db
from app import models

router = APIRouter(prefix="/menus", tags=["Menus"])

# --- ENDPOINTS ---

# 1. Ambil semua daftar menu (Read All)
@router.get("", response_model=List[MenuResponse])
def get_all_menus(db: Session = Depends(get_db)):
    # Mengambil semua data menu dari tabel PostgreSQL
    menus = db.query(models.MenuItem).all()
    return menus

# 2. Tambah menu baru (Create)
@router.post("", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
def create_menu(payload: MenuCreate, db: Session = Depends(get_db)):
    # Membuat objek menu baru untuk dimasukkan ke database
    new_menu = models.MenuItem(
        nama=payload.nama,
        harga=payload.harga,
        kategori=payload.kategori,
        tersedia=payload.tersedia
    )
    
    # Simpan ke PostgreSQL
    db.add(new_menu)
    db.commit()
    db.refresh(new_menu) # Mengambil data terbaru dari DB (termasuk ID yang otomatis dibuat)
    
    return new_menu

# 3. Ambil detail menu berdasarkan ID (Read One)
@router.get("/{menu_id}", response_model=MenuResponse)
def get_menu_by_id(menu_id: int, db: Session = Depends(get_db)):
    # Mencari menu berdasarkan ID di database
    menu = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    
    if menu is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Menu dengan id {menu_id} tidak ditemukan"
        )
    return menu

# 4. Hapus menu (Delete)
@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    # Cari menu yang akan dihapus
    menu = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    
    if menu is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Menu tidak dapat dihapus karena tidak ditemukan"
        )
    
    # Hapus dari database
    db.delete(menu)
    db.commit()
    
    return None