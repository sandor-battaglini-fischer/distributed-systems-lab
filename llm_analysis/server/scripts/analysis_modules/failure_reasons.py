from openai import OpenAI
import os
import pandas as pd

def analyze_failure_reasons(df, query=None, history=None):
    """Analyze failure reasons based on incident data and user query"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Prepare the data context
    df['combined_text'] = df.apply(lambda x: f"""
    Title: {x['Incident_Title']}
    Impact Level: {x['incident_impact_level']}
    Provider: {x['provider']}
    Description: {x.get('investigating_description', '')} {x.get('identified_description', '')} 
    Resolution: {x.get('resolved_description', '')}
    Duration: {x['time_span']}
    """, axis=1)
    
    # Create a summary of the data
    total_incidents = len(df)
    providers = df['provider'].value_counts().to_dict()
    impact_levels = df['incident_impact_level'].value_counts().to_dict()
    
    data_context = f"""
    Dataset Context:
    - Total Incidents: {total_incidents}
    - Providers: {providers}
    - Impact Levels: {impact_levels}
    """
    
    # Prepare chat messages
    messages = [
        {
            "role": "system",
            "content": f"""You are an expert in analyzing technical incidents and failures. 
            You have access to a dataset of LLM service incidents with the following context:
            
            {data_context}
            
            Format your responses using markdown for better readability.
            Focus on providing specific insights backed by data.
            Be concise but informative.
            You can reference previous messages to maintain context."""
        }
    ]
    
    # Add chat history if provided
    if history:
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Add current query
    messages.append({
        "role": "user",
        "content": query
    })
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error in LLM analysis: {e}")
        return f"Error analyzing failures: {str(e)}"
