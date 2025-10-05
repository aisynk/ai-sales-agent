import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, ShoppingBag, Zap, Shield } from 'lucide-react';
import Button from '../components/common/Button';
import useStore from '../store/useStore';

const HomePage = () => {
  const navigate = useNavigate();
  const { openChat } = useStore();

  const features = [
    {
      icon: MessageSquare,
      title: 'AI-Powered Assistance',
      description: 'Get instant help from our intelligent shopping assistant 24/7',
    },
    {
      icon: ShoppingBag,
      title: 'Personalized Recommendations',
      description: 'Discover products tailored to your style and preferences',
    },
    {
      icon: Zap,
      title: 'Seamless Experience',
      description: 'Shop across web, mobile, and in-store with perfect context',
    },
    {
      icon: Shield,
      title: 'Secure Checkout',
      description: 'Your data is protected with enterprise-grade security',
    },
  ];

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              Shop Smarter with AI
            </h1>
            <p className="text-xl md:text-2xl mb-8 opacity-90">
              Your personal shopping assistant that understands your style
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Button
                onClick={openChat}
                size="lg"
                variant="secondary"
              >
                Start Shopping with AI
              </Button>
              <Button
                onClick={() => navigate('/products')}
                size="lg"
                className="bg-white text-primary-600 hover:bg-gray-100"
              >
                Browse Products
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">
            Why Shop With Us?
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow text-center"
              >
                <div className="inline-flex p-3 bg-primary-100 rounded-full mb-4">
                  <feature.icon className="text-primary-600" size={32} />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gray-100 py-16">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-xl text-gray-600 mb-8">
            Experience the future of online shopping today
          </p>
          <Button onClick={openChat} size="lg">
            Chat with AI Assistant
          </Button>
        </div>
      </section>
    </div>
  );
};

export default HomePage;