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

### Integrating Python Analysis and Plot Generation

#### Adding Python Scripts

1. **Location for Scripts:**

   Place your Python analysis and plot generation scripts in the `server/scripts` directory. This directory is intended for any additional Python scripts that perform data analysis and generate plot images.

2. **Integrating with Flask:**

   - **Create a new endpoint** in `server/app.py` to handle requests for analysis or plot generation. For example:

     ```python
     from flask import request, send_file
     from scripts.my_analysis_script import generate_plot

     @app.route('/api/generate-plot', methods=['POST'])
     def generate_plot_endpoint():
         data = request.json
         plot_path = generate_plot(data)
         return send_file(plot_path, mimetype='image/png')
     ```

   - **Import your script** at the top of `app.py` and call the necessary functions within the endpoint.

#### Frontend Integration

1. **Making API Calls:**

   Use `fetch` or a library like `axios` to make POST requests to your new endpoint from the React frontend. For example:

2. **Displaying Images:**

   Use React components to display the image returned from the backend. For example:

   ```javascript
   // client/src/components/PlotComponent.js

   import React, { useState } from 'react';

   const PlotComponent = () => {
     const [imageSrc, setImageSrc] = useState(null);

     return (
       <div>
         <button onClick={() => fetchPlot({ x: [1, 2, 3], y: [4, 5, 6] })}>
           Generate Plot
         </button>
         {imageSrc && <img src={imageSrc} alt="Generated Plot" />}
       </div>
     );
   };

   export default PlotComponent;
   ```

### Deployment

- **Frontend**: Build the frontend for production using `npm run build`. This will create a `build` folder with static files.
- **Backend**: Deploy the Flask app using a WSGI server like Gunicorn or a platform like Heroku.

### Learn More

- [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React documentation](https://reactjs.org/)
- [Flask documentation](https://flask.palletsprojects.com/)
