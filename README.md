

🧠 Pneumonia AI Detection

An advanced **AI-based Pneumonia Detection System** that leverages deep learning to classify chest X-ray images as **Normal**, **Bacterial Pneumonia**, or **Viral Pneumonia**.
This enhanced version integrates **Capteche verification**, **email notifications**, **user profile management**, and **data analytics dashboards** — providing a complete, interactive medical support platform.

---

## 🚀 **Features**

### 🩺 **Core Functionality**

* **AI-Based Detection:** Classifies X-ray images into *Normal*, *Bacterial Pneumonia*, and *Viral Pneumonia* using a fine-tuned **VGG model**.
* **Confidence Score:** Displays prediction confidence for each class.
* **Image Upload:** Upload X-ray images securely through the web interface.

### 🔐 **User & Security**

* **Email Verification (Capteche API):** Uses Capteche API for real-time email verification during signup.
* **Secure Authentication:** Login and registration with validation and session management.
* **Profile Management:** Users can update personal details and profile images.

### 📊 **Analytics Dashboard**

* **Data Insights:** View AI prediction trends, patient demographics, and analysis over time.
* **Interactive Charts:** Graphical representation of detection results.
* **Admin Overview:** Allows administrators to manage patients, monitor usage, and view reports.

### 💬 **Email Integration**

* Automated email alerts after registration or prediction completion.
* Optional patient report delivery via email.

### 🧩 **Database Integration**

* Stores user details, image results, and activity logs in **SQLite**.
* Includes an analytics table for insights and trend evaluation.

---

## 🏗️ **Tech Stack**

| Category               | Technology                       |
| ---------------------- | -------------------------------- |
| **Frontend**           | HTML, CSS, JavaScript, Bootstrap |
| **Backend**            | Flask (Python)                   |
| **Machine Learning**   | TensorFlow, Keras (VGG Model)    |
| **Database**           | SQLite                           |
| **Email Verification** | Capteche API                     |
| **Version Control**    | Git & GitHub                     |
| **Model Storage**      | Git LFS (Large File Storage)     |

---

## ⚙️ **Installation & Setup**

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Sidddhh/Pneumonia_Ai.git
cd Pneumonia_Ai
```

### 2️⃣ Create and Activate a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate       # On Windows
source venv/bin/activate    # On Mac/Linux
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Add Environment Variables

Create a `.env` file in the project root (not tracked by Git):

```
SECRET_KEY=your_secret_key
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_password
CAPTECHE_API_KEY=your_capteche_key
```

### 5️⃣ Initialize the Database

```bash
python create_db.py
```

### 6️⃣ Run the Flask Application

```bash
python app.py
```

Visit the app in your browser:
👉 `http://127.0.0.1:5000/`

---

## 📈 **Analytics Dashboard Preview**

The dashboard provides insights such as:

* Total users and patients.
* Number of predictions by category.
* Accuracy and performance metrics.
* Daily/weekly activity graphs.

---

## 📬 **Email Integration Flow**

1. User registers → Email verification (Capteche API).
2. Admin/patient receives email confirmation.
3. Optionally, send AI prediction results to patient’s email.

---

## 👤 **Profile Management**

* Add/update profile picture.
* Edit name, contact details, and credentials.
* Manage previous predictions and reports.

---

## 📦 **Project Structure**

```
Pneumonia_Ai/
│
├── app.py                # Main Flask application
├── instance/
│   └── database.db       # SQLite database
├── static/
│   ├── uploads/          # Uploaded X-rays and avatars
│   └── css/js/images     # Frontend assets
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── analytics.html
│   ├── edit_patient.html
│   └── profile.html
├── .env                  # Environment variables (ignored in Git)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧪 **Model Details**

* Architecture: **VGG16 (fine-tuned)**
* Framework: **TensorFlow / Keras**
* Input: Chest X-ray Images
* Output: Predicted Class + Confidence Score

---

## 🔒 **Security Notes**

* `.env` is excluded from version control using `.gitignore`
* Sensitive keys are never exposed in the repo.
* All uploads and user data are securely stored.

---

## 🧾 **Future Enhancements**

* Integration with real hospital APIs.
* Multi-language support (English, Hindi, Marathi).
* Doctor report generator (PDF format).
* Extended disease detection (e.g., Tuberculosis, COVID-19).

---

## 💡 **Contributors**

**Developed by:** Siddhesh Gharat 🧑‍💻
