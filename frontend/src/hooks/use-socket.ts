import { useEffect, useState, useRef, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';

interface WebSocketMessage {
  type: string;
  data?: any;
  message?: string;
  [key: string]: any;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: any) => void;
}

export function useWebSocket(): UseWebSocketReturn {
  const { user, isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    // Only connect if authenticated and user exists
    if (!isAuthenticated || !user?.id) return;

    // Get token from storage
    const token = localStorage.getItem('token');
    if (!token) {
        console.warn('No token found for WebSocket connection');
        return;
    }

    // Determine WebSocket URL
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const wsUrl = apiUrl.replace(/^http/, 'ws');
    const url = `${wsUrl}/api/v1/notifications/${user.id}?token=${token}`;

    console.log('Connecting to WebSocket:', url);

    // Close existing connection if any
    if (socketRef.current) {
      socketRef.current.close();
    }

    try {
      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log('WebSocket Connected');
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket Message:', data);
          setLastMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      socket.onclose = (event) => {
        console.log('WebSocket Disconnected', event.code, event.reason);
        setIsConnected(false);
        socketRef.current = null;

        // Attempt reconnect if not closed cleanly/intentionally
        // 1000 = Normal Closure
        if (event.code !== 1000) {
           reconnectTimeoutRef.current = setTimeout(() => {
             console.log('Attempting to reconnect...');
             connect();
           }, 3000);
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket Error:', error);
        // Error will usually trigger close, but if not, we can close manually to trigger reconnect logic
        // socket.close(); 
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      // Retry on connection creation failure
       reconnectTimeoutRef.current = setTimeout(() => {
         connect();
       }, 5000);
    }
  }, [isAuthenticated, user?.id]);

  useEffect(() => {
    connect();

    return () => {
      // Cleanup
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        // We use 1000 to indicate normal closure
        socketRef.current.close(1000, 'Component unmounting');
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message: any) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  return { isConnected, lastMessage, sendMessage };
}
