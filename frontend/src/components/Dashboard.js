import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import './Dashboard.css';

const UserDashboard = () => {
    const [user, setUser] = useState(null);
    const [testResults, setTestResults] = useState([]);
    const [showLinkPsychologist, setShowLinkPsychologist] = useState(false);
    const [psychologistCode, setPsychologistCode] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        fetchUserData();
        fetchTestResults();
    }, []);

    const fetchUserData = async () => {
        try {
            const response = await api.get('/users/me');
            setUser(response.data);
        } catch (error) {
            console.error('Error fetching user data:', error);
        }
    };

    const fetchTestResults = async () => {
        try {
            const response = await api.get('/tests/my-results');
            setTestResults(response.data);
        } catch (error) {
            console.error('Error fetching test results:', error);
        }
    };

    const handleStartTest = () => {
        navigate('/test');
    };

    const handleLinkPsychologist = async () => {
        try {
            await api.post('/psychologist/link', {
                psychologist_code: psychologistCode
            });
            alert('Психолог успешно привязан!');
            setShowLinkPsychologist(false);
            setPsychologistCode('');
            fetchUserData(); // Обновляем данные пользователя
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
                <section className="test-section">
                    <div className="test-card">
                        <h2>Культурно-свободный тест интеллекта Кеттелла</h2>
                        <p>Пройдите тест для оценки ваших интеллектуальных способностей</p>
                        <p className="test-info">≈ 30 минут • 50 вопросов • Без регистрации</p>
                        <button className="btn-primary" onClick={handleStartTest}>
                            Начать тест
                        </button>
                    </div>
                </section>

                <section className="results-section">
                    <h2>Мои результаты тестов</h2>
                    {testResults.length === 0 ? (
                        <div className="no-results">
                            <p>Вы еще не проходили тест</p>
                            <button className="btn-secondary" onClick={handleStartTest}>
                                Пройти первый тест
                            </button>
                        </div>
                    ) : (
                        <div className="results-table-container">
                            <table className="results-table">
                                <thead>
                                    <tr>
                                        <th>№</th>
                                        <th>Дата прохождения</th>
                                        <th>Сырой балл</th>
                                        <th>IQ</th>
                                        <th>Процентиль</th>
                                        <th>Интерпретация</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {testResults.map((result, index) => (
                                        <tr key={result.id}>
                                            <td>{testResults.length - index}</td>
                                            <td>
                                                {new Date(result.completed_at).toLocaleDateString('ru-RU')}
                                            </td>
                                            <td>{result.raw_score}</td>
                                            <td>
                                                <span className={`iq-badge iq-${getIQLevel(result.standard_score)}`}>
                                                    {result.standard_score}
                                                </span>
                                            </td>
                                            <td>
                                                <div className="percentile-bar">
                                                    <div 
                                                        className="percentile-fill"
                                                        style={{ width: `${result.percentile}%` }}
                                                    ></div>
                                                    <span>{result.percentile}%</span>
                                                </div>
                                            </td>
                                            <td className="interpretation">
                                                {result.interpretation}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
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

// Вспомогательная функция для определения уровня IQ
function getIQLevel(iq) {
    if (iq < 85) return 'low';
    if (iq < 100) return 'average';
    if (iq < 115) return 'high';
    return 'very-high';
}

export default UserDashboard;
