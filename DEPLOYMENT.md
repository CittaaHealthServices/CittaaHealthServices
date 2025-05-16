# Vocalysis Deployment Guide

This guide explains how to deploy the Vocalysis system to Streamlit Cloud for free hosting.

## Prerequisites

- A GitHub account
- A Streamlit Cloud account (sign up at https://streamlit.io/cloud)
- The Vocalysis repository forked to your GitHub account

## Deployment Steps

1. **Fork the Repository**
   - Go to https://github.com/CittaaHealthServices/CittaaHealthServices
   - Click the "Fork" button in the top right corner
   - This creates a copy of the repository in your GitHub account

2. **Sign up for Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Sign up using your GitHub account

3. **Deploy the App**
   - In Streamlit Cloud, click "New app"
   - Select your forked repository
   - Set the main file path to `app.py`
   - Click "Deploy"

4. **Access the App**
   - Once deployed, Streamlit Cloud will provide a public URL for your app
   - The URL will be in the format: `https://[your-app-name].streamlit.app`

## Demo Links

The deployed app includes a demo mode for investors to quickly test the system. The demo links are in the format:

- Normal Mental Health State: `https://[your-app-name].streamlit.app/?demo=normal`
- Anxiety Indicators: `https://[your-app-name].streamlit.app/?demo=anxiety`
- Depression Indicators: `https://[your-app-name].streamlit.app/?demo=depression`
- Stress Indicators: `https://[your-app-name].streamlit.app/?demo=stress`

Replace `[your-app-name]` with the actual name of your deployed app.

## Customization

You can customize the app by modifying the following files:

- `app.py`: The main Streamlit application
- `vocalysis_clean.py`: The core functionality of the Vocalysis system

After making changes, commit and push them to your forked repository. Streamlit Cloud will automatically update the deployed app.

## Troubleshooting

If you encounter any issues during deployment:

1. Check the Streamlit Cloud logs for error messages
2. Verify that all dependencies are listed in `requirements.txt`
3. Ensure that the main file path is set correctly to `app.py`
4. Check that your repository is public or that you've granted Streamlit Cloud access to your private repository
