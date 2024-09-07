import streamlit as st
from backend import start_producers
import json
def start():
    
    if 'data' not in st.session_state:
        st.session_state.data = {
            "subreddit": [],
            "limit": 100,
            "timeFrame": 10,
            "sort": "top",
            "streamIntreval": 10,
            "sentimentKeyWord": [],
        }

    st.header("Configure Analysis",divider="blue")
    data = st.session_state.data
    if st.button("Update Data") or True:
        with st.container():
                st.write("")
                st.json(st.session_state.data)

    with st.container():
            
            subreddit = st.text_input("Enter Subreddit", value="")
            col1,col2,col3 = st.columns([1,1,1])

            with col1:
                if st.button("Add Subreddit"):
                    if subreddit and subreddit not in data["subreddit"]:
                        data["subreddit"].append(subreddit)
                        st.session_state.data = data
            with col2:
                if st.button("Remove Subreddit"):
                    data["subreddit"].remove(subreddit)
                    st.session_state.data = data

            with col3:
                if st.button("Clear Subreddit"):
                    data["subreddit"] = []
                    st.session_state.data = data

    with st.container():
            keyword = st.text_input("Enter Keyword", value="")
            col1,col2,col3 = st.columns([1,1,1])

            with col1:
                if st.button("Add Keyword"):
                    if keyword and keyword not in data["subreddit"]:
                        data["sentimentKeyWord"].append(keyword)
                        st.session_state.data = data

            with col2:
                if st.button("Remove Keyword"):
                    data["subreddit"].pop(keyword)
                    st.session_state.data = data
            with col3:
                if st.button("Clear Keyword"):
                    data["subreddit"] = []
                    st.session_state.data = data
     
    with st.container():
        data["limit"] = st.number_input("Limit", value=data["limit"])
        data["timeFrame"] = st.number_input("Time Frame (mins)", value=data["timeFrame"])
        data["streamIntreval"] = st.number_input("Stream Intreval (mins)", value=data["streamIntreval"])
        data["sort"] = st.selectbox("Sort", ["top", "hot", "new", "controversial", "rising"])
        st.session_state.data = data   

        if st.button("Submit"):
             print("Starting producers")
             start_producers(st.session_state.data)


if __name__ == '__main__':
    st.title('Reddit Analysis')
    page = st.sidebar.radio("Navigation", ("Configure", "Analysis"))
    
    if page =="Configure":
        start()
        pass
    elif page =="Analysis":
        pass