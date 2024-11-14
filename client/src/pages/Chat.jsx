import {ChatsAside} from '../components/ChatsAside'
import {ChatSection} from '../components/ChatSection'

function Chat() {

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
