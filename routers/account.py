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
# HELPER
# ============================================================

def delete_rows(
    table_name: str,
    column_name: str,
    user_id: str,
):
    """
    Delete rows belonging to the authenticated user.

    IMPORTANT:
    Any failure raises an exception immediately.

    This means the Auth account will NOT be deleted if
    database cleanup fails.
    """

    print(
        f"🗑️ Deleting {table_name}.{column_name} "
        f"for user {user_id}"
    )

    response = (
        supabase
        .table(table_name)
        .delete()
        .eq(column_name, user_id)
        .execute()
    )

    print(
        f"✅ {table_name}.{column_name} cleanup completed."
    )

    return response


# ============================================================
# DELETE ACCOUNT
# ============================================================

@router.delete("/account/delete")
async def delete_account(
    authorization: str | None = Header(default=None),
):
    """
    Permanently delete the authenticated user's account.

    Flutter sends:

        Authorization: Bearer <supabase_access_token>

    The backend:

    1. Verifies the access token.
    2. Deletes user-owned storage.
    3. Deletes user-owned database records.
    4. Deletes the Supabase Auth account.

    If ANY cleanup step fails, the process stops and the
    Auth account is NOT deleted.
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


    access_token = authorization[
        len("Bearer "):
    ].strip()


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
            detail=(
                "Invalid or expired "
                "authentication token."
            ),
        )


    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Authenticated user not found.",
        )


    user_id = user.id


    print(
        "=================================================="
    )

    print(
        f"🗑️ ACCOUNT DELETION STARTED: {user_id}"
    )

    print(
        "=================================================="
    )


    # ========================================================
    # STORAGE CLEANUP
    # ========================================================
    #
    # Expected structure:
    #
    # disease-scans/
    #     USER_ID/
    #         scan_123.jpg
    #
    # Only the authenticated user's folder is touched.
    # ========================================================

    try:

        storage = (
            supabase
            .storage
            .from_("disease-scans")
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
                    f"✅ Deleted "
                    f"{len(file_paths)} "
                    f"disease scan images."
                )

            else:

                print(
                    "ℹ️ No disease scan files found."
                )

        else:

            print(
                "ℹ️ No disease scan storage folder found."
            )


    except Exception as e:

        print(
            f"❌ Storage cleanup failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion stopped because "
                "disease scan storage could not be cleaned."
            ),
        )


    # ========================================================
    # DISEASE HISTORY
    # ========================================================

    try:

        delete_rows(
            "disease_history",
            "user_id",
            user_id,
        )

    except Exception as e:

        print(
            f"❌ Disease history deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion stopped because "
                "disease history could not be deleted."
            ),
        )


    # ========================================================
    # ORDERS
    # ========================================================
    #
    # The authenticated farmer can appear as:
    #
    # farmer_id
    # buyer_id
    # seller_id
    #
    # We remove orders associated with this account.
    #
    # ========================================================

    try:

        print(
            f"🗑️ Deleting orders for user {user_id}"
        )


        # Orders where user is the farmer
        supabase.table(
            "orders"
        ).delete().eq(
            "farmer_id",
            user_id,
        ).execute()


        # Orders where user is the buyer
        supabase.table(
            "orders"
        ).delete().eq(
            "buyer_id",
            user_id,
        ).execute()


        # Orders where user is the seller
        supabase.table(
            "orders"
        ).delete().eq(
            "seller_id",
            user_id,
        ).execute()


        print(
            "✅ Orders deleted."
        )


    except Exception as e:

        print(
            f"❌ Orders deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion stopped because "
                "orders could not be deleted."
            ),
        )


    # ========================================================
    # PRODUCT PROMOTIONS
    # ========================================================

    try:

        delete_rows(
            "product_promotions",
            "seller_id",
            user_id,
        )

    except Exception as e:

        print(
            f"❌ Product promotions deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion stopped because "
                "product promotions could not be deleted."
            ),
        )


    # ========================================================
    # PRODUCTS
    # ========================================================
    #
    # A farmer's products can be associated through:
    #
    # farmer_id
    # seller_id
    #
    # Delete both ownership types.
    #
    # ========================================================

    try:

        print(
            f"🗑️ Deleting products for user {user_id}"
        )


        supabase.table(
            "products"
        ).delete().eq(
            "farmer_id",
            user_id,
        ).execute()


        supabase.table(
            "products"
        ).delete().eq(
            "seller_id",
            user_id,
        ).execute()


        print(
            "✅ Products deleted."
        )


    except Exception as e:

        print(
            f"❌ Product deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion stopped because "
                "products could not be deleted."
            ),
        )


    # ========================================================
    # TRANSACTIONS
    # ========================================================
    #
    # Farmer can appear as farmer_id or seller_id.
    #
    # ========================================================

    try:

        print(
            f"🗑️ Deleting transactions for user {user_id}"
        )


        supabase.table(
            "transactions"
        ).delete().eq(
            "farmer_id",
            user_id,
        ).execute()


        supabase.table(
            "transactions"
        ).delete().eq(
            "seller_id",
            user_id,
        ).execute()


        print(
            "✅ Transactions deleted."
        )


    except Exception as e:

        print(
            f"❌ Transaction deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion stopped because "
                "transactions could not be deleted."
            ),
        )


    # ========================================================
    # WITHDRAWALS
    # ========================================================

    try:

        delete_rows(
            "withdrawals",
            "farmer_id",
            user_id,
        )

    except Exception as e:

        print(
            f"❌ Withdrawals deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion stopped because "
                "withdrawals could not be deleted."
            ),
        )


    # ========================================================
    # WALLET
    # ========================================================
    #
    # Farmer wallet can use farmer_id.
    #
    # seller_id is also present in the schema.
    #
    # ========================================================

    try:

        print(
            f"🗑️ Deleting wallets for user {user_id}"
        )


        supabase.table(
            "wallets"
        ).delete().eq(
            "farmer_id",
            user_id,
        ).execute()


        supabase.table(
            "wallets"
        ).delete().eq(
            "seller_id",
            user_id,
        ).execute()


        print(
            "✅ Wallet records deleted."
        )


    except Exception as e:

        print(
            f"❌ Wallet deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion stopped because "
                "wallet records could not be deleted."
            ),
        )


    # ========================================================
    # FARMER PROFILE
    # ========================================================

    try:

        delete_rows(
            "farmers",
            "user_id",
            user_id,
        )

    except Exception as e:

        print(
            f"❌ Farmer profile deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion stopped because "
                "farmer profile could not be deleted."
            ),
        )


    # ========================================================
    # PUBLIC PROFILE
    # ========================================================

    try:

        delete_rows(
            "profiles",
            "id",
            user_id,
        )

    except Exception as e:

        print(
            f"❌ Public profile deletion failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion stopped because "
                "public profile could not be deleted."
            ),
        )


    # ========================================================
    # AUTH ACCOUNT
    # ========================================================
    #
    # IMPORTANT:
    #
    # We reach this section ONLY if all previous cleanup
    # operations completed successfully.
    #
    # ========================================================

    try:

        print(
            f"🗑️ Deleting Supabase Auth user: {user_id}"
        )


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
            detail=(
                "Your account data was cleaned, "
                "but the authentication account could "
                "not be deleted. Please contact support."
            ),
        )


    # ========================================================
    # SUCCESS
    # ========================================================

    print(
        "=================================================="
    )

    print(
        f"✅ ACCOUNT DELETION COMPLETE: {user_id}"
    )

    print(
        "=================================================="
    )


    return {
        "success": True,
        "message": "Account deleted successfully.",
        }
