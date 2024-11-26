import React, { useState, useMemo } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { lightTheme, darkTheme } from './theme';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import About from './pages/About';
import './App.css';
import { AnalysisProvider } from './context/AnalysisContext';

function App() {
  const [mode, setMode] = useState('light');

  const theme = useMemo(() => 
    mode === 'light' ? lightTheme : darkTheme,
    [mode]
  );

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AnalysisProvider>
        <Router>
          <Layout toggleTheme={toggleTheme}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </Layout>
        </Router>
      </AnalysisProvider>
    </ThemeProvider>
  );
}

export default App;