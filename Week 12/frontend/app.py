
import os
from datetime import date
from decimal import Decimal

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

st.set_page_config(
    page_title="Naija Cost of Living Intelligence",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "token": None,
    "user": None,
    "page": "Overview",
    "chat_history": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# API HELPERS
# =========================================================

def api_request(method, endpoint, payload=None, params=None):
    """Send an authenticated request to the FastAPI backend."""

    headers = {}

    if st.session_state.token:
        headers["Authorization"] = (
            f"Bearer {st.session_state.token}"
        )

    try:
        response = requests.request(
            method=method,
            url=f"{API_URL}{endpoint}",
            json=payload,
            params=params,
            headers=headers,
            timeout=120,
        )

        if response.status_code == 204:
            return True

        if response.status_code >= 400:
            try:
                detail = response.json().get(
                    "detail",
                    response.text,
                )
            except ValueError:
                detail = response.text

            st.error(
                f"API error ({response.status_code}): {detail}"
            )
            return None

        return response.json()

    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to the API. "
            "Make sure FastAPI is running."
        )
        return None

    except requests.exceptions.Timeout:
        st.error("The API request timed out. Please try again.")
        return None

    except requests.exceptions.RequestException as error:
        st.error(f"Request failed: {error}")
        return None


def api_upload_request(endpoint, filename, file_bytes):
    """Send an authenticated multipart file upload to FastAPI."""

    headers = {}

    if st.session_state.token:
        headers["Authorization"] = (
            f"Bearer {st.session_state.token}"
        )

    extension = filename.lower().rsplit(".", 1)[-1]

    content_types = {
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf",
        "txt": "text/plain",
    }

    content_type = content_types.get(
        extension,
        "application/octet-stream",
    )

    try:
        response = requests.post(
            url=f"{API_URL}{endpoint}",
            files={
                "file": (
                    filename,
                    file_bytes,
                    content_type,
                )
            },
            headers=headers,
            timeout=120,
        )

        if response.status_code >= 400:
            try:
                detail = response.json().get(
                    "detail",
                    response.text,
                )
            except ValueError:
                detail = response.text

            st.error(
                f"API error ({response.status_code}): {detail}"
            )
            return None

        return response.json()

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API. Make sure FastAPI is running.")
        return None

    except requests.exceptions.Timeout:
        st.error("The upload request timed out. Please try again.")
        return None

    except requests.exceptions.RequestException as error:
        st.error(f"Upload failed: {error}")
        return None

def get_commodities():
    return api_request("GET", "/commodities") or []


def get_locations():
    return api_request("GET", "/locations") or []


def get_prices():
    return api_request("GET", "/prices") or []


# =========================================================
# AUTHENTICATION
# =========================================================

def logout():
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.chat_history = []
    st.rerun()


def authentication_screen():
    st.title("🇳🇬 Naija Cost of Living Intelligence")
    st.markdown(
        "Explore commodity prices, understand price movements "
        "and access AI-assisted cost-of-living insights."
    )

    st.info(
        "The initial dataset contains simulated prices for "
        "educational and demonstration purposes. "
        "They are not verified market prices."
    )

    login_tab, signup_tab = st.tabs(
        ["Login", "Create account"]
    )

    with login_tab:
        st.subheader("Welcome back")

        with st.form("login_form"):
            email = st.text_input("Email address")
            password = st.text_input(
                "Password",
                type="password",
            )

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True,
            )

        if submitted:
            result = api_request(
                "POST",
                "/auth/login",
                {
                    "email": email,
                    "password": password,
                },
            )

            if result and result.get("access_token"):
                st.session_state.token = result["access_token"]

                user = api_request("GET", "/auth/me")

                if user:
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.session_state.token = None

    with signup_tab:
        st.subheader("Create your account")

        with st.form("signup_form"):
            new_email = st.text_input(
                "Email address",
                key="signup_email",
            )

            new_password = st.text_input(
                "Password",
                type="password",
                key="signup_password",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
            )

            submitted = st.form_submit_button(
                "Create account",
                use_container_width=True,
            )

        if submitted:
            if new_password != confirm_password:
                st.error("Passwords do not match.")

            elif len(new_password) < 8:
                st.error(
                    "Password must contain at least 8 characters."
                )

            else:
                result = api_request(
                    "POST",
                    "/auth/signup",
                    {
                        "email": new_email,
                        "password": new_password,
                    },
                )

                if result:
                    st.success(
                        "Account created successfully. "
                        "You can now log in."
                    )


