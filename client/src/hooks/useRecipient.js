import { useLocation } from 'react-router-dom';

export function useRecipient() {
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const recipientName = queryParams.get('recipient_name');
    const recipientId = queryParams.get('id');

    return {recipientId, recipientName};
}
