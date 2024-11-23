import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Paper,
  Chip,
  Box,
  TextField,
  Button,
  Slide,
  AppBar,
  Toolbar,
  IconButton,
  Collapse,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  AnalyticsOutlined as AnalyticsIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
  DateRange as DateRangeIcon,
  Apps as AppsIcon
} from '@mui/icons-material';
import GraphDisplay from './GraphDisplay';

function Dashboard() {
  const [selectedServices, setSelectedServices] = useState([]);
  const [startDate, setStartDate] = useState('2023-08-01');
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [controlsOpen, setControlsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
      if (window.scrollY > 100) {
        setControlsOpen(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const providers = {
    'OpenAI': ['API', 'ChatGPT', 'DALL·E', 'Playground'],
    'Anthropic': ['API', 'Claude', 'Console'],
    'Character.AI': ['Character.AI'],
    'Stability AI': ['Stable Diffusion'],
    'Google': ['Gemini', 'Gemini API', 'Bard']
  };

  const handleServiceToggle = (provider, service) => {
    const serviceId = `${provider}:${service}`;
    setSelectedServices(prev => 
      prev.includes(serviceId)
        ? prev.filter(s => s !== serviceId)
        : [...prev, serviceId]
    );
  };

  const isServiceSelected = (provider, service) => {
    return selectedServices.includes(`${provider}:${service}`);
  };

  const handleAnalyze = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          startDate,
          endDate,
          selectedServices,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Analysis result:', result);
      setControlsOpen(false);
      
      if (result.plots) {
        console.log('Plots received:', result.plots);
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Failed to perform analysis. Please try again later.');
    }
  };

  return (
    <Box sx={{ height: '100%', mt: -3, pt: 3 }}>
      <Slide appear={false} direction="down" in={!scrolled}>
        <AppBar 
          position="sticky" 
          color="inherit" 
          elevation={0}
          sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            bgcolor: 'background.default'
          }}
        >
          <Toolbar 
            onClick={() => !isMobile && setControlsOpen(!controlsOpen)}
            sx={{ 
              cursor: isMobile ? 'default' : 'pointer',
              '&:hover': !isMobile ? {
                bgcolor: 'action.hover'
              } : {},
              display: 'flex',
              justifyContent: 'space-between',
              gap: 2
            }}
          >
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              flex: 1
            }}>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                Analysis Controls
                {!isMobile && (
                  <KeyboardArrowDownIcon 
                    sx={{ 
                      transform: controlsOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 0.3s ease'
                    }} 
                  />
                )}
              </Typography>
            </Box>

            {isMobile && (
              <IconButton onClick={() => setControlsOpen(!controlsOpen)}>
                <KeyboardArrowDownIcon 
                  sx={{ 
                    transform: controlsOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.3s ease'
                  }} 
                />
              </IconButton>
            )}
          </Toolbar>
          
          <Collapse in={controlsOpen}>
            <Box sx={{ p: 2 }}>
              <Box sx={{ 
                display: 'flex', 
                gap: 2, 
                mb: 2,
                flexWrap: 'wrap',
                alignItems: 'flex-start'
              }}>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AnalyticsIcon />}
                  onClick={handleAnalyze}
                  disabled={selectedServices.length === 0}
                  sx={{ 
                    minWidth: 150,
                    height: 'fit-content',
                    alignSelf: 'flex-start',
                    boxShadow: 2,
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: 3
                    }
                  }}
                >
                  Analyze
                </Button>

                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 2, 
                    border: 1, 
                    borderColor: 'divider',
                    minWidth: 280
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <DateRangeIcon color="action" sx={{ mr: 1 }} />
                    <Typography variant="subtitle2">Analysis Period</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <TextField
                      label="Start Date"
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      size="small"
                      fullWidth
                    />
                    <TextField
                      label="End Date"
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      size="small"
                      fullWidth
                    />
                  </Box>
                </Paper>

                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 2, 
                    border: 1, 
                    borderColor: 'divider',
                    flexGrow: 1
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AppsIcon color="action" sx={{ mr: 1 }} />
                    <Typography variant="subtitle2">Select Services</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {Object.entries(providers).map(([provider, services]) => (
                      <Box key={provider}>
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            color: 'text.secondary',
                            display: 'block',
                            mb: 1
                          }}
                        >
                          {provider}
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {services.map((service) => (
                            <Chip
                              key={`${provider}:${service}`}
                              label={service}
                              onClick={() => handleServiceToggle(provider, service)}
                              color={isServiceSelected(provider, service) ? "primary" : "default"}
                              variant={isServiceSelected(provider, service) ? "filled" : "outlined"}
                              size="small"
                              sx={{
                                transition: 'all 0.2s ease',
                                '&:hover': {
                                  transform: 'translateY(-2px)',
                                  boxShadow: 1
                                }
                              }}
                            />
                          ))}
                        </Box>
                      </Box>
                    ))}
                  </Box>
                </Paper>
              </Box>
            </Box>
          </Collapse>
        </AppBar>
      </Slide>

      <Box sx={{ mt: 2 }}>
        <GraphDisplay />
      </Box>
    </Box>
  );
}

export default Dashboard;