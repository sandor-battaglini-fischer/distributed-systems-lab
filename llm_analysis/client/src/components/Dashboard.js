import React, { useState, useEffect, useRef } from 'react';
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
  useMediaQuery,
  alpha
} from '@mui/material';
import {
  AnalyticsOutlined as AnalyticsIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
  DateRange as DateRangeIcon,
  Apps as AppsIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import GraphDisplay from './GraphDisplay';

function Dashboard() {
  const [selectedServices, setSelectedServices] = useState([]);
  const [startDate, setStartDate] = useState('2023-08-01');
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [controlsOpen, setControlsOpen] = useState(true);
  const [scrolled, setScrolled] = useState(false);
  const [loading, setLoading] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const graphDisplayRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 50;
      setScrolled(isScrolled);
      
      if (isScrolled && controlsOpen) {
        setControlsOpen(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [controlsOpen]);

  const providers = {
    'OpenAI': ['API', 'ChatGPT', 'DALL·E', 'Playground', 'Labs'],
    'Anthropic': ['API', 'Claude', 'Console'],
    'Character.AI': ['Character.AI'],
    'Stability AI': ['Stable Diffusion'],
    'Google': ['Gemini', 'Gemini API', 'Bard']
  };

  const handleServiceToggle = (provider, service) => {
    let serviceId;
    switch(true) {
      case provider === 'Anthropic' && service === 'API':
        serviceId = 'Anthropic:API';
        break;
      case provider === 'Anthropic' && service === 'Claude':
        serviceId = 'Anthropic:Claude';
        break;
      case provider === 'Anthropic' && service === 'Console':
        serviceId = 'Anthropic:Console';
        break;
      case provider === 'Character.AI' && service === 'Character.AI':
        serviceId = 'Character.AI:Character.AI';
        break;
      case provider === 'Stability AI' && service === 'Stable Diffusion':
        serviceId = 'Stability AI:Stable Diffusion';
        break;
      case provider === 'Google':
        serviceId = `Google:${service}`;
        break;
      default:
        serviceId = `OpenAI:${service}`;
    }

    setSelectedServices(prev => 
      prev.includes(serviceId)
        ? prev.filter(s => s !== serviceId)
        : [...prev, serviceId]
    );
  };

  const isServiceSelected = (provider, service) => {
    let serviceId;
    switch(true) {
      case provider === 'Anthropic' && service === 'API':
        serviceId = 'Anthropic:API';
        break;
      case provider === 'Anthropic' && service === 'Claude':
        serviceId = 'Anthropic:Claude';
        break;
      case provider === 'Anthropic' && service === 'Console':
        serviceId = 'Anthropic:Console';
        break;
      case provider === 'Character.AI' && service === 'Character.AI':
        serviceId = 'Character.AI:Character.AI';
        break;
      case provider === 'Stability AI' && service === 'Stable Diffusion':
        serviceId = 'Stability AI:Stable Diffusion';
        break;
      case provider === 'Google':
        serviceId = `Google:${service}`;
        break;
      default:
        serviceId = `OpenAI:${service}`;
    }
    return selectedServices.includes(serviceId);
  };

  const handleAnalyze = async () => {
    try {
      setLoading(true);
      const payload = {
        startDate,
        endDate,
        selectedServices,
      };
      console.log('Sending request with payload:', payload);

      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      let result;
      try {
        result = await response.json();
      } catch (parseError) {
        console.error('Failed to parse response:', parseError);
        throw new Error('Server response was not valid JSON');
      }

      if (!response.ok) {
        throw new Error(result.error || `HTTP error! status: ${response.status}`);
      }
      
      if (result.success) {
        setControlsOpen(false);
        if (result.plots) {
          console.log('Plots received:', result.plots);
          if (graphDisplayRef.current?.refreshPlots) {
            graphDisplayRef.current.refreshPlots(result.plots);
          }
        }
      } else {
        throw new Error(result.error || 'Analysis failed');
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      alert(`Analysis failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const isDateRangeValid = () => {
    return startDate && endDate && new Date(startDate) <= new Date(endDate);
  };

  const isFormValid = () => {
    return selectedServices.length > 0 && isDateRangeValid();
  };

  const handleToolbarClick = () => {
    if (scrolled) {
      setControlsOpen(!controlsOpen);
    }
  };

  return (
    <Box sx={{ 
      height: '100%', 
      mt: -3, 
      pt: 3,
      position: 'relative',
      '&::before': {
        content: '""',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: theme => `${theme.palette.background.gradient}`,
        zIndex: -1,
      }
    }}>
      <Slide appear={false} direction="down" in={!scrolled}>
        <AppBar 
          position="sticky" 
          elevation={scrolled ? 2 : 0}
          sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            backgroundColor: theme => alpha(theme.palette.background.paper, 0.7),
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease-in-out',
          }}
        >
          <Toolbar 
            onClick={handleToolbarClick}
            sx={{ 
              cursor: scrolled ? 'pointer' : 'default',
              '&:hover': scrolled ? {
                bgcolor: theme => alpha(theme.palette.action.hover, 0.1),
              } : {},
              display: 'flex',
              justifyContent: 'space-between',
              gap: 2,
              minHeight: scrolled ? 48 : 64,
              transition: 'all 0.3s ease-in-out',
            }}
          >
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              flex: 1
            }}>
              <Typography variant="h6" sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1,
                color: 'text.primary',
                fontSize: scrolled ? '1rem' : '1.25rem',
                transition: 'all 0.3s ease-in-out',
              }}>
                Analysis Controls
                {scrolled && (
                  <motion.div
                    animate={{ 
                      rotate: controlsOpen ? 180 : 0,
                    }}
                    transition={{ duration: 0.3 }}
                  >
                    <KeyboardArrowDownIcon />
                  </motion.div>
                )}
              </Typography>
            </Box>
          </Toolbar>
          
          <Collapse in={controlsOpen || !scrolled}>
            <Box sx={{ p: 2 }}>
              <Box sx={{ 
                display: 'flex', 
                gap: 2, 
                mb: 2,
                flexWrap: 'wrap',
                alignItems: 'flex-start'
              }}>
                <motion.div
                  whileHover={{ scale: isFormValid() ? 1.02 : 1 }}
                  whileTap={{ scale: isFormValid() ? 0.98 : 1 }}
                >
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AnalyticsIcon />}
                    onClick={handleAnalyze}
                    disabled={!isFormValid()}
                    sx={{ 
                      minWidth: 150,
                      height: 'fit-content',
                      alignSelf: 'flex-start',
                      background: theme => isFormValid()
                        ? `linear-gradient(135deg, 
                            ${theme.palette.primary.main} 0%, 
                            ${theme.palette.secondary.main} 100%)`
                        : theme.palette.action.disabledBackground,
                      color: theme => isFormValid()
                        ? '#ffffff'
                        : theme.palette.text.disabled,
                      backdropFilter: 'blur(10px)',
                      border: '1px solid',
                      borderColor: theme => isFormValid()
                        ? 'rgba(255,255,255,0.2)'
                        : 'divider',
                      transition: 'all 0.3s ease-in-out',
                      '&:hover': isFormValid() ? {
                        background: theme => `linear-gradient(135deg, 
                          ${theme.palette.primary.dark} 0%, 
                          ${theme.palette.secondary.dark} 100%)`,
                        transform: 'translateY(-2px)',
                        boxShadow: theme => `0 8px 24px ${alpha(theme.palette.primary.main, 0.25)}`,
                      } : {},
                      '&:disabled': {
                        background: theme => theme.palette.action.disabledBackground,
                        color: theme => theme.palette.text.disabled,
                        border: '1px solid',
                        borderColor: 'divider',
                      },
                      '&:active': isFormValid() ? {
                        transform: 'translateY(1px)',
                      } : {},
                    }}
                  >
                    Analyze
                  </Button>
                </motion.div>

                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 2, 
                    border: 1, 
                    borderColor: 'divider',
                    minWidth: 280,
                    backdropFilter: 'blur(10px)',
                    backgroundColor: theme => alpha(theme.palette.background.paper, 0.7),
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <DateRangeIcon color="primary" sx={{ mr: 1 }} />
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
                    flexGrow: 1,
                    backdropFilter: 'blur(10px)',
                    backgroundColor: theme => alpha(theme.palette.background.paper, 0.7),
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AppsIcon color="primary" sx={{ mr: 1 }} />
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
                            mb: 1,
                            fontWeight: 500
                          }}
                        >
                          {provider}
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {services.map((service) => (
                            <motion.div
                              key={`${provider}:${service}`}
                              whileHover={{ y: -2 }}
                              whileTap={{ scale: 0.95 }}
                            >
                              <Chip
                                label={service}
                                onClick={() => handleServiceToggle(provider, service)}
                                color={isServiceSelected(provider, service) ? "primary" : "default"}
                                variant={isServiceSelected(provider, service) ? "filled" : "outlined"}
                                size="small"
                                sx={{
                                  backdropFilter: 'blur(8px)',
                                  backgroundColor: theme => isServiceSelected(provider, service) 
                                    ? alpha(theme.palette.primary.main, 0.9)
                                    : alpha(theme.palette.background.paper, 0.5),
                                  border: '1px solid',
                                  borderColor: 'divider',
                                }}
                              />
                            </motion.div>
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
        <GraphDisplay ref={graphDisplayRef} loading={loading} />
      </Box>
    </Box>
  );
}

export default Dashboard;