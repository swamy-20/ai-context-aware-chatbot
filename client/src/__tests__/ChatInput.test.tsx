import { fireEvent, render, screen } from '@testing-library/react';
import ChatInput from '../components/ChatInput';

test('submits text to onSend callback', () => {
  const onSend = jest.fn();
  render(<ChatInput onSend={onSend} sending={false} />);
  const textbox = screen.getByRole('textbox', { name: /your message/i });
  fireEvent.change(textbox, { target: { value: 'hello world' } });
  fireEvent.submit(textbox.closest('form') as HTMLFormElement);
  expect(onSend).toHaveBeenCalledWith('hello world');
});
