import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './components/Login';
import UserDashboard from './components/UserDashboard';
import PsychologistDashboard from './components/PsychologistDashboard';
import TestSystem from './components/TestSystem';
import './App.css';

function App() {
    const [token, setToken] = useState(null);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');
        
        if (storedToken) {
            setToken(storedToken);
        }
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    const ProtectedRoute = ({ children, allowedRoles }) => {
        if (!token || !user) {
            return <Navigate to="/login" replace />;
        }
        
        if (allowedRoles && !allowedRoles.includes(user.role)) {
            // Редирект на соответствующую дашборд
            return <Navigate to={`/${user.role}-dashboard`} replace />;
        }
        
        return children;
    };

    const PublicRoute = ({ children }) => {
        return !token ? children : <Navigate to="/dashboard" replace />;
    };

    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route 
                        path="/login" 
                        element={
                            <PublicRoute>
                                <Login setToken={setToken} setUser={setUser} />
                            </PublicRoute>
                        } 
                    />
                    
                    <Route 
                        path="/dashboard" 
                        element={
                            <ProtectedRoute>
                                {user?.role === 'psychologist' ? (
                                    <PsychologistDashboard />
                                ) : (
                                    <UserDashboard />
                                )}
                            </ProtectedRoute>
                        } 
                    />
                    
                    <Route 
                        path="/test/:testId" 
                        element={
                            <ProtectedRoute allowedRoles={['user']}>
                                <TestSystem />
                            </ProtectedRoute>
                        } 
                    />
                    
                    <Route 
                        path="/psychologist-dashboard" 
                        element={
                            <ProtectedRoute allowedRoles={['psychologist']}>
                                <PsychologistDashboard />
                            </ProtectedRoute>
                        } 
                    />
                    
                    <Route 
                        path="/" 
                        element={
                            <Navigate to={token ? "/dashboard" : "/login"} replace />
                        } 
                    />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
