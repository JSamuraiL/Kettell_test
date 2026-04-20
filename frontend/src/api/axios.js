import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Функция для получения токена
const getToken = () => {
    const token = localStorage.getItem('token');
    console.log('Retrieved token:', token ? token.substring(0, 30) + '...' : 'No token');
    return token;
};

// Интерцептор для добавления токена к запросам
api.interceptors.request.use(
    (config) => {
        const token = getToken();
        if (token) {
            console.log('Adding token to request for:', config.url);
            config.headers.Authorization = `Bearer ${token}`;
        } else {
            console.warn('No token found for request:', config.url);
        }
        return config;
    },
    (error) => {
        console.error('Request interceptor error:', error);
        return Promise.reject(error);
    }
);

// Интерцептор для обработки ошибок
api.interceptors.response.use(
    (response) => {
        console.log('Response received from:', response.config.url);
        return response;
    },
    (error) => {
        console.error('Response error:', {
            url: error.config?.url,
            status: error.response?.status,
            message: error.message
        });
        
        if (error.response?.status === 401) {
            console.log('401 Unauthorized, redirecting to login');
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default api;
