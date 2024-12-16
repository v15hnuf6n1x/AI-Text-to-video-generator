from openai import OpenAI
import os
import json
import re
from datetime import datetime
from utility.utils import log_response,LOG_TYPE_GPT

if len(os.environ.get("GROQ_API_KEY")) > 30:
    from groq import Groq
    model = "llama3-70b-8192"
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
        )
else:
    model = "gpt-4o"
    OPENAI_API_KEY = os.environ.get('OPENAI_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)

log_directory = ".logs/gpt_logs"

prompt = prompt = prompt = """# Instructions

Given the following video script and timed captions, your task is to extract **three visually rich and dynamic keywords** for each time segment. These keywords will help search for background videos that bring the captions to life.

### Key Requirements:
1. **Visual Creativity**: Choose keywords that evoke vivid imagery. Instead of generic terms like "car" or "dog," opt for "sleek sports car" or "golden retriever running."
2. **Context-Aware**: If a caption is vague or general, analyze the next one for better context.
3. **Split Complex Captions**: If a time frame contains multiple ideas, split it into smaller segments with keywords for each. Ensure time segments are consecutive.
4. **Engaging Descriptions**: Use synonyms or related terms to make the keywords dynamic. If a keyword is just one word, expand it to a short phrase for richer visual meaning.
5. **Strict Timing**: Ensure that each segment spans 2-4 seconds and covers the entire video without overlaps.

### Examples:
- For the caption, *"The cheetah is the fastest land animal, capable of running at speeds up to 75 mph"*, use:
  - ["cheetah sprinting", "fastest animal", "blazing speed"].
- For the caption, *"The Great Wall of China is one of the most iconic landmarks in the world"*, use:
  - ["Great Wall sunset", "historic landmark", "China aerial view"].

### Output Format:
Your output should be in a strict JSON format, as follows:
[
    [[t1, t2], ["keyword1", "keyword2", "keyword3"]],
    [[t2, t3], ["keyword4", "keyword5", "keyword6"]],
    ...
]

### Special Notes:
- Always depict visually concrete scenes.
- Avoid abstract terms like *emotional moment* (BAD). Instead, choose *crying child* (GOOD).
- Be concise and ensure each keyword captures maximum visual impact.

Let’s make your output visually stunning and perfectly aligned with the captions!
"""



def fix_json(json_str):
    # Replace typographical apostrophes with straight quotes
    json_str = json_str.replace("’", "'")
    # Replace any incorrect quotes (e.g., mixed single and double quotes)
    json_str = json_str.replace("“", "\"").replace("”", "\"").replace("‘", "\"").replace("’", "\"")
    # Add escaping for quotes within the strings
    json_str = json_str.replace('"you didn"t"', '"you didn\'t"')
    return json_str

def getVideoSearchQueriesTimed(script,captions_timed):
    end = captions_timed[-1][0][1]
    try:
        
        out = [[[0,0],""]]
        while out[-1][0][1] != end:
            content = call_OpenAI(script,captions_timed).replace("'",'"')
            try:
                out = json.loads(content)
            except Exception as e:
                print("content: \n", content, "\n\n")
                print(e)
                content = fix_json(content.replace("```json", "").replace("```", ""))
                out = json.loads(content)
        return out
    except Exception as e:
        print("error in response",e)
   
    return None

def call_OpenAI(script,captions_timed):
    user_content = """Script: {}
Timed Captions:{}
""".format(script,"".join(map(str,captions_timed)))
    print("Content", user_content)
    
    response = client.chat.completions.create(
        model= model,
        temperature=1,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]
    )
    
    text = response.choices[0].message.content.strip()
    text = re.sub('\s+', ' ', text)
    print("Text", text)
    log_response(LOG_TYPE_GPT,script,text)
    return text

def merge_empty_intervals(segments):
    merged = []
    i = 0
    while i < len(segments):
        interval, url = segments[i]
        if url is None:
            # Find consecutive None intervals
            j = i + 1
            while j < len(segments) and segments[j][1] is None:
                j += 1
            
            # Merge consecutive None intervals with the previous valid URL
            if i > 0:
                prev_interval, prev_url = merged[-1]
                if prev_url is not None and prev_interval[1] == interval[0]:
                    merged[-1] = [[prev_interval[0], segments[j-1][0][1]], prev_url]
                else:
                    merged.append([interval, prev_url])
            else:
                merged.append([interval, None])
            
            i = j
        else:
            merged.append([interval, url])
            i += 1
    
    return merged
