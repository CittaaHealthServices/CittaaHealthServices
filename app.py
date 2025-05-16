import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import librosa
import librosa.display
import torch
import torch.nn as nn
import io
import base64
from datetime import datetime
from fpdf import FPDF
import json
import tempfile
import os
from PIL import Image

from vocalysis_clean import (
    AudioProcessor, 
    FeatureExtractor, 
    MentalHealthModel, 
    calculate_mental_health_score,
    interpret_features,
    map_to_psychology_scales,
    generate_recommendations
)

st.set_page_config(
    page_title="Vocalysis - Mental Health Voice Analysis",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

torch.manual_seed(42)
np.random.seed(42)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class MentalHealthModel(nn.Module):
    """Neural network model for mental health classification"""
    
    def __init__(self, input_dim, hidden_dims=[128, 64], num_classes=4):
        """Initialize the model"""
        super().__init__()
        
        layers = []
        prev_dim = input_dim
        for dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, dim))
            layers.append(nn.BatchNorm1d(dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.3))
            prev_dim = dim
        
        self.feature_extractor = nn.Sequential(*layers)
        
        self.classifier = nn.Linear(prev_dim, num_classes)
        
        self.confidence = nn.Sequential(
            nn.Linear(prev_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """Forward pass"""
        features = self.feature_extractor(x)
        logits = self.classifier(features)
        confidence = self.confidence(features)
        return torch.softmax(logits, dim=1), confidence

def generate_synthetic_model(input_dim=100):
    """Generate a synthetic model for demo purposes"""
    model = MentalHealthModel(input_dim=input_dim, hidden_dims=[128, 64], num_classes=4)
    model.eval()
    return model

def generate_pdf_report(features, probabilities, confidence, mental_health_score, interpretations, scale_mappings, recommendations, client_details=None):
    """Generate PDF report with analysis results"""
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'Vocalysis Mental Health Assessment Report', 0, 1, 'C')
            self.ln(5)
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Report generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
    pdf.ln(5)
    
    if client_details:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Client Information', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        pdf.cell(40, 10, 'Name:', 0, 0)
        pdf.cell(0, 10, client_details.get('name', 'N/A'), 0, 1)
        
        pdf.cell(40, 10, 'Age:', 0, 0)
        pdf.cell(0, 10, str(client_details.get('age', 'N/A')), 0, 1)
        
        pdf.cell(40, 10, 'Gender:', 0, 0)
        pdf.cell(0, 10, client_details.get('gender', 'N/A'), 0, 1)
        
        pdf.cell(40, 10, 'Contact:', 0, 0)
        contact_info = client_details.get('email', '')
        if client_details.get('phone', ''):
            if contact_info:
                contact_info += f", {client_details.get('phone', '')}"
            else:
                contact_info = client_details.get('phone', '')
        pdf.cell(0, 10, contact_info or 'N/A', 0, 1)
        
        pdf.cell(40, 10, 'Assessment Reason:', 0, 0)
        pdf.multi_cell(0, 10, client_details.get('assessment_reason', 'N/A'))
        
        pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, 'Disclaimer:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, 'This report is for educational and research purposes only. It is not intended to provide medical diagnosis or replace professional mental health evaluation. If you are experiencing significant distress, please consult a mental health professional.')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Mental Health Score', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Overall Mental Health Score: {mental_health_score:.1f}/100', 0, 1)
    pdf.cell(0, 10, f'Confidence: {confidence:.2f}', 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Mental State Classification', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    states = ['Normal', 'Anxiety', 'Depression', 'Stress']
    for i, state in enumerate(states):
        pdf.cell(0, 10, f'{state}: {probabilities[i]:.2f}', 0, 1)
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Psychology Scale Mappings', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    for scale, score in scale_mappings.items():
        if scale != 'interpretations':
            pdf.cell(0, 10, f'{scale}: {score} - {scale_mappings["interpretations"][scale]}', 0, 1)
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Clinical Interpretations', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    for interpretation in interpretations:
        pdf.multi_cell(0, 5, f'• {interpretation}')
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Recommendations', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    for recommendation in recommendations:
        pdf.multi_cell(0, 5, f'• {recommendation}')
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Voice Feature Analysis', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    key_features = [
        'speech_rate', 'pitch_mean', 'pitch_std', 'rms_mean',
        'zcr_mean', 'spectral_centroid_mean', 'jitter_mean', 'hnr'
    ]
    
    for feature in key_features:
        if feature in features:
            pdf.cell(0, 10, f'{feature}: {features[feature]:.4f}', 0, 1)
    
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    
    return pdf_bytes

def generate_demo_results(demo_type):
    """Generate pre-defined demo results for investor testing
    
    Args:
        demo_type (str): Type of demo ('normal', 'anxiety', 'depression', 'stress')
        
    Returns:
        dict: Demo analysis results
    """
    client_details = {
        "name": "Demo Client",
        "age": "35",
        "gender": "Female",
        "email": "demo@example.com",
        "phone": "555-123-4567",
        "medical_history": "No significant medical history",
        "current_medications": "None",
        "assessment_reason": "Routine mental health check"
    }
    
    features = {
        'duration': 45.0,
        'speech_rate': 3.5,
        'pitch_mean': 180.0,
        'pitch_std': 20.0,
        'rms_mean': 0.5,
        'zcr_mean': 0.1,
        'spectral_centroid_mean': 1500.0,
        'jitter_mean': 0.02,
        'hnr': 15.0
    }
    
    if demo_type == 'normal':
        probabilities = np.array([0.85, 0.05, 0.05, 0.05])  # High normal probability
        confidence = 0.9
    elif demo_type == 'anxiety':
        probabilities = np.array([0.2, 0.7, 0.05, 0.05])    # High anxiety probability
        features['speech_rate'] = 5.0                       # Faster speech rate
        features['pitch_std'] = 30.0                        # Higher pitch variability
        features['jitter_mean'] = 0.04                      # Higher vocal jitter
        confidence = 0.85
    elif demo_type == 'depression':
        probabilities = np.array([0.15, 0.05, 0.75, 0.05])  # High depression probability
        features['speech_rate'] = 2.0                       # Slower speech rate
        features['pitch_std'] = 10.0                        # Lower pitch variability
        features['rms_mean'] = 0.2                          # Lower voice energy
        confidence = 0.88
    elif demo_type == 'stress':
        probabilities = np.array([0.1, 0.15, 0.05, 0.7])    # High stress probability
        features['jitter_mean'] = 0.035                     # Higher vocal jitter
        features['hnr'] = 8.0                               # Lower harmonic-to-noise ratio
        confidence = 0.82
    else:
        probabilities = np.array([0.85, 0.05, 0.05, 0.05])
        confidence = 0.9
    
    mental_health_score = calculate_mental_health_score(probabilities, confidence)
    
    interpretations = interpret_features(features)
    
    scale_mappings = map_to_psychology_scales(probabilities, mental_health_score)
    
    # Generate recommendations
    recommendations = generate_recommendations(probabilities, mental_health_score, scale_mappings)
    
    pdf_report = generate_pdf_report(
        features, probabilities, confidence, mental_health_score,
        interpretations, scale_mappings, recommendations, client_details
    )
    
    return {
        'client_details': client_details,
        'features': features,
        'probabilities': probabilities,
        'confidence': confidence,
        'mental_health_score': mental_health_score,
        'interpretations': interpretations,
        'scale_mappings': scale_mappings,
        'recommendations': recommendations,
        'pdf_report': pdf_report
    }

def run_vocalysis_analysis(audio_data=None, file_path=None, client_details=None):
    """Run the complete Vocalysis analysis pipeline"""
    audio_processor = AudioProcessor()
    feature_extractor = FeatureExtractor()
    
    if audio_data is not None:
        segments, sr, is_valid, validation_message = audio_processor.preprocess_audio(audio_bytes=audio_data)
    elif file_path is not None:
        segments, sr, is_valid, validation_message = audio_processor.preprocess_audio(file_path=file_path)
    else:
        return {'error': 'No audio input provided'}
    
    if not is_valid:
        return {'error': validation_message}
    
    features_df = feature_extractor.extract_features_batch(segments)
    
    avg_features = features_df.mean().to_dict()
    
    model = generate_synthetic_model(input_dim=len(avg_features))
    
    features_tensor = torch.FloatTensor(features_df.values).to(device)
    
    model.eval()
    with torch.no_grad():
        probabilities, confidence = model(features_tensor)
        
        avg_probs = probabilities.mean(dim=0).cpu().numpy()
        avg_conf = confidence.mean().item()
    
    mental_health_score = calculate_mental_health_score(avg_probs, avg_conf)
    
    interpretations = interpret_features(avg_features)
    
    scale_mappings = map_to_psychology_scales(avg_probs, mental_health_score)
    
    recommendations = generate_recommendations(avg_probs, mental_health_score, scale_mappings)
    
    pdf_report = generate_pdf_report(
        avg_features, avg_probs, avg_conf, mental_health_score,
        interpretations, scale_mappings, recommendations, client_details
    )
    
    return {
        'client_details': client_details,
        'features': avg_features,
        'probabilities': avg_probs,
        'confidence': avg_conf,
        'mental_health_score': mental_health_score,
        'interpretations': interpretations,
        'scale_mappings': scale_mappings,
        'recommendations': recommendations,
        'pdf_report': pdf_report
    }

def display_results(results):
    """Display analysis results"""
    if 'error' in results:
        st.error(f"Error: {results['error']}")
        return
    
    if 'client_details' in results and results['client_details']:
        st.header("Client Information")
        client = results['client_details']
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {client.get('name', 'N/A')}")
            st.write(f"**Age:** {client.get('age', 'N/A')}")
            st.write(f"**Gender:** {client.get('gender', 'N/A')}")
        
        with col2:
            st.write(f"**Email:** {client.get('email', 'N/A')}")
            st.write(f"**Phone:** {client.get('phone', 'N/A')}")
            st.write(f"**Assessment Reason:** {client.get('assessment_reason', 'N/A')}")
    
    st.header("Mental Health Assessment Results")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        score = results['mental_health_score']
        
        if score < 40:
            color = 'red'
            category = 'Concern'
        elif score < 70:
            color = 'orange'
            category = 'Moderate'
        else:
            color = 'green'
            category = 'Good'
        
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.barh(0, score, height=0.5, color=color)
        ax.barh(0, 100, height=0.5, color='lightgray', zorder=0)
        
        ax.text(score/2, 0, f"{score:.1f}", ha='center', va='center', color='white', fontweight='bold')
        
        ax.text(score, 0.7, category, ha='center', va='bottom', fontweight='bold', color=color)
        
        ax.set_ylim(-0.5, 1)
        ax.set_xlim(0, 100)
        ax.set_yticks([])
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_title('Mental Health Score', fontsize=14, pad=10)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        st.write(f"Confidence: {results['confidence']:.2f}")
    
    with col2:
        states = ['Normal', 'Anxiety', 'Depression', 'Stress']
        probs = results['probabilities']
        
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(states, probs, color=['green', 'orange', 'red', 'purple'])
        
        for bar, prob in zip(bars, probs):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{prob:.2f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylim(0, 1)
        ax.set_ylabel('Probability')
        ax.set_title('Mental State Classification', fontsize=14)
        plt.tight_layout()
        st.pyplot(fig)
    
    st.header("Psychology Scale Mappings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("GAD-7 (Anxiety)")
        gad_score = results['scale_mappings']['GAD-7']
        gad_interp = results['scale_mappings']['interpretations']['GAD-7']
        st.metric("Score", gad_score, help="Generalized Anxiety Disorder scale (0-21)")
        st.write(f"Interpretation: {gad_interp}")
        
        st.subheader("PHQ-9 (Depression)")
        phq_score = results['scale_mappings']['PHQ-9']
        phq_interp = results['scale_mappings']['interpretations']['PHQ-9']
        st.metric("Score", phq_score, help="Patient Health Questionnaire scale (0-27)")
        st.write(f"Interpretation: {phq_interp}")
    
    with col2:
        st.subheader("PSS (Stress)")
        pss_score = results['scale_mappings']['PSS']
        pss_interp = results['scale_mappings']['interpretations']['PSS']
        st.metric("Score", pss_score, help="Perceived Stress Scale (0-40)")
        st.write(f"Interpretation: {pss_interp}")
        
        st.subheader("WEMWBS (Wellbeing)")
        wemwbs_score = results['scale_mappings']['WEMWBS']
        wemwbs_interp = results['scale_mappings']['interpretations']['WEMWBS']
        st.metric("Score", wemwbs_score, help="Warwick-Edinburgh Mental Wellbeing Scale (14-70)")
        st.write(f"Interpretation: {wemwbs_interp}")
    
    st.header("Clinical Interpretations")
    for interp in results['interpretations']:
        st.write(f"• {interp}")
    
    st.header("Recommendations")
    for rec in results['recommendations']:
        st.write(f"• {rec}")
    
    pdf_bytes = results['pdf_report']
    
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name="vocalysis_report.pdf",
        mime="application/pdf",
        help="Download a comprehensive PDF report of your mental health assessment"
    )

def main():
    if 'client_details' not in st.session_state:
        st.session_state.client_details = {
            "name": "",
            "age": "",
            "gender": "",
            "email": "",
            "phone": "",
            "medical_history": "",
            "current_medications": "",
            "assessment_reason": ""
        }
    
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    st.sidebar.image("https://raw.githubusercontent.com/CittaaHealthServices/CittaaHealthServices/main/assets/logo.png", width=200)
    st.sidebar.title("Vocalysis")
    st.sidebar.write("Advanced Voice Analysis System for Mental Health Assessment")
    
    demo_mode = st.sidebar.checkbox("Demo Mode for Investors", value=st.session_state.demo_mode)
    if demo_mode != st.session_state.demo_mode:
        st.session_state.demo_mode = demo_mode
        st.experimental_rerun()
    
    if st.session_state.demo_mode:
        st.header("Vocalysis Demo Mode for Investors")
        st.write("Select a pre-generated demo to see how Vocalysis analyzes different mental health states.")
        
        demo_options = {
            "normal": "Normal Mental Health State",
            "anxiety": "Anxiety Indicators",
            "depression": "Depression Indicators",
            "stress": "Stress Indicators"
        }
        
        selected_demo = st.selectbox("Select a demo scenario:", 
                                     list(demo_options.keys()),
                                     format_func=lambda x: demo_options[x])
        
        if st.button("Show Demo Results"):
            st.session_state.results = generate_demo_results(selected_demo)
            st.session_state.analysis_complete = True
            st.experimental_rerun()
        
        if st.session_state.analysis_complete and st.session_state.results:
            display_results(st.session_state.results)
        
        st.markdown("### Shareable Demo Links")
        st.write("Share these links with investors to demonstrate Vocalysis:")
        
        base_url = "https://vocalysis-demo.streamlit.app/?demo="
        for demo, description in demo_options.items():
            st.markdown(f"[{description}]({base_url}{demo})")
        
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["Client Details", "Record Audio", "Upload Audio", "About"])
    
    with tab1:
        st.header("Client Information")
        st.write("Please enter the client's personal details before proceeding with the voice analysis.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.client_details["name"] = st.text_input("Full Name", value=st.session_state.client_details["name"])
            st.session_state.client_details["age"] = st.number_input("Age", min_value=0, max_value=120, value=int(st.session_state.client_details["age"]) if st.session_state.client_details["age"] else 0)
            st.session_state.client_details["gender"] = st.selectbox("Gender", ["", "Male", "Female", "Non-binary", "Prefer not to say"], index=0 if not st.session_state.client_details["gender"] else ["", "Male", "Female", "Non-binary", "Prefer not to say"].index(st.session_state.client_details["gender"]))
            st.session_state.client_details["email"] = st.text_input("Email", value=st.session_state.client_details["email"])
        
        with col2:
            st.session_state.client_details["phone"] = st.text_input("Phone Number", value=st.session_state.client_details["phone"])
            st.session_state.client_details["medical_history"] = st.text_area("Relevant Medical History (Optional)", value=st.session_state.client_details["medical_history"])
            st.session_state.client_details["current_medications"] = st.text_area("Current Medications (Optional)", value=st.session_state.client_details["current_medications"])
            
        st.session_state.client_details["assessment_reason"] = st.text_area("Reason for Assessment", value=st.session_state.client_details["assessment_reason"])
        
        if st.button("Save Client Information"):
            if not st.session_state.client_details["name"]:
                st.error("Please enter the client's name.")
            elif not st.session_state.client_details["age"]:
                st.error("Please enter the client's age.")
            elif not st.session_state.client_details["gender"]:
                st.error("Please select the client's gender.")
            elif not st.session_state.client_details["email"] and not st.session_state.client_details["phone"]:
                st.error("Please enter either an email or phone number for contact.")
            else:
                st.success("Client information saved successfully. You can now proceed to record or upload audio.")
    
    with tab2:
        st.header("Record Your Voice")
        st.write("Click the button below to record your voice for analysis. Please speak naturally for at least 30 seconds.")
        
        if not st.session_state.client_details["name"]:
            st.warning("Please fill in the client details before recording.")
        else:
            audio_bytes = st.audio_recorder(
                text="Click to record",
                recording_color="#e8b62c",
                neutral_color="#6aa36f",
                stop_recording_text="Click to stop recording",
            )
            
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                
                if st.button("Analyze Recording"):
                    with st.spinner("Analyzing your voice..."):
                        results = run_vocalysis_analysis(audio_data=audio_bytes, client_details=st.session_state.client_details)
                        st.session_state.results = results
                        st.session_state.analysis_complete = True
                        display_results(results)
    
    with tab3:
        st.header("Upload Audio File")
        st.write("Upload an audio file (WAV or MP3) for analysis. The recording should be at least 30 seconds long.")
        
        if not st.session_state.client_details["name"]:
            st.warning("Please fill in the client details before uploading.")
        else:
            uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3"])
            
            if uploaded_file:
                st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
                
                if st.button("Analyze File"):
                    with st.spinner("Analyzing your voice..."):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        results = run_vocalysis_analysis(file_path=tmp_file_path, client_details=st.session_state.client_details)
                        
                        os.unlink(tmp_file_path)
                        
                        st.session_state.results = results
                        st.session_state.analysis_complete = True
                        display_results(results)
    
    with tab4:
        st.header("About Vocalysis")
        st.write("""
            Vocalysis is an advanced voice analysis system that detects mental health indicators from speech patterns. 
            The system extracts audio features from voice recordings and uses machine learning to classify mental states 
            (Normal, Anxiety, Depression, Stress) with confidence scores.
            
            1. **Audio Processing:** Your voice recording is processed and validated for quality.
            2. **Feature Extraction:** The system extracts clinical-grade voice features including time-domain, 
               frequency-domain, and prosodic features.
            3. **Analysis:** A neural network model analyzes these features to classify your mental state 
               and provide a confidence score.
            4. **Interpretation:** The system interprets the results in a clinical context and maps them 
               to established psychology scales.
            5. **Recommendations:** Based on the analysis, the system provides personalized recommendations.
            
            This system is for educational and research purposes only. It is not intended to provide medical diagnosis 
            or replace professional mental health evaluation. If you are experiencing significant distress, please consult 
            a mental health professional.
        """)
        
        st.subheader("Key Features")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                - **Comprehensive Voice Analysis**
                - **Mental State Classification**
                - **Confidence Scoring**
                - **Psychology Scale Mapping**
            """)
        
        with col2:
            st.markdown("""
                - **Clinical Interpretations**
                - **Personalized Recommendations**
                - **PDF Report Generation**
                - **Privacy-Focused Design**
            """)

if __name__ == "__main__":
    main()
