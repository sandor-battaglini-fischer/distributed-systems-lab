import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Box, Paper, Typography, IconButton, Link } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import EmailIcon from '@mui/icons-material/Email';
import Dashboard from './components/Dashboard';
import GraphDisplay from './components/GraphDisplay';
import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const prefersDark = window.matchMedia('(prefers-reduced-motion: dark)').matches;
    setDarkMode(prefersDark);
  }, []);

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: darkMode ? '#4dabf7' : '#007bff',
      },
      secondary: {
        main: darkMode ? '#adb5bd' : '#6c757d',
      },
      background: {
        default: darkMode ? '#1a1a1a' : '#ffffff',
        paper: darkMode ? '#2d2d2d' : '#f8f9fa',
      },
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontSize: '2.5rem',
        fontWeight: 500,
      },
      h2: {
        fontSize: '2rem',
        fontWeight: 500,
      },
      body1: {
        fontSize: '1rem',
        lineHeight: 1.5,
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            textTransform: 'none',
            padding: '8px 16px',
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          },
        },
      },
    },
  });

  const contributors = [
    { name: 'Bálint László Szarvas', email: 'b.l.szarvas@student.vu.nl' },
    { name: 'Nishanthi Srinivasan', email: 'n.srinivasan@student.vu.nl' },
    { name: 'Sándor Battaglini-Fischer', email: 's.battaglini-fischer@student.vu.nl' }
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className={`app ${darkMode ? 'dark' : 'light'}`}>
        <div className="theme-toggle">
          <button onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
        <Box className="dashboard-container">
          {/* Left Sidebar */}
          <Paper className="sidebar">
            <div className="sidebar-content">
              <Dashboard />
            </div>
            <div className="contributors">
              <Typography variant="subtitle2" className="contributors-title">
                Contributors
              </Typography>
              <ul className="contributors-list">
                {contributors.map((contributor, index) => (
                  <li key={index}>
                    <span>{contributor.name}</span>
                    <IconButton
                      size="small"
                      component={Link}
                      href={`mailto:${contributor.email}`}
                      className="contributor-email"
                    >
                      <EmailIcon fontSize="small" />
                    </IconButton>
                  </li>
                ))}
              </ul>
            </div>
          </Paper>

          {/* Right Content Area */}
          <Paper className="main-content">
            <GraphDisplay />
          </Paper>
        </Box>
      </div>
    </ThemeProvider>
  );
}

export default App;