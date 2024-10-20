import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import {ChatsAside} from '../components/ChatsAside'
import {ChatSection} from '../components/ChatSection'

function Chat() {

  const token = Cookies.get('access_token');


  const handleSendMessage = () => {
    console.log("send message")
  };

  const scrollToBottom = () => {
    chatBox.current.scrollTop = chatBox.current.scrollHeight;
  };

  return (
    <div className="flex box-content justify-center items-center h-screen min-w-[800px]">
      <div className="flex border-2 flex-row shadow-[0px_1px_6px_0px_rgba(0,0,0,0.2)] w-[800px] h-4/5 m-0 p-0">
        <ChatsAside />
        <ChatSection />
      </div>
    </div>
  );
}

export default Chat;
