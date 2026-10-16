import requests
import streamlit as st


# =========================================================
# CONFIG
# =========================================================

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Hospital Patient Tracker",
    page_icon="🏥",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def handle_response(response):
    if response.status_code in [200, 201]:
        return response.json()

    if response.status_code == 204:
        return {"message": "Operation completed successfully."}

    try:
        detail = response.json().get("detail", "Something went wrong.")
    except Exception:
        detail = response.text

    st.error(f"Error {response.status_code}: {detail}")
    return None


# =========================================================
# LOGIN
# =========================================================

if not st.session_state.token:

    st.title("🏥 Hospital Patient Tracker")

    st.subheader("Login")

    with st.form("login_form"):

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "🔐 Login"
        )

        if submitted:

            if not username or not password:

                st.warning(
                    "Please enter your username and password."
                )

            else:

                try:

                    response = requests.post(
                        f"{API_URL}/login",
                        json={
                            "username": username,
                            "password": password
                        },
                        timeout=30
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.session_state.token = (
                            data["access_token"]
                        )

                        st.session_state.username = username

                        st.success("Login successful!")

                        st.rerun()

                    else:

                        try:
                            detail = response.json().get(
                                "detail",
                                "Invalid username or password."
                            )
                        except Exception:
                            detail = "Invalid username or password."

                        st.error(detail)

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Could not connect to the FastAPI server. "
                        "Make sure your backend is running."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "The request timed out."
                    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏥 Hospital Tracker")

st.sidebar.write(
    f"Logged in as: **{st.session_state.username}**"
)

if st.sidebar.button("🚪 Logout"):

    st.session_state.token = None
    st.session_state.username = None

    st.rerun()


st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Dashboard",
        "🧮 Week 1 — BMI Calculator",
        "👤 Week 2/3 — Patient Management",
        "🔐 Week 5 — Authentication",
        "🤖 Week 6 — Risk Prediction",
        "🧠 Week 7 — AI Extraction",
        "📚 Week 8 — RAG Document Search"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.title("🏥 Hospital Patient Tracker")

    st.caption(
        "AI-powered Hospital Patient Tracker "
        "built across Weeks 1–7"
    )

    st.success(
        f"Logged in as {st.session_state.username}"
    )

    st.divider()

    st.subheader("📚 Course Features")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Patient Management",
            "CRUD"
        )

        st.write(
            "Create, view, update and delete patient records."
        )

    with col2:

        st.metric(
            "ML Prediction",
            "Week 6"
        )

        st.write(
            "Predict whether a patient is high risk."
        )

    with col3:

        st.metric(
            "AI Extraction",
            "Week 7"
        )

        st.write(
            "Extract patient information from natural language."
        )
    with col3:
        st.metric(
            "RAG Search",
            "Week 8"
        )

        st.write(
            "Upload documents, create embeddings, "
            "and search them using semantic similarity."
        )
    st.divider()

    st.subheader("🔌 Available API Endpoints")

    endpoints = [
        ("POST", "/signup", "Create user"),
        ("POST", "/login", "Login"),
        ("POST", "/patients/", "Create patient"),
        ("GET", "/patients/", "Get all patients"),
        ("GET", "/patients/{patient_id}", "Get one patient"),
        ("PUT", "/patients/{patient_id}", "Update patient"),
        ("DELETE", "/patients/{patient_id}", "Delete patient"),
        ("POST", "/predict", "ML risk prediction"),
        ("POST", "/patients/extract", "AI patient extraction"),
        ("POST", "/documents/upload", "Upload and ingest document"),
        ("POST", "/documents/search", "Semantic document search"),
    ]

    for method, endpoint, description in endpoints:

        st.code(
            f"{method:<7} {endpoint:<30} {description}"
        )


# =========================================================
# WEEK 1 — BMI
# =========================================================

