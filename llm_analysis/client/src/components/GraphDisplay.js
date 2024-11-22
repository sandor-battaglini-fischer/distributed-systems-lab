import React, { useState, useEffect } from 'react';
import { Paper, Typography, Grid, CircularProgress } from '@mui/material';
import TimelineIcon from '@mui/icons-material/Timeline';
import QueryStatsIcon from '@mui/icons-material/QueryStats';
import StackedLineChartIcon from '@mui/icons-material/StackedLineChart';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import DataUsageIcon from '@mui/icons-material/DataUsage';
import CompareIcon from '@mui/icons-material/Compare';
import BarChartIcon from '@mui/icons-material/BarChart';
import BubbleChartIcon from '@mui/icons-material/BubbleChart';
import TableChartIcon from '@mui/icons-material/TableChart';

function GraphDisplay() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [plots, setPlots] = useState({});

  // Function to refresh plots when new analysis is done
  const refreshPlots = (newPlots) => {
    setPlots(newPlots);
    setLoading(false);
  };

  // Add error handling for image loading
  const handleImageError = (e) => {
    e.target.src = '/placeholder.png';
    console.error(`Failed to load image: ${e.target.src}`);
  };

  const graphs = [
    {
      title: 'Monthly Website Visits, Incident and Outages',
      description: 'Monthly patterns of visits, incidents, and outages',
      icon: <TimelineIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 12,
      plotKey: 'figure1'
    },
    {
      title: 'Failure Recovery Model',
      description: 'Single incident recovery analysis',
      icon: <QueryStatsIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      plotKey: 'figure2'
    },
    {
      title: 'Status Combinations',
      description: 'Presence of different status combinations (GENERAL)',
      icon: <StackedLineChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      plotKey: 'figure3'
    },
    {
      title: 'Failure Resolution Activities',
      description: 'Time spent on Investigating, Repairing and Checking (GENERAL)',
      icon: <DataUsageIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      plotKey: 'figure4'
    },
    {
      title: 'Mean Time to Resolve',
      description: 'Distribution of mean time (hours) to resolve (GENERAL)',
      icon: <AccessTimeIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      plotKey: 'figure5'
    },
    {
      title: 'Mean Time Between Failures',
      description: 'Distribution of mean time (days) between failures (GENERAL)',
      icon: <CompareIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      plotKey: 'figure6'
    },
    {
      title: 'ECDF of MTTR per Provider',
      description: 'Empirical distribution of mean time to resolve (PROVIDER)',
      icon: <BarChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      plotKey: 'figure7'
    },
    {
      title: 'ECDF of MTBF per Provider',
      description: 'Empirical distribution of mean time between failures (PROVIDER)',
      icon: <BarChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      plotKey: 'figure8'
    },
    {
      title: 'Temporal Distribution of Incidents',
      description: 'Distribution by hour of day (PDT time)',
      icon: <TimelineIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 12,
      plotKey: 'figure9'
    },
    {
      title: 'Auto-correlations with Incidents',
      description: 'Autocorrelations at different time granularities',
      icon: <BubbleChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      plotKey: 'figure10'
    },
    {
      title: 'Service Daily Availability',
      description: 'Scaled outage minutes percentage (GENERAL)',
      icon: <QueryStatsIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      plotKey: 'figure11'
    },
    {
      title: 'Co-occurrence Outages',
      description: 'Matrix of outages co-occurrence for all services',
      icon: <TableChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 12,
      plotKey: 'figure12'
    },
    {
      title: 'Conditional Probability Matrix',
      description: 'Conditional probability of co-occurrence outages',
      icon: <TableChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 12,
      plotKey: 'figure13'
    }
  ];

  return (
    <div className="graphs-section">
      {loading && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
          <CircularProgress />
        </div>
      )}
      
      {error && (
        <Typography color="error" align="center" gutterBottom>
          {error}
        </Typography>
      )}

      <Grid container spacing={2}>
        {graphs.map((graph, index) => (
          <Grid item xs={12} md={graph.gridSize} key={index}>
            <Paper className="graph-card">
              <div className="graph-header">
                {graph.icon}
                <div className="graph-info">
                  <Typography variant="h6" className="graph-title">
                    {`Figure ${index + 1}: ${graph.title}`}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {graph.description}
                  </Typography>
                </div>
              </div>
              <div className="graph-image-container">
                {plots[graph.plotKey] ? (
                  <img 
                    src={`http://localhost:5000${plots[graph.plotKey]}`}
                    alt={graph.title}
                    className="graph-image"
                    onError={handleImageError}
                  />
                ) : (
                  <div className="graph-placeholder">
                    No data available
                  </div>
                )}
              </div>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </div>
  );
}

export default GraphDisplay; 