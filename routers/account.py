from fastapi import APIRouter, Header, HTTPException
from supabase import create_client, Client
import os


router = APIRouter()


# ============================================================
# SUPABASE CONFIGURATION
# ============================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)

if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL environment variable is missing."
    )

if not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_ROLE_KEY environment variable is missing."
    )


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)


# ============================================================
# DELETE ACCOUNT
# ============================================================

@router.delete("/account/delete")
async def delete_account(
    authorization: str | None = Header(default=None),
):
    """
    Permanently delete the currently authenticated farmer.

    The Flutter app sends:

        Authorization: Bearer <supabase_access_token>

    The backend verifies that token and obtains the actual
    Supabase Auth user ID.

    The service_role key is used ONLY on the backend.
    """

    # ========================================================
    # VERIFY AUTHORIZATION HEADER
    # ========================================================

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization token.",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header.",
        )

    access_token = authorization.replace(
        "Bearer ",
        "",
        1,
    ).strip()

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Missing access token.",
        )

    # ========================================================
    # VERIFY SUPABASE USER
    # ========================================================

    try:
        user_response = (
            supabase.auth.get_user(
                access_token
            )
        )

        user = user_response.user

    except Exception as e:
        print(
            f"❌ Supabase authentication error: {e}"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
        )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user not found.",
        )

    user_id = user.id

    print(
        f"🗑️ Starting account deletion for user: {user_id}"
    )

    # ========================================================
    # DELETE DISEASE SCAN STORAGE FILES
    # ========================================================
    #
    # Files are stored as:
    #
    # disease-scans/
    #     USER_ID/
    #         scan_123.jpg
    #
    # We delete only this user's folder.
    #
    # This does NOT affect another farmer's images.
    # ========================================================

    try:
        storage = supabase.storage.from_(
            "disease-scans"
        )

        files = storage.list(
            user_id
        )

        if files:
            file_paths = []

            for file in files:
                file_name = file.get(
                    "name"
                )

                if file_name:
                    file_paths.append(
                        f"{user_id}/{file_name}"
                    )

            if file_paths:
                storage.remove(
                    file_paths
                )

                print(
                    f"🖼️ Deleted "
                    f"{len(file_paths)} disease scan files."
                )

    except Exception as e:
        print(
            f"⚠️ Storage deletion warning: {e}"
        )

    # ========================================================
    # DELETE DISEASE HISTORY
    # ========================================================

    try:
        supabase.table(
            "disease_history"
        ).delete().eq(
            "user_id",
            user_id,
        ).execute()

        print(
            "✅ Disease history deleted."
        )

    except Exception as e:
        print(
            f"⚠️ Disease history deletion warning: {e}"
        )

    # ========================================================
    # DELETE FARMER PROFILE
    # ========================================================

    try:
        supabase.table(
            "farmers"
        ).delete().eq(
            "user_id",
            user_id,
        ).execute()

        print(
            "✅ Farmer profile deleted."
        )

    except Exception as e:
        print(
            f"⚠️ Farmer profile deletion warning: {e}"
        )

    # ========================================================
    # DELETE PUBLIC PROFILE
    # ========================================================

    try:
        supabase.table(
            "profiles"
        ).delete().eq(
            "id",
            user_id,
        ).execute()

        print(
            "✅ Public profile deleted."
        )

    except Exception as e:
        print(
            f"⚠️ Public profile deletion warning: {e}"
        )

    # ========================================================
    # DELETE FARMER WALLET
    # ========================================================

    try:
        supabase.table(
            "wallets"
        ).delete().eq(
            "farmer_id",
            user_id,
        ).execute()

        print(
            "✅ Farmer wallet deleted."
        )

    except Exception as e:
        print(
            f"⚠️ Wallet deletion warning: {e}"
        )

    # ========================================================
    # DELETE FARMER WITHDRAWALS
    # ========================================================

    try:
        supabase.table(
            "withdrawals"
        ).delete().eq(
            "farmer_id",
            user_id,
        ).execute()

        print(
            "✅ Farmer withdrawals deleted."
        )

    except Exception as e:
        print(
            f"⚠️ Withdrawals deletion warning: {e}"
        )

    # ========================================================
    # DELETE FARMER TRANSACTIONS
    # ========================================================

    try:
        supabase.table(
            "transactions"
        ).delete().eq(
            "farmer_id",
            user_id,
        ).execute()

        print(
            "✅ Farmer transactions deleted."
        )

    except Exception as e:
        print(
            f"⚠️ Transactions deletion warning: {e}"
        )

    # ========================================================
    # DELETE FARMER PRODUCTS
    # ========================================================
    #
    # Only products where the user is the farmer owner.
    #
    # Supplier products belonging to another seller are not
    # touched.
    # ========================================================

    try:
        supabase.table(
            "products"
        ).delete().eq(
            "farmer_id",
            user_id,
        ).execute()

        print(
            "✅ Farmer products deleted."
        )

    except Exception as e:
        print(
            f"⚠️ Product deletion warning: {e}"
        )

    # ========================================================
    # DELETE AUTH ACCOUNT
    # ========================================================
    #
    # THIS is what the old Flutter AccountService was missing.
    #
    # The service_role key is used only here on the backend.
    # ========================================================

    try:
        supabase.auth.admin.delete_user(
            user_id
        )

        print(
            f"✅ Supabase Auth account deleted: {user_id}"
        )

    except Exception as e:
        print(
            f"❌ Auth account deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete authentication account.",
        )

    # ========================================================
    # SUCCESS
    # ========================================================

    return {
        "success": True,
        "message": "Account deleted successfully.",
      }
