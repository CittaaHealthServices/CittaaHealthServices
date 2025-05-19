# Vocalysis Testing Guide

This guide provides instructions for testing the enhanced Vocalysis system for mental health voice analysis.

## Accessing the Testing Environment

The Vocalysis system is available for testing at the following URL:
[Vocalysis Testing Link](https://voice-stress-analyzer-tunnel-oy4e5h6v.devinapps.com)

### Authentication

The system requires two levels of authentication:

1. **Tunnel Authentication**:
   - Username: user
   - Password: 82732e9bdfa4faf05eeb16925b3b33b6

2. **Application Authentication**:
   - Username: Cittaa2003
   - Password: Cittaa@2024

## Testing Features

### 1. Model Architecture Selection

The enhanced system supports multiple neural network architectures:

- **Ensemble (Default)**: Combines predictions from all architectures for optimal performance
- **MLP**: Basic multi-layer perceptron (original architecture)
- **CNN**: Convolutional neural network for capturing local patterns
- **RNN**: Recurrent neural network for temporal dependencies
- **Attention**: Self-attention mechanism for focusing on important features

To test different architectures:
1. Select the desired architecture from the dropdown in the sidebar
2. Upload a voice recording or use the demo mode
3. Compare results across different architectures

### 2. Voice Recording Analysis

To test with your own voice recordings:

a. Use the microphone recorder:
   - Click the "Record Audio" button in the "Record Your Voice" section
   - Speak naturally for 30-60 seconds
   - Click the button again to stop recording (or it will stop automatically after 60 seconds)
   - Click "Analyze Recording" to analyze your voice

b. Upload a recording:
   - Click the "Browse files" button in the "Upload Voice Recording" section
   - Select your audio file (WAV, MP3, or OGG format)
   - Click "Analyze Voice"
   
3. Review the analysis results:
   - Mental health score (0-100 scale)
   - Probability distribution across mental health states
   - Confidence level of the analysis
   - Feature visualizations
   - Psychological scale mappings
   - Personalized recommendations

### 3. Demo Mode

To test with pre-recorded demos:

1. In the sidebar, select a demo scenario:
   - Normal: Typical voice patterns with no mental health concerns
   - Anxiety: Voice patterns indicating anxiety
   - Depression: Voice patterns indicating depression
   - Stress: Voice patterns indicating stress
   
2. Click "Run Demo"

3. Review the analysis results as described above

### 4. PDF Report Generation

Each analysis automatically generates a PDF report:

1. After analysis is complete, click the "Download PDF Report" button
2. Open the downloaded PDF to review:
   - Summary of mental health indicators
   - Detailed feature analysis
   - Visualizations of key voice biomarkers
   - Psychological scale mappings
   - Personalized recommendations

### 5. Secure Storage (For Administrators)

The system includes secure storage for voice data and analysis results:

1. Enable/disable secure storage using the checkbox in the sidebar
2. When enabled, voice recordings and analysis results are encrypted and stored securely
3. Data can be retrieved for future reference using the data ID

## Feedback and Issues

Please provide feedback on the following aspects:

1. **Accuracy**: How well do the results match expectations?
2. **User Experience**: Is the interface intuitive and easy to use?
3. **Performance**: How quickly does the system process voice recordings?
4. **Report Quality**: Are the PDF reports informative and well-formatted?
5. **Model Comparison**: Which neural network architecture performs best?

Report any issues or suggestions to: support@cittaa.in

## Privacy Notice

All voice recordings and analysis results are handled securely:

- Voice data is encrypted using industry-standard encryption
- Data is stored only for the duration of the testing period
- No personal information is required to use the testing system
- Test data will be deleted after the testing period concludes

By using this testing system, you acknowledge that your voice recordings will be processed for mental health analysis and temporarily stored in the secure storage system.
