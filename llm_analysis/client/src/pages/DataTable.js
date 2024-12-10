import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  CircularProgress,
  Chip,
  Button,
  Alert,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  CloudSync as CloudSyncIcon,
} from '@mui/icons-material';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';
import { useTheme } from '@mui/material/styles';

const DataTable = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [scraping, setScraping] = useState(false);
  const [scrapeMessage, setScrapeMessage] = useState(null);
  const [statusCheckInterval, setStatusCheckInterval] = useState(null);
  const theme = useTheme();

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      return new Intl.DateTimeFormat('default', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (e) {
      console.error('Error formatting date:', e);
      return dateStr;
    }
  };

  const getProviderColor = (provider) => {
    const colors = {
      'openai': '#00000015',
      'anthropic': '#0000ff15',
      'character': '#ff000015',
      'StabilityAI': '#00800015'
    };
    return colors[provider] || '#00000010';
  };

  const columns = [
    { 
      field: '__row_number__',
      headerName: '#',
      width: 60,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.id ? data.findIndex(row => row.id === params.id) + 1 : ''}
        </Typography>
      )
    },
    { 
      field: 'provider', 
      headerName: 'Provider', 
      width: 100,
      renderCell: (params) => (
        <Typography 
          sx={{ 
            textTransform: 'capitalize',
            whiteSpace: 'normal',
            lineHeight: 1.2,
            width: '100%',
            backgroundColor: getProviderColor(params.value),
            px: 1,
            py: 0.5,
            borderRadius: 1,
            display: 'inline-block',
            textAlign: 'center'
          }} 
          variant="body2"
        >
          {params.value || ''}
        </Typography>
      )
    },
    { 
      field: 'Incident_Title', 
      headerName: 'Title', 
      width: 100,
      flex: 1,
      renderCell: (params) => (
        <Typography 
          variant="body2" 
          sx={{ 
            whiteSpace: 'normal',
            lineHeight: 1.2,
            display: '-webkit-box',
            overflow: 'hidden',
            WebkitBoxOrient: 'vertical',
            WebkitLineClamp: 2
          }}
        >
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'incident_impact_level', 
      headerName: 'Impact', 
      width: 90,
      renderCell: (params) => {
        const value = params.value;
        const color = params.row.incident_color;
        return (
          <Chip 
            label={
              value === 0 ? 'Minor' :
              value === 1 ? 'Moderate' :
              value === 2 ? 'Major' :
              value === 3 ? 'Critical' :
              value === 4 ? 'Maintenance' : 'Unknown'
            }
            sx={{ 
              borderColor: color,
              color: color,
              '& .MuiChip-label': {
                color: color
              }
            }}
            size="small"
            variant="outlined"
          />
        );
      }
    },
    { 
      field: 'services_affected',
      headerName: 'Services',
      width: 400,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', py: 0.5 }}>
          {Object.entries(params.row)
            .filter(([key, value]) => 
              !['incident_id', 'provider', 'Incident_Title', 'incident_impact_level', 
                'incident_color', 'start_timestamp', 'close_timestamp', 'duration', 
                'status', 'id', '__row_number__'].includes(key) 
              && value === true
            )
            .map(([service]) => (
              <Chip
                key={service}
                label={service}
                size="small"
                sx={{ 
                  backgroundColor: `${theme.palette.primary.main}22`,
                  color: 'primary.main',
                  height: '20px',
                  '& .MuiChip-label': {
                    px: 1,
                    fontSize: '0.75rem'
                  }
                }}
              />
            ))}
        </Box>
      ),
    },
    { 
      field: 'start_timestamp', 
      headerName: 'Start Time', 
      width: 150,
      renderCell: (params) => (
        <Typography 
          variant="body2"
          sx={{ 
            whiteSpace: 'normal',
            lineHeight: 1.2
          }}
        >
          {formatDate(params.value)}
        </Typography>
      )
    },
    { 
      field: 'close_timestamp', 
      headerName: 'End Time', 
      width: 150,
      renderCell: (params) => (
        <Typography 
          variant="body2"
          sx={{ 
            whiteSpace: 'normal',
            lineHeight: 1.2
          }}
        >
          {params.value ? formatDate(params.value) : 'Ongoing'}
        </Typography>
      )
    },
    { 
      field: 'duration', 
      headerName: 'Duration', 
      width: 110,
      renderCell: (params) => (
        <Typography 
          variant="body2"
          sx={{ 
            whiteSpace: 'normal',
            lineHeight: 1.2
          }}
        >
          {params.value}
        </Typography>
      )
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 160,
      renderCell: (params) => (
        <Typography 
          variant="body2" 
          sx={{ 
            color: params.value?.includes('Resolved') ? 'success.main' : 'text.primary',
            whiteSpace: 'normal',
            lineHeight: 1.2,
            display: '-webkit-box',
            overflow: 'hidden',
            WebkitBoxOrient: 'vertical',
            WebkitLineClamp: 2
          }}
        >
          {params.value || 'Unknown'}
        </Typography>
      )
    }
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/incidents');
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
      const result = await response.json();
      setData(result.data.map((row, index) => ({
        ...row,
        id: row.incident_id || index,
        __row_number__: index + 1
      })));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const csvContent = [
      columns.map(col => col.headerName),
      ...data.map(row => 
        columns.map(col => 
          row[col.field]?.toString() || ''
        )
      )
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `incidents_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const checkScraperStatus = async () => {
    try {
      const response = await fetch('/api/scraper-status');
      const result = await response.json();
      
      if (result.status === 'running') {
        setScrapeMessage({
          severity: 'info',
          message: result.message,
          details: result.details
        });
      } else if (result.status === 'error') {
        setScrapeMessage({
          severity: 'error',
          message: 'Scraper process failed',
          details: result.details
        });
        clearInterval(statusCheckInterval);
        setStatusCheckInterval(null);
      } else {
        // Process completed
        setScrapeMessage({
          severity: 'success',
          message: 'Scrapers completed successfully',
          details: result.message
        });
        clearInterval(statusCheckInterval);
        setStatusCheckInterval(null);
        await fetchData();
      }
    } catch (err) {
      console.error('Error checking scraper status:', err);
    }
  };

  const handleRunScrapers = async () => {
    try {
      setScraping(true);
      setScrapeMessage({ 
        severity: 'info', 
        message: 'Starting scraper process...',
        details: 'Initializing scrapers...'
      });
      
      const response = await fetch('/api/run-scrapers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const result = await response.json();
      
      if (response.status === 202) {
        // Start polling for status updates
        setScrapeMessage({
          severity: 'info',
          message: result.message,
          details: result.details
        });
        
        // Clear any existing interval
        if (statusCheckInterval) {
          clearInterval(statusCheckInterval);
        }
        
        // Start new status check interval
        const intervalId = setInterval(checkScraperStatus, 5000); // Check every 5 seconds
        setStatusCheckInterval(intervalId);
        
        // Set a timeout to stop checking after 15 minutes
        setTimeout(() => {
          if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
            setStatusCheckInterval(null);
            setScrapeMessage({
              severity: 'warning',
              message: 'Status checking timed out',
              details: 'The scraper process may still be running. Please refresh the page to check for new data.'
            });
          }
        }, 900000); // 15 minutes
        
      } else if (!response.ok) {
        throw new Error(result.details || result.message || 'Failed to start scrapers');
      }
      
    } catch (err) {
      console.error('Error running scrapers:', err);
      setScrapeMessage({ 
        severity: 'error', 
        message: 'Failed to start scraper process',
        details: err.message
      });
      if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        setStatusCheckInterval(null);
      }
    } finally {
      setScraping(false);
    }
  };

  useEffect(() => {
    return () => {
      if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
      }
    };
  }, [statusCheckInterval]);

  return (
    <Box sx={{ p: 2, maxWidth: '100%', mx: 'auto' }}>
      <Paper 
        elevation={3}
        sx={{ 
          p: 2,
          backgroundColor: 'background.paper',
          borderRadius: 2,
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
        }}>
          <Typography variant="h6" component="h1" sx={{ 
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}>
            Incident Data
            {loading && <CircularProgress size={20} sx={{ ml: 1 }} />}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Run Scrapers">
              <IconButton
                onClick={handleRunScrapers}
                disabled={scraping || loading}
                size="small"
                color="primary"
                sx={{
                  animation: scraping ? 'spin 2s linear infinite' : 'none',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' }
                  }
                }}
              >
                <CloudSyncIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh Data">
              <IconButton 
                onClick={fetchData}
                disabled={loading || scraping}
                size="small"
                sx={{
                  transition: 'all 0.2s',
                  '&:hover': {
                    transform: 'rotate(180deg)',
                  }
                }}
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleExport}
              disabled={loading || scraping || data.length === 0}
              size="small"
            >
              Export CSV
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {scrapeMessage && (
          <Alert 
            severity={scrapeMessage.severity} 
            sx={{ mb: 2 }}
            onClose={() => setScrapeMessage(null)}
          >
            <div>
              {scrapeMessage.message}
              {scrapeMessage.details && (
                <Typography 
                  variant="body2" 
                  sx={{ 
                    mt: 1, 
                    whiteSpace: 'pre-wrap',
                    fontSize: '0.85rem',
                    opacity: 0.8
                  }}
                >
                  {scrapeMessage.details}
                </Typography>
              )}
            </div>
          </Alert>
        )}

        <Box sx={{ 
          height: 'auto', 
          width: '100%',
          overflow: 'visible'
        }}>
          <DataGrid
            rows={data}
            columns={columns}
            autoHeight
            checkboxSelection
            disableSelectionOnClick
            loading={loading}
            components={{
              Toolbar: GridToolbar,
              Footer: null,
              Pagination: null,
            }}
            componentsProps={{
              toolbar: {
                showQuickFilter: true,
                quickFilterProps: { debounceMs: 500 },
                printOptions: { disableToolbarButton: true }
              },
            }}
            pagination={false}
            paginationMode="server"
            rowCount={data.length}
            pageSize={data.length}
            rowsPerPageOptions={[data.length]}
            sx={{
              border: 'none',
              maxHeight: 'none !important',
              '& .MuiDataGrid-main': {
                maxHeight: 'none !important'
              },
              '& .MuiDataGrid-virtualScroller': {
                maxHeight: 'none !important'
              },
              '& .MuiDataGrid-cell': {
                py: 1.5,
                minHeight: '48px !important',
                maxHeight: '48px !important',
                overflow: 'hidden',
                whiteSpace: 'normal',
                lineHeight: 1.2,
                display: 'flex',
                alignItems: 'center'
              },
              '& .MuiDataGrid-row': {
                minHeight: '48px !important',
                maxHeight: '48px !important',
              },
              '& .MuiDataGrid-cell:focus': {
                outline: 'none'
              },
              '& .MuiDataGrid-columnHeader:focus': {
                outline: 'none'
              },
              '& .MuiDataGrid-cellContent': {
                whiteSpace: 'normal',
                lineHeight: 1.2
              },
              '& .MuiDataGrid-footerContainer': {
                display: 'none'
              },
              '& .MuiDataGrid-virtualScroller': {
                '&::-webkit-scrollbar': {
                  width: '8px',
                  height: '8px'
                },
                '&::-webkit-scrollbar-track': {
                  background: '#f1f1f1'
                },
                '&::-webkit-scrollbar-thumb': {
                  background: '#888',
                  borderRadius: '4px'
                },
                '&::-webkit-scrollbar-thumb:hover': {
                  background: '#666'
                }
              }
            }}
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default DataTable;