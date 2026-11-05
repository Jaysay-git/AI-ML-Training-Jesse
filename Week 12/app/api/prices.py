
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.api.dependencies import get_current_user
from app.schemas.price import PriceCreate, PriceUpdate, PriceResponse
from app.services.price_service import (
    create_price,
    get_price,
    list_prices,
    update_price,
    delete_price,
)
from app.services.price_import_service import (
    parse_price_upload,
    save_imported_prices,
)

router = APIRouter(prefix="/prices", tags=["Prices"])


@router.post("", response_model=PriceResponse, status_code=201)
def add_price(
    price_data: PriceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = price_data.model_dump()
    return create_price(db, data, current_user.id)


@router.get("", response_model=list[PriceResponse])
def get_all_prices(
    commodity_id: int | None = None,
    location_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_prices(db, commodity_id, location_id)


@router.post("/import/preview")
async def preview_price_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )

    try:
        content = await file.read()
        result = parse_price_upload(
            db,
            content,
            file.filename,
        )
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    finally:
        await file.close()


@router.post("/import/confirm")
async def confirm_price_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )

    try:
        content = await file.read()

        # Revalidate the file against the latest database records.
        result = parse_price_upload(
            db,
            content,
            file.filename,
        )

        valid_rows = result["valid_rows"]
        invalid_count = len(result["invalid_rows"])
        duplicate_count = len(result["duplicate_rows"])

        if not valid_rows:
            return {
                "status": "nothing_to_import",
                "imported_count": 0,
                "valid_count": 0,
                "invalid_count": invalid_count,
                "duplicate_count": duplicate_count,
            }

        imported_count = save_imported_prices(
            db,
            valid_rows,
            current_user.id,
        )

        return {
            "status": "success",
            "imported_count": imported_count,
            "valid_count": len(valid_rows),
            "invalid_count": invalid_count,
            "duplicate_count": duplicate_count,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "One or more records became duplicates during import. "
                "Please preview the file again."
            ),
        )

    finally:
        await file.close()


@router.get("/{price_id}", response_model=PriceResponse)
def get_single_price(
    price_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    price = get_price(db, price_id)

    if price is None:
        raise HTTPException(
            status_code=404,
            detail="Price record not found",
        )

    return price


@router.patch("/{price_id}", response_model=PriceResponse)
def edit_price(
    price_id: int,
    update_data: PriceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    price = get_price(db, price_id)

    if price is None:
        raise HTTPException(
            status_code=404,
            detail="Price record not found",
        )

    updated = update_price(
        db,
        price,
        update_data.model_dump(exclude_unset=True),
        current_user.id,
    )

    if updated is None:
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own price records",
        )

    return updated


@router.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_price(
    price_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    price = get_price(db, price_id)

    if price is None:
        raise HTTPException(
            status_code=404,
            detail="Price record not found",
        )

    deleted = delete_price(db, price, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own price records",
        )
