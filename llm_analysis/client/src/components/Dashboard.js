import React, { useState } from 'react';
import { Container, Typography, Button, TextField, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

function Dashboard() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [llmService, setLlmService] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log('Submitted:', { startDate, endDate, llmService });
    // Here you would typically make an API call to your Flask backend
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" component="h1" gutterBottom>
        LLM Analysis Dashboard
      </Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Start Date"
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
          fullWidth
          margin="normal"
        />
        <TextField
          label="End Date"
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
          fullWidth
          margin="normal"
        />
        <FormControl fullWidth margin="normal">
          <InputLabel>LLM Service</InputLabel>
          <Select
            value={llmService}
            onChange={(e) => setLlmService(e.target.value)}
          >
            <MenuItem value="openai">OpenAI</MenuItem>
            <MenuItem value="anthropic">Anthropic</MenuItem>
            <MenuItem value="other">Add more here</MenuItem>
          </Select>
        </FormControl>
        <Button type="submit" variant="contained" color="primary" fullWidth>
          Generate Analysis
        </Button>
      </form>
    </Container>
  );
}

export default Dashboard;