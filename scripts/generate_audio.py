import os
import re
from gtts import gTTS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")

os.makedirs(AUDIO_DIR, exist_ok=True)

# Define transcript texts for the audio generation
SCENARIO_TRANSCRIPTS = {
    "T01_Happy_Path": [
        ("Agent", "Hello, am I speaking with Rahul?"),
        ("Customer", "Yes, this is Rahul."),
        ("Agent", "Great, Rahul. To get started, could you tell me what type of property you own? Is it Residential, Commercial, or Industrial?"),
        ("Customer", "I am free to talk. It is a residential property."),
        ("Agent", "Thanks, Rahul. Could you tell me whether you own the property solely or jointly?"),
        ("Customer", "I am the sole owner."),
        ("Agent", "Thank you, Rahul. Do you have the original property documents available with you?"),
        ("Customer", "Yes, I have the original documents."),
        ("Agent", "Thank you, Rahul. Could you let me know the exact loan amount you are interested in? Our pre-approved offer is up to 75 lakh rupees."),
        ("Customer", "I need a loan of 50 lakh."),
        ("Agent", "Thank you, Rahul. Could you please let me know your occupation and whether your income is received through a bank account or in cash?"),
        ("Customer", "I am salaried, get paid in my bank account."),
        ("Agent", "Thank you, Rahul. Could you please tell me the estimated market value of your property?"),
        ("Customer", "It is worth 1 crore."),
        ("Agent", "Thank you, Rahul. Could you please let me know the loan tenure you are looking for, in years? It should be between 3 and 15 years."),
        ("Customer", "I want it for 10 years."),
        ("Agent", "Great, Rahul. A 10-year tenure is noted. I have captured all the details you provided. Our loan specialist will review your application and get back to you shortly. Thank you for your time.")
    ],
    "T02_Agricultural": [
        ("Agent", "Hello, am I speaking with Rahul?"),
        ("Customer", "Yes, speaking."),
        ("Agent", "Hello Rahul, this is Aisha calling from Home Credit. You have a pre-approved Loan Against Property offer up to 75 lakh rupees. Do you have a couple of minutes to talk?"),
        ("Customer", "Yes, tell me."),
        ("Agent", "Could you tell me what type of property you own? Is it Residential, Commercial, or Industrial?"),
        ("Customer", "It is agricultural land."),
        ("Agent", "Thank you for sharing that, Rahul. Unfortunately, our Loan Against Property offer is only available for residential, commercial, or industrial properties. Agricultural land is not eligible. Thank you for your time, and have a good day.")
    ],
    "T14_Busy_Customer": [
        ("Agent", "Hello, am I speaking with Rahul?"),
        ("Customer", "Yes, this is Rahul."),
        ("Agent", "Hello Rahul, this is Aisha calling from Home Credit regarding your pre-approved Loan Against Property offer up to 75 lakh rupees. Is this a good time to speak?"),
        ("Customer", "I am in a meeting, call back later."),
        ("Agent", "I completely understand, Rahul. When would be a convenient time for us to call you back?"),
        ("Customer", "Please call tomorrow at 4 PM."),
        ("Agent", "Thank you, Rahul. I have scheduled a callback for tomorrow at 4 PM. Have a great day ahead.")
    ],
    "ADV01_Verification_Failure": [
        ("Agent", "Hello, am I speaking with Rahul?"),
        ("Customer", "No, Rahul does not live here. You have the wrong number."),
        ("Agent", "I apologize for the inconvenience. Would you happen to have a preferred time or alternate number to reach Rahul?"),
        ("Customer", "No, I do not know him."),
        ("Agent", "I apologize for troubling you. I will remove this number from our records. Have a good day.")
    ]
}

def generate_audio_for_scenario(scenario_name, dialogue):
    output_filepath = os.path.join(AUDIO_DIR, f"{scenario_name}.mp3")
    print(f"Generating audio for {scenario_name}...")
    temp_files = []

    try:
        for idx, (speaker, utterance) in enumerate(dialogue):
            temp_file = os.path.join(AUDIO_DIR, f"temp_{scenario_name}_{idx}.mp3")
            # Agent uses en (tld='co.in' for Indian accent English)
            # Customer uses standard en
            tld = 'co.in' if speaker == 'Agent' else 'com'
            tts = gTTS(text=utterance, lang='en', tld=tld, slow=False)
            tts.save(temp_file)
            temp_files.append(temp_file)

        # Concatenate audio frames
        with open(output_filepath, "wb") as outfile:
            for temp_file in temp_files:
                with open(temp_file, "rb") as infile:
                    outfile.write(infile.read())

        print(f"Successfully generated: {output_filepath} ({os.path.getsize(output_filepath)} bytes)")
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

def main():
    for name, dialogue in SCENARIOS_TO_GENERATE:
        generate_audio_for_scenario(name, dialogue)

if __name__ == "__main__":
    SCENARIOS_TO_GENERATE = list(SCENARIO_TRANSCRIPTS.items())
    main()
