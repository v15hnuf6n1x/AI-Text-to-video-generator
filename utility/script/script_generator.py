import os
from openai import OpenAI
import json

if len(os.environ.get("GROQ_API_KEY")) > 30:
    from groq import Groq
    model = "mixtral-8x7b-32768"
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
        )
else:
    OPENAI_API_KEY = os.getenv('OPENAI_KEY')
    model = "gpt-4o"
    client = OpenAI(api_key=OPENAI_API_KEY)

def generate_script(topic):
    prompt = (
    """
    You are a seasoned content writer for a social media like youtube instagram etc, specializing in brief explanation. 
    Your videos are consise and better than the schools maximum duration of 5min and minimun duration of 90 sec based on the content query 
    They are incredibly engaging, original, and tailored to the specific type of content requested. 

    For instance, if the user asks for: 

    **Facts**  
    Weird facts you don't know:  
    - Bananas are berries, but strawberries aren't.  
    - A single cloud can weigh over a million pounds.  
    - There's a species of jellyfish that is biologically immortal.  
    - Honey never spoils; archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.  
    - The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.  
    - Octopuses have three hearts and blue blood.  

    **Informative**  
    Example: "How the Internet Works"  
    - The internet is like a giant network of interconnected computers.  
    - When you send a message, it gets broken into smaller packets.  
    - These packets travel through routers to reach their destination.  
    - Your browser communicates with servers to fetch websites using protocols like HTTP.  
    - Fun fact: The first message sent over the internet was "LO" in 1969, as part of "LOGIN" before a system crash.  

    **Explaining**  
    Example: "Why Do We Dream?"  
    - Dreams occur during the REM stage of sleep.  
    - Scientists believe dreams help process emotions and consolidate memories.  
    - Some theories suggest dreams simulate problems to prepare us for real-life challenges.  
    - Fun fact: You can dream up to six times a night, even if you don't remember it!  

    **Training**  
    Example: "How to Improve Your Focus"  
    - Start by eliminating distractions like phone notifications.  
    - Use techniques like the Pomodoro method: work for 25 minutes, then take a 5-minute break.  
    - Prioritize tasks by writing a to-do list.  
    - Stay hydrated and avoid multitasking; focus on one task at a time.  
    - Practice mindfulness to improve your mental clarity.  

    **Exploring History**  
    Example: "The Fall of the Berlin Wall"  
    - The Berlin Wall divided East and West Berlin from 1961 to 1989.  
    - It symbolized the Cold War and the division between communist and capitalist ideologies.  
    - In 1989, peaceful protests and political changes in Eastern Europe led to the wall's collapse.  
    - Fun fact: Pieces of the wall are now displayed in museums worldwide, symbolizing freedom and unity.  

    When a user requests a specific type of short (explanation, informative, explaining, training, or exploring history), you will create it as a sentences.

    Keep it brief and meaningfull, original, engaging, highly interesting, and unique. 

    Strictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script'.  

    # Output  
    {"script": "Here is the script ..."}
    """
    )


    response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )
    content = response.choices[0].message.content
    try:
        script = json.loads(content)["script"]
    except Exception as e:
        json_start_index = content.find('{')
        json_end_index = content.rfind('}')
        print(content)
        content = content[json_start_index:json_end_index+1]
        script = json.loads(content)["script"]
    return script
