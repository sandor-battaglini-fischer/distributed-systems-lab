import React from 'react';
import { Paper, Typography, Grid } from '@mui/material';
import TimelineIcon from '@mui/icons-material/Timeline';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CompareIcon from '@mui/icons-material/Compare';
import RestoreIcon from '@mui/icons-material/Restore';
import ShowChartIcon from '@mui/icons-material/ShowChart';

function GraphDisplay() {
  const graphs = [
    {
      title: 'Failure Analysis Over Time',
      description: 'Login, latency, and error patterns across services',
      icon: <TimelineIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 12,
      imagePath: '/plots/failure_analysis.png'
    },
    {
      title: 'Time Series Prediction',
      description: 'Predictive modeling of future performance',
      icon: <TrendingUpIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/time_series.png'
    },
    {
      title: 'Service Correlation Analysis',
      description: 'Statistical correlation between different services',
      icon: <CompareIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/correlation.png'
    },
    {
      title: 'Recovery Time Analysis',
      description: 'Service recovery patterns and predictions',
      icon: <RestoreIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/recovery_time.png'
    },
    {
      title: 'Oscillation Patterns',
      description: 'Periodic patterns and data fitting analysis',
      icon: <ShowChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/oscillation.png'
    }
  ];

  return (
    <div className="graphs-section">
      <Grid container spacing={2}>
        {graphs.map((graph, index) => (
          <Grid item xs={12} md={graph.gridSize} key={index}>
            <Paper className="graph-card">
              <div className="graph-header">
                {graph.icon}
                <div className="graph-info">
                  <Typography variant="h6" className="graph-title">
                    {graph.title}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {graph.description}
                  </Typography>
                </div>
              </div>
              <div className="graph-image-container">
                <img 
                  src={graph.imagePath} 
                  alt={graph.title}
                  className="graph-image"
                  onError={(e) => {
                    e.target.src = '/plots/placeholder.png';
                  }}
                />
              </div>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </div>
  );
}

export default GraphDisplay; 