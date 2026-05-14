import { io, Socket } from 'socket.io-client';

let socket: Socket | null = null;

export const getSocket = (): Socket => {
  if (!socket) {
    const token = localStorage.getItem('accessToken');
    socket = io('https://vireo-api.onrender.com', {  // your live backend
      auth: { token },
      transports: ['websocket', 'polling'],
      autoConnect: true,
    });
  } else {
    // Update auth token in case it changed
    const token = localStorage.getItem('accessToken');
    socket.auth = { token };
  }
  return socket;
};

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};