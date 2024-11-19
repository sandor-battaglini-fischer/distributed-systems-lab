# LLM Analysis Dashboard

This project is a web application built using React for the frontend and Flask for the backend. The frontend is styled with Material-UI and supports both light and dark themes. The backend is a simple Flask server with CORS enabled.

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.x

### Installation

1. **Install frontend dependencies:**

   Navigate to the `client` directory and install the dependencies:

   ```bash
   cd client
   npm install
   ```

2. **Install backend dependencies:**

   Navigate to the `server` directory and install the dependencies using `pip`:

   ```bash
   cd server
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the backend server:**

   In the `server` directory, run:

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

<!-- ### Deployment

- **Frontend**: Build the frontend for production using `npm run build`. This will create a `build` folder with static files.
- **Backend**: Deploy the Flask app using a WSGI server like Gunicorn or a platform like Heroku. -->

### Learn More

- [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React documentation](https://reactjs.org/)
- [Flask documentation](https://flask.palletsprojects.com/)
