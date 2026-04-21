// frontend/src/components/TestSystem.js
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/axios';
import './TestSystem.css';

const TestSystem = () => {
    const { testId } = useParams();
    const navigate = useNavigate();
    
    const [testInfo, setTestInfo] = useState(null);
    const [questions, setQuestions] = useState([]);
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [answers, setAnswers] = useState([]);
    const [testStarted, setTestStarted] = useState(false);
    const [timeLeft, setTimeLeft] = useState(0);
    const [showInstructions, setShowInstructions] = useState(true);
    const [startTime, setStartTime] = useState(null);

    useEffect(() => {
        fetchTestInfo();
        fetchQuestions();
    }, [testId]);

    useEffect(() => {
        if (!testStarted || timeLeft <= 0) return;

        const timer = setInterval(() => {
            setTimeLeft(prev => prev - 1);
        }, 1000);

        return () => clearInterval(timer);
    }, [testStarted, timeLeft]);

    const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    const normalizeImageUrl = (path) => {
        if (!path) return '';
        const cleaned = path.replace(/^\/+/, ''); // убираем ведущие слэши
        return `${API_BASE}/images/${cleaned}`;
    };

    const fetchTestInfo = async () => {
        try {
            const response = await api.get(`/tests/${testId}/questions`);
            if (response.data.length > 0) {
                const testResponse = await api.get('/tests/available');
                const test = testResponse.data.find(t => t.id === parseInt(testId));
                setTestInfo({
                    ...test,
                    description_image: normalizeImageUrl(test?.description_image),
                });
                setTimeLeft(test?.time_limit || 1800);
            }
        } catch (error) {
            console.error('Error fetching test info:', error);
        }
    };

    const fetchQuestions = async () => {
        try {
            const response = await api.get(`/tests/${testId}/questions`);
            // Приводим пути к картинкам к /images/...
            const normalizedQuestions = response.data.map(q => ({
                ...q,
                image_path: normalizeImageUrl(q.image_path),
            }));

            setQuestions(normalizedQuestions);
            
            // Инициализируем массив ответов
            const initialAnswers = normalizedQuestions.map(q => ({
                question_id: q.id,
                answer: '',
                time_spent: 0,
            }));
            setAnswers(initialAnswers);
        } catch (error) {
            console.error('Error fetching questions:', error);
        }
    };

    const handleStartTest = () => {
        setShowInstructions(false);
        setTestStarted(true);
        setStartTime(Date.now());
    };

    const handleAnswer = (answer) => {
        const newAnswers = [...answers];
        const questionStartTime = newAnswers[currentQuestion]?.startTime || Date.now();
        const timeSpent = (Date.now() - questionStartTime) / 1000;

        newAnswers[currentQuestion] = {
            question_id: questions[currentQuestion].id,
            answer,
            time_spent: timeSpent,
            startTime: Date.now()
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
            const totalTime = (Date.now() - startTime) / 1000;
            
            const submission = {
                test_part: testInfo?.test_part || 'A',
                answers: answers.map(a => ({
                    question_id: a.question_id,
                    answer: a.answer || 'skip',
                    time_spent: a.time_spent
                }))
            };

            await api.post(`/tests/${testId}/submit`, submission);
            
            alert('Тест завершен. Результаты переданы психологу.');
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

    if (!testInfo || !questions.length) {
        return <div className="loading">Загрузка теста...</div>;
    }

    if (showInstructions) {
        return (
            <div className="test-instructions">
                <div className="instructions-container">
                    <h1>Инструкция к тесту</h1>
                    <div className="test-description">
                        <h2>Тест {testInfo.test_part}{testInfo.test_number}: {testInfo.name}</h2>
                        {testInfo.description_image && (
                            <div className="description-image">
                                <img 
                                    src={testInfo.description_image} 
                                    alt="Описание теста" 
                                />
                            </div>
                        )}
                        <div className="instruction-text">
                            <h3>Инструкция:</h3>
                            <p>{testInfo.instruction_text}</p>
                        </div>
                        <div className="test-stats">
                            <p><strong>Количество вопросов:</strong> {questions.length}</p>
                            <p><strong>Лимит времени:</strong> {formatTime(testInfo.time_limit)}</p>
                            <p><strong>Варианты ответов:</strong> a, b, c, d, e</p>
                        </div>
                        <div className="important-notes">
                            <h4>Важные замечания:</h4>
                            <ul>
                                <li>Выберите один правильный ответ для каждого вопроса</li>
                                <li>На каждый вопрос можно потратить не более 2 минут</li>
                                <li>Нельзя возвращаться к предыдущим вопросам</li>
                                <li>Если не знаете ответ, можете пропустить вопрос</li>
                            </ul>
                        </div>
                        <button className="btn-start-test" onClick={handleStartTest}>
                            Начать тест
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    const question = questions[currentQuestion];
    const progress = ((currentQuestion + 1) / questions.length) * 100;

    return (
        <div className="test-system">
            <div className="test-header">
                <div className="test-info">
                    <h2>Тест {testInfo.test_part}{testInfo.test_number}: {testInfo.name}</h2>
                    <div className="test-meta">
                        <span>Вопрос {currentQuestion + 1} из {questions.length}</span>
                        <span className="timer">Осталось: {formatTime(timeLeft)}</span>
                    </div>
                </div>
                <div className="progress-bar">
                    <div 
                        className="progress-fill"
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>
            </div>

            <div className="question-area">
                <div className="question-header">
                    <h3>Вопрос {question.question_number}</h3>
                </div>
                
                <div className="question-image-container">
                    <img 
                        src={question.image_path} 
                        alt={`Вопрос ${question.question_number}`}
                        className="question-image"
                    />
                </div>
                
                <div className="answer-options">
                    <div className="options-grid">
                        {['a', 'b', 'c', 'd', 'e'].map((option) => (
                            <button
                                key={option}
                                className={`option-btn ${answers[currentQuestion]?.answer === option ? 'selected' : ''}`}
                                onClick={() => handleAnswer(option)}
                            >
                                <span className="option-letter">{option.toUpperCase()}</span>
                            </button>
                        ))}
                    </div>
                </div>
                
                <div className="navigation-buttons">
                    <button
                        className="btn-skip"
                        onClick={() => handleAnswer('skip')}
                    >
                        Пропустить вопрос
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
        </div>
    );
};

export default TestSystem;
