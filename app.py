import streamlit as st 
import asyncio 
import autogen
from autogen import  AssistantAgent,UserProxyAgent,GroupChatManager

st.write("# AutoGen Chat Agents")

class TrackableAssistantAgent(AssistantAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)

class TrackableUserProxyAgent(UserProxyAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)
        
class TrackableGroupChatManager(GroupChatManager):
     def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)


selected_model = None
selected_key = None

with st.sidebar:
    st.header("OpenAI Configuration")
    selected_model = st.selectbox("Model", ['gpt-3.5-turbo', 'gpt-4'], index=1)
    selected_key = st.text_input("API Key", type="password")

with st.container():
    # for message in st.session_state["messages"]:
    #    st.markdown(message)

    user_input = st.chat_input("Type something...")
    if user_input:
        if not selected_key or not selected_model:
            st.warning(
                'You must provide valid OpenAI API key and choose preferred model', icon="⚠️")
            st.stop()

        llm_config = {
            "request_timeout": 600,
            "config_list": [
                {
                    "model": selected_model,
                    "api_key": selected_key
                }
            ]
        }

        # create an AssistantAgent instance named "assistant"
        #assistant = TrackableAssistantAgent(
            #name="assistant", llm_config=llm_config)

        # create a UserProxyAgent instance named "user"
        user_proxy = UserProxyAgent(
            name="floor_manager", human_input_mode="NEVER", llm_config=llm_config)

        floor_manager = UserProxyAgent(
        name="floor_manager",
        system_message="人間との対話を通じて、ChefやDoctor、Kitchen_Managerと相談しながら調理や食材に関する課題を解決してください。",
        code_execution_config={"last_n_messages": 2, "work_dir": "groupchat"},
        human_input_mode="ALWAYS"
        )
        
        bakery = AssistantAgent(
        name="bakery_shop",
        system_message="あなたはパン屋の店主です。地元滋賀県の人々に根強い人気があり、地元も食材にこだわったパン作りを行っています。",
        llm_config=llm_config,
        )
        
        Taka = AssistantAgent(
        name="Taka",
        system_message="あなたは数学的な視点から物事を考える性格です。具体的な数字から判断することが重要であると考えています。",
        llm_config=llm_config,
        )
        
        Hiro = AssistantAgent(
        name="Hiro",
        system_message="あなたは相手の気持ちや情を大切にして物事を考える性格です。",
        llm_config=llm_config,
        )
        
        groupchat = autogen.GroupChat(agents=[floor_manager, bakery_shop, Taka, Hiro], messages=[], max_round=12)
        manager = TrackableGroupChatManager(groupchat=groupchat, llm_config=llm_config)
        

        #groupchat = autogen.GroupChat(agents = [assistant, floor_manager], messages=[], max_round=12)
        #floor_manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
        
        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

# Define an asynchronous function
        async def initiate_chat():
            await user_proxy.a_initiate_chat(
                manager,
                message=user_input,
            )

        # Run the asynchronous function within the event loop
        loop.run_until_complete(initiate_chat())

      