elif page == "🧮 Week 1 — BMI Calculator":

    st.title("🧮 Week 1 — BMI Calculator")

    st.write(
        "Calculate Body Mass Index using height and weight."
    )

    col1, col2 = st.columns(2)

    with col1:

        weight = st.number_input(
            "Weight (kg)",
            min_value=1.0,
            max_value=300.0,
            value=70.0
        )

    with col2:

        height = st.number_input(
            "Height (m)",
            min_value=0.5,
            max_value=2.5,
            value=1.75
        )

    if st.button("Calculate BMI"):

        bmi = weight / (height ** 2)

        st.metric(
            "BMI",
            f"{bmi:.2f}"
        )

        if bmi < 18.5:

            st.info("Underweight")

        elif bmi < 25:

            st.success("Normal weight")

        elif bmi < 30:

            st.warning("Overweight")

        else:

            st.error("Obese")


# =========================================================
# WEEK 2/3 — PATIENT MANAGEMENT
# =========================================================

elif page == "👤 Week 2/3 — Patient Management":

    st.title("👤 Week 2/3 — Patient Management")

    operation = st.selectbox(
        "Choose operation",
        [
            "Create Patient",
            "View All Patients",
            "Get Patient",
            "Update Patient",
            "Delete Patient"
        ]
    )

    # -----------------------------------------------------
    # CREATE
    # -----------------------------------------------------

    if operation == "Create Patient":

        st.subheader("➕ Create Patient")

        with st.form("create_patient"):

            patient_id = st.text_input(
                "Patient ID",
                placeholder="HNS-002"
            )

            name = st.text_input(
                "Name"
            )

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=20
            )

            email = st.text_input(
                "Email"
            )

            number = st.text_input(
                "Phone Number"
            )

            gender = st.selectbox(
                "Gender",
                ["M", "F"]
            )

            condition = st.text_input(
                "Condition"
            )

            submitted = st.form_submit_button(
                "Create Patient"
            )

        if submitted:

            data = {
                "patient_id": patient_id,
                "name": name,
                "age": age,
                "email": email,
                "number": number,
                "gender": gender,
                "condition": condition
            }

            try:

                response = requests.post(
                    f"{API_URL}/patients/",
                    json=data,
                    headers=auth_headers(),
                    timeout=30
                )

                result = handle_response(response)

                if result:

                    st.success(
                        "Patient created successfully."
                    )

                    st.json(result)

            except requests.exceptions.RequestException as exc:

                st.error(str(exc))

    # -----------------------------------------------------
    # GET ALL
    # -----------------------------------------------------

    elif operation == "View All Patients":

        st.subheader("📋 All Patients")

        if st.button("Load Patients"):

            try:

                response = requests.get(
                    f"{API_URL}/patients/",
                    headers=auth_headers(),
                    timeout=30
                )

                result = handle_response(response)

                if result is not None:

                    st.dataframe(
                        result,
                        use_container_width=True
                    )

            except requests.exceptions.RequestException as exc:

                st.error(str(exc))

    # -----------------------------------------------------
    # GET ONE
    # -----------------------------------------------------

    elif operation == "Get Patient":

        st.subheader("🔎 Get Patient")

        patient_id = st.text_input(
            "Patient ID",
            placeholder="HNS-001"
        )

        if st.button("Find Patient"):

            try:

                response = requests.get(
                    f"{API_URL}/patients/{patient_id}",
                    headers=auth_headers(),
                    timeout=30
                )

                result = handle_response(response)

                if result:

                    st.json(result)

            except requests.exceptions.RequestException as exc:

                st.error(str(exc))

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    elif operation == "Update Patient":

        st.subheader("✏️ Update Patient")

        patient_id = st.text_input(
            "Patient ID to update",
            placeholder="HNS-001"
        )

        with st.form("update_patient"):

            name = st.text_input("Name")

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=20
            )

            email = st.text_input("Email")

            number = st.text_input("Phone Number")

            gender = st.selectbox(
                "Gender",
                ["M", "F"]
            )

            condition = st.text_input("Condition")

            submitted = st.form_submit_button(
                "Update Patient"
            )

        if submitted:

            data = {
                "patient_id": patient_id,
                "name": name,
                "age": age,
                "email": email,
                "number": number,
                "gender": gender,
                "condition": condition
            }

            try:

                response = requests.put(
                    f"{API_URL}/patients/{patient_id}",
                    json=data,
                    headers=auth_headers(),
                    timeout=30
                )

                result = handle_response(response)

                if result:

                    st.success(
                        "Patient updated successfully."
                    )

                    st.json(result)

            except requests.exceptions.RequestException as exc:

                st.error(str(exc))

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------

    elif operation == "Delete Patient":

        st.subheader("🗑️ Delete Patient")

        patient_id = st.text_input(
            "Patient ID",
            placeholder="HNS-001"
        )

        if st.button("Delete Patient"):

            try:

                response = requests.delete(
                    f"{API_URL}/patients/{patient_id}",
                    headers=auth_headers(),
                    timeout=30
                )

                if response.status_code == 204:

                    st.success(
                        "Patient deleted successfully."
                    )

                else:

                    handle_response(response)

            except requests.exceptions.RequestException as exc:

                st.error(str(exc))


