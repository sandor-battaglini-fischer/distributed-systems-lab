import React, { useState, useEffect, forwardRef } from 'react';
import { Box, Paper, CircularProgress, Typography, Chip, useTheme, useMediaQuery, Button, IconButton, Tooltip, LinearProgress, Skeleton, Fade } from '@mui/material';
import { useAnalysis } from '../context/AnalysisContext';
import { 
  SaveAlt as SaveIcon,
  Download as DownloadIcon 
} from '@mui/icons-material';
import JSZip from 'jszip';

const plotConfigs = {
  figure1: {
    title: 'Days of Week Distribution',
    description: 'Distribution of incidents across days of the week by provider'
  },
  figure2: {
    title: 'MTTR Analysis',
    description: 'Mean Time To Recovery distribution and percentages by service'
  },
  figure3: {
    title: 'MTTR by Provider',
    description: 'Mean Time To Recovery patterns across different providers'
  },
  figure4: {
    title: 'MTTR Distribution',
    description: 'Detailed MTTR distribution with service-level boxplots'
  },
  figure5: {
    title: 'MTBF Analysis',
    description: 'Mean Time Between Failures distribution and percentages by service'
  },
  figure6: {
    title: 'MTBF by Provider',
    description: 'Mean Time Between Failures patterns across different providers'
  },
  figure7: {
    title: 'MTBF Distribution',
    description: 'Detailed MTBF distribution with service-level boxplots'
  },
  figure8: {
    title: 'Resolution Activities',
    description: 'Duration and distribution of incident resolution stages'
  },
  figure9: {
    title: 'Status Combinations',
    description: 'Analysis of incident status transition patterns'
  },
  figure10: {
    title: 'Service Availability',
    description: 'Daily service availability and SLA compliance'
  },
  figure11: {
    title: 'Temporal Patterns',
    description: 'Monthly trends and hourly distribution of incidents'
  },
  figure12: {
    title: 'Service Co-occurrence',
    description: 'Analysis of simultaneous incidents across services'
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

const PlotDetails = ({ details }) => {
  if (!details) return null;
  
  return (
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
      <Box sx={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: 0.5, 
        alignItems: 'center' 
      }}>
        <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
          Services:
        </Typography>
        {details.services.map(service => (
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
      <Typography variant="body2" color="text.secondary">
        From {details.startDate} to {details.endDate}
      </Typography>
    </Box>
  );
};

const GraphDisplay = forwardRef((props, ref) => {
  const { plots, setPlots, loading } = useAnalysis();
  const [imageErrors, setImageErrors] = useState({});
  const [plotDetails, setPlotDetails] = useState({});
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [savingAll, setSavingAll] = useState(false);
  const [error, setError] = useState(null);

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

  const handleSavePlot = async (figureId) => {
    try {
      if (!plots[figureId]) return;

      const response = await fetch(plots[figureId]);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Create a formatted filename with date and service info
      const plotDetails = plotConfigs[figureId];
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `${plotDetails.title.toLowerCase().replace(/\s+/g, '_')}_${timestamp}.png`;
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(`Error saving plot ${figureId}:`, error);
      setError(`Failed to save ${plotConfigs[figureId].title}`);
    }
  };

  const handleSaveAll = async () => {
    try {
      setSavingAll(true);
      const plotIds = Object.keys(plots);
      const zip = new JSZip();
      const timestamp = new Date().toISOString().split('T')[0];
      
      // Create plots folder in the zip
      const plotsFolder = zip.folder("plots");
      
      // Add each plot to the zip
      for (let i = 0; i < plotIds.length; i++) {
        const figureId = plotIds[i];
        try {
          // Fetch the image
          const response = await fetch(plots[figureId]);
          const blob = await response.blob();
          
          // Create filename
          const plotDetails = plotConfigs[figureId];
          const filename = `${plotDetails.title.toLowerCase().replace(/\s+/g, '_')}_${timestamp}.png`;
          
          // Add to zip
          plotsFolder.file(filename, blob);
          
        } catch (error) {
          console.error(`Error adding ${figureId} to zip:`, error);
          setError(`Failed to add ${plotConfigs[figureId].title} to zip`);
        }
      }
      
      // Generate the zip file
      const content = await zip.generateAsync({ type: "blob" });
      
      // Create download link
      const url = window.URL.createObjectURL(content);
      const link = document.createElement('a');
      link.href = url;
      link.download = `llm_analysis_plots_${timestamp}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Error saving all plots:', error);
      setError('Failed to create ZIP file');
    } finally {
      setSavingAll(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Paper 
          elevation={3}
          sx={{ 
            p: 4, 
            textAlign: 'center',
            backgroundColor: 'background.paper',
            borderRadius: 2
          }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
            <CircularProgress size={60} />
            <Box sx={{ width: '100%', maxWidth: 400 }}>
              <Typography variant="h6" gutterBottom>
                Analyzing Data
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Generating visualizations and processing insights...
              </Typography>
              <LinearProgress 
                sx={{ 
                  height: 8, 
                  borderRadius: 4,
                  mb: 2
                }} 
              />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {Object.keys(plotConfigs).map((figureId) => (
                  <Box 
                    key={figureId}
                    sx={{ 
                      display: 'flex', 
                      alignItems: 'center',
                      gap: 2
                    }}
                  >
                    <Skeleton 
                      variant="circular" 
                      width={24} 
                      height={24} 
                    />
                    <Typography variant="body2" color="text.secondary">
                      {plotConfigs[figureId].title}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          </Box>
        </Paper>
      </Box>
    );
  }

  // Only show plots section if there are plots
  if (Object.keys(plots).length === 0) {
    return null;  // Return nothing if no plots are generated
  }

  const allFigures = Object.keys(plotConfigs);

  // Define grid layout configurations
  const getGridConfig = (figureId) => {
    const configs = {
      figure1: { // Days of Week
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 12' },
        minHeight: { xs: '300px', sm: '400px', md: '500px' }
      },
      figure2: { // MTTR Analysis
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 6' },
        minHeight: { xs: '400px', sm: '500px' }
      },
      figure3: { // MTTR by Provider
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 6' },
        minHeight: { xs: '400px', sm: '500px' }
      },
      figure4: { // MTTR Distribution
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 12' },
        minHeight: { xs: '300px', sm: '400px' }
      },
      figure5: { // MTBF Analysis
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 6' },
        minHeight: { xs: '400px', sm: '500px' }
      },
      figure6: { // MTBF by Provider
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 6' },
        minHeight: { xs: '400px', sm: '500px' }
      },
      figure7: { // MTBF Distribution
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 12' },
        minHeight: { xs: '300px', sm: '400px' }
      },
      figure8: { // Resolution Activities
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 12' },
        minHeight: { xs: '300px', sm: '400px' }
      },
      figure9: { // Status Combinations
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 12' },
        minHeight: { xs: '300px', sm: '400px' }
      },
      figure10: { // Service Availability
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 12' },
        minHeight: { xs: '300px', sm: '400px' }
      },
      figure11: { // Temporal Patterns
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 12' },
        minHeight: { xs: '400px', sm: '500px' }
      },
      figure12: { // Service Co-occurrence
        gridColumn: { xs: 'span 12', sm: 'span 12', md: 'span 12' },
        minHeight: { xs: '400px', sm: '400px' }
      }
    };
    return configs[figureId] || {
      gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 4' },
      minHeight: { xs: '300px', sm: '400px' }
    };
  };

  return (
    <Fade in={Object.keys(plots).length > 0}>
      <Box sx={{ p: 3 }}>
        {Object.keys(plots).length > 0 && (
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleSaveAll}
              disabled={savingAll}
              sx={{
                borderRadius: 2,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: 2
                }
              }}
            >
              {savingAll ? 'Saving...' : 'Save All Plots'}
            </Button>
          </Box>
        )}

        <Box sx={{ 
          display: 'grid',
          gridTemplateColumns: {
            xs: 'repeat(12, 1fr)',
            sm: 'repeat(12, 1fr)',
            md: 'repeat(12, 1fr)'
          },
          gap: 3,
        }}>
          {allFigures.map((figureId) => {
            if (!plots[figureId]) return null;  // Don't render empty plot boxes
            
            const gridConfig = getGridConfig(figureId);
            
            return (
              <Fade in key={figureId}>
                <Paper
                  elevation={3}
                  sx={{
                    p: 2,
                    backgroundColor: 'background.paper',
                    borderRadius: 2,
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2,
                    gridColumn: gridConfig.gridColumn,
                    minHeight: gridConfig.minHeight,
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 8
                    }
                  }}
                >
                  <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'flex-start'
                  }}>
                    <Box>
                      <Typography variant="h6" fontWeight="bold" color="primary">
                        {plotConfigs[figureId].title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {plotConfigs[figureId].description}
                      </Typography>
                    </Box>
                    {plots[figureId] && (
                      <Tooltip title="Save Plot">
                        <IconButton 
                          onClick={() => handleSavePlot(figureId)}
                          size="small"
                          sx={{
                            ml: 1,
                            transition: 'all 0.2s ease-in-out',
                            '&:hover': {
                              transform: 'translateY(-2px)',
                              color: 'primary.main'
                            }
                          }}
                        >
                          <SaveIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>

                  <PlotDetails details={plotDetails[figureId]} />

                  <Box 
                    sx={{ 
                      flexGrow: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                      minHeight: isMobile ? '250px' : '300px'
                    }}
                  >
                    {plots[figureId] ? (
                      imageErrors[figureId] ? (
                        <Typography color="error">
                          Failed to load image. Please try refreshing the analysis.
                        </Typography>
                      ) : (
                        <img
                          src={plots[figureId]}
                          alt={`${plotConfigs[figureId].title}`}
                          onError={() => handleImageError(figureId)}
                          onLoad={() => handleImageLoad(figureId)}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'contain',
                            display: 'block',
                            borderRadius: '8px'
                          }}
                        />
                      )
                    ) : (
                      <Box 
                        sx={{ 
                          height: '100%',
                          width: '100%',
                          display: 'flex', 
                          justifyContent: 'center', 
                          alignItems: 'center',
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
                  </Box>
                </Paper>
              </Fade>
            );
          })}
        </Box>
      </Box>
    </Fade>
  );
});

GraphDisplay.displayName = 'GraphDisplay';

export default GraphDisplay; 