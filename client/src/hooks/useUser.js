import {jwtDecode} from "jwt-decode";
import Cookies from "js-cookie";

export function useUser() {
    const token = Cookies.get("access_token");
    let currentUser;
    try {
        currentUser = jwtDecode(token);
    } catch {
        currentUser = null;
    }
    return [currentUser, token]
}