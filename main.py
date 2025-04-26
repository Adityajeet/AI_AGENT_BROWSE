import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI  # Updated import
from browser_use import Agent, Browser

load_dotenv() 

test_input = {
    "url": "https://www.farmley.com/account/login?return_url=%2Faccount",
    "test_case": {
        "steps": [
            "Click on the 'Sign in' button " ,
            "Enter email as 'give_your_email'",
            "Enter password as 'give_your_password'",
            "Click on the 'Log in' or 'Sign in' button"
        ],
        "expected_output": "User should see 'My account' page. This page would have a url 'https://www.farmley.com/account'"
    }
}

def build_prompt(url, test_case):
    steps_text = "\n".join(f"- {step}" for step in test_case["steps"])
    return f"""
### LLM-based Website Test Execution Task

**Objective:** Follow a sequence of instructions on the website {url}, and validate if the final page or state matches the expected outcome.

STRICT INSTRUCTIONS:
    1. NEVER mark a step as complete unless ALL sub-actions are done.
    2. If any action fails (e.g., password field missing), return FAIL.
    3. Confirm visibility of ALL required fields before proceeding.

**Instructions:**

1. Visit the website: {url}
2. Execute the following steps:
{steps_text}
3.If password field says "Please fill out this field", re-execute {steps_text} 
  Else move to next step

4. Final Validation:
After successfully logging it, Check if the final page or visible DOM contains the following expected outcome:

**Expected:** {test_case['expected_output']}

5. Return a JSON with:
- status: "PASS" or "FAIL"
- observed_output: What was actually found
- explanation: Brief explanation
Ensure each step is executed sequentially and robustly. If an element is not found, retry with an alternate method or selector.
"""

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")  

browser = Browser()

agent = Agent(
    task=build_prompt(test_input["url"], test_input["test_case"]),
    llm=llm, 
    browser=browser,
)

async def main():
    result = await agent.run()
    print("\n=== Test Result ===")
    print(result)
    input('Press Enter to close the browser...')
    await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
