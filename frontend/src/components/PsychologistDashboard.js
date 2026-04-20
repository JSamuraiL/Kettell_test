import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import './Dashboard.css';

const PsychologistDashboard = () => {
    const [user, setUser] = useState(null);
    const [patients, setPatients] = useState([]);
    const [selectedPatient, setSelectedPatient] = useState(null);
    const [patientResults, setPatientResults] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetchUserData();
        fetchPatients();
    }, []);

    const fetchUserData = async () => {
        try {
            const response = await api.get('/users/me');
            setUser(response.data);
        } catch (error) {
            console.error('Error fetching user data:', error);
        }
    };

    const fetchPatients = async () => {
        try {
            const response = await api.get('/psychologist/patients');
            setPatients(response.data);
        } catch (error) {
            console.error('Error fetching patients:', error);
        }
    };

    const fetchPatientResults = async (patientId) => {
        try {
            const response = await api.get(`/psychologist/patient/${patientId}/results`);
            setPatientResults(response.data);
            setSelectedPatient(patientId);
        } catch (error) {
            console.error('Error fetching patient results:', error);
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
                    <p className="user-role">Психолог</p>
                    <p className="psychologist-code">Ваш код: PSY-{user.id}</p>
                </div>
                <button className="btn-logout" onClick={handleLogout}>
                    Выйти
                </button>
            </header>

            <main className="dashboard-main">
                <div className="psychologist-layout">
                    <section className="patients-section">
                        <h2>Мои пациенты ({patients.length})</h2>
                        <div className="patients-list">
                            {patients.length === 0 ? (
                                <div className="no-patients">
                                    <p>У вас еще нет привязанных пациентов</p>
                                    <p className="hint">Поделитесь своим кодом с пациентами: PSY-{user.id}</p>
                                </div>
                            ) : (
                                patients.map(patient => (
                                    <div 
                                        key={patient.id}
                                        className={`patient-card ${selectedPatient === patient.id ? 'selected' : ''}`}
                                        onClick={() => fetchPatientResults(patient.id)}
                                    >
                                        <div className="patient-info">
                                            <h4>{patient.full_name || 'Без имени'}</h4>
                                            <p>{patient.email}</p>
                                        </div>
                                        <div className="patient-stats">
                                            <span className="test-count">
                                                Тестов: {patient.test_count}
                                            </span>
                                            {patient.last_test_date && (
                                                <span className="last-test">
                                                    Последний: {new Date(patient.last_test_date).toLocaleDateString('ru-RU')}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </section>

                    <section className="results-section">
                        <h2>
                            {selectedPatient 
                                ? `Результаты пациента: ${patients.find(p => p.id === selectedPatient)?.full_name || 'Неизвестно'}`
                                : 'Выберите пациента для просмотра результатов'
                            }
                        </h2>
                        
                        {selectedPatient && patientResults.length > 0 ? (
                            <div className="detailed-results">
                                {patientResults.map(result => (
                                    <div key={result.id} className="result-card">
                                        <div className="result-header">
                                            <span className="test-date">
                                                Тестирование завершено {new Date(result.completed_at).toLocaleDateString('ru-RU')}
                                            </span>
                                            <span className="test-type">Полное тестирование (8 тестов)</span>
                                        </div>
                                        
                                        <div className="result-metrics">
                                            <div className="metric">
                                                <label>Общий сырой балл</label>
                                                <span className="value">{result.total_raw_score || 0}</span>
                                            </div>
                                            <div className="metric">
                                                <label>IQ</label>
                                                <span className={`value iq-${getIQLevel(result.standard_score)}`}>
                                                    {result.standard_score || 'Не рассчитан'}
                                                </span>
                                            </div>
                                            <div className="metric">
                                                <label>Процентиль</label>
                                                <span className="value">{result.percentile || 'Не рассчитан'}%</span>
                                            </div>
                                            <div className="metric">
                                                <label>Возрастная группа</label>
                                                <span className="value">{result.age_group}</span>
                                            </div>
                                        </div>
                                        
                                        {result.interpretation && (
                                            <div className="result-interpretation">
                                                <h4>Интерпретация</h4>
                                                <p>{result.interpretation}</p>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ) : selectedPatient ? (
                            <div className="no-results">
                                <p>У этого пациента еще нет результатов тестирования. Пациент должен пройти все 8 тестов для получения общего результата.</p>
                            </div>
                        ) : null}
                    </section>
                </div>
            </main>
        </div>
    );
};

function getIQLevel(iq) {
    if (iq < 85) return 'low';
    if (iq < 100) return 'average';
    if (iq < 115) return 'high';
    return 'very-high';
}

export default PsychologistDashboard;
