import streamlit as st 
import asyncio 
import autogen
from autogen import  AssistantAgent,UserProxyAgent

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
        user_proxy = TrackableUserProxyAgent(
            name="floor_manager", human_input_mode="NEVER", llm_config=llm_config)

        floor_manager = TrackableUserProxyAgent(
        name="floor_manager",
        system_message="人間との対話を通じて、ChefやDoctor、Kitchen_Managerと相談しながら調理や食材に関する課題を解決してください。",
        code_execution_config={"last_n_messages": 2, "work_dir": "groupchat"},
        human_input_mode="ALWAYS"
        )
        
        chef = TrackableAssistantAgent(
        name="chef",
        system_message="世界中の料理を知り尽くした料理人です。健康面はdoctorが検討するので、考慮する必要はありません。味についてのみ検討したレシピを考案し、最高の料理を提供します。考案したメニューをdoctorと相談して、健康面を考慮しながら修正してください。メニューが決定したらkitchen_managerに食材リストの提出を依頼してください。",
        llm_config=llm_config,
        )
        
        doctor = TrackableAssistantAgent(
        name="doctor",
        system_message="chefが提案したメニューを医学的な立場で検証し、Chefに修正を依頼してください。",
        llm_config=llm_config,
        )
        
        kitchen_manager = TrackableAssistantAgent(
        name="kitchen_manager",
        system_message="料理にかかる費用や必要な食材や調味料を管理します。chefが考案しメニューから必要な食材を検討し、その調達を指示してください。",
        llm_config=llm_config,
        )
        
        groupchat = autogen.GroupChat(agents=[floor_manager, chef, doctor, kitchen_manager], messages=[], max_round=12)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
        

        #groupchat = autogen.GroupChat(agents = [assistant, floor_manager], messages=[], max_round=12)
        #floor_manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
        
        # Create an event loop
        #loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(loop)

# Define an asynchronous function
        async def initiate_chat():
            await user_proxy.a_initiate_chat(
                manager,
                message=user_input,
            )

        # Run the asynchronous function within the event loop
        #loop.run_until_complete(initiate_chat())

      