# =========================================================
# PAGE HEADER AND SIDEBAR
# =========================================================

def sidebar():
    with st.sidebar:
        st.title("🇳🇬 Naija COLI")

        st.caption("Cost of Living Intelligence")

        st.divider()

        pages = [
            "Overview",
            "Price Explorer",
            "City Comparison",
            "Submit Price",
            "Bulk Price Upload",
            "My Submissions",
            "FoodBud AI",
        ]

        selected = st.radio(
            "Navigation",
            pages,
            key="navigation",
        )

        st.session_state.page = selected

        st.divider()

        if st.session_state.user:
            st.write(
                f"Signed in as **{st.session_state.user.get('email', '')}**"
            )

        st.caption(f"API: {API_URL}")

        if st.button("Logout", use_container_width=True):
            logout()


def page_header(title, description):
    st.title(title)
    st.caption(description)


def currency(value):
    return f"₦{float(value):,.2f}"


# =========================================================
# OVERVIEW
# =========================================================

def overview_page():
    page_header(
        "Overview",
        "A snapshot of essential commodity prices across "
        "selected Nigerian cities.",
    )

    overview = api_request(
        "GET",
        "/analytics/overview",
    )

    if not overview:
        return

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Commodities",
        overview["total_commodities"],
    )

    c2.metric(
        "Locations",
        overview["total_locations"],
    )

    c3.metric(
        "Price records",
        overview["total_price_records"],
    )

    st.divider()

    st.info(
        "Dataset notice: The original seeded prices are simulated. "
        "They are not verified Nigerian market prices."
    )

    prices = get_prices()
    commodities = get_commodities()
    locations = get_locations()

    if not prices or not commodities or not locations:
        st.warning("No price data is currently available.")
        return

    commodity_map = {
        item["id"]: item["name"]
        for item in commodities
    }

    location_map = {
        item["id"]: item["city"]
        for item in locations
    }

    df = pd.DataFrame(prices)

    df["commodity"] = df["commodity_id"].map(commodity_map)
    df["city"] = df["location_id"].map(location_map)
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])
    df["price"] = pd.to_numeric(df["price"])

    df = df.dropna(
        subset=["commodity", "city", "recorded_at", "price"]
    )

    if df.empty:
        st.warning("There are no chartable price records.")
        return

    st.subheader("Commodity price trends")

    commodity_names = sorted(
        df["commodity"].dropna().unique().tolist()
    )

    selected_commodity = st.selectbox(
        "Select commodity",
        commodity_names,
    )

    chart_df = df[
        df["commodity"] == selected_commodity
    ].sort_values("recorded_at")

    fig = px.line(
        chart_df,
        x="recorded_at",
        y="price",
        color="city",
        markers=True,
        title=f"{selected_commodity} price trend",
        labels={
            "recorded_at": "Month",
            "price": "Price (NGN)",
            "city": "City",
        },
    )

    fig.update_layout(
        hovermode="x unified",
        yaxis_tickprefix="₦",
        template="plotly_white",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Latest recorded prices")

    latest_date = df["recorded_at"].max()

    latest = df[
        df["recorded_at"] == latest_date
    ].copy()

    latest["price"] = latest["price"].apply(currency)

    st.dataframe(
        latest[
            ["commodity", "city", "price", "data_source"]
        ].rename(
            columns={
                "commodity": "Commodity",
                "city": "City",
                "price": "Price",
                "data_source": "Data source",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# PRICE EXPLORER
# =========================================================

def price_explorer_page():
    page_header(
        "Price Explorer",
        "Explore recorded prices by commodity and location.",
    )

    commodities = get_commodities()
    locations = get_locations()
    prices = get_prices()

    if not commodities or not locations or not prices:
        st.warning("Price exploration data is unavailable.")
        return

    commodity_map = {
        item["id"]: item for item in commodities
    }

    location_map = {
        item["id"]: item for item in locations
    }

    commodity_options = {
        item["name"]: item["id"]
        for item in commodities
    }

    location_options = {
        "All cities": None,
        **{
            item["city"]: item["id"]
            for item in locations
        },
    }

    col1, col2 = st.columns(2)

    with col1:
        selected_commodity = st.selectbox(
            "Commodity",
            list(commodity_options.keys()),
        )

    with col2:
        selected_location = st.selectbox(
            "Location",
            list(location_options.keys()),
        )

    df = pd.DataFrame(prices)

    df = df[
        df["commodity_id"] ==
        commodity_options[selected_commodity]
    ]

    location_id = location_options[selected_location]

    if location_id is not None:
        df = df[df["location_id"] == location_id]

    if df.empty:
        st.warning("No records match your filters.")
        return

    df["recorded_at"] = pd.to_datetime(df["recorded_at"])
    df["price"] = pd.to_numeric(df["price"])
    df["city"] = df["location_id"].map(
        lambda value: location_map[value]["city"]
    )

    df = df.sort_values("recorded_at")

    fig = px.line(
        df,
        x="recorded_at",
        y="price",
        color="city",
        markers=True,
        title=f"{selected_commodity} price history",
        labels={
            "recorded_at": "Month",
            "price": "Price (NGN)",
            "city": "City",
        },
    )

    fig.update_layout(
        yaxis_tickprefix="₦",
        template="plotly_white",
    )

    st.plotly_chart(fig, use_container_width=True)

    display = df[
        ["city", "recorded_at", "price", "data_source"]
    ].copy()

    display["price"] = display["price"].apply(currency)

    st.dataframe(
        display.rename(
            columns={
                "city": "City",
                "recorded_at": "Recorded date",
                "price": "Price",
                "data_source": "Data source",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# CITY COMPARISON
# =========================================================

def comparison_page():
    page_header(
        "City Comparison",
        "Compare the same commodity across Lagos, Ibadan and Abuja.",
    )

    commodities = get_commodities()

    if not commodities:
        st.warning("Commodity catalogue unavailable.")
        return

    selected = st.selectbox(
        "Select commodity",
        commodities,
        format_func=lambda item: item["name"],
    )

    selected_date = st.date_input(
        "Select comparison date",
        value=date(2025, 12, 1),
        min_value=date(2025, 1, 1),
        max_value=date(2025, 12, 1),
    )

    if st.button("Compare prices", type="primary"):
        result = api_request(
            "GET",
            "/analytics/compare",
            params={
                "commodity_id": selected["id"],
                "recorded_at": selected_date.isoformat(),
            },
        )

        if result:
            records = result.get("results", [])

            if not records:
                st.warning("No comparison data was found.")
                return

            df = pd.DataFrame(records)

            df["price"] = pd.to_numeric(df["price"])

            fig = px.bar(
                df,
                x="city",
                y="price",
                color="city",
                text="price",
                title=(
                    f"{selected['name']} prices "
                    f"on {selected_date.strftime('%d %B %Y')}"
                ),
            )

            fig.update_traces(
                texttemplate="₦%{y:,.2f}",
                textposition="outside",
            )

            fig.update_layout(
                yaxis_tickprefix="₦",
                template="plotly_white",
                showlegend=False,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            display = df.copy()
            display["price"] = display["price"].apply(currency)

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
            )

            st.info(
                "The seeded dataset contains simulated prices."
            )


# =========================================================
# SUBMIT PRICE
# =========================================================

def submit_price_page():
    page_header(
        "Submit a Price",
        "Contribute a commodity price observation to the dataset.",
    )

    commodities = get_commodities()
    locations = get_locations()

    if not commodities or not locations:
        st.warning("Catalogue data is unavailable.")
        return

    commodity_options = {
        item["name"]: item
        for item in commodities
    }

    location_options = {
        item["city"]: item
        for item in locations
    }

    with st.form("submit_price_form"):
        commodity_name = st.selectbox(
            "Commodity",
            list(commodity_options.keys()),
        )

        location_name = st.selectbox(
            "City",
            list(location_options.keys()),
        )

        price = st.number_input(
            "Price (NGN)",
            min_value=0.01,
            value=1000.00,
            step=50.00,
        )

        recorded_at = st.date_input(
            "Date recorded",
            value=date.today(),
        )

        submitted = st.form_submit_button(
            "Submit price",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        selected_commodity = commodity_options[commodity_name]
        selected_location = location_options[location_name]

        result = api_request(
            "POST",
            "/prices",
            {
                "commodity_id": selected_commodity["id"],
                "location_id": selected_location["id"],
                "price": str(Decimal(str(price)).quantize(Decimal("0.01"))),
                "recorded_at": recorded_at.isoformat(),
            },
        )

        if result:
            st.success(
                f"Price submitted successfully! Record ID: {result['id']}"
            )
            st.info(
                "Your submission is stored as USER_SUBMITTED "
                "and is separate from the simulated seeded records."
            )


# =========================================================
# MY SUBMISSIONS
# =========================================================

def my_submissions_page():
    page_header(
        "My Submissions",
        "Manage only the price records you have submitted.",
    )

    prices = get_prices()
    commodities = get_commodities()
    locations = get_locations()

    if not prices:
        st.info("No price records are available.")
        return

    user_id = st.session_state.user["id"]

    own_records = [
        record
        for record in prices
        if record.get("created_by") == user_id
    ]

    if not own_records:
        st.info(
            "You have not submitted any price records yet."
        )
        return

    commodity_map = {
        item["id"]: item["name"]
        for item in commodities
    }

    location_map = {
        item["id"]: item["city"]
        for item in locations
    }

    display = pd.DataFrame(own_records)

    display["commodity"] = display["commodity_id"].map(commodity_map)
    display["city"] = display["location_id"].map(location_map)

    st.dataframe(
        display[
            ["id", "commodity", "city", "price", "recorded_at"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    record_options = {
        (
            f"#{record['id']} - "
            f"{commodity_map.get(record['commodity_id'], 'Unknown')} "
            f"({location_map.get(record['location_id'], 'Unknown')})"
        ): record
        for record in own_records
    }

    selected_label = st.selectbox(
        "Select a submission to manage",
        list(record_options.keys()),
    )

    selected_record = record_options[selected_label]

    st.subheader("Edit submission")

    with st.form("edit_price_form"):
        new_price = st.number_input(
            "Updated price (NGN)",
            min_value=0.01,
            value=float(selected_record["price"]),
            step=50.00,
        )

        new_date = st.date_input(
            "Updated recorded date",
            value=date.fromisoformat(
                selected_record["recorded_at"]
            ),
        )

        update = st.form_submit_button(
            "Save changes",
            use_container_width=True,
        )

    if update:
        result = api_request(
            "PATCH",
            f"/prices/{selected_record['id']}",
            {
                "price": str(new_price),
                "recorded_at": new_date.isoformat(),
            },
        )

        if result:
            st.success("Your submission was updated.")
            st.rerun()

    st.subheader("Delete submission")

    confirm_delete = st.checkbox(
        "I understand this action cannot be undone."
    )

    if st.button(
        "Delete selected record",
        type="secondary",
        disabled=not confirm_delete,
    ):
        result = api_request(
            "DELETE",
            f"/prices/{selected_record['id']}",
        )

        if result is True:
            st.success("Submission deleted.")
            st.rerun()


# =========================================================
# BULK PRICE UPLOAD
# =========================================================

def bulk_price_upload_page():
    page_header(
        "Bulk Price Upload",
        "Import multiple commodity prices using CSV or Excel.",
    )

    st.info(
        "Upload commodity price records in bulk. "
        "Your imported records will be added alongside the "
        "simulated dataset and identified as USER_SUBMITTED."
    )

    st.subheader("1. Download the upload template")

    template = pd.DataFrame([
        {
            "commodity": "Rice",
            "location": "Lagos",
            "price": 4500,
            "recorded_at": "2026-11-05",
        },
        {
            "commodity": "Beans",
            "location": "Ibadan",
            "price": 3200,
            "recorded_at": "2026-11-05",
        },
        {
            "commodity": "Garri",
            "location": "Abuja",
            "price": 1800,
            "recorded_at": "2026-11-05",
        },
    ])

    st.download_button(
        label="Download CSV Template",
        data=template.to_csv(index=False).encode("utf-8"),
        file_name="naija_price_upload_template.csv",
        mime="text/csv",
    )

    st.caption(
        "Required columns: commodity, location, price, recorded_at. "
        "Use catalogue commodity names and city names."
    )

    st.divider()

    st.subheader("2. Upload your price file")

    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx"],
        help="Maximum file size: 5 MB. Maximum records: 1,000.",
        key="bulk_price_file",
    )

    if uploaded_file is None:
        st.caption("Upload a file to begin validation.")
        return

    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name

    import hashlib

    current_file_hash = hashlib.sha256(file_bytes).hexdigest()

    if st.button(
        "Validate and Preview",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner("Validating your file..."):
            result = api_upload_request(
                "/prices/import/preview",
                filename,
                file_bytes,
            )

        if result is not None:
            st.session_state.bulk_preview = result
            st.session_state.bulk_file_name = filename
            st.session_state.bulk_file_bytes = file_bytes
            st.session_state.bulk_file_hash = current_file_hash

    preview = st.session_state.get("bulk_preview")

    if not preview:
        return

    preview_hash = st.session_state.get("bulk_file_hash")

    if current_file_hash != preview_hash:
        st.warning(
            "The selected file has changed since the last preview. "
            "Validate and preview the new file before confirming."
        )
        return

    st.divider()

    st.subheader("3. Review validation results")

    valid_rows = preview.get("valid_rows", [])
    invalid_rows = preview.get("invalid_rows", [])
    duplicate_rows = preview.get("duplicate_rows", [])

    metric_columns = st.columns(3)

    metric_columns[0].metric(
        "Valid records",
        len(valid_rows),
    )

    metric_columns[1].metric(
        "Invalid records",
        len(invalid_rows),
    )

    metric_columns[2].metric(
        "Duplicates",
        len(duplicate_rows),
    )

    if valid_rows:
        st.markdown("**Records ready for import**")
        st.dataframe(
            pd.DataFrame(valid_rows),
            use_container_width=True,
            hide_index=True,
        )

    if invalid_rows:
        with st.expander(
            f"Invalid records ({len(invalid_rows)})",
            expanded=True,
        ):
            st.dataframe(
                pd.DataFrame(invalid_rows),
                use_container_width=True,
                hide_index=True,
            )

    if duplicate_rows:
        with st.expander(
            f"Duplicate records ({len(duplicate_rows)})",
        ):
            st.dataframe(
                pd.DataFrame(duplicate_rows),
                use_container_width=True,
                hide_index=True,
            )

    st.divider()

    st.subheader("4. Confirm import")

    st.caption(
        "Only valid records will be imported. Invalid and duplicate "
        "records will be skipped. Existing simulated records will "
        "not be modified."
    )

    if not valid_rows:
        st.warning("There are no valid records available to import.")
    else:
        confirm = st.checkbox(
            f"I confirm importing {len(valid_rows)} valid records.",
            key="confirm_bulk_import",
        )

        if st.button(
            "Confirm and Import Prices",
            type="primary",
            disabled=not confirm,
            use_container_width=True,
        ):
            with st.spinner("Importing price records..."):
                result = api_upload_request(
                    "/prices/import/confirm",
                    st.session_state.bulk_file_name,
                    st.session_state.bulk_file_bytes,
                )

            if result is not None:
                if result.get("status") == "success":
                    st.success(
                        f"Successfully imported "
                        f"{result.get('imported_count', 0)} records!"
                    )
                else:
                    st.warning("No new records were imported.")

                st.write(
                    f"Imported: {result.get('imported_count', 0)}"
                )
                st.write(
                    f"Skipped invalid: {result.get('invalid_count', 0)}"
                )
                st.write(
                    f"Skipped duplicates: "
                    f"{result.get('duplicate_count', 0)}"
                )

                st.session_state.bulk_preview = None
                st.session_state.bulk_file_name = None
                st.session_state.bulk_file_bytes = None
                st.session_state.bulk_file_hash = None

                st.rerun()

# =========================================================
# FOODBUD AI
# =========================================================

def ask_naija_page():
    page_header(
        "FoodBud AI",
        "Ask questions about commodity prices, comparisons, "
        "price changes and project documentation.",
    )

    st.info(
        "FoodBud AI uses database tools for structured price questions "
        "and document retrieval for methodology questions. "
        "Some answers may use a deterministic fallback if Gemini "
        "is unavailable."
    )

    with st.expander("Upload a document for FoodBud AI"):
        st.caption(
            "Upload a PDF or TXT document. "
            "Only you can retrieve information from your uploaded documents."
        )

        uploaded_document = st.file_uploader(
            "Choose a PDF or TXT file",
            type=["pdf", "txt"],
            key="foodbud_document_upload",
            help="Maximum file size: 5 MB.",
        )

        if uploaded_document:
            document_size = len(uploaded_document.getvalue())

            st.caption(
                f"Selected: {uploaded_document.name} "
                f"({document_size / 1024:.1f} KB)"
            )

            if document_size > 5 * 1024 * 1024:
                st.error("File size must not exceed 5 MB.")

            elif st.button(
                "Upload and index document",
                key="foodbud_upload_button",
                disabled=document_size == 0,
            ):
                with st.spinner("Extracting and indexing document..."):
                    upload_result = api_upload_request(
                        "/documents/upload",
                        uploaded_document.name,
                        uploaded_document.getvalue(),
                    )

                if upload_result:
                    st.success(
                        f"'{upload_result.get('filename', uploaded_document.name)}' "
                        "was uploaded and indexed successfully."
                    )

                    st.write(
                        "Text chunks indexed:",
                        upload_result.get("chunks_stored", 0),
                    )

                    st.caption(
                        "You can now ask FoodBud AI questions about this document."
                    )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("fallback"):
                st.caption(
                    "Deterministic fallback response — Gemini unavailable."
                )

    question = st.chat_input(
        "Ask about food prices in Nigeria..."
    )

    if question:
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analysing your question..."):
                result = api_request(
                    "POST",
                    "/agent/ask",
                    {"question": question},
                )

                if result:
                    answer = result.get(
                        "answer",
                        "No answer was returned.",
                    )

                    st.markdown(answer)

                    tools = result.get("tools_used", [])

                    if tools:
                        st.caption(
                            "Tools used: " + ", ".join(tools)
                        )

                    if result.get("fallback"):
                        st.warning(
                            "This answer was generated using "
                            "the local deterministic fallback."
                        )

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "fallback": result.get("fallback", False),
                        }
                    )

                else:
                    st.error(
                        "Unable to retrieve an answer. "
                        "Please try again."
                    )

        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()


# =========================================================
# MAIN APPLICATION
# =========================================================

def main():
    if not st.session_state.token:
        authentication_screen()
        return

    if not st.session_state.user:
        user = api_request("GET", "/auth/me")

        if not user:
            st.session_state.token = None
            st.rerun()

        st.session_state.user = user

    sidebar()

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        [data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.08);
            padding: 16px;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    page = st.session_state.page

    if page == "Overview":
        overview_page()

    elif page == "Price Explorer":
        price_explorer_page()

    elif page == "City Comparison":
        comparison_page()

    elif page == "Submit Price":
        submit_price_page()

    elif page == "My Submissions":
        my_submissions_page()

    elif page == "Bulk Price Upload":
        bulk_price_upload_page()

    elif page == "FoodBud AI":
        ask_naija_page()


if __name__ == "__main__":
    main()
