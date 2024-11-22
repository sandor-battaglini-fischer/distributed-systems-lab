import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  Avatar,
  Link,
  Divider
} from '@mui/material';
import { motion } from 'framer-motion';
import EmailIcon from '@mui/icons-material/Email';
import GitHubIcon from '@mui/icons-material/GitHub';
import LinkedInIcon from '@mui/icons-material/LinkedIn';

const features = [
  {
    title: 'Real-time Analysis',
    description: 'Monitor and analyze LLM service performance in real-time with interactive visualizations.'
  },
  {
    title: 'Multi-service Support',
    description: 'Compare and analyze multiple LLM services simultaneously across different providers.'
  },
  {
    title: 'Historical Data',
    description: 'Access and analyze historical performance data to identify trends and patterns.'
  }
];

const team = [
  {
    name: 'Bálint László Szarvas',
    role: 'Developer',
    email: 'b.l.szarvas@student.vu.nl',
    github: 'https://github.com/balintszarvas',
    linkedin: 'https://linkedin.com/in/balintszarvas',
    image: '/team/balint.jpg'
  },
  {
    name: 'Nishanthi Srinivasan',
    role: 'Developer',
    email: 'n.srinivasan@student.vu.nl',
    github: 'https://github.com/nishanthisrinivasan',
    linkedin: 'https://linkedin.com/in/nishanthisrinivasan',
    image: '/team/nishanthi.jpg'
  },
  {
    name: 'Sándor Battaglini-Fischer',
    role: 'Developer',
    email: 's.battaglini-fischer@student.vu.nl',
    github: 'https://github.com/sandor-battaglini-fischer',
    linkedin: 'https://linkedin.com/in/sandorbattaglinifischer',
    image: '/team/sandor.jpg'
  }
];

function About() {
  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h3" gutterBottom align="center" sx={{ mb: 6 }}>
          About LLM Analysis Dashboard
        </Typography>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={4} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.2 }}
              >
                <Card 
                  elevation={0}
                  sx={{ 
                    height: '100%',
                    bgcolor: 'background.paper',
                    border: 1,
                    borderColor: 'divider',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      transition: 'transform 0.3s ease-in-out'
                    }
                  }}
                >
                  <CardContent>
                    <Typography variant="h5" component="h2" gutterBottom>
                      {feature.title}
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        <Paper 
          elevation={0}
          sx={{ 
            mt: 6, 
            p: 4,
            bgcolor: 'background.paper',
            border: 1,
            borderColor: 'divider'
          }}
        >
          <Typography variant="h4" gutterBottom>
            Our Mission
          </Typography>
          <Typography variant="body1" paragraph>
            The LLM Analysis Dashboard provides comprehensive insights into the performance and reliability of various Language Learning Model services. Our goal is to help developers and organizations make informed decisions about which LLM services best suit their needs.
          </Typography>
        </Paper>

        <Box sx={{ mt: 6 }}>
          <Typography variant="h4" gutterBottom align="center">
            Meet the Team
          </Typography>
          <Grid container spacing={4} sx={{ mt: 2 }}>
            {team.map((member, index) => (
              <Grid item xs={12} md={4} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.2 }}
                >
                  <Card 
                    elevation={0} 
                    sx={{ 
                      border: 1, 
                      borderColor: 'divider',
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column'
                    }}
                  >
                    <Box
                      sx={{
                        position: 'relative',
                        paddingTop: '100%', // 1:1 Aspect ratio
                        overflow: 'hidden'
                      }}
                    >
                      {member.image ? (
                        <Box
                          component="img"
                          src={member.image}
                          alt={member.name}
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            transition: 'transform 0.3s ease-in-out',
                            '&:hover': {
                              transform: 'scale(1.05)'
                            }
                          }}
                          onError={(e) => {
                            // Fallback to Avatar if image fails to load
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <Box
                        sx={{
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          width: '100%',
                          height: '100%',
                          display: member.image ? 'none' : 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          bgcolor: 'action.selected'
                        }}
                      >
                        <Avatar
                          sx={{
                            width: '60%',
                            height: '60%',
                            fontSize: '3rem',
                            bgcolor: 'primary.main'
                          }}
                        >
                          {member.name.split(' ').map(n => n[0]).join('')}
                        </Avatar>
                      </Box>
                    </Box>

                    <CardContent sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" gutterBottom>
                        {member.name}
                      </Typography>
                      <Typography 
                        variant="subtitle2" 
                        color="textSecondary" 
                        gutterBottom
                        sx={{ mb: 2 }}
                      >
                        {member.role}
                      </Typography>
                      <Divider sx={{ my: 2 }} />
                      <Box 
                        sx={{ 
                          display: 'flex', 
                          gap: 2, 
                          justifyContent: 'center',
                          '& a': {
                            transition: 'all 0.2s ease-in-out',
                            '&:hover': {
                              transform: 'translateY(-2px)',
                              color: 'primary.main'
                            }
                          }
                        }}
                      >
                        <Link 
                          href={`mailto:${member.email}`} 
                          color="inherit"
                          title="Email"
                        >
                          <EmailIcon />
                        </Link>
                        <Link 
                          href={member.github} 
                          target="_blank" 
                          color="inherit"
                          title="GitHub"
                        >
                          <GitHubIcon />
                        </Link>
                        <Link 
                          href={member.linkedin} 
                          target="_blank" 
                          color="inherit"
                          title="LinkedIn"
                        >
                          <LinkedInIcon />
                        </Link>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Box>
      </motion.div>
    </Box>
  );
}

export default About; 