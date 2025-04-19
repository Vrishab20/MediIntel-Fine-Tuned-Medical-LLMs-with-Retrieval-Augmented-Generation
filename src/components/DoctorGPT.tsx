import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Grid,
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const API_BASE_URL = 'https://mediintel.onrender.com';

const DoctorGPT: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      await handleFileUpload(acceptedFiles[0]);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
  });

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    setError('');
    setUploadSuccess(false);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadSuccess(true);
      console.log('Upload success:', response.data);
    } catch (err) {
      setError('An error occurred while uploading the file');
      console.error(err);
      setUploadSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!uploadSuccess) {
      setError('Please upload a PDF file first');
      return;
    }

    if (!question) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/ask`, {
        question: question
      });

      setResponse(response.data.response);
    } catch (err) {
      setError('An error occurred while processing your request');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          🩺 DoctorGPT - Virtual Medical Assistant
        </Typography>
        <Typography variant="subtitle1" gutterBottom align="center" color="text.secondary">
          Powered by TinyLlama and Qdrant
        </Typography>

        <Alert severity="warning" sx={{ mb: 3 }}>
          ⚠️ Disclaimer: This is an AI assistant for informational purposes only, not a substitute for professional medical advice.
          Always consult a qualified healthcare provider for medical concerns.
        </Alert>

        <Paper
          {...getRootProps()}
          sx={{
            p: 3,
            mb: 3,
            border: '2px dashed #ccc',
            backgroundColor: isDragActive ? '#f5f5f5' : 'white',
            cursor: 'pointer',
          }}
        >
          <input {...getInputProps()} />
          {file ? (
            <Typography variant="body1">
              Selected file: {file.name} {uploadSuccess && '(✓ Uploaded)'}
            </Typography>
          ) : (
            <Typography variant="body1" align="center">
              Drag and drop a PDF file here, or click to select one
            </Typography>
          )}
        </Paper>

        <TextField
          fullWidth
          multiline
          rows={4}
          variant="outlined"
          label="Your Medical Question"
          placeholder="e.g. What treatment options would you recommend based on the patient's history?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          sx={{ mb: 3 }}
        />

        <Grid container spacing={2} justifyContent="center">
          <Grid item>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              disabled={loading || !uploadSuccess || !question}
            >
              {loading ? <CircularProgress size={24} /> : 'Generate Response'}
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              color="secondary"
              onClick={() => {
                setQuestion('');
                setResponse('');
                setFile(null);
                setUploadSuccess(false);
              }}
            >
              Clear Inputs
            </Button>
          </Grid>
        </Grid>

        {error && (
          <Alert severity="error" sx={{ mt: 3 }}>
            {error}
          </Alert>
        )}

        {response && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              🧾 DoctorGPT Response
            </Typography>
            <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
              {response}
            </Typography>
          </Paper>
        )}

        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            💡 Example Questions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => setQuestion("What treatment options would you recommend based on the patient's current condition?")}
              >
                Treatment Options
              </Button>
            </Grid>
            <Grid item xs={4}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => setQuestion("Please review the patient's current medications and suggest any necessary adjustments.")}
              >
                Medication Review
              </Button>
            </Grid>
            <Grid item xs={4}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => setQuestion("What would be an appropriate follow-up plan for this patient?")}
              >
                Follow-up Plan
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Container>
  );
};

export default DoctorGPT; 