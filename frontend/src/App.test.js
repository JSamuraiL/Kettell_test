import { render, screen } from '@testing-library/react';
import App from './App';

test('renders login screen', () => {
  render(<App />);
  expect(screen.getByText(/Система пользовательского тестирования/i)).toBeInTheDocument();
});
