import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Activity, 
  Key, 
  Database, 
  Settings, 
  MessageSquare, 
  TrendingUp,
  Users,
  Zap
} from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalRequests: 0,
    totalTokens: 0,
    activeModels: 0,
    activeProviders: 0
  });

  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    // Fetch dashboard stats
    fetchDashboardStats();
    fetchRecentActivity();
  }, []);

  const fetchDashboardStats = async () => {
    // TODO: Implement API call to fetch stats
    setStats({
      totalRequests: 1250,
      totalTokens: 45000,
      activeModels: 8,
      activeProviders: 3
    });
  };

  const fetchRecentActivity = async () => {
    // TODO: Implement API call to fetch recent activity
    setRecentActivity([
      { id: 1, type: 'request', message: 'Chat completion request to gpt-4', time: '2 minutes ago' },
      { id: 2, type: 'provider', message: 'New OpenAI provider added', time: '1 hour ago' },
      { id: 3, type: 'model', message: 'Model llama-2-7b registered', time: '3 hours ago' },
      { id: 4, type: 'key', message: 'API key created for production', time: '1 day ago' }
    ]);
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'request':
        return <MessageSquare className="h-4 w-4 text-blue-500" />;
      case 'provider':
        return <Database className="h-4 w-4 text-green-500" />;
      case 'model':
        return <Settings className="h-4 w-4 text-purple-500" />;
      case 'key':
        return <Key className="h-4 w-4 text-orange-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const quickActions = [
    {
      title: 'Add Provider',
      description: 'Connect a new AI service provider',
      icon: <Database className="h-8 w-8 text-blue-600" />,
      link: '/providers',
      color: 'bg-blue-50 border-blue-200 hover:bg-blue-100'
    },
    {
      title: 'Create API Key',
      description: 'Generate a new API key for your applications',
      icon: <Key className="h-8 w-8 text-green-600" />,
      link: '/keys',
      color: 'bg-green-50 border-green-200 hover:bg-green-100'
    },
    {
      title: 'Test Model',
      description: 'Try out your models with a test prompt',
      icon: <MessageSquare className="h-8 w-8 text-purple-600" />,
      link: '/test',
      color: 'bg-purple-50 border-purple-200 hover:bg-purple-100'
    },
    {
      title: 'View Analytics',
      description: 'Monitor usage and performance metrics',
      icon: <TrendingUp className="h-8 w-8 text-orange-600" />,
      link: '/analytics',
      color: 'bg-orange-50 border-orange-200 hover:bg-orange-100'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600">Welcome to your BYOM AI Platform workspace</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full"></div>
            <span className="text-sm text-gray-600">All systems operational</span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Requests</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalRequests.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Zap className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Tokens</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalTokens.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Settings className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Models</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.activeModels}</p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Database className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Providers</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.activeProviders}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, index) => (
            <Link
              key={index}
              to={action.link}
              className={`p-4 rounded-lg border-2 transition-colors duration-200 ${action.color}`}
            >
              <div className="text-center">
                {action.icon}
                <h3 className="mt-2 text-sm font-medium text-gray-900">{action.title}</h3>
                <p className="mt-1 text-xs text-gray-600">{action.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {recentActivity.map((activity) => (
            <div key={activity.id} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50">
              {getActivityIcon(activity.type)}
              <div className="flex-1">
                <p className="text-sm text-gray-900">{activity.message}</p>
                <p className="text-xs text-gray-500">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
