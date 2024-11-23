import React, { useState, useEffect, forwardRef } from 'react';
import { Box, Paper, CircularProgress, Typography, Chip } from '@mui/material';

const plotConfigs = {
  figure1: {
    title: 'Monthly Overview',
    description: 'Monthly distribution of incidents and outages'
  },
  figure2: {
    title: 'Failure Recovery Analysis',
    description: 'Presence of different status combinations, by service, in percentage'
  },
  figure3: {
    title: 'Status Combinations',
    description: 'Common status transition patterns'
  }
};

const formatDate = (dateStr) => {
  try {
    // Ensure dateStr is exactly 8 characters (YYYYMMDD)
    if (dateStr?.length !== 8) {
      console.error('Invalid date string:', dateStr);
      return 'Invalid Date';
    }

    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);
    
    // Validate components
    if (isNaN(year) || isNaN(month) || isNaN(day)) {
      console.error('Invalid date components:', { year, month, day });
      return 'Invalid Date';
    }

    const date = new Date(year, month - 1, day);
    
    // Validate result
    if (isNaN(date.getTime())) {
      console.error('Invalid date result:', date);
      return 'Invalid Date';
    }

    return date.toLocaleDateString('en-US', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid Date';
  }
};

const formatServiceName = (serviceName) => {
  // Convert service names to display format
  const [provider, service] = serviceName.split('_');
  switch(provider) {
    case 'OpenAI':
      return `OpenAI ${service}`;
    case 'Anthropic':
      return `Anthropic ${service}`;
    case 'Google':
      return `Google ${service}`;
    case 'CharacterAI':
      return 'Character.AI';
    case 'StabilityAI':
      return 'Stability AI';
    default:
      return serviceName;
  }
};

const GraphDisplay = forwardRef(({ loading }, ref) => {
  const [plots, setPlots] = useState({});
  const [imageErrors, setImageErrors] = useState({});
  const [plotDetails, setPlotDetails] = useState({});

  useEffect(() => {
    setImageErrors({});
    extractPlotDetails();
  }, [plots]);

  React.useImperativeHandle(ref, () => ({
    refreshPlots: (newPlots) => {
      setPlots(newPlots);
      setImageErrors({});
    }
  }));

  const handleImageError = (figureId) => {
    console.error(`Failed to load image: ${plots[figureId]}`);
    setImageErrors(prev => ({
      ...prev,
      [figureId]: true
    }));
  };

  const handleImageLoad = (figureId) => {
    setImageErrors(prev => ({
      ...prev,
      [figureId]: false
    }));
  };

  const extractPlotDetails = () => {
    const details = {};
    Object.entries(plots).forEach(([figureId, plotPath]) => {
      try {
        const filename = plotPath.split('/').pop();
        console.log('Processing filename:', filename);
        
        const [mainPart, servicePart, timestamp] = filename.split('__');
        console.log('Main part:', mainPart);
        
        // Format is: plotType_YYYYMMDD_YYYYMMDD
        const dateMatch = mainPart.match(/.*?_(\d{8})_(\d{8})/);
        if (!dateMatch) {
          console.error('Could not extract dates from:', mainPart);
          return;
        }
        
        const [, startDate, endDate] = dateMatch;
        console.log('Extracted dates:', { startDate, endDate });

        // Validate dates before formatting
        if (startDate?.length !== 8 || endDate?.length !== 8) {
          console.error('Invalid date format:', { startDate, endDate });
          return;
        }

        details[figureId] = {
          startDate: formatDate(startDate),
          endDate: formatDate(endDate),
          services: servicePart.split('-').map(formatServiceName)
        };

        console.log('Extracted details for', figureId, ':', details[figureId]);

      } catch (error) {
        console.error('Error parsing filename:', error);
      }
    });
    setPlotDetails(details);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  const allFigures = Object.keys(plotConfigs);

  return (
    <Box sx={{ 
      display: 'grid', 
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: 3,
      p: 3
    }}>
      {allFigures.map((figureId) => (
        <Paper
          key={figureId}
          elevation={3}
          sx={{
            p: 2,
            backgroundColor: 'background.paper',
            borderRadius: 2,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
            minHeight: '300px',
            transition: 'all 0.3s ease-in-out',
            '&:hover': {
              transform: plots[figureId] ? 'translateY(-4px)' : 'none',
              boxShadow: plots[figureId] ? 8 : 3
            }
          }}
        >
          <Box>
            <Typography variant="h6" fontWeight="bold" color="primary">
              {plotConfigs[figureId].title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {plotConfigs[figureId].description}
            </Typography>
          </Box>

          {figureId === 'figure2' && plotDetails[figureId] && (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column',
              gap: 1, 
              mb: 2,
              p: 1.5,
              backgroundColor: 'background.default',
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'divider',
            }}>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                  Services:
                </Typography>
                {plotDetails[figureId].services.map(service => (
                  <Chip
                    key={service}
                    label={service}
                    size="small"
                    sx={{
                      backgroundColor: theme => `${theme.palette.primary.main}22`,
                      color: 'primary.main',
                      fontWeight: 500,
                      borderRadius: '6px',
                      '& .MuiChip-label': {
                        px: 1,
                      },
                    }}
                  />
                ))}
              </Box>
              <Typography 
                variant="body2" 
                color="text.secondary" 
                sx={{ 
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  mt: 0.5
                }}
              >
                From 
                <Box component="span" sx={{ color: 'text.primary', fontWeight: 500 }}>
                  {plotDetails[figureId].startDate}
                </Box>
                to
                <Box component="span" sx={{ color: 'text.primary', fontWeight: 500 }}>
                  {plotDetails[figureId].endDate}
                </Box>
              </Typography>
            </Box>
          )}

          {plots[figureId] ? (
            imageErrors[figureId] ? (
              <Box 
                display="flex" 
                justifyContent="center" 
                alignItems="center" 
                flexGrow={1}
              >
                <Typography color="error">
                  Failed to load image. Please try refreshing the analysis.
                </Typography>
              </Box>
            ) : (
              <Box 
                sx={{ 
                  flexGrow: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <img
                  src={plots[figureId]}
                  alt={`${plotConfigs[figureId].title}`}
                  onError={() => handleImageError(figureId)}
                  onLoad={() => handleImageLoad(figureId)}
                  style={{
                    width: '100%',
                    height: 'auto',
                    display: 'block',
                    borderRadius: '8px'
                  }}
                />
              </Box>
            )
          ) : (
            <Box 
              display="flex" 
              justifyContent="center" 
              alignItems="center"
              flexGrow={1}
              sx={{ 
                bgcolor: 'background.default',
                borderRadius: 1,
                p: 2,
                opacity: 0.7
              }}
            >
              <Typography color="text.secondary" align="center">
                Select services and run analysis to generate visualization
              </Typography>
            </Box>
          )}
        </Paper>
      ))}
    </Box>
  );
});

GraphDisplay.displayName = 'GraphDisplay';

export default GraphDisplay; 