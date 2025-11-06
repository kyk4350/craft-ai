"""
프로젝트 CRUD API 엔드포인트
사용자별 프로젝트 관리
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from app.models.base import get_db
from app.models.project import Project
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])


# === Pydantic Schemas ===

class ProjectCreate(BaseModel):
    """프로젝트 생성 요청"""
    name: str
    description: Optional[str] = None
    product_name: Optional[str] = None
    product_category: Optional[str] = None  # 화장품, 식품, 패션, 전자제품, 서비스


class ProjectUpdate(BaseModel):
    """프로젝트 수정 요청"""
    name: Optional[str] = None
    description: Optional[str] = None
    product_name: Optional[str] = None
    product_category: Optional[str] = None


# === API Endpoints ===

@router.post("", summary="프로젝트 생성")
def create_project(
    request: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    새 프로젝트 생성

    - 로그인한 사용자만 가능
    - 생성한 프로젝트는 해당 사용자 소유
    """
    project = Project(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        product_name=request.product_name,
        product_category=request.product_category
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "success": True,
        "message": "프로젝트가 생성되었습니다",
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "product_name": project.product_name,
            "product_category": project.product_category,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        }
    }


@router.get("", summary="프로젝트 목록 조회")
def get_projects(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    로그인한 사용자의 프로젝트 목록 조회

    - 본인의 프로젝트만 조회 가능
    - 페이지네이션 지원
    """
    # 사용자의 프로젝트만 조회
    query = db.query(Project).filter(Project.user_id == current_user.id)

    total = query.count()
    projects = query.order_by(Project.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "product_name": p.product_name,
                "product_category": p.product_category,
                "contents_count": len(p.contents) if p.contents else 0,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat()
            }
            for p in projects
        ]
    }


@router.get("/{project_id}", summary="프로젝트 상세 조회")
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    프로젝트 상세 정보 조회

    - 본인의 프로젝트만 조회 가능
    - 연결된 콘텐츠 개수 포함
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="프로젝트를 찾을 수 없습니다"
        )

    return {
        "success": True,
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "product_name": project.product_name,
            "product_category": project.product_category,
            "contents_count": len(project.contents) if project.contents else 0,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        }
    }


@router.put("/{project_id}", summary="프로젝트 수정")
def update_project(
    project_id: int,
    request: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    프로젝트 정보 수정

    - 본인의 프로젝트만 수정 가능
    - 제공된 필드만 업데이트
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="프로젝트를 찾을 수 없습니다"
        )

    # 제공된 필드만 업데이트
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return {
        "success": True,
        "message": "프로젝트가 수정되었습니다",
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "product_name": project.product_name,
            "product_category": project.product_category,
            "updated_at": project.updated_at.isoformat()
        }
    }


@router.delete("/{project_id}", summary="프로젝트 삭제")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    프로젝트 삭제

    - 본인의 프로젝트만 삭제 가능
    - 연결된 콘텐츠도 함께 삭제 (CASCADE)
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="프로젝트를 찾을 수 없습니다"
        )

    db.delete(project)
    db.commit()

    return {
        "success": True,
        "message": "프로젝트가 삭제되었습니다"
    }
