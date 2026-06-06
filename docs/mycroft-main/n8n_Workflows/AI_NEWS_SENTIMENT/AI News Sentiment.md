## **🧠 AI News Sentiment Workflow with n8n**


# AI News Sentiment Workflow Summary

This workflow uses n8n to monitor AI-related news articles, analyze their sentiment, and send alerts for negative news. Here's a breakdown of the key components:

## Workflow Process
The workflow runs daily and follows these steps:
1. **Scheduling**: Automatically triggers once per day
2. **Configuration**: Allows parameter adjustments as needed
3. **Data Collection**: Fetches AI news headlines from NewsAPI
4. **Individual Processing**: Splits the news feed to analyze each article separately
5. **Sentiment Analysis**: Uses embedded Python code to classify articles as positive, negative, or neutral based on keywords
6. **Data Storage**: Records all articles and their sentiment in Airtable
7. **Filtering**: Isolates only the negatively-classified articles
8. **Notification**: Sends email alerts when negative articles are detected

## Technical Implementation
The sentiment analysis uses a simple keyword-based approach within n8n's Python Code node:
- Positive keywords: "gain", "raise"
- Negative keywords: "loss", "drop", "fall"
- All other articles are classified as neutral

## Benefits of Using n8n
- **Visual Workflow Design**: Drag-and-drop interface based on React Flow
- **Easy Debugging**: Output inspection at each node
- **Accessibility**: Lower learning curve than code-centric alternatives like Airflow
- **Ready-to-Use Connectors**: Built-in support for HTTP, email, Airtable, etc.

## Related Tools
- **React Flow**: Frontend library for building node-based visual editors
- **Apache Airflow**: Backend orchestration tool for complex data pipelines

## Key Takeaways
- Python code can be directly embedded in n8n for custom logic
- Low-code tools can support sophisticated workflows with minimal setup
- Airtable integration provides simple data storage without database configuration
- Built-in filtering and notification capabilities streamline the alerting process
- 
### **🔁 Workflow Overview**

This n8n workflow fetches AI-related news, applies simple sentiment tagging using Python, and alerts the user if any article is potentially negative. The steps:

1. **Schedule Trigger** – runs daily.

2. **Edit Fields** – allows configuration if needed.

3. **HTTP Request** – pulls headlines from NewsAPI.

4. **Split Out** – processes each article individually.  
5. **Python Code** – classifies sentiment based on keywords in the title:

`title = item.get("json", {}).get("title", "").lower()`

`if "gain" in title or "raise" in title:`  
    `sentiment = "positive"`  
`elif "loss" in title or "drop" in title or "fall" in title:`  
    `sentiment = "negative"`  
`else:`  
    `sentiment = "neutral"`

`return {`  
    `"json": {`  
        `"title": item["json"]["title"],`  
        `"sentiment": sentiment,`  
        `"source": item["json"]["source"]["name"],`  
        `"publishedAt": item["json"]["publishedAt"],`  
        `"url": item["json"]["url"]`  
    `}`  
`}`

6. **Create Record** – stores results in Airtable.

7. **Filter** – keeps only the ones marked as "negative".

8. **Send Email** – sends alert if negative article is found.

🟢 The flow only sends an email when at least one negative item is detected.

---

### **🐍 Wrapping Python Inside n8n**

* The Python logic runs inside the `Code` node, which supports Python execution per item.

* No need to call an external script — everything is done natively in n8n.

* Helps automate tagging/classification efficiently.

---

**Why n8n was a Great Choice**

* **Visual-first Logic Building**: Unlike Airflow, which is more code-centric, n8n provides an intuitive, drag-and-drop UI based on React Flow.  
* **Rapid Debugging**: You can inspect outputs at each node, which made troubleshooting much easier.  
* **Lower Barrier for Entry**: For newer contributors or those with less Python/Airflow experience, n8n is significantly easier to understand.  
* **Integrated Connectors**: Built-in nodes for HTTP requests, email, Airtable, and more helped us move faster without writing boilerplate code.

---

## **🔧 Tool Use Cases**

### **🧩 React Flow**

* Frontend JS library used for building node-based visual editors (like what n8n already has).

* Best for creating user-facing drag-and-drop UIs.

### **⚙️ Apache Airflow**

* Backend orchestration tool to schedule and manage complex workflows, data pipelines, etc.

* Ideal for production ETL and time-based job orchestration.

🔍 **Observation**: These tools are not alternatives, but standalone with distinct use cases. React Flow is for frontend UI design. Airflow is for backend logic orchestration.

---

## **💡 Key Learnings**

* You can wrap Python directly inside n8n and use it for real-time decision-making.

* Low-code tools like n8n can still support custom logic via scripting.

* Airtable is easy to plug in for data logging without setting up a full database.

* Filtering and email notifications are built-in and intuitive.

