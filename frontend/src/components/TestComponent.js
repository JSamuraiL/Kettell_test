import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import './TestComponent.css';

const TestComponent = () => {
    const [questions, setQuestions] = useState([]);
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [answers, setAnswers] = useState([]);
    const [age, setAge] = useState('');
    const [testStarted, setTestStarted] = useState(false);
    const [timeLeft, setTimeLeft] = useState(1800); // 30 минут
    const navigate = useNavigate();

    // Загружаем вопросы теста (заглушка)
    useEffect(() => {
        const loadQuestions = () => {
            // В реальном приложении здесь запрос к API
            const mockQuestions = Array.from({ length: 50 }, (_, i) => ({
                id: i + 1,
                type: 'matrix',
                question: `Найдите недостающий элемент в матрице ${i + 1}`,
                options: ['A', 'B', 'C', 'D', 'E'],
                image: `/images/matrix-${(i % 5) + 1}.png`,
                correctAnswer: 'C' // только для демо, в реальности на бэкенде
            }));
            setQuestions(mockQuestions);
        };

        loadQuestions();
    }, []);

    // Таймер
    useEffect(() => {
        if (!testStarted || timeLeft <= 0) return;

        const timer = setInterval(() => {
            setTimeLeft(prev => prev - 1);
        }, 1000);

        return () => clearInterval(timer);
    }, [testStarted, timeLeft]);

    const handleStartTest = () => {
        if (!age || age < 16 || age > 80) {
            alert('Пожалуйста, введите корректный возраст (16-80 лет)');
            return;
        }
        setTestStarted(true);
    };

    const handleAnswer = (answer) => {
        const newAnswers = [...answers];
        const startTime = newAnswers[currentQuestion]?.startTime || Date.now();
        const timeSpent = (Date.now() - startTime) / 1000;

        newAnswers[currentQuestion] = {
            question_id: questions[currentQuestion].id,
            answer,
            time_spent: timeSpent
        };

        setAnswers(newAnswers);

        if (currentQuestion < questions.length - 1) {
            setCurrentQuestion(currentQuestion + 1);
        } else {
            handleSubmitTest();
        }
    };

    const handleSubmitTest = async () => {
        try {
            const submission = {
                test_type: 'cattell_cfit',
                answers: answers,
                age: parseInt(age)
            };

            const response = await api.post('/tests/submit', submission);
            
            alert(`Тест завершен! Ваш IQ: ${response.data.standard_score}`);
            navigate('/dashboard');
        } catch (error) {
            console.error('Error submitting test:', error);
            alert('Ошибка при отправке теста');
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    if (!testStarted) {
        return (
            <div className="test-start">
                <h1>Инструкция к тесту</h1>
                <div className="instructions">
                    <p>Тест состоит из 50 заданий на выявление закономерностей.</p>
                    <p>На выполнение теста отводится 30 минут.</p>
                    <p>Выберите правильный вариант ответа для каждой матрицы.</p>
                    <p>Не задерживайтесь слишком долго на одном задании.</p>
                </div>
                
                <div className="age-input">
                    <label>Ваш возраст (16-80 лет):</label>
                    <input
                        type="number"
                        min="16"
                        max="80"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        placeholder="Введите ваш возраст"
                    />
                </div>
                
                <button className="btn-start" onClick={handleStartTest}>
                    Начать тест
                </button>
            </div>
        );
    }

    const question = questions[currentQuestion];
    const progress = ((currentQuestion + 1) / questions.length) * 100;

    return (
        <div className="test-container">
            <div className="test-header">
                <div className="progress-bar">
                    <div 
                        className="progress-fill"
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>
                <div className="test-info">
                    <span>Вопрос {currentQuestion + 1} из {questions.length}</span>
                    <span className="timer">Осталось: {formatTime(timeLeft)}</span>
                </div>
            </div>

            <div className="question-container">
                <h3>Вопрос {question.id}: {question.question}</h3>
                
                {question.image && (
                    <div className="question-image">
                        <img 
                            src={question.image} 
                            alt={`Matrix ${question.id}`} 
                        />
                    </div>
                )}
                
                <div className="options-grid">
                    {question.options.map((option, index) => (
                        <button
                            key={index}
                            className="option-btn"
                            onClick={() => handleAnswer(option)}
                        >
                            {option}
                        </button>
                    ))}
                </div>
            </div>

            <div className="test-navigation">
                <button
                    className="btn-prev"
                    onClick={() => setCurrentQuestion(prev => Math.max(0, prev - 1))}
                    disabled={currentQuestion === 0}
                >
                    Назад
                </button>
                
                <button
                    className="btn-skip"
                    onClick={() => handleAnswer('skip')}
                >
                    Пропустить
                </button>
                
                {currentQuestion === questions.length - 1 && (
                    <button
                        className="btn-finish"
                        onClick={handleSubmitTest}
                    >
                        Завершить тест
                    </button>
                )}
            </div>
        </div>
    );
};

export default TestComponent;
