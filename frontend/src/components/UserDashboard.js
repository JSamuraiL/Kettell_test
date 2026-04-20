import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import './Dashboard.css';

const UserDashboard = () => {
    const [user, setUser] = useState(null);
    const [availableTests, setAvailableTests] = useState([]); // Добавили для тестов
    const [showLinkPsychologist, setShowLinkPsychologist] = useState(false);
    const [psychologistCode, setPsychologistCode] = useState('');
    const navigate = useNavigate(); // Хук useNavigate должен быть внутри компонента!

    useEffect(() => {
        fetchUserData();
        fetchAvailableTests(); // Добавили вызов
    }, []);

    const fetchUserData = async () => {
        try {
            const response = await api.get('/users/me');
            setUser(response.data);
        } catch (error) {
            console.error('Error fetching user data:', error);
        }
    };

    // Новая функция для получения доступных тестов
    const fetchAvailableTests = async () => {
        try {
            const response = await api.get('/tests/available');
            setAvailableTests(response.data);
        } catch (error) {
            console.error('Error fetching available tests:', error);
        }
    };

    const handleStartTest = (testId) => {
        navigate(`/test/${testId}`);
    };

    const handleLinkPsychologist = async () => {
        try {
            let code = psychologistCode;
            if (code.toLowerCase().startsWith('psy-')) {
                code = code.split('-')[1];
            }
            
            await api.post('/psychologist/link', {
                psychologist_code: code.trim()
            });
            
            alert('Психолог успешно привязан!');
            setShowLinkPsychologist(false);
            setPsychologistCode('');
            fetchUserData();
        } catch (error) {
            alert(error.response?.data?.detail || 'Ошибка при привязке психолога');
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
    };

    if (!user) return <div className="loading">Загрузка...</div>;

    return (
        <div className="dashboard">
            <header className="dashboard-header">
                <div>
                    <h1>Добро пожаловать, {user.full_name || user.email}!</h1>
                    <p className="user-role">Пользователь</p>
                    {user.date_of_birth && (
                        <p className="user-age">
                            Возраст: {new Date().getFullYear() - new Date(user.date_of_birth).getFullYear()} лет
                        </p>
                    )}
                </div>
                <div className="header-actions">
                    {user.psychologist_id ? (
                        <span className="psychologist-linked">
                            ✓ Привязан к психологу
                        </span>
                    ) : (
                        <button 
                            className="btn-link"
                            onClick={() => setShowLinkPsychologist(true)}
                        >
                            Привязать психолога
                        </button>
                    )}
                    <button className="btn-logout" onClick={handleLogout}>
                        Выйти
                    </button>
                </div>
            </header>

            <main className="dashboard-main">
                <section className="available-tests">
                    <h2>Доступные тесты</h2>
                    {availableTests.length === 0 ? (
                        <div className="no-tests">
                            <p>Нет доступных тестов</p>
                        </div>
                    ) : (
                        <div className="tests-grid">
                            {availableTests.map(test => (
                                <div key={test.id} className="test-card-small">
                                    <div className="test-header-small">
                                        <h3>Тест {test.test_part}{test.test_number}</h3>
                                        <span className="test-time">{Math.floor(test.time_limit / 60)} мин</span>
                                    </div>
                                    <h4>{test.name}</h4>
                                    <p className="test-description-small">
                                        {test.instruction_text && test.instruction_text.length > 100 
                                            ? test.instruction_text.substring(0, 100) + '...' 
                                            : test.instruction_text}
                                    </p>
                                    <div className="test-stats-small">
                                        <span>{test.question_count} вопросов</span>
                                        <span>Часть {test.test_part}</span>
                                    </div>
                                    {test.completed ? (
                                        <div className="test-completed">Тест пройден</div>
                                    ) : (
                                        <button 
                                            className="btn-start-test-small"
                                            onClick={() => handleStartTest(test.id)}
                                        >
                                            Начать тест
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </section>

                <section className="results-section">
                    <h2>Результаты</h2>
                    <div className="no-results">
                        <p>Результаты доступны вашему психологу.</p>
                        <p className="hint">После прохождения теста свяжитесь с психологом для обсуждения.</p>
                    </div>
                </section>
            </main>

            {showLinkPsychologist && (
                <div className="modal-overlay">
                    <div className="modal">
                        <h3>Привязать психолога</h3>
                        <p>Введите код психолога или email для привязки</p>
                        <input
                            type="text"
                            placeholder="Код психолога или email"
                            value={psychologistCode}
                            onChange={(e) => setPsychologistCode(e.target.value)}
                            className="modal-input"
                        />
                        <div className="modal-actions">
                            <button 
                                className="btn-secondary"
                                onClick={() => setShowLinkPsychologist(false)}
                            >
                                Отмена
                            </button>
                            <button 
                                className="btn-primary"
                                onClick={handleLinkPsychologist}
                            >
                                Привязать
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserDashboard;