# =========================================================
# WEEK 5 — AUTHENTICATION
# =========================================================

elif page == "🔐 Week 5 — Authentication":

    st.title("🔐 Week 5 — Authentication")

    st.info(
        "Your current session is authenticated using JWT."
    )

    st.subheader("Current Session")

    st.write(
        f"**Username:** {st.session_state.username}"
    )

    st.write(
        "**Authentication:** JWT Bearer Token"
    )

    st.write(
        "**Login rate limit:** 5 requests/minute"
    )

    st.divider()

    st.subheader("🔑 Create Another User")

    with st.form("signup_form"):

        new_username = st.text_input(
            "New Username"
        )

        new_password = st.text_input(
            "New Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Create User"
        )

    if submitted:

        try:

            response = requests.post(
                f"{API_URL}/signup",
                json={
                    "username": new_username,
                    "password": new_password
                },
                timeout=30
            )

            result = handle_response(response)

            if result:

                st.success(
                    "User created successfully."
                )

                st.json(result)

        except requests.exceptions.RequestException as exc:

            st.error(str(exc))


# =========================================================
# WEEK 6 — ML RISK PREDICTION
# =========================================================

elif page == "🤖 Week 6 — Risk Prediction":

    st.title("🤖 Week 6 — ML Risk Prediction")

    st.write(
        "Enter patient information to predict whether "
        "the patient is high risk."
    )

    st.info(
        "This uses the trained hospital risk prediction "
        "model from Week 6."
    )

    # -----------------------------------------------------
    # PATIENT INFORMATION
    # -----------------------------------------------------

    st.subheader("Patient Information")

    col1, col2 = st.columns(2)

    with col1:

        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=20,
            step=1
        )

        gender = st.selectbox(
            "Gender",
            ["M", "F"]
        )

        temperature = st.number_input(
            "Temperature (°C)",
            min_value=30.0,
            max_value=45.0,
            value=37.0,
            step=0.1
        )

        heart_rate = st.number_input(
            "Heart Rate (bpm)",
            min_value=30,
            max_value=220,
            value=75,
            step=1
        )

    with col2:

        oxygen_saturation = st.number_input(
            "Oxygen Saturation (%)",
            min_value=50.0,
            max_value=100.0,
            value=98.0,
            step=0.1
        )

        previous_admissions = st.number_input(
            "Previous Admissions",
            min_value=0,
            max_value=50,
            value=0,
            step=1
        )

        symptom_count = st.number_input(
            "Symptom Count",
            min_value=0,
            max_value=20,
            value=1,
            step=1
        )

        chronic_condition = st.selectbox(
            "Chronic Condition",
            [0, 1],
            format_func=lambda x: (
                "Yes" if x == 1 else "No"
            )
        )

    # -----------------------------------------------------
    # PREDICT
    # -----------------------------------------------------

    if st.button("🔮 Predict Risk"):

        data = {
            "age": age,
            "gender": gender,
            "temperature": temperature,
            "heart_rate": heart_rate,
            "oxygen_saturation": oxygen_saturation,
            "previous_admissions": previous_admissions,
            "symptom_count": symptom_count,
            "chronic_condition": chronic_condition
        }

        try:

            response = requests.post(
                f"{API_URL}/predict",
                json=data,
                timeout=30
            )

            result = handle_response(response)

            if result:

                st.divider()

                high_risk = result["high_risk"]
                probability = result["probability"]

                # -------------------------------------------------
                # RESULT
                # -------------------------------------------------

                if high_risk == 1:

                    st.error(
                        "⚠️ HIGH RISK PATIENT"
                    )

                else:

                    st.success(
                        "✅ LOW RISK PATIENT"
                    )

                st.metric(
                    "Risk Probability",
                    f"{probability * 100:.2f}%"
                )

                st.divider()

                # -------------------------------------------------
                # API RESPONSE
                # -------------------------------------------------

                st.subheader("📊 Prediction Result")

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**High Risk:** "
                        f"{high_risk}"
                    )

                with col2:

                    st.write(
                        f"**Probability:** "
                        f"{probability}"
                    )

                with st.expander(
                    "View Raw API Response"
                ):

                    st.json(result)

        except requests.exceptions.Timeout:

            st.error(
                "The prediction request timed out."
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the FastAPI server."
            )

        except requests.exceptions.RequestException as exc:

            st.error(str(exc))

