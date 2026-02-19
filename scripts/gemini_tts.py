#!/usr/bin/env python3
"""
Gemini Live API TTS Script
Uses Gemini Live API for text-to-speech
"""

import sys
import json
import requests
import os

API_KEY = "AIzaSyB24dZvCkIBV5FaxMvH6d3vBQjDLLfYbp4"

def gemini_tts(text, output_file="/tmp/gemini_tts_output.mp3"):
    """Generate TTS using Gemini Live API"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
    
    # Note: Gemini API doesn't have direct TTS endpoint
    # This is a placeholder - actual TTS would use a different API
    # For now, we'll use the chat completion and return text
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Please respond naturally to: {text}"
            }]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Extract text response
        if 'candidates' in result and len(result['candidates']) > 0:
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            return text_response
        return "No response from Gemini"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: gemini_tts.py 'Your text here'")
        sys.exit(1)
    
    text = sys.argv[1]
    result = gemini_tts(text)
    print(result)
