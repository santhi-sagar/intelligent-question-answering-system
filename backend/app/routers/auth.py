from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import get_db
from ..models import User
from ..schemas import LoginRequest, LoginResponse
from datetime import datetime

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user using roll number and date of birth.
    """
    # Normalize roll number (uppercase, trim)
    roll_no = request.roll_no.strip().upper()
    dob = request.dob.strip()
    
    # Validate date format
    try:
        datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Please use YYYY-MM-DD format."
        )
    
    # Check if user exists
    user = db.query(User).filter(User.roll_no == roll_no).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid roll number or date of birth"
        )
    
    # Verify date of birth
    if user.dob != dob:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid roll number or date of birth"
        )
    
    return LoginResponse(
        success=True,
        message="Login successful",
        user_id=str(user.id),
        roll_no=user.roll_no
    )


@router.post("/register", response_model=LoginResponse)
def register(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Register a new user (for admin/testing purposes).
    In production, this should be restricted or removed.
    """
    # Normalize roll number
    roll_no = request.roll_no.strip().upper()
    dob = request.dob.strip()
    
    # Validate date format
    try:
        datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Please use YYYY-MM-DD format."
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.roll_no == roll_no).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this roll number already exists"
        )
    
    # Create new user
    user = User(roll_no=roll_no, dob=dob)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return LoginResponse(
        success=True,
        message="User registered successfully",
        user_id=str(user.id),
        roll_no=user.roll_no
    )

