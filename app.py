import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime
from fpdf import FPDF
import tempfile
import os

st.set_page_config(
    page_title="Vocalysis - Mental Health Voice Analysis",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

np.random.seed(42)

def calculate_mental_health_score(probabilities, confidence):
    """Calculate 0-100 mental health score from probabilities and confidence"""
    normal_weight = 1.0
    anxiety_weight = -0.5
    depression_weight = -0.5
    stress_weight = -0.5
    
    base_score = (
        probabilities[0] * normal_weight + 
        probabilities[1] * anxiety_weight + 
        probabilities[2] * depression_weight +
        probabilities[3] * stress_weight
    )
    
    scaled_score = (base_score + 0.5) * 100
    adjusted_score = scaled_score * (0.7 + 0.3 * confidence)
    
    return max(0, min(100, adjusted_score))

def interpret_features(features):
    """Generate clinical interpretations from voice features"""
    interpretations = []
    
    if 'speech_rate' in features:
        if features['speech_rate'] < 2.5:
            interpretations.append(
                f"Speech rate is slow ({features['speech_rate']:.2f} syllables/sec), "
                f"which may indicate reduced cognitive processing speed, fatigue, "
                f"or possible depression."
            )
        elif features['speech_rate'] > 4.5:
            interpretations.append(
                f"Speech rate is elevated ({features['speech_rate']:.2f} syllables/sec), "
                f"which may indicate heightened arousal, anxiety, or agitation."
            )
    
    if 'pitch_std' in features:
        if features['pitch_std'] < 15.0:
            interpretations.append(
                f"Low pitch variability ({features['pitch_std']:.2f} Hz), "
                f"which may indicate emotional flattening, reduced expressivity, "
                f"or possible depression."
            )
        elif features['pitch_std'] > 25.0:
            interpretations.append(
                f"High pitch variability ({features['pitch_std']:.2f} Hz), "
                f"which may indicate emotional lability, heightened reactivity, "
                f"or possible anxiety."
            )
    
    if 'rms_mean' in features:
        if features['rms_mean'] < 0.3:
            interpretations.append(
                f"Low voice energy ({features['rms_mean']:.2f}), "
                f"which may indicate low motivation, fatigue, "
                f"or possible depression."
            )
        elif features['rms_mean'] > 0.7:
            interpretations.append(
                f"High voice energy ({features['rms_mean']:.2f}), "
                f"which may indicate agitation, heightened arousal, "
                f"or possible mania/anxiety."
            )
    
    if 'jitter_mean' in features:
        if features['jitter_mean'] > 0.03:
            interpretations.append(
                f"High vocal jitter ({features['jitter_mean']:.4f}), "
                f"which may indicate vocal tension, physiological stress, "
                f"or possible anxiety."
            )
    
    if 'hnr' in features:
        if features['hnr'] < 10.0:
            interpretations.append(
                f"Low harmonic-to-noise ratio ({features['hnr']:.2f} dB), "
                f"which may indicate increased vocal noise, reduced vocal control, "
                f"or possible stress/anxiety."
            )
    
    return interpretations

def map_to_psychology_scales(probabilities, mental_health_score):
    """Map model outputs to established psychology scales"""
    mappings = {}
    
    mappings['GAD-7'] = min(21, int(probabilities[1] * 21))
    if mappings['GAD-7'] < 5:
        mappings['interpretations'] = {'GAD-7': "Minimal anxiety"}
    elif mappings['GAD-7'] < 10:
        mappings['interpretations'] = {'GAD-7': "Mild anxiety"}
    elif mappings['GAD-7'] < 15:
        mappings['interpretations'] = {'GAD-7': "Moderate anxiety"}
    else:
        mappings['interpretations'] = {'GAD-7': "Severe anxiety"}
    
    mappings['PHQ-9'] = min(27, int(probabilities[2] * 27))
    if mappings['PHQ-9'] < 5:
        mappings['interpretations']['PHQ-9'] = "Minimal depression"
    elif mappings['PHQ-9'] < 10:
        mappings['interpretations']['PHQ-9'] = "Mild depression"
    elif mappings['PHQ-9'] < 15:
        mappings['interpretations']['PHQ-9'] = "Moderate depression"
    elif mappings['PHQ-9'] < 20:
        mappings['interpretations']['PHQ-9'] = "Moderately severe depression"
    else:
        mappings['interpretations']['PHQ-9'] = "Severe depression"
    
    mappings['PSS'] = min(40, int(probabilities[3] * 40))
    if mappings['PSS'] < 14:
        mappings['interpretations']['PSS'] = "Low stress"
    elif mappings['PSS'] < 27:
        mappings['interpretations']['PSS'] = "Moderate stress"
    else:
        mappings['interpretations']['PSS'] = "High stress"
    
    mappings['WEMWBS'] = int(14 + (mental_health_score / 100) * (70 - 14))
    if mappings['WEMWBS'] < 40:
        mappings['interpretations']['WEMWBS'] = "Low wellbeing"
    elif mappings['WEMWBS'] < 59:
        mappings['interpretations']['WEMWBS'] = "Average wellbeing"
    else:
        mappings['interpretations']['WEMWBS'] = "High wellbeing"
    
    return mappings

def generate_recommendations(probabilities, mental_health_score, scale_mappings):
    """Generate recommendations based on probabilities and mental health score"""
    recommendations = []
    
    if mental_health_score < 40:
        recommendations.append(
            "Consider consulting with a mental health professional for a comprehensive evaluation."
        )
        recommendations.append(
            "Establish a self-care routine including regular physical activity, adequate sleep, and balanced nutrition."
        )
    elif mental_health_score < 70:
        recommendations.append(
            "Monitor your mental health regularly and be attentive to changes in mood, energy, or stress levels."
        )
        recommendations.append(
            "Practice stress management techniques such as deep breathing, mindfulness, or progressive muscle relaxation."
        )
    else:
        recommendations.append(
            "Maintain your current well-being practices and continue monitoring your mental health."
        )
        recommendations.append(
            "Share your successful coping strategies with others who may benefit from your experience."
        )
    
    if probabilities[1] > 0.3:  # Anxiety
        recommendations.append(
            "For anxiety management, consider regular mindfulness meditation practice and breathing exercises."
        )
        if scale_mappings['GAD-7'] >= 10:
            recommendations.append(
                "Based on your anxiety indicators, consider consulting a mental health professional for targeted anxiety interventions."
            )
    
    if probabilities[2] > 0.3:  # Depression
        recommendations.append(
            "For mood improvement, engage in regular physical activity and maintain social connections."
        )
        if scale_mappings['PHQ-9'] >= 10:
            recommendations.append(
                "Based on your depression indicators, consider consulting a mental health professional for appropriate support."
            )
    
    if probabilities[3] > 0.3:  # Stress
        recommendations.append(
            "For stress reduction, identify and address sources of stress in your life and practice regular relaxation techniques."
        )
        if scale_mappings['PSS'] >= 27:
            recommendations.append(
                "Based on your stress levels, consider implementing boundaries, time management strategies, and seeking support."
            )
    
    return recommendations

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
        pdf.multi_cell(0, 5, f'- {interpretation}')
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Recommendations', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    for recommendation in recommendations:
        pdf.multi_cell(0, 5, f'- {recommendation}')
    
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
    
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin1')
    
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
    """Main application function"""
    st.title("Vocalysis - Mental Health Voice Analysis")
    
    st.sidebar.title("Options")
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    if 'demo_type' not in st.session_state:
        st.session_state.demo_type = None
    
    model_type = st.sidebar.selectbox(
        "Select Model Architecture",
        ["ensemble", "mlp", "cnn", "rnn", "attention"],
        index=0,
        help="Choose the neural network architecture to use for analysis"
    )
    
    use_secure_storage = st.sidebar.checkbox(
        "Use Secure Storage",
        value=True,
        help="Enable secure storage for voice data and analysis results"
    )
    
    st.sidebar.markdown("## Demo Mode")
    st.sidebar.markdown("Try a pre-recorded demo:")
    
    demo_options = {
        "Normal": "normal",
        "Anxiety": "anxiety",
        "Depression": "depression",
        "Stress": "stress"
    }
    
    selected_demo = st.sidebar.selectbox("Select Demo", list(demo_options.keys()))
    
    if st.sidebar.button("Run Demo"):
        with st.spinner("Analyzing demo voice sample..."):
            st.session_state.results = generate_demo_results(demo_options[selected_demo])
            st.session_state.analysis_complete = True
            st.session_state.demo_type = demo_options[selected_demo]
            st.rerun()
    
    st.markdown("## Upload Voice Recording")
    st.markdown("Upload a voice recording for mental health analysis:")
    
    uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "ogg"])
    
    if uploaded_file is not None and st.button("Analyze Voice"):
        with st.spinner("Analyzing voice recording..."):
            try:
                audio_bytes = uploaded_file.read()
                
                from vocalysis_clean import run_vocalysis_analysis
                
                results = run_vocalysis_analysis(
                    audio_data=audio_bytes,
                    model_type=model_type,
                    use_secure_storage=use_secure_storage
                )
                
                st.session_state.results = results
                st.session_state.analysis_complete = True
                st.session_state.demo_type = None
                st.rerun()
            except Exception as e:
                st.error(f"Error analyzing voice recording: {str(e)}")
    
    if st.session_state.analysis_complete and st.session_state.results:
        display_results(st.session_state.results)
    
    st.markdown("---")
    st.markdown("### About Vocalysis")
    st.write("""
        Vocalysis is an advanced voice analysis system that detects mental health indicators from speech patterns. 
        The system extracts audio features from voice recordings and uses machine learning to classify mental states 
        (Normal, Anxiety, Depression, Stress) with confidence scores.
        
        This system is for educational and research purposes only. It is not intended to provide medical diagnosis 
        or replace professional mental health evaluation.
    """)

if __name__ == "__main__":
    main()
