// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * AI Chatbot Interface Component
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  Drawer, 
  Input, 
  Button, 
  List, 
  Avatar, 
  Typography, 
  Space, 
  Spin,
  Card,
  Tag,
  Tooltip
} from 'antd';
import { 
  SendOutlined, 
  RobotOutlined, 
  UserOutlined, 
  CloseOutlined,
  BarChartOutlined,
  TableOutlined
} from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';

import { RootState } from '../../store';
import { chatActions } from '../../store/slices/chatSlice';
import { useChatSession } from '../../hooks/useChatSession';
import { ChatMessage } from '../../types/chat';
import { ChartRenderer } from '../Charts/ChartRenderer';

import './ChatInterface.css';

const { TextArea } = Input;
const { Text, Paragraph } = Typography;

export const ChatInterface: React.FC = () => {
  const dispatch = useDispatch();
  const { chatVisible, currentSessionId } = useSelector((state: RootState) => state.chat);
  const { user } = useSelector((state: RootState) => state.auth);
  
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const {
    messages,
    sendMessage,
    createSession,
    isSessionLoading
  } = useChatSession(currentSessionId);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Create session if none exists and chat is visible
    if (chatVisible && !currentSessionId && user) {
      createSession(user.id);
    }
  }, [chatVisible, currentSessionId, user, createSession]);

  const handleSendMessage = async () => {
    if (!message.trim() || isLoading || !currentSessionId) return;

    const userMessage = message.trim();
    setMessage('');
    setIsLoading(true);

    try {
      await sendMessage(userMessage);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClose = () => {
    dispatch(chatActions.toggleChat());
  };

  const renderMessage = (msg: ChatMessage) => {
    const isUser = msg.role === 'user';
    const isSystem = msg.role === 'system';

    return (
      <div key={msg.id} className={`chat-message ${msg.role}`}>
        <div className="message-header">
          <Avatar 
            icon={isUser ? <UserOutlined /> : <RobotOutlined />} 
            size="small"
            style={{ 
              backgroundColor: isUser ? '#1890ff' : '#52c41a',
              marginRight: 8 
            }}
          />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {isUser ? user?.username : 'Songo AI'}
            {msg.timestamp && ` • ${new Date(msg.timestamp).toLocaleTimeString()}`}
          </Text>
        </div>
        
        <div className="message-content">
          {msg.content_type === 'chart' && msg.chart_config ? (
            <Card size="small" style={{ marginTop: 8 }}>
              <ChartRenderer config={msg.chart_config} />
            </Card>
          ) : msg.content_type === 'data' && msg.data_preview ? (
            <Card size="small" style={{ marginTop: 8 }}>
              <div className="data-preview">
                <Space>
                  <TableOutlined />
                  <Text strong>Data Results</Text>
                  <Tag>{msg.data_preview.length} rows</Tag>
                </Space>
                {msg.query_sql && (
                  <details style={{ marginTop: 8 }}>
                    <summary>SQL Query</summary>
                    <pre style={{ fontSize: '12px', background: '#f5f5f5', padding: 8 }}>
                      {msg.query_sql}
                    </pre>
                  </details>
                )}
              </div>
            </Card>
          ) : (
            <Paragraph style={{ marginBottom: 0, whiteSpace: 'pre-wrap' }}>
              {msg.content}
            </Paragraph>
          )}
        </div>
      </div>
    );
  };

  return (
    <Drawer
      title={
        <Space>
          <RobotOutlined />
          <span>Songo AI Assistant</span>
        </Space>
      }
      placement="right"
      width={400}
      open={chatVisible}
      onClose={handleClose}
      closeIcon={<CloseOutlined />}
      className="chat-drawer"
    >
      <div className="chat-container">
        <div className="chat-messages">
          {isSessionLoading ? (
            <div className="loading-container">
              <Spin size="large" />
              <Text>Initializing chat session...</Text>
            </div>
          ) : (
            <>
              {messages.map(renderMessage)}
              {isLoading && (
                <div className="chat-message assistant">
                  <div className="message-header">
                    <Avatar icon={<RobotOutlined />} size="small" style={{ backgroundColor: '#52c41a', marginRight: 8 }} />
                    <Text type="secondary" style={{ fontSize: '12px' }}>Songo AI</Text>
                  </div>
                  <div className="message-content">
                    <Spin size="small" style={{ marginRight: 8 }} />
                    <Text type="secondary">Thinking...</Text>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
        
        <div className="chat-input">
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your data, create charts, or get insights..."
              autoSize={{ minRows: 1, maxRows: 4 }}
              disabled={isLoading || !currentSessionId}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSendMessage}
              disabled={!message.trim() || isLoading || !currentSessionId}
              loading={isLoading}
            />
          </Space.Compact>
          
          <div className="chat-suggestions">
            <Space wrap>
              <Button 
                size="small" 
                type="text"
                onClick={() => setMessage("Show me sales trends for this month")}
              >
                📈 Sales trends
              </Button>
              <Button 
                size="small" 
                type="text"
                onClick={() => setMessage("Create a chart showing top customers")}
              >
                📊 Top customers
              </Button>
              <Button 
                size="small" 
                type="text"
                onClick={() => setMessage("Analyze revenue by region")}
              >
                🌍 Revenue analysis
              </Button>
            </Space>
          </div>
        </div>
      </div>
    </Drawer>
  );
};
