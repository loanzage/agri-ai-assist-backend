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


# IMPORTANT:
# This client uses the SERVICE ROLE KEY.
#
# It must ONLY exist on the FastAPI backend.
# Never put this key inside Flutter.
# ============================================================

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
    Permanently delete the currently authenticated user.

    Flutter sends:

        Authorization: Bearer <supabase_access_token>

    The backend:

        1. Verifies the access token.
        2. Gets the real Supabase Auth user ID.
        3. Deletes that user's Storage files.
        4. Deletes that user's application data.
        5. Deletes the Supabase Auth account.

    The service-role key is used ONLY by this backend.
    """

    # ========================================================
    # 1. VERIFY AUTHORIZATION HEADER
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


    access_token = authorization[
        len("Bearer "):
    ].strip()


    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Missing access token.",
        )


    # ========================================================
    # 2. VERIFY SUPABASE USER
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
    # 3. DELETE DISEASE SCAN STORAGE FILES
    # ========================================================
    #
    # Storage structure:
    #
    # disease-scans/
    #     USER_ID/
    #         scan_123.jpg
    #         scan_456.jpg
    #
    # We ONLY delete:
    #
    # disease-scans/USER_ID/
    #
    # Other farmers' images remain untouched.
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
                    "✅ Disease scan images deleted."
                )

        else:

            print(
                "ℹ️ No disease scan images found."
            )


    except Exception as e:

        print(
            f"❌ Disease storage deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete disease scan images.",
        )


    # ========================================================
    # 4. DELETE DISEASE HISTORY
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
            f"❌ Disease history deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete disease history.",
        )


    # ========================================================
    # 5. DELETE FARMER PROFILE
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
            f"❌ Farmer profile deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete farmer profile.",
        )


    # ========================================================
    # 6. DELETE PUBLIC PROFILE
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
            f"❌ Public profile deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete user profile.",
        )


    # ========================================================
    # 7. DELETE FARMER WALLET
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
            f"❌ Wallet deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete farmer wallet.",
        )


    # ========================================================
    # 8. DELETE FARMER WITHDRAWALS
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
            f"❌ Withdrawals deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete withdrawals.",
        )


    # ========================================================
    # 9. DELETE FARMER TRANSACTIONS
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
            f"❌ Transactions deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete transactions.",
        )


    # ========================================================
    # 10. DELETE FARMER PRODUCTS
    # ========================================================
    #
    # We only delete products where:
    #
    # farmer_id = current user
    #
    # This does NOT delete another supplier's products.
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
            f"❌ Farmer products deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete farmer products.",
        )


    # ========================================================
    # 11. DELETE AUTH ACCOUNT
    # ========================================================
    #
    # THIS is the critical operation.
    #
    # The service-role key allows the backend to delete
    # the Supabase Auth user.
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
    # 12. SUCCESS
    # ========================================================

    return {

        "success": True,

        "message":
            "Account deleted successfully.",

        "user_id":
            user_id,

            }
