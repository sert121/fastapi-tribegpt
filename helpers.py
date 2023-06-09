
import openai
from llama_index import  download_loader
from urllib.parse import urlparse
from dotenv import load_dotenv
import os 
import json

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")
bsl_loader = BeautifulSoupWebReader()

def _chat_openai(prompt, system_text="",token_limit=2048):
    """ construct an openai gpt3.5/gpt4 call

    Args:
        prompt (str): input_prompt
        system_text (str, optional): system text. Defaults to "".
        token_limit (int, optional): token limit for the api call. Defaults to 2048.

    Returns:
        output (str):  output text
    """
    chat_query = [{"role":"system", "content": system_text}, {"role":"user", "content": prompt}]

    response = openai.ChatCompletion.create(
            messages=chat_query,    
            # model="gpt-4-0314",
            model = "gpt-3.5-turbo",
            temperature=0,
            max_tokens=token_limit,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=' ;'
            )
    output = response["choices"][0]["message"]["content"]
    return output

def _scrape_website(web_url:str):
    """
    Scrape the website for the company description

    Args:
        web_url (str): URL of the website

    Returns:
        str: Company description/summary
    """

    # BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")
    
    documents = bsl_loader.load_data(urls=[web_url])
    text_description = documents[0].text

    print(text_description)

    summarize_prompt = f'''
    Summarize the company details from the given website context. Tell us more about the company itself.
    Make a detailed summary.

    Website Context:
    {text_description[:3000]}
    '''
    system_text = "You are great at summarizing relevant information from website page data."
    chat_query = [{"role":"system", "content": system_text}, {"role":"user", "content": summarize_prompt}]
    
    web_summary = openai.ChatCompletion.create(
            messages=chat_query,    
            # model="gpt-4-0314",
            model = "gpt-3.5-turbo",
            temperature=0,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=' ;'
            )    
    web_summary = web_summary["choices"][0]["message"]["content"]
    web_summary = str(web_summary)

    print("-------------------")
    print(web_summary)
    return web_summary


def generate_roadmap(idea:str):
    """
    Generate a roadmap for the idea selected by the user

    Args:
        idea (str): Idea selected by the user

    Returns:
        roadmap(str) : Roadmap for the idea
    """
    prompt = f"""
    Create a three phase PRD and roadmap for the following product: {idea}
    Each phase has its own roadmap without dates. 
    Write for a well-informed, professional audience. Be detailed and lengthy. Think step-by-step. 
    Return in JSON format, with each phase as a key.
    """+"""
    JSON Format example:
    {
    "roadmap": {
        "Phase 1": {
        "Objective": "Develop a Minimum Viable Product (MVP) for the Predictive Maintenance solution using AI algorithms to analyze sensor data and predict equipment failure.",
        "Roadmap": [
            "1.1 Conduct market research to identify target industries and customers for the Predictive Maintenance solution.",
            "1.2 Define the scope of the MVP, including the types of equipment and sensors to be supported, and the specific AI algorithms to be used for analysis.",
            "1.3 Assemble a cross-functional team, including data scientists, engineers, and domain experts, to design and develop the MVP.",
            "1.4 Collect and preprocess historical sensor data from target industries to train and validate the AI algorithms.",
            "1.5 Develop a user-friendly interface for customers to input their equipment and sensor data, and receive predictions on equipment failure.",
            "1.6 Implement a secure and scalable cloud-based infrastructure to support the processing and storage of large volumes of sensor data.",
            "1.7 Test the MVP with a small group of pilot customers, and gather feedback on its performance and usability.",
            "1.8 Refine the MVP based on customer feedback, and prepare for a wider launch."
         ]
        }, 
    }
    }
    """


    system_prompt = 'You are a Product manager with expertise in Machine Learning, Generative AI, and Business.'

    phases_text = _chat_openai(prompt, system_prompt)
    try:
        phases = json.loads(phases_text)
        return phases
    except:
        print("Error in loading...")
        return 'Internal Server Error, invalid JSON from gpt'

def generate_ideas(company_link:str):
    """
    Generate ideas for the company based on the company description

    Args:
        company_link (str): URL of the company website
    Returns:
        list : List of ideas generated by the GPT-3 model
    """
    company_description = _scrape_website(company_link)

    old_prompt = '''
    Given a summary of a business in any industry, provide exactly three suggestions on how  AI could be used to improve various aspects of its operations, tailored specifically for that business. 
    The AI improvement suggestions should be suitable for a professional audience, such as executives or those reporting to executives.
    Do not include an introduction or conclusion.
    Please respond with the 3 ideas in JSON format like this: {"idea_1_title": "IDEA 1 DESCRIPTION", "idea_2_title": "IDEA 2 DESCRIPTION", "idea_3_title": "IDEA 3 DESCRIPTION"}.
    Here is the provide summary of a specific business, which could be in any industry, for you to analyze and suggest AI improvements:
    {company_description}
    '''
    system_prompt = 'You are a really helpful product manager that understand company needs, and specialize in generative AI, so you can act as a good guide.'
    ideas = _chat_openai(prompt, system_prompt, 4048 - (len(prompt) + len(system_prompt)))

    return ideas

