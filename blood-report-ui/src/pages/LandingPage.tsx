/**
 * Landing Page
 * Public landing page for the application
 */

import ThemeToggle from '@/components/ThemeToggle';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header with theme toggle */}
      <div className="container mx-auto px-4 py-4 flex justify-end">
        <ThemeToggle />
      </div>

      {/* Main content */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Blood Report Analysis
          </h1>
          <p className="text-2xl text-gray-600 dark:text-gray-300 mb-12">
            Intelligent blood report analysis and visualization powered by AI
          </p>

          {/* Feature cards */}
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Smart Analysis
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                AI-powered analysis of blood parameters with intelligent classification
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <div className="text-4xl mb-4">📈</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Trend Tracking
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Track your health metrics over time with beautiful visualizations
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Personalized Insights
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Get personalized health recommendations based on your results
              </p>
            </div>
          </div>

          {/* Quick links */}
          <div className="mt-16 flex gap-4 justify-center">
            <a
              href="/dashboard"
              className="btn-primary text-lg px-8 py-3"
            >
              View Dashboard
            </a>
            <a
              href="/upload"
              className="btn-secondary text-lg px-8 py-3"
            >
              Upload Report
            </a>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="container mx-auto px-4 py-8 text-center text-gray-600 dark:text-gray-400">
        <p>Blood Report Analysis System - Milestone 1 Complete ✅</p>
      </div>
    </div>
  );
}
