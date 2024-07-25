import { useState, useEffect } from "react";
import { Navigate, useLocation  } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";
import api from "../api";


function ProtectedRoute({ children }) {
    const [isAuthorized, setIsAuthorized] = useState(null);
    const location = useLocation();

    useEffect(() => {
        checkAuth().catch(() => setIsAuthorized(false))
    }, [])

    const getNewRefreshToken = async () => {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN);
        try {
            const res = await api.post("/auth/token/refresh/", {
                refresh: refreshToken,
            });
            if (res.status === 200) {
                localStorage.setItem(ACCESS_TOKEN, res.data.access)
                localStorage.setItem(REFRESH_TOKEN, res.data.refresh)
                setIsAuthorized(true)
            } else {
                setIsAuthorized(false)
            }
        } catch (error) {
            console.log(error);
            setIsAuthorized(false);
        }
    };

    const isAccessTokenExpired = async (token) => {
        const decodedToken = jwtDecode(token);
        const tokenExpirationTime = decodedToken.exp;
        const now = Date.now() / 1000;

        if (tokenExpirationTime < now) {
            await getNewRefreshToken();
        } else {
            setIsAuthorized(true);
        }        
    }

    const checkAuth = async () => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (!token) {
            setIsAuthorized(false);
            return;
        }
        
        await isAccessTokenExpired(token)

    };

    if (isAuthorized === null) {
        return <div>Check Authorization...</div>;
    }

    return isAuthorized ? children : <Navigate to="/login" state={{ from: location }} replace />;
}

export default ProtectedRoute;