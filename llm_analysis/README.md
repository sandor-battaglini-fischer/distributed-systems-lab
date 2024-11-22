# LLM Analysis Dashboard

This project is a web application built using React for the frontend and Flask for the backend. The frontend is styled with Material-UI and supports both light and dark themes. The backend is a simple Flask server with CORS enabled.

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.x

### Installation

1. **Install Node.js and npm:**

   If you haven't installed Node.js and npm, download and install them from the [official Node.js website](https://nodejs.org/). This will also install npm, which is the package manager for Node.js.

2. **Install frontend dependencies:**

   Navigate to the `client` directory and install the dependencies:

   ```bash
   cd client
   npm install
   ```

3. **Set up Python virtual environment:**

   Navigate to the `server` directory and create a virtual environment:

   ```bash
   cd server
   python -m venv venv
   ```

   Activate the virtual environment:

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install backend dependencies:**

   With the virtual environment activated, install the dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the backend server:**

   In the `server` directory, ensure the virtual environment is activated, then run:

   ```bash
   python app.py
   ```

   This will start the Flask server on `http://localhost:5000`.

2. **Start the frontend development server:**

   In the `client` directory, run:

   ```bash
   npm start
   ```

   This will start the React development server on `http://localhost:3000`.

### Learn More

- [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React documentation](https://reactjs.org/)
- [Flask documentation](https://flask.palletsprojects.com/)
