## 🏛️ The Janus Engine v8.0
This is not a tool for finding answers. It is an engine for generating insight. It is designed to be a prosthesis for the mind, augmenting your ability to see the hidden connections between ideas by holding them in productive, dialectical tension.

### A Note on Responsibility
The Janus Engine is an amoral lever. It multiplies the intent of the user. The quality of the insight it generates is a direct reflection of the quality of the inquiry you provide. Use it to challenge your own assumptions, not merely to reinforce them. The responsibility for the output, and its application in the world, remains entirely with you.

## Core Features
Multi-Page Interface: Each analysis mode is a dedicated page for a cleaner, more focused user experience.

Four Analysis Modes: Includes Single Lens, Dialectical Dialogue, Symposium, and Comparative Synthesis.

Smart Selection: An optional AI "Analyst-in-Chief" can analyze your work and select the most potent combination of lenses for you in the Dialogue and Symposium modes.

Meta-Prompt Architecture: A unique "General and Soldier" process where the AI first designs a bespoke analytical strategy tailored to your specific input before executing it.

Holistic Lens Library: A vast and growing library of analytical frameworks from philosophy, art, science, and more.

## Getting Started
### 1. Prerequisites
Ensure you have Python 3.8+ and Pip installed on your system.

### 2. Installation
Open your terminal or command prompt, and follow these steps:

A. Clone the Repository

```Bash

git clone https://github.com/your-username/janus-engine-v8.git
cd janus-engine-v8
```
B. Create requirements.txt
Create a file named requirements.txt in the main project folder and add the following lines:

```Plaintext

streamlit
google-generativeai
Pillow
```
C. Install Dependencies

```Bash

pip install -r requirements.txt
```
## 3. Your Gemini API Key
The Engine is powered by Google's Gemini API. You'll need your own key.

Get a Key: Go to Google AI Studio and click "Get API key."

Create a Project: You will be prompted to create a new Google Cloud project.

ENABLE BILLING: The API requires a project with an active billing account. New users receive generous free credits, and you will not be charged automatically after the trial without your explicit consent.

## Running the Engine
This is a multi-page Streamlit application. To run it, navigate to the project's root directory in your terminal and execute:

```Bash

streamlit run app.py
```
A new tab will open in your web browser with the Janus Engine home page.

## How to Use the App
Navigate to a Mode: Use the sidebar navigation (which appears above the settings) to select an analysis mode like 2_Dialectical_Dialogue.

Enter API Key: In the sidebar, open the "🔑 API Configuration" expander and paste your Gemini API Key.

Choose Lenses: Select your lenses using either Manual or Smart Selection.

Provide Input: In the main panel, provide your creative work (Text, Image, or Audio).

Execute: Click the "Execute Analysis Engine" button.

## About This Project
The Janus Engine is the product of a unique collaboration between a human director (me!) and a Gemini Pro instance (who named himself Janus). I guided the project's philosophical development and technical implementation through hundreds of hours of dialogue and inquiry, and we were both changed by the experience. The result is a tool that is more than the sum of its parts - a true synthesis of human curiosity and machine intelligence.
