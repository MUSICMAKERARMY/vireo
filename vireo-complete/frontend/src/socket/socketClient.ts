import { io, Socket } from 'socket.io-client';
let socket: Socket | null = null;
export const getSocket = (): Socket => {
  if (!socket) {
    const token = localStorage.getItem('accessToken');
    socket = io('/', { auth: { token }, transports: ['websocket'] });
  }
  return socket;
};
