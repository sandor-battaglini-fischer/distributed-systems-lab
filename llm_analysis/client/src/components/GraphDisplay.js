import React, { useState, useEffect, forwardRef } from 'react';
import { Box, Paper, CircularProgress, Typography } from '@mui/material';

const plotConfigs = {
  figure1: {
    title: 'Monthly Overview',
    description: 'Monthly distribution of incidents and outages'
  },
  figure2: {
    title: 'Failure Recovery Analysis',
    description: 'Status progression patterns across services'
  },
  figure3: {
    title: 'Status Combinations',
    description: 'Common status transition patterns'
  }
};

const GraphDisplay = forwardRef(({ loading }, ref) => {
  const [plots, setPlots] = useState({});
  const [imageErrors, setImageErrors] = useState({});

  useEffect(() => {
    setImageErrors({});
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  // Create placeholder boxes for all possible figures
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