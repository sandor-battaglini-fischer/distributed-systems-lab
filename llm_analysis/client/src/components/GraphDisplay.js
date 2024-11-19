import React from 'react';
import { Paper, Typography, Grid } from '@mui/material';
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
  const graphs = [
    {
      title: 'Monthly Website Visits, Incident and Outages',
      description: 'Monthly patterns of visits, incidents, and outages',
      icon: <TimelineIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 12,
      imagePath: '/plots/figure1.png'
    },
    {
      title: 'Failure Recovery Model',
      description: 'Single incident recovery analysis',
      icon: <QueryStatsIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/figure2.png'
    },
    {
      title: 'Status Combinations',
      description: 'Presence of different status combinations (GENERAL)',
      icon: <StackedLineChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/figure3.png'
    },
    {
      title: 'Failure Resolution Activities',
      description: 'Time spent on Investigating, Repairing and Checking (GENERAL)',
      icon: <DataUsageIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/figure4.png'
    },
    {
      title: 'Mean Time to Resolve',
      description: 'Distribution of mean time (hours) to resolve (GENERAL)',
      icon: <AccessTimeIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/figure5.png'
    },
    {
      title: 'Mean Time Between Failures',
      description: 'Distribution of mean time (days) between failures (GENERAL)',
      icon: <CompareIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/figure6.png'
    },
    {
      title: 'ECDF of MTTR per Provider',
      description: 'Empirical distribution of mean time to resolve (PROVIDER)',
      icon: <BarChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/figure7.png'
    },
    {
      title: 'ECDF of MTBF per Provider',
      description: 'Empirical distribution of mean time between failures (PROVIDER)',
      icon: <BarChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/figure8.png'
    },
    {
      title: 'Temporal Distribution of Incidents',
      description: 'Distribution by hour of day (PDT time)',
      icon: <TimelineIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 12,
      imagePath: '/plots/figure9.png'
    },
    {
      title: 'Auto-correlations with Incidents',
      description: 'Autocorrelations at different time granularities',
      icon: <BubbleChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/figure10.png'
    },
    {
      title: 'Service Daily Availability',
      description: 'Scaled outage minutes percentage (GENERAL)',
      icon: <QueryStatsIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 6,
      imagePath: '/plots/figure11.png'
    },
    {
      title: 'Co-occurrence Outages',
      description: 'Matrix of outages co-occurrence for all services',
      icon: <TableChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 12,
      imagePath: '/plots/figure12.png'
    },
    {
      title: 'Conditional Probability Matrix',
      description: 'Conditional probability of co-occurrence outages',
      icon: <TableChartIcon sx={{ fontSize: 30, opacity: 0.5 }} />,
      gridSize: 12,
      imagePath: '/plots/figure13.png'
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
                    {`Figure ${index + 1}: ${graph.title}`}
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