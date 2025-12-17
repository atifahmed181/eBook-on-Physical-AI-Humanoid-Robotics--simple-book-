import React from 'react';
import Layout from '@theme/Layout';
import Chatbot from '../components/Chatbot';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

function ChatbotPage() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={`AI Assistant - ${siteConfig.title}`}
      description="AI-powered chatbot for the Physical AI and Humanoid Robotics e-book">
      <main style={{ padding: '2rem 0', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ padding: '0 2rem' }}>
          <h1 style={{ textAlign: 'center', marginBottom: '2rem' }}>
            AI Assistant for Physical AI & Humanoid Robotics
          </h1>
          <p style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '1.1rem' }}>
            Ask questions about the e-book content and get AI-powered answers based on the provided documentation.
          </p>

          <div style={{ marginBottom: '2rem', padding: '1rem', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <h2>How to Use This Chatbot</h2>
            <ul style={{ paddingLeft: '1.5rem' }}>
              <li>Type your question about Physical AI, Humanoid Robotics, ROS 2, NVIDIA Isaac, or related topics</li>
              <li>The AI will search the e-book content and provide relevant answers</li>
              <li>Sources will be provided for each answer so you can read more in the documentation</li>
              <li>Try one of the sample questions if you're not sure what to ask</li>
            </ul>
          </div>

          <Chatbot />
        </div>
      </main>
    </Layout>
  );
}

export default ChatbotPage;