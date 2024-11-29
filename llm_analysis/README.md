# LLM Analysis Dashboard

This project is a web application built using React for the frontend and Flask for the backend. The frontend is styled with Material-UI and supports both light and dark themes. The backend is a simple Flask server running on Gunicorn.

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.x
- OpenAI API key (for AI plot analysis feature)

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

   - On Windows:

     ```bash
     .\venv\Scripts\activate
     ```

4. **Install backend dependencies:**

   With the virtual environment activated, install the dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables:**

   Create a `.env` file in the `server/scripts` directory with your API keys:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   Replace `your_openai_api_key_here` with your actual OpenAI API key.

### Running the Application

1. **Start the backend server:**

   #### Development Mode

   For development with auto-reload:

   In the `server` directory, ensure the virtual environment is activated, then run:

   ```bash
   python app.py
   ```

   This will start the Flask server on `http://localhost:5000`.

   #### Production Mode

   For production deployment using Gunicorn:

   ```bash
   cd server
   chmod +x start.sh stop.sh # Make scripts executable (first time only)
   ./start.sh # Start the server
   ./stop.sh # Stop the server when needed
   ```

   The server will be available at `http://localhost:5000`.

2. **Start the frontend development server:**

   In the `client` directory, run:

   ```bash
   npm start
   ```

   This will start the React development server on `http://localhost:3000`.

## Using the AI Plot Analysis Feature

The application includes an AI-powered plot analysis feature that can analyze visualizations and provide insights. To use this feature:

1. **Setup Requirements:**
   - Ensure you have a valid OpenAI API key
   - Add the API key to your `.env` file as described above
   - Make sure you're running the application in production mode using the start.sh script

2. **Using the Feature:**
   - Generate plots by selecting services and date range
   - Once plots are displayed, find the "AI Plot Analysis" section below the plots
   - Choose either:
     - A single plot to analyze specific visualizations
     - "Analyze All Plots" for a comprehensive summary
   - Click "Analyze Plot" to generate AI insights

3. **Analysis Types:**
   - **Single Plot Analysis**: Provides detailed insights about specific visualizations
   - **All Plots Analysis**: Generates a comprehensive summary of all plots, highlighting key patterns and insights

4. **Troubleshooting:**
   - If you see "Please use production server" message, ensure you're running the server using start.sh
   - Verify your API key is correctly set in the .env file
   - Check the server logs for any API-related errors

### Learn More

- [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React documentation](https://reactjs.org/)
- [Flask documentation](https://flask.palletsprojects.com/)
- [OpenAI API documentation](https://platform.openai.com/docs/api-reference)
