function Message({messageData, currentUser, recipientName}) {
    return (
        <div
            key={messageData["id"]}
            className={`max-w-[400px] p-1 mx-2 border flex flex-col ${
                currentUser["sub"] === messageData["owner"]
                    ? 'self-end bg-blue-100'
                    : 'self-start bg-gray-100'
            }`}
        >
            <p className="text-sm">
                {messageData["owner"] === currentUser["sub"] ? currentUser["name"] : recipientName}
            </p>
            <p className="text-sm max-w-[380px]">
                {messageData["content"]}
            </p>
            <div className="flex items-center justify-between space-x-2">
                <small className="text-gray-500 mt-2">
                    {new Date(messageData.timestamp).toLocaleDateString('default', {
                        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                    })}
                    {' '}
                    {new Date(messageData.timestamp).toLocaleTimeString('default', {
                        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false,
                    })}
                </small>
                <div>
                    {messageData["owner"] === currentUser["sub"] ? (
                        <small className="flex items-center mt-2">
                            {messageData["is_read"] ? (
                                <svg
                                    className="h-5 w-5 text-green-500"
                                    width="24"
                                    height="24"
                                    viewBox="0 0 24 24"
                                    strokeWidth="2" stroke="currentColor" fill="none" strokeLinecap="round"
                                    strokeLinejoin="round"
                                >
                                    <path stroke="none" d="M0 0h24v24H0z"/>
                                    <path d="M7 12l5 5l10 -10"/>
                                    <path d="M2 12l5 5m5 -5l5 -5"/>
                                </svg>
                            ) : (
                                <svg
                                    className="h-5 w-5 text-gray-400"
                                    width="24"
                                    height="24"
                                    viewBox="0 0 24 24"
                                    strokeWidth="2" stroke="currentColor" fill="none" strokeLinecap="round"
                                    strokeLinejoin="round"
                                >
                                    <path stroke="none" d="M0 0h24v24H0z"/>
                                    <path d="M5 12l5 5l10 -10"/>
                                </svg>
                            )
                            }
                        </small>
                    ) : (
                        <div></div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default Message;