# =========================================================
# WEEK 7 — AI EXTRACTION
# =========================================================

elif page == "🧠 Week 7 — AI Extraction":

    st.title("🧠 Week 7 — AI Patient Information Extraction")

    st.write(
        "Describe a patient in natural language. "
        "Gemini extracts structured information and "
        "matches it against the patient database."
    )

    patient_text = st.text_area(
        "Patient information",
        height=180,
        placeholder=(
            "The patient Salem Khaos is experiencing "
            "fever and fatigue. Temperature is 38.5°C."
        )
    )

    if st.button("🔍 Extract Patient Information"):

        if not patient_text.strip():

            st.warning(
                "Please enter patient information."
            )

        else:

            try:

                response = requests.post(
                    f"{API_URL}/patients/extract",
                    json={
                        "text": patient_text
                    },
                    headers=auth_headers(),
                    timeout=60
                )

                if response.status_code == 200:

                    result = response.json()

                    st.success(
                        "Patient information extracted successfully."
                    )

                    st.divider()

                    # -------------------------------------------------
                    # RESPONSE DATA
                    # -------------------------------------------------

                    patient = result["patient"]

                    new_information = result[
                        "new_information"
                    ]

                    ai_metadata = result.get(
                        "ai_metadata",
                        {}
                    )

                    # -------------------------------------------------
                    # EXISTING PATIENT
                    # -------------------------------------------------

                    st.subheader(
                        "👤 Existing Patient Record"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            f"**Patient ID:** "
                            f"{patient['patient_id']}"
                        )

                        st.write(
                            f"**Name:** "
                            f"{patient['name']}"
                        )

                        st.write(
                            f"**Age:** "
                            f"{patient['age']}"
                        )

                        st.write(
                            f"**Gender:** "
                            f"{patient['gender']}"
                        )

                    with col2:

                        st.write(
                            f"**Email:** "
                            f"{patient['email']}"
                        )

                        st.write(
                            f"**Phone:** "
                            f"{patient['number']}"
                        )

                        st.write(
                            f"**Condition:** "
                            f"{patient['condition']}"
                        )

                    st.divider()

                    # -------------------------------------------------
                    # NEWLY EXTRACTED INFORMATION
                    # -------------------------------------------------

                    st.subheader(
                        "🧠 Newly Extracted Information"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write("**Symptoms**")

                        symptoms = new_information.get(
                            "symptoms",
                            []
                        )

                        if symptoms:

                            for symptom in symptoms:

                                st.write(
                                    f"• {symptom}"
                                )

                        else:

                            st.write(
                                "No symptoms extracted."
                            )

                    with col2:

                        temperature = new_information.get(
                            "temperature"
                        )

                        if temperature is not None:

                            st.metric(
                                "Temperature",
                                f"{temperature} °C"
                            )

                        else:

                            st.write(
                                "**Temperature:** Not provided."
                            )

                    st.divider()

                    # -------------------------------------------------
                    # AI PERFORMANCE METRICS
                    # -------------------------------------------------

                    st.subheader(
                        "📊 AI Request Metadata"
                    )

                    metadata_col1, metadata_col2, metadata_col3, metadata_col4 = (
                        st.columns(4)
                    )

                    with metadata_col1:

                        latency = ai_metadata.get(
                            "latency"
                        )

                        if latency is not None:

                            st.metric(
                                "Latency",
                                f"{latency:.2f}s"
                            )

                        else:

                            st.metric(
                                "Latency",
                                "N/A"
                            )

                    with metadata_col2:

                        estimated_cost = ai_metadata.get(
                            "estimated_cost"
                        )

                        if estimated_cost is not None:

                            st.metric(
                                "Estimated Cost",
                                f"${estimated_cost:.4f}"
                            )

                        else:

                            st.metric(
                                "Estimated Cost",
                                "N/A"
                            )

                    with metadata_col3:

                        attempts = ai_metadata.get(
                            "attempts"
                        )

                        if attempts is not None:

                            st.metric(
                                "Attempts",
                                str(attempts)
                            )

                        else:

                            st.metric(
                                "Attempts",
                                "N/A"
                            )

                    with metadata_col4:

                        ai_status = ai_metadata.get(
                            "status",
                            "Unknown"
                        )

                        st.metric(
                            "Status",
                            ai_status
                        )

                    st.divider()

                    # -------------------------------------------------
                    # AI SAFETY / RELIABILITY
                    # -------------------------------------------------

                    st.subheader(
                        "🛡️ AI Safety & Reliability"
                    )

                    st.write(
                        "The AI extraction service includes:"
                    )

                    st.write(
                        "✅ Structured JSON output validation"
                    )

                    st.write(
                        "✅ Retry once after transient Gemini failures"
                    )

                    st.write(
                        "✅ Request timeout handling"
                    )

                    st.write(
                        "✅ Malformed response detection"
                    )

                    st.write(
                        "✅ Existing database record verification"
                    )

                    st.write(
                        "✅ Estimated cost and latency tracking"
                    )

                    st.divider()

                    # -------------------------------------------------
                    # RAW RESPONSE
                    # -------------------------------------------------

                    with st.expander(
                        "🔎 View Raw API Response"
                    ):

                        st.json(result)

                elif response.status_code == 401:

                    st.error(
                        "Your session has expired. "
                        "Please log in again."
                    )

                    st.session_state.token = None
                    st.session_state.username = None

                    st.rerun()

                elif response.status_code == 404:

                    st.error(
                        response.json().get(
                            "detail",
                            "No matching patient found."
                        )
                    )

                elif response.status_code == 409:

                    st.error(
                        response.json().get(
                            "detail",
                            "Multiple patients matched."
                        )
                    )

                elif response.status_code == 502:

                    st.error(
                        response.json().get(
                            "detail",
                            "Gemini returned an invalid response."
                        )
                    )

                elif response.status_code == 503:

                    st.error(
                        response.json().get(
                            "detail",
                            "Gemini is temporarily unavailable."
                        )
                    )

                elif response.status_code == 504:

                    st.error(
                        response.json().get(
                            "detail",
                            "The AI request timed out."
                        )
                    )

                else:

                    try:

                        detail = response.json().get(
                            "detail",
                            "AI extraction failed."
                        )

                    except Exception:

                        detail = response.text

                    st.error(
                        f"Error {response.status_code}: {detail}"
                    )

            except requests.exceptions.Timeout:

                st.error(
                    "The AI request timed out. "
                    "Gemini may be taking too long to respond."
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the FastAPI server."
                )

            except requests.exceptions.RequestException as exc:

                st.error(str(exc))

# =========================================================
# WEEK 8 — RAG DOCUMENT SEARCH
# =========================================================

elif page == "📚 Week 8 — RAG Document Search":

    st.title("📚 Week 8 — RAG Document Search")

    st.write(
        "Upload a PDF or TXT document, ingest it into the "
        "vector database, and search the document using "
        "semantic similarity."
    )

    st.info(
        "Week 8 uses PyMuPDF for document extraction, "
        "two chunking strategies, Gemini embeddings, "
        "and ChromaDB for vector storage."
    )

    # -----------------------------------------------------
    # UPLOAD & INGEST
    # -----------------------------------------------------

    st.subheader("📄 Upload & Ingest Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt"]
    )

    chunking_strategy = st.selectbox(
        "Chunking Strategy",
        ["paragraph", "fixed"],
        help=(
            "Paragraph keeps document structure where possible. "
            "Fixed uses fixed-size chunks with overlap."
        )
    )

    if uploaded_file is not None:

        st.write(
            f"**File:** {uploaded_file.name}"
        )

        st.write(
            f"**Size:** "
            f"{uploaded_file.size / 1024:.2f} KB"
        )

        if st.button("📥 Upload & Ingest"):

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                response = requests.post(
                    f"{API_URL}/documents/upload",
                    files=files,
                    data={
                        "strategy": chunking_strategy
                    },
                    headers=auth_headers(),
                    timeout=60
                )
                st.write(response.status_code)
                st.write(response.text)

                result = handle_response(response)

                if result:

                    st.success(
                        "Document uploaded and ingested successfully."
                    )

                    st.subheader("📊 Ingestion Result")

                    st.json(result)

            except requests.exceptions.Timeout:

                st.error(
                    "The document ingestion request timed out."
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the FastAPI server."
                )

            except requests.exceptions.RequestException as exc:

                st.error(str(exc))

    st.divider()

    # -----------------------------------------------------
    # SEMANTIC SEARCH
    # -----------------------------------------------------

    st.subheader("🔎 Semantic Document Search")

    search_query = st.text_area(
        "Ask a question about your documents",
        height=120,
        placeholder=(
            "What training and development does "
            "the employee want in the next quarter?"
        )
    )

    search_strategy = st.selectbox(
        "Search Strategy",
        ["paragraph", "fixed"],
        key="week8_search_strategy"
    )

    n_results = st.number_input(
        "Number of Results",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )

    if st.button("🔍 Search Documents"):

        if not search_query.strip():

            st.warning(
                "Please enter a search question."
            )

        else:

            try:

                response = requests.post(
                    f"{API_URL}/documents/search",
                    json={
                        "query": search_query,
                        "n_results": n_results,
                        "strategy": search_strategy
                    },
                    headers=auth_headers(),
                    timeout=60
                )

                result = handle_response(response)

                if result:

                    st.success(
                        "Search completed successfully."
                    )

                    st.divider()

                    st.subheader("📚 Retrieved Documents")

                    # Display retrieved results
                    results = result.get(
                        "results",
                        result
                    )

                    if isinstance(results, list):

                        for index, item in enumerate(
                            results,
                            start=1
                        ):

                            st.markdown(
                                f"### Result {index}"
                            )

                            if isinstance(item, dict):

                                filename = item.get(
                                    "filename",
                                    item.get(
                                        "source",
                                        "Unknown"
                                    )
                                )

                                pages = item.get(
                                    "pages",
                                    "Unknown"
                                )

                                distance = item.get(
                                    "distance"
                                )

                                chunk = item.get(
                                    "text",
                                    item.get(
                                        "chunk",
                                        ""
                                    )
                                )

                                st.write(
                                    f"**Source:** {filename}"
                                )

                                st.write(
                                    f"**Pages:** {pages}"
                                )

                                if distance is not None:

                                    st.write(
                                        f"**Distance:** "
                                        f"{distance:.4f}"
                                    )

                                st.write(
                                    "**Retrieved Text:**"
                                )

                                st.info(chunk)

                            else:

                                st.write(item)

                            st.divider()

                    else:

                        st.json(result)

            except requests.exceptions.Timeout:

                st.error(
                    "The search request timed out."
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the FastAPI server."
                )

            except requests.exceptions.RequestException as exc:

                st.error(str(exc))