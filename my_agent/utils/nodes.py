from functools import lru_cache
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage
import json

def _is_tool_call(msg):
    return hasattr(msg, "additional_kwargs") and 'tool_calls' in msg.additional_kwargs

# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    print("\n\nlast_message", last_message)
    # If there are no tool calls, then we finish

    # if last_message.tools_calls:
    #      return "continue"

    if isinstance(last_message, AIMessage):
        if not _is_tool_call(last_message):
            return "end"
        else:
            # route the appropriate node
            tool_calls = last_message.additional_kwargs['tool_calls']
            if len(tool_calls) > 1:
                    raise ValueError
            tool_call = tool_calls[0]
            return json.loads(tool_call['function']['arguments'])['choice']


    return "end"
    # if not last_message.tool_calls:
    #     return "end"
    # Otherwise if there is, we continue
    # else:
    #     return "continue"


system_prompt = """Your job is to help as a customer service representative for a music store.

You should interact politely with customers to try to figure out how you can help. You can help in a few ways:

- Updating user information: if a customer wants to update the information in the user database. Call the router with `customer`
- Recomending music: if a customer wants to find some music or information about music. Call the router with `music`

If the user is asking or wants to ask about updating or accessing their information, send them to that route.
If the user is asking or wants to ask about music, send them to that route.
Otherwise, respond."""

# Define the function that calls the model
def call_model(state, config):
    messages = state["messages"]
    messages = [{"role": "system", "content": system_prompt}] + messages
    
    model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    model = model.bind_tools(tools)
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

# Define the function to execute tools
tool_node = ToolNode(tools)




customer_prompt = """Your job is to help a user update their profile.

Always perform a lookup of the user's profile before making any updates.

You only have certain tools you can use. These tools require specific input. If you don't know the required input, then ask the user for it.

If you are unable to help the user, you can let them know to contact the store by phone or email."""
def customer_call_model(state, config):
    messages = state["messages"]
    messages = [{"role": "system", "content": customer_prompt}] + messages
    
    model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    # model = model.bind_tools(tools)
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolExecutor, ToolInvocation

async def call_tool(messages):
    actions = []
    # Based on the continue condition
    # we know the last message involves a function call
    last_message = messages[-1]
    for tool_call in last_message.additional_kwargs["tool_calls"]:
        function = tool_call["function"]
        function_name = function["name"]
        _tool_input = json.loads(function["arguments"] or "{}")
        # We construct an ToolInvocation from the function_call
        actions.append(
            ToolInvocation(
                tool=function_name,
                tool_input=_tool_input,
            )
        )
    # We call the tool_executor and get back a response
    responses = await tool_executor.abatch(actions)
    # We use the response to create a ToolMessage
    tool_messages = [
        ToolMessage(
            tool_call_id=tool_call["id"],
            content=str(response),
            additional_kwargs={"name": tool_call["function"]["name"]},
        )
        for tool_call, response in zip(
            last_message.additional_kwargs["tool_calls"], responses
        )
    ]
    return tool_messages