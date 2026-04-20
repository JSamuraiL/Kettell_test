import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = ({ setToken, setUser }) => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        date_of_birth: '',
        role: 'user',
        rememberMe: false
    });
    const [isLogin, setIsLogin] = useState(true);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
        setFormData({
            ...formData,
            [e.target.name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            let response;
            
            if (isLogin) {
                // Для логина используем form-data как ожидает FastAPI OAuth2
                const payload = new FormData();
                payload.append('username', formData.email);
                payload.append('password', formData.password);
                
                response = await axios.post(
                    `http://localhost:8000/login`,
                    payload,
                    {
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded'
                        }
                    }
                );
            } else {
                // Для регистрации используем JSON
                const requestData = {
                    email: formData.email,
                    password: formData.password,
                    full_name: formData.full_name || '',
                    date_of_birth: formData.role === 'user' ? formData.date_of_birth : null,
                    role: formData.role
                };
                
                response = await axios.post(
                    `http://localhost:8000/register`,
                    requestData,
                    {
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    }
                );
            }

            if (isLogin) {
                console.log('Response data:', response.data); // Для отладки
                
                const token = response.data.access_token;
                const userData = response.data.user;
                
                console.log('Token received:', token); // Для отладки
                
                // Сохраняем токен и данные пользователя
                localStorage.setItem('token', token);
                localStorage.setItem('user', JSON.stringify(userData));
                
                setToken(token);
                if (setUser) setUser(userData);
                
                // Небольшая задержка для гарантии сохранения
                setTimeout(() => {
                    navigate('/dashboard');
                }, 100);
            } else {
                setIsLogin(true);
                alert('Регистрация успешна! Теперь войдите в систему.');
                setFormData({
                    email: '',
                    password: '',
                    full_name: '',
                    date_of_birth: '',
                    role: 'user',
                    rememberMe: false
                });
            }
        } catch (error) {
            console.error('Auth error details:', error.response || error);
            const errorMessage = error.response?.data?.detail || 
                            error.response?.data?.message || 
                            'Ошибка аутентификации';
            alert(errorMessage);
        }
    };

    // Вычисляем максимальную дату (сегодня) для календаря
    const today = new Date().toISOString().split('T')[0];
    // Вычисляем минимальную дату (100 лет назад)
    const minDate = new Date();
    minDate.setFullYear(minDate.getFullYear() - 100);
    const minDateStr = minDate.toISOString().split('T')[0];

    return (
        <div className="split-login-container">
            {/* Левый блок */}
            <div className="left-panel">
                <div className="project-header">
                    <h1 className="project-title">Система пользовательского тестирования</h1>
                    <p className="project-subtitle">Объективная оценка интеллектуальных способностей</p>
                </div>
                
                <div className="infographic-container">
                    <div className="infographic">
                        <div className="infographic-item">
                            <div className="icon">🌍</div>
                            <h3>Культурная независимость</h3>
                            <p>Оценка биологически детерминированного интеллекта без влияния культурной среды</p>
                        </div>
                        <div className="infographic-item">
                            <div className="icon">🧩</div>
                            <h3>Двухфакторная модель</h3>
                            <p>Измерение флюидного (g1) и кристаллического (g2) интеллекта по теории Кеттелла</p>
                        </div>
                        <div className="infographic-item">
                            <div className="icon">⚡</div>
                            <h3>Флюидный интеллект</h3>
                            <p>Оценка врожденных способностей к логическим операциям и пространственному мышлению</p>
                        </div>
                        <div className="infographic-item">
                            <div className="icon">💎</div>
                            <h3>Кристаллический интеллект</h3>
                            <p>Измерение знаний и навыков, приобретенных через образование и опыт</p>
                        </div>
                    </div>
                </div>

                <div className="left-footer">
                    <p>© 2025 Культурно-свободный тест интеллекта Кеттелла</p>
                </div>
            </div>

            {/* Правый блок */}
            <div className="right-panel">
                <div className="login-form-wrapper">
                    <div className="login-form">
                        <div className="login-header">
                            <h2 className="login-title">
                                {isLogin ? 'Вход в систему' : 'Регистрация'}
                            </h2>
                            <p className="login-subtitle">
                                {isLogin 
                                    ? 'Войдите в свою учетную запись' 
                                    : 'Создайте новую учетную запись'
                                }
                            </p>
                        </div>

                        <form onSubmit={handleSubmit}>
                            {!isLogin && (
                                <>
                                    <div className="form-group">
                                        <label className="form-label">Полное имя *</label>
                                        <input
                                            type="text"
                                            name="full_name"
                                            className="form-input"
                                            placeholder="Иван Иванов"
                                            value={formData.full_name}
                                            onChange={handleChange}
                                            required
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Роль</label>
                                        <select
                                            name="role"
                                            className="form-input"
                                            value={formData.role}
                                            onChange={handleChange}
                                        >
                                            <option value="user">Пользователь</option>
                                            <option value="psychologist">Психолог</option>
                                        </select>
                                        <small className="form-hint">
                                            Выберите "Психолог", если вы специалист
                                        </small>
                                    </div>

                                    {formData.role === 'user' && (
                                        <div className="form-group">
                                            <label className="form-label">Дата рождения *</label>
                                            <input
                                                type="date"
                                                name="date_of_birth"
                                                className="form-input"
                                                value={formData.date_of_birth}
                                                onChange={handleChange}
                                                required={formData.role === 'user'}
                                                min={minDateStr}
                                                max={today}
                                                title="Выберите вашу дату рождения"
                                            />
                                        </div>
                                    )}
                                </>
                            )}
                            
                            <div className="form-group">
                                <label className="form-label">E-mail *</label>
                                <input
                                    type="email"
                                    name="email"
                                    className="form-input"
                                    placeholder="your@email.com"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Пароль *</label>
                                <input
                                    type="password"
                                    name="password"
                                    className="form-input"
                                    placeholder="Минимум 6 символов"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    minLength="6"
                                />
                                {!isLogin && (
                                    <small className="form-hint">
                                        Пароль должен содержать не менее 6 символов
                                    </small>
                                )}
                            </div>

                            {isLogin && (
                                <div className="form-options">
                                    <label className="remember-me">
                                        <input
                                            type="checkbox"
                                            name="rememberMe"
                                            className="checkbox"
                                            checked={formData.rememberMe}
                                            onChange={handleChange}
                                        />
                                        Запомнить меня
                                    </label>
                                    <a href="#forgot" className="forgot-password" onClick={(e) => {
                                        e.preventDefault();
                                        alert('Функция восстановления пароля временно недоступна');
                                    }}>
                                        Забыли пароль?
                                    </a>
                                </div>
                            )}

                            <button type="submit" className="login-button">
                                {isLogin ? 'Войти' : 'Зарегистрироваться'}
                            </button>
                        </form>

                        <div className="login-footer">
                            <div className="divider">
                                <span>или</span>
                            </div>
                            <button 
                                type="button" 
                                onClick={() => {
                                    setIsLogin(!isLogin);
                                    // Очищаем поля при переключении
                                    if (!isLogin) {
                                        setFormData({
                                            ...formData,
                                            full_name: '',
                                            date_of_birth: '',
                                            role: 'user'
                                        });
                                    }
                                }}
                                className="toggle-btn"
                            >
                                {isLogin 
                                    ? 'Нет учетной записи? Создайте её' 
                                    : 'Уже есть учетная запись? Войдите'
                                }
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
