import React, { useState } from 'react';
import { 
  Typography, 
  Paper,
  Chip,
  Box,
  Divider,
  TextField,
  Button
} from '@mui/material';
import AnalyticsIcon from '@mui/icons-material/Analytics';

function Dashboard() {
  const [selectedServices, setSelectedServices] = useState([]);
  const [startDate, setStartDate] = useState('2023-08-01');
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);

  const providers = {
    'OpenAI': ['API', 'ChatGPT', 'DALL·E', 'Playground'],
    'Anthropic': ['API', 'Claude', 'Console'],
    'Character.AI': ['Character.AI'],
    'Stability AI': ['Stable Diffusion']
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

  const handleAnalyze = () => {
    console.log('Analyzing with parameters:', {
      startDate,
      endDate,
      selectedServices
    });
    // Add your analysis logic here
  };

  return (
    <div className="dashboard-controls">
      <Typography variant="h6" gutterBottom>
        LLM Service Analysis
      </Typography>
      <Divider sx={{ mb: 2 }} />

      {/* Date Range Selection */}
      <Paper elevation={0} sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
        <Typography variant="subtitle2" gutterBottom>
          Analysis Period
        </Typography>
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

      {/* Service Selection */}
      <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default' }}>
        <Typography variant="subtitle2" gutterBottom>
          Select Services to Analyze
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {Object.entries(providers).map(([provider, services]) => (
            <Box key={provider} sx={{ width: '100%' }}>
              <Typography variant="caption" color="textSecondary" sx={{ mb: 1, display: 'block' }}>
                {provider}
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {services.map((service) => (
                  <Chip
                    key={`${provider}:${service}`}
                    label={service}
                    onClick={() => handleServiceToggle(provider, service)}
                    color={isServiceSelected(provider, service) ? "primary" : "default"}
                    variant={isServiceSelected(provider, service) ? "filled" : "outlined"}
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: isServiceSelected(provider, service) 
                          ? 'primary.dark' 
                          : 'action.hover'
                      }
                    }}
                  />
                ))}
              </Box>
            </Box>
          ))}
        </Box>
      </Paper>

      {/* Selected Services Summary */}
      {selectedServices.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" color="textSecondary" gutterBottom>
            Selected Services: {selectedServices.length}
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {selectedServices.map((serviceId) => {
              const [provider, service] = serviceId.split(':');
              return (
                <Chip
                  key={serviceId}
                  label={`${service} (${provider})`}
                  size="small"
                  onDelete={() => handleServiceToggle(provider, service)}
                  color="primary"
                />
              );
            })}
          </Box>
        </Box>
      )}

      {/* Analyze Button */}
      <Button
        variant="contained"
        color="primary"
        startIcon={<AnalyticsIcon />}
        onClick={handleAnalyze}
        disabled={selectedServices.length === 0}
        sx={{ 
          mt: 3,
          width: '100%',
          py: 1.5,
          textTransform: 'none',
          fontWeight: 500
        }}
      >
        Analyze Selected Services
      </Button>
    </div>
  );
}

export default Dashboard;