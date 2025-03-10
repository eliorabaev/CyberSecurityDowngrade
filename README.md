# CyberSecurity Project

This project is a **full-stack application** built with **FastAPI** (backend) and **React** (frontend). It includes a user authentication system with a login page and API communication.

---

## 📁 Project Structure

```
CyberSecurity/
├── backend/       # FastAPI backend
│   ├── main.py    # Main FastAPI app
│   ├── requirements.txt  # Backend dependencies
│   ├── ...
│
├── frontend/      # React frontend
│   ├── src/
│   │   ├── App.js  # Login Page UI
│   │   ├── index.js # React entry point
│   │   ├── App.css # Styling
│   ├── public/
│   ├── package.json  # Frontend dependencies
│   ├── ...
│
├── README.md  # Project documentation
```

---

## 🚀 Setup & Run Instructions

### 🔧 Backend (FastAPI)
1. **Navigate to the backend folder:**
   ```sh
   cd backend
   ```
2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Run FastAPI server:**
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
5. **Test API endpoints:** Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

---

### 🎨 Frontend (React)
1. **Navigate to the frontend folder:**
   ```sh
   cd frontend
   ```
2. **Install dependencies:**
   ```sh
   npm install
   ```
3. **Run the frontend server:**
   ```sh
   npm start
   ```
4. **Open the app:** Visit [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🔗 API Integration
The frontend connects to the backend via REST API. The login request is sent to:
```sh
POST http://localhost:8000/login
```
With the following JSON payload:
```json
{
  "username": "admin",
  "password": "admin"
}
```
If successful, the backend responds with:
```json
{
  "message": "Login successful"
}
```
Otherwise, it returns an error message.

---

## 📝 Features Implemented
✅ Simple **React login page**
✅ FastAPI **backend with authentication**
✅ CORS enabled for **frontend-backend communication**
✅ **Live reload** for development

---

## 📌 Future Improvements
- [ ] Implement JWT authentication
- [ ] Add user registration & password reset
- [ ] Enhance UI with better styling
- [ ] Dockerize the entire stack (optional)

---

## 📜 License
MIT License © 2025
```
